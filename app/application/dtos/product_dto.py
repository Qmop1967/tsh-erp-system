"""
Product Data Transfer Objects

DTOs for product data validation and transfer.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from decimal import Decimal


class ProductCreateDTO(BaseModel):
    """DTO for creating a new product."""

    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    sku: Optional[str] = Field(None, max_length=100, description="Stock Keeping Unit")
    barcode: Optional[str] = Field(None, max_length=100, description="Product barcode")
    description: Optional[str] = Field(None, description="Product description")

    # Pricing
    price: float = Field(..., ge=0, description="Product selling price")
    cost: Optional[float] = Field(None, ge=0, description="Product cost price")
    currency: Optional[str] = Field("IQD", max_length=3, description="Currency code")

    # Inventory
    stock_quantity: int = Field(0, ge=0, description="Current stock quantity")
    reorder_level: Optional[int] = Field(None, ge=0, description="Reorder level threshold")
    min_stock_level: Optional[int] = Field(None, ge=0, description="Minimum stock level")
    max_stock_level: Optional[int] = Field(None, ge=0, description="Maximum stock level")

    # Classification
    category_id: Optional[int] = Field(None, description="Category ID")
    supplier_id: Optional[int] = Field(None, description="Primary supplier ID")

    # Physical attributes
    weight: Optional[float] = Field(None, ge=0, description="Product weight (kg)")
    dimensions: Optional[str] = Field(None, max_length=100, description="Product dimensions")
    unit: Optional[str] = Field("piece", max_length=50, description="Unit of measurement")

    # Tax and accounting
    tax_rate: Optional[float] = Field(0.0, ge=0, le=100, description="Tax rate percentage")
    tax_exempt: bool = Field(False, description="Whether product is tax exempt")

    # E-commerce
    is_featured: bool = Field(False, description="Whether product is featured")
    image_url: Optional[str] = Field(None, max_length=500, description="Product image URL")

    # Integration
    zoho_item_id: Optional[str] = Field(None, max_length=100, description="Zoho item ID")

    # Status
    is_active: bool = Field(True, description="Whether product is active")
    notes: Optional[str] = Field(None, description="Additional notes")

    @validator('sku')
    def validate_sku(cls, v):
        """Validate SKU format."""
        if v:
            return v.upper().strip()
        return v

    @validator('price', 'cost')
    def validate_prices(cls, v):
        """Validate prices are positive."""
        if v is not None and v < 0:
            raise ValueError('Prices must be non-negative')
        return v

    class Config:
        from_attributes = True


class ProductUpdateDTO(BaseModel):
    """DTO for updating an existing product."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Product name")
    sku: Optional[str] = Field(None, max_length=100, description="Stock Keeping Unit")
    barcode: Optional[str] = Field(None, max_length=100, description="Product barcode")
    description: Optional[str] = Field(None, description="Product description")

    # Pricing
    price: Optional[float] = Field(None, ge=0, description="Product selling price")
    cost: Optional[float] = Field(None, ge=0, description="Product cost price")
    currency: Optional[str] = Field(None, max_length=3, description="Currency code")

    # Inventory
    stock_quantity: Optional[int] = Field(None, ge=0, description="Current stock quantity")
    reorder_level: Optional[int] = Field(None, ge=0, description="Reorder level threshold")
    min_stock_level: Optional[int] = Field(None, ge=0, description="Minimum stock level")
    max_stock_level: Optional[int] = Field(None, ge=0, description="Maximum stock level")

    # Classification
    category_id: Optional[int] = Field(None, description="Category ID")
    supplier_id: Optional[int] = Field(None, description="Primary supplier ID")

    # Physical attributes
    weight: Optional[float] = Field(None, ge=0, description="Product weight (kg)")
    dimensions: Optional[str] = Field(None, max_length=100, description="Product dimensions")
    unit: Optional[str] = Field(None, max_length=50, description="Unit of measurement")

    # Tax and accounting
    tax_rate: Optional[float] = Field(None, ge=0, le=100, description="Tax rate percentage")
    tax_exempt: Optional[bool] = Field(None, description="Whether product is tax exempt")

    # E-commerce
    is_featured: Optional[bool] = Field(None, description="Whether product is featured")
    image_url: Optional[str] = Field(None, max_length=500, description="Product image URL")

    # Integration
    zoho_item_id: Optional[str] = Field(None, max_length=100, description="Zoho item ID")

    # Status
    is_active: Optional[bool] = Field(None, description="Whether product is active")
    notes: Optional[str] = Field(None, description="Additional notes")

    @validator('sku')
    def validate_sku(cls, v):
        """Validate SKU format."""
        if v:
            return v.upper().strip()
        return v

    class Config:
        from_attributes = True


class ProductResponseDTO(BaseModel):
    """DTO for product response."""

    id: int
    name: str
    sku: Optional[str] = None
    barcode: Optional[str] = None
    description: Optional[str] = None

    # Pricing
    price: float
    cost: Optional[float] = None
    currency: str = "IQD"

    # Inventory
    stock_quantity: int = 0
    reorder_level: Optional[int] = None
    min_stock_level: Optional[int] = None
    max_stock_level: Optional[int] = None

    # Classification
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None

    # Physical attributes
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    unit: str = "piece"

    # Tax and accounting
    tax_rate: float = 0.0
    tax_exempt: bool = False

    # E-commerce
    is_featured: bool = False
    image_url: Optional[str] = None

    # Integration
    zoho_item_id: Optional[str] = None

    # Status
    is_active: bool = True
    notes: Optional[str] = None

    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductListResponseDTO(BaseModel):
    """DTO for product list response with pagination."""

    items: list[ProductResponseDTO]
    total: int
    skip: int
    limit: int

    class Config:
        from_attributes = True


class ProductSearchDTO(BaseModel):
    """DTO for product search parameters."""

    query: Optional[str] = Field(None, description="Search query")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    category_id: Optional[int] = Field(None, description="Filter by category")
    supplier_id: Optional[int] = Field(None, description="Filter by supplier")
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price")
    low_stock: Optional[bool] = Field(None, description="Filter low stock products")
    out_of_stock: Optional[bool] = Field(None, description="Filter out of stock products")
    is_featured: Optional[bool] = Field(None, description="Filter featured products")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum records to return")

    class Config:
        from_attributes = True


class ProductSummaryDTO(BaseModel):
    """DTO for product summary information."""

    id: int
    name: str
    sku: Optional[str] = None
    barcode: Optional[str] = None
    price: float
    stock_quantity: int = 0
    is_active: bool = True
    image_url: Optional[str] = None

    class Config:
        from_attributes = True


class StockUpdateDTO(BaseModel):
    """DTO for updating product stock quantity."""

    product_id: int = Field(..., description="Product ID")
    quantity_change: int = Field(..., description="Quantity change (positive for increase, negative for decrease)")
    reason: Optional[str] = Field(None, max_length=255, description="Reason for stock update")

    class Config:
        from_attributes = True


class ProductStockStatusDTO(BaseModel):
    """DTO for product stock status information."""

    product_id: int
    name: str
    sku: Optional[str] = None
    stock_quantity: int
    reorder_level: Optional[int] = None
    status: str  # "in_stock", "low_stock", "out_of_stock"
    needs_reorder: bool

    class Config:
        from_attributes = True
