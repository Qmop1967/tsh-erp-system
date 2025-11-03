"""
Review Model
Product reviews and ratings system
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from datetime import datetime
from app.db.database import Base


class Review(Base):
    """
    Product reviews and ratings

    Used for:
    - Product ratings and feedback
    - Customer testimonials
    - Quality assurance
    - Purchase decisions
    """
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)

    # Product and Customer
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)

    # Rating (1-5 stars)
    rating = Column(Integer, nullable=False, comment="1-5 star rating")

    # Review Content
    title = Column(String(255), nullable=True, comment="Review headline")
    comment = Column(Text, nullable=True, comment="Detailed review text")

    # Media Attachments
    images = Column(ARRAY(String), nullable=True, comment="Array of image URLs")
    video_url = Column(String(500), nullable=True)

    # Purchase Verification
    is_verified_purchase = Column(Boolean, default=False, index=True, comment="Verified buyer")
    order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=True)
    purchase_date = Column(DateTime, nullable=True)

    # Moderation
    status = Column(
        String(50),
        nullable=False,
        default="pending",
        index=True,
        comment="pending, approved, rejected, flagged"
    )
    is_visible = Column(Boolean, default=False, comment="Public visibility")
    moderated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    moderated_at = Column(DateTime, nullable=True)
    moderation_notes = Column(Text, nullable=True)

    # Helpfulness Tracking
    helpful_count = Column(Integer, default=0, nullable=False, comment="Helpful votes")
    not_helpful_count = Column(Integer, default=0, nullable=False)

    # Response from Business
    response_text = Column(Text, nullable=True, comment="Seller/support response")
    responded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    responded_at = Column(DateTime, nullable=True)

    # Flagging/Reporting
    is_flagged = Column(Boolean, default=False, index=True)
    flag_count = Column(Integer, default=0)
    flag_reasons = Column(JSONB, nullable=True, comment="Array of flag reasons")

    # SEO and Display
    is_featured = Column(Boolean, default=False, comment="Featured review")
    display_priority = Column(Integer, default=0, comment="Higher priority shows first")

    # Customer Information (at time of review)
    customer_name = Column(String(255), nullable=True, comment="Display name")
    customer_location = Column(String(255), nullable=True)

    # Review Attributes (Product-specific)
    attributes = Column(JSONB, nullable=True, comment="Product-specific ratings (quality, value, etc.)")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    published_at = Column(DateTime, nullable=True)

    # Soft Delete
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False, index=True)

    # Relationships
    product = relationship("Product", back_populates="reviews")
    customer = relationship("Customer", foreign_keys=[customer_id])
    order = relationship("SalesOrder", foreign_keys=[order_id])
    moderator = relationship("User", foreign_keys=[moderated_by])
    responder = relationship("User", foreign_keys=[responded_by])

    def __repr__(self):
        return f"<Review(id={self.id}, product_id={self.product_id}, rating={self.rating}, status='{self.status}')>"

    @property
    def helpfulness_score(self) -> float:
        """Calculate helpfulness score (0-1)"""
        total = self.helpful_count + self.not_helpful_count
        if total == 0:
            return 0.0
        return self.helpful_count / total

    def approve(self, moderator_id: int, notes: str = None):
        """Approve review for public display"""
        self.status = "approved"
        self.is_visible = True
        self.moderated_by = moderator_id
        self.moderated_at = datetime.utcnow()
        self.moderation_notes = notes
        self.published_at = datetime.utcnow()

    def reject(self, moderator_id: int, reason: str):
        """Reject review"""
        self.status = "rejected"
        self.is_visible = False
        self.moderated_by = moderator_id
        self.moderated_at = datetime.utcnow()
        self.moderation_notes = reason

    def flag(self, reason: str):
        """Flag review for moderation"""
        self.is_flagged = True
        self.flag_count += 1

        if not self.flag_reasons:
            self.flag_reasons = []

        self.flag_reasons.append({
            "reason": reason,
            "flagged_at": datetime.utcnow().isoformat()
        })

        # Auto-hide if too many flags
        if self.flag_count >= 3:
            self.is_visible = False
            self.status = "flagged"

    def mark_helpful(self):
        """Mark review as helpful"""
        self.helpful_count += 1

    def mark_not_helpful(self):
        """Mark review as not helpful"""
        self.not_helpful_count += 1

    def add_response(self, responder_id: int, response_text: str):
        """Add business response to review"""
        self.response_text = response_text
        self.responded_by = responder_id
        self.responded_at = datetime.utcnow()

    def soft_delete(self):
        """Soft delete review"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.is_visible = False

    def validate_rating(self) -> bool:
        """Validate rating is within range"""
        return 1 <= self.rating <= 5

    @classmethod
    def calculate_average_rating(cls, reviews: list) -> float:
        """Calculate average rating from list of reviews"""
        if not reviews:
            return 0.0

        visible_reviews = [r for r in reviews if r.is_visible and not r.is_deleted]
        if not visible_reviews:
            return 0.0

        total_rating = sum(r.rating for r in visible_reviews)
        return round(total_rating / len(visible_reviews), 2)

    @classmethod
    def calculate_rating_distribution(cls, reviews: list) -> dict:
        """Calculate rating distribution (1-5 stars)"""
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        visible_reviews = [r for r in reviews if r.is_visible and not r.is_deleted]

        for review in visible_reviews:
            if review.rating in distribution:
                distribution[review.rating] += 1

        return distribution
