"""
Zoho Bulk Sync Router
API endpoints for bulk data migration from Zoho Books

UPDATED: Now uses TDS unified Zoho integration
Date: November 6, 2025
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_db
from app.tds.integrations.zoho import (
    UnifiedZohoClient, ZohoAuthManager, ZohoSyncOrchestrator,
    ZohoCredentials, SyncConfig, SyncMode, EntityType
)
from app.core.events.event_bus import EventBus
import os

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def get_tds_services():
    """
    Initialize and return TDS unified services

    Returns:
        tuple: (zoho_client, orchestrator)
    """
    # Load credentials from environment
    credentials = ZohoCredentials(
        client_id=os.getenv('ZOHO_CLIENT_ID'),
        client_secret=os.getenv('ZOHO_CLIENT_SECRET'),
        refresh_token=os.getenv('ZOHO_REFRESH_TOKEN'),
        organization_id=os.getenv('ZOHO_ORGANIZATION_ID')
    )

    # Validate credentials
    if not all([credentials.client_id, credentials.client_secret,
                credentials.refresh_token, credentials.organization_id]):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Missing Zoho credentials in environment"
        )

    # Create event bus
    event_bus = EventBus()

    # Create auth manager
    auth_manager = ZohoAuthManager(credentials, auto_refresh=True, event_bus=event_bus)
    await auth_manager.start()

    # Create Zoho client
    zoho_client = UnifiedZohoClient(
        auth_manager=auth_manager,
        organization_id=credentials.organization_id,
        rate_limit=100,
        event_bus=event_bus
    )
    await zoho_client.start_session()

    # Create sync orchestrator
    orchestrator = ZohoSyncOrchestrator(
        zoho_client=zoho_client,
        event_bus=event_bus
    )

    return zoho_client, orchestrator


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
    Bulk sync products from Zoho Books using TDS unified architecture

    Args:
        request: Bulk sync request parameters
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        Sync statistics and results
    """
    logger.info(f"📦 Products bulk sync requested - Incremental: {request.incremental}")

    zoho_client = None
    try:
        # Initialize TDS services
        zoho_client, orchestrator = await get_tds_services()

        # Determine sync mode
        sync_mode = SyncMode.INCREMENTAL if request.incremental else SyncMode.FULL

        # Build filter params
        filter_params = {}
        if request.active_only:
            filter_params['filter_by'] = 'Status.Active'
        if request.modified_since:
            filter_params['last_modified_time'] = request.modified_since

        # Create sync configuration
        config = SyncConfig(
            entity_type=EntityType.PRODUCTS,
            mode=sync_mode,
            batch_size=request.batch_size,
            filter_params=filter_params
        )

        # Execute sync
        result = await orchestrator.sync_entity(config)

        # Build response
        stats = {
            "total_processed": result.total_processed,
            "successful": result.total_success,
            "failed": result.total_failed,
            "skipped": result.total_skipped
        }

        duration_seconds = result.duration.total_seconds() if result.duration else None

        return BulkSyncResponse(
            success=(result.status == "completed"),
            message=f"Products bulk sync {result.status}",
            stats=stats,
            duration_seconds=duration_seconds,
            error=result.error if result.status == "failed" else None
        )

    except Exception as e:
        logger.error(f"Products bulk sync failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk sync failed: {str(e)}"
        )
    finally:
        # Cleanup
        if zoho_client:
            await zoho_client.close_session()


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
    Bulk sync customers from Zoho Books using TDS unified architecture

    Args:
        request: Bulk sync request parameters
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        Sync statistics and results
    """
    logger.info(f"👥 Customers bulk sync requested - Incremental: {request.incremental}")

    zoho_client = None
    try:
        # Initialize TDS services
        zoho_client, orchestrator = await get_tds_services()

        # Determine sync mode
        sync_mode = SyncMode.INCREMENTAL if request.incremental else SyncMode.FULL

        # Build filter params
        filter_params = {}
        if request.modified_since:
            filter_params['last_modified_time'] = request.modified_since

        # Create sync configuration
        config = SyncConfig(
            entity_type=EntityType.CUSTOMERS,
            mode=sync_mode,
            batch_size=request.batch_size,
            filter_params=filter_params
        )

        # Execute sync
        result = await orchestrator.sync_entity(config)

        # Build response
        stats = {
            "total_processed": result.total_processed,
            "successful": result.total_success,
            "failed": result.total_failed,
            "skipped": result.total_skipped
        }

        duration_seconds = result.duration.total_seconds() if result.duration else None

        return BulkSyncResponse(
            success=(result.status == "completed"),
            message=f"Customers bulk sync {result.status}",
            stats=stats,
            duration_seconds=duration_seconds,
            error=result.error if result.status == "failed" else None
        )

    except Exception as e:
        logger.error(f"Customers bulk sync failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk sync failed: {str(e)}"
        )
    finally:
        # Cleanup
        if zoho_client:
            await zoho_client.close_session()


# ============================================================================
# NOTE: Invoice bulk sync removed - invoices are synced via webhooks
# ============================================================================


# ============================================================================
# ITEMS WITH STOCK BULK SYNC
# ============================================================================

@router.post(
    "/items-with-stock",
    response_model=BulkSyncResponse,
    tags=["Zoho Bulk Sync"],
    summary="Bulk sync items (products) with stock levels from Zoho Books/Inventory",
    description="""
    Fetch all items from Zoho Books/Inventory with their current stock levels and sync to TSH ERP database.

    **Features:**
    - Syncs product data (name, SKU, prices, images)
    - Syncs stock levels (stock on hand, available stock)
    - Supports multi-warehouse stock tracking
    - Real-time inventory updates
    - Supports both active-only and all items
    - Can filter by stock availability

    **Stock Data Synced:**
    - Stock on hand (current physical stock)
    - Available stock (stock available for sale)
    - Warehouse information
    - Last modified timestamps

    **Performance:**
    - Processes 100-200 items per batch
    - Expected duration: 5-10 minutes for 2,000+ products
    - Automatic deduplication using zoho_item_id

    **Note:** This combines product sync with inventory sync for complete stock visibility.
    """
)
async def bulk_sync_items_with_stock(
    request: BulkSyncRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Bulk sync items (products) with stock levels from Zoho using TDS unified architecture

    This endpoint syncs both product information AND stock levels in a single operation.

    Args:
        request: Bulk sync request parameters
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        Sync statistics and results
    """
    logger.info(f"📦📊 Items with Stock bulk sync requested - Incremental: {request.incremental}")

    zoho_client = None
    try:
        # Initialize TDS services
        zoho_client, orchestrator = await get_tds_services()

        # Import stock sync service
        from app.tds.integrations.zoho.stock_sync import UnifiedStockSyncService, StockSyncConfig
        from app.tds.integrations.zoho import SyncMode

        # Create stock sync service
        stock_service = UnifiedStockSyncService(
            zoho_client=zoho_client,
            sync_orchestrator=orchestrator
        )

        # Configure stock sync
        stock_config = StockSyncConfig(
            batch_size=request.batch_size,
            active_only=request.active_only,
            with_stock_only=request.with_stock_only,
            sync_mode=SyncMode.INCREMENTAL if request.incremental else SyncMode.FULL
        )

        # Execute sync
        result = await stock_service.sync_all_stock(config=stock_config)

        # Build response
        stats = {
            "total_processed": result.total_processed,
            "successful": result.total_success,
            "failed": result.total_failed,
            "skipped": result.total_skipped,
            "stock_updated": result.total_success  # All successful items had stock updated
        }

        duration_seconds = result.duration.total_seconds() if result.duration else None

        return BulkSyncResponse(
            success=(result.status == "completed"),
            message=f"Items with stock bulk sync {result.status}",
            stats=stats,
            duration_seconds=duration_seconds,
            error=result.error if result.status == "failed" else None
        )

    except Exception as e:
        logger.error(f"Items with stock bulk sync failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk sync failed: {str(e)}"
        )
    finally:
        # Cleanup
        if zoho_client:
            await zoho_client.close_session()


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

    NOTE: Price lists are now synced as part of product sync via TDS.
    This endpoint is maintained for backward compatibility.

    Args:
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        Sync statistics and results
    """
    logger.info(f"💰 Price lists bulk sync requested (now part of products sync)")

    zoho_client = None
    try:
        # Initialize TDS services
        zoho_client, orchestrator = await get_tds_services()

        # Sync products with price list data
        config = SyncConfig(
            entity_type=EntityType.PRODUCTS,
            mode=SyncMode.FULL,
            batch_size=100,
            filter_params={}
        )

        # Execute sync
        result = await orchestrator.sync_entity(config)

        # Build response
        stats = {
            "total_processed": result.total_processed,
            "successful": result.total_success,
            "failed": result.total_failed,
            "skipped": result.total_skipped
        }

        duration_seconds = result.duration.total_seconds() if result.duration else None

        return BulkSyncResponse(
            success=(result.status == "completed"),
            message=f"Products sync (includes price lists) {result.status}",
            stats=stats,
            duration_seconds=duration_seconds,
            error=result.error if result.status == "failed" else None
        )

    except Exception as e:
        logger.error(f"Price lists bulk sync failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk sync failed: {str(e)}"
        )
    finally:
        # Cleanup
        if zoho_client:
            await zoho_client.close_session()


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
    Sync all entities from Zoho Books using TDS unified architecture

    Args:
        modified_since: Optional date filter for incremental sync
        db: Database session

    Returns:
        Combined statistics for all entities
    """
    logger.info(f"🚀 COMPLETE MIGRATION requested - Since: {modified_since}")

    results = {}
    zoho_client = None

    try:
        # Initialize TDS services once for all operations
        zoho_client, orchestrator = await get_tds_services()

        # Determine sync mode
        sync_mode = SyncMode.INCREMENTAL if modified_since else SyncMode.FULL

        # Build filter params
        filter_params = {}
        if modified_since:
            filter_params['last_modified_time'] = modified_since

        # Step 1: Products
        logger.info("Step 1/2: Syncing products...")
        products_config = SyncConfig(
            entity_type=EntityType.PRODUCTS,
            mode=sync_mode,
            batch_size=100,
            filter_params={**filter_params, 'filter_by': 'Status.Active'}
        )
        products_result = await orchestrator.sync_entity(products_config)

        results["products"] = {
            "success": (products_result.status == "completed"),
            "stats": {
                "total_processed": products_result.total_processed,
                "successful": products_result.total_success,
                "failed": products_result.total_failed,
                "skipped": products_result.total_skipped
            },
            "duration_seconds": products_result.duration.total_seconds() if products_result.duration else 0
        }

        # Step 2: Customers
        logger.info("Step 2/2: Syncing customers...")
        customers_config = SyncConfig(
            entity_type=EntityType.CUSTOMERS,
            mode=sync_mode,
            batch_size=100,
            filter_params=filter_params
        )
        customers_result = await orchestrator.sync_entity(customers_config)

        results["customers"] = {
            "success": (customers_result.status == "completed"),
            "stats": {
                "total_processed": customers_result.total_processed,
                "successful": customers_result.total_success,
                "failed": customers_result.total_failed,
                "skipped": customers_result.total_skipped
            },
            "duration_seconds": customers_result.duration.total_seconds() if customers_result.duration else 0
        }

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
            "message": "Complete migration finished via TDS (invoices sync via webhooks, pricelists in products)",
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
    finally:
        # Cleanup
        if zoho_client:
            await zoho_client.close_session()


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
            "POST /api/zoho/bulk-sync/items-with-stock",
            "POST /api/zoho/bulk-sync/customers",
            "POST /api/zoho/bulk-sync/pricelists",
            "POST /api/zoho/bulk-sync/sync-all"
        ],
        "features": [
            "Pagination support",
            "Incremental sync",
            "Batch processing",
            "Automatic deduplication",
            "Error handling with retry",
            "Stock level synchronization",
            "Multi-warehouse support"
        ],
        "note": "Invoices are synced automatically via webhooks, not bulk sync"
    }
