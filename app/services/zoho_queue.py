"""
Zoho Sync Queue Service
========================

Service for managing the TDS sync queue (tds_sync_queue table).
Provides methods for fetching, updating, and managing queue items.

Author: TSH ERP Team
Date: November 7, 2025
Version: 2.0.0 (Migrated to TDS)
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.orm import selectinload

from app.models.zoho_sync import (
    TDSSyncQueue, TDSInboxEvent, EventStatus, SourceType, EntityType
)

logger = logging.getLogger(__name__)


class QueueService:
    """
    Queue Service for TDS Sync Queue Management

    Provides methods to:
    - Fetch pending queue items
    - Update queue item status
    - Handle retries and failures
    - Clean up old items
    - Get queue statistics
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize queue service

        Args:
            db: Async database session
        """
        self.db = db

    async def get_pending_items(
        self,
        batch_size: int = 10,
        entity_types: Optional[List[str]] = None,
        max_retry_count: int = 5
    ) -> List[TDSSyncQueue]:
        """
        Get pending queue items for processing

        Args:
            batch_size: Maximum number of items to fetch
            entity_types: Optional list of entity types to filter
            max_retry_count: Maximum retry count to include

        Returns:
            List of pending queue items
        """
        try:
            query = select(TDSSyncQueue).where(
                TDSSyncQueue.status == EventStatus.PENDING,
                TDSSyncQueue.retry_count < max_retry_count
            ).order_by(TDSSyncQueue.queued_at.asc()).limit(batch_size)

            if entity_types:
                query = query.where(TDSSyncQueue.entity_type.in_(entity_types))

            result = await self.db.execute(query)
            items = result.scalars().all()

            logger.debug(f"Fetched {len(items)} pending queue items")
            return list(items)

        except Exception as e:
            logger.error(f"Error fetching pending items: {e}", exc_info=True)
            return []

    async def mark_processing(self, queue_item: TDSSyncQueue) -> bool:
        """
        Mark queue item as processing

        Args:
            queue_item: Queue item to mark

        Returns:
            True if successful, False otherwise
        """
        try:
            queue_item.status = EventStatus.PROCESSING
            queue_item.processing_started_at = datetime.utcnow()

            await self.db.commit()
            return True

        except Exception as e:
            logger.error(f"Error marking item as processing: {e}")
            await self.db.rollback()
            return False

    async def mark_completed(
        self,
        queue_item: TDSSyncQueue,
        local_entity_id: Optional[str] = None,
        sync_result: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Mark queue item as completed

        Args:
            queue_item: Queue item to mark
            local_entity_id: Local entity ID (if applicable)
            sync_result: Sync result data

        Returns:
            True if successful, False otherwise
        """
        try:
            queue_item.status = EventStatus.COMPLETED
            queue_item.processing_completed_at = datetime.utcnow()
            queue_item.local_entity_id = local_entity_id
            queue_item.sync_result = sync_result or {}

            await self.db.commit()
            return True

        except Exception as e:
            logger.error(f"Error marking item as completed: {e}")
            await self.db.rollback()
            return False

    async def mark_failed(
        self,
        queue_item: TDSSyncQueue,
        error_message: str,
        should_retry: bool = True
    ) -> bool:
        """
        Mark queue item as failed

        Args:
            queue_item: Queue item to mark
            error_message: Error message
            should_retry: Whether to retry this item

        Returns:
            True if successful, False otherwise
        """
        try:
            queue_item.retry_count += 1
            queue_item.last_error_at = datetime.utcnow()
            queue_item.error_message = error_message

            # Determine final status
            if should_retry and queue_item.retry_count < 5:
                queue_item.status = EventStatus.RETRY
                queue_item.next_retry_at = datetime.utcnow() + timedelta(
                    minutes=2 ** queue_item.retry_count  # Exponential backoff
                )
            else:
                queue_item.status = EventStatus.DEAD_LETTER

            await self.db.commit()
            return True

        except Exception as e:
            logger.error(f"Error marking item as failed: {e}")
            await self.db.rollback()
            return False

    async def get_retry_items(self, batch_size: int = 10) -> List[TDSSyncQueue]:
        """
        Get items ready for retry

        Args:
            batch_size: Maximum number of items to fetch

        Returns:
            List of items ready for retry
        """
        try:
            now = datetime.utcnow()

            query = select(TDSSyncQueue).where(
                TDSSyncQueue.status == EventStatus.RETRY,
                TDSSyncQueue.next_retry_at <= now,
                TDSSyncQueue.retry_count < 5
            ).order_by(TDSSyncQueue.next_retry_at.asc()).limit(batch_size)

            result = await self.db.execute(query)
            items = result.scalars().all()

            logger.debug(f"Fetched {len(items)} retry items")
            return list(items)

        except Exception as e:
            logger.error(f"Error fetching retry items: {e}", exc_info=True)
            return []

    # ============================================================================
    # COMPATIBILITY METHODS FOR ZOHO_SYNC_WORKER
    # ============================================================================

    async def get_pending_events(
        self, limit: int = 100, priority_filter: Optional[int] = None
    ) -> List[TDSSyncQueue]:
        """
        Get pending events from queue (compatibility wrapper)

        Args:
            limit: Maximum number of events to return
            priority_filter: Optional minimum priority filter (not used in this implementation)

        Returns:
            List of pending queue entries
        """
        return await self.get_pending_items(batch_size=limit)

    async def get_retry_ready_events(self, limit: int = 100) -> List[TDSSyncQueue]:
        """
        Get events that are ready for retry (compatibility wrapper)

        Args:
            limit: Maximum number of events to return

        Returns:
            List of retry-ready queue entries
        """
        return await self.get_retry_items(batch_size=limit)

    async def get_queue_entry_by_id(self, queue_id: str) -> Optional[TDSSyncQueue]:
        """
        Get queue entry by ID

        Args:
            queue_id: Queue entry ID (UUID as string)

        Returns:
            Queue entry or None if not found
        """
        try:
            result = await self.db.execute(
                select(TDSSyncQueue).where(TDSSyncQueue.id == queue_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching queue entry {queue_id}: {e}")
            return None

    async def mark_as_processing(self, queue_id: str, worker_id: str) -> bool:
        """
        Mark queue entry as processing

        Args:
            queue_id: Queue entry ID
            worker_id: Worker ID

        Returns:
            True if successful, False otherwise
        """
        try:
            await self.db.execute(
                update(TDSSyncQueue)
                .where(TDSSyncQueue.id == queue_id)
                .values(
                    status=EventStatus.PROCESSING,
                    processing_started_at=datetime.utcnow(),
                )
            )
            await self.db.commit()
            logger.debug(f"Marked as processing: {queue_id} by {worker_id}")
            return True
        except Exception as e:
            logger.error(f"Error marking as processing: {e}")
            await self.db.rollback()
            return False

    async def mark_as_completed(
        self,
        queue_id: str,
        target_entity_id: Optional[str] = None,
        processing_result: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Mark queue entry as completed

        Args:
            queue_id: Queue entry ID
            target_entity_id: Local entity ID
            processing_result: Result of processing

        Returns:
            True if successful, False otherwise
        """
        try:
            await self.db.execute(
                update(TDSSyncQueue)
                .where(TDSSyncQueue.id == queue_id)
                .values(
                    status=EventStatus.COMPLETED,
                    processing_completed_at=datetime.utcnow(),
                    local_entity_id=target_entity_id,
                    sync_result=processing_result or {},
                )
            )
            await self.db.commit()
            logger.info(f"Marked as completed: {queue_id}")
            return True
        except Exception as e:
            logger.error(f"Error marking as completed: {e}")
            await self.db.rollback()
            return False

    async def mark_as_failed(
        self,
        queue_id: str,
        error_message: str,
        error_code: Optional[str] = None,
        should_retry: bool = True,
    ) -> bool:
        """
        Mark queue entry as failed

        Automatically handles retry logic and dead letter queue

        Args:
            queue_id: Queue entry ID
            error_message: Error description
            error_code: Optional error code
            should_retry: Whether to retry this item

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get queue entry
            queue_entry = await self.get_queue_entry_by_id(queue_id)
            if not queue_entry:
                logger.error(f"Queue entry not found: {queue_id}")
                return False

            # Increment retry count
            new_retry_count = (queue_entry.retry_count or 0) + 1

            # Determine if should move to dead letter queue
            max_attempts_reached = new_retry_count >= 5
            move_to_dlq = max_attempts_reached or not should_retry

            if move_to_dlq:
                # Move to dead letter queue
                await self.db.execute(
                    update(TDSSyncQueue)
                    .where(TDSSyncQueue.id == queue_id)
                    .values(
                        status=EventStatus.DEAD_LETTER,
                        error_message=error_message,
                        retry_count=new_retry_count,
                        last_error_at=datetime.utcnow(),
                    )
                )
                logger.error(f"Moved to dead letter queue: {queue_id} - {error_message}")
            else:
                # Schedule retry with exponential backoff
                retry_delay_minutes = 2 ** new_retry_count  # 2, 4, 8, 16...
                next_retry = datetime.utcnow() + timedelta(minutes=retry_delay_minutes)

                await self.db.execute(
                    update(TDSSyncQueue)
                    .where(TDSSyncQueue.id == queue_id)
                    .values(
                        status=EventStatus.RETRY,
                        error_message=error_message,
                        retry_count=new_retry_count,
                        next_retry_at=next_retry,
                        last_error_at=datetime.utcnow(),
                    )
                )
                logger.warning(
                    f"Scheduled for retry: {queue_id} "
                    f"(attempt {new_retry_count}, next retry in {retry_delay_minutes}min)"
                )

            await self.db.commit()
            return True

        except Exception as e:
            logger.error(f"Error marking as failed: {e}")
            await self.db.rollback()
            return False

    async def get_queue_stats(self) -> Dict[str, Any]:
        """
        Get queue statistics

        Returns:
            Dictionary with queue statistics
        """
        try:
            # Count by status
            status_counts = await self.db.execute(
                select(
                    TDSSyncQueue.status,
                    func.count(TDSSyncQueue.id)
                ).group_by(TDSSyncQueue.status)
            )

            stats = {
                "by_status": {row[0].value: row[1] for row in status_counts},
                "total": sum(row[1] for row in status_counts)
            }

            # Count by entity type
            entity_counts = await self.db.execute(
                select(
                    TDSSyncQueue.entity_type,
                    func.count(TDSSyncQueue.id)
                ).where(
                    TDSSyncQueue.status == EventStatus.PENDING
                ).group_by(TDSSyncQueue.entity_type)
            )

            stats["pending_by_entity"] = {
                row[0].value: row[1] for row in entity_counts
            }

            return stats

        except Exception as e:
            logger.error(f"Error getting queue stats: {e}", exc_info=True)
            return {}

    async def cleanup_old_items(self, days: int = 30) -> int:
        """
        Clean up old completed/failed items

        Args:
            days: Delete items older than this many days

        Returns:
            Number of items deleted
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            result = await self.db.execute(
                delete(TDSSyncQueue).where(
                    and_(
                        TDSSyncQueue.status.in_([EventStatus.COMPLETED, EventStatus.DEAD_LETTER]),
                        TDSSyncQueue.queued_at < cutoff_date
                    )
                )
            )

            await self.db.commit()

            deleted_count = result.rowcount
            logger.info(f"Cleaned up {deleted_count} old queue items")

            return deleted_count

        except Exception as e:
            logger.error(f"Error cleaning up old items: {e}")
            await self.db.rollback()
            return 0

    async def requeue_failed_item(self, queue_item_id: str) -> bool:
        """
        Manually requeue a failed item

        Args:
            queue_item_id: Queue item ID

        Returns:
            True if successful, False otherwise
        """
        try:
            result = await self.db.execute(
                update(TDSSyncQueue).where(
                    TDSSyncQueue.id == queue_item_id
                ).values(
                    status=EventStatus.PENDING,
                    retry_count=0,
                    error_message=None,
                    next_retry_at=None
                )
            )

            await self.db.commit()

            if result.rowcount > 0:
                logger.info(f"Requeued item: {queue_item_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error requeuing item: {e}")
            await self.db.rollback()
            return False
