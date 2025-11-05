"""
TDS Queue Service - Enhanced with Event Publishing
Manages the TDS sync queue with event-driven architecture
"""
import logging
from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_

from app.core.events.event_bus import event_bus
from app.tds.core.events import (
    TDSDeadLetterEvent,
    TDSQueueEmptyEvent,
)
from app.models.zoho_sync import (
    TDSInboxEvent,
    TDSSyncQueue,
    TDSDeadLetterQueue,
    TDSSyncLog,
    EventStatus,
    SourceType,
    EntityType,
    OperationType,
)

logger = logging.getLogger(__name__)


class TDSQueueService:
    """
    TDS Queue Service with Event Publishing

    Manages:
    - Queue entry lifecycle
    - Retry logic
    - Dead letter queue
    - Event publishing
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.event_bus = event_bus

    async def enqueue(
        self,
        inbox_event_id: UUID,
        entity_type: EntityType,
        source_entity_id: str,
        operation_type: OperationType,
        validated_payload: Dict[str, Any],
        priority: int = 5,
        max_retry_attempts: int = 3,
    ) -> TDSSyncQueue:
        """
        Add a new item to the sync queue

        Args:
            inbox_event_id: ID of the inbox event
            entity_type: Type of entity
            source_entity_id: Source system entity ID
            operation_type: Operation to perform
            validated_payload: Validated payload data
            priority: Queue priority (1-10, higher = more important)
            max_retry_attempts: Maximum retry attempts

        Returns:
            Created queue entry
        """
        queue_entry = TDSSyncQueue(
            id=uuid4(),
            inbox_event_id=inbox_event_id,
            entity_type=entity_type,
            source_entity_id=source_entity_id,
            operation_type=operation_type,
            validated_payload=validated_payload,
            status=EventStatus.PENDING,
            priority=priority,
            attempt_count=0,
            max_retry_attempts=max_retry_attempts,
        )

        self.db.add(queue_entry)
        await self.db.commit()
        await self.db.refresh(queue_entry)

        logger.info(
            f"Enqueued: {entity_type} {source_entity_id} "
            f"(id={queue_entry.id}, priority={priority})"
        )

        return queue_entry

    async def get_pending_events(
        self, limit: int = 100, priority_filter: Optional[int] = None
    ) -> List[TDSSyncQueue]:
        """
        Get pending events from queue

        Args:
            limit: Maximum number of events to return
            priority_filter: Optional minimum priority filter

        Returns:
            List of pending queue entries
        """
        query = (
            select(TDSSyncQueue)
            .where(
                and_(
                    TDSSyncQueue.status == EventStatus.PENDING,
                    TDSSyncQueue.locked_by == None,
                )
            )
            .order_by(TDSSyncQueue.priority.desc(), TDSSyncQueue.created_at.asc())
            .limit(limit)
        )

        if priority_filter:
            query = query.where(TDSSyncQueue.priority >= priority_filter)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_retry_ready_events(self, limit: int = 100) -> List[TDSSyncQueue]:
        """
        Get events that are ready for retry

        Args:
            limit: Maximum number of events to return

        Returns:
            List of retry-ready queue entries
        """
        now = datetime.utcnow()

        query = (
            select(TDSSyncQueue)
            .where(
                and_(
                    TDSSyncQueue.status == EventStatus.RETRY,
                    TDSSyncQueue.next_retry_at <= now,
                    TDSSyncQueue.locked_by == None,
                )
            )
            .order_by(TDSSyncQueue.priority.desc(), TDSSyncQueue.next_retry_at.asc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_queue_entry_by_id(self, queue_id: UUID) -> Optional[TDSSyncQueue]:
        """Get queue entry by ID"""
        result = await self.db.execute(
            select(TDSSyncQueue).where(TDSSyncQueue.id == queue_id)
        )
        return result.scalar_one_or_none()

    async def mark_as_processing(self, queue_id: UUID, worker_id: str):
        """
        Mark queue entry as processing

        Args:
            queue_id: Queue entry ID
            worker_id: Worker ID
        """
        await self.db.execute(
            update(TDSSyncQueue)
            .where(TDSSyncQueue.id == queue_id)
            .values(
                status=EventStatus.PROCESSING,
                started_at=datetime.utcnow(),
                attempt_count=TDSSyncQueue.attempt_count + 1,
            )
        )
        await self.db.commit()

        logger.debug(f"Marked as processing: {queue_id} by {worker_id}")

    async def mark_as_completed(
        self,
        queue_id: UUID,
        target_entity_id: Optional[str] = None,
        processing_result: Optional[Dict[str, Any]] = None,
    ):
        """
        Mark queue entry as completed

        Args:
            queue_id: Queue entry ID
            target_entity_id: Local entity ID
            processing_result: Result of processing
        """
        await self.db.execute(
            update(TDSSyncQueue)
            .where(TDSSyncQueue.id == queue_id)
            .values(
                status=EventStatus.COMPLETED,
                completed_at=datetime.utcnow(),
                target_entity_id=target_entity_id,
                processing_result=processing_result,
                locked_by=None,
                lock_expires_at=None,
            )
        )
        await self.db.commit()

        logger.info(f"Marked as completed: {queue_id}")

    async def mark_as_failed(
        self,
        queue_id: UUID,
        error_message: str,
        error_code: Optional[str] = None,
        should_retry: bool = True,
    ):
        """
        Mark queue entry as failed

        Automatically handles retry logic and dead letter queue

        Args:
            queue_id: Queue entry ID
            error_message: Error description
            error_code: Optional error code
            should_retry: Whether to retry this item
        """
        # Get queue entry
        queue_entry = await self.get_queue_entry_by_id(queue_id)
        if not queue_entry:
            logger.error(f"Queue entry not found: {queue_id}")
            return

        # Determine if should move to dead letter queue
        max_attempts_reached = queue_entry.attempt_count >= queue_entry.max_retry_attempts
        move_to_dlq = max_attempts_reached or not should_retry

        if move_to_dlq:
            # Move to dead letter queue
            await self._move_to_dead_letter_queue(
                queue_entry, error_message, error_code
            )

            await self.db.execute(
                update(TDSSyncQueue)
                .where(TDSSyncQueue.id == queue_id)
                .values(
                    status=EventStatus.DEAD_LETTER,
                    error_message=error_message,
                    error_code=error_code,
                    locked_by=None,
                    lock_expires_at=None,
                )
            )

            logger.error(f"Moved to dead letter queue: {queue_id} - {error_message}")
        else:
            # Schedule retry with exponential backoff
            retry_delay_minutes = 2 ** queue_entry.attempt_count  # 1, 2, 4, 8...
            next_retry = datetime.utcnow() + timedelta(minutes=retry_delay_minutes)

            await self.db.execute(
                update(TDSSyncQueue)
                .where(TDSSyncQueue.id == queue_id)
                .values(
                    status=EventStatus.RETRY,
                    error_message=error_message,
                    error_code=error_code,
                    next_retry_at=next_retry,
                    locked_by=None,
                    lock_expires_at=None,
                )
            )

            logger.warning(
                f"Scheduled for retry: {queue_id} "
                f"(attempt {queue_entry.attempt_count}, next retry in {retry_delay_minutes}min)"
            )

        await self.db.commit()

    async def _move_to_dead_letter_queue(
        self,
        queue_entry: TDSSyncQueue,
        error_message: str,
        error_code: Optional[str] = None,
    ):
        """
        Move a queue entry to the dead letter queue

        Args:
            queue_entry: Queue entry to move
            error_message: Error description
            error_code: Optional error code
        """
        dlq_entry = TDSDeadLetterQueue(
            id=uuid4(),
            sync_queue_id=queue_entry.id,
            entity_type=queue_entry.entity_type,
            source_entity_id=queue_entry.source_entity_id,
            failure_reason=error_message,
            error_code=error_code,
            total_attempts=queue_entry.attempt_count,
            last_error_message=error_message,
            last_payload=queue_entry.validated_payload,
            resolved=False,
        )

        self.db.add(dlq_entry)

        # Publish event
        event = TDSDeadLetterEvent(
            entity_type=str(queue_entry.entity_type),
            source_entity_id=queue_entry.source_entity_id,
            failure_reason=error_message,
            total_attempts=queue_entry.attempt_count,
        )
        await self.event_bus.publish(event)

        logger.error(
            f"Dead letter queue: {queue_entry.entity_type} "
            f"{queue_entry.source_entity_id} - {error_message}"
        )

    async def get_queue_depth(self) -> Dict[str, int]:
        """
        Get current queue depth by status

        Returns:
            Dictionary with counts by status
        """
        result = await self.db.execute(
            select(TDSSyncQueue.status, func.count(TDSSyncQueue.id)).group_by(
                TDSSyncQueue.status
            )
        )

        return {str(row[0]): row[1] for row in result.all()}

    async def cleanup_old_entries(self, days: int = 30):
        """
        Clean up old completed queue entries

        Args:
            days: Number of days to keep
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        result = await self.db.execute(
            delete(TDSSyncQueue).where(
                and_(
                    TDSSyncQueue.status == EventStatus.COMPLETED,
                    TDSSyncQueue.completed_at < cutoff_date,
                )
            )
        )

        deleted_count = result.rowcount
        await self.db.commit()

        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old queue entries")

        return deleted_count

    async def check_queue_health(self) -> Dict[str, Any]:
        """
        Check queue health and return metrics

        Returns:
            Dictionary with health metrics
        """
        # Get queue depths
        depths = await self.get_queue_depth()

        # Check for stale processing items (processing > 1 hour)
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        result = await self.db.execute(
            select(func.count(TDSSyncQueue.id)).where(
                and_(
                    TDSSyncQueue.status == EventStatus.PROCESSING,
                    TDSSyncQueue.started_at < one_hour_ago,
                )
            )
        )
        stale_count = result.scalar() or 0

        # Check dead letter queue size
        result = await self.db.execute(
            select(func.count(TDSDeadLetterQueue.id)).where(
                TDSDeadLetterQueue.resolved == False
            )
        )
        dlq_count = result.scalar() or 0

        # Determine health status
        is_healthy = stale_count == 0 and dlq_count < 100 and depths.get("pending", 0) < 10000

        return {
            "healthy": is_healthy,
            "queue_depths": depths,
            "stale_processing": stale_count,
            "dead_letter_queue": dlq_count,
            "warnings": [
                f"Stale processing items: {stale_count}" if stale_count > 0 else None,
                f"Large DLQ: {dlq_count} items" if dlq_count >= 100 else None,
                f"High pending queue: {depths.get('pending', 0)}" if depths.get('pending', 0) >= 10000 else None,
            ],
        }
