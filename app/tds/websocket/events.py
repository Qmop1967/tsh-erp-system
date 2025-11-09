"""
TDS WebSocket Event Emitters

Helper functions to emit specific events to the TDS Admin Dashboard.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

from .server import emit_event

logger = logging.getLogger(__name__)


async def emit_sync_completed(
    run_id: int,
    run_type: str,
    entity_type: Optional[str],
    status: str,
    total_events: int,
    processed_events: int,
    failed_events: int,
    duration_seconds: Optional[float] = None,
) -> None:
    """
    Emit sync_completed event when a sync run finishes.

    Args:
        run_id: Sync run ID
        run_type: Type of sync run
        entity_type: Entity type (if applicable)
        status: Run status (completed, failed, etc.)
        total_events: Total number of events
        processed_events: Successfully processed events
        failed_events: Failed events
        duration_seconds: Duration in seconds
    """
    data = {
        "run_id": run_id,
        "run_type": run_type,
        "entity_type": entity_type,
        "status": status,
        "total_events": total_events,
        "processed_events": processed_events,
        "failed_events": failed_events,
        "duration_seconds": duration_seconds,
        "timestamp": datetime.utcnow().isoformat(),
    }

    await emit_event("sync_completed", data)
    logger.info(f"Emitted sync_completed for run {run_id} ({status})")


async def emit_alert_created(
    alert_id: int,
    severity: str,
    title: str,
    message: str,
) -> None:
    """
    Emit alert_created event when a new alert is triggered.

    Args:
        alert_id: Alert ID
        severity: Alert severity (info, warning, error, critical)
        title: Alert title
        message: Alert message
    """
    data = {
        "alert_id": alert_id,
        "severity": severity,
        "title": title,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
    }

    await emit_event("alert_created", data)
    logger.info(f"Emitted alert_created: {title} ({severity})")


async def emit_queue_updated(
    total: int,
    pending: int,
    processing: int,
    completed_today: int,
    failed_today: int,
    dead_letter: int,
) -> None:
    """
    Emit queue_updated event when queue statistics change.

    Args:
        total: Total queue items
        pending: Pending items
        processing: Currently processing items
        completed_today: Completed today
        failed_today: Failed today
        dead_letter: Dead letter queue items
    """
    data = {
        "total": total,
        "pending": pending,
        "processing": processing,
        "completed_today": completed_today,
        "failed_today": failed_today,
        "dead_letter": dead_letter,
        "timestamp": datetime.utcnow().isoformat(),
    }

    await emit_event("queue_updated", data)
    logger.debug(f"Emitted queue_updated: {pending} pending, {processing} processing")


async def emit_health_changed(
    status: str,
    score: float,
    component_statuses: Dict[str, str],
) -> None:
    """
    Emit health_changed event when system health changes.

    Args:
        status: Overall health status (healthy, degraded, critical)
        score: Health score (0-100)
        component_statuses: Status of individual components
    """
    data = {
        "status": status,
        "score": score,
        "components": component_statuses,
        "timestamp": datetime.utcnow().isoformat(),
    }

    await emit_event("health_changed", data)
    logger.info(f"Emitted health_changed: {status} (score: {score})")


async def emit_webhook_received(
    webhook_id: int,
    source_type: str,
    entity_type: str,
    source_entity_id: str,
    signature_verified: bool,
) -> None:
    """
    Emit webhook_received event when a new webhook is received.

    Args:
        webhook_id: Webhook event ID
        source_type: Source system (e.g., zoho)
        entity_type: Entity type
        source_entity_id: Source entity ID
        signature_verified: Whether signature was verified
    """
    data = {
        "webhook_id": webhook_id,
        "source_type": source_type,
        "entity_type": entity_type,
        "source_entity_id": source_entity_id,
        "signature_verified": signature_verified,
        "timestamp": datetime.utcnow().isoformat(),
    }

    await emit_event("webhook_received", data)
    logger.debug(f"Emitted webhook_received: {entity_type} {source_entity_id}")


async def emit_circuit_breaker_state_changed(
    breaker_name: str,
    old_state: str,
    new_state: str,
    failure_count: int,
) -> None:
    """
    Emit circuit_breaker_state_changed event when a circuit breaker changes state.

    Args:
        breaker_name: Circuit breaker name
        old_state: Previous state
        new_state: New state
        failure_count: Current failure count
    """
    data = {
        "breaker_name": breaker_name,
        "old_state": old_state,
        "new_state": new_state,
        "failure_count": failure_count,
        "timestamp": datetime.utcnow().isoformat(),
    }

    await emit_event("circuit_breaker_state_changed", data)
    logger.warning(f"Emitted circuit_breaker_state_changed: {breaker_name} {old_state} -> {new_state}")


# Additional helper function for custom events
async def emit_custom_event(event_type: str, data: Dict[str, Any]) -> None:
    """
    Emit a custom event.

    Args:
        event_type: Custom event type
        data: Event data
    """
    data["timestamp"] = datetime.utcnow().isoformat()
    await emit_event(event_type, data)
    logger.info(f"Emitted custom event: {event_type}")
