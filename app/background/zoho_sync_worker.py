"""
Zoho Sync Worker (Unified from TDS Core)
Background worker for processing sync queue events
"""
import asyncio
import logging
import time
from uuid import uuid4
from typing import Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import AsyncSessionLocal
from app.core.config import settings
from app.services.zoho_queue import QueueService
from app.background.zoho_entity_handlers import EntityHandlerFactory
from app.utils.locking import acquire_lock, release_lock, cleanup_expired_locks
from app.utils.retry import should_retry, is_transient_error

logger = logging.getLogger(__name__)


class SyncWorker:
    """
    Background worker for processing sync queue

    Features:
    - Processes events from tds_sync_queue
    - Distributed locking for concurrent workers
    - Automatic retry with exponential backoff
    - Dead letter queue for permanent failures
    - Graceful shutdown
    """

    def __init__(
        self,
        worker_id: Optional[str] = None,
        batch_size: int = None,
        poll_interval_ms: int = None
    ):
        """
        Initialize sync worker

        Args:
            worker_id: Unique worker identifier (auto-generated if None)
            batch_size: Number of events to process per batch
            poll_interval_ms: Polling interval in milliseconds
        """
        self.worker_id = worker_id or f"worker-{uuid4().hex[:8]}"
        self.batch_size = batch_size or settings.tds_batch_size
        self.poll_interval_ms = poll_interval_ms or settings.tds_queue_poll_interval_ms
        self.running = False
        self.stats = {
            "processed": 0,
            "succeeded": 0,
            "failed": 0,
            "retried": 0,
            "dead_lettered": 0,
            "start_time": None
        }

        logger.info(
            f"Sync worker initialized: {self.worker_id} "
            f"[batch_size={self.batch_size}, poll_interval={self.poll_interval_ms}ms]"
        )

    async def start(self):
        """
        Start the worker

        Runs continuously until stopped
        """
        self.running = True
        self.stats["start_time"] = time.time()

        logger.info(f"🚀 Sync worker {self.worker_id} started")

        try:
            while self.running:
                try:
                    # Process a batch of events
                    processed = await self._process_batch()

                    # If no events processed, wait before polling again
                    if processed == 0:
                        await asyncio.sleep(self.poll_interval_ms / 1000)

                except Exception as e:
                    logger.error(f"Error in worker loop: {e}", exc_info=True)
                    # Wait before retrying to avoid tight error loop
                    await asyncio.sleep(5)

        finally:
            logger.info(f"🛑 Sync worker {self.worker_id} stopped")
            self._print_stats()

    async def stop(self):
        """Stop the worker gracefully"""
        logger.info(f"Stopping worker {self.worker_id}...")
        self.running = False

    async def _process_batch(self) -> int:
        """
        Process a batch of pending events

        Returns:
            Number of events processed
        """
        async with AsyncSessionLocal() as db:
            queue_service = QueueService(db)

            # Get pending events (includes retry-ready events)
            pending_events = await queue_service.get_pending_events(limit=self.batch_size)
            retry_events = await queue_service.get_retry_ready_events(limit=self.batch_size)

            # Combine and limit to batch size
            all_events = (pending_events + retry_events)[:self.batch_size]

            if not all_events:
                return 0

            logger.debug(f"Processing batch of {len(all_events)} events")

            # Process each event
            for queue_entry in all_events:
                await self._process_event(queue_entry.id)

            return len(all_events)

    async def _process_event(self, queue_id: str):
        """
        Process a single queue event

        Args:
            queue_id: Queue entry UUID
        """
        start_time = time.time()

        async with AsyncSessionLocal() as db:
            try:
                queue_service = QueueService(db)

                # Get queue entry
                queue_entry = await queue_service.get_queue_entry_by_id(queue_id)
                if not queue_entry:
                    logger.warning(f"Queue entry not found: {queue_id}")
                    return

                # Try to acquire lock
                lock_acquired = await acquire_lock(
                    db=db,
                    queue_id=queue_id,
                    worker_id=self.worker_id,
                    lock_duration_seconds=settings.tds_lock_timeout_seconds
                )

                if not lock_acquired:
                    logger.debug(f"Could not acquire lock for {queue_id} (already locked)")
                    return

                # Mark as processing
                await queue_service.mark_as_processing(queue_id, self.worker_id)

                logger.info(
                    f"Processing event: {queue_id} "
                    f"[{queue_entry.entity_type}:{queue_entry.source_entity_id}] "
                    f"(attempt {queue_entry.attempt_count + 1})"
                )

                # Get entity handler
                handler = EntityHandlerFactory.get_handler(
                    str(queue_entry.entity_type),
                    db
                )

                # Execute sync
                result = await handler.sync(
                    payload=queue_entry.validated_payload,
                    operation=str(queue_entry.operation_type)
                )

                # Mark as completed
                await queue_service.mark_as_completed(
                    queue_id=queue_id,
                    target_entity_id=result.get("local_entity_id"),
                    processing_result=result
                )

                # Release lock
                await release_lock(db, queue_id, self.worker_id)

                # Update stats
                self.stats["processed"] += 1
                self.stats["succeeded"] += 1

                duration_ms = (time.time() - start_time) * 1000
                logger.info(
                    f"✅ Event processed successfully: {queue_id} "
                    f"[{duration_ms:.2f}ms]"
                )

            except Exception as e:
                # Handle failure
                await self._handle_failure(queue_id, e, db)

                # Update stats
                self.stats["processed"] += 1
                self.stats["failed"] += 1

                logger.error(
                    f"❌ Event processing failed: {queue_id} - {e}",
                    exc_info=True
                )

    async def _handle_failure(
        self,
        queue_id: str,
        error: Exception,
        db: AsyncSession
    ):
        """
        Handle event processing failure

        Determines whether to retry or move to dead letter queue

        Args:
            queue_id: Queue entry UUID
            error: Exception that occurred
            db: Database session
        """
        try:
            queue_service = QueueService(db)
            queue_entry = await queue_service.get_queue_entry_by_id(queue_id)

            if not queue_entry:
                return

            # Determine error code
            error_code = getattr(error, 'code', None) or type(error).__name__

            # Determine if should retry
            is_retryable = should_retry(
                attempt_count=queue_entry.attempt_count + 1,
                max_attempts=queue_entry.max_retry_attempts,
                error_code=error_code
            )

            # Also check if error is transient
            if is_retryable and not is_transient_error(error):
                # Non-transient error, don't retry
                is_retryable = False

            # Mark as failed (will auto-retry or dead-letter based on is_retryable)
            await queue_service.mark_as_failed(
                queue_id=queue_id,
                error_message=str(error),
                error_code=error_code,
                should_retry=is_retryable
            )

            # Release lock
            try:
                await release_lock(db, queue_id, self.worker_id)
            except:
                pass  # Lock may have already expired

            # Update stats
            if is_retryable:
                self.stats["retried"] += 1
                logger.warning(
                    f"Event will be retried: {queue_id} "
                    f"(attempt {queue_entry.attempt_count + 1})"
                )
            else:
                self.stats["dead_lettered"] += 1
                logger.error(
                    f"Event moved to dead letter queue: {queue_id} "
                    f"(non-retryable or max attempts reached)"
                )

        except Exception as e:
            logger.error(f"Error handling failure for {queue_id}: {e}", exc_info=True)

    def _print_stats(self):
        """Print worker statistics"""
        if self.stats["start_time"]:
            runtime = time.time() - self.stats["start_time"]
            runtime_str = f"{runtime:.1f}s"
        else:
            runtime_str = "N/A"

        logger.info(
            f"📊 Worker {self.worker_id} stats:\n"
            f"  Runtime: {runtime_str}\n"
            f"  Processed: {self.stats['processed']}\n"
            f"  Succeeded: {self.stats['succeeded']}\n"
            f"  Failed: {self.stats['failed']}\n"
            f"  Retried: {self.stats['retried']}\n"
            f"  Dead Lettered: {self.stats['dead_lettered']}"
        )

    async def cleanup_expired_locks_task(self):
        """
        Periodic task to cleanup expired locks

        Runs every 60 seconds to release locks from crashed workers
        """
        while self.running:
            try:
                async with AsyncSessionLocal() as db:
                    cleaned = await cleanup_expired_locks(db)
                    if cleaned > 0:
                        logger.info(f"Cleaned up {cleaned} expired locks")
            except Exception as e:
                logger.error(f"Error cleaning up locks: {e}")

            # Wait 60 seconds
            await asyncio.sleep(60)


# ============================================================================
# STANDALONE WORKER SCRIPT
# ============================================================================

async def run_worker():
    """
    Run a single worker instance

    Usage:
        python -m workers.sync_worker
    """
    # Create worker
    worker = SyncWorker()

    # Create cleanup task
    cleanup_task = asyncio.create_task(worker.cleanup_expired_locks_task())

    try:
        # Run worker (blocks until stopped)
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, stopping worker...")
        await worker.stop()
    finally:
        # Cancel cleanup task
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Run worker
    asyncio.run(run_worker())
