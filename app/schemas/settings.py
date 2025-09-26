# Enhanced Settings Schemas for Advanced ERP Features
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class BackupType(str, Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    DATABASE_ONLY = "database_only"
    CONFIGURATION = "configuration"

class BackupFrequency(str, Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class BackupCreateRequest(BaseModel):
    backup_type: BackupType = BackupType.FULL
    include_files: bool = True
    description: Optional[str] = None
    schedule_for_later: bool = False

class BackupScheduleRequest(BaseModel):
    frequency: BackupFrequency
    time: str = Field(..., description="Time in HH:MM format")
    days_of_week: Optional[List[int]] = Field(None, description="Days of week (0=Monday, 6=Sunday)")
    backup_type: BackupType = BackupType.FULL
    include_files: bool = True
    retention_days: int = Field(30, ge=1, le=365)
    
    @validator('time')
    def validate_time_format(cls, v):
        try:
            datetime.strptime(v, '%H:%M')
            return v
        except ValueError:
            raise ValueError('Time must be in HH:MM format')
    
    @validator('days_of_week')
    def validate_days_of_week(cls, v):
        if v is not None:
            for day in v:
                if not 0 <= day <= 6:
                    raise ValueError('Days of week must be between 0 (Monday) and 6 (Sunday)')
        return v

class BackupRestoreRequest(BaseModel):
    approver_ids: List[int] = Field(..., min_items=1)
    restore_point: Optional[datetime] = None
    target_environment: str = Field("current", description="Target environment for restore")
    confirmation_code: Optional[str] = Field(None, description="Confirmation code for critical restore")

class BackupInfo(BaseModel):
    name: str
    size_bytes: int
    created_at: datetime
    backup_type: BackupType
    encrypted: bool
    verification_status: str
    metadata: Optional[Dict[str, Any]] = None

class BackupListResponse(BaseModel):
    backups: List[BackupInfo]
    total_count: int
    total_size_bytes: int
    oldest_backup: Optional[datetime] = None
    newest_backup: Optional[datetime] = None

# Permission Management Schemas
class PermissionCondition(BaseModel):
    field: str
    operator: str = Field(..., pattern="^(eq|ne|in|not_in|gt|gte|lt|lte)$")
    value: Any

class GrantPermissionRequest(BaseModel):
    user_id: int
    permission_name: str
    conditions: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None
    reason: Optional[str] = None

class RevokePermissionRequest(BaseModel):
    user_id: int
    permission_name: str
    reason: Optional[str] = None

class UserPermissionInfo(BaseModel):
    name: str
    description: Optional[str]
    resource_type: str
    permission_type: str
    source: str  # "role" or "direct"
    granted: bool
    conditions: Optional[str] = None
    expires_at: Optional[datetime] = None

class UserPermissionsResponse(BaseModel):
    user_id: int
    permissions: List[UserPermissionInfo]
    role_name: Optional[str] = None

# Security and Audit Schemas
class AuditLogEntry(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    resource_type: str
    resource_id: Optional[str]
    timestamp: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None

class AuditLogResponse(BaseModel):
    logs: List[AuditLogEntry]
    total: int
    filters_applied: Dict[str, Any]
    generated_at: datetime

class SecurityAlert(BaseModel):
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    message: str
    detected_at: datetime
    user_id: Optional[int] = None
    ip_address: Optional[str] = None
    action_required: bool = False

class SuspiciousActivityResponse(BaseModel):
    risk_score: int = Field(..., ge=0, le=100)
    alerts: List[str]
    action_required: bool
    recommendations: List[str] = []

# Tenant Management Schemas
class TenantUsageStats(BaseModel):
    users_count: int
    branches_count: int
    storage_used_mb: float
    api_calls_today: int = 0
    last_activity: Optional[datetime] = None

class TenantLimits(BaseModel):
    max_users: int
    max_branches: int
    max_storage_gb: int
    max_api_calls_per_day: int = 10000

class TenantLimitsCheck(BaseModel):
    valid: bool
    violations: List[str]
    stats: TenantUsageStats
    limits: TenantLimits
    utilization_percent: Dict[str, float] = {}

class TenantInfo(BaseModel):
    id: int
    name: str
    code: str
    subdomain: str
    subscription_tier: str
    is_active: bool
    created_at: datetime
    usage_stats: TenantUsageStats
    limits_check: TenantLimitsCheck

# System Health and Performance Schemas
class DatabaseHealth(BaseModel):
    status: str
    connection_pool_size: int = 0
    active_connections: int = 0
    query_performance_ms: float = 0.0

class SystemResource(BaseModel):
    cpu_usage_percent: float
    memory_usage_percent: float
    disk_usage_percent: float
    network_io_mbps: float = 0.0

class SystemHealthResponse(BaseModel):
    overall_status: str = Field(..., pattern="^(healthy|warning|critical)$")
    database: DatabaseHealth
    resources: SystemResource
    services_status: Dict[str, str] = {}
    last_backup: Optional[datetime] = None
    uptime_hours: float = 0.0
    timestamp: datetime

class PerformanceMetrics(BaseModel):
    total_requests: int
    avg_response_time_ms: float
    error_rate_percent: float
    requests_per_minute: float
    peak_concurrent_users: int = 0
    cache_hit_rate_percent: float = 0.0

class PerformanceResponse(BaseModel):
    current_metrics: PerformanceMetrics
    historical_data: Dict[str, List[float]] = {}
    period_hours: int
    generated_at: datetime

# Configuration and Settings Schemas
class SystemConfiguration(BaseModel):
    maintenance_mode: bool = False
    max_upload_size_mb: int = 100
    session_timeout_minutes: int = 30
    password_policy: Dict[str, Any] = {}
    email_settings: Dict[str, str] = {}
    integration_settings: Dict[str, Any] = {}

class SystemConfigurationUpdate(BaseModel):
    maintenance_mode: Optional[bool] = None
    max_upload_size_mb: Optional[int] = Field(None, ge=1, le=1000)
    session_timeout_minutes: Optional[int] = Field(None, ge=5, le=1440)
    password_policy: Optional[Dict[str, Any]] = None
    email_settings: Optional[Dict[str, str]] = None
    integration_settings: Optional[Dict[str, Any]] = None

# API Response Schemas
class SettingsResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime

# Enhanced Settings Page Data
class SettingsPageData(BaseModel):
    system_info: SystemHealthResponse
    tenant_info: TenantInfo
    backup_info: BackupListResponse
    security_alerts: List[SecurityAlert] = []
    recent_activity: List[AuditLogEntry] = []
    performance_summary: PerformanceMetrics
    configuration: SystemConfiguration
