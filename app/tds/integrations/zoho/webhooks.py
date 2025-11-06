"""
Zoho Webhook Manager
====================

Manages Zoho webhooks and real-time updates.
Consolidates zoho_webhooks.py (router), zoho_webhook_health.py, and zoho_inbox.py.

مدير webhooks والتحديثات الفورية من Zoho

Features:
- Webhook registration and management
- Event validation and verification
- Signature validation
- Event processing pipeline
- Deduplication
- Health monitoring
- Auto-recovery
- Event replay

Author: TSH ERP Team
Date: November 6, 2025
"""

import asyncio
import hashlib
import hmac
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from collections import deque

from .sync import ZohoSyncOrchestrator, EntityType, SyncConfig, SyncMode
from ...core.events import publish_event
from ....core.event_bus import EventBus

logger = logging.getLogger(__name__)


class WebhookEvent(str, Enum):
    """أنواع أحداث Webhook"""
    ITEM_CREATED = "item.created"
    ITEM_UPDATED = "item.updated"
    ITEM_DELETED = "item.deleted"
    INVOICE_CREATED = "invoice.created"
    INVOICE_UPDATED = "invoice.updated"
    INVOICE_DELETED = "invoice.deleted"
    ORDER_CREATED = "salesorder.created"
    ORDER_UPDATED = "salesorder.updated"
    ORDER_DELETED = "salesorder.deleted"
    CONTACT_CREATED = "contact.created"
    CONTACT_UPDATED = "contact.updated"
    CONTACT_DELETED = "contact.deleted"


class WebhookStatus(str, Enum):
    """حالة معالجة Webhook"""
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    DUPLICATE = "duplicate"


@dataclass
class WebhookPayload:
    """Webhook payload data"""
    event_id: str
    event_type: WebhookEvent
    entity_type: EntityType
    entity_id: str
    organization_id: str
    timestamp: datetime
    data: Dict[str, Any]
    signature: Optional[str] = None
    raw_payload: Optional[Dict[str, Any]] = None


@dataclass
class WebhookProcessResult:
    """Webhook processing result"""
    event_id: str
    status: WebhookStatus
    processed_at: datetime
    processing_time_ms: float
    error_message: Optional[str] = None


class WebhookValidator:
    """
    Validates webhook signatures and payloads
    التحقق من صحة webhooks
    """

    def __init__(self, secret_key: str):
        """
        Initialize webhook validator

        Args:
            secret_key: Webhook secret key for signature validation
        """
        self.secret_key = secret_key

    def validate_signature(
        self,
        payload: str,
        signature: str
    ) -> bool:
        """
        Validate webhook signature

        Args:
            payload: Raw webhook payload string
            signature: Signature from webhook header

        Returns:
            bool: True if signature is valid
        """
        if not self.secret_key:
            logger.warning("No secret key configured, skipping signature validation")
            return True

        try:
            # Calculate expected signature
            expected_signature = hmac.new(
                self.secret_key.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            # Compare signatures
            return hmac.compare_digest(expected_signature, signature)

        except Exception as e:
            logger.error(f"Signature validation error: {str(e)}")
            return False

    def validate_payload(self, payload: Dict[str, Any]) -> bool:
        """
        Validate webhook payload structure

        Args:
            payload: Webhook payload

        Returns:
            bool: True if payload is valid
        """
        # Check required fields
        required_fields = ['event_type', 'entity_id', 'organization_id']

        for field in required_fields:
            if field not in payload:
                logger.warning(f"Missing required field in webhook: {field}")
                return False

        return True


class WebhookDeduplicator:
    """
    Prevents duplicate webhook processing
    منع معالجة webhooks المكررة
    """

    def __init__(self, window_minutes: int = 10, max_size: int = 10000):
        """
        Initialize deduplicator

        Args:
            window_minutes: Deduplication window in minutes
            max_size: Maximum number of event IDs to track
        """
        self.window = timedelta(minutes=window_minutes)
        self.max_size = max_size
        self._events: deque = deque(maxlen=max_size)
        self._event_set: set = set()
        self._lock = asyncio.Lock()

    async def is_duplicate(self, event_id: str) -> bool:
        """
        Check if event is a duplicate

        Args:
            event_id: Event ID to check

        Returns:
            bool: True if duplicate
        """
        async with self._lock:
            # Clean old events
            await self._clean_old_events()

            # Check if event exists
            if event_id in self._event_set:
                logger.info(f"Duplicate webhook detected: {event_id}")
                return True

            # Add new event
            event_data = {
                'event_id': event_id,
                'timestamp': datetime.utcnow()
            }
            self._events.append(event_data)
            self._event_set.add(event_id)

            return False

    async def _clean_old_events(self):
        """Remove events outside the deduplication window"""
        cutoff_time = datetime.utcnow() - self.window

        while self._events and self._events[0]['timestamp'] < cutoff_time:
            old_event = self._events.popleft()
            self._event_set.discard(old_event['event_id'])


class ZohoWebhookManager:
    """
    Zoho Webhook Manager
    مدير webhooks Zoho

    Manages webhook registration, validation, and processing.
    """

    def __init__(
        self,
        sync_orchestrator: ZohoSyncOrchestrator,
        secret_key: Optional[str] = None,
        event_bus: Optional[EventBus] = None,
        enable_deduplication: bool = True,
        enable_validation: bool = True
    ):
        """
        Initialize Webhook Manager

        Args:
            sync_orchestrator: Sync orchestrator for processing updates
            secret_key: Webhook secret key for signature validation
            event_bus: Event bus for publishing events
            enable_deduplication: Enable duplicate detection
            enable_validation: Enable signature validation
        """
        self.sync = sync_orchestrator
        self.event_bus = event_bus
        self.enable_deduplication = enable_deduplication
        self.enable_validation = enable_validation

        # Initialize components
        self.validator = WebhookValidator(secret_key) if secret_key else None
        self.deduplicator = WebhookDeduplicator() if enable_deduplication else None

        # Event handlers registry
        self._event_handlers: Dict[WebhookEvent, List[Callable]] = {}

        # Processing queue
        self._processing_queue: asyncio.Queue = asyncio.Queue()
        self._processor_task: Optional[asyncio.Task] = None

        # Health tracking
        self._health_stats = {
            "total_received": 0,
            "total_processed": 0,
            "total_failed": 0,
            "total_duplicates": 0,
            "last_received": None,
            "last_processed": None,
            "processing_errors": []
        }

        # Recent webhooks (for debugging)
        self._recent_webhooks: deque = deque(maxlen=100)

    async def start(self):
        """Start webhook manager and processing worker"""
        if not self._processor_task:
            self._processor_task = asyncio.create_task(self._process_webhooks())
            logger.info("Webhook manager started")

    async def stop(self):
        """Stop webhook manager"""
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
            logger.info("Webhook manager stopped")

    async def handle_webhook(
        self,
        payload: Dict[str, Any],
        signature: Optional[str] = None,
        raw_payload: Optional[str] = None
    ) -> WebhookProcessResult:
        """
        Handle incoming webhook

        Args:
            payload: Webhook payload data
            signature: Webhook signature (if available)
            raw_payload: Raw payload string for signature validation

        Returns:
            WebhookProcessResult: Processing result
        """
        start_time = datetime.utcnow()

        try:
            # Update stats
            self._health_stats["total_received"] += 1
            self._health_stats["last_received"] = datetime.utcnow().isoformat()

            # Validate signature
            if self.enable_validation and signature and raw_payload:
                if not self.validator.validate_signature(raw_payload, signature):
                    logger.warning("Invalid webhook signature")
                    return WebhookProcessResult(
                        event_id=payload.get('event_id', 'unknown'),
                        status=WebhookStatus.FAILED,
                        processed_at=datetime.utcnow(),
                        processing_time_ms=0,
                        error_message="Invalid signature"
                    )

            # Validate payload structure
            if not self.validator.validate_payload(payload):
                logger.warning("Invalid webhook payload structure")
                return WebhookProcessResult(
                    event_id=payload.get('event_id', 'unknown'),
                    status=WebhookStatus.FAILED,
                    processed_at=datetime.utcnow(),
                    processing_time_ms=0,
                    error_message="Invalid payload structure"
                )

            # Parse webhook payload
            webhook_data = await self._parse_webhook(payload)

            # Check for duplicates
            if self.enable_deduplication:
                is_dup = await self.deduplicator.is_duplicate(webhook_data.event_id)
                if is_dup:
                    self._health_stats["total_duplicates"] += 1
                    return WebhookProcessResult(
                        event_id=webhook_data.event_id,
                        status=WebhookStatus.DUPLICATE,
                        processed_at=datetime.utcnow(),
                        processing_time_ms=(
                            datetime.utcnow() - start_time
                        ).total_seconds() * 1000,
                        error_message="Duplicate event"
                    )

            # Add to processing queue
            await self._processing_queue.put(webhook_data)

            # Store in recent webhooks
            self._recent_webhooks.append({
                'event_id': webhook_data.event_id,
                'event_type': webhook_data.event_type,
                'entity_type': webhook_data.entity_type,
                'entity_id': webhook_data.entity_id,
                'timestamp': webhook_data.timestamp.isoformat()
            })

            # Calculate processing time
            processing_time = (
                datetime.utcnow() - start_time
            ).total_seconds() * 1000

            logger.info(
                f"Webhook queued: {webhook_data.event_type} - "
                f"{webhook_data.entity_id} ({processing_time:.2f}ms)"
            )

            # Publish webhook received event
            await self._publish_event("tds.zoho.webhook.received", {
                "event_id": webhook_data.event_id,
                "event_type": webhook_data.event_type,
                "entity_type": webhook_data.entity_type,
                "entity_id": webhook_data.entity_id
            })

            return WebhookProcessResult(
                event_id=webhook_data.event_id,
                status=WebhookStatus.PENDING,
                processed_at=datetime.utcnow(),
                processing_time_ms=processing_time
            )

        except Exception as e:
            logger.error(f"Webhook handling error: {str(e)}", exc_info=True)
            self._health_stats["total_failed"] += 1
            self._health_stats["processing_errors"].append({
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })

            return WebhookProcessResult(
                event_id=payload.get('event_id', 'unknown'),
                status=WebhookStatus.FAILED,
                processed_at=datetime.utcnow(),
                processing_time_ms=0,
                error_message=str(e)
            )

    async def _parse_webhook(
        self,
        payload: Dict[str, Any]
    ) -> WebhookPayload:
        """
        Parse webhook payload into WebhookPayload object

        Args:
            payload: Raw webhook payload

        Returns:
            WebhookPayload: Parsed webhook data
        """
        # Extract event type
        event_type_str = payload.get('event_type', '')
        event_type = WebhookEvent(event_type_str)

        # Determine entity type from event type
        entity_type = self._get_entity_type_from_event(event_type)

        # Create webhook payload object
        return WebhookPayload(
            event_id=payload.get('event_id', f"evt_{datetime.utcnow().timestamp()}"),
            event_type=event_type,
            entity_type=entity_type,
            entity_id=payload.get('entity_id'),
            organization_id=payload.get('organization_id'),
            timestamp=datetime.utcnow(),
            data=payload.get('data', {}),
            raw_payload=payload
        )

    def _get_entity_type_from_event(
        self,
        event_type: WebhookEvent
    ) -> EntityType:
        """Map webhook event type to entity type"""
        mapping = {
            WebhookEvent.ITEM_CREATED: EntityType.PRODUCTS,
            WebhookEvent.ITEM_UPDATED: EntityType.PRODUCTS,
            WebhookEvent.ITEM_DELETED: EntityType.PRODUCTS,
            WebhookEvent.INVOICE_CREATED: EntityType.INVOICES,
            WebhookEvent.INVOICE_UPDATED: EntityType.INVOICES,
            WebhookEvent.INVOICE_DELETED: EntityType.INVOICES,
            WebhookEvent.ORDER_CREATED: EntityType.ORDERS,
            WebhookEvent.ORDER_UPDATED: EntityType.ORDERS,
            WebhookEvent.ORDER_DELETED: EntityType.ORDERS,
            WebhookEvent.CONTACT_CREATED: EntityType.CUSTOMERS,
            WebhookEvent.CONTACT_UPDATED: EntityType.CUSTOMERS,
            WebhookEvent.CONTACT_DELETED: EntityType.CUSTOMERS,
        }
        return mapping.get(event_type, EntityType.PRODUCTS)

    async def _process_webhooks(self):
        """Background worker to process webhooks from queue"""
        logger.info("Webhook processor worker started")

        while True:
            try:
                # Get webhook from queue
                webhook = await self._processing_queue.get()

                try:
                    # Process webhook
                    await self._process_webhook(webhook)

                    # Update stats
                    self._health_stats["total_processed"] += 1
                    self._health_stats["last_processed"] = datetime.utcnow().isoformat()

                except Exception as e:
                    logger.error(
                        f"Webhook processing error: {str(e)}",
                        exc_info=True
                    )
                    self._health_stats["total_failed"] += 1

                finally:
                    self._processing_queue.task_done()

            except asyncio.CancelledError:
                logger.info("Webhook processor worker stopped")
                break
            except Exception as e:
                logger.error(f"Webhook processor error: {str(e)}", exc_info=True)
                await asyncio.sleep(1)

    async def _process_webhook(self, webhook: WebhookPayload):
        """
        Process a webhook event

        Args:
            webhook: Webhook payload to process
        """
        logger.info(
            f"Processing webhook: {webhook.event_type} - {webhook.entity_id}"
        )

        # Call registered event handlers
        if webhook.event_type in self._event_handlers:
            for handler in self._event_handlers[webhook.event_type]:
                try:
                    await handler(webhook)
                except Exception as e:
                    logger.error(f"Event handler error: {str(e)}", exc_info=True)

        # Trigger sync for the specific entity
        sync_config = SyncConfig(
            entity_type=webhook.entity_type,
            mode=SyncMode.REALTIME,
            batch_size=1
        )

        await self.sync.sync_entity(
            config=sync_config,
            entity_ids=[webhook.entity_id]
        )

        # Publish webhook processed event
        await self._publish_event("tds.zoho.webhook.processed", {
            "event_id": webhook.event_id,
            "event_type": webhook.event_type,
            "entity_type": webhook.entity_type,
            "entity_id": webhook.entity_id
        })

    def register_handler(
        self,
        event_type: WebhookEvent,
        handler: Callable[[WebhookPayload], None]
    ):
        """
        Register a custom event handler

        Args:
            event_type: Event type to handle
            handler: Async callable to handle the event
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []

        self._event_handlers[event_type].append(handler)
        logger.info(f"Registered handler for {event_type}")

    async def _publish_event(self, event_type: str, data: Dict[str, Any]):
        """Publish event to event bus"""
        if self.event_bus:
            await self.event_bus.publish({
                "event_type": event_type,
                "module": "tds.zoho.webhooks",
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            })

    def get_health(self) -> Dict[str, Any]:
        """
        Get webhook manager health status

        Returns:
            dict: Health status and statistics
        """
        queue_size = self._processing_queue.qsize()

        return {
            **self._health_stats,
            "queue_size": queue_size,
            "is_healthy": queue_size < 1000,  # Consider unhealthy if queue too large
            "deduplication_enabled": self.enable_deduplication,
            "validation_enabled": self.enable_validation
        }

    def get_recent_webhooks(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent webhooks

        Args:
            limit: Maximum number of webhooks to return

        Returns:
            list: Recent webhook data
        """
        return list(self._recent_webhooks)[-limit:]
