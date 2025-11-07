"""
TDS (TSH Data Sync) - Modular Data Synchronization System
Enhanced with Modular Monolith, BFF, and Event-Driven Architecture

The TDS system provides:
- Modular architecture with clear boundaries
- Event-driven synchronization
- BFF endpoints for mobile/web clients
- Real-time monitoring and metrics
- Distributed processing with workers
- UNIFIED ZOHO INTEGRATION (Single source of truth)

🎯 Quick Start - Zoho Integration:
    from app.tds.zoho import ZohoService

    service = ZohoService()
    await service.start()
    result = await service.sync_products()
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

# Import Zoho facade for easy access
from app.tds.zoho import ZohoService

__version__ = "3.0.0"  # Bumped for Zoho consolidation
__all__ = [
    # Core
    "TDSEvent",
    "TDSSyncStartedEvent",
    "TDSSyncCompletedEvent",
    "TDSSyncFailedEvent",
    "TDSEntitySyncedEvent",
    "TDSService",
    "TDSQueueService",

    # Zoho Integration (NEW - v3.0.0)
    "ZohoService",
]
