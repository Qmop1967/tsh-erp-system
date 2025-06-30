from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.schemas.product import (
    CategoryCreate, CategoryUpdate, Category,
    ProductCreate, ProductUpdate, Product, ProductSummary
)
from app.services.product_service import ProductService

router = APIRouter(tags=["products"])


# Category endpoints
@router.post("/categories", response_model=Category, status_code=201)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    """إنشاء فئة منتجات جديدة"""
    return ProductService.create_category(db, category)


@router.get("/categories", response_model=List[Category])
def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """الحصول على قائمة فئات المنتجات"""
    return ProductService.get_categories(db, skip, limit, active_only)


@router.put("/categories/{category_id}", response_model=Category)
def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """تحديث فئة منتجات"""
    return ProductService.update_category(db, category_id, category_update)


# Product endpoints
@router.post("/", response_model=Product, status_code=201)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    """إنشاء منتج جديد"""
    return ProductService.create_product(db, product)


@router.get("/", response_model=List[Product])
def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="البحث في الاسم أو رمز المنتج أو الوصف"),
    category_id: Optional[int] = Query(None, description="تصفية حسب الفئة"),
    active_only: bool = Query(True, description="المنتجات النشطة فقط"),
    db: Session = Depends(get_db)
):
    """الحصول على قائمة المنتجات مع إمكانية البحث والتصفية"""
    return ProductService.get_products(db, skip, limit, search, category_id, active_only)


@router.get("/{product_id}", response_model=Product)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """الحصول على منتج بالمعرف"""
    return ProductService.get_product_by_id(db, product_id)


@router.get("/sku/{sku}", response_model=Product)
def get_product_by_sku(
    sku: str,
    db: Session = Depends(get_db)
):
    """الحصول على منتج برمز المنتج (SKU)"""
    return ProductService.get_product_by_sku(db, sku)


@router.put("/{product_id}", response_model=Product)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db)
):
    """تحديث منتج"""
    return ProductService.update_product(db, product_id, product_update)


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """حذف منتج (تعطيل)"""
    ProductService.delete_product(db, product_id)
    return {"message": "Product deactivated successfully"}
