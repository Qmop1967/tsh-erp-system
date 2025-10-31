"""
TDS Core - Queue Service
Manages the sync queue for event processing
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import UUID

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.tds_models import (
    TDSSyncQueue,
    TDSInboxEvent,
    EventStatus,
    EntityType,
    OperationType
)
from core.config import settings
from utils.retry import calculate_next_retry_time

logger = logging.getLogger(__name__)


class QueueService:
    """Service for managing sync queue"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def enqueue_event(
        self,
        inbox_event: TDSInboxEvent,
        operation_type: str = "upsert",
        priority: int = 5,
        sync_run_id: Optional[UUID] = None
    ) -> TDSSyncQueue:
        """
        Add validated event to sync queue

        Args:
            inbox_event: Validated inbox event
            operation_type: Operation type (create, update, delete, upsert)
            priority: Queue priority (1=highest, 10=lowest)
            sync_run_id: Optional sync run ID for batch operations

        Returns:
            Created queue entry

        Raises:
            ValueError: If inbox event is invalid or already queued
        """
        try:
            # Validate inbox event
            if not inbox_event.is_valid:
                raise ValueError("Cannot queue invalid inbox event")

            if inbox_event.moved_to_queue:
                raise ValueError("Inbox event already queued")

            # Create queue entry
            queue_entry = TDSSyncQueue(
                inbox_event_id=inbox_event.id,
                sync_run_id=sync_run_id,
                entity_type=inbox_event.entity_type,
                source_entity_id=inbox_event.source_entity_id,
                operation_type=OperationType(operation_type),
                validated_payload=inbox_event.raw_payload,
                status=EventStatus.PENDING,
                priority=priority,
                attempt_count=0,
                max_retry_attempts=settings.tds_max_retry_attempts,
                next_retry_at=None,
                created_at=datetime.utcnow()
            )

            self.db.add(queue_entry)
            await self.db.commit()
            await self.db.refresh(queue_entry)

            logger.info(
                f"Event queued: {queue_entry.id} "
                f"[{inbox_event.entity_type}:{inbox_event.source_entity_id}]"
            )

            return queue_entry

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to enqueue event: {e}")
            raise

    async def get_pending_events(
        self,
        limit: int = 100,
        entity_type: Optional[str] = None,
        priority_min: int = 1
    ) -> List[TDSSyncQueue]:
        """
        Get pending events from queue

        Args:
            limit: Maximum number of events to return
            entity_type: Filter by entity type (optional)
            priority_min: Minimum priority (1=highest)

        Returns:
            List of pending queue entries ordered by priority and creation time
        """
        query = (
            select(TDSSyncQueue)
            .where(
                TDSSyncQueue.status == EventStatus.PENDING,
                TDSSyncQueue.locked_by == None,
                TDSSyncQueue.priority >= priority_min
            )
            .order_by(
                TDSSyncQueue.priority.asc(),  # Higher priority first
                TDSSyncQueue.created_at.asc()  # Older events first
            )
            .limit(limit)
        )

        if entity_type:
            query = query.where(TDSSyncQueue.entity_type == EntityType(entity_type))

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_retry_ready_events(self, limit: int = 100) -> List[TDSSyncQueue]:
        """
        Get events ready for retry

        Returns events in 'retry' status where next_retry_at has passed

        Args:
            limit: Maximum number of events to return

        Returns:
            List of retry-ready queue entries
        """
        result = await self.db.execute(
            select(TDSSyncQueue)
            .where(
                TDSSyncQueue.status == EventStatus.RETRY,
                TDSSyncQueue.next_retry_at <= datetime.utcnow(),
                TDSSyncQueue.locked_by == None
            )
            .order_by(TDSSyncQueue.next_retry_at.asc())
            .limit(limit)
        )
        return result.scalars().all()

    async def mark_as_processing(
        self,
        queue_id: UUID,
        worker_id: str
    ) -> bool:
        """
        Mark queue entry as processing

        Args:
            queue_id: Queue entry UUID
            worker_id: Worker identifier

        Returns:
            True if marked successfully
        """
        try:
            result = await self.db.execute(
                select(TDSSyncQueue)
                .where(TDSSyncQueue.id == queue_id)
            )
            queue_entry = result.scalar_one_or_none()

            if queue_entry:
                queue_entry.status = EventStatus.PROCESSING
                queue_entry.started_at = datetime.utcnow()
                queue_entry.locked_by = worker_id
                await self.db.commit()
                logger.debug(f"Queue entry marked as processing: {queue_id}")
                return True

            return False

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to mark as processing: {e}")
            return False

    async def mark_as_completed(
        self,
        queue_id: UUID,
        target_entity_id: Optional[str] = None,
        processing_result: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Mark queue entry as completed successfully

        Args:
            queue_id: Queue entry UUID
            target_entity_id: Target entity ID in local database
            processing_result: Processing result details

        Returns:
            True if marked successfully
        """
        try:
            result = await self.db.execute(
                select(TDSSyncQueue)
                .where(TDSSyncQueue.id == queue_id)
            )
            queue_entry = result.scalar_one_or_none()

            if queue_entry:
                queue_entry.status = EventStatus.COMPLETED
                queue_entry.completed_at = datetime.utcnow()
                queue_entry.target_entity_id = target_entity_id
                queue_entry.processing_result = processing_result
                queue_entry.locked_by = None
                queue_entry.lock_expires_at = None
                await self.db.commit()
                logger.info(f"Queue entry completed: {queue_id}")
                return True

            return False

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to mark as completed: {e}")
            return False

    async def mark_as_failed(
        self,
        queue_id: UUID,
        error_message: str,
        error_code: Optional[str] = None,
        should_retry: bool = True
    ) -> bool:
        """
        Mark queue entry as failed and schedule retry if applicable

        Args:
            queue_id: Queue entry UUID
            error_message: Error description
            error_code: Error code (optional)
            should_retry: Whether to retry this event

        Returns:
            True if marked successfully
        """
        try:
            result = await self.db.execute(
                select(TDSSyncQueue)
                .where(TDSSyncQueue.id == queue_id)
            )
            queue_entry = result.scalar_one_or_none()

            if not queue_entry:
                return False

            # Increment attempt count
            queue_entry.attempt_count += 1
            queue_entry.error_message = error_message
            queue_entry.error_code = error_code
            queue_entry.locked_by = None
            queue_entry.lock_expires_at = None

            # Check if should retry
            if should_retry and queue_entry.attempt_count < queue_entry.max_retry_attempts:
                # Schedule retry with exponential backoff
                queue_entry.status = EventStatus.RETRY
                queue_entry.next_retry_at = calculate_next_retry_time(
                    queue_entry.attempt_count,
                    settings.tds_retry_backoff_base_ms,
                    settings.tds_retry_backoff_max_ms
                )
                logger.warning(
                    f"Queue entry scheduled for retry: {queue_id} "
                    f"(attempt {queue_entry.attempt_count}/{queue_entry.max_retry_attempts})"
                )
            else:
                # Max retries reached or non-retryable error
                queue_entry.status = EventStatus.DEAD_LETTER
                queue_entry.completed_at = datetime.utcnow()
                logger.error(
                    f"Queue entry moved to dead letter: {queue_id} "
                    f"(attempts: {queue_entry.attempt_count})"
                )

            await self.db.commit()
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to mark as failed: {e}")
            return False

    async def get_queue_entry_by_id(self, queue_id: UUID) -> Optional[TDSSyncQueue]:
        """Get queue entry by ID"""
        result = await self.db.execute(
            select(TDSSyncQueue)
            .where(TDSSyncQueue.id == queue_id)
        )
        return result.scalar_one_or_none()

    async def get_queue_stats(self) -> Dict[str, Any]:
        """
        Get queue statistics

        Returns:
            Dictionary with queue metrics
        """
        # Total by status
        status_result = await self.db.execute(
            select(
                TDSSyncQueue.status,
                func.count(TDSSyncQueue.id)
            )
            .group_by(TDSSyncQueue.status)
        )
        by_status = {str(row[0]): row[1] for row in status_result.all()}

        # Total by entity type
        entity_result = await self.db.execute(
            select(
                TDSSyncQueue.entity_type,
                func.count(TDSSyncQueue.id)
            )
            .group_by(TDSSyncQueue.entity_type)
        )
        by_entity = {str(row[0]): row[1] for row in entity_result.all()}

        # By priority
        priority_result = await self.db.execute(
            select(
                TDSSyncQueue.priority,
                func.count(TDSSyncQueue.id)
            )
            .group_by(TDSSyncQueue.priority)
        )
        by_priority = {row[0]: row[1] for row in priority_result.all()}

        # Oldest pending
        oldest_result = await self.db.execute(
            select(func.min(TDSSyncQueue.created_at))
            .where(TDSSyncQueue.status == EventStatus.PENDING)
        )
        oldest_pending = oldest_result.scalar()

        # Total events
        total = sum(by_status.values())

        return {
            "total_events": total,
            "by_status": by_status,
            "by_entity_type": by_entity,
            "by_priority": by_priority,
            "oldest_pending": oldest_pending.isoformat() if oldest_pending else None
        }

    async def cleanup_old_completed(self, days: int = 7) -> int:
        """
        Clean up old completed queue entries

        Args:
            days: Delete entries completed more than this many days ago

        Returns:
            Number of entries deleted
        """
        try:
            from datetime import timedelta

            cutoff_date = datetime.utcnow() - timedelta(days=days)

            result = await self.db.execute(
                select(TDSSyncQueue)
                .where(
                    TDSSyncQueue.status == EventStatus.COMPLETED,
                    TDSSyncQueue.completed_at < cutoff_date
                )
            )
            entries_to_delete = result.scalars().all()

            for entry in entries_to_delete:
                await self.db.delete(entry)

            await self.db.commit()

            deleted_count = len(entries_to_delete)
            logger.info(f"Cleaned up {deleted_count} old completed queue entries")
            return deleted_count

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to cleanup old entries: {e}")
            return 0
