# TDS Phase 1: Critical Fixes Implementation
## Webhook Processing + Auto-Healing + Scheduling + Monitoring

**Date:** 2025-11-14
**Priority:** 🔴 CRITICAL
**Estimated Time:** 12-16 hours
**Status:** READY FOR IMPLEMENTATION

---

## 🎯 Overview

This document contains the complete implementation for Phase 1 critical fixes that will make TDS production-ready.

### What We're Fixing:

1. **Webhook async context error** (CRITICAL - blocks real-time sync)
2. **Auto-healing activation** (HIGH - enables self-recovery)
3. **Automated scheduling** (HIGH - eliminates manual operations)
4. **Basic monitoring setup** (HIGH - visibility into system health)

### Expected Outcome:

- ✅ 100% webhook processing success (currently 0%)
- ✅ Automatic recovery from failures (currently manual)
- ✅ Zero manual sync operations (currently all manual)
- ✅ Real-time visibility into system health

---

## 🔴 Fix #1: Webhook Async Context Error

### Root Cause Analysis

**Problem Location:** `app/background/zoho_sync_worker.py` lines 172-181

The worker is creating an AsyncSession properly BUT the entity handlers' async database operations are not being executed within an explicit async transaction context.

**Error:**
```
greenlet_spawn has not been called; can't call await_only() here.
Was IO attempted in an unexpected place?
```

**Why It Fails:**
```python
# Current flow in worker:
async with AsyncSessionLocal() as db:  # ✅ Async session created
    handler = EntityHandlerFactory.get_handler(entity_type, db)
    result = await handler.sync(payload, operation)  # ❌ Async operations inside handler fail

# Inside handler (ProductHandler.sync):
result = await self.db.execute(text(...))  # ❌ FAILS HERE
await self.db.commit()  # ❌ NO ASYNC TRANSACTION CONTEXT
```

### Solution

We need to ensure database operations are wrapped in an explicit async transaction context.

#### File 1: Fix Entity Handler Base Class

**Location:** `app/background/zoho_entity_handlers.py`

```python
# Current (BROKEN):
class BaseEntityHandler(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert(self, table, values: Dict, conflict_column: str):
        stmt = pg_insert(table).values(**values)
        stmt = stmt.on_conflict_do_update(
            index_elements=[conflict_column],
            set_=values
        )
        result = await self.db.execute(stmt)  # ❌ No transaction context
        await self.db.commit()  # ❌ Fails here
        return result
```

**Fix (ADD THIS):**
```python
class BaseEntityHandler(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert(self, table, values: Dict, conflict_column: str):
        """
        Perform PostgreSQL upsert with proper async transaction context
        """
        async with self.db.begin():  # ✅ EXPLICIT ASYNC TRANSACTION
            stmt = pg_insert(table).values(**values)
            stmt = stmt.on_conflict_do_update(
                index_elements=[conflict_column],
                set_=values
            )
            result = await self.db.execute(stmt)
            return result  # Auto-commits on context exit

    async def execute_with_context(self, query, params: Dict = None):
        """
        Execute query with proper async context

        Helper method for all database operations
        """
        async with self.db.begin():  # ✅ EXPLICIT ASYNC TRANSACTION
            result = await self.db.execute(query, params or {})
            return result  # Auto-commits on context exit
```

#### File 2: Update ProductHandler

**Location:** `app/background/zoho_entity_handlers.py` (ProductHandler.sync method)

```python
# Current (BROKEN):
async def sync(self, payload: Dict[str, Any], operation: str) -> Dict[str, Any]:
    try:
        # ... validation code ...

        result = await self.db.execute(text("""..."""), {...})  # ❌ No transaction
        await self.db.commit()  # ❌ Fails

        row = result.fetchone()
        product_id = row[0] if row else None

        return {"success": True, "local_entity_id": str(product_id), ...}

    except Exception as e:
        await self.db.rollback()  # ❌ Also fails
        raise
```

**Fix (REPLACE WITH):**
```python
async def sync(self, payload: Dict[str, Any], operation: str) -> Dict[str, Any]:
    """Sync product with proper async transaction context"""
    try:
        # Extract required fields
        zoho_item_id = payload.get("item_id")
        if not zoho_item_id:
            raise ValueError("Missing required field: item_id")

        # Map Zoho fields to local database fields
        product_data = {
            "zoho_item_id": zoho_item_id,
            "name": payload.get("name", ""),
            "sku": payload.get("sku", ""),
            "description": payload.get("description", ""),
            "price": float(payload.get("rate", 0)),
            "stock_quantity": int(payload.get("stock_on_hand", 0)),
            "is_active": payload.get("is_active", True),
        }

        # ✅ USE HELPER METHOD WITH TRANSACTION CONTEXT
        result = await self.execute_with_context(
            text("""
                INSERT INTO products (zoho_item_id, name, sku, description, price, stock_quantity, is_active, updated_at)
                VALUES (:zoho_item_id, :name, :sku, :description, :price, :stock_quantity, :is_active, NOW())
                ON CONFLICT (zoho_item_id)
                DO UPDATE SET
                    name = EXCLUDED.name,
                    sku = EXCLUDED.sku,
                    description = EXCLUDED.description,
                    price = EXCLUDED.price,
                    stock_quantity = EXCLUDED.stock_quantity,
                    is_active = EXCLUDED.is_active,
                    updated_at = NOW()
                RETURNING id
            """),
            product_data
        )

        # Get the product ID
        row = result.fetchone()
        product_id = row[0] if row else None

        logger.info(f"Product synced successfully: {zoho_item_id} -> local ID {product_id}")

        return {
            "success": True,
            "local_entity_id": str(product_id),
            "operation_performed": "upsert",
            "records_affected": 1
        }

    except Exception as e:
        # ✅ NO MANUAL ROLLBACK - Context manager handles it
        logger.error(f"Product sync failed: {e}", exc_info=True)
        raise
```

#### File 3: Update ALL Other Handlers (Same Pattern)

Apply the **SAME FIX** to all other entity handlers:

1. **CustomerHandler** (line 187-230)
2. **InvoiceHandler** (line 285-330)
3. **SalesOrderHandler** (line 340-480)
4. **PaymentHandler** (line 490-600)
5. **VendorHandler** (line 610-720)
6. **UserHandler** (line 730-850)
7. **BillHandler** (line 860-980)
8. **CreditNoteHandler** (line 990-1110)
9. **StockAdjustmentHandler** (line 1120-1170)
10. **PriceListHandler** (line 1180-1190)

**Pattern for all:**
```python
# Replace this pattern:
result = await self.db.execute(text(...), {...})
await self.db.commit()

# With this pattern:
result = await self.execute_with_context(text(...), {...})
# No manual commit needed - auto-commits
```

### Testing the Fix

**Step 1: Test with Single Webhook**

```python
# Create test script: scripts/test_webhook_fix.py
import asyncio
from app.db.database import AsyncSessionLocal
from app.services.zoho_processor import ProcessorService
from app.background.zoho_sync_worker import SyncWorker

async def test_single_webhook():
    """Test webhook processing with fixed async context"""
    async with AsyncSessionLocal() as db:
        # Get first item from dead letter queue
        from sqlalchemy import select, text
        from app.models.zoho_sync import TDSSyncQueue, EventStatus

        result = await db.execute(
            select(TDSSyncQueue)
            .where(TDSSyncQueue.status == EventStatus.DEAD_LETTER)
            .limit(1)
        )
        queue_item = result.scalar_one_or_none()

        if not queue_item:
            print("No items in dead letter queue")
            return

        print(f"Testing webhook: {queue_item.entity_type}/{queue_item.source_entity_id}")

        # Reset status to pending
        queue_item.status = EventStatus.PENDING
        queue_item.attempt_count = 0
        await db.commit()

        # Process with worker
        worker = SyncWorker(worker_id="test-worker")
        await worker._process_event(str(queue_item.id))

        # Check result
        await db.refresh(queue_item)
        print(f"Result: {queue_item.status}")
        if queue_item.status == EventStatus.COMPLETED:
            print("✅ WEBHOOK PROCESSED SUCCESSFULLY!")
        else:
            print(f"❌ FAILED: {queue_item.error_message}")

if __name__ == "__main__":
    asyncio.run(test_single_webhook())
```

**Run test:**
```bash
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem
python3 scripts/test_webhook_fix.py
```

**Step 2: Process Dead Letter Queue**

After confirming single webhook works, process all 58 failed webhooks:

```python
# scripts/process_dead_letter_queue.py
import asyncio
from app.db.database import AsyncSessionLocal
from app.background.zoho_sync_worker import SyncWorker
from sqlalchemy import select, text
from app.models.zoho_sync import TDSSyncQueue, EventStatus

async def process_dlq():
    """Process all items in dead letter queue"""
    async with AsyncSessionLocal() as db:
        # Get all dead letter items
        result = await db.execute(
            select(TDSSyncQueue)
            .where(TDSSyncQueue.status == EventStatus.DEAD_LETTER)
        )
        dlq_items = result.scalars().all()

        print(f"Found {len(dlq_items)} items in dead letter queue")

        # Reset all to pending
        for item in dlq_items:
            item.status = EventStatus.PENDING
            item.attempt_count = 0
            item.error_message = None

        await db.commit()
        print("✅ Reset all DLQ items to PENDING")

    # Let workers process them
    print("Workers will now process the queue...")
    print("Monitor with: SELECT status, COUNT(*) FROM tds_sync_queue GROUP BY status;")

if __name__ == "__main__":
    asyncio.run(process_dlq())
```

**Run:**
```bash
python3 scripts/process_dead_letter_queue.py
```

---

## 🔄 Fix #2: Automated Scheduling with APScheduler

### Implementation

**File:** `app/main.py`

Add APScheduler to automate all sync operations:

```python
# Add imports at top
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import logging

logger = logging.getLogger(__name__)

# Initialize scheduler (after app creation)
scheduler = AsyncIOScheduler()

# ============================================================================
# SCHEDULED JOBS
# ============================================================================

async def daily_full_sync_job():
    """Daily full sync at 2 AM (low traffic period)"""
    logger.info("🕐 Starting daily full sync job...")
    try:
        # Call bulk sync endpoint internally
        from app.routers.zoho_bulk_sync import trigger_sync_all
        from app.db.database import AsyncSessionLocal

        async with AsyncSessionLocal() as db:
            result = await trigger_sync_all(db)
            logger.info(f"✅ Daily full sync completed: {result}")
    except Exception as e:
        logger.error(f"❌ Daily full sync failed: {e}", exc_info=True)

async def hourly_incremental_sync_job():
    """Hourly incremental sync"""
    logger.info("🕐 Starting hourly incremental sync...")
    try:
        from app.routers.zoho_bulk_sync import trigger_incremental_sync
        from app.db.database import AsyncSessionLocal

        async with AsyncSessionLocal() as db:
            # Sync products and customers only (incremental)
            result = await trigger_incremental_sync(db)
            logger.info(f"✅ Hourly sync completed: {result}")
    except Exception as e:
        logger.error(f"❌ Hourly sync failed: {e}", exc_info=True)

async def stock_sync_job():
    """Stock sync every 15 minutes (critical for inventory)"""
    logger.info("📦 Starting stock sync job...")
    try:
        from app.routers.zoho_bulk_sync import sync_stock_levels
        from app.db.database import AsyncSessionLocal

        async with AsyncSessionLocal() as db:
            result = await sync_stock_levels(db)
            logger.info(f"✅ Stock sync completed: {result}")
    except Exception as e:
        logger.error(f"❌ Stock sync failed: {e}", exc_info=True)

async def auto_healing_job():
    """Auto-healing every 15 minutes"""
    logger.info("🔧 Starting auto-healing job...")
    try:
        from app.services.tds_auto_healing import run_auto_healing
        from app.db.database import AsyncSessionLocal

        async with AsyncSessionLocal() as db:
            result = await run_auto_healing(db)
            logger.info(f"✅ Auto-healing completed: {result}")
    except Exception as e:
        logger.error(f"❌ Auto-healing failed: {e}", exc_info=True)

async def statistics_comparison_job():
    """Daily statistics comparison at 3 AM"""
    logger.info("📊 Starting statistics comparison job...")
    try:
        from app.tds.statistics.engine import StatisticsEngine
        from app.db.database import AsyncSessionLocal

        async with AsyncSessionLocal() as db:
            engine = StatisticsEngine(db)
            report = await engine.collect_and_compare()
            logger.info(f"✅ Statistics comparison completed: match={report.overall_match_percentage}%")

            # Alert if mismatch > 5%
            if report.overall_match_percentage < 95:
                logger.warning(f"⚠️ Data mismatch detected: {report.overall_match_percentage}% match")
    except Exception as e:
        logger.error(f"❌ Statistics comparison failed: {e}", exc_info=True)

# ============================================================================
# STARTUP EVENT: Configure Scheduler
# ============================================================================

@app.on_event("startup")
async def startup_scheduler():
    """Configure and start APScheduler on app startup"""
    try:
        # Daily full sync at 2 AM
        scheduler.add_job(
            daily_full_sync_job,
            CronTrigger(hour=2, minute=0),
            id='daily_full_sync',
            name='Daily Full Sync (2 AM)',
            replace_existing=True
        )

        # Hourly incremental sync
        scheduler.add_job(
            hourly_incremental_sync_job,
            IntervalTrigger(hours=1),
            id='hourly_incremental_sync',
            name='Hourly Incremental Sync',
            replace_existing=True
        )

        # Stock sync every 15 minutes
        scheduler.add_job(
            stock_sync_job,
            IntervalTrigger(minutes=15),
            id='stock_sync_15min',
            name='Stock Sync (Every 15 Min)',
            replace_existing=True
        )

        # Auto-healing every 15 minutes
        scheduler.add_job(
            auto_healing_job,
            IntervalTrigger(minutes=15),
            id='auto_healing',
            name='Auto-Healing (Every 15 Min)',
            replace_existing=True
        )

        # Statistics comparison daily at 3 AM
        scheduler.add_job(
            statistics_comparison_job,
            CronTrigger(hour=3, minute=0),
            id='daily_statistics',
            name='Daily Statistics Comparison (3 AM)',
            replace_existing=True
        )

        scheduler.start()
        logger.info("✅ TDS Scheduler started with 5 jobs:")
        logger.info("  - Daily Full Sync (2 AM)")
        logger.info("  - Hourly Incremental Sync")
        logger.info("  - Stock Sync (Every 15 Min)")
        logger.info("  - Auto-Healing (Every 15 Min)")
        logger.info("  - Daily Statistics (3 AM)")

    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {e}", exc_info=True)

@app.on_event("shutdown")
async def shutdown_scheduler():
    """Gracefully shutdown scheduler"""
    logger.info("Shutting down TDS scheduler...")
    scheduler.shutdown()
    logger.info("✅ TDS scheduler stopped")
```

**Install APScheduler:**
```bash
pip install apscheduler
echo "apscheduler==3.10.4" >> requirements.txt
```

---

## 🔧 Fix #3: Auto-Healing Service

Create comprehensive auto-healing service:

**File:** `app/services/tds_auto_healing.py` (NEW FILE)

```python
"""
TDS Auto-Healing Service
Automatically recovers from failures
"""
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_

from app.models.zoho_sync import TDSSyncQueue, EventStatus, TDSDeadLetterQueue

logger = logging.getLogger(__name__)

async def run_auto_healing(db: AsyncSession) -> Dict[str, Any]:
    """
    Run auto-healing operations

    Returns:
        Dictionary with healing statistics
    """
    stats = {
        "stuck_tasks_recovered": 0,
        "dlq_items_retried": 0,
        "alerts_created": 0,
        "timestamp": datetime.utcnow().isoformat()
    }

    try:
        # 1. Recover stuck tasks (processing > 60 minutes)
        stuck_count = await recover_stuck_tasks(db)
        stats["stuck_tasks_recovered"] = stuck_count

        # 2. Retry dead letter queue items (after 24 hours)
        dlq_count = await retry_dead_letter_queue(db)
        stats["dlq_items_retried"] = dlq_count

        # 3. Check queue health and create alerts if needed
        alerts_count = await check_queue_health(db)
        stats["alerts_created"] = alerts_count

        logger.info(f"Auto-healing completed: {stats}")
        return stats

    except Exception as e:
        logger.error(f"Auto-healing failed: {e}", exc_info=True)
        raise

async def recover_stuck_tasks(db: AsyncSession) -> int:
    """
    Recover tasks stuck in PROCESSING state > 60 minutes

    Returns:
        Number of tasks recovered
    """
    sixty_minutes_ago = datetime.utcnow() - timedelta(minutes=60)

    # Find stuck tasks
    result = await db.execute(
        select(TDSSyncQueue).where(
            and_(
                TDSSyncQueue.status == EventStatus.PROCESSING,
                TDSSyncQueue.processing_started_at < sixty_minutes_ago
            )
        )
    )
    stuck_tasks = result.scalars().all()

    if not stuck_tasks:
        return 0

    # Reset to pending
    for task in stuck_tasks:
        task.status = EventStatus.PENDING
        task.locked_by = None
        task.processing_started_at = None
        task.attempt_count = 0  # Reset attempts

        logger.warning(f"Recovered stuck task: {task.id} ({task.entity_type}/{task.source_entity_id})")

    await db.commit()

    logger.info(f"✅ Recovered {len(stuck_tasks)} stuck tasks")
    return len(stuck_tasks)

async def retry_dead_letter_queue(db: AsyncSession) -> int:
    """
    Retry items in dead letter queue (after 24 hours)

    Returns:
        Number of items retried
    """
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)

    # Find DLQ items that can be retried
    result = await db.execute(
        select(TDSSyncQueue).where(
            and_(
                TDSSyncQueue.status == EventStatus.DEAD_LETTER,
                TDSSyncQueue.dead_letter_at < twenty_four_hours_ago,
                TDSSyncQueue.attempt_count < 10  # Max 10 total attempts
            )
        ).limit(100)  # Limit to 100 per run
    )
    dlq_items = result.scalars().all()

    if not dlq_items:
        return 0

    # Reset to pending
    for item in dlq_items:
        item.status = EventStatus.PENDING
        item.locked_by = None
        item.error_message = None
        item.dead_letter_at = None
        # Don't reset attempt_count - track total attempts

        logger.info(f"Retrying DLQ item: {item.id} (attempt {item.attempt_count + 1})")

    await db.commit()

    logger.info(f"✅ Retried {len(dlq_items)} DLQ items")
    return len(dlq_items)

async def check_queue_health(db: AsyncSession) -> int:
    """
    Check queue health and create alerts if needed

    Returns:
        Number of alerts created
    """
    from sqlalchemy import func
    from app.models.zoho_sync import TDSAlert, AlertSeverity

    alerts_created = 0

    # Check queue depth
    result = await db.execute(
        select(func.count(TDSSyncQueue.id)).where(
            TDSSyncQueue.status == EventStatus.PENDING
        )
    )
    pending_count = result.scalar()

    # Alert if queue depth > 1000
    if pending_count > 1000:
        alert = TDSAlert(
            alert_type="queue_depth",
            severity=AlertSeverity.WARNING,
            title="High Queue Depth",
            message=f"Queue has {pending_count} pending items",
            metadata={"pending_count": pending_count}
        )
        db.add(alert)
        alerts_created += 1
        logger.warning(f"⚠️ High queue depth: {pending_count} items")

    # Check DLQ count
    result = await db.execute(
        select(func.count(TDSSyncQueue.id)).where(
            TDSSyncQueue.status == EventStatus.DEAD_LETTER
        )
    )
    dlq_count = result.scalar()

    # Alert if DLQ > 100
    if dlq_count > 100:
        alert = TDSAlert(
            alert_type="dlq_overflow",
            severity=AlertSeverity.ERROR,
            title="Dead Letter Queue Overflow",
            message=f"DLQ has {dlq_count} failed items",
            metadata={"dlq_count": dlq_count}
        )
        db.add(alert)
        alerts_created += 1
        logger.error(f"🚨 DLQ overflow: {dlq_count} items")

    if alerts_created > 0:
        await db.commit()

    return alerts_created
```

---

## 📊 Fix #4: Basic Monitoring Dashboard

Create simple health monitoring endpoint:

**File:** `app/routers/tds_monitoring.py` (NEW FILE)

```python
"""
TDS Monitoring Router
Basic monitoring and health check endpoints
"""
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any

from app.db.database import get_async_db
from app.models.zoho_sync import TDSSyncQueue, EventStatus, TDSAlert

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tds/monitoring", tags=["TDS Monitoring"])

@router.get("/health")
async def get_tds_health(db: AsyncSession = Depends(get_async_db)) -> Dict[str, Any]:
    """
    Get TDS system health overview

    Returns comprehensive health metrics
    """
    try:
        # Queue statistics
        pending = await db.scalar(
            select(func.count(TDSSyncQueue.id)).where(TDSSyncQueue.status == EventStatus.PENDING)
        )
        processing = await db.scalar(
            select(func.count(TDSSyncQueue.id)).where(TDSSyncQueue.status == EventStatus.PROCESSING)
        )
        completed = await db.scalar(
            select(func.count(TDSSyncQueue.id)).where(TDSSyncQueue.status == EventStatus.COMPLETED)
        )
        failed = await db.scalar(
            select(func.count(TDSSyncQueue.id)).where(TDSSyncQueue.status == EventStatus.FAILED)
        )
        dead_letter = await db.scalar(
            select(func.count(TDSSyncQueue.id)).where(TDSSyncQueue.status == EventStatus.DEAD_LETTER)
        )

        # Active alerts
        active_alerts = await db.scalar(
            select(func.count(TDSAlert.id)).where(TDSAlert.acknowledged == False)
        )

        # Calculate health status
        total = pending + processing + completed + failed + dead_letter
        success_rate = (completed / total * 100) if total > 0 else 100

        health_status = "healthy"
        if dead_letter > 100:
            health_status = "critical"
        elif pending > 1000:
            health_status = "warning"
        elif success_rate < 95:
            health_status = "degraded"

        return {
            "status": health_status,
            "timestamp": datetime.utcnow().isoformat(),
            "queue": {
                "pending": pending,
                "processing": processing,
                "completed": completed,
                "failed": failed,
                "dead_letter": dead_letter,
                "total": total
            },
            "metrics": {
                "success_rate": round(success_rate, 2),
                "active_alerts": active_alerts
            },
            "thresholds": {
                "queue_warning": 1000,
                "queue_critical": 5000,
                "dlq_warning": 50,
                "dlq_critical": 100
            }
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/scheduler/jobs")
async def get_scheduler_jobs() -> Dict[str, Any]:
    """Get status of all scheduled jobs"""
    from app.main import scheduler

    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger)
        })

    return {
        "jobs": jobs,
        "count": len(jobs),
        "scheduler_running": scheduler.running
    }
```

**Register router in main.py:**
```python
from app.routers import tds_monitoring

app.include_router(tds_monitoring.router)
```

---

## 🧪 Testing Plan

### Test 1: Webhook Fix Verification

```bash
# 1. Run test script for single webhook
python3 scripts/test_webhook_fix.py

# Expected: ✅ WEBHOOK PROCESSED SUCCESSFULLY!

# 2. Process all dead letter queue
python3 scripts/process_dead_letter_queue.py

# 3. Monitor queue status
PGPASSWORD="changeme" psql -h localhost -U tsh_admin -d tsh_erp -c \
  "SELECT status, COUNT(*) FROM tds_sync_queue GROUP BY status;"

# Expected:
#    status   | count
# -----------+-------
#  completed |    58  ← All 58 webhooks processed!
```

### Test 2: Scheduler Verification

```bash
# 1. Check scheduler status
curl http://localhost:8000/api/tds/monitoring/scheduler/jobs

# Expected: 5 jobs listed (daily_full_sync, hourly_sync, etc.)

# 2. Check next run times
# Should show next run times for all jobs

# 3. Monitor logs for scheduled execution
tail -f /var/log/tsh-erp/backend.log | grep "Starting.*job"

# Wait for next scheduled job to execute
```

### Test 3: Auto-Healing Verification

```bash
# 1. Manually trigger auto-healing
curl -X POST http://localhost:8000/api/bff/tds/auto-healing/run

# Expected: {"stuck_tasks_recovered": X, "dlq_items_retried": Y, ...}

# 2. Create a stuck task (for testing)
PGPASSWORD="changeme" psql -h localhost -U tsh_admin -d tsh_erp -c \
  "UPDATE tds_sync_queue SET status = 'PROCESSING', processing_started_at = NOW() - INTERVAL '2 hours' WHERE id = (SELECT id FROM tds_sync_queue LIMIT 1);"

# 3. Wait 15 minutes for auto-healing job
# Or trigger manually with curl command above

# 4. Verify task was recovered
PGPASSWORD="changeme" psql -h localhost -U tsh_admin -d tsh_erp -c \
  "SELECT status FROM tds_sync_queue WHERE id = '<task_id>';"

# Expected: status = 'PENDING' (recovered)
```

### Test 4: Monitoring Dashboard

```bash
# 1. Check health endpoint
curl http://localhost:8000/api/tds/monitoring/health

# Expected:
# {
#   "status": "healthy",
#   "queue": {"pending": X, "completed": Y, ...},
#   "metrics": {"success_rate": 99.5, ...}
# }

# 2. Check TDS dashboard
curl http://localhost:8000/api/bff/tds/dashboard/complete

# Should show updated statistics
```

---

## 📋 Deployment Checklist

### Pre-Deployment

- [ ] Backup production database
- [ ] Test all fixes on staging
- [ ] Verify webhook processing works (100% success)
- [ ] Verify scheduler jobs configured
- [ ] Verify auto-healing works

### Deployment Steps

```bash
# 1. Pull latest code
cd /home/deploy/TSH_ERP_Ecosystem
git pull origin develop

# 2. Install dependencies
pip install -r requirements.txt

# 3. Restart service
systemctl restart tsh-erp

# 4. Check logs
journalctl -u tsh-erp -f

# Look for:
# ✅ "TDS Scheduler started with 5 jobs"
# ✅ "Sync worker worker-1 started"
# ✅ "Sync worker worker-2 started"
```

### Post-Deployment Verification

```bash
# 1. Check system health
curl http://localhost:8000/api/tds/monitoring/health

# 2. Process dead letter queue
python3 scripts/process_dead_letter_queue.py

# 3. Monitor for 1 hour
# Watch logs, queue status, success rates

# 4. Verify scheduled jobs execute
# Wait for stock sync (15 min)
# Check logs for "Starting stock sync job..."
```

---

## ✅ Success Criteria

After implementing these fixes, you should have:

1. **Webhook Processing:**
   - ✅ 0 items in dead letter queue
   - ✅ 100% webhook processing success
   - ✅ < 1 second processing time

2. **Automation:**
   - ✅ 5 scheduled jobs running
   - ✅ Daily full sync at 2 AM
   - ✅ Hourly incremental sync
   - ✅ Stock sync every 15 minutes
   - ✅ Auto-healing every 15 minutes

3. **Auto-Healing:**
   - ✅ Stuck tasks recovered automatically
   - ✅ DLQ items retried after 24 hours
   - ✅ Alerts created for issues

4. **Monitoring:**
   - ✅ Health endpoint responding
   - ✅ Queue metrics visible
   - ✅ Scheduler status available

---

## 🎯 Next Steps (Phase 2)

After Phase 1 is complete and stable:

1. **Complete Statistics Engine** (comparators for all entities)
2. **Implement Circuit Breakers** (prevent cascading failures)
3. **Add Comprehensive Testing** (80% code coverage)
4. **Optimize Performance** (3x speed improvement)

---

**END OF PHASE 1 IMPLEMENTATION GUIDE**

Ready to implement? Run the fixes in this order:
1. Fix entity handlers (async context)
2. Test with single webhook
3. Process dead letter queue
4. Add APScheduler to main.py
5. Deploy auto-healing service
6. Add monitoring endpoints
7. Deploy and verify

Estimated time: 12-16 hours for complete implementation and testing.
