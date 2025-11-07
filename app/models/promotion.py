"""
Promotion Model
Promotional campaigns and discount offers
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.db.database import Base


class Promotion(Base):
    """
    Promotional campaigns and special offers

    Used for:
    - Homepage banners and featured promotions
    - Seasonal sales and discounts
    - Product-specific promotions
    - Category-wide promotions
    """
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True)

    # Basic Information
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    banner_url = Column(String(500), nullable=True, comment="URL to promotional banner image")

    # Discount Details
    discount_type = Column(
        String(50),
        nullable=False,
        default="percentage",
        comment="percentage, fixed_amount, buy_x_get_y"
    )
    discount_value = Column(Float, nullable=True, comment="Percentage (0-100) or fixed amount")

    # Validity Period
    start_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_date = Column(DateTime, nullable=True)

    # Status
    is_active = Column(Boolean, default=True, index=True)
    priority = Column(Integer, default=0, comment="Higher priority shows first")

    # Application Rules
    applies_to_checkout = Column(Boolean, default=False, comment="Show in checkout flow")
    applies_to_home = Column(Boolean, default=True, comment="Show on home screen")
    min_purchase_amount = Column(Float, nullable=True, comment="Minimum purchase required")
    max_uses = Column(Integer, nullable=True, comment="Maximum number of uses")
    current_uses = Column(Integer, default=0, comment="Current usage count")

    # Scope
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True, index=True)

    # Applicable Products/Categories
    product_ids = Column(JSONB, nullable=True, comment="List of applicable product IDs")
    category_ids = Column(JSONB, nullable=True, comment="List of applicable category IDs")

    # Promo Code
    promo_code = Column(String(50), nullable=True, unique=True, index=True)
    requires_code = Column(Boolean, default=False, comment="Whether promo code is required")

    # Additional Settings
    settings = Column(JSONB, nullable=True, comment="Additional promotion settings")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    branch = relationship("Branch", back_populates="promotions")

    def __repr__(self):
        return f"<Promotion(id={self.id}, title='{self.title}', discount={self.discount_value})>"

    def is_valid(self) -> bool:
        """Check if promotion is currently valid"""
        if not self.is_active:
            return False

        now = datetime.utcnow()

        # Check start date
        if self.start_date and now < self.start_date:
            return False

        # Check end date
        if self.end_date and now > self.end_date:
            return False

        # Check max uses
        if self.max_uses and self.current_uses >= self.max_uses:
            return False

        return True

    def applies_to_product(self, product_id: int) -> bool:
        """Check if promotion applies to specific product"""
        if not self.product_ids:
            return True  # Applies to all products

        return product_id in self.product_ids

    def applies_to_category(self, category_id: int) -> bool:
        """Check if promotion applies to specific category"""
        if not self.category_ids:
            return True  # Applies to all categories

        return category_id in self.category_ids

    def calculate_discount(self, amount: float) -> float:
        """Calculate discount amount for given purchase amount"""
        if not self.is_valid():
            return 0.0

        if self.min_purchase_amount and amount < self.min_purchase_amount:
            return 0.0

        if self.discount_type == "percentage":
            return amount * (self.discount_value / 100)
        elif self.discount_type == "fixed_amount":
            return min(self.discount_value, amount)

        return 0.0
