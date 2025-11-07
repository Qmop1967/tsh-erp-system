"""
TDS Core - Response Schemas
Pydantic models for API responses
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


# ============================================================================
# WEBHOOK RESPONSE
# ============================================================================

class WebhookResponse(BaseModel):
    """Standard webhook response"""

    success: bool = Field(..., description="Whether webhook was accepted")
    message: str = Field(..., description="Response message")
    event_id: Optional[UUID] = Field(None, description="TDS inbox event ID")
    idempotency_key: Optional[str] = Field(None, description="Idempotency key for deduplication")
    queued: bool = Field(default=False, description="Whether event was queued for processing")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Webhook received and queued for processing",
                "event_id": "550e8400-e29b-41d4-a716-446655440000",
                "idempotency_key": "zoho:product:123456:update",
                "queued": True
            }
        }


class BatchWebhookResponse(BaseModel):
    """Batch webhook processing response"""

    success: bool = Field(..., description="Overall batch success")
    total_events: int = Field(..., description="Total events in batch")
    accepted: int = Field(..., description="Events accepted")
    rejected: int = Field(..., description="Events rejected")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Validation errors")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "total_events": 10,
                "accepted": 9,
                "rejected": 1,
                "errors": [
                    {
                        "event_index": 5,
                        "error": "Missing required field: item_id"
                    }
                ]
            }
        }


# ============================================================================
# HEALTH CHECK RESPONSES
# ============================================================================

class HealthResponse(BaseModel):
    """System health check response"""

    status: str = Field(..., description="Health status (healthy/unhealthy)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    version: str = Field(..., description="Application version")
    database: Dict[str, Any] = Field(..., description="Database health")
    queue: Dict[str, Any] = Field(..., description="Queue statistics")
    uptime_seconds: Optional[int] = Field(None, description="Application uptime")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-10-31T10:30:00Z",
                "version": "1.0.0",
                "database": {
                    "status": "healthy",
                    "latency_ms": 5.2,
                    "pool": {
                        "size": 20,
                        "checked_in": 18,
                        "checked_out": 2
                    }
                },
                "queue": {
                    "pending": 15,
                    "processing": 3,
                    "failed": 1
                },
                "uptime_seconds": 86400
            }
        }


class DetailedHealthResponse(HealthResponse):
    """Detailed health check with component status"""

    components: Dict[str, Dict[str, Any]] = Field(
        ...,
        description="Individual component health"
    )
    metrics: Dict[str, Any] = Field(..., description="Performance metrics")
    alerts: List[Dict[str, Any]] = Field(default_factory=list, description="Active alerts")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-10-31T10:30:00Z",
                "version": "1.0.0",
                "database": {"status": "healthy", "latency_ms": 5.2},
                "queue": {"pending": 15, "processing": 3},
                "components": {
                    "inbox": {"status": "healthy", "count": 1200},
                    "processor": {"status": "healthy", "throughput": 150},
                    "worker": {"status": "healthy", "active_workers": 4}
                },
                "metrics": {
                    "success_rate_24h": 99.5,
                    "avg_processing_time_ms": 250,
                    "events_processed_24h": 15000
                },
                "alerts": []
            }
        }


# ============================================================================
# QUEUE STATISTICS
# ============================================================================

class QueueStatsResponse(BaseModel):
    """Queue statistics response"""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    total_events: int = Field(..., description="Total events in queue")
    by_status: Dict[str, int] = Field(..., description="Events by status")
    by_entity: Dict[str, int] = Field(..., description="Events by entity type")
    by_priority: Dict[int, int] = Field(..., description="Events by priority")
    oldest_pending: Optional[datetime] = Field(None, description="Oldest pending event timestamp")
    processing_rate: Optional[float] = Field(None, description="Events per minute")

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-10-31T10:30:00Z",
                "total_events": 150,
                "by_status": {
                    "pending": 100,
                    "processing": 40,
                    "failed": 10
                },
                "by_entity": {
                    "product": 80,
                    "customer": 40,
                    "invoice": 30
                },
                "by_priority": {
                    1: 10,
                    5: 120,
                    10: 20
                },
                "oldest_pending": "2025-10-31T10:00:00Z",
                "processing_rate": 125.5
            }
        }


# ============================================================================
# SYNC RUN RESPONSES
# ============================================================================

class SyncRunResponse(BaseModel):
    """Sync run status response"""

    run_id: UUID = Field(..., description="Sync run ID")
    run_type: str = Field(..., description="Run type (zoho, manual, scheduled)")
    entity_type: Optional[str] = Field(None, description="Entity type")
    status: str = Field(..., description="Run status")
    started_at: datetime = Field(..., description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    duration_seconds: Optional[int] = Field(None, description="Duration in seconds")
    statistics: Dict[str, int] = Field(..., description="Processing statistics")
    error_summary: Optional[Dict[str, Any]] = Field(None, description="Error summary if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "650e8400-e29b-41d4-a716-446655440000",
                "run_type": "scheduled",
                "entity_type": "product",
                "status": "completed",
                "started_at": "2025-10-31T10:00:00Z",
                "completed_at": "2025-10-31T10:05:30Z",
                "duration_seconds": 330,
                "statistics": {
                    "total_events": 1000,
                    "processed": 995,
                    "failed": 5,
                    "skipped": 0
                },
                "error_summary": None
            }
        }


class SyncRunListResponse(BaseModel):
    """List of sync runs"""

    total: int = Field(..., description="Total number of runs")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size")
    runs: List[SyncRunResponse] = Field(..., description="Sync runs")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 100,
                "page": 1,
                "page_size": 20,
                "runs": []
            }
        }


# ============================================================================
# DEAD LETTER QUEUE RESPONSE
# ============================================================================

class DLQItemResponse(BaseModel):
    """Dead letter queue item"""

    id: UUID = Field(..., description="DLQ item ID")
    entity_type: str = Field(..., description="Entity type")
    source_entity_id: str = Field(..., description="Source entity ID")
    failure_reason: str = Field(..., description="Failure reason")
    total_attempts: int = Field(..., description="Total retry attempts")
    created_at: datetime = Field(..., description="Creation timestamp")
    resolved: bool = Field(..., description="Whether resolved")
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")
    last_payload: Dict[str, Any] = Field(..., description="Last attempted payload")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "750e8400-e29b-41d4-a716-446655440000",
                "entity_type": "product",
                "source_entity_id": "123456",
                "failure_reason": "Validation error: Invalid price format",
                "total_attempts": 3,
                "created_at": "2025-10-31T09:00:00Z",
                "resolved": False,
                "resolved_at": None,
                "last_payload": {
                    "item_id": "123456",
                    "name": "Product",
                    "price": "invalid"
                }
            }
        }


class DLQListResponse(BaseModel):
    """List of DLQ items"""

    total: int = Field(..., description="Total DLQ items")
    unresolved: int = Field(..., description="Unresolved items")
    items: List[DLQItemResponse] = Field(..., description="DLQ items")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 50,
                "unresolved": 35,
                "items": []
            }
        }


# ============================================================================
# METRICS RESPONSE
# ============================================================================

class MetricsResponse(BaseModel):
    """System metrics response"""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    time_range: str = Field(..., description="Time range (1h, 24h, 7d)")
    metrics: Dict[str, Any] = Field(..., description="Metric values")

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-10-31T10:30:00Z",
                "time_range": "24h",
                "metrics": {
                    "events_received": 15000,
                    "events_processed": 14800,
                    "events_failed": 200,
                    "success_rate": 98.67,
                    "avg_processing_time_ms": 250,
                    "p95_processing_time_ms": 450,
                    "p99_processing_time_ms": 800
                }
            }
        }


# ============================================================================
# ERROR RESPONSE
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response"""

    success: bool = Field(default=False, description="Always False for errors")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "ValidationError",
                "message": "Invalid request data",
                "details": {
                    "field": "entity_id",
                    "reason": "Field is required"
                },
                "timestamp": "2025-10-31T10:30:00Z"
            }
        }
