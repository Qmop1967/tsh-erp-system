"""
User and Customer-Salesperson Sync API Endpoints
=================================================

API endpoints for triggering user and customer ownership sync operations.

Endpoints:
- POST /api/tds/sync/users - Sync users from Zoho Books
- POST /api/tds/sync/customer-assignments - Update customer salesperson assignments
- POST /api/tds/sync/full-pipeline - Run complete sync pipeline
- GET /api/tds/sync/user-mapping - Get Zoho→TSH user ID mapping

Author: TSH ERP Team
Date: November 16, 2025
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.db.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.user import User
from app.tds.integrations.zoho.client import UnifiedZohoClient
from app.tds.integrations.zoho.auth import ZohoAuthManager
from app.tds.integrations.zoho.user_customer_sync import UserCustomerSyncService
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/tds/sync",
    tags=["TDS User Sync"]
)


def get_zoho_client() -> UnifiedZohoClient:
    """Get configured Zoho client"""
    auth_manager = ZohoAuthManager(
        client_id=settings.ZOHO_CLIENT_ID,
        client_secret=settings.ZOHO_CLIENT_SECRET,
        refresh_token=settings.ZOHO_REFRESH_TOKEN,
    )

    return UnifiedZohoClient(
        auth_manager=auth_manager,
        organization_id=settings.ZOHO_ORGANIZATION_ID
    )


@router.post("/users")
async def sync_users_from_zoho(
    background_tasks: BackgroundTasks,
    full_sync: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"]))
) -> Dict[str, Any]:
    """
    Sync users from Zoho Books

    **Requires:** Admin or Manager role

    **Parameters:**
    - full_sync: If true, sync all users. If false, only sync updated users.

    **Returns:**
    - Sync results with counts of created/updated/skipped users
    """
    try:
        logger.info(f"User {current_user.email} triggered user sync (full_sync={full_sync})")

        zoho_client = get_zoho_client()
        sync_service = UserCustomerSyncService(db, zoho_client)

        # Run sync
        result = await sync_service.sync_users_from_zoho(full_sync=full_sync)

        return {
            "success": True,
            "message": "User sync completed",
            "result": result,
            "triggered_by": current_user.email
        }

    except Exception as e:
        logger.error(f"Error during user sync: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"User sync failed: {str(e)}"
        )


@router.post("/customer-assignments")
async def update_customer_salesperson_assignments(
    background_tasks: BackgroundTasks,
    resync_all: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"]))
) -> Dict[str, Any]:
    """
    Update customer salesperson assignments based on Zoho owner_id

    **Requires:** Admin or Manager role

    **Parameters:**
    - resync_all: If true, update all customers. If false, only update customers without salesperson.

    **Returns:**
    - Update results with counts of updated customers
    """
    try:
        logger.info(f"User {current_user.email} triggered customer assignment update (resync_all={resync_all})")

        zoho_client = get_zoho_client()
        sync_service = UserCustomerSyncService(db, zoho_client)

        # Run update
        result = await sync_service.update_customer_salesperson_assignments(resync_all=resync_all)

        return {
            "success": True,
            "message": "Customer salesperson assignments updated",
            "result": result,
            "triggered_by": current_user.email
        }

    except Exception as e:
        logger.error(f"Error during customer assignment update: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Customer assignment update failed: {str(e)}"
        )


@router.post("/full-pipeline")
async def run_full_sync_pipeline(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
) -> Dict[str, Any]:
    """
    Run complete sync pipeline: users → customer assignments

    **Requires:** Admin role only

    **Process:**
    1. Sync all users from Zoho Books
    2. Update customer salesperson assignments

    **Returns:**
    - Combined results from all sync operations
    """
    try:
        logger.info(f"User {current_user.email} triggered full sync pipeline")

        zoho_client = get_zoho_client()
        sync_service = UserCustomerSyncService(db, zoho_client)

        # Run full pipeline
        result = await sync_service.full_sync_pipeline()

        return {
            "success": True,
            "message": "Full sync pipeline completed",
            "result": result,
            "triggered_by": current_user.email
        }

    except Exception as e:
        logger.error(f"Error during full sync pipeline: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Full sync pipeline failed: {str(e)}"
        )


@router.get("/user-mapping")
async def get_user_mapping(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"]))
) -> Dict[str, Any]:
    """
    Get mapping of Zoho user IDs to TSH ERP user IDs

    **Requires:** Admin or Manager role

    **Returns:**
    - Dictionary mapping Zoho user IDs to TSH ERP user IDs
    """
    try:
        zoho_client = get_zoho_client()
        sync_service = UserCustomerSyncService(db, zoho_client)

        mapping = await sync_service.get_user_mapping()

        return {
            "success": True,
            "mapping": mapping,
            "total_mapped_users": len(mapping)
        }

    except Exception as e:
        logger.error(f"Error fetching user mapping: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch user mapping: {str(e)}"
        )
