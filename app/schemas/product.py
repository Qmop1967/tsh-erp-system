from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# Category Schemas
class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None


class Category(CategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Product Schemas
class ProductBase(BaseModel):
    sku: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    category_id: int
    unit_price: Decimal = Field(..., gt=0)
    cost_price: Optional[Decimal] = Field(None, ge=0)
    unit_of_measure: str = Field(..., max_length=50)
    min_stock_level: int = Field(0, ge=0)
    max_stock_level: Optional[int] = Field(None, ge=0)
    reorder_point: int = Field(0, ge=0)
    barcode: Optional[str] = Field(None, max_length=100)
    is_active: bool = True
    is_trackable: bool = True

    @validator('max_stock_level')
    def validate_max_stock_level(cls, v, values):
        if v is not None and 'min_stock_level' in values and v < values['min_stock_level']:
            raise ValueError('max_stock_level must be greater than or equal to min_stock_level')
        return v


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    sku: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    category_id: Optional[int] = None
    unit_price: Optional[Decimal] = Field(None, gt=0)
    cost_price: Optional[Decimal] = Field(None, ge=0)
    unit_of_measure: Optional[str] = Field(None, max_length=50)
    min_stock_level: Optional[int] = Field(None, ge=0)
    max_stock_level: Optional[int] = Field(None, ge=0)
    reorder_point: Optional[int] = Field(None, ge=0)
    barcode: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    is_trackable: Optional[bool] = None


class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    category: Category
    
    class Config:
        from_attributes = True


class ProductSummary(BaseModel):
    """ملخص المنتج للاستخدام في القوائم"""
    id: int
    sku: str
    name: str
    unit_price: Decimal
    unit_of_measure: str
    is_active: bool
    category_name: str
    
    class Config:
        from_attributes = True
