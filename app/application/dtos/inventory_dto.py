"""
Inventory Data Transfer Objects

DTOs for inventory data validation and transfer.
"""

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, validator


class InventoryItemResponseDTO(BaseModel):
    """DTO for inventory item response."""

    id: int
    product_id: int
    warehouse_id: int
    quantity_on_hand: float = 0.0
    quantity_reserved: float = 0.0
    quantity_ordered: float = 0.0
    last_cost: Optional[float] = None
    average_cost: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    @property
    def available_quantity(self) -> float:
        """Calculate available quantity."""
        return self.quantity_on_hand - self.quantity_reserved

    class Config:
        from_attributes = True


class InventoryItemListResponseDTO(BaseModel):
    """DTO for inventory item list response with pagination."""

    items: list[InventoryItemResponseDTO]
    total: int
    skip: int
    limit: int

    class Config:
        from_attributes = True


class StockMovementResponseDTO(BaseModel):
    """DTO for stock movement response."""

    id: int
    inventory_item_id: int
    movement_type: str
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    quantity: float
    unit_cost: Optional[float] = None
    notes: Optional[str] = None
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class StockMovementListResponseDTO(BaseModel):
    """DTO for stock movement list response with pagination."""

    items: list[StockMovementResponseDTO]
    total: int
    skip: int
    limit: int

    class Config:
        from_attributes = True


class StockUpdateDTO(BaseModel):
    """DTO for updating stock quantity."""

    product_id: int = Field(..., description="Product ID")
    warehouse_id: int = Field(..., description="Warehouse ID")
    quantity_change: float = Field(..., description="Quantity change (positive for IN, negative for OUT)")
    movement_type: str = Field(..., description="Movement type (IN, OUT, ADJUSTMENT)")
    reference_type: Optional[str] = Field(None, description="Reference type (SALE, PURCHASE, etc.)")
    reference_id: Optional[int] = Field(None, description="Reference ID")
    unit_cost: Optional[float] = Field(None, ge=0, description="Unit cost")
    notes: Optional[str] = Field(None, description="Movement notes")
    created_by: int = Field(..., description="User ID who created the movement")

    @validator('movement_type')
    def validate_movement_type(cls, v):
        """Validate movement type."""
        valid_types = ["IN", "OUT", "TRANSFER", "ADJUSTMENT"]
        if v not in valid_types:
            raise ValueError(f"Movement type must be one of: {', '.join(valid_types)}")
        return v

    class Config:
        from_attributes = True


class StockTransferDTO(BaseModel):
    """DTO for transferring stock between warehouses."""

    product_id: int = Field(..., description="Product ID")
    from_warehouse_id: int = Field(..., description="Source warehouse ID")
    to_warehouse_id: int = Field(..., description="Destination warehouse ID")
    quantity: float = Field(..., gt=0, description="Quantity to transfer")
    unit_cost: Optional[float] = Field(None, ge=0, description="Unit cost")
    notes: Optional[str] = Field(None, description="Transfer notes")
    created_by: int = Field(..., description="User ID who created the transfer")

    @validator('to_warehouse_id')
    def validate_different_warehouses(cls, v, values):
        """Validate that source and destination warehouses are different."""
        if 'from_warehouse_id' in values and v == values['from_warehouse_id']:
            raise ValueError('Source and destination warehouses must be different')
        return v

    class Config:
        from_attributes = True


class StockReserveDTO(BaseModel):
    """DTO for reserving stock quantity."""

    product_id: int = Field(..., description="Product ID")
    warehouse_id: int = Field(..., description="Warehouse ID")
    quantity: float = Field(..., gt=0, description="Quantity to reserve")

    class Config:
        from_attributes = True


class StockReleaseDTO(BaseModel):
    """DTO for releasing reserved stock."""

    product_id: int = Field(..., description="Product ID")
    warehouse_id: int = Field(..., description="Warehouse ID")
    quantity: float = Field(..., gt=0, description="Quantity to release")

    class Config:
        from_attributes = True


class InventorySearchDTO(BaseModel):
    """DTO for inventory search parameters."""

    product_id: Optional[int] = Field(None, description="Filter by product")
    warehouse_id: Optional[int] = Field(None, description="Filter by warehouse")
    low_stock: Optional[bool] = Field(None, description="Filter low stock items")
    out_of_stock: Optional[bool] = Field(None, description="Filter out of stock items")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum records to return")

    class Config:
        from_attributes = True


class StockMovementSearchDTO(BaseModel):
    """DTO for stock movement search parameters."""

    inventory_item_id: Optional[int] = Field(None, description="Filter by inventory item")
    movement_type: Optional[str] = Field(None, description="Filter by movement type")
    reference_type: Optional[str] = Field(None, description="Filter by reference type")
    reference_id: Optional[int] = Field(None, description="Filter by reference ID")
    start_date: Optional[date] = Field(None, description="Start date")
    end_date: Optional[date] = Field(None, description="End date")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum records to return")

    @validator('end_date')
    def validate_date_range(cls, v, values):
        """Validate that end date is not before start date."""
        if v and 'start_date' in values and values['start_date'] and v < values['start_date']:
            raise ValueError('End date cannot be before start date')
        return v

    class Config:
        from_attributes = True


class InventorySummaryDTO(BaseModel):
    """DTO for inventory summary information."""

    product_id: int
    total_quantity: float
    total_reserved: float
    total_available: float
    warehouses: int  # Number of warehouses with stock

    class Config:
        from_attributes = True


class WarehouseStockSummaryDTO(BaseModel):
    """DTO for warehouse stock summary."""

    warehouse_id: int
    total_products: int
    total_quantity: float
    low_stock_items: int
    out_of_stock_items: int

    class Config:
        from_attributes = True


class StockValuationDTO(BaseModel):
    """DTO for stock valuation information."""

    product_id: int
    warehouse_id: int
    quantity_on_hand: float
    average_cost: float
    total_value: float

    class Config:
        from_attributes = True
