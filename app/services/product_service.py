from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.models.product import Product, Category
from app.schemas.product import ProductCreate, ProductUpdate, CategoryCreate, CategoryUpdate
from fastapi import HTTPException, status


class ProductService:
    """خدمة إدارة المنتجات"""

    @staticmethod
    def create_category(db: Session, category: CategoryCreate) -> Category:
        """إنشاء فئة جديدة"""
        # التحقق من عدم تكرار الاسم
        existing = db.query(Category).filter(Category.name == category.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists"
            )
        
        # التحقق من وجود الفئة الأساسية
        if category.parent_id:
            parent = db.query(Category).filter(Category.id == category.parent_id).first()
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent category not found"
                )
        
        db_category = Category(**category.dict())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category

    @staticmethod
    def get_categories(db: Session, skip: int = 0, limit: int = 100, 
                      active_only: bool = True) -> List[Category]:
        """الحصول على قائمة الفئات"""
        query = db.query(Category)
        
        if active_only:
            query = query.filter(Category.is_active == True)
            
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update_category(db: Session, category_id: int, category_update: CategoryUpdate) -> Category:
        """تحديث فئة"""
        db_category = db.query(Category).filter(Category.id == category_id).first()
        if not db_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        update_data = category_update.dict(exclude_unset=True)
        
        # التحقق من عدم تكرار الاسم
        if "name" in update_data:
            existing = db.query(Category).filter(
                Category.name == update_data["name"],
                Category.id != category_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category name already exists"
                )
        
        for field, value in update_data.items():
            setattr(db_category, field, value)
        
        db.commit()
        db.refresh(db_category)
        return db_category

    @staticmethod
    def create_product(db: Session, product: ProductCreate) -> Product:
        """إنشاء منتج جديد"""
        # التحقق من عدم تكرار رمز المنتج
        existing_sku = db.query(Product).filter(Product.sku == product.sku).first()
        if existing_sku:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product SKU already exists"
            )
        
        # التحقق من عدم تكرار الباركود إذا تم توفيره
        if product.barcode:
            existing_barcode = db.query(Product).filter(Product.barcode == product.barcode).first()
            if existing_barcode:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Barcode already exists"
                )
        
        # التحقق من وجود الفئة
        category = db.query(Category).filter(Category.id == product.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        db_product = Product(**product.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product

    @staticmethod
    def get_products(db: Session, skip: int = 0, limit: int = 100, 
                    search: Optional[str] = None, category_id: Optional[int] = None,
                    active_only: bool = True) -> List[Product]:
        """الحصول على قائمة المنتجات مع إمكانية البحث والتصفية"""
        query = db.query(Product)
        
        if active_only:
            query = query.filter(Product.is_active == True)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        if search:
            search_filter = or_(
                Product.name.ilike(f"%{search}%"),
                Product.sku.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> Product:
        """الحصول على منتج بالمعرف"""
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return product

    @staticmethod
    def get_product_by_sku(db: Session, sku: str) -> Product:
        """الحصول على منتج برمز المنتج"""
        product = db.query(Product).filter(Product.sku == sku).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return product

    @staticmethod
    def update_product(db: Session, product_id: int, product_update: ProductUpdate) -> Product:
        """تحديث منتج"""
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if not db_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        update_data = product_update.dict(exclude_unset=True)
        
        # التحقق من عدم تكرار رمز المنتج
        if "sku" in update_data:
            existing = db.query(Product).filter(
                Product.sku == update_data["sku"],
                Product.id != product_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Product SKU already exists"
                )
        
        # التحقق من عدم تكرار الباركود
        if "barcode" in update_data and update_data["barcode"]:
            existing = db.query(Product).filter(
                Product.barcode == update_data["barcode"],
                Product.id != product_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Barcode already exists"
                )
        
        # التحقق من وجود الفئة الجديدة
        if "category_id" in update_data:
            category = db.query(Category).filter(Category.id == update_data["category_id"]).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found"
                )
        
        for field, value in update_data.items():
            setattr(db_product, field, value)
        
        db.commit()
        db.refresh(db_product)
        return db_product

    @staticmethod
    def delete_product(db: Session, product_id: int) -> bool:
        """حذف منتج (تعطيل فقط)"""
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if not db_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # تعطيل المنتج بدلاً من حذفه
        db_product.is_active = False
        db.commit()
        return True
