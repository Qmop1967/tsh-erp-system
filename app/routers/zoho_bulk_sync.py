"""
Zoho Bulk Sync Router
API endpoints for bulk data migration from Zoho Books
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_db
from app.services.zoho_bulk_sync import ZohoBulkSyncService

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================================

class BulkSyncRequest(BaseModel):
    """Request model for bulk sync operations"""
    incremental: bool = Field(
        default=False,
        description="If true, only sync items modified since the specified date"
    )
    modified_since: Optional[str] = Field(
        default=None,
        description="ISO date string (YYYY-MM-DD) for incremental sync"
    )
    batch_size: int = Field(
        default=100,
        ge=10,
        le=200,
        description="Number of items to process in each batch"
    )
    active_only: bool = Field(
        default=True,
        description="If true, only sync active items (default: True)"
    )
    with_stock_only: bool = Field(
        default=True,
        description="If true, only sync items with stock on hand (default: True)"
    )
    sync_images: bool = Field(
        default=True,
        description="If true, sync product images from Zoho (default: True)"
    )


class BulkSyncResponse(BaseModel):
    """Response model for bulk sync operations"""
    success: bool
    message: str
    stats: dict
    duration_seconds: Optional[float] = None
    error: Optional[str] = None


# ============================================================================
# PRODUCTS BULK SYNC
# ============================================================================

@router.post(
    "/products",
    response_model=BulkSyncResponse,
    tags=["Zoho Bulk Sync"],
    summary="Bulk sync products from Zoho Books",
    description="""
    Fetch all products (items) from Zoho Books and sync to TSH ERP database.

    **Modes:**
    - **Full sync** (incremental=false): Import ALL products from Zoho Books
    - **Incremental sync** (incremental=true): Only import products modified since specified date

    **Performance:**
    - Processes 100-200 items per batch
    - Expected duration: 5-10 minutes for 2,000+ products
    - Automatic deduplication using zoho_item_id

    **Note:** This operation may take several minutes for large catalogs.
    """
)
async def bulk_sync_products(
    request: BulkSyncRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Bulk sync products from Zoho Books

    Args:
        request: Bulk sync request parameters
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        Sync statistics and results
    """
    logger.info(f"📦 Products bulk sync requested - Incremental: {request.incremental}")

    try:
        service = ZohoBulkSyncService(db)

        result = await service.sync_products(
            incremental=request.incremental,
            modified_since=request.modified_since,
            batch_size=request.batch_size,
            active_only=request.active_only,
            with_stock_only=request.with_stock_only,
            sync_images=request.sync_images
        )

        if result["success"]:
            stats = result["stats"]
            return BulkSyncResponse(
                success=True,
                message=f"Products bulk sync completed successfully",
                stats=stats,
                duration_seconds=result.get("duration_seconds")
            )
        else:
            return BulkSyncResponse(
                success=False,
                message="Products bulk sync failed",
                stats=result["stats"],
                error=result.get("error")
            )

    except Exception as e:
        logger.error(f"Products bulk sync failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk sync failed: {str(e)}"
        )


# ============================================================================
# CUSTOMERS BULK SYNC
# ============================================================================

@router.post(
    "/customers",
    response_model=BulkSyncResponse,
    tags=["Zoho Bulk Sync"],
    summary="Bulk sync customers from Zoho Books",
    description="""
    Fetch all customers (contacts) from Zoho Books and sync to TSH ERP database.

    **Features:**
    - Imports customer details and addresses
    - Handles both business and individual contacts
    - Automatic email uniqueness validation
    - Syncs billing and shipping addresses

    **Performance:**
    - Expected duration: 1-2 minutes for hundreds of customers
    """
)
async def bulk_sync_customers(
    request: BulkSyncRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Bulk sync customers from Zoho Books

    Args:
        request: Bulk sync request parameters
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        Sync statistics and results
    """
    logger.info(f"👥 Customers bulk sync requested - Incremental: {request.incremental}")

    try:
        service = ZohoBulkSyncService(db)

        result = await service.sync_customers(
            incremental=request.incremental,
            modified_since=request.modified_since,
            batch_size=request.batch_size
        )

        if result["success"]:
            stats = result["stats"]
            return BulkSyncResponse(
                success=True,
                message=f"Customers bulk sync completed successfully",
                stats=stats,
                duration_seconds=result.get("duration_seconds")
            )
        else:
            return BulkSyncResponse(
                success=False,
                message="Customers bulk sync failed",
                stats=result["stats"],
                error=result.get("error")
            )

    except Exception as e:
        logger.error(f"Customers bulk sync failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk sync failed: {str(e)}"
        )


# ============================================================================
# NOTE: Invoice bulk sync removed - invoices are synced via webhooks
# ============================================================================


# ============================================================================
# PRICE LISTS BULK SYNC
# ============================================================================

@router.post(
    "/pricelists",
    response_model=BulkSyncResponse,
    tags=["Zoho Bulk Sync"],
    summary="Bulk sync price lists from Zoho Books",
    description="""
    Fetch all price lists from Zoho Books and sync to TSH ERP database.

    **Features:**
    - Imports all price lists with item-specific prices
    - Supports multi-currency pricing
    - Links prices to existing products
    - Handles percentage-based and fixed pricing

    **Performance:**
    - Expected duration: 2-3 minutes
    """
)
async def bulk_sync_pricelists(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Bulk sync price lists from Zoho Books

    Args:
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        Sync statistics and results
    """
    logger.info(f"💰 Price lists bulk sync requested")

    try:
        service = ZohoBulkSyncService(db)

        result = await service.sync_pricelists()

        if result["success"]:
            stats = result["stats"]
            return BulkSyncResponse(
                success=True,
                message=f"Price lists bulk sync completed successfully",
                stats=stats,
                duration_seconds=result.get("duration_seconds")
            )
        else:
            return BulkSyncResponse(
                success=False,
                message="Price lists bulk sync failed",
                stats=result["stats"],
                error=result.get("error")
            )

    except Exception as e:
        logger.error(f"Price lists bulk sync failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk sync failed: {str(e)}"
        )


# ============================================================================
# SYNC ALL (COMPLETE MIGRATION)
# ============================================================================

@router.post(
    "/sync-all",
    response_model=dict,
    tags=["Zoho Bulk Sync"],
    summary="Complete migration - sync all entities",
    description="""
    Execute a complete data migration from Zoho Books to TSH ERP.

    **Order of execution:**
    1. Products (foundation data)
    2. Customers (required for orders)
    3. Price Lists (product pricing)

    **Total Duration:** 10-15 minutes for complete migration

    **Note:** Invoices are synced automatically via webhooks, not included in bulk sync.
    """
)
async def sync_all_entities(
    modified_since: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Sync all entities from Zoho Books

    Args:
        modified_since: Optional date filter for incremental sync
        db: Database session

    Returns:
        Combined statistics for all entities
    """
    logger.info(f"🚀 COMPLETE MIGRATION requested - Since: {modified_since}")

    results = {}

    try:
        service = ZohoBulkSyncService(db)

        # Step 1: Products
        logger.info("Step 1/3: Syncing products...")
        products_result = await service.sync_products(
            incremental=bool(modified_since),
            modified_since=modified_since
        )
        results["products"] = products_result

        # Step 2: Customers
        logger.info("Step 2/3: Syncing customers...")
        customers_result = await service.sync_customers(
            incremental=bool(modified_since),
            modified_since=modified_since
        )
        results["customers"] = customers_result

        # Step 3: Price Lists
        logger.info("Step 3/3: Syncing price lists...")
        pricelists_result = await service.sync_pricelists()
        results["pricelists"] = pricelists_result

        # Calculate totals
        total_success = all(r["success"] for r in results.values())
        total_items = sum(r["stats"]["total_processed"] for r in results.values())
        total_successful = sum(r["stats"]["successful"] for r in results.values())
        total_failed = sum(r["stats"]["failed"] for r in results.values())

        logger.info(f"✅ COMPLETE MIGRATION finished!")
        logger.info(f"   Total items: {total_items}")
        logger.info(f"   Successful: {total_successful}")
        logger.info(f"   Failed: {total_failed}")

        return {
            "success": total_success,
            "message": "Complete migration finished (invoices sync via webhooks)",
            "results": results,
            "totals": {
                "items": total_items,
                "successful": total_successful,
                "failed": total_failed
            }
        }

    except Exception as e:
        logger.error(f"Complete migration failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Migration failed: {str(e)}"
        )


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get(
    "/status",
    tags=["Zoho Bulk Sync"],
    summary="Check bulk sync service status"
)
async def get_sync_status(db: AsyncSession = Depends(get_async_db)):
    """
    Get bulk sync service status

    Returns:
        Service health and configuration
    """
    return {
        "service": "Zoho Bulk Sync",
        "status": "healthy",
        "available_operations": [
            "POST /api/zoho/bulk-sync/products",
            "POST /api/zoho/bulk-sync/customers",
            "POST /api/zoho/bulk-sync/pricelists",
            "POST /api/zoho/bulk-sync/sync-all"
        ],
        "features": [
            "Pagination support",
            "Incremental sync",
            "Batch processing",
            "Automatic deduplication",
            "Error handling with retry"
        ],
        "note": "Invoices are synced automatically via webhooks, not bulk sync"
    }
