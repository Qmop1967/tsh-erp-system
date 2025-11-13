"""
Zoho Webhook Processor Service
================================

Adapter service for processing Zoho webhooks using TDS entity handlers.
This service bridges the gap between webhook routers and TDS background workers.

Author: TSH ERP Team
Date: November 7, 2025
Version: 2.0.0 (Migrated to TDS)
"""

import logging
import hashlib
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, insert

from app.models.zoho_sync import (
    TDSInboxEvent, TDSSyncQueue, SourceType, EntityType, EventStatus
)
from app.background.zoho_entity_handlers import EntityHandlerFactory

logger = logging.getLogger(__name__)


class ProcessorService:
    """
    Webhook Processor Service (TDS Adapter)

    Processes incoming webhooks by:
    1. Storing raw webhook in tds_inbox_events
    2. Validating and deduplicating
    3. Queuing for processing in tds_sync_queue
    4. Background workers handle actual sync
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize processor service

        Args:
            db: Async database session
        """
        self.db = db

    async def process_webhook(
        self,
        webhook: Any,
        source_type: str = "zoho",
        webhook_headers: Optional[Dict[str, str]] = None,
        ip_address: Optional[str] = None,
        signature_verified: bool = False
    ) -> Dict[str, Any]:
        """
        Process incoming webhook

        Args:
            webhook: Webhook event object
            source_type: Source system type (default: "zoho")
            webhook_headers: HTTP headers from webhook request
            ip_address: IP address of webhook sender
            signature_verified: Whether webhook signature was verified

        Returns:
            Dictionary with processing result:
            {
                "success": bool,
                "inbox_event_id": UUID (if successful),
                "idempotency_key": str,
                "queued": bool
            }

        Raises:
            ValueError: If webhook validation fails or duplicate detected
        """
        try:
            # Extract webhook data
            entity_type = webhook.entity_type
            entity_id = webhook.entity_id
            event_type = webhook.event_type
            payload_data = webhook.data if hasattr(webhook, 'data') else {}

            # Generate idempotency key
            idempotency_key = f"{source_type}:{entity_type}:{entity_id}:{event_type}"

            # Generate content hash
            content_str = json.dumps(payload_data, sort_keys=True)
            content_hash = hashlib.sha256(content_str.encode()).hexdigest()

            # Check for duplicate events (within 10 minutes)
            ten_minutes_ago = datetime.utcnow() - timedelta(minutes=10)

            duplicate_check = await self.db.execute(
                select(TDSInboxEvent).where(
                    TDSInboxEvent.idempotency_key == idempotency_key,
                    TDSInboxEvent.received_at >= ten_minutes_ago
                )
            )

            if duplicate_check.scalars().first():
                raise ValueError(f"Duplicate event detected: {idempotency_key}")

            # Store in inbox
            inbox_event = TDSInboxEvent(
                source_type=SourceType(source_type),
                entity_type=EntityType(entity_type),
                source_entity_id=str(entity_id),
                raw_payload=payload_data,
                idempotency_key=idempotency_key,
                content_hash=content_hash,
                webhook_headers=webhook_headers or {},
                ip_address=ip_address,
                signature_verified=signature_verified,
                received_at=datetime.utcnow()
            )

            self.db.add(inbox_event)
            await self.db.flush()

            # Queue for processing
            queue_item = TDSSyncQueue(
                inbox_event_id=inbox_event.id,
                source_type=SourceType(source_type),
                entity_type=EntityType(entity_type),
                source_entity_id=str(entity_id),
                event_type=event_type,
                payload=payload_data,
                status=EventStatus.PENDING,
                retry_count=0,
                queued_at=datetime.utcnow()
            )

            self.db.add(queue_item)
            await self.db.commit()

            logger.info(
                f"Webhook processed successfully: {entity_type}/{entity_id} "
                f"-> inbox:{inbox_event.id}, queue:{queue_item.id}"
            )

            return {
                "success": True,
                "inbox_event_id": str(inbox_event.id),
                "queue_item_id": str(queue_item.id),
                "idempotency_key": idempotency_key,
                "queued": True
            }

        except ValueError as e:
            # Validation or duplicate error - rollback
            await self.db.rollback()
            logger.warning(f"Webhook validation failed: {e}")
            raise

        except Exception as e:
            # Unexpected error - rollback
            await self.db.rollback()
            logger.error(f"Webhook processing failed: {e}", exc_info=True)
            raise

    async def process_sync_item(self, queue_item: TDSSyncQueue) -> Dict[str, Any]:
        """
        Process a sync queue item immediately (for testing/manual processing)

        Args:
            queue_item: Queue item to process

        Returns:
            Sync result dictionary
        """
        try:
            # Mark as processing
            queue_item.status = EventStatus.PROCESSING
            queue_item.processing_started_at = datetime.utcnow()
            await self.db.commit()

            # Get appropriate handler
            handler = EntityHandlerFactory.get_handler(
                entity_type=queue_item.entity_type.value,
                db=self.db
            )

            # Sync entity
            result = await handler.sync(
                payload=queue_item.payload,
                operation=queue_item.event_type
            )

            # Mark as completed
            queue_item.status = EventStatus.COMPLETED
            queue_item.processing_completed_at = datetime.utcnow()
            queue_item.local_entity_id = result.get("local_entity_id")
            queue_item.sync_result = result

            await self.db.commit()

            logger.info(f"Sync completed: {queue_item.entity_type}/{queue_item.source_entity_id}")

            return result

        except Exception as e:
            # Mark as failed
            queue_item.status = EventStatus.FAILED
            queue_item.error_message = str(e)
            queue_item.last_error_at = datetime.utcnow()
            queue_item.retry_count += 1

            await self.db.commit()

            logger.error(f"Sync failed: {queue_item.entity_type}/{queue_item.source_entity_id} - {e}")
            raise
