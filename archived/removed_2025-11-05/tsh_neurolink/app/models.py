"""
TSH NeuroLink - SQLAlchemy Models
ORM models for NeuroLink database tables
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, TIMESTAMP,
    ForeignKey, CheckConstraint, Index, ARRAY, Numeric
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class NeurolinkEvent(Base):
    """Business events from TSH ERP modules"""

    __tablename__ = "neurolink_events"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    # TSH ERP Integration
    tds_event_id = Column(PG_UUID(as_uuid=True), nullable=True)
    branch_id = Column(Integer, nullable=True)
    warehouse_id = Column(Integer, nullable=True)
    user_id = Column(Integer, nullable=True)
    company_id = Column(Integer, nullable=True)

    # Event Classification
    source_module = Column(String(100), nullable=False)
    event_type = Column(String(100), nullable=False)
    severity = Column(String(20), default="info")

    # Event Data
    occurred_at = Column(TIMESTAMP(timezone=True), nullable=False)
    payload = Column(JSONB, nullable=False)

    # Idempotency & Correlation
    correlation_id = Column(String(255), nullable=True)
    producer_idempotency_key = Column(String(255), unique=True, nullable=True)

    # Metadata
    tags = Column(ARRAY(Text), nullable=True)
    ingested_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    processed_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    notifications = relationship("NeurolinkNotification", back_populates="event")
    messages = relationship("NeurolinkMessage", back_populates="event")

    __table_args__ = (
        CheckConstraint(
            "severity IN ('info', 'warning', 'error', 'critical')",
            name="neurolink_events_severity_check"
        ),
        Index("idx_neurolink_events_branch_id", "branch_id"),
        Index("idx_neurolink_events_user_id", "user_id"),
        Index("idx_neurolink_events_source_module", "source_module"),
        Index("idx_neurolink_events_event_type", "event_type"),
        Index("idx_neurolink_events_occurred_at", "occurred_at"),
        Index("idx_neurolink_events_correlation_id", "correlation_id"),
    )


class NeurolinkNotificationRule(Base):
    """Rules for converting events into notifications"""

    __tablename__ = "neurolink_notification_rules"

    id = Column(Integer, primary_key=True)

    # Rule Identification
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)

    # Rule Matching
    source_module = Column(String(100), nullable=True)
    event_type_pattern = Column(String(255), nullable=True)
    condition_dsl = Column(JSONB, nullable=True)

    # Notification Template
    notification_template = Column(JSONB, nullable=False)

    # Rate Limiting
    cooldown_minutes = Column(Integer, default=0)
    max_per_hour = Column(Integer, nullable=True)

    # Metadata
    created_by = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Audit
    version = Column(Integer, default=1)
    last_triggered_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    notifications = relationship("NeurolinkNotification", back_populates="rule")

    __table_args__ = (
        Index("idx_neurolink_notification_rules_active", "is_active", "priority"),
        Index("idx_neurolink_notification_rules_event_type", "event_type_pattern"),
    )


class NeurolinkNotification(Base):
    """User-specific notifications"""

    __tablename__ = "neurolink_notifications"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Relationships
    event_id = Column(PG_UUID(as_uuid=True), ForeignKey("neurolink_events.id", ondelete="CASCADE"), nullable=False)
    rule_id = Column(Integer, ForeignKey("neurolink_notification_rules.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(Integer, nullable=False)
    branch_id = Column(Integer, nullable=True)

    # Content
    title = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    severity = Column(String(20), default="info")

    # Actions
    action_url = Column(String(500), nullable=True)
    action_label = Column(String(100), nullable=True)
    metadata = Column(JSONB, nullable=True)

    # Delivery
    status = Column(String(50), default="pending")
    channels = Column(ARRAY(Text), default=["in_app"])

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    delivered_at = Column(TIMESTAMP(timezone=True), nullable=True)
    read_at = Column(TIMESTAMP(timezone=True), nullable=True)
    dismissed_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Grouping
    group_key = Column(String(255), nullable=True)

    # Relationships
    event = relationship("NeurolinkEvent", back_populates="notifications")
    rule = relationship("NeurolinkNotificationRule", back_populates="notifications")
    messages = relationship("NeurolinkMessage", back_populates="notification")
    delivery_logs = relationship("NeurolinkDeliveryLog", back_populates="notification")

    __table_args__ = (
        CheckConstraint(
            "severity IN ('info', 'warning', 'error', 'critical')",
            name="neurolink_notifications_severity_check"
        ),
        CheckConstraint(
            "status IN ('pending', 'delivered', 'read', 'dismissed', 'failed')",
            name="neurolink_notifications_status_check"
        ),
        Index("idx_neurolink_notifications_user_id", "user_id", "created_at"),
        Index("idx_neurolink_notifications_status", "status", "created_at"),
        Index("idx_neurolink_notifications_branch_id", "branch_id"),
        Index("idx_neurolink_notifications_event_id", "event_id"),
        Index("idx_neurolink_notifications_group_key", "group_key"),
    )


class NeurolinkMessage(Base):
    """Contextual chat messages about events"""

    __tablename__ = "neurolink_messages"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Relationships
    event_id = Column(PG_UUID(as_uuid=True), ForeignKey("neurolink_events.id", ondelete="CASCADE"), nullable=True)
    notification_id = Column(PG_UUID(as_uuid=True), ForeignKey("neurolink_notifications.id", ondelete="CASCADE"), nullable=True)
    parent_message_id = Column(PG_UUID(as_uuid=True), ForeignKey("neurolink_messages.id", ondelete="CASCADE"), nullable=True)

    # Author
    user_id = Column(Integer, nullable=False)
    user_name = Column(String(255), nullable=True)

    # Content
    content = Column(Text, nullable=False)
    message_type = Column(String(50), default="user")

    # Attachments
    attachments = Column(JSONB, nullable=True)

    # Metadata
    mentions = Column(ARRAY(Integer), nullable=True)
    is_resolved = Column(Boolean, default=False)
    resolved_by = Column(Integer, nullable=True)
    resolved_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    event = relationship("NeurolinkEvent", back_populates="messages")
    notification = relationship("NeurolinkNotification", back_populates="messages")

    __table_args__ = (
        CheckConstraint(
            "message_type IN ('user', 'system', 'ai_assistant')",
            name="neurolink_messages_type_check"
        ),
        Index("idx_neurolink_messages_event_id", "event_id", "created_at"),
        Index("idx_neurolink_messages_notification_id", "notification_id", "created_at"),
        Index("idx_neurolink_messages_user_id", "user_id"),
        Index("idx_neurolink_messages_parent_id", "parent_message_id"),
    )


class NeurolinkDeliveryLog(Base):
    """Multi-channel delivery tracking"""

    __tablename__ = "neurolink_delivery_log"

    id = Column(Integer, primary_key=True)

    # Relationships
    notification_id = Column(PG_UUID(as_uuid=True), ForeignKey("neurolink_notifications.id", ondelete="CASCADE"), nullable=False)

    # Delivery Details
    channel = Column(String(50), nullable=False)
    recipient = Column(String(255), nullable=False)

    # Status
    status = Column(String(50), nullable=False)
    provider = Column(String(100), nullable=True)

    # Result
    error_message = Column(Text, nullable=True)
    provider_message_id = Column(String(255), nullable=True)

    # Metadata
    metadata = Column(JSONB, nullable=True)

    # Timestamps
    queued_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    sent_at = Column(TIMESTAMP(timezone=True), nullable=True)
    delivered_at = Column(TIMESTAMP(timezone=True), nullable=True)
    failed_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    notification = relationship("NeurolinkNotification", back_populates="delivery_logs")

    __table_args__ = (
        CheckConstraint(
            "channel IN ('email', 'sms', 'telegram', 'slack', 'webhook', 'push')",
            name="neurolink_delivery_log_channel_check"
        ),
        CheckConstraint(
            "status IN ('queued', 'sending', 'sent', 'delivered', 'failed', 'bounced')",
            name="neurolink_delivery_log_status_check"
        ),
        Index("idx_neurolink_delivery_log_notification_id", "notification_id"),
        Index("idx_neurolink_delivery_log_status", "status", "queued_at"),
        Index("idx_neurolink_delivery_log_channel", "channel", "status"),
    )


class NeurolinkUserPreferences(Base):
    """Per-user notification preferences"""

    __tablename__ = "neurolink_user_preferences"

    user_id = Column(Integer, primary_key=True)

    # Channel Preferences
    enabled_channels = Column(ARRAY(Text), default=["in_app"])
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    telegram_enabled = Column(Boolean, default=False)

    # Notification Settings
    severity_filter = Column(String(20), default="info")
    quiet_hours_start = Column(String(5), nullable=True)  # HH:MM format
    quiet_hours_end = Column(String(5), nullable=True)
    quiet_hours_timezone = Column(String(50), default="UTC")

    # Module Settings
    module_settings = Column(JSONB, nullable=True)

    # Batching
    enable_batching = Column(Boolean, default=False)
    batch_interval_minutes = Column(Integer, default=60)

    # Metadata
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint(
            "severity_filter IN ('info', 'warning', 'error', 'critical')",
            name="neurolink_user_preferences_severity_check"
        ),
    )


class NeurolinkMetric(Base):
    """System performance metrics"""

    __tablename__ = "neurolink_metrics"

    id = Column(Integer, primary_key=True)

    # Metric Details
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Numeric, nullable=False)
    metric_unit = Column(String(50), nullable=True)

    # Dimensions
    dimensions = Column(JSONB, nullable=True)

    # Timestamp
    recorded_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_neurolink_metrics_name", "metric_name", "recorded_at"),
        Index("idx_neurolink_metrics_recorded_at", "recorded_at"),
    )
