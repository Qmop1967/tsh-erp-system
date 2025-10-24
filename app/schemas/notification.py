"""
Pydantic schemas for TSH ERP Notification System
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.notification import NotificationType, NotificationPriority, NotificationChannel


# Notification Schemas

class NotificationAction(BaseModel):
    """Action button in notification"""
    label: str
    url: str
    style: Optional[str] = "primary"  # "primary", "secondary", "danger"


class NotificationBase(BaseModel):
    """Base notification schema"""
    title: str = Field(..., max_length=255)
    message: str
    type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM

    # Rich content
    image_url: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None

    # Actions
    action_url: Optional[str] = None
    action_label: Optional[str] = None
    actions: Optional[List[NotificationAction]] = None

    # Metadata
    meta_data: Optional[Dict[str, Any]] = None

    # Delivery
    channels: List[str] = ["in_app"]

    # Related entity
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None

    # Expiration
    expires_at: Optional[datetime] = None


class NotificationCreate(NotificationBase):
    """Create notification schema"""
    user_id: int
    tenant_id: Optional[int] = None


class NotificationBulkCreate(BaseModel):
    """Create notifications for multiple users"""
    user_ids: List[int]
    notification: NotificationBase
    tenant_id: Optional[int] = None


class NotificationUpdate(BaseModel):
    """Update notification schema"""
    is_read: Optional[bool] = None
    is_archived: Optional[bool] = None


class NotificationResponse(NotificationBase):
    """Notification response schema"""
    id: int
    user_id: int
    tenant_id: Optional[int]

    is_read: bool
    is_archived: bool
    read_at: Optional[datetime]

    sent_via: Optional[List[str]]
    delivery_status: Optional[Dict[str, str]]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Paginated notification list response"""
    notifications: List[NotificationResponse]
    total: int
    unread_count: int
    page: int
    page_size: int
    has_more: bool


# Notification Template Schemas

class NotificationTemplateBase(BaseModel):
    """Base template schema"""
    code: str = Field(..., max_length=100)
    name: str = Field(..., max_length=200)
    description: Optional[str] = None

    title_template: str = Field(..., max_length=500)
    message_template: str

    type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM
    default_channels: List[str] = ["in_app"]

    icon: Optional[str] = None
    color: Optional[str] = None

    default_action_url: Optional[str] = None
    default_action_label: Optional[str] = None

    is_active: bool = True


class NotificationTemplateCreate(NotificationTemplateBase):
    """Create template schema"""
    pass


class NotificationTemplateUpdate(BaseModel):
    """Update template schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    title_template: Optional[str] = None
    message_template: Optional[str] = None
    priority: Optional[NotificationPriority] = None
    default_channels: Optional[List[str]] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None


class NotificationTemplateResponse(NotificationTemplateBase):
    """Template response schema"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationFromTemplate(BaseModel):
    """Create notification from template"""
    template_code: str
    user_id: int
    variables: Dict[str, Any] = {}  # Template variables
    tenant_id: Optional[int] = None
    channels: Optional[List[str]] = None  # Override default channels
    meta_data: Optional[Dict[str, Any]] = None


# Notification Preference Schemas

class NotificationPreferenceBase(BaseModel):
    """Base preference schema"""
    enabled: bool = True
    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None

    enable_in_app: bool = True
    enable_push: bool = True
    enable_email: bool = True
    enable_sms: bool = False

    type_preferences: Optional[Dict[str, Dict[str, bool]]] = None
    min_priority: NotificationPriority = NotificationPriority.LOW

    email_address: Optional[str] = None
    email_digest_enabled: bool = False
    email_digest_frequency: str = "daily"


class NotificationPreferenceCreate(NotificationPreferenceBase):
    """Create preference schema"""
    user_id: int


class NotificationPreferenceUpdate(BaseModel):
    """Update preference schema"""
    enabled: Optional[bool] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None

    enable_in_app: Optional[bool] = None
    enable_push: Optional[bool] = None
    enable_email: Optional[bool] = None
    enable_sms: Optional[bool] = None

    type_preferences: Optional[Dict[str, Dict[str, bool]]] = None
    min_priority: Optional[NotificationPriority] = None

    email_address: Optional[str] = None
    email_digest_enabled: Optional[bool] = None
    email_digest_frequency: Optional[str] = None


class NotificationPreferenceResponse(NotificationPreferenceBase):
    """Preference response schema"""
    id: int
    user_id: int
    fcm_tokens: Optional[List[str]]
    apns_tokens: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DeviceTokenRequest(BaseModel):
    """Register/update device token"""
    token: str
    platform: str = Field(..., pattern="^(ios|android|web)$")
    device_id: Optional[str] = None


# Statistics and Analytics

class NotificationStats(BaseModel):
    """Notification statistics"""
    total_notifications: int
    unread_count: int
    read_count: int
    archived_count: int
    by_priority: Dict[str, int]
    by_type: Dict[str, int]
    recent_activity: List[Dict[str, Any]]


class NotificationSettingsResponse(BaseModel):
    """Complete notification settings response"""
    preferences: NotificationPreferenceResponse
    stats: NotificationStats
    available_types: List[Dict[str, str]]
    available_priorities: List[str]


# Bulk Operations

class BulkMarkAsRead(BaseModel):
    """Mark multiple notifications as read"""
    notification_ids: List[int]


class BulkDelete(BaseModel):
    """Delete multiple notifications"""
    notification_ids: List[int]


class BulkArchive(BaseModel):
    """Archive multiple notifications"""
    notification_ids: List[int]
