"""
TSH NeuroLink - Pydantic Schemas
Request/Response models for API validation
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr


# ============================================================================
# EVENT SCHEMAS
# ============================================================================

class EventCreate(BaseModel):
    """Schema for creating a new event"""

    # TSH ERP Integration (optional - filled by auth middleware)
    branch_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    user_id: Optional[int] = None
    company_id: Optional[int] = None

    # Event Classification
    source_module: str = Field(..., description="Source module (e.g., 'sales', 'inventory')")
    event_type: str = Field(..., description="Event type (e.g., 'invoice.overdue')")
    severity: str = Field(default="info", description="Severity level")

    # Event Data
    occurred_at: datetime = Field(..., description="When the event occurred")
    payload: Dict[str, Any] = Field(..., description="Event payload")

    # Idempotency
    correlation_id: Optional[str] = Field(None, description="Correlation ID for related events")
    producer_idempotency_key: str = Field(..., description="Unique key to prevent duplicates")

    # Metadata
    tags: Optional[List[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "source_module": "invoicing",
                "event_type": "invoice.overdue",
                "severity": "warning",
                "occurred_at": "2024-10-31T10:00:00Z",
                "payload": {
                    "invoice_id": 12345,
                    "invoice_number": "INV-2024-001",
                    "customer_name": "Acme Corp",
                    "amount": 50000,
                    "currency": "IQD",
                    "days_overdue": 7
                },
                "producer_idempotency_key": "invoice_12345_overdue_20241031",
                "correlation_id": "order_flow_98765",
                "tags": ["finance", "urgent"]
            }
        }


class EventResponse(BaseModel):
    """Schema for event response"""

    id: UUID
    source_module: str
    event_type: str
    severity: str
    occurred_at: datetime
    payload: Dict[str, Any]
    correlation_id: Optional[str]
    producer_idempotency_key: Optional[str]
    tags: Optional[List[str]]
    ingested_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================================================
# NOTIFICATION SCHEMAS
# ============================================================================

class NotificationResponse(BaseModel):
    """Schema for notification response"""

    id: UUID
    event_id: UUID
    user_id: int
    branch_id: Optional[int]
    title: str
    body: str
    severity: str
    action_url: Optional[str]
    action_label: Optional[str]
    metadata: Optional[Dict[str, Any]]
    status: str
    channels: List[str]
    created_at: datetime
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]
    dismissed_at: Optional[datetime]
    group_key: Optional[str]

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Paginated notification list"""

    notifications: List[NotificationResponse]
    total: int
    unread_count: int
    page: int
    page_size: int


class NotificationMarkReadRequest(BaseModel):
    """Request to mark notification(s) as read"""

    notification_ids: List[UUID] = Field(..., description="List of notification IDs to mark as read")


class NotificationMarkAllReadResponse(BaseModel):
    """Response after marking all as read"""

    marked_count: int


# ============================================================================
# RULE SCHEMAS
# ============================================================================

class NotificationRuleCreate(BaseModel):
    """Schema for creating notification rule"""

    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    is_active: bool = True
    priority: int = 0
    source_module: Optional[str] = None
    event_type_pattern: Optional[str] = None
    condition_dsl: Optional[Dict[str, Any]] = None
    notification_template: Dict[str, Any] = Field(..., description="Template for creating notifications")
    cooldown_minutes: int = 0
    max_per_hour: Optional[int] = None


class NotificationRuleResponse(BaseModel):
    """Schema for notification rule response"""

    id: int
    name: str
    description: Optional[str]
    is_active: bool
    priority: int
    source_module: Optional[str]
    event_type_pattern: Optional[str]
    condition_dsl: Optional[Dict[str, Any]]
    notification_template: Dict[str, Any]
    cooldown_minutes: int
    max_per_hour: Optional[int]
    created_at: datetime
    updated_at: datetime
    version: int
    last_triggered_at: Optional[datetime]

    class Config:
        from_attributes = True


class NotificationRuleUpdate(BaseModel):
    """Schema for updating notification rule"""

    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None
    source_module: Optional[str] = None
    event_type_pattern: Optional[str] = None
    condition_dsl: Optional[Dict[str, Any]] = None
    notification_template: Optional[Dict[str, Any]] = None
    cooldown_minutes: Optional[int] = None
    max_per_hour: Optional[int] = None


# ============================================================================
# MESSAGE SCHEMAS (NeuroChat)
# ============================================================================

class MessageCreate(BaseModel):
    """Schema for creating a message"""

    event_id: Optional[UUID] = None
    notification_id: Optional[UUID] = None
    parent_message_id: Optional[UUID] = None
    content: str = Field(..., min_length=1, max_length=5000)
    attachments: Optional[List[Dict[str, Any]]] = None
    mentions: Optional[List[int]] = None


class MessageResponse(BaseModel):
    """Schema for message response"""

    id: UUID
    event_id: Optional[UUID]
    notification_id: Optional[UUID]
    parent_message_id: Optional[UUID]
    user_id: int
    user_name: Optional[str]
    content: str
    message_type: str
    attachments: Optional[List[Dict[str, Any]]]
    mentions: Optional[List[int]]
    is_resolved: bool
    resolved_by: Optional[int]
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# USER PREFERENCES SCHEMAS
# ============================================================================

class UserPreferencesResponse(BaseModel):
    """Schema for user preferences response"""

    user_id: int
    enabled_channels: List[str]
    email_enabled: bool
    sms_enabled: bool
    telegram_enabled: bool
    severity_filter: str
    quiet_hours_start: Optional[str]
    quiet_hours_end: Optional[str]
    quiet_hours_timezone: str
    module_settings: Optional[Dict[str, Any]]
    enable_batching: bool
    batch_interval_minutes: int
    updated_at: datetime

    class Config:
        from_attributes = True


class UserPreferencesUpdate(BaseModel):
    """Schema for updating user preferences"""

    enabled_channels: Optional[List[str]] = None
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    telegram_enabled: Optional[bool] = None
    severity_filter: Optional[str] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    quiet_hours_timezone: Optional[str] = None
    module_settings: Optional[Dict[str, Any]] = None
    enable_batching: Optional[bool] = None
    batch_interval_minutes: Optional[int] = None


# ============================================================================
# SYSTEM SCHEMAS
# ============================================================================

class HealthCheckResponse(BaseModel):
    """Health check response"""

    status: str
    version: str
    timestamp: datetime
    database: str
    redis: str


class SystemMetricsResponse(BaseModel):
    """System metrics response"""

    events_ingested_today: int
    notifications_sent_today: int
    active_users_today: int
    average_event_processing_time_ms: float
    redis_connected: bool
    database_connected: bool


# ============================================================================
# AUTHENTICATION SCHEMAS
# ============================================================================

class TokenData(BaseModel):
    """JWT token payload"""

    user_id: int
    email: str
    role: str
    branch_id: Optional[int] = None
    permissions: List[str] = []


class User(BaseModel):
    """User model for authentication"""

    id: int
    email: EmailStr
    full_name: Optional[str]
    role: str
    branch_id: Optional[int]
    is_active: bool

    class Config:
        from_attributes = True
