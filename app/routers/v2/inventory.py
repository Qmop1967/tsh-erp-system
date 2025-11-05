"""
Inventory Router V2

Clean architecture implementation of inventory endpoints using repository pattern.
"""

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.services.inventory_service import InventoryService
from app.application.dtos.inventory_dto import (
    InventoryItemResponseDTO,
    InventoryItemListResponseDTO,
    StockMovementResponseDTO,
    StockMovementListResponseDTO,
    StockUpdateDTO as InventoryStockUpdateDTO,
    StockTransferDTO,
    StockReserveDTO,
    StockReleaseDTO,
    InventorySearchDTO,
    StockMovementSearchDTO,
    InventorySummaryDTO,
    WarehouseStockSummaryDTO,
    StockValuationDTO,
)
from app.core.dependencies import get_inventory_service

router = APIRouter(prefix="/v2/inventory", tags=["inventory-v2"])


@router.get("/search", response_model=InventoryItemListResponseDTO)
async def search_inventory(
    product_id: Optional[int] = Query(None, description="Filter by product"),
    warehouse_id: Optional[int] = Query(None, description="Filter by warehouse"),
    low_stock: Optional[bool] = Query(None, description="Filter low stock items"),
    out_of_stock: Optional[bool] = Query(None, description="Filter out of stock items"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Search inventory items with filters.

    Args:
        product_id: Filter by product
        warehouse_id: Filter by warehouse
        low_stock: Filter low stock items
        out_of_stock: Filter out of stock items
        skip: Number of records to skip
        limit: Maximum records to return
        service: Inventory service dependency

    Returns:
        Inventory item list response
    """
    search_dto = InventorySearchDTO(
        product_id=product_id,
        warehouse_id=warehouse_id,
        low_stock=low_stock,
        out_of_stock=out_of_stock,
        skip=skip,
        limit=limit
    )
    return await service.search_inventory(search_dto)


@router.get("/product/{product_id}", response_model=InventoryItemListResponseDTO)
async def get_inventory_by_product(
    product_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Get all inventory items for a product across warehouses.

    Args:
        product_id: Product ID
        skip: Number of records to skip
        limit: Maximum records to return
        service: Inventory service dependency

    Returns:
        Inventory item list response
    """
    return await service.get_inventory_by_product(product_id, skip, limit)


@router.get("/warehouse/{warehouse_id}", response_model=InventoryItemListResponseDTO)
async def get_inventory_by_warehouse(
    warehouse_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Get all inventory items in a warehouse.

    Args:
        warehouse_id: Warehouse ID
        skip: Number of records to skip
        limit: Maximum records to return
        service: Inventory service dependency

    Returns:
        Inventory item list response
    """
    return await service.get_inventory_by_warehouse(warehouse_id, skip, limit)


@router.get("/product/{product_id}/warehouse/{warehouse_id}", response_model=InventoryItemResponseDTO)
async def get_inventory_item(
    product_id: int,
    warehouse_id: int,
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Get inventory item for a product in a warehouse.

    Args:
        product_id: Product ID
        warehouse_id: Warehouse ID
        service: Inventory service dependency

    Returns:
        Inventory item response

    Raises:
        HTTPException: 404 if inventory item not found
    """
    item = await service.get_inventory_item(product_id, warehouse_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No inventory found for product {product_id} in warehouse {warehouse_id}"
        )
    return item


@router.get("/product/{product_id}/summary", response_model=InventorySummaryDTO)
async def get_product_summary(
    product_id: int,
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Get inventory summary for a product.

    Args:
        product_id: Product ID
        service: Inventory service dependency

    Returns:
        Inventory summary
    """
    return await service.get_product_summary(product_id)


@router.get("/warehouse/{warehouse_id}/summary", response_model=WarehouseStockSummaryDTO)
async def get_warehouse_summary(
    warehouse_id: int,
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Get stock summary for a warehouse.

    Args:
        warehouse_id: Warehouse ID
        service: Inventory service dependency

    Returns:
        Warehouse stock summary
    """
    return await service.get_warehouse_summary(warehouse_id)


@router.get("/valuation", response_model=List[StockValuationDTO])
async def get_stock_valuation(
    product_id: Optional[int] = Query(None, description="Filter by product"),
    warehouse_id: Optional[int] = Query(None, description="Filter by warehouse"),
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Get stock valuation.

    Args:
        product_id: Filter by product (optional)
        warehouse_id: Filter by warehouse (optional)
        service: Inventory service dependency

    Returns:
        List of stock valuations
    """
    return await service.get_stock_valuation(product_id, warehouse_id)


@router.post("/stock/update", response_model=InventoryItemResponseDTO)
async def update_stock(
    dto: InventoryStockUpdateDTO,
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Update stock quantity.

    Args:
        dto: Stock update data
        service: Inventory service dependency

    Returns:
        Updated inventory item response

    Raises:
        HTTPException: 400 if validation fails
    """
    try:
        return await service.update_stock(dto)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/stock/transfer", status_code=status.HTTP_200_OK)
async def transfer_stock(
    dto: StockTransferDTO,
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Transfer stock between warehouses.

    Args:
        dto: Stock transfer data
        service: Inventory service dependency

    Returns:
        Success message

    Raises:
        HTTPException: 400 if validation fails
    """
    try:
        success = await service.transfer_stock(dto)
        return {
            "success": success,
            "message": f"Successfully transferred {dto.quantity} units of product {dto.product_id} "
                      f"from warehouse {dto.from_warehouse_id} to warehouse {dto.to_warehouse_id}"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/stock/reserve", response_model=InventoryItemResponseDTO)
async def reserve_stock(
    dto: StockReserveDTO,
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Reserve stock quantity.

    Args:
        dto: Stock reserve data
        service: Inventory service dependency

    Returns:
        Updated inventory item response

    Raises:
        HTTPException: 400 if validation fails
    """
    try:
        return await service.reserve_stock(dto)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/stock/release", response_model=InventoryItemResponseDTO)
async def release_stock(
    dto: StockReleaseDTO,
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Release reserved stock.

    Args:
        dto: Stock release data
        service: Inventory service dependency

    Returns:
        Updated inventory item response

    Raises:
        HTTPException: 400 if validation fails
    """
    try:
        return await service.release_stock(dto)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/movements/search", response_model=StockMovementListResponseDTO)
async def search_stock_movements(
    inventory_item_id: Optional[int] = Query(None, description="Filter by inventory item"),
    movement_type: Optional[str] = Query(None, description="Filter by movement type"),
    reference_type: Optional[str] = Query(None, description="Filter by reference type"),
    reference_id: Optional[int] = Query(None, description="Filter by reference ID"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Search stock movements with filters.

    Args:
        inventory_item_id: Filter by inventory item
        movement_type: Filter by movement type
        reference_type: Filter by reference type
        reference_id: Filter by reference ID
        start_date: Start date filter
        end_date: End date filter
        skip: Number of records to skip
        limit: Maximum records to return
        service: Inventory service dependency

    Returns:
        Stock movement list response
    """
    search_dto = StockMovementSearchDTO(
        inventory_item_id=inventory_item_id,
        movement_type=movement_type,
        reference_type=reference_type,
        reference_id=reference_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    return await service.get_stock_movements(search_dto)
