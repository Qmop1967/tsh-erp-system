"""
Money Transfer Schemas for TSH ERP System
CRITICAL: API schemas for fraud prevention and tracking
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum


class TransferStatus(str, Enum):
    """Money transfer status options"""
    PENDING = "pending"
    VERIFIED = "verified"
    RECEIVED = "received"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"


class TransferPlatform(str, Enum):
    """Supported money transfer platforms"""
    ALTAIF = "ALTaif Bank"
    ZAIN_CASH = "ZAIN Cash"
    SUPERQI = "SuperQi"
    OTHER = "Other"


class MoneyTransferCreate(BaseModel):
    """Schema for creating a new money transfer"""
    amount_usd: float = Field(..., gt=0, description="Transfer amount in USD")
    amount_iqd: float = Field(..., gt=0, description="Transfer amount in Iraqi Dinar")
    exchange_rate: float = Field(..., gt=0, description="USD to IQD exchange rate")
    
    # Commission data
    gross_sales: float = Field(..., gt=0, description="Total sales before commission")
    claimed_commission: float = Field(..., ge=0, description="Commission claimed by salesperson")
    
    # Transfer details
    transfer_platform: TransferPlatform = Field(..., description="Transfer platform used")
    platform_reference: Optional[str] = Field(None, description="Platform transaction reference")
    transfer_fee: float = Field(0.0, ge=0, description="Transfer fee charged")
    
    # Location data
    gps_latitude: Optional[float] = Field(None, description="GPS latitude")
    gps_longitude: Optional[float] = Field(None, description="GPS longitude")
    location_name: Optional[str] = Field(None, description="Location name")
    
    # Receipt
    receipt_photo_url: Optional[str] = Field(None, description="Receipt photo URL")
    
    @validator('claimed_commission')
    def validate_commission(cls, v, values):
        """Validate commission against gross sales"""
        if 'gross_sales' in values:
            expected_commission = values['gross_sales'] * 2.25 / 100
            if abs(v - expected_commission) > (expected_commission * 0.05):  # 5% tolerance
                raise ValueError(f"Commission seems incorrect. Expected ~{expected_commission:.2f}, got {v}")
        return v


class MoneyTransferUpdate(BaseModel):
    """Schema for updating money transfer"""
    status: Optional[TransferStatus] = None
    money_received: Optional[bool] = None
    received_datetime: Optional[datetime] = None
    receipt_verified: Optional[bool] = None
    commission_verified: Optional[bool] = None
    manager_approval_required: Optional[bool] = None
    verification_notes: Optional[str] = None


class MoneyTransferResponse(BaseModel):
    """Schema for money transfer response"""
    id: int
    transfer_uuid: str
    salesperson_id: int
    salesperson_name: str
    
    # Financial details
    amount_usd: float
    amount_iqd: float
    exchange_rate: float
    
    # Commission details
    gross_sales: float
    commission_rate: float
    calculated_commission: float
    claimed_commission: float
    commission_verified: bool
    
    # Transfer details
    transfer_platform: str
    platform_reference: Optional[str]
    transfer_fee: float
    
    # Location and verification
    transfer_datetime: datetime
    gps_latitude: Optional[float]
    gps_longitude: Optional[float]
    location_name: Optional[str]
    receipt_photo_url: Optional[str]
    receipt_verified: bool
    
    # Status
    status: str
    money_received: bool
    received_datetime: Optional[datetime]
    
    # Fraud detection
    is_suspicious: bool
    fraud_alert_reason: Optional[str]
    manager_approval_required: bool
    
    # Audit
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MoneyTransferSummary(BaseModel):
    """Summary schema for dashboard"""
    salesperson_id: int
    salesperson_name: str
    total_transfers: int
    total_amount_usd: float
    total_amount_iqd: float
    pending_transfers: int
    suspicious_transfers: int
    total_commission: float
    last_transfer_date: Optional[datetime]


class WeeklyCommissionReport(BaseModel):
    """Weekly commission report for salesperson"""
    salesperson_id: int
    salesperson_name: str
    week_start: datetime
    week_end: datetime
    total_sales: float
    calculated_commission: float
    commission_taken: float
    commission_difference: float
    transfer_count: int
    total_transferred: float
    is_approved: bool
    
    
class DashboardStats(BaseModel):
    """Dashboard statistics for money transfers"""
    total_pending_amount: float
    total_received_today: float
    suspicious_transfers_count: int
    pending_transfers_count: int
    salesperson_summaries: List[MoneyTransferSummary]
    platform_breakdown: dict
    
    
class FraudAlert(BaseModel):
    """Fraud alert schema"""
    transfer_id: int
    salesperson_name: str
    alert_reason: str
    amount_usd: float
    created_at: datetime
    priority: str  # high, medium, low
    
    
class TransferPlatformConfig(BaseModel):
    """Transfer platform configuration"""
    platform_name: str
    platform_code: str
    has_api: bool
    api_endpoint: Optional[str]
    is_active: bool 