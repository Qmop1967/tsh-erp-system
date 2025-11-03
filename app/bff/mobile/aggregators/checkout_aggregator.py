"""
Checkout Aggregator
Aggregates checkout data for mobile checkout flow
"""
import asyncio
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.bff.mobile.schemas import (
    MobileCheckoutResponse,
    MobileCart,
    MobileCartItem,
    MobileAddress,
    MobilePaymentMethod,
    MobileDeliveryOption,
    MobilePromotion
)
from app.models.cart import Cart, CartItem
from app.models.customer import Customer
from app.models.customer_address import CustomerAddress
from app.models.product import Product
from app.models.promotion import Promotion

logger = logging.getLogger(__name__)


class CheckoutAggregator:
    """
    Aggregates checkout data from multiple sources

    Fetches:
    - Cart with items
    - Customer addresses
    - Payment methods
    - Delivery options
    - Active promotions
    - Price calculations
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_checkout_data(
        self,
        customer_id: int,
        branch_id: Optional[int] = None
    ) -> Optional[MobileCheckoutResponse]:
        """
        Get complete checkout data in ONE call

        Args:
            customer_id: Customer ID
            branch_id: Branch ID (optional)

        Returns:
            Complete checkout data or None
        """
        try:
            # Fetch all data in parallel
            cart, addresses, payment_methods, delivery_options, promotions = \
                await asyncio.gather(
                    self._get_cart(customer_id),
                    self._get_addresses(customer_id),
                    self._get_payment_methods(customer_id),
                    self._get_delivery_options(branch_id),
                    self._get_active_promotions(branch_id),
                    return_exceptions=True
                )

            # Handle exceptions
            if isinstance(cart, Exception):
                logger.error(f"Error fetching cart: {cart}")
                return None  # Cart is required
            if isinstance(addresses, Exception):
                logger.error(f"Error fetching addresses: {addresses}")
                addresses = []
            if isinstance(payment_methods, Exception):
                logger.error(f"Error fetching payment methods: {payment_methods}")
                payment_methods = []
            if isinstance(delivery_options, Exception):
                logger.error(f"Error fetching delivery options: {delivery_options}")
                delivery_options = []
            if isinstance(promotions, Exception):
                logger.error(f"Error fetching promotions: {promotions}")
                promotions = []

            # Calculate summary
            summary = self._calculate_summary(cart, promotions)

            return MobileCheckoutResponse(
                cart=cart,
                addresses=addresses,
                payment_methods=payment_methods,
                delivery_options=delivery_options,
                promotions=promotions,
                summary=summary
            )

        except Exception as e:
            logger.error(f"Error aggregating checkout data: {e}")
            return None

    async def _get_cart(self, customer_id: int) -> Optional[MobileCart]:
        """Get cart with items"""
        # Get active cart
        cart_result = await self.db.execute(
            select(Cart).where(
                and_(
                    Cart.customer_id == customer_id,
                    Cart.is_active == True
                )
            )
        )
        cart = cart_result.scalar_one_or_none()

        if not cart:
            # Return empty cart
            return MobileCart(
                items=[],
                subtotal=0.0,
                discount=0.0,
                delivery_fee=0.0,
                total=0.0,
                currency="IQD"
            )

        # Get cart items with product details
        items_result = await self.db.execute(
            select(CartItem, Product).join(
                Product, CartItem.product_id == Product.id
            ).where(CartItem.cart_id == cart.id)
        )
        items_data = items_result.all()

        # Transform to mobile format
        mobile_items = []
        subtotal = 0.0

        for cart_item, product in items_data:
            # Get product image
            image = None
            if hasattr(product, 'images') and product.images:
                if isinstance(product.images, list) and len(product.images) > 0:
                    image = product.images[0]
                elif isinstance(product.images, str):
                    image = product.images

            item_subtotal = float(cart_item.quantity * cart_item.price)
            subtotal += item_subtotal

            mobile_items.append(MobileCartItem(
                id=cart_item.id,
                product_id=product.id,
                product_name=product.name,
                product_image=image,
                quantity=cart_item.quantity,
                price=float(cart_item.price),
                subtotal=item_subtotal
            ))

        return MobileCart(
            items=mobile_items,
            subtotal=subtotal,
            discount=0.0,  # Will be calculated in summary
            delivery_fee=0.0,  # Will be calculated based on selected option
            total=subtotal,  # Will be calculated in summary
            currency="IQD"
        )

    async def _get_addresses(self, customer_id: int) -> list[MobileAddress]:
        """Get customer addresses"""
        result = await self.db.execute(
            select(CustomerAddress).where(
                and_(
                    CustomerAddress.customer_id == customer_id,
                    CustomerAddress.is_active == True
                )
            ).order_by(CustomerAddress.is_default.desc())
        )
        addresses = result.scalars().all()

        return [
            MobileAddress(
                id=addr.id,
                label=addr.label or "Address",
                address=addr.address,
                is_default=addr.is_default
            )
            for addr in addresses
        ]

    async def _get_payment_methods(self, customer_id: int) -> list[MobilePaymentMethod]:
        """Get available payment methods"""
        # For now, return static payment methods
        # In production, fetch from database or payment gateway
        return [
            MobilePaymentMethod(
                id="cash",
                name="Cash on Delivery",
                icon="cash",
                is_default=True
            ),
            MobilePaymentMethod(
                id="card",
                name="Credit/Debit Card",
                icon="card",
                is_default=False
            ),
            MobilePaymentMethod(
                id="zain_cash",
                name="Zain Cash",
                icon="zaincash",
                is_default=False
            ),
            MobilePaymentMethod(
                id="fastpay",
                name="FastPay",
                icon="fastpay",
                is_default=False
            )
        ]

    async def _get_delivery_options(self, branch_id: Optional[int] = None) -> list[MobileDeliveryOption]:
        """Get available delivery options"""
        # For now, return static delivery options
        # In production, calculate based on location, weight, etc.
        return [
            MobileDeliveryOption(
                id="standard",
                name="Standard Delivery",
                fee=5000.0,
                estimated_days=3,
                is_default=True
            ),
            MobileDeliveryOption(
                id="express",
                name="Express Delivery",
                fee=10000.0,
                estimated_days=1,
                is_default=False
            ),
            MobileDeliveryOption(
                id="pickup",
                name="Store Pickup",
                fee=0.0,
                estimated_days=0,
                is_default=False
            )
        ]

    async def _get_active_promotions(self, branch_id: Optional[int] = None) -> list[MobilePromotion]:
        """Get active promotions applicable to checkout"""
        from datetime import datetime

        query = select(Promotion).where(
            and_(
                Promotion.is_active == True,
                Promotion.start_date <= datetime.utcnow(),
                Promotion.end_date >= datetime.utcnow(),
                Promotion.applies_to_checkout == True
            )
        )

        if branch_id:
            query = query.where(Promotion.branch_id == branch_id)

        query = query.order_by(Promotion.priority.desc()).limit(5)

        result = await self.db.execute(query)
        promotions = result.scalars().all()

        return [
            MobilePromotion(
                id=promo.id,
                title=promo.title,
                description=promo.description,
                banner_url=promo.banner_url if hasattr(promo, 'banner_url') else None,
                discount_percentage=promo.discount_percentage if hasattr(promo, 'discount_percentage') else None,
                valid_until=promo.end_date.isoformat() if hasattr(promo, 'end_date') else None
            )
            for promo in promotions
        ]

    def _calculate_summary(self, cart: MobileCart, promotions: list[MobilePromotion]) -> dict:
        """
        Calculate checkout summary

        Args:
            cart: Mobile cart
            promotions: Active promotions

        Returns:
            Summary dict with subtotal, discount, delivery_fee, total
        """
        subtotal = cart.subtotal
        discount = 0.0

        # Apply best promotion discount
        if promotions:
            best_discount = max(
                (p.discount_percentage or 0) for p in promotions
            )
            if best_discount > 0:
                discount = subtotal * (best_discount / 100)

        # Default delivery fee (standard)
        delivery_fee = 5000.0

        # Calculate total
        total = subtotal - discount + delivery_fee

        return {
            "subtotal": round(subtotal, 2),
            "discount": round(discount, 2),
            "delivery_fee": round(delivery_fee, 2),
            "total": round(total, 2),
            "currency": "IQD"
        }
