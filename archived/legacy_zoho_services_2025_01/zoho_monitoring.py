"""
TDS Core - Monitoring Service
System health monitoring and metrics collection
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from sqlalchemy import select, func, and_, text
from sqlalchemy.ext.asyncio import AsyncSession

from tds_core.core.database import AsyncSessionLocal
from app.models.zoho_sync import (
    TDSSyncQueue, TDSInboxEvent, TDSDeadLetterQueue,
    TDSSyncLog, EventStatus
)
from tds_core.services.alert_service import AlertService

logger = logging.getLogger(__name__)


class MonitoringService:
    """
    System monitoring and health checks

    Runs periodic checks and collects metrics
    """

    def __init__(self):
        self.running = False
        self.check_interval_seconds = 300  # 5 minutes
        self.last_check = None

    async def start(self):
        """Start monitoring loop"""
        self.running = True
        logger.info("📊 Monitoring service started")

        while self.running:
            try:
                await self._run_health_checks()
                await asyncio.sleep(self.check_interval_seconds)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(60)  # Wait 1 minute on error

    async def stop(self):
        """Stop monitoring"""
        self.running = False
        logger.info("📊 Monitoring service stopped")

    async def _run_health_checks(self):
        """Run all health checks"""
        async with AsyncSessionLocal() as db:
            alert_service = AlertService(db)

            logger.debug("Running health checks...")

            # 1. Queue health check
            queue_health = await alert_service.check_queue_health()
            logger.info(f"Queue health: {queue_health['status']}")

            # 2. Failure rate check
            failure_report = await alert_service.check_failure_rate(hours=1)
            logger.info(
                f"Failure rate (1h): {failure_report['failure_rate_percent']}% "
                f"({failure_report['failed']}/{failure_report['total_processed']})"
            )

            # 3. System metrics
            metrics = await self.get_system_metrics(db)
            logger.debug(f"System metrics: {metrics}")

            self.last_check = datetime.utcnow()

    async def get_system_metrics(self, db: AsyncSession) -> Dict[str, Any]:
        """
        Collect comprehensive system metrics

        Returns metrics for monitoring dashboards
        """
        # Queue metrics
        queue_metrics = await self._get_queue_metrics(db)

        # Processing metrics
        processing_metrics = await self._get_processing_metrics(db)

        # Database metrics
        db_metrics = await self._get_database_metrics(db)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "queue": queue_metrics,
            "processing": processing_metrics,
            "database": db_metrics
        }

    async def _get_queue_metrics(self, db: AsyncSession) -> Dict[str, Any]:
        """Get queue statistics"""
        # Count by status
        result = await db.execute(
            select(
                TDSSyncQueue.status,
                func.count().label("count")
            ).group_by(TDSSyncQueue.status)
        )

        by_status = {row.status: row.count for row in result}

        # Age of oldest pending
        result = await db.execute(
            select(func.min(TDSSyncQueue.queued_at)).where(
                TDSSyncQueue.status == EventStatus.PENDING
            )
        )
        oldest_pending = result.scalar()

        # Dead letter queue
        result = await db.execute(
            select(func.count()).select_from(TDSDeadLetterQueue)
        )
        dlq_count = result.scalar() or 0

        return {
            "by_status": by_status,
            "oldest_pending_age_seconds": (
                (datetime.utcnow() - oldest_pending).total_seconds()
                if oldest_pending else None
            ),
            "dead_letter_count": dlq_count
        }

    async def _get_processing_metrics(self, db: AsyncSession) -> Dict[str, Any]:
        """Get processing performance metrics"""
        # Last hour stats
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)

        result = await db.execute(
            select(
                func.count().label("total"),
                func.avg(
                    func.extract('epoch', TDSSyncQueue.completed_at - TDSSyncQueue.started_at)
                ).label("avg_duration_seconds"),
                func.sum(
                    func.case((TDSSyncQueue.status == EventStatus.COMPLETED, 1), else_=0)
                ).label("succeeded"),
                func.sum(
                    func.case((TDSSyncQueue.status == EventStatus.DEAD_LETTER, 1), else_=0)
                ).label("failed")
            ).where(
                and_(
                    TDSSyncQueue.completed_at >= one_hour_ago,
                    TDSSyncQueue.completed_at.isnot(None)
                )
            )
        )

        row = result.one()

        total = row.total or 0
        succeeded = row.succeeded or 0
        failed = row.failed or 0

        return {
            "last_hour": {
                "total_processed": total,
                "succeeded": succeeded,
                "failed": failed,
                "success_rate_percent": round(succeeded / total * 100, 2) if total > 0 else 100,
                "avg_duration_seconds": round(row.avg_duration_seconds, 2) if row.avg_duration_seconds else None
            }
        }

    async def _get_database_metrics(self, db: AsyncSession) -> Dict[str, Any]:
        """Get database statistics"""
        # Table sizes
        result = await db.execute(text("""
            SELECT
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
                pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes
            FROM pg_tables
            WHERE schemaname = 'public'
            AND tablename LIKE 'tds_%'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        """))

        table_sizes = [
            {
                "table": row.tablename,
                "size": row.size,
                "size_bytes": row.size_bytes
            }
            for row in result
        ]

        # Active connections
        result = await db.execute(text("""
            SELECT count(*) as active_connections
            FROM pg_stat_activity
            WHERE datname = current_database()
            AND state = 'active'
        """))

        active_connections = result.scalar()

        return {
            "table_sizes": table_sizes,
            "active_connections": active_connections
        }
