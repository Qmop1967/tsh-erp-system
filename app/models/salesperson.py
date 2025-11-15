"""
Salesperson Feature Models for TSH ERP System
Database models for field sales app: GPS tracking, commissions, targets

Business Context:
- 12 travel salespersons managing $35,000 USD weekly
- Real-time GPS tracking for route verification
- 2.25% commission automatic calculation
- Sales target tracking and leaderboards
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Date, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.database import Base


class SalespersonGPSLocation(Base):
    """
    GPS Location Tracking for Field Salespersons

    Business Purpose:
    - Track salesperson movements and routes
    - Verify customer visits with geofencing
    - Calculate distance traveled and time on route
    - Fraud prevention (ensure visits are genuine)
    - Performance analytics

    Integration:
    - Used by mobile app for automatic background tracking
    - Supports offline mode (batch sync when online)
    - Customer visit verification with proximity checks
    """
    __tablename__ = "salesperson_gps_locations"

    id = Column(Integer, primary_key=True, index=True)
    location_uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)

    # Salesperson tracking
    salesperson_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # GPS coordinates
    latitude = Column(Numeric(10, 8), nullable=False)  # Precision: 8 decimal places (~1mm accuracy)
    longitude = Column(Numeric(11, 8), nullable=False)
    accuracy = Column(Float)  # Accuracy in meters
    altitude = Column(Float)  # Altitude in meters
    speed = Column(Float)  # Speed in meters/second
    heading = Column(Float)  # Direction in degrees (0-360)

    # Timing
    timestamp = Column(DateTime, nullable=False, index=True)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    # Activity context
    activity_type = Column(String(50))  # driving, walking, stationary
    is_customer_visit = Column(Boolean, default=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    visit_verified = Column(Boolean, default=False)
    distance_from_customer = Column(Float)  # Distance in meters when visit logged

    # Battery and device info
    battery_level = Column(Integer)  # 0-100
    is_charging = Column(Boolean)
    device_id = Column(String(100))

    # Sync status
    is_synced = Column(Boolean, default=False, index=True)
    synced_at = Column(DateTime)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    salesperson = relationship("User", foreign_keys=[salesperson_id])
    customer = relationship("Customer", foreign_keys=[customer_id])


class SalespersonCommission(Base):
    """
    Commission Tracking for Salespersons

    Business Logic:
    - Commission Rate: 2.25% of total sales
    - Calculated automatically from sales orders
    - Tracked by period (daily, weekly, monthly)
    - Payout workflow with approval
    - Integration with money transfers

    Status Flow:
    pending → calculated → approved → paid → settled
    """
    __tablename__ = "salesperson_commissions"

    id = Column(Integer, primary_key=True, index=True)
    commission_uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))

    # Salesperson
    salesperson_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    salesperson_name = Column(String(100), nullable=False)

    # Period tracking
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly, custom
    period_start = Column(Date, nullable=False, index=True)
    period_end = Column(Date, nullable=False, index=True)

    # Financial calculations
    total_sales_amount = Column(Numeric(12, 2), nullable=False, default=0)  # Total sales in period
    commission_rate = Column(Numeric(5, 2), default=2.25)  # Commission percentage
    calculated_commission = Column(Numeric(12, 2), nullable=False, default=0)  # Auto-calculated
    approved_commission = Column(Numeric(12, 2))  # Manager can adjust

    # Order details
    total_orders = Column(Integer, default=0)
    total_customers = Column(Integer, default=0)
    avg_order_value = Column(Numeric(12, 2), default=0)

    # Status and workflow
    status = Column(String(20), default="pending", index=True)  # pending, calculated, approved, paid, settled
    is_paid = Column(Boolean, default=False, index=True)
    paid_date = Column(Date)
    payment_method = Column(String(50))  # cash, bank_transfer, offset
    payment_reference = Column(String(100))

    # Integration with money transfers
    transfer_id = Column(Integer, ForeignKey("money_transfers.id"), nullable=True)

    # Approval workflow
    calculated_by = Column(Integer, ForeignKey("users.id"))
    calculated_at = Column(DateTime)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime)
    paid_by = Column(Integer, ForeignKey("users.id"))
    paid_at = Column(DateTime)

    # Notes
    notes = Column(Text)
    manager_notes = Column(Text)

    # Sync status
    is_synced = Column(Boolean, default=False)
    synced_at = Column(DateTime)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    salesperson = relationship("User", foreign_keys=[salesperson_id])
    transfer = relationship("MoneyTransfer", foreign_keys=[transfer_id])
    calculator = relationship("User", foreign_keys=[calculated_by])
    approver = relationship("User", foreign_keys=[approved_by])
    payer = relationship("User", foreign_keys=[paid_by])


class SalespersonTarget(Base):
    """
    Sales Targets for Salespersons

    Business Purpose:
    - Set monthly/quarterly sales targets
    - Track achievement progress
    - Calculate bonus commissions
    - Team performance rankings
    - Motivation and gamification

    Target Types:
    - Revenue target (IQD/USD)
    - Order count target
    - Customer acquisition target
    - Product category targets
    """
    __tablename__ = "salesperson_targets"

    id = Column(Integer, primary_key=True, index=True)
    target_uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))

    # Salesperson
    salesperson_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    salesperson_name = Column(String(100), nullable=False)

    # Target period
    period_type = Column(String(20), nullable=False)  # monthly, quarterly, yearly, custom
    period_start = Column(Date, nullable=False, index=True)
    period_end = Column(Date, nullable=False, index=True)

    # Target metrics
    target_revenue_iqd = Column(Numeric(12, 2), default=0)
    target_revenue_usd = Column(Numeric(12, 2), default=0)
    target_orders = Column(Integer, default=0)
    target_customers = Column(Integer, default=0)

    # Achievement tracking
    achieved_revenue_iqd = Column(Numeric(12, 2), default=0)
    achieved_revenue_usd = Column(Numeric(12, 2), default=0)
    achieved_orders = Column(Integer, default=0)
    achieved_customers = Column(Integer, default=0)

    # Progress percentages (auto-calculated)
    revenue_progress_percentage = Column(Numeric(5, 2), default=0)
    orders_progress_percentage = Column(Numeric(5, 2), default=0)
    customers_progress_percentage = Column(Numeric(5, 2), default=0)
    overall_progress_percentage = Column(Numeric(5, 2), default=0)

    # Status
    is_achieved = Column(Boolean, default=False, index=True)
    achievement_date = Column(Date)
    is_active = Column(Boolean, default=True, index=True)

    # Bonus configuration
    bonus_enabled = Column(Boolean, default=False)
    bonus_percentage = Column(Numeric(5, 2))  # Extra commission % if target met
    bonus_amount = Column(Numeric(12, 2))  # Fixed bonus amount
    bonus_paid = Column(Boolean, default=False)

    # Management
    set_by = Column(Integer, ForeignKey("users.id"))  # Manager who set the target
    set_at = Column(DateTime, default=datetime.utcnow)

    # Notes
    description = Column(Text)
    notes = Column(Text)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    salesperson = relationship("User", foreign_keys=[salesperson_id])
    manager = relationship("User", foreign_keys=[set_by])


class SalespersonDailySummary(Base):
    """
    Daily Performance Summary for Salespersons

    Pre-calculated daily metrics for fast dashboard loading
    Updated automatically at end of day or on-demand

    Performance Optimization:
    - Avoid calculating on every API call
    - Cache daily statistics
    - Fast leaderboard generation
    """
    __tablename__ = "salesperson_daily_summaries"

    id = Column(Integer, primary_key=True, index=True)

    # Salesperson and date
    salesperson_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    summary_date = Column(Date, nullable=False, index=True)

    # Sales metrics
    total_sales_iqd = Column(Numeric(12, 2), default=0)
    total_sales_usd = Column(Numeric(12, 2), default=0)
    total_orders = Column(Integer, default=0)
    total_customers_visited = Column(Integer, default=0)
    avg_order_value = Column(Numeric(12, 2), default=0)

    # Commission
    daily_commission = Column(Numeric(12, 2), default=0)

    # GPS tracking
    total_distance_km = Column(Numeric(8, 2), default=0)
    total_time_hours = Column(Numeric(6, 2), default=0)
    gps_points_count = Column(Integer, default=0)

    # Activity
    customer_visits = Column(Integer, default=0)
    verified_visits = Column(Integer, default=0)

    # Money transfers
    transfers_made = Column(Integer, default=0)
    total_transferred_usd = Column(Numeric(12, 2), default=0)

    # Performance ranking
    daily_rank = Column(Integer)  # Ranking among all salespersons for this date

    # Calculated at
    calculated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    salesperson = relationship("User", foreign_keys=[salesperson_id])

    # Unique constraint: one summary per salesperson per day
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )
