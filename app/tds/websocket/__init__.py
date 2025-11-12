"""
TDS WebSocket Module

Provides real-time updates to the TDS Admin Dashboard via Socket.IO.
"""

from .server import sio, init_socketio, emit_event
from .events import (
    emit_sync_completed,
    emit_alert_created,
    emit_queue_updated,
    emit_health_changed,
    emit_webhook_received,
    emit_circuit_breaker_state_changed,
)

__all__ = [
    "sio",
    "init_socketio",
    "emit_event",
    "emit_sync_completed",
    "emit_alert_created",
    "emit_queue_updated",
    "emit_health_changed",
    "emit_webhook_received",
    "emit_circuit_breaker_state_changed",
]
