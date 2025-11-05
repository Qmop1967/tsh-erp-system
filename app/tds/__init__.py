"""
TDS (TSH Data Sync) - Modular Data Synchronization System
Enhanced with Modular Monolith, BFF, and Event-Driven Architecture

The TDS system provides:
- Modular architecture with clear boundaries
- Event-driven synchronization
- BFF endpoints for mobile/web clients
- Real-time monitoring and metrics
- Distributed processing with workers
"""

from app.tds.core.events import (
    TDSEvent,
    TDSSyncStartedEvent,
    TDSSyncCompletedEvent,
    TDSSyncFailedEvent,
    TDSEntitySyncedEvent
)
from app.tds.core.service import TDSService
from app.tds.core.queue import TDSQueueService

__version__ = "2.0.0"
__all__ = [
    "TDSEvent",
    "TDSSyncStartedEvent",
    "TDSSyncCompletedEvent",
    "TDSSyncFailedEvent",
    "TDSEntitySyncedEvent",
    "TDSService",
    "TDSQueueService",
]
