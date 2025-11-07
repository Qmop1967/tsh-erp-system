"""
TDS Core Service - Main Synchronization Service
Integrates with event bus for publish/subscribe pattern
"""
import logging
from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.events.event_bus import event_bus
from app.tds.core.events import (
    TDSSyncStartedEvent,
    TDSSyncCompletedEvent,
    TDSSyncFailedEvent,
    TDSEntitySyncedEvent,
    TDSEntitySyncFailedEvent,
)
from app.models.zoho_sync import (
    TDSInboxEvent,
    TDSSyncQueue,
    TDSSyncRun,
    TDSSyncLog,
    TDSDeadLetterQueue,
    TDSSyncCursor,
    TDSAuditTrail,
    TDSAlert,
    TDSMetric,
    EventStatus,
    SourceType,
    EntityType,
    OperationType,
    AlertSeverity,
)
from sqlalchemy import select, update, delete, func, and_, or_
import time

logger = logging.getLogger(__name__)


class TDSService:
    """
    TDS Core Service - Orchestrates data synchronization

    This service:
    - Creates sync runs
    - Publishes events to event bus
    - Manages sync lifecycle
    - Records metrics and alerts
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.event_bus = event_bus

    async def create_sync_run(
        self,
        run_type: SourceType,
        entity_type: Optional[EntityType] = None,
        configuration: Optional[Dict[str, Any]] = None,
    ) -> TDSSyncRun:
        """
        Create a new sync run

        Args:
            run_type: Type of sync (zoho, manual, scheduled, etc.)
            entity_type: Optional entity type filter
            configuration: Optional configuration snapshot

        Returns:
            Created sync run
        """
        sync_run = TDSSyncRun(
            id=uuid4(),
            run_type=run_type,
            entity_type=entity_type,
            status=EventStatus.PENDING,
            worker_id=None,
            total_events=0,
            processed_events=0,
            failed_events=0,
            skipped_events=0,
            configuration_snapshot=configuration,
        )

        self.db.add(sync_run)
        await self.db.commit()
        await self.db.refresh(sync_run)

        # Publish event
        event = TDSSyncStartedEvent(
            sync_run_id=sync_run.id,
            entity_type=str(entity_type) if entity_type else "all",
            source_type=str(run_type),
        )
        await self.event_bus.publish(event)

        logger.info(f"Created sync run: {sync_run.id} ({run_type} - {entity_type})")

        return sync_run

    async def complete_sync_run(
        self,
        sync_run_id: UUID,
        total_processed: int,
        successful: int,
        failed: int,
        skipped: int = 0,
    ):
        """
        Mark sync run as completed

        Args:
            sync_run_id: ID of the sync run
            total_processed: Total events processed
            successful: Number of successful events
            failed: Number of failed events
            skipped: Number of skipped events
        """
        # Calculate duration
        result = await self.db.execute(
            select(TDSSyncRun).where(TDSSyncRun.id == sync_run_id)
        )
        sync_run = result.scalar_one_or_none()

        if not sync_run:
            logger.error(f"Sync run not found: {sync_run_id}")
            return

        duration = None
        if sync_run.started_at:
            duration = int((datetime.utcnow() - sync_run.started_at).total_seconds())

        # Update sync run
        await self.db.execute(
            update(TDSSyncRun)
            .where(TDSSyncRun.id == sync_run_id)
            .values(
                status=EventStatus.COMPLETED,
                completed_at=datetime.utcnow(),
                total_events=total_processed,
                processed_events=successful,
                failed_events=failed,
                skipped_events=skipped,
                duration_seconds=duration,
            )
        )
        await self.db.commit()

        # Publish event
        event = TDSSyncCompletedEvent(
            sync_run_id=sync_run_id,
            entity_type=str(sync_run.entity_type) if sync_run.entity_type else "all",
            total_processed=total_processed,
            successful=successful,
            failed=failed,
            duration_seconds=duration or 0,
        )
        await self.event_bus.publish(event)

        logger.info(
            f"Completed sync run: {sync_run_id} "
            f"({successful}/{total_processed} successful, {failed} failed)"
        )

    async def fail_sync_run(
        self,
        sync_run_id: UUID,
        error_message: str,
        error_code: Optional[str] = None,
    ):
        """
        Mark sync run as failed

        Args:
            sync_run_id: ID of the sync run
            error_message: Error description
            error_code: Optional error code
        """
        # Get sync run
        result = await self.db.execute(
            select(TDSSyncRun).where(TDSSyncRun.id == sync_run_id)
        )
        sync_run = result.scalar_one_or_none()

        if not sync_run:
            logger.error(f"Sync run not found: {sync_run_id}")
            return

        # Calculate duration
        duration = None
        if sync_run.started_at:
            duration = int((datetime.utcnow() - sync_run.started_at).total_seconds())

        # Update sync run
        await self.db.execute(
            update(TDSSyncRun)
            .where(TDSSyncRun.id == sync_run_id)
            .values(
                status=EventStatus.FAILED,
                completed_at=datetime.utcnow(),
                duration_seconds=duration,
                error_summary={"error": error_message, "code": error_code},
            )
        )
        await self.db.commit()

        # Publish event
        event = TDSSyncFailedEvent(
            sync_run_id=sync_run_id,
            entity_type=str(sync_run.entity_type) if sync_run.entity_type else "all",
            error_message=error_message,
            error_code=error_code,
        )
        await self.event_bus.publish(event)

        logger.error(f"Failed sync run: {sync_run_id} - {error_message}")

    async def record_entity_sync(
        self,
        entity_type: EntityType,
        entity_id: str,
        source_entity_id: str,
        operation: OperationType,
        changes: Optional[Dict[str, Any]] = None,
    ):
        """
        Record successful entity synchronization

        Args:
            entity_type: Type of entity
            entity_id: Local entity ID
            source_entity_id: Source system entity ID
            operation: Operation performed
            changes: Changed fields
        """
        # Publish event
        event = TDSEntitySyncedEvent(
            entity_type=str(entity_type),
            entity_id=entity_id,
            source_entity_id=source_entity_id,
            operation=str(operation),
            changes=changes,
        )
        await self.event_bus.publish(event)

        logger.debug(
            f"Entity synced: {entity_type} {source_entity_id} -> {entity_id} ({operation})"
        )

    async def record_entity_sync_failure(
        self,
        entity_type: EntityType,
        source_entity_id: str,
        error_message: str,
        attempt_count: int,
    ):
        """
        Record entity sync failure

        Args:
            entity_type: Type of entity
            source_entity_id: Source system entity ID
            error_message: Error description
            attempt_count: Number of attempts made
        """
        # Publish event
        event = TDSEntitySyncFailedEvent(
            entity_type=str(entity_type),
            source_entity_id=source_entity_id,
            error_message=error_message,
            attempt_count=attempt_count,
        )
        await self.event_bus.publish(event)

        logger.warning(
            f"Entity sync failed: {entity_type} {source_entity_id} - {error_message}"
        )

    async def record_metric(
        self,
        metric_name: str,
        value: Any,
        entity_type: Optional[EntityType] = None,
        source_type: Optional[SourceType] = None,
        tags: Optional[Dict[str, Any]] = None,
    ):
        """
        Record a performance metric

        Args:
            metric_name: Name of the metric
            value: Metric value
            entity_type: Optional entity type
            source_type: Optional source type
            tags: Optional tags
        """
        metric = TDSMetric(
            id=uuid4(),
            metric_name=metric_name,
            metric_type="gauge",
            entity_type=entity_type,
            source_type=source_type,
            value={"value": value},
            tags=tags,
        )

        self.db.add(metric)
        await self.db.commit()

        logger.debug(f"Recorded metric: {metric_name} = {value}")

    async def create_alert(
        self,
        alert_type: str,
        severity: AlertSeverity,
        title: str,
        message: str,
        entity_type: Optional[EntityType] = None,
        affected_count: Optional[int] = None,
    ) -> TDSAlert:
        """
        Create a system alert

        Args:
            alert_type: Type of alert
            severity: Alert severity
            title: Alert title
            message: Alert message
            entity_type: Optional entity type
            affected_count: Number of affected items

        Returns:
            Created alert
        """
        alert = TDSAlert(
            id=uuid4(),
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            entity_type=entity_type,
            affected_count=affected_count,
            is_active=True,
            acknowledged=False,
            resolved=False,
        )

        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)

        logger.warning(f"Alert created: [{severity}] {title}")

        return alert

    async def get_sync_stats(self) -> Dict[str, Any]:
        """
        Get overall sync statistics

        Returns:
            Dictionary with sync statistics
        """
        # Count by status
        result = await self.db.execute(
            select(
                TDSSyncQueue.status, func.count(TDSSyncQueue.id)
            ).group_by(TDSSyncQueue.status)
        )
        status_counts = {row[0]: row[1] for row in result.all()}

        # Count dead letter queue
        result = await self.db.execute(
            select(func.count(TDSDeadLetterQueue.id)).where(
                TDSDeadLetterQueue.resolved == False
            )
        )
        dlq_count = result.scalar() or 0

        # Count active alerts
        result = await self.db.execute(
            select(func.count(TDSAlert.id)).where(
                and_(TDSAlert.is_active == True, TDSAlert.resolved == False)
            )
        )
        alert_count = result.scalar() or 0

        # Recent sync runs
        result = await self.db.execute(
            select(TDSSyncRun)
            .order_by(TDSSyncRun.started_at.desc())
            .limit(5)
        )
        recent_runs = result.scalars().all()

        return {
            "queue_status": status_counts,
            "dead_letter_queue": dlq_count,
            "active_alerts": alert_count,
            "recent_runs": [
                {
                    "id": str(run.id),
                    "type": str(run.run_type),
                    "entity_type": str(run.entity_type) if run.entity_type else None,
                    "status": str(run.status),
                    "processed": run.processed_events,
                    "failed": run.failed_events,
                    "started_at": run.started_at.isoformat() if run.started_at else None,
                }
                for run in recent_runs
            ],
        }
