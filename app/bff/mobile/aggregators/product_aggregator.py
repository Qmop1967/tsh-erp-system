"""
Product Aggregator
Aggregates product data for mobile product screens
"""
import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from app.bff.mobile.schemas import (
    MobileProductDetail,
    MobileProductMinimal,
    MobileSearchResponse,
    MobileCategoryProductsResponse,
    MobileCategory
)
from app.models.product import Product
from app.models.category import Category
from app.models.review import Review

logger = logging.getLogger(__name__)


class ProductAggregator:
    """
    Aggregates product data from multiple sources

    Handles:
    - Product detail with reviews
    - Product search
    - Category browsing
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_product_detail(
        self,
        product_id: int,
        customer_id: Optional[int] = None
    ) -> Optional[MobileProductDetail]:
        """
        Get complete product details

        Args:
            product_id: Product ID
            customer_id: Customer ID (for personalization)

        Returns:
            Complete product detail or None
        """
        try:
            # Get product
            result = await self.db.execute(
                select(Product).where(
                    and_(
                        Product.id == product_id,
                        Product.is_active == True
                    )
                )
            )
            product = result.scalar_one_or_none()

            if not product:
                return None

            # Get rating and review count
            rating_result = await self.db.execute(
                select(
                    func.avg(Review.rating).label('avg_rating'),
                    func.count(Review.id).label('review_count')
                ).where(
                    and_(
                        Review.product_id == product_id,
                        Review.is_approved == True
                    )
                )
            )
            rating_data = rating_result.one()

            return self._transform_product_detail(
                product,
                avg_rating=rating_data.avg_rating,
                review_count=rating_data.review_count
            )

        except Exception as e:
            logger.error(f"Error fetching product detail {product_id}: {e}")
            return None

    async def search_products(
        self,
        query: str,
        page: int = 1,
        page_size: int = 20,
        branch_id: Optional[int] = None,
        category_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> MobileSearchResponse:
        """
        Search products with filters

        Args:
            query: Search query
            page: Page number (1-indexed)
            page_size: Results per page
            branch_id: Filter by branch
            category_id: Filter by category
            min_price: Minimum price
            max_price: Maximum price

        Returns:
            Search results with pagination
        """
        try:
            # Build base query
            base_query = select(Product).where(
                and_(
                    Product.is_active == True,
                    Product.stock_quantity > 0,
                    or_(
                        Product.name.ilike(f"%{query}%"),
                        Product.description.ilike(f"%{query}%"),
                        Product.sku.ilike(f"%{query}%")
                    )
                )
            )

            # Apply filters
            if branch_id:
                base_query = base_query.where(Product.branch_id == branch_id)
            if category_id:
                base_query = base_query.where(Product.category_id == category_id)
            if min_price:
                base_query = base_query.where(Product.price >= min_price)
            if max_price:
                base_query = base_query.where(Product.price <= max_price)

            # Get total count
            count_query = select(func.count()).select_from(base_query.subquery())
            count_result = await self.db.execute(count_query)
            total_count = count_result.scalar()

            # Get paginated results
            offset = (page - 1) * page_size
            results_query = base_query.order_by(Product.name.asc()).limit(page_size).offset(offset)
            results = await self.db.execute(results_query)
            products = results.scalars().all()

            return MobileSearchResponse(
                query=query,
                results=[self._transform_product_minimal(p) for p in products],
                total_count=total_count,
                page=page,
                page_size=page_size,
                has_more=(offset + len(products)) < total_count
            )

        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return MobileSearchResponse(
                query=query,
                results=[],
                total_count=0,
                page=page,
                page_size=page_size,
                has_more=False
            )

    async def get_category_products(
        self,
        category_id: int,
        page: int = 1,
        page_size: int = 20,
        branch_id: Optional[int] = None
    ) -> Optional[MobileCategoryProductsResponse]:
        """
        Get category with its products

        Args:
            category_id: Category ID
            page: Page number
            page_size: Results per page
            branch_id: Filter by branch

        Returns:
            Category with products
        """
        try:
            # Get category
            category_result = await self.db.execute(
                select(Category).where(Category.id == category_id)
            )
            category = category_result.scalar_one_or_none()

            if not category:
                return None

            # Get products in category
            products_query = select(Product).where(
                and_(
                    Product.category_id == category_id,
                    Product.is_active == True,
                    Product.stock_quantity > 0
                )
            )

            if branch_id:
                products_query = products_query.where(Product.branch_id == branch_id)

            # Get total count
            count_query = select(func.count()).select_from(products_query.subquery())
            count_result = await self.db.execute(count_query)
            total_count = count_result.scalar()

            # Get paginated products
            offset = (page - 1) * page_size
            products_query = products_query.order_by(Product.name.asc()).limit(page_size).offset(offset)
            products_result = await self.db.execute(products_query)
            products = products_result.scalars().all()

            # Get product count for category
            product_count_result = await self.db.execute(
                select(func.count(Product.id)).where(
                    and_(
                        Product.category_id == category_id,
                        Product.is_active == True
                    )
                )
            )
            product_count = product_count_result.scalar()

            return MobileCategoryProductsResponse(
                category=MobileCategory(
                    id=category.id,
                    name=category.name,
                    icon=category.icon if hasattr(category, 'icon') else None,
                    product_count=product_count
                ),
                products=[self._transform_product_minimal(p) for p in products],
                total_count=total_count,
                page=page,
                has_more=(offset + len(products)) < total_count
            )

        except Exception as e:
            logger.error(f"Error fetching category products {category_id}: {e}")
            return None

    async def get_related_products(
        self,
        product_id: int,
        limit: int = 10
    ) -> List[MobileProductMinimal]:
        """
        Get related products (same category)

        Args:
            product_id: Product ID
            limit: Maximum results

        Returns:
            List of related products
        """
        try:
            # Get product category
            product_result = await self.db.execute(
                select(Product).where(Product.id == product_id)
            )
            product = product_result.scalar_one_or_none()

            if not product or not product.category_id:
                return []

            # Get related products
            related_query = select(Product).where(
                and_(
                    Product.category_id == product.category_id,
                    Product.id != product_id,
                    Product.is_active == True,
                    Product.stock_quantity > 0
                )
            ).order_by(Product.sales_count.desc()).limit(limit)

            result = await self.db.execute(related_query)
            products = result.scalars().all()

            return [self._transform_product_minimal(p) for p in products]

        except Exception as e:
            logger.error(f"Error fetching related products for {product_id}: {e}")
            return []

    def _transform_product_minimal(self, product: Product) -> MobileProductMinimal:
        """Transform Product to MobileProductMinimal"""
        discount = None
        if hasattr(product, 'original_price') and product.original_price and product.original_price > product.price:
            discount = round(((product.original_price - product.price) / product.original_price) * 100, 1)

        image = None
        if hasattr(product, 'images') and product.images:
            if isinstance(product.images, list) and len(product.images) > 0:
                image = product.images[0]
            elif isinstance(product.images, str):
                image = product.images

        return MobileProductMinimal(
            id=product.id,
            name=product.name,
            price=float(product.price),
            image=image,
            in_stock=product.stock_quantity > 0,
            discount=discount
        )

    def _transform_product_detail(
        self,
        product: Product,
        avg_rating: Optional[float] = None,
        review_count: int = 0
    ) -> MobileProductDetail:
        """Transform Product to MobileProductDetail"""
        # Calculate discount
        discount = None
        original_price = None
        if hasattr(product, 'original_price') and product.original_price and product.original_price > product.price:
            original_price = float(product.original_price)
            discount = round(((product.original_price - product.price) / product.original_price) * 100, 1)

        # Get images
        images = []
        if hasattr(product, 'images') and product.images:
            if isinstance(product.images, list):
                images = product.images
            elif isinstance(product.images, str):
                images = [product.images]

        # Get specifications
        specifications = {}
        if hasattr(product, 'specifications') and product.specifications:
            specifications = product.specifications

        # Get branch name
        branch_name = None
        if hasattr(product, 'branch') and product.branch:
            branch_name = product.branch.name

        return MobileProductDetail(
            id=product.id,
            name=product.name,
            description=product.description or "",
            price=float(product.price),
            original_price=original_price,
            discount=discount,
            images=images,
            in_stock=product.stock_quantity > 0,
            stock_quantity=product.stock_quantity,
            branch_name=branch_name,
            rating=float(avg_rating) if avg_rating else None,
            review_count=review_count,
            specifications=specifications
        )
