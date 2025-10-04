"""
Security Schemas for TSH ERP System
Pydantic models for security-related API endpoints
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum

# === ENUMS ===

class SecurityLevel(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"

class AccessAction(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    APPROVE = "approve"
    EXPORT = "export"
    IMPORT = "import"
    AUDIT = "audit"
    MANAGE = "manage"

class PolicyEffect(str, Enum):
    ALLOW = "allow"
    DENY = "deny"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"

class MFAType(str, Enum):
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    PUSH = "push"
    BIOMETRIC = "biometric"
    HARDWARE_TOKEN = "hardware_token"

# === SECURITY POLICY SCHEMAS ===

class SecurityPolicyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    policy_document: Dict[str, Any] = Field(...)
    effect: PolicyEffect = Field(...)
    priority: int = Field(default=500, ge=1, le=1000)
    applies_to_roles: Optional[List[int]] = Field(default=None)
    applies_to_users: Optional[List[int]] = Field(default=None)
    conditions: Optional[Dict[str, Any]] = Field(default=None)
    is_active: bool = Field(default=True)

    @validator('policy_document')
    def validate_policy_document(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Policy document must be a valid JSON object')
        if 'version' not in v:
            raise ValueError('Policy document must include a version field')
        if 'rules' not in v:
            raise ValueError('Policy document must include rules')
        return v

class SecurityPolicyCreate(SecurityPolicyBase):
    pass

class SecurityPolicyUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    policy_document: Optional[Dict[str, Any]] = Field(None)
    effect: Optional[PolicyEffect] = Field(None)
    priority: Optional[int] = Field(None, ge=1, le=1000)
    applies_to_roles: Optional[List[int]] = Field(None)
    applies_to_users: Optional[List[int]] = Field(None)
    conditions: Optional[Dict[str, Any]] = Field(None)
    is_active: Optional[bool] = Field(None)

class SecurityPolicyResponse(SecurityPolicyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: int
    updated_by: Optional[int]

    class Config:
        from_attributes = True

# === RESTRICTION GROUP SCHEMAS ===

class RestrictionGroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    restrictions: Dict[str, Any] = Field(...)
    is_active: bool = Field(default=True)

class RestrictionGroupCreate(RestrictionGroupBase):
    pass

class RestrictionGroupUpdate(BaseModel):
    description: Optional[str] = Field(None, max_length=1000)
    restrictions: Optional[Dict[str, Any]] = Field(None)
    is_active: Optional[bool] = Field(None)

class RestrictionGroupResponse(RestrictionGroupBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: int
    updated_by: Optional[int]

    class Config:
        from_attributes = True

# === RLS RULE SCHEMAS ===

class RLSRuleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    table_name: str = Field(..., min_length=1, max_length=100)
    rule_expression: str = Field(..., min_length=1, max_length=2000)
    applies_to_actions: List[AccessAction] = Field(...)
    applies_to_roles: Optional[List[int]] = Field(default=None)
    applies_to_users: Optional[List[int]] = Field(default=None)
    conditions: Optional[Dict[str, Any]] = Field(default=None)
    is_active: bool = Field(default=True)

class RLSRuleCreate(RLSRuleBase):
    pass

class RLSRuleUpdate(BaseModel):
    description: Optional[str] = Field(None, max_length=1000)
    rule_expression: Optional[str] = Field(None, min_length=1, max_length=2000)
    applies_to_actions: Optional[List[AccessAction]] = Field(None)
    applies_to_roles: Optional[List[int]] = Field(None)
    applies_to_users: Optional[List[int]] = Field(None)
    conditions: Optional[Dict[str, Any]] = Field(None)
    is_active: Optional[bool] = Field(None)

class RLSRuleResponse(RLSRuleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: int
    updated_by: Optional[int]

    class Config:
        from_attributes = True

# === FLS RULE SCHEMAS ===

class FLSRuleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    table_name: str = Field(..., min_length=1, max_length=100)
    column_name: str = Field(..., min_length=1, max_length=100)
    is_visible: bool = Field(default=True)
    is_readable: bool = Field(default=True)
    is_writable: bool = Field(default=True)
    masking_pattern: Optional[str] = Field(None, max_length=100)
    requires_encryption: bool = Field(default=False)
    applies_to_roles: Optional[List[int]] = Field(default=None)
    applies_to_users: Optional[List[int]] = Field(default=None)
    conditions: Optional[Dict[str, Any]] = Field(default=None)
    is_active: bool = Field(default=True)

class FLSRuleCreate(FLSRuleBase):
    pass

class FLSRuleUpdate(BaseModel):
    description: Optional[str] = Field(None, max_length=1000)
    is_visible: Optional[bool] = Field(None)
    is_readable: Optional[bool] = Field(None)
    is_writable: Optional[bool] = Field(None)
    masking_pattern: Optional[str] = Field(None, max_length=100)
    requires_encryption: Optional[bool] = Field(None)
    applies_to_roles: Optional[List[int]] = Field(None)
    applies_to_users: Optional[List[int]] = Field(None)
    conditions: Optional[Dict[str, Any]] = Field(None)
    is_active: Optional[bool] = Field(None)

class FLSRuleResponse(FLSRuleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: int
    updated_by: Optional[int]

    class Config:
        from_attributes = True

# === MFA SCHEMAS ===

class MFADeviceBase(BaseModel):
    device_name: str = Field(..., min_length=1, max_length=100)
    device_type: MFAType = Field(...)
    is_primary: bool = Field(default=False)

class MFADeviceCreate(MFADeviceBase):
    pass

class MFADeviceResponse(MFADeviceBase):
    id: int
    user_id: int
    device_fingerprint: str
    last_used: Optional[datetime]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class MFAVerificationRequest(BaseModel):
    device_id: int
    verification_code: str = Field(..., min_length=4, max_length=10)
    challenge_id: Optional[str] = Field(None)

class MFAVerificationResponse(BaseModel):
    success: bool
    message: str
    remaining_attempts: Optional[int] = Field(None)
    next_challenge: Optional[Dict[str, Any]] = Field(None)

# === AUDIT LOG SCHEMAS ===

class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    user_email: Optional[str]
    session_id: Optional[str]
    action: str
    resource_type: str
    resource_id: Optional[str]
    resource_name: Optional[str]
    details: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    user_agent: Optional[str]
    location_info: Optional[Dict[str, Any]]
    risk_score: Optional[float]
    risk_level: Optional[RiskLevel]
    timestamp: datetime
    success: bool
    error_message: Optional[str]

    class Config:
        from_attributes = True

# === SECURITY INCIDENT SCHEMAS ===

class SecurityIncidentResponse(BaseModel):
    id: int
    incident_type: str
    title: str
    description: str
    severity: str
    status: IncidentStatus
    affected_user_id: Optional[int]
    affected_resource: Optional[str]
    detection_method: str
    risk_score: float
    created_at: datetime
    updated_at: Optional[datetime]
    resolved_at: Optional[datetime]
    assigned_to: Optional[int]
    investigation_notes: Optional[str]

    class Config:
        from_attributes = True

# === USER SESSION SCHEMAS ===

class UserSessionResponse(BaseModel):
    id: str
    user_id: int
    device_info: Optional[Dict[str, Any]]
    location_info: Optional[Dict[str, Any]]
    risk_score: float
    is_active: bool
    last_activity: datetime
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True

# === DASHBOARD SCHEMAS ===

class SecurityDashboardResponse(BaseModel):
    active_sessions: int
    failed_logins_24h: int
    open_incidents: int
    mfa_devices: int
    high_risk_sessions: int
    policy_violations_7d: int
    recent_audits: List[AuditLogResponse]
    system_health: str

class RiskAssessmentResponse(BaseModel):
    overall_risk_score: float
    risk_level: RiskLevel
    active_threats: List[Dict[str, Any]]
    risk_factors: Dict[str, float]
    recommendations: List[str]
    assessment_timestamp: datetime

# === ACCESS CONTROL SCHEMAS ===

class AccessRequestBase(BaseModel):
    user_id: int
    resource_type: str
    resource_id: str
    action: AccessAction
    context: Optional[Dict[str, Any]] = Field(default=None)

class AccessRequestCreate(AccessRequestBase):
    pass

class AccessEvaluationResponse(BaseModel):
    allowed: bool
    decision: str
    reason: str
    policies_evaluated: List[str]
    risk_score: float
    required_mfa: Optional[List[MFAType]] = Field(None)
    conditions: Optional[Dict[str, Any]] = Field(None)
    timestamp: datetime

# === POLICY EVALUATION SCHEMAS ===

class PolicyEvaluationRequest(BaseModel):
    user_id: int
    action: AccessAction
    resource_type: str
    resource_id: Optional[str] = Field(None)
    context: Dict[str, Any] = Field(default_factory=dict)

class PolicyEvaluationResponse(BaseModel):
    decision: str
    matched_policies: List[Dict[str, Any]]
    risk_assessment: Dict[str, float]
    required_conditions: List[Dict[str, Any]]
    evaluation_time_ms: float
    timestamp: datetime

# === DEVICE MANAGEMENT SCHEMAS ===

class DeviceRegistrationRequest(BaseModel):
    device_name: str = Field(..., min_length=1, max_length=100)
    device_type: str = Field(..., min_length=1, max_length=50)
    device_info: Dict[str, Any] = Field(...)
    biometric_data: Optional[str] = Field(None)  # Encrypted
    push_token: Optional[str] = Field(None)

class DeviceRegistrationResponse(BaseModel):
    device_id: int
    registration_token: str
    qr_code_url: str
    setup_instructions: List[str]
    expires_at: datetime

class DeviceSessionResponse(BaseModel):
    id: str
    device_id: int
    user_id: int
    session_token: str
    location_info: Optional[Dict[str, Any]]
    is_active: bool
    risk_score: float
    last_activity: datetime
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True

# === NOTIFICATION SCHEMAS ===

class SecurityNotificationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    notification_type: str = Field(..., min_length=1, max_length=50)
    priority: str = Field(default="medium")
    channels: List[str] = Field(default=["push"])

class SecurityNotificationCreate(SecurityNotificationBase):
    user_ids: List[int] = Field(...)

class SecurityNotificationResponse(SecurityNotificationBase):
    id: int
    user_id: int
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime]

    class Config:
        from_attributes = True

# === BIOMETRIC SCHEMAS ===

class BiometricRegistrationRequest(BaseModel):
    biometric_type: str = Field(..., regex="^(fingerprint|face|voice|iris)$")
    biometric_data: str = Field(...)  # Base64 encoded encrypted data
    device_id: int = Field(...)

class BiometricVerificationRequest(BaseModel):
    biometric_type: str = Field(..., regex="^(fingerprint|face|voice|iris)$")
    biometric_data: str = Field(...)  # Base64 encoded encrypted data
    device_id: int = Field(...)
    challenge_id: str = Field(...)

class BiometricVerificationResponse(BaseModel):
    success: bool
    confidence_score: float
    message: str
    session_token: Optional[str] = Field(None)

# === PASSLESS AUTHENTICATION SCHEMAS ===

class PasslessAuthRequest(BaseModel):
    identifier: str = Field(...)  # Email or username
    device_fingerprint: str = Field(...)
    biometric_challenge: Optional[str] = Field(None)

class PasslessAuthResponse(BaseModel):
    challenge_id: str
    challenge_type: str
    challenge_data: Dict[str, Any]
    expires_at: datetime
    qr_code_url: Optional[str] = Field(None)

class PasslessAuthVerification(BaseModel):
    challenge_id: str = Field(...)
    verification_data: Dict[str, Any] = Field(...)

class PasslessAuthResult(BaseModel):
    success: bool
    access_token: Optional[str] = Field(None)
    refresh_token: Optional[str] = Field(None)
    user_info: Optional[Dict[str, Any]] = Field(None)
    session_id: Optional[str] = Field(None)
    message: str

# === COMPLIANCE SCHEMAS ===

class ComplianceReportRequest(BaseModel):
    report_type: str = Field(..., regex="^(gdpr|ccpa|sox|iso27001|custom)$")
    start_date: datetime = Field(...)
    end_date: datetime = Field(...)
    include_details: bool = Field(default=False)

class ComplianceReportResponse(BaseModel):
    report_id: str
    report_type: str
    period: Dict[str, datetime]
    summary: Dict[str, Any]
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    export_urls: Dict[str, str]  # Format -> URL mapping
    generated_at: datetime

# === SYSTEM CONFIGURATION SCHEMAS ===

class SecurityConfigUpdate(BaseModel):
    password_min_length: Optional[int] = Field(None, ge=8, le=128)
    session_timeout_minutes: Optional[int] = Field(None, ge=5, le=1440)
    mfa_required_for_admins: Optional[bool] = Field(None)
    failed_login_threshold: Optional[int] = Field(None, ge=3, le=20)
    rate_limit_requests_per_minute: Optional[int] = Field(None, ge=10, le=10000)
    audit_log_retention_days: Optional[int] = Field(None, ge=30, le=3650)
    geolocation_required: Optional[bool] = Field(None)
    risk_score_thresholds: Optional[Dict[str, float]] = Field(None)

class SecurityConfigResponse(BaseModel):
    current_config: Dict[str, Any]
    environment: str
    last_updated: datetime
    updated_by: int
