"""
Money Transfer Tracking Module for TSH ERP System
CRITICAL: Prevents fraud for $35K USD weekly transfers from 12 travel salespersons
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.database import Base


class MoneyTransfer(Base):
    """Money Transfer Tracking - FRAUD PREVENTION CRITICAL"""
    __tablename__ = "money_transfers"

    id = Column(Integer, primary_key=True, index=True)
    transfer_uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    
    # Salesperson tracking
    salesperson_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    salesperson_name = Column(String(100), nullable=False)
    
    # Financial details
    amount_usd = Column(Float, nullable=False)
    amount_iqd = Column(Float, nullable=False)
    exchange_rate = Column(Float, nullable=False)
    
    # Commission tracking (CRITICAL)
    gross_sales = Column(Float, nullable=False)
    commission_rate = Column(Float, default=2.25)
    calculated_commission = Column(Float, nullable=False)
    claimed_commission = Column(Float, nullable=False)
    commission_verified = Column(Boolean, default=False)
    
    # Platform information
    transfer_platform = Column(String(50), nullable=False)
    platform_reference = Column(String(100))
    transfer_fee = Column(Float, default=0.0)
    
    # GPS and verification
    transfer_datetime = Column(DateTime, nullable=False)
    gps_latitude = Column(Float)
    gps_longitude = Column(Float)
    location_name = Column(String(200))
    receipt_photo_url = Column(String(500))
    receipt_verified = Column(Boolean, default=False)
    
    # Status tracking
    status = Column(String(20), default="pending")
    money_received = Column(Boolean, default=False)
    received_datetime = Column(DateTime)
    
    # Fraud detection
    is_suspicious = Column(Boolean, default=False)
    fraud_alert_reason = Column(Text)
    manager_approval_required = Column(Boolean, default=False)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    salesperson = relationship("User", back_populates="money_transfers")


class TransferPlatform(Base):
    """Money transfer platforms configuration"""
    __tablename__ = "transfer_platforms"
    
    id = Column(Integer, primary_key=True, index=True)
    platform_name = Column(String(50), nullable=False)
    platform_code = Column(String(10), nullable=False)
    has_api = Column(Boolean, default=False)
    api_endpoint = Column(String(200))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow) 