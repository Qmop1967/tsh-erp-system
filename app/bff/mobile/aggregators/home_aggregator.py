"""
Home Screen Aggregator
Aggregates data for mobile home screen in ONE call
"""
import asyncio
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.bff.mobile.schemas import (
    MobileHomeResponse,
    MobileProductMinimal,
    MobilePromotion,
    MobileCustomerInfo,
    MobileCartSummary
)
from app.models.product import Product
from app.models.promotion import Promotion
from app.models.customer import Customer
from app.models.cart import Cart, CartItem

logger = logging.getLogger(__name__)


class HomeAggregator:
    """
    Aggregates home screen data from multiple modules

    Fetches:
    - Featured products
    - Best sellers
    - New arrivals
    - Active promotions
    - Customer info
    - Cart summary
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_home_data(
        self,
        customer_id: Optional[int] = None,
        branch_id: Optional[int] = None
    ) -> MobileHomeResponse:
        """
        Get complete home screen data in ONE call

        Args:
            customer_id: Customer ID (optional, for personalization)
            branch_id: Branch ID (optional, for location-based filtering)

        Returns:
            Complete home screen data
        """
        try:
            # Fetch all data in parallel for performance
            featured, best_sellers, new_arrivals, promotions, customer, cart = \
                await asyncio.gather(
                    self._get_featured_products(branch_id),
                    self._get_best_sellers(branch_id),
                    self._get_new_arrivals(branch_id),
                    self._get_active_promotions(branch_id),
                    self._get_customer_info(customer_id) if customer_id else self._get_none(),
                    self._get_cart_summary(customer_id) if customer_id else self._get_empty_cart(),
                    return_exceptions=True
                )

            # Handle exceptions
            if isinstance(featured, Exception):
                logger.error(f"Error fetching featured products: {featured}")
                featured = []
            if isinstance(best_sellers, Exception):
                logger.error(f"Error fetching best sellers: {best_sellers}")
                best_sellers = []
            if isinstance(new_arrivals, Exception):
                logger.error(f"Error fetching new arrivals: {new_arrivals}")
                new_arrivals = []
            if isinstance(promotions, Exception):
                logger.error(f"Error fetching promotions: {promotions}")
                promotions = []
            if isinstance(customer, Exception):
                logger.error(f"Error fetching customer: {customer}")
                customer = None
            if isinstance(cart, Exception):
                logger.error(f"Error fetching cart: {cart}")
                cart = MobileCartSummary()

            return MobileHomeResponse(
                featured_products=featured,
                best_sellers=best_sellers,
                new_arrivals=new_arrivals,
                promotions=promotions,
                customer=customer,
                cart=cart
            )

        except Exception as e:
            logger.error(f"Error aggregating home data: {e}")
            # Return empty response rather than failing
            return MobileHomeResponse()

    async def _get_featured_products(self, branch_id: Optional[int] = None) -> list[MobileProductMinimal]:
        """Get featured products (limit: 10)"""
        query = select(Product).where(
            and_(
                Product.is_active == True,
                Product.is_featured == True,
                Product.stock_quantity > 0
            )
        )

        if branch_id:
            query = query.where(Product.branch_id == branch_id)

        query = query.order_by(Product.featured_order.asc()).limit(10)

        result = await self.db.execute(query)
        products = result.scalars().all()

        return [self._transform_product(p) for p in products]

    async def _get_best_sellers(self, branch_id: Optional[int] = None) -> list[MobileProductMinimal]:
        """Get best selling products (limit: 10)"""
        query = select(Product).where(
            and_(
                Product.is_active == True,
                Product.stock_quantity > 0
            )
        )

        if branch_id:
            query = query.where(Product.branch_id == branch_id)

        # Order by sales count (if you have this field) or popularity
        query = query.order_by(Product.sales_count.desc()).limit(10)

        result = await self.db.execute(query)
        products = result.scalars().all()

        return [self._transform_product(p) for p in products]

    async def _get_new_arrivals(self, branch_id: Optional[int] = None) -> list[MobileProductMinimal]:
        """Get newly added products (limit: 10)"""
        query = select(Product).where(
            and_(
                Product.is_active == True,
                Product.stock_quantity > 0
            )
        )

        if branch_id:
            query = query.where(Product.branch_id == branch_id)

        query = query.order_by(Product.created_at.desc()).limit(10)

        result = await self.db.execute(query)
        products = result.scalars().all()

        return [self._transform_product(p) for p in products]

    async def _get_active_promotions(self, branch_id: Optional[int] = None) -> list[MobilePromotion]:
        """Get active promotions"""
        from datetime import datetime

        query = select(Promotion).where(
            and_(
                Promotion.is_active == True,
                Promotion.start_date <= datetime.utcnow(),
                Promotion.end_date >= datetime.utcnow()
            )
        )

        if branch_id:
            query = query.where(Promotion.branch_id == branch_id)

        query = query.order_by(Promotion.priority.desc()).limit(5)

        result = await self.db.execute(query)
        promotions = result.scalars().all()

        return [self._transform_promotion(p) for p in promotions]

    async def _get_customer_info(self, customer_id: int) -> Optional[MobileCustomerInfo]:
        """Get customer info"""
        result = await self.db.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        customer = result.scalar_one_or_none()

        if not customer:
            return None

        return MobileCustomerInfo(
            id=customer.id,
            name=customer.name,
            avatar=customer.avatar_url if hasattr(customer, 'avatar_url') else None,
            phone=customer.phone if hasattr(customer, 'phone') else None
        )

    async def _get_cart_summary(self, customer_id: int) -> MobileCartSummary:
        """Get cart summary"""
        # Get cart for customer
        result = await self.db.execute(
            select(Cart).where(
                and_(
                    Cart.customer_id == customer_id,
                    Cart.is_active == True
                )
            )
        )
        cart = result.scalar_one_or_none()

        if not cart:
            return MobileCartSummary()

        # Get cart items count and total
        items_result = await self.db.execute(
            select(
                func.count(CartItem.id).label('count'),
                func.sum(CartItem.quantity * CartItem.price).label('total')
            ).where(CartItem.cart_id == cart.id)
        )
        items_data = items_result.one()

        return MobileCartSummary(
            items_count=items_data.count or 0,
            total=float(items_data.total or 0),
            currency="IQD"
        )

    async def _get_none(self):
        """Return None (for optional fields)"""
        return None

    async def _get_empty_cart(self):
        """Return empty cart summary"""
        return MobileCartSummary()

    def _transform_product(self, product: Product) -> MobileProductMinimal:
        """Transform Product model to mobile-optimized schema"""
        # Calculate discount if applicable
        discount = None
        if hasattr(product, 'original_price') and product.original_price and product.original_price > product.price:
            discount = round(((product.original_price - product.price) / product.original_price) * 100, 1)

        # Get first image
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

    def _transform_promotion(self, promotion: Promotion) -> MobilePromotion:
        """Transform Promotion model to mobile-optimized schema"""
        return MobilePromotion(
            id=promotion.id,
            title=promotion.title,
            description=promotion.description,
            banner_url=promotion.banner_url if hasattr(promotion, 'banner_url') else None,
            discount_percentage=promotion.discount_percentage if hasattr(promotion, 'discount_percentage') else None,
            valid_until=promotion.end_date.isoformat() if hasattr(promotion, 'end_date') else None
        )
