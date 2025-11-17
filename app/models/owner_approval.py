"""
Owner Approval Model for TSH Security Console

This model handles secure approval workflows for sensitive operations
that require Owner/Director authorization.

Features:
- 6-digit approval codes with expiration
- QR code generation with signed JWT payloads
- Multiple approval methods (PUSH, QR, SMS, MANUAL)
- Complete audit trail with device and location info
- Geolocation tracking for security verification
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey,
    DateTime, Text, Enum, JSON, Float
)
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import enum
import uuid
import secrets
from typing import Optional

from app.db.database import Base


# === ENUMS ===

class ApprovalMethod(enum.Enum):
    """Method used for approval delivery and verification"""
    PUSH = "push"           # Push notification via TSH NeuroLink
    QR = "qr"               # QR code scanning
    SMS = "sms"             # SMS code (via TSH NeuroLink)
    MANUAL = "manual"       # Manual entry by Owner
    BIOMETRIC = "biometric" # Face ID/Touch ID verification


class ApprovalStatus(enum.Enum):
    """Status of the approval request"""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ApprovalType(enum.Enum):
    """Type of action requiring approval"""
    LOGIN_SUSPICIOUS = "login_suspicious"           # Suspicious login attempt
    HIGH_VALUE_TRANSACTION = "high_value_transaction"  # Large financial operation
    SENSITIVE_DATA_ACCESS = "sensitive_data_access"    # Access to critical data
    USER_ROLE_CHANGE = "user_role_change"           # Role/permission modification
    SYSTEM_CONFIG_CHANGE = "system_config_change"   # System configuration change
    BULK_OPERATION = "bulk_operation"               # Bulk data operations
    DEVICE_TRUST = "device_trust"                   # New device authorization
    EMERGENCY_ACCESS = "emergency_access"           # Emergency override request
    FINANCIAL_REPORT = "financial_report"           # Financial report access
    DATA_EXPORT = "data_export"                     # Data export operation


class RiskLevel(enum.Enum):
    """Risk level assessment of the approval request"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# === OWNER APPROVAL MODEL ===

class OwnerApproval(Base):
    """
    Owner Approval Request Model

    Tracks approval requests for sensitive operations requiring
    Owner/Director authorization. Supports multiple approval methods
    including push notifications, QR codes, and manual verification.
    """
    __tablename__ = "owner_approvals"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Request information
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approval_type = Column(Enum(ApprovalType), nullable=False)
    risk_level = Column(Enum(RiskLevel), default=RiskLevel.MEDIUM)

    # Approval credentials
    approval_code = Column(String(6), nullable=False, index=True)  # 6-digit code
    qr_payload = Column(Text)  # Signed JWT for QR scanning
    method = Column(Enum(ApprovalMethod), default=ApprovalMethod.PUSH)

    # Status tracking
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING, index=True)

    # Application context
    app_id = Column(String(100))  # Which app/service initiated the request
    request_description = Column(Text)  # Human-readable description
    request_description_ar = Column(Text)  # Arabic description

    # Device information (requester)
    device_info = Column(JSON)  # Device name, type, OS version
    device_fingerprint = Column(String(255))
    user_agent = Column(String(500))

    # Location information (requester)
    ip_address = Column(String(45))
    geolocation = Column(JSON)  # {lat, lng, accuracy, address}

    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=False)
    resolved_at = Column(DateTime)

    # Resolution details
    resolved_by = Column(Integer, ForeignKey("users.id"))
    resolution_reason = Column(Text)
    resolution_reason_ar = Column(Text)  # Arabic reason

    # Owner device info (when approved/denied)
    owner_device_info = Column(JSON)
    owner_ip_address = Column(String(45))
    owner_geolocation = Column(JSON)

    # Additional metadata
    metadata = Column(JSON)  # Any additional context data
    notification_sent = Column(Boolean, default=False)
    notification_sent_at = Column(DateTime)
    reminder_count = Column(Integer, default=0)

    # Relationships
    requester = relationship("User", foreign_keys=[requester_id], backref="approval_requests")
    resolver = relationship("User", foreign_keys=[resolved_by], backref="resolved_approvals")

    @staticmethod
    def generate_approval_code() -> str:
        """Generate a secure 6-digit approval code"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(6)])

    @staticmethod
    def default_expiration() -> datetime:
        """Default expiration is 10 minutes from now"""
        return datetime.utcnow() + timedelta(minutes=10)

    def is_expired(self) -> bool:
        """Check if the approval request has expired"""
        return datetime.utcnow() > self.expires_at

    def is_pending(self) -> bool:
        """Check if the approval is still pending"""
        return self.status == ApprovalStatus.PENDING and not self.is_expired()

    def to_notification_payload(self) -> dict:
        """Generate payload for TSH NeuroLink notification"""
        return {
            "type": "owner_approval_request",
            "approval_id": self.id,
            "approval_type": self.approval_type.value,
            "risk_level": self.risk_level.value,
            "requester_id": self.requester_id,
            "description": self.request_description,
            "description_ar": self.request_description_ar,
            "approval_code": self.approval_code,
            "expires_at": self.expires_at.isoformat(),
            "created_at": self.created_at.isoformat(),
            "device_info": self.device_info,
            "ip_address": self.ip_address,
            "geolocation": self.geolocation
        }

    def __repr__(self):
        return f"<OwnerApproval(id={self.id}, type={self.approval_type.value}, status={self.status.value})>"


# === APPROVAL AUDIT LOG ===

class ApprovalAuditLog(Base):
    """
    Audit trail for all approval-related actions

    Tracks every action taken on approval requests for
    compliance and security monitoring.
    """
    __tablename__ = "approval_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    approval_id = Column(String(36), ForeignKey("owner_approvals.id"), nullable=False)

    # Action details
    action = Column(String(100), nullable=False, index=True)  # created, viewed, approved, denied, expired
    actor_id = Column(Integer, ForeignKey("users.id"))

    # Context
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    device_info = Column(JSON)
    geolocation = Column(JSON)

    # Details
    old_status = Column(Enum(ApprovalStatus))
    new_status = Column(Enum(ApprovalStatus))
    notes = Column(Text)

    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    approval = relationship("OwnerApproval", backref="audit_logs")
    actor = relationship("User", foreign_keys=[actor_id])

    def __repr__(self):
        return f"<ApprovalAuditLog(approval_id={self.approval_id}, action={self.action})>"


# === OWNER SECURITY SETTINGS ===

class OwnerSecuritySettings(Base):
    """
    Security settings specific to Owner/Director role

    Configures approval requirements and notification preferences.
    """
    __tablename__ = "owner_security_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Approval settings
    require_biometric = Column(Boolean, default=True)  # Require Face ID/Touch ID
    auto_approve_low_risk = Column(Boolean, default=False)  # Auto-approve low risk
    default_expiration_minutes = Column(Integer, default=10)
    max_pending_approvals = Column(Integer, default=10)

    # Notification preferences
    enable_push_notifications = Column(Boolean, default=True)
    enable_sms_notifications = Column(Boolean, default=False)
    enable_email_notifications = Column(Boolean, default=True)
    quiet_hours_start = Column(String(5))  # "22:00" format
    quiet_hours_end = Column(String(5))    # "07:00" format
    emergency_override_quiet_hours = Column(Boolean, default=True)

    # Security restrictions
    allowed_approval_ips = Column(JSON)  # List of allowed IPs
    require_geofence = Column(Boolean, default=False)
    allowed_locations = Column(JSON)  # Geofence coordinates

    # Session settings
    session_timeout_minutes = Column(Integer, default=30)
    max_concurrent_sessions = Column(Integer, default=2)

    # Audit settings
    log_all_views = Column(Boolean, default=True)
    retain_audit_days = Column(Integer, default=365)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="owner_security_settings")

    def __repr__(self):
        return f"<OwnerSecuritySettings(user_id={self.user_id})>"
