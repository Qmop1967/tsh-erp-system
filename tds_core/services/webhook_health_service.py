"""
TDS Core - Webhook Health Monitoring Service
Monitors webhook health, tracks failures, and provides diagnostics
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models.tds_models import TDSInboxEvent, TDSSyncQueue, TDSDeadLetterQueue, EventStatus

logger = logging.getLogger(__name__)


class WebhookHealthService:
    """Service for monitoring webhook health and detecting issues"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_health_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get comprehensive webhook health metrics

        Args:
            hours: Number of hours to analyze (default: 24)

        Returns:
            Dictionary with health metrics and alerts
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        # Get inbox event statistics
        inbox_stats = await self._get_inbox_stats(cutoff_time)

        # Get processing statistics
        processing_stats = await self._get_processing_stats(cutoff_time)

        # Get failure analysis
        failure_analysis = await self._get_failure_analysis(cutoff_time)

        # Detect issues
        issues = await self._detect_issues(inbox_stats, processing_stats, failure_analysis)

        # Calculate health score (0-100)
        health_score = self._calculate_health_score(inbox_stats, processing_stats, failure_analysis)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "period_hours": hours,
            "health_score": health_score,
            "status": self._get_health_status(health_score),
            "inbox_stats": inbox_stats,
            "processing_stats": processing_stats,
            "failure_analysis": failure_analysis,
            "issues": issues,
            "recommendations": self._get_recommendations(issues)
        }

    async def _get_inbox_stats(self, since: datetime) -> Dict[str, Any]:
        """Get inbox event statistics"""
        # Total events
        total_result = await self.db.execute(
            select(func.count(TDSInboxEvent.id))
            .where(TDSInboxEvent.received_at >= since)
        )
        total = total_result.scalar() or 0

        # Duplicate events (rejected)
        duplicate_result = await self.db.execute(
            select(func.count(TDSInboxEvent.id))
            .where(
                and_(
                    TDSInboxEvent.received_at >= since,
                    TDSInboxEvent.is_valid == False,
                    TDSInboxEvent.validation_errors.isnot(None)
                )
            )
        )
        duplicates = duplicate_result.scalar() or 0

        # Valid events
        valid_result = await self.db.execute(
            select(func.count(TDSInboxEvent.id))
            .where(
                and_(
                    TDSInboxEvent.received_at >= since,
                    TDSInboxEvent.is_valid == True
                )
            )
        )
        valid = valid_result.scalar() or 0

        # By entity type
        entity_result = await self.db.execute(
            select(
                TDSInboxEvent.entity_type,
                func.count(TDSInboxEvent.id)
            )
            .where(TDSInboxEvent.received_at >= since)
            .group_by(TDSInboxEvent.entity_type)
        )
        by_entity = {str(row[0]): row[1] for row in entity_result.all()}

        return {
            "total_received": total,
            "duplicates_rejected": duplicates,
            "valid_events": valid,
            "duplicate_rate": (duplicates / total * 100) if total > 0 else 0,
            "by_entity_type": by_entity
        }

    async def _get_processing_stats(self, since: datetime) -> Dict[str, Any]:
        """Get processing queue statistics"""
        # Total queued
        total_result = await self.db.execute(
            select(func.count(TDSSyncQueue.id))
            .where(TDSSyncQueue.created_at >= since)
        )
        total = total_result.scalar() or 0

        # By status
        status_result = await self.db.execute(
            select(
                TDSSyncQueue.status,
                func.count(TDSSyncQueue.id)
            )
            .where(TDSSyncQueue.created_at >= since)
            .group_by(TDSSyncQueue.status)
        )
        by_status = {str(row[0]): row[1] for row in status_result.all()}

        # Success rate
        completed = by_status.get('COMPLETED', 0)
        success_rate = (completed / total * 100) if total > 0 else 0

        # Average processing time for completed events
        avg_time_result = await self.db.execute(
            select(
                func.avg(
                    func.extract('epoch', TDSSyncQueue.completed_at - TDSSyncQueue.created_at)
                )
            )
            .where(
                and_(
                    TDSSyncQueue.created_at >= since,
                    TDSSyncQueue.status == EventStatus.COMPLETED,
                    TDSSyncQueue.completed_at.isnot(None)
                )
            )
        )
        avg_processing_time = avg_time_result.scalar() or 0

        return {
            "total_queued": total,
            "by_status": by_status,
            "success_rate": success_rate,
            "avg_processing_time_seconds": round(avg_processing_time, 2)
        }

    async def _get_failure_analysis(self, since: datetime) -> Dict[str, Any]:
        """Analyze failures and errors"""
        # Failed queue events
        failed_result = await self.db.execute(
            select(func.count(TDSSyncQueue.id))
            .where(
                and_(
                    TDSSyncQueue.created_at >= since,
                    TDSSyncQueue.status == EventStatus.FAILED
                )
            )
        )
        failed = failed_result.scalar() or 0

        # Dead letter queue
        dlq_result = await self.db.execute(
            select(func.count(TDSDeadLetterQueue.id))
            .where(TDSDeadLetterQueue.moved_at >= since)
        )
        dead_letter = dlq_result.scalar() or 0

        # Common error types
        error_result = await self.db.execute(
            select(
                TDSSyncQueue.last_error,
                func.count(TDSSyncQueue.id)
            )
            .where(
                and_(
                    TDSSyncQueue.created_at >= since,
                    TDSSyncQueue.status.in_([EventStatus.FAILED, EventStatus.DEAD_LETTER]),
                    TDSSyncQueue.last_error.isnot(None)
                )
            )
            .group_by(TDSSyncQueue.last_error)
            .order_by(func.count(TDSSyncQueue.id).desc())
            .limit(10)
        )
        common_errors = [
            {"error": row[0][:200], "count": row[1]}
            for row in error_result.all()
        ]

        return {
            "failed_events": failed,
            "dead_letter_events": dead_letter,
            "common_errors": common_errors
        }

    async def _detect_issues(
        self,
        inbox_stats: Dict[str, Any],
        processing_stats: Dict[str, Any],
        failure_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Detect potential issues based on metrics"""
        issues = []

        # High duplicate rate (>10%)
        if inbox_stats["duplicate_rate"] > 10:
            issues.append({
                "severity": "warning",
                "type": "high_duplicate_rate",
                "message": f"High duplicate webhook rate: {inbox_stats['duplicate_rate']:.1f}%",
                "details": "Zoho may be retrying webhooks excessively",
                "action": "Check Zoho webhook configuration and logs"
            })

        # Low success rate (<90%)
        if processing_stats["success_rate"] < 90 and processing_stats["total_queued"] > 10:
            issues.append({
                "severity": "critical",
                "type": "low_success_rate",
                "message": f"Low processing success rate: {processing_stats['success_rate']:.1f}%",
                "details": "Many events are failing to process",
                "action": "Review error logs and dead letter queue"
            })

        # Many dead letter events
        if failure_analysis["dead_letter_events"] > 5:
            issues.append({
                "severity": "error",
                "type": "dead_letter_accumulation",
                "message": f"{failure_analysis['dead_letter_events']} events in dead letter queue",
                "details": "Events have permanently failed after max retries",
                "action": "Review and manually retry failed events"
            })

        # Slow processing (>30 seconds average)
        if processing_stats["avg_processing_time_seconds"] > 30:
            issues.append({
                "severity": "warning",
                "type": "slow_processing",
                "message": f"Slow average processing time: {processing_stats['avg_processing_time_seconds']}s",
                "details": "Events are taking longer than expected to process",
                "action": "Check database performance and API response times"
            })

        return issues

    def _calculate_health_score(
        self,
        inbox_stats: Dict[str, Any],
        processing_stats: Dict[str, Any],
        failure_analysis: Dict[str, Any]
    ) -> int:
        """Calculate overall health score (0-100)"""
        score = 100

        # Deduct for duplicates
        duplicate_penalty = min(inbox_stats["duplicate_rate"] * 2, 20)
        score -= duplicate_penalty

        # Deduct for low success rate
        if processing_stats["total_queued"] > 0:
            success_penalty = (100 - processing_stats["success_rate"]) * 0.5
            score -= success_penalty

        # Deduct for dead letter events
        dlq_penalty = min(failure_analysis["dead_letter_events"] * 2, 20)
        score -= dlq_penalty

        # Deduct for slow processing
        if processing_stats["avg_processing_time_seconds"] > 10:
            slow_penalty = min(processing_stats["avg_processing_time_seconds"] - 10, 20)
            score -= slow_penalty

        return max(0, int(score))

    def _get_health_status(self, score: int) -> str:
        """Get health status based on score"""
        if score >= 90:
            return "healthy"
        elif score >= 70:
            return "degraded"
        elif score >= 50:
            return "unhealthy"
        else:
            return "critical"

    def _get_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Get actionable recommendations based on issues"""
        recommendations = []

        for issue in issues:
            if issue["type"] == "high_duplicate_rate":
                recommendations.append(
                    "Review Zoho webhook retry settings and ensure endpoints return proper HTTP status codes"
                )
            elif issue["type"] == "low_success_rate":
                recommendations.append(
                    "Investigate common error patterns and fix underlying issues"
                )
            elif issue["type"] == "dead_letter_accumulation":
                recommendations.append(
                    "Review dead letter queue and manually retry or fix data issues"
                )
            elif issue["type"] == "slow_processing":
                recommendations.append(
                    "Optimize database queries and consider increasing worker processes"
                )

        if not recommendations:
            recommendations.append("All systems operating normally. Continue monitoring.")

        return recommendations

    async def get_duplicate_webhook_stats(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get detailed statistics about duplicate webhooks

        This helps identify if Zoho is retrying excessively
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        # Get events grouped by idempotency key
        result = await self.db.execute(
            select(
                TDSInboxEvent.idempotency_key,
                TDSInboxEvent.entity_type,
                TDSInboxEvent.source_entity_id,
                func.count(TDSInboxEvent.id).label('attempt_count'),
                func.min(TDSInboxEvent.received_at).label('first_attempt'),
                func.max(TDSInboxEvent.received_at).label('last_attempt')
            )
            .where(TDSInboxEvent.received_at >= cutoff_time)
            .group_by(
                TDSInboxEvent.idempotency_key,
                TDSInboxEvent.entity_type,
                TDSInboxEvent.source_entity_id
            )
            .having(func.count(TDSInboxEvent.id) > 1)
            .order_by(func.count(TDSInboxEvent.id).desc())
            .limit(20)
        )

        duplicate_events = []
        for row in result.all():
            time_span = (row.last_attempt - row.first_attempt).total_seconds()
            duplicate_events.append({
                "idempotency_key": row.idempotency_key,
                "entity_type": str(row.entity_type),
                "entity_id": row.source_entity_id,
                "retry_count": row.attempt_count,
                "first_attempt": row.first_attempt.isoformat(),
                "last_attempt": row.last_attempt.isoformat(),
                "time_span_seconds": round(time_span, 2)
            })

        return {
            "period_hours": hours,
            "duplicate_event_groups": len(duplicate_events),
            "events": duplicate_events
        }
