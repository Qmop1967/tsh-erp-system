"""
TDS Events - Domain Events for Data Synchronization
Integrates with the main event bus for decoupled communication
"""
from typing import Any, Dict, Optional
from uuid import UUID
from datetime import datetime

from app.core.events.base_event import DomainEvent


class TDSEvent(DomainEvent):
    """Base event for all TDS synchronization events"""

    def __init__(self, **data):
        if 'module' not in data:
            data['module'] = 'tds'
        super().__init__(**data)


class TDSSyncStartedEvent(TDSEvent):
    """
    Published when a sync operation starts

    Data:
        - sync_run_id: UUID of the sync run
        - entity_type: Type of entity being synced
        - source_type: Source of the sync (zoho, manual, etc.)
        - batch_size: Number of items in this sync
    """

    def __init__(
        self,
        sync_run_id: UUID,
        entity_type: str,
        source_type: str,
        batch_size: int = 0,
        **kwargs
    ):
        super().__init__(
            event_type="tds.sync.started",
            aggregate_type="TDSSyncRun",
            aggregate_id=str(sync_run_id),
            data={
                "sync_run_id": str(sync_run_id),
                "entity_type": entity_type,
                "source_type": source_type,
                "batch_size": batch_size,
            },
            **kwargs
        )


class TDSSyncCompletedEvent(TDSEvent):
    """
    Published when a sync operation completes successfully

    Data:
        - sync_run_id: UUID of the sync run
        - entity_type: Type of entity synced
        - total_processed: Total items processed
        - successful: Number of successful syncs
        - failed: Number of failed syncs
        - duration_seconds: Time taken
    """

    def __init__(
        self,
        sync_run_id: UUID,
        entity_type: str,
        total_processed: int,
        successful: int,
        failed: int,
        duration_seconds: float,
        **kwargs
    ):
        super().__init__(
            event_type="tds.sync.completed",
            aggregate_type="TDSSyncRun",
            aggregate_id=str(sync_run_id),
            data={
                "sync_run_id": str(sync_run_id),
                "entity_type": entity_type,
                "total_processed": total_processed,
                "successful": successful,
                "failed": failed,
                "duration_seconds": duration_seconds,
            },
            **kwargs
        )


class TDSSyncFailedEvent(TDSEvent):
    """
    Published when a sync operation fails

    Data:
        - sync_run_id: UUID of the sync run
        - entity_type: Type of entity being synced
        - error_message: Error description
        - error_code: Error code
    """

    def __init__(
        self,
        sync_run_id: UUID,
        entity_type: str,
        error_message: str,
        error_code: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            event_type="tds.sync.failed",
            aggregate_type="TDSSyncRun",
            aggregate_id=str(sync_run_id),
            data={
                "sync_run_id": str(sync_run_id),
                "entity_type": entity_type,
                "error_message": error_message,
                "error_code": error_code,
            },
            **kwargs
        )


class TDSEntitySyncedEvent(TDSEvent):
    """
    Published when a single entity is successfully synced

    Data:
        - entity_type: Type of entity (product, customer, etc.)
        - entity_id: Local entity ID
        - source_entity_id: Source system entity ID
        - operation: Operation performed (create, update, delete)
        - changes: Dictionary of changed fields
    """

    def __init__(
        self,
        entity_type: str,
        entity_id: str,
        source_entity_id: str,
        operation: str,
        changes: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            event_type=f"tds.entity.{operation}",
            aggregate_type=entity_type,
            aggregate_id=entity_id,
            data={
                "entity_type": entity_type,
                "entity_id": entity_id,
                "source_entity_id": source_entity_id,
                "operation": operation,
                "changes": changes or {},
            },
            **kwargs
        )


class TDSEntitySyncFailedEvent(TDSEvent):
    """
    Published when a single entity sync fails

    Data:
        - entity_type: Type of entity
        - source_entity_id: Source system entity ID
        - error_message: Error description
        - attempt_count: Number of attempts made
    """

    def __init__(
        self,
        entity_type: str,
        source_entity_id: str,
        error_message: str,
        attempt_count: int,
        **kwargs
    ):
        super().__init__(
            event_type="tds.entity.sync.failed",
            aggregate_type=entity_type,
            aggregate_id=source_entity_id,
            data={
                "entity_type": entity_type,
                "source_entity_id": source_entity_id,
                "error_message": error_message,
                "attempt_count": attempt_count,
            },
            **kwargs
        )


class TDSQueueEmptyEvent(TDSEvent):
    """
    Published when the sync queue becomes empty

    Data:
        - worker_id: ID of the worker that detected empty queue
        - last_processed_at: When the last item was processed
    """

    def __init__(
        self,
        worker_id: str,
        last_processed_at: Optional[datetime] = None,
        **kwargs
    ):
        super().__init__(
            event_type="tds.queue.empty",
            aggregate_type="TDSQueue",
            data={
                "worker_id": worker_id,
                "last_processed_at": last_processed_at.isoformat() if last_processed_at else None,
            },
            **kwargs
        )


class TDSDeadLetterEvent(TDSEvent):
    """
    Published when an item is moved to dead letter queue

    Data:
        - entity_type: Type of entity
        - source_entity_id: Source system entity ID
        - failure_reason: Why it failed
        - total_attempts: How many times it was attempted
    """

    def __init__(
        self,
        entity_type: str,
        source_entity_id: str,
        failure_reason: str,
        total_attempts: int,
        **kwargs
    ):
        super().__init__(
            event_type="tds.deadletter.added",
            aggregate_type=entity_type,
            aggregate_id=source_entity_id,
            data={
                "entity_type": entity_type,
                "source_entity_id": source_entity_id,
                "failure_reason": failure_reason,
                "total_attempts": total_attempts,
            },
            **kwargs
        )


class TDSAlertTriggeredEvent(TDSEvent):
    """
    Published when a TDS alert is triggered

    Data:
        - alert_type: Type of alert
        - severity: Alert severity (info, warning, error, critical)
        - message: Alert message
        - affected_count: Number of affected items
    """

    def __init__(
        self,
        alert_type: str,
        severity: str,
        message: str,
        affected_count: int = 0,
        **kwargs
    ):
        super().__init__(
            event_type="tds.alert.triggered",
            aggregate_type="TDSAlert",
            data={
                "alert_type": alert_type,
                "severity": severity,
                "message": message,
                "affected_count": affected_count,
            },
            **kwargs
        )
