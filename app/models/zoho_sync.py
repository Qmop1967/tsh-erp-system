"""
Zoho Sync - Database Models
SQLAlchemy ORM models for Zoho Books integration and synchronization
(Moved from TDS Core - now unified with main ERP)
"""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
import enum

from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Text,
    Enum, ForeignKey, Index, CheckConstraint, JSON
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


# ============================================================================
# ENUMS (matching PostgreSQL custom types)
# ============================================================================

class EventStatus(str, enum.Enum):
    """Event processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"
    DEAD_LETTER = "dead_letter"


class SourceType(str, enum.Enum):
    """Source system type"""
    ZOHO = "zoho"
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    RECONCILIATION = "reconciliation"


class EntityType(str, enum.Enum):
    """Entity type being synchronized"""
    PRODUCT = "product"
    CUSTOMER = "customer"
    INVOICE = "invoice"
    BILL = "bill"
    CREDIT_NOTE = "credit_note"
    STOCK_ADJUSTMENT = "stock_adjustment"
    PRICE_LIST = "price_list"
    BRANCH = "branch"
    USER = "USER"  # Uppercase to match webhook processor
    ORDER = "order"
    PAYMENT = "PAYMENT"  # Customer payments (uppercase to match webhook processor)
    VENDOR = "VENDOR"  # Vendors/suppliers (uppercase)
    SUPPLIER = "SUPPLIER"  # Alternate key for vendors


class AlertSeverity(str, enum.Enum):
    """Alert severity level"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class OperationType(str, enum.Enum):
    """Sync operation type"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    UPSERT = "upsert"


# ============================================================================
# INBOX - Raw Event Staging
# ============================================================================

class TDSInboxEvent(Base):
    """
    Raw incoming events quarantine table
    All webhooks land here first for validation before processing
    Auto-cleanup after 7 days (configurable)
    """
    __tablename__ = "tds_inbox_events"

    # Primary Key
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Source Information
    source_type = Column(Enum(SourceType, name="tds_source_type", values_callable=lambda x: [e.value for e in x]), nullable=False, index=True)
    entity_type = Column(Enum(EntityType, name="tds_entity_type", values_callable=lambda x: [e.value for e in x]), nullable=False, index=True)
    source_entity_id = Column(Text, nullable=False, index=True)

    # Payload
    raw_payload = Column(JSONB, nullable=False)

    # Deduplication
    idempotency_key = Column(Text, unique=True, index=True)
    content_hash = Column(Text, nullable=False, index=True)

    # Metadata
    webhook_headers = Column(JSONB)
    signature_verified = Column(Boolean, default=False)
    ip_address = Column(String(45))

    # Timestamps
    received_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    processed_at = Column(DateTime(timezone=True))

    # Processing Status
    is_valid = Column(Boolean, default=False)
    validation_errors = Column(JSONB)
    moved_to_queue = Column(Boolean, default=False)

    # Indexes
    __table_args__ = (
        Index('idx_inbox_source_entity', 'source_type', 'source_entity_id'),
        Index('idx_inbox_received_at', 'received_at'),
        Index('idx_inbox_content_hash', 'content_hash'),
    )

    def __repr__(self):
        return f"<TDSInboxEvent(id={self.id}, entity_type={self.entity_type}, source_id={self.source_entity_id})>"


# ============================================================================
# SYNC QUEUE - Validated Events Ready for Processing
# ============================================================================

class TDSSyncQueue(Base):
    """
    Validated events ready for synchronization
    Main processing queue with retry logic and distributed locking
    """
    __tablename__ = "tds_sync_queue"

    # Primary Key
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign Keys
    inbox_event_id = Column(PG_UUID(as_uuid=True), ForeignKey("tds_inbox_events.id"), nullable=False, index=True)
    sync_run_id = Column(PG_UUID(as_uuid=True), ForeignKey("tds_sync_runs.id"), index=True)

    # Entity Information
    entity_type = Column(Enum(EntityType, name="tds_entity_type", values_callable=lambda x: [e.value for e in x]), nullable=False, index=True)
    source_entity_id = Column(Text, nullable=False, index=True)
    operation_type = Column(Enum(OperationType, name="tds_operation_type", values_callable=lambda x: [e.value for e in x]), nullable=False)

    # Payload
    validated_payload = Column(JSONB, nullable=False)

    # Processing State
    status = Column(
        Enum(EventStatus, name="tds_event_status", values_callable=lambda x: [e.value for e in x]),
        default=EventStatus.PENDING,
        nullable=False,
        index=True
    )
    priority = Column(Integer, default=5, nullable=False, index=True)

    # Retry Logic
    attempt_count = Column(Integer, default=0, nullable=False)
    max_retry_attempts = Column(Integer, default=3, nullable=False)
    next_retry_at = Column(DateTime(timezone=True), index=True)

    # Distributed Lock
    locked_by = Column(Text)
    lock_expires_at = Column(DateTime(timezone=True), index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    # Results
    target_entity_id = Column(Text)
    processing_result = Column(JSONB)
    error_message = Column(Text)
    error_code = Column(String(50))

    # Relationships
    inbox_event = relationship("TDSInboxEvent", backref="queue_entries")
    sync_run = relationship("TDSSyncRun", backref="queue_entries")

    # Indexes
    __table_args__ = (
        Index('idx_queue_status_priority', 'status', 'priority', 'created_at'),
        Index('idx_queue_entity', 'entity_type', 'source_entity_id'),
        Index('idx_queue_lock', 'locked_by', 'lock_expires_at'),
        Index('idx_queue_retry', 'next_retry_at'),
        CheckConstraint('attempt_count >= 0', name='check_attempt_count_positive'),
        CheckConstraint('priority BETWEEN 1 AND 10', name='check_priority_range'),
    )

    def __repr__(self):
        return f"<TDSSyncQueue(id={self.id}, entity={self.entity_type}, status={self.status})>"


# ============================================================================
# SYNC RUNS - Batch Execution Metadata
# ============================================================================

class TDSSyncRun(Base):
    """
    Batch synchronization run metadata
    Tracks execution of sync batches for performance monitoring
    """
    __tablename__ = "tds_sync_runs"

    # Primary Key
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Run Information
    run_type = Column(Enum(SourceType, name="tds_source_type", values_callable=lambda x: [e.value for e in x]), nullable=False, index=True)
    entity_type = Column(Enum(EntityType, name="tds_entity_type", values_callable=lambda x: [e.value for e in x]), index=True)

    # Execution
    status = Column(
        Enum(EventStatus, name="tds_event_status", values_callable=lambda x: [e.value for e in x]),
        default=EventStatus.PENDING,
        nullable=False,
        index=True
    )
    worker_id = Column(Text)

    # Statistics
    total_events = Column(Integer, default=0, nullable=False)
    processed_events = Column(Integer, default=0, nullable=False)
    failed_events = Column(Integer, default=0, nullable=False)
    skipped_events = Column(Integer, default=0, nullable=False)

    # Timing
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)

    # Metadata
    configuration_snapshot = Column(JSONB)
    error_summary = Column(JSONB)

    # Indexes
    __table_args__ = (
        Index('idx_runs_status_started', 'status', 'started_at'),
        Index('idx_runs_type', 'run_type', 'entity_type', 'started_at'),
    )

    def __repr__(self):
        return f"<TDSSyncRun(id={self.id}, type={self.run_type}, status={self.status})>"


# ============================================================================
# SYNC LOGS - Detailed Audit Trail
# ============================================================================

class TDSSyncLog(Base):
    """
    Detailed synchronization audit trail
    Immutable log of all sync operations for compliance and debugging
    Auto-cleanup after 90 days (configurable)
    """
    __tablename__ = "tds_sync_logs"

    # Primary Key
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign Keys
    sync_queue_id = Column(PG_UUID(as_uuid=True), ForeignKey("tds_sync_queue.id"), nullable=False, index=True)
    sync_run_id = Column(PG_UUID(as_uuid=True), ForeignKey("tds_sync_runs.id"), index=True)

    # Entity Information
    entity_type = Column(Enum(EntityType, name="tds_entity_type", values_callable=lambda x: [e.value for e in x]), nullable=False, index=True)
    source_entity_id = Column(Text, nullable=False, index=True)
    target_entity_id = Column(Text, index=True)

    # Operation
    operation_type = Column(Enum(OperationType, name="tds_operation_type", values_callable=lambda x: [e.value for e in x]), nullable=False)
    operation_status = Column(
        Enum(EventStatus, name="tds_event_status", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True
    )

    # Payloads
    input_payload = Column(JSONB)
    output_payload = Column(JSONB)

    # Execution
    attempt_number = Column(Integer, nullable=False)
    execution_time_ms = Column(Integer)
    error_message = Column(Text)
    error_code = Column(String(50))
    stack_trace = Column(Text)

    # Metadata
    worker_id = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Context
    context_data = Column(JSONB)

    # Relationships
    sync_queue = relationship("TDSSyncQueue", backref="logs")
    sync_run = relationship("TDSSyncRun", backref="logs")

    # Indexes
    __table_args__ = (
        Index('idx_logs_entity', 'entity_type', 'source_entity_id'),
        Index('idx_logs_status_timestamp', 'operation_status', 'timestamp'),
        Index('idx_logs_timestamp', 'timestamp'),
    )

    def __repr__(self):
        return f"<TDSSyncLog(id={self.id}, entity={self.entity_type}, status={self.operation_status})>"


# ============================================================================
# DEAD LETTER QUEUE - Failed Events
# ============================================================================

class TDSDeadLetterQueue(Base):
    """
    Failed events requiring manual investigation
    Quarantine for events that exceeded max retry attempts
    """
    __tablename__ = "tds_dead_letter_queue"

    # Primary Key
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign Key
    sync_queue_id = Column(PG_UUID(as_uuid=True), ForeignKey("tds_sync_queue.id"), nullable=False, index=True)

    # Entity Information
    entity_type = Column(Enum(EntityType, name="tds_entity_type", values_callable=lambda x: [e.value for e in x]), nullable=False, index=True)
    source_entity_id = Column(Text, nullable=False, index=True)

    # Failure Information
    failure_reason = Column(Text, nullable=False)
    error_code = Column(String(50))
    total_attempts = Column(Integer, nullable=False)
    last_error_message = Column(Text)
    last_stack_trace = Column(Text)

    # Payload
    last_payload = Column(JSONB, nullable=False)

    # Resolution
    resolved = Column(Boolean, default=False, nullable=False, index=True)
    resolved_at = Column(DateTime(timezone=True))
    resolved_by = Column(Text)
    resolution_notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Investigation
    assigned_to = Column(Text)
    priority = Column(Integer, default=5)

    # Relationship
    sync_queue = relationship("TDSSyncQueue", backref="dlq_entries")

    # Indexes
    __table_args__ = (
        Index('idx_dlq_resolved', 'resolved', 'created_at'),
        Index('idx_dlq_entity', 'entity_type', 'source_entity_id'),
    )

    def __repr__(self):
        return f"<TDSDeadLetterQueue(id={self.id}, entity={self.entity_type}, resolved={self.resolved})>"


# ============================================================================
# SYNC CURSORS - Incremental Sync Checkpoints
# ============================================================================

class TDSSyncCursor(Base):
    """
    Cursor-based incremental synchronization checkpoints
    Tracks last successful sync point for each entity type
    """
    __tablename__ = "tds_sync_cursors"

    # Primary Key
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Cursor Identity
    source_type = Column(Enum(SourceType, name="tds_source_type", values_callable=lambda x: [e.value for e in x]), nullable=False)
    entity_type = Column(Enum(EntityType, name="tds_entity_type", values_callable=lambda x: [e.value for e in x]), nullable=False)

    # Cursor State
    last_sync_at = Column(DateTime(timezone=True), nullable=False, index=True)
    last_entity_id = Column(Text)
    last_entity_version = Column(Integer)
    cursor_value = Column(Text)

    # Statistics
    total_synced = Column(Integer, default=0, nullable=False)
    last_sync_count = Column(Integer, default=0)

    # Metadata
    last_sync_status = Column(
        Enum(EventStatus, name="tds_event_status", values_callable=lambda x: [e.value for e in x]),
        default=EventStatus.COMPLETED
    )
    sync_metadata = Column(JSONB)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_cursor_source_entity', 'source_type', 'entity_type', unique=True),
        Index('idx_cursor_last_sync', 'last_sync_at'),
    )

    def __repr__(self):
        return f"<TDSSyncCursor(source={self.source_type}, entity={self.entity_type}, last_sync={self.last_sync_at})>"


# ============================================================================
# AUDIT TRAIL - Immutable Change History
# ============================================================================

class TDSAuditTrail(Base):
    """
    Immutable audit trail of all data changes
    Complete change history for compliance and forensics
    """
    __tablename__ = "tds_audit_trail"

    # Primary Key
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Entity Information
    entity_type = Column(Enum(EntityType, name="tds_entity_type", values_callable=lambda x: [e.value for e in x]), nullable=False, index=True)
    entity_id = Column(Text, nullable=False, index=True)

    # Operation
    operation = Column(Enum(OperationType, name="tds_operation_type", values_callable=lambda x: [e.value for e in x]), nullable=False)

    # Changes
    old_value = Column(JSONB)
    new_value = Column(JSONB)
    changed_fields = Column(JSONB)

    # Actor
    changed_by = Column(Text)
    change_source = Column(Enum(SourceType, name="tds_source_type", values_callable=lambda x: [e.value for e in x]))

    # Timestamp
    changed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Context
    sync_queue_id = Column(PG_UUID(as_uuid=True), ForeignKey("tds_sync_queue.id"), index=True)
    context = Column(JSONB)

    # Relationship
    sync_queue = relationship("TDSSyncQueue", backref="audit_entries")

    # Indexes
    __table_args__ = (
        Index('idx_audit_entity', 'entity_type', 'entity_id', 'changed_at'),
        Index('idx_audit_changed_at', 'changed_at'),
    )

    def __repr__(self):
        return f"<TDSAuditTrail(entity={self.entity_type}, id={self.entity_id}, op={self.operation})>"


# ============================================================================
# ALERTS - System Health Alerts
# ============================================================================

class TDSAlert(Base):
    """
    System health and performance alerts
    Tracks issues requiring attention
    """
    __tablename__ = "tds_alerts"

    # Primary Key
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Alert Information
    alert_type = Column(String(100), nullable=False, index=True)
    severity = Column(
        Enum(AlertSeverity, name="tds_alert_severity", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True
    )
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    # Context
    entity_type = Column(Enum(EntityType, name="tds_entity_type", values_callable=lambda x: [e.value for e in x]), index=True)
    affected_count = Column(Integer)
    threshold_value = Column(JSONB)
    actual_value = Column(JSONB)

    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    acknowledged = Column(Boolean, default=False)
    resolved = Column(Boolean, default=False, index=True)

    # Timestamps
    triggered_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    acknowledged_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))

    # Actor
    acknowledged_by = Column(Text)
    resolved_by = Column(Text)

    # Metadata
    alert_metadata = Column(JSONB)
    resolution_notes = Column(Text)

    # Indexes
    __table_args__ = (
        Index('idx_alerts_active', 'is_active', 'severity', 'triggered_at'),
        Index('idx_alerts_type', 'alert_type', 'triggered_at'),
    )

    def __repr__(self):
        return f"<TDSAlert(type={self.alert_type}, severity={self.severity}, active={self.is_active})>"


# ============================================================================
# METRICS - Performance Time-Series Data
# ============================================================================

class TDSMetric(Base):
    """
    Time-series performance metrics
    Tracks system health and performance over time
    """
    __tablename__ = "tds_metrics"

    # Primary Key
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Metric Identity
    metric_name = Column(String(100), nullable=False, index=True)
    metric_type = Column(String(50), nullable=False)

    # Dimensions
    entity_type = Column(Enum(EntityType, name="tds_entity_type", values_callable=lambda x: [e.value for e in x]), index=True)
    source_type = Column(Enum(SourceType, name="tds_source_type", values_callable=lambda x: [e.value for e in x]), index=True)

    # Values
    value = Column(JSONB, nullable=False)
    unit = Column(String(50))

    # Timestamp
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Metadata
    tags = Column(JSONB)
    dimensions = Column(JSONB)

    # Indexes
    __table_args__ = (
        Index('idx_metrics_name_time', 'metric_name', 'recorded_at'),
        Index('idx_metrics_entity', 'entity_type', 'recorded_at'),
        Index('idx_metrics_recorded', 'recorded_at'),
    )

    def __repr__(self):
        return f"<TDSMetric(name={self.metric_name}, value={self.value}, time={self.recorded_at})>"


# ============================================================================
# CONFIGURATION - Dynamic Runtime Configuration
# ============================================================================

class TDSConfiguration(Base):
    """
    Dynamic system configuration
    Allows runtime configuration changes without deployment
    """
    __tablename__ = "tds_configuration"

    # Primary Key
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Configuration
    config_key = Column(String(100), unique=True, nullable=False, index=True)
    config_value = Column(JSONB, nullable=False)
    value_type = Column(String(50), nullable=False)

    # Metadata
    description = Column(Text)
    category = Column(String(50), index=True)

    # Validation
    validation_schema = Column(JSONB)
    is_sensitive = Column(Boolean, default=False)

    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Version Control
    updated_by = Column(Text)
    version = Column(Integer, default=1, nullable=False)

    # Indexes
    __table_args__ = (
        Index('idx_config_key', 'config_key'),
        Index('idx_config_category', 'category', 'is_active'),
    )

    def __repr__(self):
        return f"<TDSConfiguration(key={self.config_key}, version={self.version})>"
