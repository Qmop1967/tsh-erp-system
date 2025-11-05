"""
Zoho Dashboard Router
Dashboard and monitoring endpoints for Zoho integration
(Unified from TDS Core - now part of main ERP)
"""
import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db

# Import models from unified location
from app.models.zoho_sync import TDSSyncQueue, TDSDeadLetterQueue, EventStatus

# Import schemas from TDS Core (will be moved to app/schemas in Phase 3)
from app.schemas.response_schemas import QueueStatsResponse

# Import services from unified location
from app.services.zoho_queue import QueueService

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# QUEUE STATISTICS ENDPOINTS
# ============================================================================

@router.get("/queue-stats", response_model=QueueStatsResponse, tags=["Zoho Dashboard"])
async def get_queue_stats(db: AsyncSession = Depends(get_db)):
    """
    Get queue statistics

    Returns current queue status and processing metrics
    """
    queue_service = QueueService(db)
    stats = await queue_service.get_queue_stats()

    # Parse oldest_pending
    oldest_pending = None
    if stats.get("oldest_pending"):
        try:
            oldest_pending = datetime.fromisoformat(stats["oldest_pending"])
        except:
            pass

    return QueueStatsResponse(
        total_events=stats["total_events"],
        by_status=stats["by_status"],
        by_entity=stats["by_entity_type"],
        by_priority=stats["by_priority"],
        oldest_pending=oldest_pending,
        processing_rate=None  # TODO: Calculate from metrics
    )


# ============================================================================
# SYSTEM METRICS ENDPOINTS
# ============================================================================

@router.get(
    "/metrics",
    tags=["Zoho Dashboard"],
    summary="Get system metrics"
)
async def get_dashboard_metrics(
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive system metrics for dashboard

    Returns:
        - Queue statistics
        - Processing performance
        - Database metrics
        - Recent alerts
    """
    from app.services.zoho_monitoring import MonitoringService
    from app.services.zoho_alert import AlertService

    try:
        monitoring = MonitoringService()
        metrics = await monitoring.get_system_metrics(db)

        # Get recent alerts
        alert_service = AlertService(db)
        active_alerts = await alert_service.get_active_alerts(acknowledged=False)

        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics,
            "active_alerts": [
                {
                    "id": str(alert.id),
                    "severity": alert.severity,
                    "title": alert.title,
                    "message": alert.message,
                    "created_at": alert.created_at.isoformat()
                }
                for alert in active_alerts[:10]
            ]
        }
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/recent-events",
    tags=["Zoho Dashboard"],
    summary="Get recent sync events"
)
async def get_recent_events(
    limit: int = 50,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get recent sync queue events"""
    try:
        query = select(TDSSyncQueue).order_by(TDSSyncQueue.queued_at.desc()).limit(limit)

        if status_filter:
            try:
                status_enum = EventStatus(status_filter.upper())
                query = query.where(TDSSyncQueue.status == status_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status_filter}")

        result = await db.execute(query)
        events = result.scalars().all()

        return {
            "success": True,
            "count": len(events),
            "events": [
                {
                    "id": str(event.id),
                    "entity_type": event.entity_type,
                    "source_entity_id": event.source_entity_id,
                    "operation": event.operation_type,
                    "status": event.status,
                    "attempt_count": event.attempt_count,
                    "queued_at": event.queued_at.isoformat() if event.queued_at else None,
                    "completed_at": event.completed_at.isoformat() if event.completed_at else None,
                    "last_error": event.last_error
                }
                for event in events
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recent events: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/dead-letter",
    tags=["Zoho Dashboard"],
    summary="Get dead letter queue"
)
async def get_dead_letter_queue(
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get events in dead letter queue"""
    try:
        result = await db.execute(
            select(TDSDeadLetterQueue)
            .order_by(TDSDeadLetterQueue.moved_at.desc())
            .limit(limit)
        )
        dlq_events = result.scalars().all()

        return {
            "success": True,
            "count": len(dlq_events),
            "events": [
                {
                    "id": str(event.id),
                    "entity_type": event.entity_type,
                    "source_entity_id": event.source_entity_id,
                    "failure_reason": event.failure_reason,
                    "error_code": event.error_code,
                    "attempt_count": event.attempt_count,
                    "moved_at": event.moved_at.isoformat() if event.moved_at else None,
                    "payload": event.payload
                }
                for event in dlq_events
            ]
        }
    except Exception as e:
        logger.error(f"Error getting dead letter queue: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ALERT MANAGEMENT ENDPOINTS
# ============================================================================

@router.post(
    "/alerts/{alert_id}/acknowledge",
    tags=["Zoho Dashboard"],
    summary="Acknowledge an alert"
)
async def acknowledge_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Mark an alert as acknowledged"""
    from app.services.zoho_alert import AlertService

    try:
        alert_service = AlertService(db)
        success = await alert_service.acknowledge_alert(UUID(alert_id))

        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")

        return {
            "success": True,
            "message": "Alert acknowledged"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/dead-letter/{event_id}/retry",
    tags=["Zoho Dashboard"],
    summary="Retry a dead letter event"
)
async def retry_dead_letter_event(
    event_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Move an event from dead letter queue back to processing queue

    This allows manual retry of permanently failed events
    """
    try:
        # Get dead letter event
        result = await db.execute(
            select(TDSDeadLetterQueue).where(TDSDeadLetterQueue.id == UUID(event_id))
        )
        dlq_event = result.scalar_one_or_none()

        if not dlq_event:
            raise HTTPException(status_code=404, detail="Dead letter event not found")

        # Create new queue entry
        new_queue_entry = TDSSyncQueue(
            entity_type=dlq_event.entity_type,
            source_entity_id=dlq_event.source_entity_id,
            operation_type=dlq_event.operation_type,
            normalized_payload=dlq_event.payload,
            status=EventStatus.PENDING,
            priority=2,  # High priority for manual retries
            attempt_count=0,
            max_attempts=3
        )

        db.add(new_queue_entry)

        # Remove from dead letter queue
        await db.delete(dlq_event)

        await db.commit()

        return {
            "success": True,
            "message": "Event moved back to processing queue",
            "new_queue_id": str(new_queue_entry.id)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrying dead letter event: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# WEBHOOK HEALTH MONITORING ENDPOINTS
# ============================================================================

@router.get("/webhook-health", tags=["Zoho Dashboard", "Monitoring"])
async def get_webhook_health(
    hours: int = 24,
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive webhook health metrics

    Returns:
        - Health score (0-100)
        - Webhook statistics
        - Detected issues
        - Recommendations

    Use this endpoint to proactively monitor webhook health
    """
    from app.services.zoho_webhook_health import WebhookHealthService

    health_service = WebhookHealthService(db)
    metrics = await health_service.get_health_metrics(hours=hours)

    return {
        "success": True,
        "metrics": metrics
    }


@router.get("/webhook-duplicates", tags=["Zoho Dashboard", "Monitoring"])
async def get_duplicate_webhook_analysis(
    hours: int = 24,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze duplicate webhook attempts

    Helps identify if Zoho or other sources are retrying webhooks excessively

    Returns:
        - List of events with multiple delivery attempts
        - Retry counts and time spans
        - Patterns in duplicate deliveries
    """
    from app.services.zoho_webhook_health import WebhookHealthService

    health_service = WebhookHealthService(db)
    stats = await health_service.get_duplicate_webhook_stats(hours=hours)

    return {
        "success": True,
        "analysis": stats
    }
