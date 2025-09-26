from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from typing import List, Optional
from app.db.database import get_db
from app.models.product import Product, Category
from app.schemas.product import (
    Product as ProductSchema, ProductCreate, ProductUpdate, ProductSummary,
    Category as CategorySchema, CategoryCreate, CategoryUpdate,
    TranslateNameRequest, TranslateNameResponse,
    MediaUploadRequest, MediaUploadResponse
)
from app.services.product_service import ProductService
from pydantic import BaseModel
import json

router = APIRouter()


# Product CRUD Operations
@router.post("/", response_model=ProductSchema, status_code=201)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    """إنشاء منتج جديد"""
    # Check if category exists
    category = db.query(Category).filter(Category.id == product.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if SKU already exists
    existing_sku = db.query(Product).filter(Product.sku == product.sku).first()
    if existing_sku:
        raise HTTPException(status_code=400, detail="SKU already exists")
    
    # Check if barcode already exists
    if product.barcode:
        existing_barcode = db.query(Product).filter(Product.barcode == product.barcode).first()
        if existing_barcode:
            raise HTTPException(status_code=400, detail="Barcode already exists")
    
    # Create product
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/", response_model=List[ProductSummary])
def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """الحصول على قائمة المنتجات مع البحث والفلترة"""
    query = db.query(Product).join(Category)
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    
    if search:
        search_filter = or_(
            Product.name.ilike(f"%{search}%"),
            Product.name_ar.ilike(f"%{search}%") if Product.name_ar.isnot(None) else False,
            Product.sku.ilike(f"%{search}%"),
            Product.description.ilike(f"%{search}%") if Product.description.isnot(None) else False
        )
        query = query.filter(search_filter)
    
    products = query.offset(skip).limit(limit).all()
    
    # Convert to ProductSummary
    result = []
    for product in products:
        summary_data = {
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
        result.append(ProductSummary(**summary_data))
    
    return result


@router.get("/{product_id}", response_model=ProductSchema)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """الحصول على منتج محدد"""
    product = db.query(Product).options(joinedload(Product.category)).filter(
        Product.id == product_id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductSchema)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db)
):
    """تحديث منتج"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_update.dict(exclude_unset=True)
    
    # Check SKU uniqueness if updating
    if "sku" in update_data and update_data["sku"] != db_product.sku:
        existing_sku = db.query(Product).filter(
            Product.sku == update_data["sku"],
            Product.id != product_id
        ).first()
        if existing_sku:
            raise HTTPException(status_code=400, detail="SKU already exists")
    
    # Check barcode uniqueness if updating
    if "barcode" in update_data and update_data["barcode"] and update_data["barcode"] != db_product.barcode:
        existing_barcode = db.query(Product).filter(
            Product.barcode == update_data["barcode"],
            Product.id != product_id
        ).first()
        if existing_barcode:
            raise HTTPException(status_code=400, detail="Barcode already exists")
    
    # Update fields
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """حذف منتج"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Soft delete - just deactivate instead of hard delete
    db_product.is_active = False
    db.commit()
    return {"message": "Product deactivated successfully"}


# AI Translation Feature
class TranslateRequest(BaseModel):
    english_name: str
    description: Optional[str] = None

class TranslateResponse(BaseModel):
    arabic_name: str
    arabic_description: Optional[str] = None


@router.post("/translate", response_model=TranslateResponse)
async def translate_product_name(request: TranslateRequest):
    """
    Translate English product name to Arabic using AI
    ترجمة اسم المنتج من الإنجليزية إلى العربية باستخدام الذكاء الاصطناعي
    """
    try:
        # For demo purposes, use a simple translation mapping
        # In production, you would use OpenAI, Google Translate, or other AI services
        
        # Simple rule-based translation for common words
        translation_map = {
            "laptop": "لابتوب",
            "computer": "كمبيوتر",
            "phone": "هاتف",
            "mobile": "موبايل",
            "tablet": "لوحي",
            "keyboard": "لوحة مفاتيح",
            "mouse": "ماوس",
            "monitor": "شاشة",
            "printer": "طابعة",
            "scanner": "ماسح ضوئي",
            "camera": "كاميرا",
            "headphones": "سماعات رأس",
            "speaker": "مكبر صوت",
            "microphone": "ميكروفون",
            "cable": "كابل",
            "adapter": "محول",
            "charger": "شاحن",
            "battery": "بطارية",
            "power": "طاقة",
            "wireless": "لاسلكي",
            "bluetooth": "بلوتوث",
            "usb": "يو إس بي",
            "hard drive": "قرص صلب",
            "storage": "تخزين",
            "memory": "ذاكرة",
            "processor": "معالج",
            "graphics": "رسوميات",
            "software": "برمجيات",
            "hardware": "أجهزة",
            "network": "شبكة",
            "router": "موجه",
            "switch": "مبدل",
            "server": "خادم",
            "black": "أسود",
            "white": "أبيض",
            "red": "أحمر",
            "blue": "أزرق",
            "green": "أخضر",
            "yellow": "أصفر",
            "orange": "برتقالي",
            "purple": "بنفسجي",
            "pink": "وردي",
            "gray": "رمادي",
            "grey": "رمادي",
            "brown": "بني",
            "small": "صغير",
            "medium": "متوسط",
            "large": "كبير",
            "extra large": "كبير جداً",
            "pro": "برو",
            "plus": "بلس",
            "max": "ماكس",
            "mini": "ميني",
            "air": "آير",
            "lite": "لايت",
            "standard": "قياسي",
            "premium": "مميز",
            "professional": "احترافي",
            "business": "أعمال",
            "home": "منزلي",
            "office": "مكتبي"
        }
        
        english_name = request.english_name.lower()
        words = english_name.split()
        translated_words = []
        
        for word in words:
            # Remove common punctuation
            clean_word = word.strip(".,!?;:")
            if clean_word in translation_map:
                translated_words.append(translation_map[clean_word])
            else:
                # For unknown words, keep them as-is or apply basic rules
                if clean_word.isdigit():
                    translated_words.append(clean_word)
                else:
                    # Keep the original word for brand names and unknown terms
                    translated_words.append(word)
        
        arabic_name = " ".join(translated_words)
        
        # If no translation was found, provide a generic Arabic name
        if arabic_name.lower() == english_name.lower():
            arabic_name = f"منتج {request.english_name}"
        
        arabic_description = None
        if request.description:
            # Simple description translation
            desc_words = request.description.lower().split()
            translated_desc = []
            for word in desc_words:
                clean_word = word.strip(".,!?;:")
                if clean_word in translation_map:
                    translated_desc.append(translation_map[clean_word])
                else:
                    translated_desc.append(word)
            arabic_description = " ".join(translated_desc)
        
        return TranslateResponse(
            arabic_name=arabic_name,
            arabic_description=arabic_description
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}"
        )


# Media Management
@router.post("/{product_id}/media", response_model=MediaUploadResponse)
def upload_product_media(
    product_id: int,
    media_request: MediaUploadRequest,
    db: Session = Depends(get_db)
):
    """رفع وسائط للمنتج"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    try:
        if media_request.media_type == "image":
            if media_request.is_primary:
                product.image_url = media_request.media_url
            else:
                images = product.images or []
                images.append(media_request.media_url)
                product.images = images
                
        elif media_request.media_type == "video":
            videos = product.videos or []
            videos.append(media_request.media_url)
            product.videos = videos
        
        db.commit()
        
        return MediaUploadResponse(
            success=True,
            message="Media uploaded successfully",
            media_url=media_request.media_url
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload media: {str(e)}")


@router.delete("/{product_id}/media")
def remove_product_media(
    product_id: int,
    media_url: str = Query(...),
    media_type: str = Query(..., regex="^(image|video)$"),
    db: Session = Depends(get_db)
):
    """حذف وسائط من المنتج"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    try:
        if media_type == "image":
            if product.image_url == media_url:
                product.image_url = None
            elif product.images and media_url in product.images:
                images = list(product.images)
                images.remove(media_url)
                product.images = images
                
        elif media_type == "video":
            if product.videos and media_url in product.videos:
                videos = list(product.videos)
                videos.remove(media_url)
                product.videos = videos
        
        db.commit()
        return {"message": "Media removed successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove media: {str(e)}")


# Categories Management
@router.get("/categories/", response_model=List[CategorySchema])
def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """الحصول على قائمة الفئات"""
    return db.query(Category).filter(Category.is_active == True).offset(skip).limit(limit).all()


@router.post("/categories/", response_model=CategorySchema, status_code=201)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """إنشاء فئة جديدة"""
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


# Statistics
@router.get("/statistics")
def get_product_statistics(db: Session = Depends(get_db)):
    """إحصائيات المنتجات"""
    total_products = db.query(Product).count()
    active_products = db.query(Product).filter(Product.is_active == True).count()
    inactive_products = total_products - active_products
    
    # Products by category
    categories_stats = db.query(
        Category.name, 
        func.count(Product.id)
    ).join(Product).group_by(Category.name).all()
    
    return {
        "total_products": total_products,
        "active_products": active_products,
        "inactive_products": inactive_products,
        "categories_stats": dict(categories_stats)
    }
