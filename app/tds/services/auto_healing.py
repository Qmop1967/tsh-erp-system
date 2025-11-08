"""
TDS Auto-Healing Service
=========================

Automatically detects and recovers from common failure scenarios.
Provides self-healing capabilities for the TDS system.

خدمة الإصلاح التلقائي لنظام TDS

Features:
- Stuck task detection and recovery
- Dead letter queue auto-retry
- Queue depth monitoring
- Automatic reprocessing
- Health-based recovery decisions

Author: TSH ERP Team
Date: November 9, 2025
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_, func

from app.models.zoho_sync import (
    TDSSyncQueue,
    TDSDeadLetterQueue,
    TDSAlert,
    EventStatus,
    AlertSeverity,
)
from app.tds.core.queue import TDSQueueService
from app.core.events.event_bus import event_bus

logger = logging.getLogger(__name__)


class AutoHealingService:
    """
    Auto-Healing Service for TDS
    خدمة الإصلاح التلقائي

    Automatically detects and recovers from failures:
    - Stuck tasks (processing > threshold)
    - Stale retries (retry time passed)
    - Dead letter queue items (eligible for retry)
    - Queue depth issues (too many pending)
    """

    def __init__(
        self,
        db: AsyncSession,
        stuck_task_threshold_minutes: int = 60,
        dlq_retry_after_hours: int = 24,
        max_dlq_retry_attempts: int = 3,
        queue_depth_warning: int = 1000,
        queue_depth_critical: int = 5000
    ):
        """
        Initialize auto-healing service

        Args:
            db: Database session
            stuck_task_threshold_minutes: Minutes before task considered stuck
            dlq_retry_after_hours: Hours before DLQ item eligible for retry
            max_dlq_retry_attempts: Max retry attempts for DLQ items
            queue_depth_warning: Queue depth warning threshold
            queue_depth_critical: Queue depth critical threshold
        """
        self.db = db
        self.stuck_threshold = timedelta(minutes=stuck_task_threshold_minutes)
        self.dlq_retry_after = timedelta(hours=dlq_retry_after_hours)
        self.max_dlq_retries = max_dlq_retry_attempts
        self.queue_warning = queue_depth_warning
        self.queue_critical = queue_depth_critical

        self.queue_service = TDSQueueService(db)

        # Statistics
        self.stats = {
            "stuck_tasks_recovered": 0,
            "dlq_items_retried": 0,
            "alerts_created": 0,
            "total_recoveries": 0,
            "last_run": None,
        }

    async def run_healing_cycle(self) -> Dict[str, Any]:
        """
        Run a complete healing cycle

        Returns:
            dict: Healing results
        """
        logger.info("🔧 Starting auto-healing cycle...")

        results = {
            "stuck_tasks": 0,
            "dlq_retries": 0,
            "alerts": 0,
            "timestamp": datetime.utcnow().isoformat()
        }

        try:
            # 1. Detect and recover stuck tasks
            stuck_count = await self.recover_stuck_tasks()
            results["stuck_tasks"] = stuck_count

            # 2. Retry eligible DLQ items
            dlq_count = await self.retry_dead_letter_queue()
            results["dlq_retries"] = dlq_count

            # 3. Check queue depth and create alerts
            alerts_count = await self.monitor_queue_depth()
            results["alerts"] = alerts_count

            # 4. Clean up expired locks
            await self.cleanup_expired_locks()

            # Update stats
            self.stats["stuck_tasks_recovered"] += stuck_count
            self.stats["dlq_items_retried"] += dlq_count
            self.stats["alerts_created"] += alerts_count
            self.stats["total_recoveries"] += stuck_count + dlq_count
            self.stats["last_run"] = datetime.utcnow().isoformat()

            logger.info(
                f"✅ Auto-healing cycle complete: "
                f"Stuck={stuck_count}, DLQ={dlq_count}, Alerts={alerts_count}"
            )

            # Publish healing event
            await event_bus.publish({
                "event_type": "tds.auto_healing.completed",
                "module": "tds.auto_healing",
                "data": results,
                "timestamp": datetime.utcnow().isoformat()
            })

        except Exception as e:
            logger.error(f"❌ Auto-healing cycle failed: {str(e)}", exc_info=True)
            results["error"] = str(e)

        return results

    async def recover_stuck_tasks(self) -> int:
        """
        Detect and recover stuck tasks

        A task is considered stuck if:
        - Status is PROCESSING
        - Started more than threshold minutes ago
        - Not locked by active worker

        Returns:
            int: Number of stuck tasks recovered
        """
        threshold_time = datetime.utcnow() - self.stuck_threshold

        # Find stuck tasks
        result = await self.db.execute(
            select(TDSSyncQueue).where(
                and_(
                    TDSSyncQueue.status == EventStatus.PROCESSING,
                    TDSSyncQueue.started_at < threshold_time
                )
            )
        )
        stuck_tasks = result.scalars().all()

        if not stuck_tasks:
            logger.debug("No stuck tasks found")
            return 0

        logger.warning(f"🔧 Found {len(stuck_tasks)} stuck tasks")

        recovered = 0
        for task in stuck_tasks:
            try:
                # Calculate how long it's been stuck
                stuck_duration = datetime.utcnow() - task.started_at
                stuck_minutes = int(stuck_duration.total_seconds() / 60)

                logger.warning(
                    f"Recovering stuck task: {task.id} "
                    f"(stuck for {stuck_minutes} minutes, "
                    f"entity={task.entity_type}, id={task.source_entity_id})"
                )

                # Mark as failed with retry
                await self.queue_service.mark_as_failed(
                    task.id,
                    error_message=f"Task stuck for {stuck_minutes} minutes - auto-recovery",
                    error_code="STUCK_TASK",
                    should_retry=True
                )

                recovered += 1

                # Create alert for stuck task
                await self._create_alert(
                    title=f"Stuck task recovered: {task.entity_type}",
                    message=f"Task {task.id} was stuck for {stuck_minutes} minutes and has been requeued",
                    severity=AlertSeverity.WARNING,
                    metadata={
                        "task_id": str(task.id),
                        "entity_type": str(task.entity_type),
                        "stuck_duration_minutes": stuck_minutes,
                    }
                )

            except Exception as e:
                logger.error(f"Failed to recover stuck task {task.id}: {str(e)}")

        await self.db.commit()
        return recovered

    async def retry_dead_letter_queue(self) -> int:
        """
        Retry eligible dead letter queue items

        Items are eligible if:
        - Not resolved
        - Created more than retry_after hours ago
        - Retry count < max_retry_attempts
        - Priority is medium or high

        Returns:
            int: Number of DLQ items retried
        """
        retry_threshold = datetime.utcnow() - self.dlq_retry_after

        # Find eligible DLQ items
        result = await self.db.execute(
            select(TDSDeadLetterQueue).where(
                and_(
                    TDSDeadLetterQueue.resolved == False,
                    TDSDeadLetterQueue.created_at < retry_threshold,
                    TDSDeadLetterQueue.retry_count < self.max_dlq_retries,
                    TDSDeadLetterQueue.priority.in_(['medium', 'high'])
                )
            ).limit(50)  # Limit to prevent overwhelming the queue
        )
        dlq_items = result.scalars().all()

        if not dlq_items:
            logger.debug("No DLQ items eligible for retry")
            return 0

        logger.info(f"🔄 Found {len(dlq_items)} DLQ items eligible for retry")

        retried = 0
        for dlq_item in dlq_items:
            try:
                logger.info(
                    f"Retrying DLQ item: {dlq_item.id} "
                    f"(entity={dlq_item.entity_type}, "
                    f"attempts={dlq_item.retry_count})"
                )

                # Get original sync queue entry
                result = await self.db.execute(
                    select(TDSSyncQueue).where(
                        TDSSyncQueue.id == dlq_item.sync_queue_id
                    )
                )
                original_task = result.scalar_one_or_none()

                if original_task:
                    # Reset task to retry
                    original_task.status = EventStatus.RETRY
                    original_task.next_retry_at = datetime.utcnow()
                    original_task.attempt_count = 0  # Reset attempts
                    original_task.error_message = f"Auto-retry from DLQ (attempt {dlq_item.retry_count + 1})"

                    # Update DLQ item
                    dlq_item.retry_count += 1
                    dlq_item.last_retry_at = datetime.utcnow()

                    retried += 1

            except Exception as e:
                logger.error(f"Failed to retry DLQ item {dlq_item.id}: {str(e)}")

        await self.db.commit()
        return retried

    async def monitor_queue_depth(self) -> int:
        """
        Monitor queue depth and create alerts

        Returns:
            int: Number of alerts created
        """
        # Get current queue depth
        depth = await self.queue_service.get_queue_depth()
        pending = depth.get("pending", 0)

        alerts_created = 0

        # Check warning threshold
        if pending >= self.queue_warning and pending < self.queue_critical:
            await self._create_alert(
                title="Queue depth warning",
                message=f"Queue has {pending} pending items (warning threshold: {self.queue_warning})",
                severity=AlertSeverity.WARNING,
                metadata={"queue_depth": pending, "threshold": self.queue_warning}
            )
            alerts_created += 1

        # Check critical threshold
        elif pending >= self.queue_critical:
            await self._create_alert(
                title="Queue depth critical",
                message=f"Queue has {pending} pending items (critical threshold: {self.queue_critical})",
                severity=AlertSeverity.CRITICAL,
                metadata={"queue_depth": pending, "threshold": self.queue_critical}
            )
            alerts_created += 1

        return alerts_created

    async def cleanup_expired_locks(self):
        """
        Clean up expired task locks

        Locks expire after 2 hours by default
        """
        expired_time = datetime.utcnow() - timedelta(hours=2)

        result = await self.db.execute(
            update(TDSSyncQueue)
            .where(
                and_(
                    TDSSyncQueue.locked_by.isnot(None),
                    TDSSyncQueue.lock_expires_at < expired_time
                )
            )
            .values(
                locked_by=None,
                lock_expires_at=None
            )
        )

        cleaned = result.rowcount
        if cleaned > 0:
            logger.info(f"🧹 Cleaned up {cleaned} expired task locks")
            await self.db.commit()

        return cleaned

    async def _create_alert(
        self,
        title: str,
        message: str,
        severity: AlertSeverity,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Create an alert in the database"""
        alert = TDSAlert(
            title=title,
            message=message,
            severity=severity,
            triggered_at=datetime.utcnow(),
            is_active=True,
            resolved=False,
            acknowledged=False,
            metadata=metadata or {}
        )

        self.db.add(alert)
        await self.db.commit()

        logger.info(f"🚨 Alert created: {title} ({severity})")

    def get_stats(self) -> Dict[str, Any]:
        """Get auto-healing statistics"""
        return {
            **self.stats,
            "configuration": {
                "stuck_threshold_minutes": int(self.stuck_threshold.total_seconds() / 60),
                "dlq_retry_after_hours": int(self.dlq_retry_after.total_seconds() / 3600),
                "max_dlq_retries": self.max_dlq_retries,
                "queue_warning_threshold": self.queue_warning,
                "queue_critical_threshold": self.queue_critical,
            }
        }


class AutoHealingScheduler:
    """
    Scheduler for running auto-healing cycles periodically
    جدولة الإصلاح التلقائي
    """

    def __init__(
        self,
        db: AsyncSession,
        interval_minutes: int = 5,
        healing_service: Optional[AutoHealingService] = None
    ):
        """
        Initialize auto-healing scheduler

        Args:
            db: Database session
            interval_minutes: Minutes between healing cycles
            healing_service: Optional healing service instance
        """
        self.db = db
        self.interval = timedelta(minutes=interval_minutes)
        self.healing_service = healing_service or AutoHealingService(db)
        self._task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        """Start the auto-healing scheduler"""
        if self._running:
            logger.warning("Auto-healing scheduler already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info(f"🔧 Auto-healing scheduler started (interval: {self.interval})")

    async def stop(self):
        """Stop the auto-healing scheduler"""
        if not self._running:
            return

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("🔧 Auto-healing scheduler stopped")

    async def _run_loop(self):
        """Run healing cycles in a loop"""
        while self._running:
            try:
                # Run healing cycle
                await self.healing_service.run_healing_cycle()

                # Wait for next cycle
                await asyncio.sleep(self.interval.total_seconds())

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Auto-healing loop error: {str(e)}", exc_info=True)
                await asyncio.sleep(60)  # Wait 1 minute on error

    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            "running": self._running,
            "interval_minutes": int(self.interval.total_seconds() / 60),
            "healing_stats": self.healing_service.get_stats()
        }
