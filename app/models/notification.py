"""
TSH ERP Unified Notification System Models
Supports: Real-time, Push, In-app, Email notifications
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


class NotificationType(str, enum.Enum):
    """Types of notifications in the system"""
    # Inventory notifications
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    STOCK_MOVEMENT = "stock_movement"
    STOCK_ADJUSTMENT = "stock_adjustment"

    # Sales notifications
    NEW_ORDER = "new_order"
    ORDER_CONFIRMED = "order_confirmed"
    ORDER_SHIPPED = "order_shipped"
    ORDER_DELIVERED = "order_delivered"
    ORDER_CANCELLED = "order_cancelled"

    # Purchase notifications
    PURCHASE_ORDER_CREATED = "purchase_order_created"
    PURCHASE_ORDER_APPROVED = "purchase_order_approved"
    PURCHASE_ORDER_RECEIVED = "purchase_order_received"

    # Financial notifications
    INVOICE_CREATED = "invoice_created"
    INVOICE_PAID = "invoice_paid"
    INVOICE_OVERDUE = "invoice_overdue"
    PAYMENT_RECEIVED = "payment_received"

    # HR notifications
    LEAVE_REQUEST = "leave_request"
    LEAVE_APPROVED = "leave_approved"
    LEAVE_REJECTED = "leave_rejected"
    TIMESHEET_REMINDER = "timesheet_reminder"

    # System notifications
    SYSTEM_ALERT = "system_alert"
    SYSTEM_UPDATE = "system_update"
    BACKUP_COMPLETE = "backup_complete"
    BACKUP_FAILED = "backup_failed"

    # User notifications
    USER_MENTIONED = "user_mentioned"
    TASK_ASSIGNED = "task_assigned"
    APPROVAL_REQUEST = "approval_request"
    MESSAGE_RECEIVED = "message_received"

    # Custom
    CUSTOM = "custom"


class NotificationPriority(str, enum.Enum):
    """Priority levels for notifications"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationChannel(str, enum.Enum):
    """Channels through which notifications can be sent"""
    IN_APP = "in_app"          # In-app notification center
    PUSH = "push"              # Mobile push notification (FCM)
    EMAIL = "email"            # Email notification
    SMS = "sms"                # SMS notification
    WEBSOCKET = "websocket"    # Real-time WebSocket


class Notification(Base):
    """Main notification model - stores all notifications"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    # User and tenant
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    tenant_id = Column(Integer, nullable=True, index=True)  # Foreign key removed (tenants table disabled)

    # Notification details
    type = Column(Enum(NotificationType), nullable=False, index=True)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.MEDIUM)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    # Rich content
    image_url = Column(String(500), nullable=True)
    icon = Column(String(100), nullable=True)  # Icon name or emoji
    color = Column(String(20), nullable=True)  # Hex color code

    # Action buttons and deep linking
    action_url = Column(String(500), nullable=True)  # Deep link or URL
    action_label = Column(String(100), nullable=True)  # Button text
    actions = Column(JSON, nullable=True)  # Multiple actions: [{"label": "View", "url": "/orders/123"}]

    # Metadata (using meta_data to avoid conflict with SQLAlchemy's reserved 'metadata')
    meta_data = Column(JSON, nullable=True)  # Additional data: {"order_id": 123, "amount": 1500}

    # Status tracking
    is_read = Column(Boolean, default=False, index=True)
    is_archived = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime, nullable=True)

    # Delivery tracking
    channels = Column(JSON, nullable=False, default=["in_app"])  # ["in_app", "push", "email"]
    sent_via = Column(JSON, nullable=True)  # Track which channels were actually used
    delivery_status = Column(JSON, nullable=True)  # {"push": "delivered", "email": "sent"}

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # Auto-delete after this date

    # Related entities (for filtering and grouping)
    related_entity_type = Column(String(50), nullable=True, index=True)  # "order", "invoice", "product"
    related_entity_id = Column(Integer, nullable=True, index=True)

    # Relationships
    user = relationship("User", backref="notifications")
    # Tenant relationship disabled (multi-tenancy not used in unified database)
    # tenant = relationship("Tenant", backref="notifications")


class NotificationTemplate(Base):
    """Templates for consistent notification formatting"""
    __tablename__ = "notification_templates"

    id = Column(Integer, primary_key=True, index=True)

    # Template identification
    code = Column(String(100), unique=True, nullable=False, index=True)  # "low_stock_alert"
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Template content (supports variables like {product_name}, {quantity})
    title_template = Column(String(500), nullable=False)
    message_template = Column(Text, nullable=False)

    # Default settings
    type = Column(Enum(NotificationType), nullable=False)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.MEDIUM)
    default_channels = Column(JSON, default=["in_app"])  # Default delivery channels

    # Styling
    icon = Column(String(100), nullable=True)
    color = Column(String(20), nullable=True)

    # Actions
    default_action_url = Column(String(500), nullable=True)
    default_action_label = Column(String(100), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NotificationPreference(Base):
    """User preferences for notification delivery"""
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)

    # Global settings
    enabled = Column(Boolean, default=True)
    quiet_hours_enabled = Column(Boolean, default=False)
    quiet_hours_start = Column(String(5), nullable=True)  # "22:00"
    quiet_hours_end = Column(String(5), nullable=True)    # "08:00"

    # Channel preferences
    enable_in_app = Column(Boolean, default=True)
    enable_push = Column(Boolean, default=True)
    enable_email = Column(Boolean, default=True)
    enable_sms = Column(Boolean, default=False)

    # Type-specific preferences (JSON: {"low_stock": {"push": true, "email": false}})
    type_preferences = Column(JSON, nullable=True)

    # Priority filtering
    min_priority = Column(Enum(NotificationPriority), default=NotificationPriority.LOW)

    # Device tokens for push notifications
    fcm_tokens = Column(JSON, nullable=True)  # ["token1", "token2"]
    apns_tokens = Column(JSON, nullable=True)  # ["token1", "token2"]

    # Email settings
    email_address = Column(String(255), nullable=True)
    email_digest_enabled = Column(Boolean, default=False)
    email_digest_frequency = Column(String(20), default="daily")  # "realtime", "hourly", "daily"

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="notification_preference")


class NotificationGroup(Base):
    """Group notifications together (e.g., "5 new orders")"""
    __tablename__ = "notification_groups"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Group details
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String(255), nullable=False)
    count = Column(Integer, default=1)

    # Status
    is_read = Column(Boolean, default=False)
    is_expanded = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_notification_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")


class NotificationLog(Base):
    """Audit log for notification delivery"""
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)

    notification_id = Column(Integer, ForeignKey("notifications.id"), nullable=False, index=True)

    # Delivery details
    channel = Column(Enum(NotificationChannel), nullable=False)
    status = Column(String(50), nullable=False)  # "sent", "delivered", "failed", "clicked"

    # Error tracking
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)

    # External IDs (from push notification services, email providers, etc.)
    external_id = Column(String(255), nullable=True)

    # Metadata (using meta_data to avoid conflict with SQLAlchemy's reserved 'metadata')
    meta_data = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    notification = relationship("Notification", backref="logs")
