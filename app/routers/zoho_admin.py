"""
Zoho Admin Router
Administrative endpoints for Zoho integration management
(Unified from TDS Core - now part of main ERP)
"""
import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.config import settings

# Import schemas from TDS Core (will be moved to app/schemas in Phase 3)
from tds_core.schemas.webhook_schemas import ManualSyncRequest

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# CONFIGURATION ENDPOINTS
# ============================================================================

@router.get("/config", tags=["Zoho Admin"])
async def get_configuration(db: AsyncSession = Depends(get_db)):
    """
    Get current system configuration

    Returns non-sensitive configuration values
    """
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "debug": settings.debug,
        "api_workers": settings.api_workers,
        "database": {
            "host": settings.database_host,
            "name": settings.database_name,
            "pool_size": settings.database_pool_size
        },
        "tds_config": {
            "max_retry_attempts": settings.tds_max_retry_attempts,
            "batch_size": settings.tds_batch_size,
            "alert_failure_threshold": settings.tds_alert_failure_rate_threshold
        }
    }


# ============================================================================
# MANUAL SYNC ENDPOINT
# ============================================================================

@router.post("/sync/manual", tags=["Zoho Admin"])
async def trigger_manual_sync(
    request: ManualSyncRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger manual synchronization

    Allows administrators to manually trigger sync for specific entities
    """
    logger.info(f"Manual sync requested: {request.entity_type}")

    # TODO: Implement manual sync logic

    return {
        "success": True,
        "message": f"Manual sync triggered for {request.entity_type}",
        "entity_type": request.entity_type,
        "entity_count": len(request.entity_ids) if request.entity_ids else "all",
        "priority": request.priority
    }
