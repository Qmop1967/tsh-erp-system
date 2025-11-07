## TDS 2.0 Quick Start Guide

### 🚀 Getting Started with Enhanced TDS

This guide will help you quickly get started with the enhanced TDS (TSH Data Sync) system.

---

## 📦 What's Included

✅ Event-driven synchronization
✅ BFF endpoints for monitoring
✅ Modular architecture
✅ Real-time metrics
✅ Dead letter queue handling
✅ Automatic retry with backoff

---

## 🔧 Installation

### 1. Import TDS Module

```python
from app.tds.core.service import TDSService
from app.tds.core.queue import TDSQueueService
from app.tds.core.events import TDSEntitySyncedEvent
```

### 2. Initialize Event Handlers

The event handlers are automatically registered when you import the module:

```python
# This happens automatically on app startup
from app.tds.handlers import sync_handlers
```

---

## 💻 Basic Usage

### Starting a Sync Run

```python
from app.tds.core.service import TDSService
from app.models.zoho_sync import SourceType, EntityType

async def start_product_sync(db: AsyncSession):
    tds_service = TDSService(db)

    # Create sync run
    sync_run = await tds_service.create_sync_run(
        run_type=SourceType.ZOHO,
        entity_type=EntityType.PRODUCT,
        configuration={"batch_size": 100}
    )

    return sync_run.id
```

### Enqueueing Items

```python
from app.tds.core.queue import TDSQueueService
from app.models.zoho_sync import EntityType, OperationType

async def enqueue_product(db: AsyncSession, product_data: dict):
    queue_service = TDSQueueService(db)

    # Add to queue
    queue_entry = await queue_service.enqueue(
        inbox_event_id=inbox_id,
        entity_type=EntityType.PRODUCT,
        source_entity_id=product_data['zoho_id'],
        operation_type=OperationType.CREATE,
        validated_payload=product_data,
        priority=5
    )

    return queue_entry.id
```

### Recording Sync Results

```python
async def complete_sync(db: AsyncSession, sync_run_id: str):
    tds_service = TDSService(db)

    # Mark as completed with stats
    await tds_service.complete_sync_run(
        sync_run_id=sync_run_id,
        total_processed=100,
        successful=98,
        failed=2
    )
```

---

## 📡 Subscribing to Events

### Listen to Sync Completions

```python
from app.core.events.event_bus import event_bus

@event_bus.subscribe('tds.sync.completed')
async def handle_sync_done(event):
    print(f"Sync completed: {event.data['successful']} items")
    # Do something with the results
```

### Listen to Entity Changes

```python
@event_bus.subscribe('tds.entity.create')
async def handle_product_created(event):
    if event.data['entity_type'] == 'product':
        product_id = event.data['entity_id']
        # Update search index
        await update_search_index(product_id)
```

### Listen to Failures

```python
@event_bus.subscribe('tds.deadletter.added')
async def handle_dead_letter(event):
    # Send alert to ops team
    await send_alert(
        title="Item in Dead Letter Queue",
        message=f"{event.data['entity_type']}: {event.data['failure_reason']}"
    )
```

---

## 🎯 BFF API Endpoints

### Dashboard Overview

```bash
curl http://localhost:8000/api/bff/tds/dashboard
```

Returns:
- System health
- Queue statistics
- Recent sync runs
- Active alerts

### Get Sync Runs

```bash
curl http://localhost:8000/api/bff/tds/runs?limit=10&entity_type=product
```

### Get Entity Status

```bash
curl http://localhost:8000/api/bff/tds/entities
```

### Get Active Alerts

```bash
curl http://localhost:8000/api/bff/tds/alerts
```

### Health Check

```bash
curl http://localhost:8000/api/bff/tds/health
```

---

## 🔍 Monitoring

### Check Queue Health

```python
from app.tds.core.queue import TDSQueueService

async def check_health(db: AsyncSession):
    queue_service = TDSQueueService(db)
    health = await queue_service.check_queue_health()

    print(f"Healthy: {health['healthy']}")
    print(f"Queue depths: {health['queue_depths']}")
    print(f"DLQ count: {health['dead_letter_queue']}")
```

### Get Statistics

```python
from app.tds.core.service import TDSService

async def get_stats(db: AsyncSession):
    tds_service = TDSService(db)
    stats = await tds_service.get_sync_stats()

    print(f"Active alerts: {stats['active_alerts']}")
    print(f"DLQ items: {stats['dead_letter_queue']}")
    print(f"Recent runs: {len(stats['recent_runs'])}")
```

---

## 🛠️ Common Tasks

### Handle Dead Letter Queue

```python
from app.models.zoho_sync import TDSDeadLetterQueue
from sqlalchemy import select, and_

async def process_dlq_items(db: AsyncSession):
    # Get unresolved items
    result = await db.execute(
        select(TDSDeadLetterQueue)
        .where(TDSDeadLetterQueue.resolved == False)
        .limit(10)
    )
    items = result.scalars().all()

    for item in items:
        # Fix the issue and re-enqueue
        fixed_payload = fix_payload(item.last_payload)

        # Enqueue again
        queue_service = TDSQueueService(db)
        await queue_service.enqueue(...)

        # Mark as resolved
        item.resolved = True
        item.resolved_at = datetime.utcnow()

    await db.commit()
```

### Retry Failed Items

```python
from app.models.zoho_sync import TDSSyncQueue, EventStatus

async def retry_failed_items(db: AsyncSession):
    # Get failed items
    result = await db.execute(
        select(TDSSyncQueue)
        .where(TDSSyncQueue.status == EventStatus.FAILED)
        .limit(10)
    )
    items = result.scalars().all()

    queue_service = TDSQueueService(db)

    for item in items:
        # Reset and re-enqueue
        await queue_service.enqueue(
            inbox_event_id=item.inbox_event_id,
            entity_type=item.entity_type,
            source_entity_id=item.source_entity_id,
            operation_type=item.operation_type,
            validated_payload=item.validated_payload,
            priority=10  # High priority
        )
```

### Create Custom Alerts

```python
from app.tds.core.service import TDSService
from app.models.zoho_sync import AlertSeverity, EntityType

async def create_alert(db: AsyncSession):
    tds_service = TDSService(db)

    alert = await tds_service.create_alert(
        alert_type="high_failure_rate",
        severity=AlertSeverity.ERROR,
        title="High Sync Failure Rate",
        message="Product sync failure rate exceeded 10%",
        entity_type=EntityType.PRODUCT,
        affected_count=25
    )

    return alert.id
```

---

## 📊 Performance Tips

### Caching

BFF endpoints use automatic caching:

```python
from app.bff.services.cache_service import cache_response

@router.get("/my-endpoint")
@cache_response(ttl_seconds=60)
async def my_endpoint():
    # Response is cached for 60 seconds
    return {"data": "..."}
```

### Batch Processing

Process items in batches for better performance:

```python
async def process_batch(db: AsyncSession):
    queue_service = TDSQueueService(db)

    # Get 100 items at once
    pending = await queue_service.get_pending_events(limit=100)

    for item in pending:
        await process_item(item)
```

### Prioritization

Use priority for important items:

```python
# High priority (processed first)
await queue_service.enqueue(..., priority=10)

# Normal priority
await queue_service.enqueue(..., priority=5)

# Low priority
await queue_service.enqueue(..., priority=1)
```

---

## 🧪 Testing

### Unit Test Example

```python
import pytest
from app.tds.core.service import TDSService
from app.models.zoho_sync import SourceType, EntityType

@pytest.mark.asyncio
async def test_create_sync_run(db_session):
    tds_service = TDSService(db_session)

    sync_run = await tds_service.create_sync_run(
        run_type=SourceType.ZOHO,
        entity_type=EntityType.PRODUCT
    )

    assert sync_run.id is not None
    assert sync_run.status == EventStatus.PENDING
```

### Integration Test Example

```python
@pytest.mark.asyncio
async def test_complete_sync_flow(db_session):
    # Create sync run
    tds_service = TDSService(db_session)
    sync_run = await tds_service.create_sync_run(
        run_type=SourceType.ZOHO,
        entity_type=EntityType.PRODUCT
    )

    # Enqueue item
    queue_service = TDSQueueService(db_session)
    entry = await queue_service.enqueue(...)

    # Process item
    await queue_service.mark_as_completed(entry.id)

    # Complete sync
    await tds_service.complete_sync_run(
        sync_run_id=sync_run.id,
        total_processed=1,
        successful=1,
        failed=0
    )

    # Verify
    assert entry.status == EventStatus.COMPLETED
```

---

## 🔗 Integration with Other Modules

### With Inventory Module

```python
from app.core.events.event_bus import event_bus

@event_bus.subscribe('tds.entity.create')
async def update_inventory(event):
    if event.data['entity_type'] == 'product':
        product_id = event.data['entity_id']
        # Update inventory levels
        await inventory_service.sync_stock_levels(product_id)
```

### With Sales Module

```python
@event_bus.subscribe('tds.entity.update')
async def notify_sales(event):
    if event.data['entity_type'] == 'customer':
        customer_id = event.data['entity_id']
        # Notify sales team of customer update
        await sales_service.notify_customer_update(customer_id)
```

---

## 🚨 Troubleshooting

### Issue: Events not being published

**Solution:** Ensure event handlers are imported at startup:

```python
# In main.py or app initialization
from app.tds.handlers import sync_handlers
```

### Issue: Queue items stuck in processing

**Solution:** Clean up expired locks:

```python
from app.utils.locking import cleanup_expired_locks

async def cleanup_locks(db: AsyncSession):
    cleaned = await cleanup_expired_locks(db)
    print(f"Cleaned up {cleaned} expired locks")
```

### Issue: High memory usage

**Solution:** Clean up old completed entries:

```python
from app.tds.core.queue import TDSQueueService

async def cleanup(db: AsyncSession):
    queue_service = TDSQueueService(db)
    deleted = await queue_service.cleanup_old_entries(days=7)
    print(f"Deleted {deleted} old entries")
```

---

## 📚 Next Steps

1. **Read the full documentation**: [TDS_ENHANCED_ARCHITECTURE.md](./TDS_ENHANCED_ARCHITECTURE.md)
2. **Explore examples**: Check `app/tds/handlers/sync_handlers.py` for event handler examples
3. **Set up monitoring**: Configure alerts and metrics collection
4. **Test the BFF API**: Try the dashboard endpoint to see live data
5. **Integrate with your modules**: Subscribe to TDS events in your domain modules

---

## 🆘 Support

For questions or issues:
- Check the full documentation: `TDS_ENHANCED_ARCHITECTURE.md`
- Review event handler examples: `app/tds/handlers/sync_handlers.py`
- Look at BFF endpoint implementations: `app/bff/routers/tds.py`

---

**Happy Syncing! 🚀**
