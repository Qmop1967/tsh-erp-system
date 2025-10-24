"""All PRSS models in one file for quick setup"""
from sqlalchemy import Column, BigInteger, String, Boolean, Integer, DateTime, Text, Numeric, Date, ForeignKey, Enum as SQLEnum, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from prss.db import Base
from .base import *


class Product(Base):
    __tablename__ = "products"
    id = Column(BigInteger, primary_key=True)
    external_product_id = Column(BigInteger, unique=True, nullable=False)
    name = Column(Text, nullable=False)
    sku = Column(Text, nullable=False)
    requires_serial = Column(Boolean, default=False)
    warranty_months = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())


class ReturnRequest(Base):
    __tablename__ = "return_requests"
    id = Column(BigInteger, primary_key=True)
    customer_id = Column(BigInteger, nullable=False, index=True)
    sales_order_id = Column(BigInteger)
    invoice_id = Column(BigInteger)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False)
    serial_number = Column(Text, index=True)
    reason_code = Column(Text, nullable=False)
    reason_description = Column(Text)
    photos = Column(JSONB, default=[])
    videos = Column(JSONB, default=[])
    status = Column(SQLEnum(ReturnStatus), default=ReturnStatus.SUBMITTED, index=True)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(BigInteger)


class ReverseLogistics(Base):
    __tablename__ = "reverse_logistics"
    id = Column(BigInteger, primary_key=True)
    return_request_id = Column(BigInteger, ForeignKey("return_requests.id", ondelete="CASCADE"), nullable=False)
    pickup_method = Column(Text)
    carrier = Column(Text)
    tracking_no = Column(Text, index=True)
    status = Column(SQLEnum(LogisticsStatus), default=LogisticsStatus.REQUESTED)
    estimated_pickup_date = Column(Date)
    actual_pickup_date = Column(Date)
    estimated_delivery_date = Column(Date)
    actual_delivery_date = Column(Date)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())


class Inspection(Base):
    __tablename__ = "inspections"
    id = Column(BigInteger, primary_key=True)
    return_request_id = Column(BigInteger, ForeignKey("return_requests.id", ondelete="CASCADE"), nullable=False, unique=True)
    inspector_id = Column(BigInteger, nullable=False)
    checklists = Column(JSONB, default={})
    finding = Column(SQLEnum(FindingType), nullable=False, index=True)
    recommendation = Column(SQLEnum(RecommendationType), nullable=False)
    inspection_photos = Column(JSONB, default=[])
    notes = Column(Text)
    inspection_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MaintenanceJob(Base):
    __tablename__ = "maintenance_jobs"
    id = Column(BigInteger, primary_key=True)
    return_request_id = Column(BigInteger, ForeignKey("return_requests.id", ondelete="CASCADE"), nullable=False)
    technician_id = Column(BigInteger, nullable=False, index=True)
    job_card_no = Column(Text, unique=True, nullable=False, index=True)
    parts_used = Column(JSONB, default=[])
    labor_minutes = Column(Integer, default=0)
    outcome = Column(SQLEnum(MaintenanceOutcome))
    warranty_impact = Column(Boolean, default=False)
    cost_estimate = Column(Numeric(12, 2))
    actual_cost = Column(Numeric(12, 2))
    notes = Column(Text)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WarrantyPolicy(Base):
    __tablename__ = "warranty_policies"
    id = Column(BigInteger, primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text)
    duration_months = Column(Integer, nullable=False)
    coverage_details = Column(JSONB, default={})
    terms = Column(Text)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WarrantyCase(Base):
    __tablename__ = "warranty_cases"
    id = Column(BigInteger, primary_key=True)
    return_request_id = Column(BigInteger, ForeignKey("return_requests.id", ondelete="CASCADE"), nullable=False, unique=True)
    policy_id = Column(BigInteger, ForeignKey("warranty_policies.id"))
    purchase_date = Column(Date, nullable=False)
    warranty_expiry_date = Column(Date, nullable=False)
    is_valid = Column(Boolean, default=True)
    decision = Column(SQLEnum(WarrantyDecision))
    decision_by = Column(BigInteger)
    decision_date = Column(DateTime(timezone=True))
    coverage_notes = Column(Text)
    sla_deadline = Column(DateTime(timezone=True), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Decision(Base):
    __tablename__ = "decisions"
    id = Column(BigInteger, primary_key=True)
    return_request_id = Column(BigInteger, ForeignKey("return_requests.id", ondelete="CASCADE"), nullable=False, unique=True)
    final_decision = Column(SQLEnum(FinalDecision), nullable=False, index=True)
    approved_by = Column(BigInteger, nullable=False)
    approved_at = Column(DateTime(timezone=True), server_default=func.now())
    reason = Column(Text)
    estimated_value = Column(Numeric(12, 2))
    notes = Column(Text)


class ReturnInventoryMove(Base):
    __tablename__ = "return_inventory_moves"
    id = Column(BigInteger, primary_key=True)
    return_request_id = Column(BigInteger, ForeignKey("return_requests.id", ondelete="CASCADE"), nullable=False)
    from_zone = Column(SQLEnum(InventoryZone))
    to_zone = Column(SQLEnum(InventoryZone), nullable=False)
    qty = Column(Integer, default=1)
    moved_by = Column(BigInteger, nullable=False)
    moved_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    notes = Column(Text)


class AccountingEffect(Base):
    __tablename__ = "accounting_effects"
    id = Column(BigInteger, primary_key=True)
    return_request_id = Column(BigInteger, ForeignKey("return_requests.id", ondelete="CASCADE"), nullable=False)
    effect_type = Column(SQLEnum(AccountingEffectType), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(Text, default="SAR")
    reference_no = Column(Text)
    posted = Column(Boolean, default=False, index=True)
    posted_at = Column(DateTime(timezone=True))
    posted_by = Column(BigInteger)
    external_ref = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class OutboxEvent(Base):
    __tablename__ = "outbox_events"
    id = Column(BigInteger, primary_key=True)
    topic = Column(Text, nullable=False, index=True)
    payload = Column(JSONB, nullable=False)
    status = Column(SQLEnum(OutboxStatus), default=OutboxStatus.PENDING, index=True)
    retries = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    last_error = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    sent_at = Column(DateTime(timezone=True))
    next_retry_at = Column(DateTime(timezone=True), index=True)


class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    external_user_id = Column(BigInteger, unique=True)
    username = Column(Text, unique=True, nullable=False, index=True)
    email = Column(Text, unique=True, nullable=False, index=True)
    full_name = Column(Text)
    role = Column(SQLEnum(UserRole), nullable=False, index=True)
    scopes = Column(ARRAY(Text), default=[])
    hashed_password = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id = Column(BigInteger, primary_key=True)
    return_request_id = Column(BigInteger, ForeignKey("return_requests.id", ondelete="CASCADE"))
    user_id = Column(BigInteger, ForeignKey("users.id"))
    action = Column(Text, nullable=False)
    entity_type = Column(Text, nullable=False)
    entity_id = Column(BigInteger)
    old_value = Column(JSONB)
    new_value = Column(JSONB)
    ip_address = Column(Text)
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
