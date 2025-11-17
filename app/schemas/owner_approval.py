"""
Owner Approval Pydantic Schemas

Validation and serialization schemas for Owner Approval endpoints.
Includes Arabic field support for bilingual responses.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# === ENUMS FOR SCHEMAS ===

class ApprovalMethodSchema(str, Enum):
    PUSH = "push"
    QR = "qr"
    SMS = "sms"
    MANUAL = "manual"
    BIOMETRIC = "biometric"


class ApprovalStatusSchema(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ApprovalTypeSchema(str, Enum):
    LOGIN_SUSPICIOUS = "login_suspicious"
    HIGH_VALUE_TRANSACTION = "high_value_transaction"
    SENSITIVE_DATA_ACCESS = "sensitive_data_access"
    USER_ROLE_CHANGE = "user_role_change"
    SYSTEM_CONFIG_CHANGE = "system_config_change"
    BULK_OPERATION = "bulk_operation"
    DEVICE_TRUST = "device_trust"
    EMERGENCY_ACCESS = "emergency_access"
    FINANCIAL_REPORT = "financial_report"
    DATA_EXPORT = "data_export"


class RiskLevelSchema(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# === REQUEST SCHEMAS ===

class CreateApprovalRequest(BaseModel):
    """Request to create a new approval request"""
    approval_type: ApprovalTypeSchema
    risk_level: RiskLevelSchema = RiskLevelSchema.MEDIUM
    request_description: str = Field(..., min_length=10, max_length=1000)
    request_description_ar: Optional[str] = Field(None, max_length=1000)
    app_id: Optional[str] = Field(None, max_length=100)
    metadata: Optional[Dict[str, Any]] = None
    method: ApprovalMethodSchema = ApprovalMethodSchema.PUSH
    expiration_minutes: Optional[int] = Field(10, ge=1, le=60)

    class Config:
        json_schema_extra = {
            "example": {
                "approval_type": "high_value_transaction",
                "risk_level": "high",
                "request_description": "Transfer 5,000,000 IQD to vendor account",
                "request_description_ar": "تحويل 5,000,000 دينار عراقي إلى حساب المورد",
                "app_id": "tsh_accounting_app",
                "method": "push",
                "expiration_minutes": 10
            }
        }


class ApproveRequest(BaseModel):
    """Request to approve an approval request"""
    approval_code: str = Field(..., min_length=6, max_length=6, pattern=r'^\d{6}$')
    resolution_reason: Optional[str] = Field(None, max_length=500)
    resolution_reason_ar: Optional[str] = Field(None, max_length=500)
    biometric_verified: bool = False

    @validator('approval_code')
    def validate_code(cls, v):
        if not v.isdigit() or len(v) != 6:
            raise ValueError('Approval code must be exactly 6 digits')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "approval_code": "123456",
                "resolution_reason": "Approved after verification",
                "resolution_reason_ar": "تمت الموافقة بعد التحقق",
                "biometric_verified": True
            }
        }


class DenyRequest(BaseModel):
    """Request to deny an approval request"""
    resolution_reason: str = Field(..., min_length=10, max_length=500)
    resolution_reason_ar: Optional[str] = Field(None, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "resolution_reason": "Request denied due to suspicious activity",
                "resolution_reason_ar": "تم رفض الطلب بسبب نشاط مشبوه"
            }
        }


class QRScanRequest(BaseModel):
    """Request to approve via QR code scan"""
    qr_payload: str = Field(..., min_length=50)
    biometric_verified: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "qr_payload": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "biometric_verified": True
            }
        }


class DeviceInfoSchema(BaseModel):
    """Device information for tracking"""
    device_name: Optional[str] = None
    device_type: Optional[str] = None  # iOS, Android, Web
    device_model: Optional[str] = None
    os_version: Optional[str] = None
    app_version: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "device_name": "iPhone 15 Pro",
                "device_type": "iOS",
                "device_model": "iPhone15,3",
                "os_version": "17.0",
                "app_version": "1.0.0"
            }
        }


class GeolocationSchema(BaseModel):
    """Geolocation information"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy: Optional[float] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 33.3152,
                "longitude": 44.3661,
                "accuracy": 10.5,
                "address": "Al Karrada, Baghdad",
                "city": "Baghdad",
                "country": "Iraq"
            }
        }


# === RESPONSE SCHEMAS ===

class RequesterInfo(BaseModel):
    """Information about the requester"""
    id: int
    name: str
    email: str
    role: Optional[str] = None


class ApprovalResponse(BaseModel):
    """Complete approval request response"""
    id: str
    requester: RequesterInfo
    approval_type: ApprovalTypeSchema
    risk_level: RiskLevelSchema
    status: ApprovalStatusSchema
    method: ApprovalMethodSchema

    request_description: str
    request_description_ar: Optional[str] = None

    app_id: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    geolocation: Optional[Dict[str, Any]] = None

    created_at: datetime
    expires_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = None
    resolution_reason: Optional[str] = None
    resolution_reason_ar: Optional[str] = None

    is_expired: bool
    time_remaining_seconds: Optional[int] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "requester": {
                    "id": 5,
                    "name": "Ahmad Hassan",
                    "email": "ahmad@tsh.sale",
                    "role": "accountant"
                },
                "approval_type": "high_value_transaction",
                "risk_level": "high",
                "status": "pending",
                "method": "push",
                "request_description": "Transfer 5,000,000 IQD",
                "request_description_ar": "تحويل 5,000,000 دينار",
                "created_at": "2025-01-15T10:30:00Z",
                "expires_at": "2025-01-15T10:40:00Z",
                "is_expired": False,
                "time_remaining_seconds": 420
            }
        }


class ApprovalListResponse(BaseModel):
    """Paginated list of approvals"""
    approvals: List[ApprovalResponse]
    total: int
    page: int
    page_size: int
    has_more: bool

    class Config:
        json_schema_extra = {
            "example": {
                "approvals": [],
                "total": 25,
                "page": 1,
                "page_size": 20,
                "has_more": True
            }
        }


class ApprovalCreatedResponse(BaseModel):
    """Response after creating an approval request"""
    success: bool = True
    message: str
    message_ar: str
    approval_id: str
    approval_code: str
    expires_at: datetime
    notification_sent: bool

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Approval request created successfully",
                "message_ar": "تم إنشاء طلب الموافقة بنجاح",
                "approval_id": "550e8400-e29b-41d4-a716-446655440000",
                "approval_code": "123456",
                "expires_at": "2025-01-15T10:40:00Z",
                "notification_sent": True
            }
        }


class ApprovalActionResponse(BaseModel):
    """Response after approving/denying"""
    success: bool = True
    message: str
    message_ar: str
    approval_id: str
    new_status: ApprovalStatusSchema
    resolved_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Request approved successfully",
                "message_ar": "تمت الموافقة على الطلب بنجاح",
                "approval_id": "550e8400-e29b-41d4-a716-446655440000",
                "new_status": "approved",
                "resolved_at": "2025-01-15T10:35:00Z"
            }
        }


class QRCodeResponse(BaseModel):
    """Response containing QR code data"""
    success: bool = True
    approval_id: str
    qr_payload: str  # Signed JWT
    qr_data_url: Optional[str] = None  # Base64 encoded QR image
    expires_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "approval_id": "550e8400-e29b-41d4-a716-446655440000",
                "qr_payload": "eyJhbGciOiJIUzI1NiJ9...",
                "expires_at": "2025-01-15T10:40:00Z"
            }
        }


class ApprovalStatsResponse(BaseModel):
    """Statistics about approvals"""
    pending: int
    approved_today: int
    denied_today: int
    expired_today: int
    average_resolution_time_seconds: Optional[float] = None
    by_risk_level: Dict[str, int]
    by_type: Dict[str, int]

    class Config:
        json_schema_extra = {
            "example": {
                "pending": 3,
                "approved_today": 15,
                "denied_today": 2,
                "expired_today": 1,
                "average_resolution_time_seconds": 180.5,
                "by_risk_level": {
                    "low": 5,
                    "medium": 10,
                    "high": 4,
                    "critical": 1
                },
                "by_type": {
                    "high_value_transaction": 8,
                    "user_role_change": 4,
                    "sensitive_data_access": 3
                }
            }
        }


# === SECURITY SETTINGS SCHEMAS ===

class OwnerSecuritySettingsResponse(BaseModel):
    """Owner security settings"""
    require_biometric: bool
    auto_approve_low_risk: bool
    default_expiration_minutes: int
    max_pending_approvals: int
    enable_push_notifications: bool
    enable_sms_notifications: bool
    enable_email_notifications: bool
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    session_timeout_minutes: int
    max_concurrent_sessions: int

    class Config:
        from_attributes = True


class UpdateSecuritySettingsRequest(BaseModel):
    """Update security settings"""
    require_biometric: Optional[bool] = None
    auto_approve_low_risk: Optional[bool] = None
    default_expiration_minutes: Optional[int] = Field(None, ge=1, le=60)
    max_pending_approvals: Optional[int] = Field(None, ge=1, le=100)
    enable_push_notifications: Optional[bool] = None
    enable_sms_notifications: Optional[bool] = None
    enable_email_notifications: Optional[bool] = None
    quiet_hours_start: Optional[str] = Field(None, pattern=r'^\d{2}:\d{2}$')
    quiet_hours_end: Optional[str] = Field(None, pattern=r'^\d{2}:\d{2}$')
    session_timeout_minutes: Optional[int] = Field(None, ge=5, le=480)
    max_concurrent_sessions: Optional[int] = Field(None, ge=1, le=10)
