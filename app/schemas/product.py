from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


# Category Schemas
class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    name_ar: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    description_ar: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    name_ar: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    description_ar: Optional[str] = None
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
    name_ar: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    description_ar: Optional[str] = None
    category_id: int
    unit_price: Decimal = Field(..., gt=0)
    cost_price: Optional[Decimal] = Field(None, ge=0)
    unit_of_measure: str = Field(..., max_length=50)
    min_stock_level: int = Field(0, ge=0)
    max_stock_level: Optional[int] = Field(None, ge=0)
    reorder_point: int = Field(0, ge=0)
    barcode: Optional[str] = Field(None, max_length=100)
    
    # Media fields
    image_url: Optional[str] = Field(None, max_length=500)
    images: Optional[List[str]] = Field(default_factory=list)
    videos: Optional[List[str]] = Field(default_factory=list)
    
    # Additional fields
    weight: Optional[Decimal] = Field(None, ge=0)
    dimensions: Optional[Dict[str, Any]] = None
    color: Optional[str] = Field(None, max_length=50)
    size: Optional[str] = Field(None, max_length=50)
    brand: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    
    is_active: bool = True
    is_trackable: bool = True
    is_digital: bool = False
    is_featured: bool = False
    
    # SEO fields
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)

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
    name_ar: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    description_ar: Optional[str] = None
    category_id: Optional[int] = None
    unit_price: Optional[Decimal] = Field(None, gt=0)
    cost_price: Optional[Decimal] = Field(None, ge=0)
    unit_of_measure: Optional[str] = Field(None, max_length=50)
    min_stock_level: Optional[int] = Field(None, ge=0)
    max_stock_level: Optional[int] = Field(None, ge=0)
    reorder_point: Optional[int] = Field(None, ge=0)
    barcode: Optional[str] = Field(None, max_length=100)
    
    # Media fields
    image_url: Optional[str] = Field(None, max_length=500)
    images: Optional[List[str]] = None
    videos: Optional[List[str]] = None
    
    # Additional fields
    weight: Optional[Decimal] = Field(None, ge=0)
    dimensions: Optional[Dict[str, Any]] = None
    color: Optional[str] = Field(None, max_length=50)
    size: Optional[str] = Field(None, max_length=50)
    brand: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    
    is_active: Optional[bool] = None
    is_trackable: Optional[bool] = None
    is_digital: Optional[bool] = None
    is_featured: Optional[bool] = None
    
    # SEO fields
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = None
    tags: Optional[List[str]] = None


class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    category: Category
    
    class Config:
        from_attributes = True


class ProductResponse(Product):
    """Response model for Product API endpoints"""
    pass


class ProductSummary(BaseModel):
    """ملخص المنتج للاستخدام في القوائم"""
    id: int
    sku: str
    name: str
    name_ar: Optional[str] = None
    unit_price: Decimal
    unit_of_measure: str
    is_active: bool
    category_name: str
    category_name_ar: Optional[str] = None
    image_url: Optional[str] = None
    actual_available_stock: int = 0  # Stock quantity from Zoho

    class Config:
        from_attributes = True


# AI Translation Request Schema
class TranslateNameRequest(BaseModel):
    english_name: str = Field(..., max_length=200)
    description: Optional[str] = None


class TranslateNameResponse(BaseModel):
    arabic_name: str
    arabic_description: Optional[str] = None


# Media Upload Schemas
class MediaUploadRequest(BaseModel):
    product_id: int
    media_type: str = Field(..., pattern="^(image|video)$")
    media_url: str = Field(..., max_length=500)
    is_primary: bool = False


class MediaUploadResponse(BaseModel):
    success: bool
    message: str
    media_url: str
