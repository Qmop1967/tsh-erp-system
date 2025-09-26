from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import List, Optional
from fastapi import HTTPException, status
from app.models.product import Product, Category
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductSummary, 
    TranslateNameRequest, TranslateNameResponse,
    MediaUploadRequest, MediaUploadResponse,
    CategoryCreate, CategoryUpdate
)


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
        # التحقق من وجود الفئة
        category = db.query(Category).filter(Category.id == product.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

        # التحقق من عدم تكرار SKU
        existing_product = db.query(Product).filter(Product.sku == product.sku).first()
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SKU already exists"
            )

        # التحقق من عدم تكرار الباركود
        if product.barcode:
            existing_barcode = db.query(Product).filter(Product.barcode == product.barcode).first()
            if existing_barcode:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Barcode already exists"
                )

        # إنشاء المنتج
        db_product = Product(**product.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product

    @staticmethod
    def get_product(db: Session, product_id: int) -> Optional[Product]:
        """الحصول على منتج بالمعرف"""
        return db.query(Product).options(joinedload(Product.category)).filter(
            Product.id == product_id
        ).first()

    @staticmethod
    def get_products(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Product]:
        """الحصول على قائمة المنتجات مع البحث والفلترة"""
        query = db.query(Product).options(joinedload(Product.category))
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        if is_active is not None:
            query = query.filter(Product.is_active == is_active)
        
        if search:
            query = query.filter(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.name_ar.ilike(f"%{search}%"),
                    Product.sku.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%"),
                    Product.description_ar.ilike(f"%{search}%")
                )
            )
        
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_products_summary(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        category_id: Optional[int] = None,
        search: Optional[str] = None
    ) -> List[ProductSummary]:
        """الحصول على ملخص المنتجات للقوائم"""
        query = db.query(Product).join(Category)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        if search:
            query = query.filter(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.name_ar.ilike(f"%{search}%"),
                    Product.sku.ilike(f"%{search}%")
                )
            )
        
        products = query.offset(skip).limit(limit).all()
        
        # Convert to ProductSummary with category name
        result = []
        for product in products:
            summary_dict = {
                "id": product.id,
                "sku": product.sku,
                "name": product.name,
                "name_ar": product.name_ar,
                "unit_price": product.unit_price,
                "unit_of_measure": product.unit_of_measure,
                "is_active": product.is_active,
                "category_name": product.category.name if product.category else "Unknown",
                "category_name_ar": product.category.name_ar if product.category else None,
                "image_url": product.image_url
            }
            summary = ProductSummary(**summary_dict)
            result.append(summary)
        
        return result

    @staticmethod
    def update_product(db: Session, product_id: int, product_update: ProductUpdate) -> Product:
        """تحديث منتج"""
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if not db_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        # التحقق من SKU إذا تم تحديثه
        if product_update.sku and product_update.sku != db_product.sku:
            existing_product = db.query(Product).filter(
                and_(Product.sku == product_update.sku, Product.id != product_id)
            ).first()
            if existing_product:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="SKU already exists"
                )

        # التحقق من الباركود إذا تم تحديثه
        if product_update.barcode and product_update.barcode != db_product.barcode:
            existing_barcode = db.query(Product).filter(
                and_(Product.barcode == product_update.barcode, Product.id != product_id)
            ).first()
            if existing_barcode:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Barcode already exists"
                )

        # تحديث الحقول
        update_data = product_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)

        db.commit()
        db.refresh(db_product)
        return db_product

    @staticmethod
    def delete_product(db: Session, product_id: int) -> bool:
        """حذف منتج"""
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if not db_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        # التحقق من عدم وجود مراجع أخرى (مبيعات، مشتريات، مخزون)
        # يمكن إضافة منطق إضافي هنا للتحقق من المراجع

        db.delete(db_product)
        db.commit()
        return True

    @staticmethod
    async def translate_product_name(request: TranslateNameRequest) -> TranslateNameResponse:
        """ترجمة اسم المنتج إلى العربية باستخدام AI"""
        try:
            # Using a simple AI translation service (you can replace with OpenAI, Google Translate, etc.)
            # For demo purposes, I'll create a simple mapping and rules-based translation
            
            # Simple translation rules (you can enhance this with actual AI service)
            translation_map = {
                "laptop": "لابتوب",
                "computer": "كمبيوتر",
                "phone": "هاتف",
                "mobile": "جوال",
                "iphone": "آيفون",
                "samsung": "سامسونج",
                "dell": "ديل",
                "hp": "إتش بي",
                "apple": "أبل",
                "mouse": "فأرة",
                "keyboard": "لوحة مفاتيح",
                "monitor": "شاشة",
                "speaker": "سماعة",
                "headphone": "سماعة رأس",
                "tablet": "تابلت",
                "watch": "ساعة",
                "camera": "كاميرا",
                "printer": "طابعة",
                "scanner": "ماسح ضوئي",
                "router": "راوتر",
                "cable": "كابل",
                "charger": "شاحن",
                "battery": "بطارية",
                "memory": "ذاكرة",
                "storage": "تخزين",
                "hard drive": "قرص صلب",
                "ssd": "إس إس دي",
                "usb": "يو إس بي",
                "bluetooth": "بلوتوث",
                "wireless": "لاسلكي",
                "pro": "برو",
                "plus": "بلس",
                "max": "ماكس",
                "mini": "ميني",
                "air": "إير",
                "studio": "ستوديو",
                "premium": "بريميوم",
                "standard": "قياسي",
                "basic": "أساسي",
                "professional": "احترافي",
                "gaming": "ألعاب"
            }
            
            english_name = request.english_name.lower()
            arabic_name = ""
            
            # Try to translate each word
            words = english_name.split()
            arabic_words = []
            
            for word in words:
                # Remove special characters
                clean_word = ''.join(char for char in word if char.isalnum())
                if clean_word in translation_map:
                    arabic_words.append(translation_map[clean_word])
                else:
                    # If no translation found, keep the English word
                    arabic_words.append(word)
            
            arabic_name = " ".join(arabic_words)
            
            # If no translation was made, create a simple Arabic version
            if arabic_name.lower() == english_name.lower():
                arabic_name = f"{request.english_name}"  # Keep original if no translation
            
            # Translate description if provided
            arabic_description = None
            if request.description:
                # Simple description translation (can be enhanced with actual AI)
                desc_lower = request.description.lower()
                if "laptop" in desc_lower:
                    arabic_description = request.description.replace("laptop", "لابتوب")
                elif "phone" in desc_lower:
                    arabic_description = request.description.replace("phone", "هاتف")
                else:
                    arabic_description = request.description  # Keep original
            
            return TranslateNameResponse(
                arabic_name=arabic_name,
                arabic_description=arabic_description
            )
            
        except Exception as e:
            # Fallback: return the original name if translation fails
            return TranslateNameResponse(
                arabic_name=request.english_name,
                arabic_description=request.description
            )

    @staticmethod
    def upload_media(db: Session, media_request: MediaUploadRequest) -> MediaUploadResponse:
        """رفع وسائط للمنتج"""
        # التحقق من وجود المنتج
        product = db.query(Product).filter(Product.id == media_request.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        try:
            if media_request.media_type == "image":
                if media_request.is_primary:
                    # Set as primary image
                    product.image_url = media_request.media_url
                else:
                    # Add to images list
                    if product.images is None:
                        product.images = []
                    product.images.append(media_request.media_url)
                    
            elif media_request.media_type == "video":
                # Add to videos list
                if product.videos is None:
                    product.videos = []
                product.videos.append(media_request.media_url)

            db.commit()
            db.refresh(product)

            return MediaUploadResponse(
                success=True,
                message="Media uploaded successfully",
                media_url=media_request.media_url
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload media: {str(e)}"
            )

    @staticmethod
    def remove_media(db: Session, product_id: int, media_url: str, media_type: str) -> bool:
        """حذف وسائط من المنتج"""
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        try:
            if media_type == "image":
                if product.image_url == media_url:
                    product.image_url = None
                elif product.images and media_url in product.images:
                    product.images.remove(media_url)
                    
            elif media_type == "video":
                if product.videos and media_url in product.videos:
                    product.videos.remove(media_url)

            db.commit()
            return True
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to remove media: {str(e)}"
            )

    @staticmethod
    def get_product_statistics(db: Session) -> dict:
        """إحصائيات المنتجات"""
        total_products = db.query(Product).count()
        active_products = db.query(Product).filter(Product.is_active == True).count()
        inactive_products = total_products - active_products
        
        # Products by category
        categories_stats = db.query(Category.name, db.func.count(Product.id)).join(
            Product, Category.id == Product.category_id
        ).group_by(Category.name).all()

        return {
            "total_products": total_products,
            "active_products": active_products,
            "inactive_products": inactive_products,
            "categories_stats": dict(categories_stats)
        }
