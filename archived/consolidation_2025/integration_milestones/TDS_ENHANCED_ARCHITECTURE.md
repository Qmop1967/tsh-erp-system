# TDS Enhanced Architecture

## TSH Data Sync (TDS) 2.0

**Date:** November 5, 2025
**Version:** 2.0.0
**Status:** ✅ Enhanced - Production Ready

---

## 🎯 Overview

TDS (TSH Data Sync) has been completely enhanced to align with the modern **Modular Monolith**, **BFF (Backend for Frontend)**, and **Event-Driven** architecture patterns used throughout the TSH ERP system.

### What's New in TDS 2.0

- ✅ **Event-Driven Architecture**: Full integration with the system event bus
- ✅ **Modular Design**: Clean separation of concerns with domain boundaries
- ✅ **BFF Endpoints**: Mobile and web-optimized API endpoints
- ✅ **Real-Time Monitoring**: Dashboard with live metrics
- ✅ **Enhanced Caching**: Response caching for improved performance
- ✅ **Distributed Processing**: Multi-worker support with distributed locking
- ✅ **Comprehensive Observability**: Metrics, alerts, and audit trail

---

## 📐 Architecture

### Modular Monolith Structure

```
app/tds/
├── __init__.py              # Module exports
├── core/                    # Core domain logic
│   ├── events.py           # Domain events
│   ├── service.py          # Main TDS service
│   └── queue.py            # Queue management
├── handlers/               # Event handlers (optional)
│   └── sync_handlers.py   # Handlers for sync events
└── README.md              # Module documentation
```

### Event-Driven Flow

```
┌─────────────┐
│   Webhook   │
│  /External  │
└──────┬──────┘
       │
       v
┌─────────────┐     ┌──────────────┐
│   Inbox     │────>│  Validation  │
│   Event     │     │    Queue     │
└─────────────┘     └──────┬───────┘
                           │
                           v
                    ┌──────────────┐     Events Published:
                    │  Sync Queue  │     • tds.sync.started
                    │              │<────• tds.entity.synced
                    └──────┬───────┘     • tds.sync.completed
                           │             • tds.sync.failed
                           v             • tds.deadletter.added
                    ┌──────────────┐
                    │   Workers    │
                    │  (Multiple)  │
                    └──────┬───────┘
                           │
                    ┌──────┴───────┐
                    v              v
           ┌────────────┐  ┌────────────────┐
           │  Complete  │  │  Dead Letter   │
           │   &Audit   │  │     Queue      │
           └────────────┘  └────────────────┘
```

---

## 🎪 Events

### TDS Domain Events

All TDS events inherit from `TDSEvent` which extends `DomainEvent`:

#### 1. **TDSSyncStartedEvent**
```python
{
    "event_type": "tds.sync.started",
    "module": "tds",
    "data": {
        "sync_run_id": "uuid",
        "entity_type": "product",
        "source_type": "zoho",
        "batch_size": 100
    }
}
```

#### 2. **TDSEntitySyncedEvent**
```python
{
    "event_type": "tds.entity.create",  # or update, delete
    "module": "tds",
    "data": {
        "entity_type": "product",
        "entity_id": "local-id",
        "source_entity_id": "zoho-id",
        "operation": "create",
        "changes": {...}
    }
}
```

#### 3. **TDSSyncCompletedEvent**
```python
{
    "event_type": "tds.sync.completed",
    "module": "tds",
    "data": {
        "sync_run_id": "uuid",
        "total_processed": 100,
        "successful": 98,
        "failed": 2,
        "duration_seconds": 45.2
    }
}
```

#### 4. **TDSDeadLetterEvent**
```python
{
    "event_type": "tds.deadletter.added",
    "module": "tds",
    "data": {
        "entity_type": "customer",
        "source_entity_id": "zoho-customer-123",
        "failure_reason": "Validation error",
        "total_attempts": 3
    }
}
```

### Event Handlers (Examples)

```python
from app.core.events.event_bus import event_bus
from app.tds.core.events import TDSEntitySyncedEvent

# Handler for product synced events
@event_bus.subscribe('tds.entity.create')
async def handle_product_synced(event: TDSEntitySyncedEvent):
    """Update search index when product is synced"""
    if event.data['entity_type'] == 'product':
        await update_search_index(event.data['entity_id'])

# Handler for sync failures
@event_bus.subscribe('tds.sync.failed')
async def handle_sync_failure(event):
    """Send alert when sync fails"""
    await send_alert_to_ops_team(event.data)
```

---

## 🔌 BFF Endpoints

### Mobile/Web Optimized API

All TDS BFF endpoints are available at `/api/bff/tds/`

#### 1. **Dashboard Overview**

```http
GET /api/bff/tds/dashboard
```

**Response:**
```json
{
  "health": {
    "status": "healthy",
    "queue_depth": 0,
    "processing_rate": 12.5,
    "error_rate": 0.5,
    "active_workers": 2,
    "active_alerts": 0
  },
  "queue": {
    "pending": 0,
    "processing": 2,
    "completed_today": 1250,
    "failed_today": 5,
    "retry_ready": 0,
    "dead_letter": 3
  },
  "recent_runs": [...],
  "alerts": [...]
}
```

#### 2. **Sync Run History**

```http
GET /api/bff/tds/runs?limit=20&entity_type=product
```

**Response:**
```json
[
  {
    "id": "uuid",
    "type": "zoho",
    "entity_type": "product",
    "status": "completed",
    "progress_percentage": 100.0,
    "processed": 2000,
    "total": 2000,
    "failed": 0,
    "started_at": "2025-11-05T10:00:00Z",
    "duration": "5m30s"
  }
]
```

#### 3. **Entity Sync Status**

```http
GET /api/bff/tds/entities
```

**Response:**
```json
[
  {
    "entity_type": "product",
    "last_sync": "2025-11-05T10:05:00Z",
    "total_synced": 2000,
    "pending": 0,
    "failed_last_24h": 2,
    "success_rate": 99.9
  },
  {
    "entity_type": "customer",
    "last_sync": "2025-11-05T09:30:00Z",
    "total_synced": 500,
    "pending": 0,
    "failed_last_24h": 0,
    "success_rate": 100.0
  }
]
```

#### 4. **Active Alerts**

```http
GET /api/bff/tds/alerts?severity=error
```

**Response:**
```json
[
  {
    "id": "uuid",
    "severity": "error",
    "title": "High failure rate detected",
    "message": "Product sync failure rate exceeded 10% in last hour",
    "triggered_at": "2025-11-05T10:30:00Z",
    "is_active": true,
    "acknowledged": false
  }
]
```

#### 5. **Dead Letter Queue**

```http
GET /api/bff/tds/dead-letter?entity_type=product
```

**Response:**
```json
[
  {
    "id": "uuid",
    "entity_type": "product",
    "source_entity_id": "zoho-123",
    "failure_reason": "Invalid SKU format",
    "total_attempts": 3,
    "created_at": "2025-11-05T08:00:00Z",
    "resolved": false,
    "priority": 5
  }
]
```

---

## 🔧 Core Services

### TDSService

Main orchestration service for sync operations.

```python
from app.tds.core.service import TDSService

# Initialize
tds_service = TDSService(db)

# Create sync run
sync_run = await tds_service.create_sync_run(
    run_type=SourceType.ZOHO,
    entity_type=EntityType.PRODUCT,
    configuration={"batch_size": 100}
)

# Record entity sync
await tds_service.record_entity_sync(
    entity_type=EntityType.PRODUCT,
    entity_id="local-123",
    source_entity_id="zoho-456",
    operation=OperationType.CREATE,
    changes={"name": "New Product"}
)

# Complete sync run
await tds_service.complete_sync_run(
    sync_run_id=sync_run.id,
    total_processed=100,
    successful=98,
    failed=2
)

# Get statistics
stats = await tds_service.get_sync_stats()
```

### TDSQueueService

Queue management with retry logic and dead letter queue.

```python
from app.tds.core.queue import TDSQueueService

# Initialize
queue_service = TDSQueueService(db)

# Enqueue item
queue_entry = await queue_service.enqueue(
    inbox_event_id=inbox_id,
    entity_type=EntityType.PRODUCT,
    source_entity_id="zoho-123",
    operation_type=OperationType.CREATE,
    validated_payload={"name": "Product", ...},
    priority=5
)

# Get pending items
pending = await queue_service.get_pending_events(limit=100)

# Mark as completed
await queue_service.mark_as_completed(
    queue_id=queue_entry.id,
    target_entity_id="local-123"
)

# Check queue health
health = await queue_service.check_queue_health()
```

---

## 📊 Monitoring & Observability

### Metrics Collection

TDS automatically records the following metrics:

- **Sync throughput**: Items processed per minute
- **Success rate**: Percentage of successful syncs
- **Error rate**: Percentage of failed syncs
- **Queue depth**: Number of pending items
- **Processing time**: Average time per item
- **Worker performance**: Per-worker statistics

### Alerts

Automatic alerts are triggered for:

- High failure rate (> 10%)
- Queue backup (> 10,000 items)
- Stale processing (> 1 hour)
- Dead letter queue growth
- Worker failures

### Audit Trail

Complete audit trail maintained in `tds_audit_trail`:

- All data changes
- Before/after values
- Change source (zoho, manual, etc.)
- User attribution
- Timestamp

---

## 🚀 Usage Examples

### Example 1: Subscribe to Sync Events

```python
from app.core.events.event_bus import event_bus

# Listen for all TDS events
@event_bus.subscribe('tds.*')
async def log_all_tds_events(event):
    logger.info(f"TDS Event: {event.event_type} - {event.data}")

# Listen for specific events
@event_bus.subscribe('tds.entity.create')
async def handle_entity_created(event):
    entity_type = event.data['entity_type']
    entity_id = event.data['entity_id']
    logger.info(f"New {entity_type} created: {entity_id}")

    # Trigger downstream actions
    if entity_type == 'product':
        await update_search_index(entity_id)
        await clear_product_cache(entity_id)
```

### Example 2: Monitor Sync Progress

```python
from app.tds.core.service import TDSService

async def monitor_sync_run(sync_run_id: str, db: AsyncSession):
    """Monitor sync run progress"""
    tds_service = TDSService(db)

    while True:
        # Get sync run details
        result = await db.execute(
            select(TDSSyncRun).where(TDSSyncRun.id == sync_run_id)
        )
        run = result.scalar_one()

        if run.status == EventStatus.COMPLETED:
            print(f"✅ Sync completed: {run.processed_events} items")
            break
        elif run.status == EventStatus.FAILED:
            print(f"❌ Sync failed: {run.error_summary}")
            break
        else:
            progress = (run.processed_events / run.total_events * 100) if run.total_events else 0
            print(f"⏳ Progress: {progress:.1f}% ({run.processed_events}/{run.total_events})")
            await asyncio.sleep(5)
```

### Example 3: Handle Dead Letter Items

```python
from app.tds.core.queue import TDSQueueService

async def reprocess_dead_letter_items(db: AsyncSession):
    """Reprocess items from dead letter queue"""
    queue_service = TDSQueueService(db)

    # Get unresolved items
    result = await db.execute(
        select(TDSDeadLetterQueue)
        .where(TDSDeadLetterQueue.resolved == False)
        .limit(10)
    )
    items = result.scalars().all()

    for item in items:
        try:
            # Re-enqueue with fixed payload
            fixed_payload = fix_payload(item.last_payload)

            await queue_service.enqueue(
                inbox_event_id=item.sync_queue.inbox_event_id,
                entity_type=item.entity_type,
                source_entity_id=item.source_entity_id,
                operation_type=OperationType.CREATE,
                validated_payload=fixed_payload,
                priority=10  # High priority
            )

            # Mark as resolved
            item.resolved = True
            item.resolved_at = datetime.utcnow()
            item.resolution_notes = "Manually reprocessed after payload fix"

        except Exception as e:
            logger.error(f"Failed to reprocess {item.id}: {e}")

    await db.commit()
```

---

## 🔐 Integration Points

### With Event Bus

```python
# TDS automatically publishes to the global event bus
from app.core.events.event_bus import event_bus

# All TDS events flow through the event bus
# Other modules can subscribe to TDS events
```

### With BFF Layer

```python
# BFF endpoints use TDS services
from app.tds.core.service import TDSService

@router.get("/api/bff/tds/dashboard")
async def get_dashboard(db: AsyncSession = Depends(get_async_db)):
    tds_service = TDSService(db)
    stats = await tds_service.get_sync_stats()
    return format_for_mobile(stats)
```

### With Background Workers

```python
# Workers use TDS queue service
from app.tds.core.queue import TDSQueueService

class SyncWorker:
    async def process_batch(self):
        queue_service = TDSQueueService(self.db)
        pending = await queue_service.get_pending_events(limit=100)

        for item in pending:
            await self.process_item(item)
```

---

## 📈 Performance

### Caching Strategy

- Dashboard endpoint: 30s TTL
- Sync run list: 30s TTL
- Entity status: 60s TTL
- Alerts list: 30s TTL
- Dead letter queue: 60s TTL

### Processing Rate

- **Target**: 50-100 items/minute per worker
- **Concurrent workers**: 2-10 (configurable)
- **Batch size**: 100 items (configurable)
- **Retry backoff**: Exponential (1m, 2m, 4m, 8m)

### Database Optimization

- Indexes on: `status`, `priority`, `created_at`, `entity_type`
- Partitioning: By `created_at` (monthly)
- Auto-cleanup: Old completed items (30 days)
- Archive strategy: Move to cold storage after 90 days

---

## 🧪 Testing

### Unit Tests

```python
# Test event publishing
async def test_sync_run_publishes_events():
    service = TDSService(db)

    # Create sync run
    run = await service.create_sync_run(
        run_type=SourceType.ZOHO,
        entity_type=EntityType.PRODUCT
    )

    # Verify event was published
    events = event_bus.get_event_history(limit=1)
    assert events[0].event_type == "tds.sync.started"
```

### Integration Tests

```python
# Test end-to-end sync flow
async def test_complete_sync_flow():
    # Enqueue item
    queue_service = TDSQueueService(db)
    entry = await queue_service.enqueue(...)

    # Process item
    worker = SyncWorker()
    await worker.process_event(entry.id)

    # Verify completion
    assert entry.status == EventStatus.COMPLETED
```

---

## 🎯 Best Practices

1. **Always use TDSService** for orchestration, not direct DB access
2. **Subscribe to events** instead of polling database
3. **Use BFF endpoints** for client consumption
4. **Monitor queue depth** and alert on backups
5. **Handle dead letters** promptly - don't let them accumulate
6. **Use distributed locking** for multi-worker setups
7. **Implement circuit breakers** for external API calls
8. **Cache aggressively** for read-heavy endpoints

---

## 🔄 Migration from Old TDS

### Old Code (Direct DB Access)

```python
# ❌ Don't do this
result = await db.execute(select(TDSSyncQueue).where(...))
queue_entries = result.scalars().all()

for entry in queue_entries:
    # Process...
    entry.status = EventStatus.COMPLETED
    await db.commit()
```

### New Code (Event-Driven)

```python
# ✅ Do this
tds_service = TDSService(db)
queue_service = TDSQueueService(db)

# Events are automatically published
await tds_service.record_entity_sync(...)
await queue_service.mark_as_completed(...)

# Subscribe to events
@event_bus.subscribe('tds.entity.synced')
async def handle_sync(event):
    # React to sync completion
    pass
```

---

## 📚 References

- [Modular Monolith Architecture](./CLEAN_ARCHITECTURE_2025.md)
- [BFF Pattern](./BFF_ARCHITECTURE_COMPLETE.md)
- [Event Bus Documentation](./EVENT_BUS_EXAMPLES.md)
- [Performance Optimization](./PERFORMANCE_OPTIMIZATION_GUIDE.md)

---

**Next Steps:**
1. Deploy TDS 2.0 to staging
2. Monitor event flow and performance
3. Migrate all direct DB access to use TDS services
4. Implement additional event handlers as needed
5. Set up alerting for queue health metrics
