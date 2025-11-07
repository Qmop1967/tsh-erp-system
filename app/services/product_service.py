"""
Product Service - Business Logic for Product Management

Refactored to use Phase 4 patterns:
- Instance methods instead of static methods
- BaseRepository for CRUD operations
- Custom exceptions instead of HTTPException
- Pagination and search support

Author: Claude Code (Senior Software Engineer AI)
Date: January 7, 2025
Phase: 5 P1 - Products Router Migration
"""

from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func
from fastapi import Depends
from decimal import Decimal

from app.models.product import Product, Category
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductSummary,
    CategoryCreate, CategoryUpdate,
    TranslateNameRequest, TranslateNameResponse,
    MediaUploadRequest, MediaUploadResponse
)
from app.repositories import BaseRepository
from app.exceptions import (
    EntityNotFoundError,
    DuplicateEntityError,
    ValidationError
)


class ProductService:
    """
    Service for product management.

    Handles all business logic for products, replacing direct
    database operations in the router.
    """

    def __init__(self, db: Session):
        """
        Initialize product service.

        Args:
            db: Database session
        """
        self.db = db
        self.product_repo = BaseRepository(Product, db)
        self.category_repo = BaseRepository(Category, db)

    # ========================================================================
    # Product CRUD Operations
    # ========================================================================

    def get_all_products(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Product], int]:
        """
        Get all products with optional filters.

        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            category_id: Filter by category ID
            is_active: Filter by active status
            search: Search term for name, name_ar, SKU, description

        Returns:
            Tuple of (products list, total count)
        """
        # Build filters
        filters = {}
        if category_id is not None:
            filters['category_id'] = category_id
        if is_active is not None:
            filters['is_active'] = is_active

        # Apply search if provided
        if search:
            # Use custom query for multi-field search with joins
            query = self.db.query(Product).options(joinedload(Product.category))

            # Apply filters
            if filters:
                for field, value in filters.items():
                    query = query.filter(getattr(Product, field) == value)

            # Apply search across multiple fields
            search_filter = or_(
                Product.name.ilike(f"%{search}%"),
                Product.name_ar.ilike(f"%{search}%"),
                Product.sku.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%"),
                Product.description_ar.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

            # Get results
            products = query.offset(skip).limit(limit).all()
            total = query.count()
        else:
            # Use BaseRepository for simple queries
            products = self.db.query(Product).options(
                joinedload(Product.category)
            ).filter_by(**filters).offset(skip).limit(limit).all()

            total = self.product_repo.get_count(filters=filters)

        return products, total

    def get_products_summary(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> Tuple[List[ProductSummary], int]:
        """
        Get product summaries for list views.

        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            category_id: Filter by category ID
            is_active: Filter by active status
            search: Search term

        Returns:
            Tuple of (product summaries list, total count)
        """
        products, total = self.get_all_products(
            skip=skip,
            limit=limit,
            category_id=category_id,
            is_active=is_active,
            search=search
        )

        # Convert to ProductSummary
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

        return result, total

    def get_product_by_id(self, product_id: int) -> Product:
        """
        Get product by ID with category joined.

        Args:
            product_id: Product ID

        Returns:
            Product instance

        Raises:
            EntityNotFoundError: If product not found
        """
        product = self.db.query(Product).options(
            joinedload(Product.category)
        ).filter(Product.id == product_id).first()

        if not product:
            raise EntityNotFoundError("Product", product_id)

        return product

    def create_product(self, product_data: ProductCreate) -> Product:
        """
        Create new product.

        Args:
            product_data: Product creation data

        Returns:
            Created product

        Raises:
            EntityNotFoundError: If category not found
            DuplicateEntityError: If SKU or barcode already exists
        """
        # Validate category exists
        category = self.category_repo.get(product_data.category_id)
        if not category:
            raise EntityNotFoundError("Category", product_data.category_id)

        # Validate unique SKU
        if self.product_repo.exists({'sku': product_data.sku}):
            raise DuplicateEntityError("Product", "SKU", product_data.sku)

        # Validate unique barcode if provided
        if product_data.barcode:
            if self.product_repo.exists({'barcode': product_data.barcode}):
                raise DuplicateEntityError("Product", "barcode", product_data.barcode)

        # Create product
        product = self.product_repo.create(product_data.dict())

        # Load with category relation
        return self.get_product_by_id(product.id)

    def update_product(
        self,
        product_id: int,
        product_data: ProductUpdate
    ) -> Product:
        """
        Update existing product.

        Args:
            product_id: Product ID
            product_data: Product update data

        Returns:
            Updated product

        Raises:
            EntityNotFoundError: If product not found
            DuplicateEntityError: If new SKU or barcode conflicts
        """
        # Verify product exists
        existing_product = self.get_product_by_id(product_id)

        update_dict = product_data.dict(exclude_unset=True)

        # Validate unique SKU if being updated
        if 'sku' in update_dict and update_dict['sku'] != existing_product.sku:
            if self.product_repo.exists({'sku': update_dict['sku']}):
                raise DuplicateEntityError("Product", "SKU", update_dict['sku'])

        # Validate unique barcode if being updated
        if 'barcode' in update_dict and update_dict['barcode']:
            if update_dict['barcode'] != existing_product.barcode:
                if self.product_repo.exists({'barcode': update_dict['barcode']}):
                    raise DuplicateEntityError("Product", "barcode", update_dict['barcode'])

        # Validate category if being updated
        if 'category_id' in update_dict:
            category = self.category_repo.get(update_dict['category_id'])
            if not category:
                raise EntityNotFoundError("Category", update_dict['category_id'])

        # Update product
        updated_product = self.product_repo.update(product_id, update_dict)

        # Load with category relation
        return self.get_product_by_id(product_id)

    def delete_product(self, product_id: int) -> bool:
        """
        Soft delete product (set is_active=False).

        Args:
            product_id: Product ID

        Returns:
            True if deactivated

        Raises:
            EntityNotFoundError: If product not found
        """
        # Use soft delete
        self.product_repo.soft_delete(product_id)
        return True

    # ========================================================================
    # Category Operations
    # ========================================================================

    def get_categories(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> Tuple[List[Category], int]:
        """
        Get all categories with optional filters.

        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            active_only: Filter by active status

        Returns:
            Tuple of (categories list, total count)
        """
        filters = {}
        if active_only:
            filters['is_active'] = True

        categories = self.category_repo.get_all(
            skip=skip,
            limit=limit,
            filters=filters
        )
        total = self.category_repo.get_count(filters=filters)

        return categories, total

    def create_category(self, category_data: CategoryCreate) -> Category:
        """
        Create new category.

        Args:
            category_data: Category creation data

        Returns:
            Created category

        Raises:
            DuplicateEntityError: If category name already exists
            EntityNotFoundError: If parent category not found
        """
        # Validate unique name
        if self.category_repo.exists({'name': category_data.name}):
            raise DuplicateEntityError("Category", "name", category_data.name)

        # Validate parent exists if provided
        if category_data.parent_id:
            parent = self.category_repo.get(category_data.parent_id)
            if not parent:
                raise EntityNotFoundError("Parent Category", category_data.parent_id)

        # Create category
        return self.category_repo.create(category_data.dict())

    def update_category(
        self,
        category_id: int,
        category_data: CategoryUpdate
    ) -> Category:
        """
        Update existing category.

        Args:
            category_id: Category ID
            category_data: Category update data

        Returns:
            Updated category

        Raises:
            EntityNotFoundError: If category not found
            DuplicateEntityError: If new name conflicts
        """
        update_dict = category_data.dict(exclude_unset=True)

        # Validate unique name if being updated
        if 'name' in update_dict:
            # Check if another category has this name
            existing = self.db.query(Category).filter(
                Category.name == update_dict['name'],
                Category.id != category_id
            ).first()
            if existing:
                raise DuplicateEntityError("Category", "name", update_dict['name'])

        # Update category
        return self.category_repo.update(category_id, update_dict)

    # ========================================================================
    # AI Translation
    # ========================================================================

    async def translate_product_name(
        self,
        request: TranslateNameRequest
    ) -> TranslateNameResponse:
        """
        Translate English product name to Arabic using AI.

        Args:
            request: Translation request

        Returns:
            Translation response with Arabic name and description
        """
        try:
            # Simple translation mapping (can be enhanced with OpenAI/Google Translate)
            translation_map = {
                "laptop": "لابتوب", "computer": "كمبيوتر", "phone": "هاتف",
                "mobile": "جوال", "iphone": "آيفون", "samsung": "سامسونج",
                "dell": "ديل", "hp": "إتش بي", "apple": "أبل",
                "mouse": "فأرة", "keyboard": "لوحة مفاتيح", "monitor": "شاشة",
                "speaker": "سماعة", "headphone": "سماعة رأس", "tablet": "تابلت",
                "watch": "ساعة", "camera": "كاميرا", "printer": "طابعة",
                "scanner": "ماسح ضوئي", "router": "راوتر", "cable": "كابل",
                "charger": "شاحن", "battery": "بطارية", "memory": "ذاكرة",
                "storage": "تخزين", "hard drive": "قرص صلب", "ssd": "إس إس دي",
                "usb": "يو إس بي", "bluetooth": "بلوتوث", "wireless": "لاسلكي",
                "pro": "برو", "plus": "بلس", "max": "ماكس", "mini": "ميني",
                "air": "إير", "studio": "ستوديو", "premium": "بريميوم",
                "standard": "قياسي", "basic": "أساسي", "professional": "احترافي",
                "gaming": "ألعاب", "black": "أسود", "white": "أبيض",
                "red": "أحمر", "blue": "أزرق", "green": "أخضر",
                "yellow": "أصفر", "orange": "برتقالي", "purple": "بنفسجي",
                "gray": "رمادي", "brown": "بني", "small": "صغير",
                "medium": "متوسط", "large": "كبير", "extra large": "كبير جداً"
            }

            english_name = request.english_name.lower()
            words = english_name.split()
            arabic_words = []

            for word in words:
                clean_word = ''.join(char for char in word if char.isalnum())
                if clean_word in translation_map:
                    arabic_words.append(translation_map[clean_word])
                else:
                    arabic_words.append(word)

            arabic_name = " ".join(arabic_words)

            # If no translation was made, keep original
            if arabic_name.lower() == english_name.lower():
                arabic_name = request.english_name

            # Translate description if provided
            arabic_description = None
            if request.description:
                desc_lower = request.description.lower()
                desc_words = desc_lower.split()
                translated_desc = []
                for word in desc_words:
                    clean_word = ''.join(char for char in word if char.isalnum())
                    if clean_word in translation_map:
                        translated_desc.append(translation_map[clean_word])
                    else:
                        translated_desc.append(word)
                arabic_description = " ".join(translated_desc)

            return TranslateNameResponse(
                arabic_name=arabic_name,
                arabic_description=arabic_description
            )

        except Exception:
            # Fallback: return original if translation fails
            return TranslateNameResponse(
                arabic_name=request.english_name,
                arabic_description=request.description
            )

    # ========================================================================
    # Media Management
    # ========================================================================

    def upload_media(self, media_request: MediaUploadRequest) -> MediaUploadResponse:
        """
        Upload media for product.

        Args:
            media_request: Media upload request

        Returns:
            Media upload response

        Raises:
            EntityNotFoundError: If product not found
            ValidationError: If media upload fails
        """
        # Verify product exists
        product = self.product_repo.get(media_request.product_id)
        if not product:
            raise EntityNotFoundError("Product", media_request.product_id)

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

            self.db.commit()
            self.db.refresh(product)

            return MediaUploadResponse(
                success=True,
                message="Media uploaded successfully",
                media_url=media_request.media_url
            )

        except Exception as e:
            raise ValidationError(
                f"Failed to upload media: {str(e)}",
                f"فشل تحميل الوسائط: {str(e)}"
            )

    def remove_media(
        self,
        product_id: int,
        media_url: str,
        media_type: str
    ) -> bool:
        """
        Remove media from product.

        Args:
            product_id: Product ID
            media_url: URL of media to remove
            media_type: Type of media (image or video)

        Returns:
            True if removed successfully

        Raises:
            EntityNotFoundError: If product not found
            ValidationError: If media removal fails
        """
        # Verify product exists
        product = self.product_repo.get(product_id)
        if not product:
            raise EntityNotFoundError("Product", product_id)

        try:
            if media_type == "image":
                if product.image_url == media_url:
                    product.image_url = None
                elif product.images and media_url in product.images:
                    product.images.remove(media_url)

            elif media_type == "video":
                if product.videos and media_url in product.videos:
                    product.videos.remove(media_url)

            self.db.commit()
            return True

        except Exception as e:
            raise ValidationError(
                f"Failed to remove media: {str(e)}",
                f"فشل حذف الوسائط: {str(e)}"
            )

    # ========================================================================
    # Statistics
    # ========================================================================

    def get_product_statistics(self) -> Dict[str, Any]:
        """
        Get product statistics.

        Returns:
            Dictionary with statistics
        """
        total_products = self.product_repo.get_count()
        active_products = self.product_repo.get_count({'is_active': True})
        inactive_products = total_products - active_products

        # Products by category
        categories_stats = self.db.query(
            Category.name,
            func.count(Product.id)
        ).join(Product).group_by(Category.name).all()

        return {
            "total_products": total_products,
            "active_products": active_products,
            "inactive_products": inactive_products,
            "categories_stats": dict(categories_stats)
        }


# ============================================================================
# Dependency for FastAPI
# ============================================================================

from app.db.database import get_db


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    """
    Dependency to get ProductService instance.

    Usage in routers:
        @router.get("/products")
        def get_products(
            service: ProductService = Depends(get_product_service)
        ):
            products, total = service.get_all_products()
            return products
    """
    return ProductService(db)
