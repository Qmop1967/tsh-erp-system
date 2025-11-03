"""
TDS Core - Alert Service
Monitoring, alerting, and notification system
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.zoho_sync import TDSAlert, TDSSyncQueue, TDSDeadLetterQueue, EventStatus
from tds_core.core.config import settings

logger = logging.getLogger(__name__)


class AlertService:
    """
    Alert and monitoring service

    Features:
    - Monitors queue health
    - Tracks failure rates
    - Creates alerts for anomalies
    - Sends notifications (email, Slack, etc.)
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ========================================================================
    # ALERT MANAGEMENT
    # ========================================================================

    async def create_alert(
        self,
        severity: str,
        title: str,
        message: str,
        alert_type: str = "system",
        metadata: Optional[Dict[str, Any]] = None,
        queue_id: Optional[UUID] = None
    ) -> TDSAlert:
        """
        Create a new alert

        Args:
            severity: critical, warning, info
            title: Alert title
            message: Detailed message
            alert_type: Type of alert (system, queue, performance, etc.)
            metadata: Additional context
            queue_id: Related queue entry if applicable
        """
        alert = TDSAlert(
            severity=severity,
            title=title,
            message=message,
            alert_type=alert_type,
            metadata=metadata or {},
            queue_id=queue_id,
            acknowledged=False
        )

        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)

        logger.warning(f"🚨 Alert created: [{severity.upper()}] {title}")

        # Send notification if critical
        if severity == "critical":
            await self._send_notification(alert)

        return alert

    async def acknowledge_alert(self, alert_id: UUID) -> bool:
        """Mark alert as acknowledged"""
        result = await self.db.execute(
            select(TDSAlert).where(TDSAlert.id == alert_id)
        )
        alert = result.scalar_one_or_none()

        if alert:
            alert.acknowledged = True
            alert.acknowledged_at = datetime.utcnow()
            await self.db.commit()
            return True

        return False

    async def get_active_alerts(
        self,
        severity: Optional[str] = None,
        acknowledged: bool = False
    ) -> List[TDSAlert]:
        """Get active alerts"""
        query = select(TDSAlert).where(TDSAlert.acknowledged == acknowledged)

        if severity:
            query = query.where(TDSAlert.severity == severity)

        query = query.order_by(TDSAlert.created_at.desc()).limit(100)

        result = await self.db.execute(query)
        return result.scalars().all()

    # ========================================================================
    # HEALTH MONITORING
    # ========================================================================

    async def check_queue_health(self) -> Dict[str, Any]:
        """
        Check queue health and create alerts if needed

        Monitors:
        - Queue size (pending events)
        - Processing rate
        - Failure rate
        - Dead letter queue size
        - Stuck events
        """
        health_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy",
            "issues": [],
            "metrics": {}
        }

        # 1. Check pending queue size
        pending_count = await self._get_queue_count(EventStatus.PENDING)
        health_report["metrics"]["pending_events"] = pending_count

        if pending_count > 1000:
            await self.create_alert(
                severity="critical",
                title="Queue Backlog Critical",
                message=f"Pending queue has {pending_count} events (threshold: 1000)",
                alert_type="queue",
                metadata={"pending_count": pending_count}
            )
            health_report["status"] = "critical"
            health_report["issues"].append("High queue backlog")
        elif pending_count > 500:
            await self.create_alert(
                severity="warning",
                title="Queue Backlog Warning",
                message=f"Pending queue has {pending_count} events (threshold: 500)",
                alert_type="queue",
                metadata={"pending_count": pending_count}
            )
            health_report["status"] = "warning"
            health_report["issues"].append("Elevated queue backlog")

        # 2. Check dead letter queue
        dlq_count = await self._get_dlq_count()
        health_report["metrics"]["dead_letter_events"] = dlq_count

        if dlq_count > 100:
            await self.create_alert(
                severity="critical",
                title="High Dead Letter Queue",
                message=f"Dead letter queue has {dlq_count} events",
                alert_type="queue",
                metadata={"dlq_count": dlq_count}
            )
            health_report["status"] = "critical"
            health_report["issues"].append("High failure rate")
        elif dlq_count > 50:
            await self.create_alert(
                severity="warning",
                title="Elevated Dead Letter Queue",
                message=f"Dead letter queue has {dlq_count} events",
                alert_type="queue",
                metadata={"dlq_count": dlq_count}
            )
            if health_report["status"] == "healthy":
                health_report["status"] = "warning"
            health_report["issues"].append("Elevated failure rate")

        # 3. Check for stuck events (processing for > 1 hour)
        stuck_count = await self._get_stuck_events_count()
        health_report["metrics"]["stuck_events"] = stuck_count

        if stuck_count > 0:
            await self.create_alert(
                severity="warning",
                title="Stuck Events Detected",
                message=f"{stuck_count} events stuck in processing state",
                alert_type="performance",
                metadata={"stuck_count": stuck_count}
            )
            if health_report["status"] == "healthy":
                health_report["status"] = "warning"
            health_report["issues"].append("Events stuck in processing")

        # 4. Check retry queue
        retry_count = await self._get_queue_count(EventStatus.RETRY)
        health_report["metrics"]["retry_events"] = retry_count

        if retry_count > 200:
            await self.create_alert(
                severity="warning",
                title="High Retry Queue",
                message=f"Retry queue has {retry_count} events",
                alert_type="queue",
                metadata={"retry_count": retry_count}
            )
            if health_report["status"] == "healthy":
                health_report["status"] = "warning"
            health_report["issues"].append("High retry rate")

        return health_report

    async def check_failure_rate(self, hours: int = 1) -> Dict[str, Any]:
        """
        Calculate failure rate for recent period

        Args:
            hours: Time period to analyze
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        # Total completed/failed in period
        result = await self.db.execute(
            select(
                func.count().label("total"),
                func.sum(
                    func.case((TDSSyncQueue.status == EventStatus.DEAD_LETTER, 1), else_=0)
                ).label("failed")
            ).where(
                and_(
                    TDSSyncQueue.completed_at >= cutoff_time,
                    or_(
                        TDSSyncQueue.status == EventStatus.COMPLETED,
                        TDSSyncQueue.status == EventStatus.DEAD_LETTER
                    )
                )
            )
        )

        row = result.one()
        total = row.total or 0
        failed = row.failed or 0

        failure_rate = (failed / total * 100) if total > 0 else 0

        report = {
            "period_hours": hours,
            "total_processed": total,
            "failed": failed,
            "succeeded": total - failed,
            "failure_rate_percent": round(failure_rate, 2)
        }

        # Alert if failure rate is high
        if failure_rate > 10 and total > 10:
            await self.create_alert(
                severity="critical",
                title="High Failure Rate",
                message=f"Failure rate is {failure_rate:.1f}% over last {hours} hour(s)",
                alert_type="performance",
                metadata=report
            )
        elif failure_rate > 5 and total > 10:
            await self.create_alert(
                severity="warning",
                title="Elevated Failure Rate",
                message=f"Failure rate is {failure_rate:.1f}% over last {hours} hour(s)",
                alert_type="performance",
                metadata=report
            )

        return report

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    async def _get_queue_count(self, status: EventStatus) -> int:
        """Get count of events with specific status"""
        result = await self.db.execute(
            select(func.count()).select_from(TDSSyncQueue).where(
                TDSSyncQueue.status == status
            )
        )
        return result.scalar() or 0

    async def _get_dlq_count(self) -> int:
        """Get dead letter queue count"""
        result = await self.db.execute(
            select(func.count()).select_from(TDSDeadLetterQueue)
        )
        return result.scalar() or 0

    async def _get_stuck_events_count(self) -> int:
        """Get count of events stuck in processing"""
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)

        result = await self.db.execute(
            select(func.count()).select_from(TDSSyncQueue).where(
                and_(
                    TDSSyncQueue.status == EventStatus.PROCESSING,
                    TDSSyncQueue.started_at < one_hour_ago
                )
            )
        )
        return result.scalar() or 0

    async def _send_notification(self, alert: TDSAlert):
        """
        Send notification for critical alerts via email and Slack
        """
        logger.critical(
            f"CRITICAL ALERT: {alert.title}\n"
            f"Message: {alert.message}\n"
            f"Type: {alert.alert_type}\n"
            f"Time: {alert.created_at}"
        )

        try:
            # Import notification service
            from tds_core.services.notification_service import NotificationService

            # Initialize notification service
            notif_service = NotificationService()

            # Send to all configured channels
            results = await notif_service.send_alert(
                title=alert.title,
                message=alert.message,
                severity=alert.severity,
                metadata=alert.metadata,
                channels=['all']  # Send to email and Slack
            )

            # Log results
            for channel, success in results.items():
                if success:
                    logger.info(f"Alert notification sent via {channel}: {alert.title}")
                else:
                    logger.warning(f"Failed to send alert via {channel}: {alert.title}")

        except Exception as e:
            logger.error(f"Error sending alert notification: {e}", exc_info=True)
