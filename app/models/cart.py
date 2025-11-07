"""
Cart Models
Shopping cart for e-commerce and mobile app
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.db.database import Base


class Cart(Base):
    """
    Shopping cart for customers

    Used for:
    - E-commerce checkout flow
    - Mobile app shopping
    - Persistent cart across sessions
    - Cart abandonment tracking
    """
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)

    # Owner
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True, index=True)

    # Status
    status = Column(
        String(50),
        nullable=False,
        default="active",
        index=True,
        comment="active, abandoned, converted, expired"
    )
    is_active = Column(Boolean, default=True, index=True)

    # Session Tracking
    session_id = Column(String(255), nullable=True, index=True, comment="Browser/app session ID")
    device_type = Column(String(50), nullable=True, comment="mobile, web, tablet")
    device_info = Column(JSONB, nullable=True, comment="Device information")

    # Pricing Summary (Cached for Performance)
    subtotal = Column(Float, default=0.0, nullable=False, comment="Sum of all items")
    discount_amount = Column(Float, default=0.0, nullable=False)
    tax_amount = Column(Float, default=0.0, nullable=False)
    delivery_fee = Column(Float, default=0.0, nullable=False)
    total = Column(Float, default=0.0, nullable=False, comment="Final total")

    # Promotions Applied
    promotion_id = Column(Integer, ForeignKey("promotions.id"), nullable=True)
    promo_code = Column(String(50), nullable=True)

    # Delivery Information
    delivery_address_id = Column(Integer, nullable=True, comment="Selected delivery address")
    delivery_method = Column(String(50), nullable=True, comment="pickup, delivery, express")
    delivery_notes = Column(Text, nullable=True)

    # Conversion
    converted_to_order_id = Column(Integer, nullable=True, comment="ID of created order")
    converted_at = Column(DateTime, nullable=True)

    # Abandonment Tracking
    last_activity_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    abandoned_at = Column(DateTime, nullable=True)
    abandonment_reason = Column(String(255), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True, comment="Cart expiration for cleanup")

    # Relationships
    customer = relationship("Customer", back_populates="carts")
    branch = relationship("Branch")
    promotion = relationship("Promotion")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Cart(id={self.id}, customer_id={self.customer_id}, total={self.total}, items={len(self.items)})>"

    @property
    def item_count(self) -> int:
        """Total number of items in cart"""
        return sum(item.quantity for item in self.items) if self.items else 0

    def calculate_totals(self):
        """Recalculate cart totals from items"""
        if not self.items:
            self.subtotal = 0.0
            self.total = 0.0
            return

        # Calculate subtotal
        self.subtotal = sum(item.subtotal for item in self.items)

        # Apply discount
        discount = 0.0
        if self.promotion and hasattr(self.promotion, 'calculate_discount'):
            discount = self.promotion.calculate_discount(self.subtotal)
        self.discount_amount = discount

        # Calculate tax (example: 5%)
        taxable_amount = self.subtotal - discount
        self.tax_amount = taxable_amount * 0.05

        # Calculate total
        self.total = self.subtotal - self.discount_amount + self.tax_amount + self.delivery_fee

    def add_item(self, product_id: int, quantity: int, price: float, **kwargs):
        """Add item to cart (to be implemented with CartItem)"""
        pass

    def remove_item(self, product_id: int):
        """Remove item from cart"""
        pass

    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity_at = datetime.utcnow()

    def mark_as_abandoned(self, reason: str = None):
        """Mark cart as abandoned"""
        self.status = "abandoned"
        self.abandoned_at = datetime.utcnow()
        self.abandonment_reason = reason

    def convert_to_order(self, order_id: int):
        """Mark cart as converted to order"""
        self.status = "converted"
        self.converted_to_order_id = order_id
        self.converted_at = datetime.utcnow()
        self.is_active = False


class CartItem(Base):
    """
    Individual items in shopping cart

    Each item represents a product with specific quantity and pricing
    """
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)

    # Cart Reference
    cart_id = Column(Integer, ForeignKey("carts.id", ondelete="CASCADE"), nullable=False, index=True)

    # Product Reference
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)

    # Quantity and Pricing
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False, comment="Price per unit at time of adding")
    subtotal = Column(Float, nullable=False, comment="quantity * unit_price")

    # Pricing Details
    original_price = Column(Float, nullable=True, comment="Original price before discounts")
    discount_amount = Column(Float, default=0.0, nullable=False)
    applied_promotion_id = Column(Integer, ForeignKey("promotions.id"), nullable=True)

    # Product Snapshot (for history)
    product_name = Column(String(255), nullable=True, comment="Product name at time of adding")
    product_sku = Column(String(100), nullable=True)
    product_image = Column(String(500), nullable=True)

    # Customization/Notes
    notes = Column(Text, nullable=True, comment="Special instructions")
    customization = Column(JSONB, nullable=True, comment="Product customization options")

    # Availability
    is_available = Column(Boolean, default=True, comment="Whether product is still in stock")
    availability_checked_at = Column(DateTime, nullable=True)

    # Timestamps
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")
    applied_promotion = relationship("Promotion")

    def __repr__(self):
        return f"<CartItem(id={self.id}, product_id={self.product_id}, quantity={self.quantity}, subtotal={self.subtotal})>"

    def calculate_subtotal(self):
        """Calculate item subtotal"""
        self.subtotal = self.quantity * self.unit_price - self.discount_amount

    def update_quantity(self, new_quantity: int):
        """Update item quantity and recalculate subtotal"""
        if new_quantity <= 0:
            raise ValueError("Quantity must be positive")

        self.quantity = new_quantity
        self.calculate_subtotal()
        self.updated_at = datetime.utcnow()

    def apply_discount(self, discount_amount: float, promotion_id: int = None):
        """Apply discount to item"""
        self.discount_amount = discount_amount
        self.applied_promotion_id = promotion_id
        self.calculate_subtotal()

    def snapshot_product(self, product):
        """Take snapshot of product details"""
        self.product_name = product.name
        self.product_sku = product.sku if hasattr(product, 'sku') else None
        self.product_image = product.image_url if hasattr(product, 'image_url') else None

    def check_availability(self, current_stock: int) -> bool:
        """Check if item quantity is available"""
        self.is_available = current_stock >= self.quantity
        self.availability_checked_at = datetime.utcnow()
        return self.is_available
