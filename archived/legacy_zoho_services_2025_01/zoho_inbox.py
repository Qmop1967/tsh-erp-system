"""
TDS Core - Inbox Service
Handles incoming webhook events and stores them in the inbox table
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.zoho_sync import TDSInboxEvent, SourceType, EntityType
from app.utils.hashing import generate_content_hash, generate_idempotency_key
from app.schemas.webhook_schemas import WebhookEvent

logger = logging.getLogger(__name__)


class InboxService:
    """Service for managing inbox events"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def store_webhook_event(
        self,
        webhook: WebhookEvent,
        source_type: str = "zoho",
        webhook_headers: Optional[Dict[str, str]] = None,
        ip_address: Optional[str] = None,
        signature_verified: bool = False
    ) -> TDSInboxEvent:
        """
        Store incoming webhook event to inbox

        Args:
            webhook: Validated webhook event
            source_type: Source system (default: "zoho")
            webhook_headers: HTTP headers from webhook request
            ip_address: Client IP address
            signature_verified: Whether webhook signature was verified

        Returns:
            Created inbox event

        Raises:
            ValueError: If duplicate event (same idempotency key)
        """
        try:
            # Generate idempotency key
            idempotency_key = generate_idempotency_key(
                source_type=source_type,
                entity_type=webhook.entity_type,
                entity_id=webhook.entity_id,
                operation=webhook.event_type
            )

            # Check for duplicate
            existing = await self._check_duplicate(idempotency_key)
            if existing:
                logger.info(f"Duplicate event detected: {idempotency_key}")
                raise ValueError(f"Duplicate event: {idempotency_key}")

            # Generate content hash (exclude timestamp fields)
            content_hash = generate_content_hash(
                webhook.data,
                exclude_fields=['updated_at', 'modified_at', 'last_modified', 'event_time']
            )

            # Create inbox event
            inbox_event = TDSInboxEvent(
                source_type=SourceType(source_type),
                entity_type=EntityType(webhook.entity_type),
                source_entity_id=webhook.entity_id,
                raw_payload=webhook.data,
                idempotency_key=idempotency_key,
                content_hash=content_hash,
                webhook_headers=webhook_headers or {},
                signature_verified=signature_verified,
                ip_address=ip_address,
                received_at=datetime.utcnow(),
                is_valid=False,  # Will be validated before queuing
                moved_to_queue=False
            )

            self.db.add(inbox_event)
            await self.db.commit()
            await self.db.refresh(inbox_event)

            logger.info(
                f"Inbox event stored: {inbox_event.id} "
                f"[{webhook.entity_type}:{webhook.entity_id}]"
            )

            return inbox_event

        except IntegrityError as e:
            # Database caught a duplicate that slipped through our check (race condition)
            await self.db.rollback()
            if "idempotency_key" in str(e):
                logger.info(f"Duplicate event caught by database: {idempotency_key}")
                raise ValueError(f"Duplicate event: {idempotency_key}")
            else:
                logger.error(f"Database integrity error: {e}")
                raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to store inbox event: {e}")
            raise

    async def _check_duplicate(self, idempotency_key: str) -> Optional[TDSInboxEvent]:
        """Check if event with same idempotency key already exists"""
        result = await self.db.execute(
            select(TDSInboxEvent)
            .where(TDSInboxEvent.idempotency_key == idempotency_key)
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def mark_as_processed(self, inbox_event_id: UUID) -> bool:
        """
        Mark inbox event as processed

        Args:
            inbox_event_id: Inbox event UUID

        Returns:
            True if marked successfully
        """
        try:
            result = await self.db.execute(
                select(TDSInboxEvent)
                .where(TDSInboxEvent.id == inbox_event_id)
            )
            inbox_event = result.scalar_one_or_none()

            if inbox_event:
                inbox_event.processed_at = datetime.utcnow()
                await self.db.commit()
                logger.debug(f"Inbox event marked as processed: {inbox_event_id}")
                return True

            return False

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to mark inbox event as processed: {e}")
            return False

    async def mark_as_valid(self, inbox_event_id: UUID, validation_errors: Optional[Dict] = None) -> bool:
        """
        Mark inbox event as valid or invalid

        Args:
            inbox_event_id: Inbox event UUID
            validation_errors: Validation errors if invalid (None if valid)

        Returns:
            True if marked successfully
        """
        try:
            result = await self.db.execute(
                select(TDSInboxEvent)
                .where(TDSInboxEvent.id == inbox_event_id)
            )
            inbox_event = result.scalar_one_or_none()

            if inbox_event:
                inbox_event.is_valid = validation_errors is None
                inbox_event.validation_errors = validation_errors
                await self.db.commit()
                logger.debug(
                    f"Inbox event validation: {inbox_event_id} "
                    f"[valid={inbox_event.is_valid}]"
                )
                return True

            return False

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to mark validation status: {e}")
            return False

    async def mark_as_queued(self, inbox_event_id: UUID) -> bool:
        """
        Mark inbox event as moved to queue

        Args:
            inbox_event_id: Inbox event UUID

        Returns:
            True if marked successfully
        """
        try:
            result = await self.db.execute(
                select(TDSInboxEvent)
                .where(TDSInboxEvent.id == inbox_event_id)
            )
            inbox_event = result.scalar_one_or_none()

            if inbox_event:
                inbox_event.moved_to_queue = True
                await self.db.commit()
                logger.debug(f"Inbox event marked as queued: {inbox_event_id}")
                return True

            return False

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to mark as queued: {e}")
            return False

    async def get_unprocessed_events(self, limit: int = 100) -> list[TDSInboxEvent]:
        """
        Get unprocessed inbox events

        Args:
            limit: Maximum number of events to return

        Returns:
            List of unprocessed inbox events
        """
        result = await self.db.execute(
            select(TDSInboxEvent)
            .where(
                TDSInboxEvent.processed_at == None,
                TDSInboxEvent.moved_to_queue == False
            )
            .order_by(TDSInboxEvent.received_at)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_event_by_id(self, inbox_event_id: UUID) -> Optional[TDSInboxEvent]:
        """Get inbox event by ID"""
        result = await self.db.execute(
            select(TDSInboxEvent)
            .where(TDSInboxEvent.id == inbox_event_id)
        )
        return result.scalar_one_or_none()

    async def get_event_by_idempotency_key(self, idempotency_key: str) -> Optional[TDSInboxEvent]:
        """Get inbox event by idempotency key"""
        result = await self.db.execute(
            select(TDSInboxEvent)
            .where(TDSInboxEvent.idempotency_key == idempotency_key)
        )
        return result.scalar_one_or_none()

    async def check_content_hash_exists(self, content_hash: str) -> bool:
        """
        Check if an event with the same content hash exists

        Useful for detecting duplicate data with different idempotency keys

        Args:
            content_hash: Content hash to check

        Returns:
            True if hash exists
        """
        result = await self.db.execute(
            select(TDSInboxEvent)
            .where(TDSInboxEvent.content_hash == content_hash)
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def get_inbox_stats(self) -> Dict[str, Any]:
        """
        Get inbox statistics

        Returns:
            Dictionary with inbox metrics
        """
        from sqlalchemy import func

        # Total events
        total_result = await self.db.execute(
            select(func.count(TDSInboxEvent.id))
        )
        total = total_result.scalar()

        # Processed events
        processed_result = await self.db.execute(
            select(func.count(TDSInboxEvent.id))
            .where(TDSInboxEvent.processed_at != None)
        )
        processed = processed_result.scalar()

        # Valid events
        valid_result = await self.db.execute(
            select(func.count(TDSInboxEvent.id))
            .where(TDSInboxEvent.is_valid == True)
        )
        valid = valid_result.scalar()

        # Queued events
        queued_result = await self.db.execute(
            select(func.count(TDSInboxEvent.id))
            .where(TDSInboxEvent.moved_to_queue == True)
        )
        queued = queued_result.scalar()

        # By entity type
        entity_type_result = await self.db.execute(
            select(
                TDSInboxEvent.entity_type,
                func.count(TDSInboxEvent.id)
            )
            .group_by(TDSInboxEvent.entity_type)
        )
        by_entity = {str(row[0]): row[1] for row in entity_type_result.all()}

        return {
            "total_events": total,
            "processed": processed,
            "unprocessed": total - processed,
            "valid": valid,
            "invalid": total - valid,
            "queued": queued,
            "by_entity_type": by_entity
        }
