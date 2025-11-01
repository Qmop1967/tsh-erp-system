"""
TSH NeuroLink - Rule Engine Service
Evaluates events against notification rules and generates notifications
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID
from jinja2 import Template, TemplateError
from sqlalchemy import select, and_, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis
import json

from app.config import settings
from app.models import (
    NeurolinkEvent,
    NeurolinkNotificationRule,
    NeurolinkNotification
)


logger = logging.getLogger(__name__)


class RuleEngineService:
    """
    Rule Engine Service

    Responsibilities:
    - Subscribe to Redis event channels
    - Fetch events from database
    - Evaluate events against active rules
    - Generate notifications from matching rules
    - Handle template rendering with Jinja2
    """

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.running = False

    async def start(self):
        """Start the rule engine worker"""
        logger.info("🚀 Starting Rule Engine Service...")

        # Connect to Redis
        self.redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )

        self.running = True

        # Start Redis subscriber
        asyncio.create_task(self._subscribe_to_events())

        logger.info("✅ Rule Engine Service started")

    async def stop(self):
        """Stop the rule engine worker"""
        logger.info("🛑 Stopping Rule Engine Service...")
        self.running = False

        if self.redis_client:
            await self.redis_client.close()

        logger.info("✅ Rule Engine Service stopped")

    async def _subscribe_to_events(self):
        """Subscribe to Redis event channels and process events"""
        pubsub = self.redis_client.pubsub()

        # Subscribe to all events channel
        await pubsub.subscribe(f"{settings.redis_channel_prefix}events:all")

        logger.info(f"📡 Subscribed to {settings.redis_channel_prefix}events:all")

        try:
            while self.running:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)

                if message and message['type'] == 'message':
                    try:
                        # Parse event message
                        event_data = eval(message['data'])  # Safe because we control the publisher
                        event_id = event_data.get('event_id')

                        if event_id:
                            await self._process_event(UUID(event_id))

                    except Exception as e:
                        logger.error(f"❌ Error processing event message: {e}")

                await asyncio.sleep(0.1)  # Small delay to prevent CPU spinning

        except asyncio.CancelledError:
            logger.info("Rule engine subscriber cancelled")
        finally:
            await pubsub.unsubscribe()

    async def _process_event(self, event_id: UUID):
        """
        Process a single event through the rule engine

        Steps:
        1. Fetch event from database
        2. Fetch active rules matching the event
        3. Evaluate each rule
        4. Generate notifications for matching rules
        """
        from app.database import AsyncSessionLocal

        async with AsyncSessionLocal() as db:
            try:
                # Fetch event
                event_query = select(NeurolinkEvent).where(NeurolinkEvent.id == event_id)
                result = await db.execute(event_query)
                event = result.scalar_one_or_none()

                if not event:
                    logger.warning(f"⚠️ Event {event_id} not found")
                    return

                # Skip if already processed
                if event.processed_at:
                    logger.debug(f"ℹ️ Event {event_id} already processed")
                    return

                logger.info(f"🔍 Processing event {event_id}: {event.source_module}.{event.event_type}")

                # Fetch matching rules
                rules = await self._get_matching_rules(db, event)

                if not rules:
                    logger.debug(f"ℹ️ No matching rules for event {event_id}")
                    event.processed_at = datetime.utcnow()
                    await db.commit()
                    return

                logger.info(f"📋 Found {len(rules)} matching rules for event {event_id}")

                # Generate notifications for each matching rule
                notifications_created = 0
                for rule in rules:
                    try:
                        count = await self._generate_notifications_from_rule(db, event, rule)
                        notifications_created += count
                    except Exception as e:
                        logger.error(f"❌ Error generating notifications from rule {rule.id}: {e}")

                # Mark event as processed
                event.processed_at = datetime.utcnow()
                await db.commit()

                logger.info(f"✅ Event {event_id} processed: {notifications_created} notifications created")

            except Exception as e:
                logger.error(f"❌ Error processing event {event_id}: {e}")
                await db.rollback()

    async def _get_matching_rules(
        self,
        db: AsyncSession,
        event: NeurolinkEvent
    ) -> List[NeurolinkNotificationRule]:
        """
        Get all active rules that match the event

        Matching criteria:
        - Rule is active
        - source_module matches (or rule has no module filter)
        - event_type matches pattern
        - Conditional DSL passes (if defined)
        """
        # Base query: active rules sorted by priority
        query = select(NeurolinkNotificationRule).where(
            NeurolinkNotificationRule.is_active == True
        ).order_by(NeurolinkNotificationRule.priority.desc())

        result = await db.execute(query)
        all_rules = result.scalars().all()

        matching_rules = []

        for rule in all_rules:
            if self._rule_matches_event(rule, event):
                matching_rules.append(rule)

        return matching_rules

    def _rule_matches_event(
        self,
        rule: NeurolinkNotificationRule,
        event: NeurolinkEvent
    ) -> bool:
        """Check if a rule matches an event"""

        # Check module filter
        if rule.source_module and rule.source_module != event.source_module:
            return False

        # Check event type pattern
        if rule.event_type_pattern:
            if not self._pattern_matches(rule.event_type_pattern, event.event_type):
                return False

        # Check conditional DSL (if defined)
        if rule.condition_dsl:
            if not self._evaluate_condition_dsl(rule.condition_dsl, event):
                return False

        return True

    def _pattern_matches(self, pattern: str, event_type: str) -> bool:
        """
        Check if event_type matches pattern

        Supports:
        - Exact match: "invoice.created"
        - Wildcard: "invoice.*" matches "invoice.created", "invoice.updated", etc.
        """
        if pattern == event_type:
            return True

        # Wildcard matching
        if '*' in pattern:
            pattern_parts = pattern.split('.')
            event_parts = event_type.split('.')

            if len(pattern_parts) != len(event_parts):
                return False

            for pattern_part, event_part in zip(pattern_parts, event_parts):
                if pattern_part == '*':
                    continue
                if pattern_part != event_part:
                    return False

            return True

        return False

    def _evaluate_condition_dsl(
        self,
        condition: Dict[str, Any],
        event: NeurolinkEvent
    ) -> bool:
        """
        Evaluate conditional DSL against event

        Simple DSL format:
        {
            "field": "payload.amount",
            "operator": "gt",
            "value": 10000
        }

        Operators: eq, ne, gt, gte, lt, lte, in, contains
        """
        try:
            field_path = condition.get('field', '')
            operator = condition.get('operator', 'eq')
            expected_value = condition.get('value')

            # Extract value from event
            actual_value = self._get_nested_value(event, field_path)

            # Apply operator
            if operator == 'eq':
                return actual_value == expected_value
            elif operator == 'ne':
                return actual_value != expected_value
            elif operator == 'gt':
                return actual_value > expected_value
            elif operator == 'gte':
                return actual_value >= expected_value
            elif operator == 'lt':
                return actual_value < expected_value
            elif operator == 'lte':
                return actual_value <= expected_value
            elif operator == 'in':
                return actual_value in expected_value
            elif operator == 'contains':
                return expected_value in actual_value
            else:
                logger.warning(f"Unknown operator: {operator}")
                return False

        except Exception as e:
            logger.error(f"Error evaluating condition DSL: {e}")
            return False

    def _get_nested_value(self, event: NeurolinkEvent, field_path: str) -> Any:
        """
        Get nested value from event using dot notation

        Examples:
        - "severity" -> event.severity
        - "payload.amount" -> event.payload['amount']
        - "payload.customer.name" -> event.payload['customer']['name']
        """
        parts = field_path.split('.')
        value = event

        for part in parts:
            if hasattr(value, part):
                value = getattr(value, part)
            elif isinstance(value, dict):
                value = value.get(part)
            else:
                return None

        return value

    async def _generate_notifications_from_rule(
        self,
        db: AsyncSession,
        event: NeurolinkEvent,
        rule: NeurolinkNotificationRule
    ) -> int:
        """
        Generate notifications from a rule for an event

        Steps:
        1. Render notification template with event data
        2. Determine recipient users based on roles/branches
        3. Check rate limits and cooldowns
        4. Create notification records
        """
        template_config = rule.notification_template

        # Render template fields
        try:
            rendered = self._render_template(template_config, event)
        except Exception as e:
            logger.error(f"❌ Error rendering template for rule {rule.id}: {e}")
            return 0

        # Get recipient users
        recipients = await self._get_recipients(db, event, template_config)

        if not recipients:
            logger.debug(f"ℹ️ No recipients found for rule {rule.id}")
            return 0

        # Create notifications
        notifications_created = 0
        for user_id in recipients:
            try:
                # Check rate limits
                if await self._is_rate_limited(db, user_id, rule):
                    logger.debug(f"⏳ User {user_id} is rate-limited for rule {rule.id}")
                    continue

                # Create notification
                notification = NeurolinkNotification(
                    event_id=event.id,
                    rule_id=rule.id,
                    user_id=user_id,
                    branch_id=event.branch_id,
                    title=rendered['title'],
                    body=rendered['body'],
                    severity=rendered.get('severity', 'info'),
                    action_url=rendered.get('action_url'),
                    action_label=rendered.get('action_label'),
                    metadata=rendered.get('metadata', {}),
                    channels=rendered.get('channels', ['in_app']),
                    status='pending'
                )

                db.add(notification)
                notifications_created += 1

            except Exception as e:
                logger.error(f"❌ Error creating notification for user {user_id}: {e}")

        # Update rule last triggered time
        rule.last_triggered_at = datetime.utcnow()

        await db.commit()

        return notifications_created

    def _render_template(
        self,
        template_config: Dict[str, Any],
        event: NeurolinkEvent
    ) -> Dict[str, Any]:
        """
        Render notification template with event data using Jinja2

        Template variables available:
        - All event fields (source_module, event_type, severity, etc.)
        - All payload fields (flattened)
        """
        # Prepare template context
        context = {
            'event_id': str(event.id),
            'source_module': event.source_module,
            'event_type': event.event_type,
            'severity': event.severity,
            'occurred_at': event.occurred_at.isoformat(),
            'branch_id': event.branch_id,
            'user_id': event.user_id,
            **event.payload  # Flatten payload into context
        }

        rendered = {}

        # Render each template field
        for key, value in template_config.items():
            if isinstance(value, str):
                try:
                    template = Template(value)
                    rendered[key] = template.render(**context)
                except TemplateError as e:
                    logger.error(f"Template error in field '{key}': {e}")
                    rendered[key] = value  # Use original value
            else:
                rendered[key] = value  # Non-string values pass through

        return rendered

    async def _get_recipients(
        self,
        db: AsyncSession,
        event: NeurolinkEvent,
        template_config: Dict[str, Any]
    ) -> List[int]:
        """
        Get list of user IDs who should receive this notification

        Based on:
        - recipient_roles in template
        - branch_id from event
        - is_active status
        """
        recipient_roles = template_config.get('recipient_roles', [])

        if not recipient_roles:
            # No role filter - send to event creator only
            if event.user_id:
                return [event.user_id]
            return []

        # Query users by roles and branch
        query = text("""
            SELECT DISTINCT u.id
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            WHERE u.is_active = true
            AND r.name = ANY(:roles)
            AND (u.branch_id = :branch_id OR :branch_id IS NULL)
        """)

        result = await db.execute(
            query,
            {"roles": recipient_roles, "branch_id": event.branch_id}
        )

        user_ids = [row[0] for row in result.fetchall()]

        return user_ids

    async def _is_rate_limited(
        self,
        db: AsyncSession,
        user_id: int,
        rule: NeurolinkNotificationRule
    ) -> bool:
        """
        Check if user is rate-limited for this rule

        Checks:
        - Cooldown period (minimum time between same notification)
        - Max per hour limit
        """
        if not rule.cooldown_minutes and not rule.max_per_hour:
            return False  # No rate limiting

        # Check cooldown
        if rule.cooldown_minutes:
            cooldown_threshold = datetime.utcnow() - timedelta(minutes=rule.cooldown_minutes)

            cooldown_query = select(func.count(NeurolinkNotification.id)).where(
                and_(
                    NeurolinkNotification.user_id == user_id,
                    NeurolinkNotification.rule_id == rule.id,
                    NeurolinkNotification.created_at >= cooldown_threshold
                )
            )

            result = await db.execute(cooldown_query)
            count = result.scalar()

            if count > 0:
                return True  # Still in cooldown period

        # Check max per hour
        if rule.max_per_hour:
            from datetime import timedelta
            hour_ago = datetime.utcnow() - timedelta(hours=1)

            hour_query = select(func.count(NeurolinkNotification.id)).where(
                and_(
                    NeurolinkNotification.user_id == user_id,
                    NeurolinkNotification.rule_id == rule.id,
                    NeurolinkNotification.created_at >= hour_ago
                )
            )

            result = await db.execute(hour_query)
            count = result.scalar()

            if count >= rule.max_per_hour:
                return True  # Exceeded hourly limit

        return False  # Not rate limited


# Global instance
rule_engine_service = RuleEngineService()
