"""
Customer Address Model
Multiple delivery/billing addresses per customer
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.db.database import Base


class CustomerAddress(Base):
    """
    Customer delivery and billing addresses

    Used for:
    - Multiple shipping addresses per customer
    - Billing address management
    - Address book for quick checkout
    - Delivery zone calculation
    """
    __tablename__ = "customer_addresses"

    id = Column(Integer, primary_key=True, index=True)

    # Customer Reference
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)

    # Address Type
    address_type = Column(
        String(50),
        nullable=False,
        default="shipping",
        comment="shipping, billing, both"
    )

    # Address Label
    label = Column(String(100), nullable=True, comment="Home, Office, Warehouse, etc.")

    # Primary Fields
    full_name = Column(String(255), nullable=False, comment="Recipient name")
    phone = Column(String(20), nullable=False, index=True)
    alternate_phone = Column(String(20), nullable=True)

    # Address Components
    address_line1 = Column(String(255), nullable=False, comment="Street address")
    address_line2 = Column(String(255), nullable=True, comment="Apartment, suite, etc.")
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=True, comment="State/Province")
    postal_code = Column(String(20), nullable=True, index=True)
    country = Column(String(100), nullable=False, default="Iraq")

    # Location Coordinates (for delivery routing)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Delivery Instructions
    delivery_instructions = Column(Text, nullable=True, comment="Gate code, landmarks, etc.")

    # Default Address Flags
    is_default_shipping = Column(Boolean, default=False, index=True)
    is_default_billing = Column(Boolean, default=False, index=True)

    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False, comment="Address verified by delivery")

    # Delivery Zone (for shipping cost calculation)
    delivery_zone_id = Column(Integer, nullable=True, comment="Delivery zone ID")
    delivery_zone_name = Column(String(100), nullable=True)

    # Usage Statistics
    times_used = Column(Integer, default=0, comment="Number of times address used")
    last_used_at = Column(DateTime, nullable=True)

    # Verification
    verified_at = Column(DateTime, nullable=True)
    verified_by_order_id = Column(Integer, nullable=True, comment="Order that verified address")

    # Additional Metadata
    extra_data = Column(JSONB, nullable=True, comment="Additional address data")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Soft Delete
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)

    # Relationships
    customer = relationship("Customer", back_populates="addresses")

    def __repr__(self):
        return f"<CustomerAddress(id={self.id}, customer_id={self.customer_id}, label='{self.label}', city='{self.city}')>"

    @property
    def full_address(self) -> str:
        """Get formatted full address"""
        parts = [
            self.address_line1,
            self.address_line2,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        return ", ".join([p for p in parts if p])

    @property
    def short_address(self) -> str:
        """Get short address for display"""
        return f"{self.address_line1}, {self.city}"

    def set_as_default_shipping(self, db_session):
        """Set this address as default shipping"""
        # Remove default from other addresses
        db_session.query(CustomerAddress).filter(
            CustomerAddress.customer_id == self.customer_id,
            CustomerAddress.id != self.id
        ).update({"is_default_shipping": False})

        self.is_default_shipping = True

    def set_as_default_billing(self, db_session):
        """Set this address as default billing"""
        # Remove default from other addresses
        db_session.query(CustomerAddress).filter(
            CustomerAddress.customer_id == self.customer_id,
            CustomerAddress.id != self.id
        ).update({"is_default_billing": False})

        self.is_default_billing = True

    def mark_as_used(self):
        """Increment usage counter"""
        self.times_used += 1
        self.last_used_at = datetime.utcnow()

    def verify(self, order_id: int = None):
        """Mark address as verified"""
        self.is_verified = True
        self.verified_at = datetime.utcnow()
        self.verified_by_order_id = order_id

    def soft_delete(self):
        """Soft delete address"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.is_active = False

    def calculate_distance_to(self, lat: float, lng: float) -> float:
        """
        Calculate distance to another location (in kilometers)
        Using Haversine formula
        """
        if not self.latitude or not self.longitude:
            return None

        import math

        R = 6371  # Earth's radius in kilometers

        lat1 = math.radians(self.latitude)
        lat2 = math.radians(lat)
        delta_lat = math.radians(lat - self.latitude)
        delta_lng = math.radians(lng - self.longitude)

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lng / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def is_within_delivery_radius(self, warehouse_lat: float, warehouse_lng: float, max_km: float = 50) -> bool:
        """Check if address is within delivery radius"""
        distance = self.calculate_distance_to(warehouse_lat, warehouse_lng)
        if distance is None:
            return True  # Allow if coordinates not set

        return distance <= max_km

    @classmethod
    def get_default_shipping(cls, customer_id: int, db_session):
        """Get customer's default shipping address"""
        return db_session.query(cls).filter(
            cls.customer_id == customer_id,
            cls.is_default_shipping == True,
            cls.is_active == True,
            cls.is_deleted == False
        ).first()

    @classmethod
    def get_default_billing(cls, customer_id: int, db_session):
        """Get customer's default billing address"""
        return db_session.query(cls).filter(
            cls.customer_id == customer_id,
            cls.is_default_billing == True,
            cls.is_active == True,
            cls.is_deleted == False
        ).first()

    @classmethod
    def get_active_addresses(cls, customer_id: int, db_session):
        """Get all active addresses for customer"""
        return db_session.query(cls).filter(
            cls.customer_id == customer_id,
            cls.is_active == True,
            cls.is_deleted == False
        ).order_by(cls.is_default_shipping.desc(), cls.created_at.desc()).all()
