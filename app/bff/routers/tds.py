"""
TDS BFF Router - Backend for Frontend endpoints for TDS
Provides mobile and web-optimized endpoints for data sync monitoring
"""
import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.db.database import get_async_db
from app.tds.core.service import TDSService
from app.models.zoho_sync import (
    TDSSyncRun,
    TDSSyncQueue,
    TDSDeadLetterQueue,
    TDSAlert,
    EventStatus,
    EntityType,
)
from sqlalchemy import select, func, and_, or_, desc
from app.bff.services.cache_service import cache_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tds", tags=["TDS BFF"])


# ============================================================================
# RESPONSE MODELS (Mobile/Web Optimized)
# ============================================================================

class SyncRunSummary(BaseModel):
    """Mobile-optimized sync run summary"""
    id: str
    type: str
    entity_type: Optional[str]
    status: str
    progress_percentage: float = Field(..., description="Progress as percentage (0-100)")
    processed: int
    total: int
    failed: int
    started_at: Optional[str]
    duration: Optional[str] = Field(None, description="Human-readable duration")


class QueueStats(BaseModel):
    """Current queue statistics"""
    pending: int
    processing: int
    completed_today: int
    failed_today: int
    retry_ready: int
    dead_letter: int


class SyncHealth(BaseModel):
    """Overall sync system health"""
    status: str = Field(..., description="healthy, degraded, or critical")
    queue_depth: int
    processing_rate: float = Field(..., description="Items per minute")
    error_rate: float = Field(..., description="Percentage of errors")
    active_workers: int
    active_alerts: int
    last_sync: Optional[str]


class AlertSummary(BaseModel):
    """Mobile-optimized alert summary"""
    id: str
    severity: str
    title: str
    message: str
    triggered_at: str
    is_active: bool
    acknowledged: bool


class EntitySyncStatus(BaseModel):
    """Status for a specific entity type"""
    entity_type: str
    last_sync: Optional[str]
    total_synced: int
    pending: int
    failed_last_24h: int
    success_rate: float = Field(..., description="Success rate as percentage")


# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@router.get(
    "/dashboard",
    response_model=dict,
    summary="Get TDS dashboard overview",
    description="Get a complete overview of the TDS system for dashboard display"
)
@cache_response(ttl_seconds=30)
async def get_dashboard(db: AsyncSession = Depends(get_async_db)):
    """
    Get comprehensive TDS dashboard data

    Returns:
        - System health
        - Queue statistics
        - Recent sync runs
        - Active alerts
        - Entity-specific stats
    """
    tds_service = TDSService(db)

    # Get overall stats
    stats = await tds_service.get_sync_stats()

    # Get queue stats
    queue_result = await db.execute(
        select(TDSSyncQueue.status, func.count(TDSSyncQueue.id))
        .group_by(TDSSyncQueue.status)
    )
    queue_counts = {str(row[0]): row[1] for row in queue_result.all()}

    # Calculate processing rate (last 5 minutes)
    five_min_ago = datetime.utcnow() - timedelta(minutes=5)
    result = await db.execute(
        select(func.count(TDSSyncQueue.id))
        .where(
            and_(
                TDSSyncQueue.status == EventStatus.COMPLETED,
                TDSSyncQueue.completed_at >= five_min_ago
            )
        )
    )
    recent_processed = result.scalar() or 0
    processing_rate = recent_processed / 5.0  # per minute

    # Calculate error rate
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(
        select(
            func.count(TDSSyncQueue.id).filter(TDSSyncQueue.status == EventStatus.COMPLETED).label("completed"),
            func.count(TDSSyncQueue.id).filter(TDSSyncQueue.status == EventStatus.FAILED).label("failed"),
        )
        .where(TDSSyncQueue.created_at >= today)
    )
    row = result.one()
    total_today = row.completed + row.failed
    error_rate = (row.failed / total_today * 100) if total_today > 0 else 0

    # Determine health status
    if error_rate > 20 or stats["active_alerts"] > 5:
        health_status = "critical"
    elif error_rate > 10 or stats["active_alerts"] > 2:
        health_status = "degraded"
    else:
        health_status = "healthy"

    # Get recent runs (formatted)
    recent_runs = []
    for run in stats["recent_runs"]:
        progress = 0
        if run["processed"] and run.get("total"):
            progress = (run["processed"] / max(run["processed"] + run["failed"], 1)) * 100

        duration = None
        if run["started_at"]:
            started = datetime.fromisoformat(run["started_at"])
            duration_sec = (datetime.utcnow() - started).total_seconds()
            if duration_sec < 60:
                duration = f"{int(duration_sec)}s"
            elif duration_sec < 3600:
                duration = f"{int(duration_sec / 60)}m"
            else:
                duration = f"{int(duration_sec / 3600)}h"

        recent_runs.append(
            SyncRunSummary(
                id=run["id"],
                type=run["type"],
                entity_type=run["entity_type"],
                status=run["status"],
                progress_percentage=progress,
                processed=run["processed"],
                total=run["processed"] + run["failed"],
                failed=run["failed"],
                started_at=run["started_at"],
                duration=duration,
            )
        )

    # Get active alerts
    result = await db.execute(
        select(TDSAlert)
        .where(and_(TDSAlert.is_active == True, TDSAlert.resolved == False))
        .order_by(desc(TDSAlert.triggered_at))
        .limit(10)
    )
    alerts = result.scalars().all()

    alert_summaries = [
        AlertSummary(
            id=str(alert.id),
            severity=str(alert.severity),
            title=alert.title,
            message=alert.message,
            triggered_at=alert.triggered_at.isoformat(),
            is_active=alert.is_active,
            acknowledged=alert.acknowledged,
        )
        for alert in alerts
    ]

    return {
        "health": SyncHealth(
            status=health_status,
            queue_depth=queue_counts.get("pending", 0),
            processing_rate=processing_rate,
            error_rate=round(error_rate, 2),
            active_workers=1,  # TODO: Get from worker registry
            active_alerts=stats["active_alerts"],
            last_sync=stats["recent_runs"][0]["started_at"] if stats["recent_runs"] else None,
        ),
        "queue": QueueStats(
            pending=queue_counts.get("pending", 0),
            processing=queue_counts.get("processing", 0),
            completed_today=row.completed,
            failed_today=row.failed,
            retry_ready=queue_counts.get("retry", 0),
            dead_letter=stats["dead_letter_queue"],
        ),
        "recent_runs": recent_runs,
        "alerts": alert_summaries,
    }


# ============================================================================
# SYNC RUNS
# ============================================================================

@router.get(
    "/runs",
    response_model=List[SyncRunSummary],
    summary="Get sync run history",
    description="Get paginated list of sync runs"
)
@cache_response(ttl_seconds=30)
async def get_sync_runs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    entity_type: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db)
):
    """Get list of sync runs with optional filters"""
    query = select(TDSSyncRun).order_by(desc(TDSSyncRun.started_at))

    # Apply filters
    if entity_type:
        query = query.where(TDSSyncRun.entity_type == EntityType(entity_type))
    if status:
        query = query.where(TDSSyncRun.status == EventStatus(status))

    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    runs = result.scalars().all()

    return [
        SyncRunSummary(
            id=str(run.id),
            type=str(run.run_type),
            entity_type=str(run.entity_type) if run.entity_type else None,
            status=str(run.status),
            progress_percentage=(run.processed_events / max(run.total_events, 1) * 100) if run.total_events else 0,
            processed=run.processed_events,
            total=run.total_events,
            failed=run.failed_events,
            started_at=run.started_at.isoformat() if run.started_at else None,
            duration=f"{run.duration_seconds}s" if run.duration_seconds else None,
        )
        for run in runs
    ]


@router.get(
    "/runs/{run_id}",
    response_model=dict,
    summary="Get sync run details",
    description="Get detailed information about a specific sync run"
)
@cache_response(ttl_seconds=30)
async def get_sync_run_details(
    run_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Get detailed sync run information"""
    result = await db.execute(
        select(TDSSyncRun).where(TDSSyncRun.id == run_id)
    )
    run = result.scalar_one_or_none()

    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sync run not found"
        )

    # Get associated queue entries
    result = await db.execute(
        select(TDSSyncQueue.status, func.count(TDSSyncQueue.id))
        .where(TDSSyncQueue.sync_run_id == run.id)
        .group_by(TDSSyncQueue.status)
    )
    queue_breakdown = {str(row[0]): row[1] for row in result.all()}

    return {
        "id": str(run.id),
        "type": str(run.run_type),
        "entity_type": str(run.entity_type) if run.entity_type else None,
        "status": str(run.status),
        "worker_id": run.worker_id,
        "statistics": {
            "total": run.total_events,
            "processed": run.processed_events,
            "failed": run.failed_events,
            "skipped": run.skipped_events,
            "success_rate": (run.processed_events / max(run.total_events, 1) * 100) if run.total_events else 0,
        },
        "timing": {
            "started_at": run.started_at.isoformat() if run.started_at else None,
            "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            "duration_seconds": run.duration_seconds,
        },
        "queue_breakdown": queue_breakdown,
        "configuration": run.configuration_snapshot,
        "error_summary": run.error_summary,
    }


# ============================================================================
# ENTITY STATUS
# ============================================================================

@router.get(
    "/entities",
    response_model=List[EntitySyncStatus],
    summary="Get entity sync status",
    description="Get sync status for all entity types"
)
@cache_response(ttl_seconds=60)
async def get_entity_status(db: AsyncSession = Depends(get_async_db)):
    """Get sync status grouped by entity type"""
    entity_statuses = []

    for entity_type in EntityType:
        # Get last sync time
        result = await db.execute(
            select(TDSSyncQueue.completed_at)
            .where(
                and_(
                    TDSSyncQueue.entity_type == entity_type,
                    TDSSyncQueue.status == EventStatus.COMPLETED
                )
            )
            .order_by(desc(TDSSyncQueue.completed_at))
            .limit(1)
        )
        last_sync = result.scalar_one_or_none()

        # Count totals
        result = await db.execute(
            select(func.count(TDSSyncQueue.id))
            .where(
                and_(
                    TDSSyncQueue.entity_type == entity_type,
                    TDSSyncQueue.status == EventStatus.COMPLETED
                )
            )
        )
        total_synced = result.scalar() or 0

        # Count pending
        result = await db.execute(
            select(func.count(TDSSyncQueue.id))
            .where(
                and_(
                    TDSSyncQueue.entity_type == entity_type,
                    TDSSyncQueue.status == EventStatus.PENDING
                )
            )
        )
        pending = result.scalar() or 0

        # Count failed last 24h
        yesterday = datetime.utcnow() - timedelta(days=1)
        result = await db.execute(
            select(func.count(TDSSyncQueue.id))
            .where(
                and_(
                    TDSSyncQueue.entity_type == entity_type,
                    TDSSyncQueue.status == EventStatus.FAILED,
                    TDSSyncQueue.created_at >= yesterday
                )
            )
        )
        failed_24h = result.scalar() or 0

        # Calculate success rate
        result = await db.execute(
            select(
                func.count(TDSSyncQueue.id).filter(TDSSyncQueue.status == EventStatus.COMPLETED).label("completed"),
                func.count(TDSSyncQueue.id).filter(TDSSyncQueue.status == EventStatus.FAILED).label("failed"),
            )
            .where(TDSSyncQueue.entity_type == entity_type)
        )
        row = result.one()
        total_attempts = row.completed + row.failed
        success_rate = (row.completed / total_attempts * 100) if total_attempts > 0 else 100.0

        entity_statuses.append(
            EntitySyncStatus(
                entity_type=str(entity_type),
                last_sync=last_sync.isoformat() if last_sync else None,
                total_synced=total_synced,
                pending=pending,
                failed_last_24h=failed_24h,
                success_rate=round(success_rate, 2),
            )
        )

    return entity_statuses


# ============================================================================
# ALERTS
# ============================================================================

@router.get(
    "/alerts",
    response_model=List[AlertSummary],
    summary="Get active alerts",
    description="Get list of active TDS alerts"
)
@cache_response(ttl_seconds=30)
async def get_alerts(
    include_resolved: bool = Query(False),
    severity: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_async_db)
):
    """Get active alerts"""
    query = select(TDSAlert).where(TDSAlert.is_active == True)

    if not include_resolved:
        query = query.where(TDSAlert.resolved == False)

    if severity:
        query = query.where(TDSAlert.severity == severity)

    query = query.order_by(desc(TDSAlert.triggered_at)).limit(limit)

    result = await db.execute(query)
    alerts = result.scalars().all()

    return [
        AlertSummary(
            id=str(alert.id),
            severity=str(alert.severity),
            title=alert.title,
            message=alert.message,
            triggered_at=alert.triggered_at.isoformat(),
            is_active=alert.is_active,
            acknowledged=alert.acknowledged,
        )
        for alert in alerts
    ]


@router.post(
    "/alerts/{alert_id}/acknowledge",
    summary="Acknowledge an alert",
    description="Mark an alert as acknowledged"
)
async def acknowledge_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Acknowledge an alert"""
    result = await db.execute(
        select(TDSAlert).where(TDSAlert.id == alert_id)
    )
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )

    alert.acknowledged = True
    alert.acknowledged_at = datetime.utcnow()
    await db.commit()

    return {"success": True, "message": "Alert acknowledged"}


# ============================================================================
# DEAD LETTER QUEUE
# ============================================================================

@router.get(
    "/dead-letter",
    summary="Get dead letter queue items",
    description="Get items that failed permanently and require manual intervention"
)
@cache_response(ttl_seconds=60)
async def get_dead_letter_queue(
    entity_type: Optional[str] = None,
    resolved: bool = Query(False),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_async_db)
):
    """Get dead letter queue items"""
    query = select(TDSDeadLetterQueue)

    if entity_type:
        query = query.where(TDSDeadLetterQueue.entity_type == EntityType(entity_type))

    query = query.where(TDSDeadLetterQueue.resolved == resolved)
    query = query.order_by(desc(TDSDeadLetterQueue.created_at))
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    items = result.scalars().all()

    return [
        {
            "id": str(item.id),
            "entity_type": str(item.entity_type),
            "source_entity_id": item.source_entity_id,
            "failure_reason": item.failure_reason,
            "error_code": item.error_code,
            "total_attempts": item.total_attempts,
            "created_at": item.created_at.isoformat(),
            "resolved": item.resolved,
            "assigned_to": item.assigned_to,
            "priority": item.priority,
        }
        for item in items
    ]


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get(
    "/health",
    summary="TDS health check",
    description="Quick health check for TDS system"
)
async def health_check(db: AsyncSession = Depends(get_async_db)):
    """Quick health check"""
    tds_service = TDSService(db)
    stats = await tds_service.get_sync_stats()

    return {
        "status": "healthy",
        "service": "TDS (TSH Data Sync)",
        "version": "2.0.0",
        "features": [
            "Event-driven architecture",
            "Modular monolith design",
            "BFF endpoints for mobile/web",
            "Real-time monitoring",
            "Automatic retry with backoff",
        ],
        "queue_depth": sum(stats["queue_status"].values()),
        "active_alerts": stats["active_alerts"],
        "dead_letter_count": stats["dead_letter_queue"],
    }
