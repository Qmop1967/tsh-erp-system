"""
Background Worker Manager
Manages background workers for Zoho sync and other async tasks
"""
import asyncio
import logging
from typing import List
from contextlib import asynccontextmanager

from app.background.zoho_sync_worker import SyncWorker

logger = logging.getLogger(__name__)


class WorkerManager:
    """
    Manager for background workers

    Handles:
    - Starting/stopping workers
    - Worker lifecycle
    - Graceful shutdown
    """

    def __init__(self, num_workers: int = 1):
        """
        Initialize worker manager

        Args:
            num_workers: Number of concurrent sync workers to run
        """
        self.num_workers = num_workers
        self.workers: List[SyncWorker] = []
        self.tasks: List[asyncio.Task] = []
        self.running = False

        logger.info(f"Worker manager initialized with {num_workers} workers")

    async def start(self):
        """Start all workers"""
        if self.running:
            logger.warning("Workers already running")
            return

        self.running = True
        logger.info(f"Starting {self.num_workers} workers...")

        # Create and start workers
        for i in range(self.num_workers):
            worker = SyncWorker(worker_id=f"worker-{i+1}")
            self.workers.append(worker)

            # Start worker as background task
            task = asyncio.create_task(worker.start())
            self.tasks.append(task)

            logger.info(f"Worker {i+1}/{self.num_workers} started")

        logger.info(f"✅ All {self.num_workers} workers started successfully")

    async def stop(self):
        """Stop all workers gracefully"""
        if not self.running:
            logger.warning("Workers not running")
            return

        logger.info(f"Stopping {len(self.workers)} workers...")
        self.running = False

        # Stop all workers
        for worker in self.workers:
            await worker.stop()

        # Wait for all tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)

        self.workers.clear()
        self.tasks.clear()

        logger.info("✅ All workers stopped")

    @asynccontextmanager
    async def lifespan(self):
        """
        Context manager for worker lifecycle

        Usage:
            async with worker_manager.lifespan():
                # Workers are running
                await some_work()
            # Workers are stopped
        """
        try:
            await self.start()
            yield
        finally:
            await self.stop()


# Global worker manager instance
worker_manager: WorkerManager = None


def init_worker_manager(num_workers: int = 1):
    """
    Initialize global worker manager

    Call this during application startup

    Args:
        num_workers: Number of concurrent workers
    """
    global worker_manager
    worker_manager = WorkerManager(num_workers=num_workers)
    logger.info("Worker manager initialized globally")


async def start_workers():
    """Start workers (called during app startup)"""
    if worker_manager:
        await worker_manager.start()
    else:
        logger.warning("Worker manager not initialized")


async def stop_workers():
    """Stop workers (called during app shutdown)"""
    if worker_manager:
        await worker_manager.stop()
    else:
        logger.warning("Worker manager not initialized")
