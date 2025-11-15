"""
Salesperson App Pydantic Schemas
Request/Response models for field sales BFF API endpoints

Features:
- GPS Location Tracking (8 endpoints)
- Money Transfers (12 endpoints - using existing money_transfer schemas)
- Commission Management (13 endpoints)
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
from enum import Enum


# ============================================================================
# GPS LOCATION TRACKING SCHEMAS
# ============================================================================

class GPSLocationCreate(BaseModel):
    """Create single GPS location point"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude (-90 to 90)")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude (-180 to 180)")
    timestamp: datetime = Field(..., description="Location timestamp (device time)")
    accuracy: Optional[float] = Field(None, ge=0, description="Accuracy in meters")
    altitude: Optional[float] = Field(None, description="Altitude in meters")
    speed: Optional[float] = Field(None, ge=0, description="Speed in m/s")
    heading: Optional[float] = Field(None, ge=0, le=360, description="Direction in degrees")

    # Activity context
    activity_type: Optional[str] = Field(None, description="driving, walking, stationary")
    battery_level: Optional[int] = Field(None, ge=0, le=100, description="Battery percentage")
    is_charging: Optional[bool] = Field(None, description="Is device charging")
    device_id: Optional[str] = Field(None, description="Device identifier")

    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 33.3152,
                "longitude": 44.3661,
                "timestamp": "2025-11-15T10:30:00Z",
                "accuracy": 5.0,
                "speed": 15.5,
                "heading": 180,
                "activity_type": "driving",
                "battery_level": 75
            }
        }


class BatchLocationRequest(BaseModel):
    """Batch upload GPS locations (offline sync)"""
    locations: List[GPSLocationCreate] = Field(..., min_length=1, max_length=1000)

    class Config:
        json_schema_extra = {
            "example": {
                "locations": [
                    {
                        "latitude": 33.3152,
                        "longitude": 44.3661,
                        "timestamp": "2025-11-15T10:30:00Z",
                        "accuracy": 5.0
                    }
                ]
            }
        }


class VerifyVisitRequest(BaseModel):
    """Verify customer visit with GPS coordinates"""
    customer_id: int = Field(..., description="Customer ID being visited")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    visit_time: datetime = Field(..., description="Visit timestamp")
    notes: Optional[str] = Field(None, max_length=500, description="Visit notes")

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": 123,
                "latitude": 33.3152,
                "longitude": 44.3661,
                "visit_time": "2025-11-15T10:30:00Z",
                "notes": "Met with store manager, discussed new products"
            }
        }


class GPSLocationResponse(BaseModel):
    """GPS location response"""
    id: int
    location_uuid: str
    salesperson_id: int
    latitude: Decimal
    longitude: Decimal
    accuracy: Optional[float]
    altitude: Optional[float]
    speed: Optional[float]
    heading: Optional[float]
    timestamp: datetime
    activity_type: Optional[str]
    is_customer_visit: bool
    customer_id: Optional[int]
    visit_verified: bool
    distance_from_customer: Optional[float]
    is_synced: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DailySummaryResponse(BaseModel):
    """Daily GPS tracking summary"""
    date: date
    total_distance_km: Decimal
    total_duration_hours: Decimal
    customer_visits: int
    verified_visits: int
    route: List[GPSLocationResponse]
    start_time: Optional[datetime]
    end_time: Optional[datetime]


class WeeklySummaryResponse(BaseModel):
    """Weekly GPS tracking summary"""
    week_start: date
    week_end: date
    total_distance_km: Decimal
    total_duration_hours: Decimal
    total_customer_visits: int
    total_verified_visits: int
    daily_breakdown: List[DailySummaryResponse]


class VerifyVisitResponse(BaseModel):
    """Customer visit verification response"""
    verified: bool
    distance_from_customer: float
    within_geofence: bool
    customer_name: str
    customer_address: Optional[str]
    visit_id: int


class SyncStatusResponse(BaseModel):
    """GPS sync status"""
    pending_locations: int
    last_sync: Optional[datetime]
    is_syncing: bool
    sync_errors: int


# ============================================================================
# COMMISSION MANAGEMENT SCHEMAS
# ============================================================================

class CommissionStatus(str, Enum):
    """Commission status options"""
    PENDING = "pending"
    CALCULATED = "calculated"
    APPROVED = "approved"
    PAID = "paid"
    SETTLED = "settled"


class CommissionPeriod(str, Enum):
    """Commission period types"""
    TODAY = "today"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    ALL = "all"
    CUSTOM = "custom"


class CommissionSummaryResponse(BaseModel):
    """Commission summary for a period"""
    salesperson_id: int
    salesperson_name: str
    period: str
    period_start: date
    period_end: date

    # Financial data
    total_sales: Decimal
    commission_rate: Decimal
    total_commission: Decimal
    pending_commission: Decimal
    paid_commission: Decimal

    # Order statistics
    total_orders: int
    total_customers: int
    avg_order_value: Decimal

    # Performance
    target_sales: Optional[Decimal]
    target_achievement_percentage: Optional[Decimal]
    rank: Optional[int]


class CommissionHistoryItem(BaseModel):
    """Single commission record"""
    id: int
    commission_uuid: str
    period_type: str
    period_start: date
    period_end: date
    total_sales_amount: Decimal
    commission_rate: Decimal
    calculated_commission: Decimal
    approved_commission: Optional[Decimal]
    status: str
    is_paid: bool
    paid_date: Optional[date]
    payment_method: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class CommissionHistoryResponse(BaseModel):
    """Commission history list"""
    commissions: List[CommissionHistoryItem]
    total: int
    total_earned: Decimal
    total_pending: Decimal


class CommissionDetailResponse(BaseModel):
    """Detailed commission information"""
    id: int
    commission_uuid: str
    salesperson_id: int
    salesperson_name: str
    period_type: str
    period_start: date
    period_end: date

    # Financial details
    total_sales_amount: Decimal
    commission_rate: Decimal
    calculated_commission: Decimal
    approved_commission: Optional[Decimal]

    # Order details
    total_orders: int
    total_customers: int
    avg_order_value: Decimal

    # Status
    status: str
    is_paid: bool
    paid_date: Optional[date]
    payment_method: Optional[str]
    payment_reference: Optional[str]

    # Workflow
    calculated_at: Optional[datetime]
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    paid_by: Optional[int]
    paid_at: Optional[datetime]

    # Notes
    notes: Optional[str]
    manager_notes: Optional[str]

    # Audit
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CalculateCommissionRequest(BaseModel):
    """Calculate commission preview"""
    sales_amount: Decimal = Field(..., gt=0, description="Total sales amount")
    commission_rate: Optional[Decimal] = Field(2.25, description="Commission rate percentage")

    class Config:
        json_schema_extra = {
            "example": {
                "sales_amount": 10000000,
                "commission_rate": 2.25
            }
        }


class CalculateCommissionResponse(BaseModel):
    """Commission calculation result"""
    sales_amount: Decimal
    commission_rate: Decimal
    commission_amount: Decimal
    estimated_payout: Decimal
    tax_amount: Optional[Decimal]
    net_payout: Optional[Decimal]


class SalesTargetResponse(BaseModel):
    """Sales target information"""
    id: int
    target_uuid: str
    salesperson_id: int
    salesperson_name: str
    period_type: str
    period_start: date
    period_end: date

    # Targets
    target_revenue_iqd: Decimal
    target_revenue_usd: Decimal
    target_orders: int
    target_customers: int

    # Achievement
    achieved_revenue_iqd: Decimal
    achieved_revenue_usd: Decimal
    achieved_orders: int
    achieved_customers: int

    # Progress
    revenue_progress_percentage: Decimal
    orders_progress_percentage: Decimal
    customers_progress_percentage: Decimal
    overall_progress_percentage: Decimal

    # Status
    is_achieved: bool
    achievement_date: Optional[date]
    is_active: bool

    # Bonus
    bonus_enabled: bool
    bonus_percentage: Optional[Decimal]
    bonus_amount: Optional[Decimal]
    bonus_paid: bool

    class Config:
        from_attributes = True


class SetTargetRequest(BaseModel):
    """Set sales target"""
    salesperson_id: int
    period_type: str = Field(..., description="monthly, quarterly, yearly")
    period_start: date
    period_end: date
    target_revenue_iqd: Optional[Decimal] = Field(None, ge=0)
    target_revenue_usd: Optional[Decimal] = Field(None, ge=0)
    target_orders: Optional[int] = Field(None, ge=0)
    target_customers: Optional[int] = Field(None, ge=0)
    bonus_enabled: bool = False
    bonus_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    bonus_amount: Optional[Decimal] = Field(None, ge=0)
    description: Optional[str] = Field(None, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "salesperson_id": 5,
                "period_type": "monthly",
                "period_start": "2025-11-01",
                "period_end": "2025-11-30",
                "target_revenue_iqd": 50000000,
                "target_orders": 100,
                "bonus_enabled": True,
                "bonus_percentage": 1.0
            }
        }


class LeaderboardEntry(BaseModel):
    """Leaderboard entry"""
    rank: int
    salesperson_id: int
    salesperson_name: str
    total_sales: Decimal
    total_commission: Decimal
    total_orders: int
    total_customers: int
    target_achievement_percentage: Optional[Decimal]
    badge: Optional[str]  # "top_performer", "rising_star", etc.


class LeaderboardResponse(BaseModel):
    """Team leaderboard"""
    period: str
    period_start: date
    period_end: date
    leaderboard: List[LeaderboardEntry]
    total_participants: int
    my_rank: Optional[int]


class WeeklyEarningsResponse(BaseModel):
    """Weekly earnings breakdown"""
    week_start: date
    week_end: date
    total_sales: Decimal
    total_commission: Decimal
    paid_commission: Decimal
    pending_commission: Decimal
    total_orders: int
    avg_order_value: Decimal
    daily_breakdown: List[dict]  # [{date, sales, commission, orders}, ...]


class CommissionStatisticsResponse(BaseModel):
    """Commission statistics"""
    lifetime_earnings: Decimal
    ytd_earnings: Decimal
    mtd_earnings: Decimal
    avg_monthly_commission: Decimal
    highest_monthly_commission: Decimal
    total_orders_all_time: int
    avg_commission_per_order: Decimal
    commission_trend: str  # "increasing", "decreasing", "stable"


class UpdateCommissionStatusRequest(BaseModel):
    """Update commission status"""
    status: CommissionStatus
    notes: Optional[str] = Field(None, max_length=500)


class MarkPaidRequest(BaseModel):
    """Mark commission as paid"""
    payment_method: str = Field(..., description="cash, bank_transfer, offset")
    payment_reference: Optional[str] = Field(None, max_length=100)
    paid_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)


class RequestPayoutRequest(BaseModel):
    """Request commission payout"""
    commission_ids: List[int] = Field(..., min_length=1, description="Commission IDs to pay out")
    payment_method: str = Field(..., description="Preferred payment method")
    notes: Optional[str] = Field(None, max_length=500)


class RequestPayoutResponse(BaseModel):
    """Payout request response"""
    request_id: int
    total_amount: Decimal
    commission_count: int
    status: str
    estimated_payment_date: Optional[date]


# ============================================================================
# BATCH OPERATIONS AND SYNC
# ============================================================================

class BatchOperationResponse(BaseModel):
    """Generic batch operation response"""
    success: bool
    total: int
    uploaded: int
    failed: int
    errors: List[dict]  # [{index, error, details}, ...]
    ids: Optional[List[int]]  # IDs of successfully created records


class SyncResult(BaseModel):
    """Sync operation result"""
    success: bool
    gps_uploaded: int
    gps_failed: int
    transfers_uploaded: int
    transfers_failed: int
    total_uploaded: int
    total_failed: int
    message: str
    errors: List[dict]
