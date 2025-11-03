"""
Zoho Processor Service
Orchestrates the complete workflow: Inbox → Validation → Queue → Processing
(Unified from TDS Core - now part of main ERP)
"""
import logging
from typing import Dict, Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

# Import from unified services
from app.services.zoho_inbox import InboxService
from app.services.zoho_queue import QueueService

# Import from TDS Core schemas (temporary - will be moved to app/schemas later)
from app.schemas.webhook_schemas import WebhookEvent

# Import from unified models
from app.models.zoho_sync import TDSInboxEvent, TDSSyncQueue

logger = logging.getLogger(__name__)


class ProcessorService:
    """Orchestrates the complete event processing workflow"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.inbox_service = InboxService(db)
        self.queue_service = QueueService(db)

    async def process_webhook(
        self,
        webhook: WebhookEvent,
        source_type: str = "zoho",
        webhook_headers: Optional[Dict[str, str]] = None,
        ip_address: Optional[str] = None,
        signature_verified: bool = False
    ) -> Dict[str, Any]:
        """
        Complete webhook processing workflow:
        1. Store in inbox
        2. Validate event
        3. Queue for processing

        Args:
            webhook: Validated webhook event
            source_type: Source system (default: "zoho")
            webhook_headers: HTTP headers
            ip_address: Client IP
            signature_verified: Whether signature was verified

        Returns:
            Dictionary with processing results

        Raises:
            ValueError: If webhook is duplicate or invalid
        """
        try:
            # Step 1: Store in inbox
            inbox_event = await self.inbox_service.store_webhook_event(
                webhook=webhook,
                source_type=source_type,
                webhook_headers=webhook_headers,
                ip_address=ip_address,
                signature_verified=signature_verified
            )

            logger.info(f"Step 1/3: Inbox event created: {inbox_event.id}")

            # Step 2: Validate event
            validation_result = await self._validate_event(inbox_event)

            if not validation_result["is_valid"]:
                # Mark as invalid and return
                await self.inbox_service.mark_as_valid(
                    inbox_event.id,
                    validation_errors=validation_result["errors"]
                )
                await self.inbox_service.mark_as_processed(inbox_event.id)

                logger.warning(
                    f"Event validation failed: {inbox_event.id} "
                    f"- {validation_result['errors']}"
                )

                return {
                    "success": False,
                    "inbox_event_id": inbox_event.id,
                    "idempotency_key": inbox_event.idempotency_key,
                    "queued": False,
                    "validation_errors": validation_result["errors"]
                }

            # Mark as valid
            await self.inbox_service.mark_as_valid(inbox_event.id, validation_errors=None)
            logger.info(f"Step 2/3: Event validated: {inbox_event.id}")

            # Step 3: Queue for processing
            queue_entry = await self.queue_service.enqueue_event(
                inbox_event=inbox_event,
                operation_type=webhook.event_type,
                priority=self._determine_priority(webhook.entity_type)
            )

            # Mark inbox event as queued
            await self.inbox_service.mark_as_queued(inbox_event.id)
            await self.inbox_service.mark_as_processed(inbox_event.id)

            logger.info(
                f"Step 3/3: Event queued: {queue_entry.id} "
                f"[priority={queue_entry.priority}]"
            )

            return {
                "success": True,
                "inbox_event_id": inbox_event.id,
                "queue_entry_id": queue_entry.id,
                "idempotency_key": inbox_event.idempotency_key,
                "queued": True,
                "priority": queue_entry.priority
            }

        except ValueError as e:
            # Duplicate or validation error
            logger.warning(f"Webhook processing failed: {e}")
            raise

        except Exception as e:
            # Unexpected error
            logger.error(f"Unexpected error processing webhook: {e}", exc_info=True)
            raise

    async def _validate_event(self, inbox_event: TDSInboxEvent) -> Dict[str, Any]:
        """
        Validate inbox event before queuing

        Args:
            inbox_event: Inbox event to validate

        Returns:
            Dictionary with validation result
        """
        errors = []

        # Validate entity type
        entity_type = str(inbox_event.entity_type)
        payload = inbox_event.raw_payload

        # Entity-specific validation
        if entity_type == "product":
            # Product must have item_id and name
            if "item_id" not in payload:
                errors.append("Missing required field: item_id")
            if "name" not in payload:
                errors.append("Missing required field: name")

        elif entity_type == "customer":
            # Customer must have contact_id and contact_name
            if "contact_id" not in payload:
                errors.append("Missing required field: contact_id")
            if "contact_name" not in payload:
                errors.append("Missing required field: contact_name")

        elif entity_type == "invoice":
            # Invoice must have invoice_id, invoice_number, customer_id
            if "invoice_id" not in payload:
                errors.append("Missing required field: invoice_id")
            if "invoice_number" not in payload:
                errors.append("Missing required field: invoice_number")
            if "customer_id" not in payload:
                errors.append("Missing required field: customer_id")

        elif entity_type == "bill":
            # Bill must have bill_id, bill_number, vendor_id
            if "bill_id" not in payload:
                errors.append("Missing required field: bill_id")
            if "bill_number" not in payload:
                errors.append("Missing required field: bill_number")
            if "vendor_id" not in payload:
                errors.append("Missing required field: vendor_id")

        # Add more entity-specific validations as needed

        return {
            "is_valid": len(errors) == 0,
            "errors": errors if errors else None
        }

    def _determine_priority(self, entity_type: str) -> int:
        """
        Determine queue priority based on entity type

        Priority scale: 1 (highest) to 10 (lowest)

        Args:
            entity_type: Entity type

        Returns:
            Priority value (1-10)
        """
        # Critical entities get high priority
        high_priority = ["invoice", "order"]
        if entity_type in high_priority:
            return 2

        # Standard entities
        medium_priority = ["product", "customer", "bill"]
        if entity_type in medium_priority:
            return 5

        # Low priority entities
        return 8

    async def reprocess_inbox_event(self, inbox_event_id: UUID) -> Dict[str, Any]:
        """
        Reprocess a failed or invalid inbox event

        Useful for manual retry of failed events

        Args:
            inbox_event_id: Inbox event UUID

        Returns:
            Dictionary with reprocessing results
        """
        try:
            # Get inbox event
            inbox_event = await self.inbox_service.get_event_by_id(inbox_event_id)

            if not inbox_event:
                raise ValueError(f"Inbox event not found: {inbox_event_id}")

            if inbox_event.moved_to_queue:
                raise ValueError(f"Event already queued: {inbox_event_id}")

            # Re-validate
            validation_result = await self._validate_event(inbox_event)

            if not validation_result["is_valid"]:
                await self.inbox_service.mark_as_valid(
                    inbox_event.id,
                    validation_errors=validation_result["errors"]
                )

                return {
                    "success": False,
                    "inbox_event_id": inbox_event.id,
                    "queued": False,
                    "validation_errors": validation_result["errors"]
                }

            # Mark as valid
            await self.inbox_service.mark_as_valid(inbox_event.id, validation_errors=None)

            # Queue for processing
            queue_entry = await self.queue_service.enqueue_event(
                inbox_event=inbox_event,
                operation_type="upsert",  # Default operation for reprocessing
                priority=3  # Higher priority for manual reprocessing
            )

            # Mark as queued
            await self.inbox_service.mark_as_queued(inbox_event.id)

            logger.info(f"Inbox event reprocessed: {inbox_event.id} → {queue_entry.id}")

            return {
                "success": True,
                "inbox_event_id": inbox_event.id,
                "queue_entry_id": queue_entry.id,
                "queued": True
            }

        except Exception as e:
            logger.error(f"Failed to reprocess inbox event: {e}")
            raise

    async def get_processing_stats(self) -> Dict[str, Any]:
        """
        Get overall processing statistics

        Returns:
            Dictionary with combined inbox and queue stats
        """
        inbox_stats = await self.inbox_service.get_inbox_stats()
        queue_stats = await self.queue_service.get_queue_stats()

        return {
            "inbox": inbox_stats,
            "queue": queue_stats,
            "health": {
                "inbox_processing_rate": (
                    inbox_stats["processed"] / inbox_stats["total_events"] * 100
                    if inbox_stats["total_events"] > 0 else 0
                ),
                "queue_pending": queue_stats["by_status"].get("pending", 0),
                "queue_failed": queue_stats["by_status"].get("failed", 0) +
                                queue_stats["by_status"].get("dead_letter", 0)
            }
        }
