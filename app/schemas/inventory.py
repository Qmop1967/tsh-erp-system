from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal
from .product import ProductSummary


# Inventory Item Schemas
class InventoryItemBase(BaseModel):
    product_id: int
    warehouse_id: int
    quantity_on_hand: Decimal = Field(0, ge=0)
    quantity_reserved: Decimal = Field(0, ge=0)
    quantity_ordered: Decimal = Field(0, ge=0)
    last_cost: Optional[Decimal] = Field(None, ge=0)
    average_cost: Optional[Decimal] = Field(None, ge=0)


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseModel):
    quantity_on_hand: Optional[Decimal] = Field(None, ge=0)
    quantity_reserved: Optional[Decimal] = Field(None, ge=0)
    quantity_ordered: Optional[Decimal] = Field(None, ge=0)
    last_cost: Optional[Decimal] = Field(None, ge=0)
    average_cost: Optional[Decimal] = Field(None, ge=0)


class InventoryItem(InventoryItemBase):
    id: int
    available_quantity: Decimal
    created_at: datetime
    updated_at: Optional[datetime]
    product: ProductSummary
    
    class Config:
        from_attributes = True


# Stock Movement Schemas
class StockMovementBase(BaseModel):
    inventory_item_id: int
    movement_type: str = Field(..., max_length=50)  # IN, OUT, TRANSFER, ADJUSTMENT
    reference_type: Optional[str] = Field(None, max_length=50)  # SALE, PURCHASE, TRANSFER, ADJUSTMENT
    reference_id: Optional[int] = None
    quantity: Decimal = Field(...)  # موجبة للدخول، سالبة للخروج
    unit_cost: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None

    @validator('movement_type')
    def validate_movement_type(cls, v):
        allowed_types = ['IN', 'OUT', 'TRANSFER', 'ADJUSTMENT']
        if v not in allowed_types:
            raise ValueError(f'Movement type must be one of: {", ".join(allowed_types)}')
        return v

    @validator('reference_type')
    def validate_reference_type(cls, v):
        if v is not None:
            allowed_types = ['SALE', 'PURCHASE', 'TRANSFER', 'ADJUSTMENT']
            if v not in allowed_types:
                raise ValueError(f'Reference type must be one of: {", ".join(allowed_types)}')
        return v


class StockMovementCreate(StockMovementBase):
    created_by: int


class StockMovement(StockMovementBase):
    id: int
    created_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Inventory Reports
class InventoryReport(BaseModel):
    """تقرير المخزون"""
    product_id: int
    product_sku: str
    product_name: str
    warehouse_id: int
    warehouse_name: str
    quantity_on_hand: Decimal
    quantity_reserved: Decimal
    available_quantity: Decimal
    min_stock_level: int
    reorder_point: int
    is_below_min: bool
    is_below_reorder: bool
    last_cost: Optional[Decimal]
    average_cost: Optional[Decimal]
    total_value: Optional[Decimal]
    
    class Config:
        from_attributes = True


class StockAdjustment(BaseModel):
    """تعديل المخزون"""
    inventory_item_id: int
    new_quantity: Decimal = Field(..., ge=0)
    reason: str
    notes: Optional[str] = None
