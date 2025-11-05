# Phase 2B: Background Jobs & Monitoring - Implementation Plan

**Date:** November 5, 2025
**Status:** Planning Complete
**Timeline:** 1-2 weeks
**Dependencies:** Phase 2A Complete ✅

---

## 📋 Executive Summary

Phase 2B focuses on moving long-running, non-critical operations to background workers, improving API response times and system reliability.

### Goals:
1. **Async Email Processing** - Move email sending to background queue
2. **Async Zoho Sync** - Decouple Zoho API calls from user requests
3. **Scheduled Tasks** - Automated reports, backups, cleanup
4. **Monitoring System** - Real-time metrics and alerting
5. **Task Management** - Retry logic, failure handling, task history

### Expected Benefits:
- **API Response Time:** -50% for endpoints with emails/sync
- **User Experience:** No waiting for external services
- **Reliability:** Automatic retries on failures
- **Visibility:** Real-time monitoring and alerts
- **Scalability:** Horizontal scaling of workers

---

## 🏗️ Architecture Overview

```
┌─────────────────┐
│  FastAPI App    │
│  (Web Server)   │
└────────┬────────┘
         │
         ├─ Immediate Response to User
         │
         └─ Queue Background Task
                  ↓
         ┌────────────────┐
         │  Redis Queue   │
         │  (Message Bus) │
         └────────┬───────┘
                  ↓
         ┌────────────────┐
         │ Celery Workers │
         │  (Processors)  │
         └────────┬───────┘
                  ↓
         ┌────────────────────────┐
         │  External Services     │
         │  - Email (SMTP)        │
         │  - Zoho Books API      │
         │  - File System         │
         └────────────────────────┘
```

---

## 🔧 Technology Stack

### Core Components:
1. **Celery** - Distributed task queue
2. **Redis** - Message broker & result backend
3. **Flower** - Real-time monitoring UI
4. **Prometheus** (Future) - Metrics collection
5. **Grafana** (Future) - Visualization dashboard

### Why Celery?
- ✅ Mature, battle-tested (13+ years)
- ✅ Native Python integration
- ✅ Built-in retry logic
- ✅ Scheduled task support (beat)
- ✅ Horizontal scalability
- ✅ Redis integration
- ✅ Monitoring tools (Flower)

---

## 📦 Phase 2B Components

### Part 1: Infrastructure Setup (Days 1-2)

#### 1.1 Celery Configuration
**File:** `app/celery/celery_app.py`

```python
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "tsh_erp",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        'app.celery.tasks.email_tasks',
        'app.celery.tasks.zoho_tasks',
        'app.celery.tasks.scheduled_tasks',
    ]
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)
```

**Environment Variables:**
```bash
# .env
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

#### 1.2 Task Base Classes
**File:** `app/celery/base_task.py`

- Automatic retry logic
- Failure logging
- Progress tracking
- Error notifications

#### 1.3 Systemd Service
**File:** `/etc/systemd/system/tsh-celery-worker.service`

```ini
[Unit]
Description=TSH ERP Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/opt/tsh_erp/releases/green
Environment="PATH=/opt/tsh_erp/venvs/green/bin"
EnvironmentFile=/opt/tsh_erp/shared/env/prod.env
ExecStart=/opt/tsh_erp/venvs/green/bin/celery -A app.celery.celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --max-tasks-per-child=1000 \
    --pidfile=/var/run/celery/worker.pid
ExecStop=/bin/kill -s TERM $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

### Part 2: Email Queue Tasks (Days 3-4)

#### 2.1 Email Task Types

**Order Confirmation Email:**
```python
@celery_app.task(bind=True, max_retries=3)
def send_order_confirmation_email(self, order_id: int):
    """Send order confirmation email to customer"""
    try:
        order = get_order(order_id)
        customer = order.customer

        email_service.send_email(
            to=customer.email,
            subject=f"Order Confirmation #{order.order_number}",
            template="order_confirmation",
            context={
                "order": order,
                "customer": customer,
                "items": order.items,
            }
        )

        log_email_sent(order_id, "order_confirmation")

    except SMTPException as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

**Invoice Email:**
```python
@celery_app.task(bind=True, max_retries=3)
def send_invoice_email(self, invoice_id: int):
    """Send invoice to customer with PDF attachment"""
```

**Payment Receipt:**
```python
@celery_app.task(bind=True, max_retries=3)
def send_payment_receipt(self, payment_id: int):
    """Send payment receipt to customer"""
```

**Welcome Email:**
```python
@celery_app.task(bind=True, max_retries=3)
def send_welcome_email(self, customer_id: int):
    """Send welcome email to new customer"""
```

#### 2.2 Email Queue Integration

**Before (Synchronous):**
```python
# In order creation endpoint
@router.post("/orders")
async def create_order(order_data: OrderCreate, db: Session):
    order = create_order_in_db(order_data, db)

    # ❌ This blocks the response
    send_email_service.send_order_confirmation(order.id)  # 2-3 seconds

    return order
```

**After (Asynchronous):**
```python
# In order creation endpoint
@router.post("/orders")
async def create_order(order_data: OrderCreate, db: Session):
    order = create_order_in_db(order_data, db)

    # ✅ Queue the task, return immediately
    send_order_confirmation_email.delay(order.id)  # ~5ms

    return order
```

**Response Time Improvement:**
- Before: 2,500ms (includes email sending)
- After: 500ms (just database operations)
- **Improvement: 80% faster**

---

### Part 3: Zoho Sync Queue Tasks (Days 5-6)

#### 3.1 Zoho Task Types

**Customer Sync:**
```python
@celery_app.task(bind=True, max_retries=5)
def sync_customer_to_zoho(self, customer_id: int):
    """Sync customer data to Zoho Books"""
    try:
        customer = get_customer(customer_id)

        if customer.zoho_contact_id:
            # Update existing
            zoho_api.update_contact(customer.zoho_contact_id, customer.to_zoho_dict())
        else:
            # Create new
            zoho_contact = zoho_api.create_contact(customer.to_zoho_dict())
            customer.zoho_contact_id = zoho_contact['contact_id']
            db.commit()

        log_zoho_sync(customer_id, "customer", "success")

    except ZohoAPIException as exc:
        log_zoho_sync(customer_id, "customer", "failed", str(exc))
        raise self.retry(exc=exc, countdown=300)  # Retry after 5 minutes
```

**Order Sync:**
```python
@celery_app.task(bind=True, max_retries=5)
def sync_order_to_zoho(self, order_id: int):
    """Sync order to Zoho Books as Sales Order"""
```

**Invoice Sync:**
```python
@celery_app.task(bind=True, max_retries=5)
def sync_invoice_to_zoho(self, invoice_id: int):
    """Sync invoice to Zoho Books"""
```

**Payment Sync:**
```python
@celery_app.task(bind=True, max_retries=5)
def sync_payment_to_zoho(self, payment_id: int):
    """Sync payment to Zoho Books"""
```

**Product Sync:**
```python
@celery_app.task(bind=True, max_retries=5)
def sync_product_to_zoho(self, product_id: int):
    """Sync product to Zoho Books as Item"""
```

#### 3.2 Bulk Sync Tasks

**Sync All Pending:**
```python
@celery_app.task
def sync_all_pending_to_zoho():
    """Process all pending Zoho sync queue entries"""
    pending_syncs = get_pending_zoho_syncs(limit=100)

    for sync in pending_syncs:
        if sync.entity_type == 'customer':
            sync_customer_to_zoho.delay(sync.entity_id)
        elif sync.entity_type == 'order':
            sync_order_to_zoho.delay(sync.entity_id)
        # ... etc
```

#### 3.3 Zoho Webhook Processing

**Process Incoming Webhook:**
```python
@celery_app.task
def process_zoho_webhook(self, webhook_data: dict):
    """Process incoming Zoho webhook asynchronously"""
    # Parse and process webhook
    # Update local database
    # Log the event
```

---

### Part 4: Scheduled Tasks (Days 7-8)

#### 4.1 Celery Beat Configuration

**File:** `app/celery/celery_beat.py`

```python
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    # Daily Reports
    'daily-sales-report': {
        'task': 'app.celery.tasks.scheduled_tasks.generate_daily_sales_report',
        'schedule': crontab(hour=8, minute=0),  # 8 AM daily
    },

    # Hourly Sync
    'sync-pending-zoho': {
        'task': 'app.celery.tasks.zoho_tasks.sync_all_pending_to_zoho',
        'schedule': crontab(minute=0),  # Every hour
    },

    # Daily Backup
    'daily-database-backup': {
        'task': 'app.celery.tasks.scheduled_tasks.backup_database',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    },

    # Weekly Cleanup
    'weekly-cleanup': {
        'task': 'app.celery.tasks.scheduled_tasks.cleanup_old_logs',
        'schedule': crontab(day_of_week=1, hour=3, minute=0),  # Monday 3 AM
    },

    # Monthly Reports
    'monthly-report': {
        'task': 'app.celery.tasks.scheduled_tasks.generate_monthly_report',
        'schedule': crontab(day_of_month=1, hour=9, minute=0),  # 1st of month, 9 AM
    },
}
```

#### 4.2 Report Tasks

**Daily Sales Report:**
```python
@celery_app.task
def generate_daily_sales_report():
    """Generate and email daily sales report to management"""
    yesterday = date.today() - timedelta(days=1)

    sales_data = get_sales_data(yesterday)
    report_pdf = generate_sales_report_pdf(sales_data)

    send_email(
        to=settings.MANAGEMENT_EMAILS,
        subject=f"Daily Sales Report - {yesterday}",
        body="Please find attached the daily sales report.",
        attachments=[('daily_sales_report.pdf', report_pdf)]
    )
```

**Low Stock Alert:**
```python
@celery_app.task
def check_low_stock_alert():
    """Check for low stock items and send alerts"""
    low_stock_items = get_low_stock_items()

    if low_stock_items:
        send_email(
            to=settings.INVENTORY_MANAGER_EMAIL,
            subject=f"Low Stock Alert - {len(low_stock_items)} Items",
            template="low_stock_alert",
            context={"items": low_stock_items}
        )
```

**Overdue Invoices:**
```python
@celery_app.task
def send_overdue_invoice_reminders():
    """Send reminders for overdue invoices"""
    overdue_invoices = get_overdue_invoices()

    for invoice in overdue_invoices:
        send_invoice_reminder_email.delay(invoice.id)
```

#### 4.3 Maintenance Tasks

**Database Backup:**
```python
@celery_app.task
def backup_database():
    """Backup database to S3/local storage"""
    backup_file = create_database_backup()
    upload_to_s3(backup_file)
    cleanup_old_backups(keep_last=30)
```

**Log Cleanup:**
```python
@celery_app.task
def cleanup_old_logs():
    """Remove logs older than 90 days"""
    delete_old_audit_logs(days=90)
    delete_old_celery_results(days=30)
```

**Cache Warmup:**
```python
@celery_app.task
def warm_up_caches():
    """Pre-warm frequently accessed caches"""
    # Warm up product caches
    # Warm up customer caches
    # Warm up dashboard caches
```

---

### Part 5: Monitoring & Management (Days 9-10)

#### 5.1 Flower Setup

**Installation:**
```bash
pip install flower
```

**Systemd Service:**
```ini
[Unit]
Description=TSH ERP Celery Flower
After=network.target redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/tsh_erp/releases/green
Environment="PATH=/opt/tsh_erp/venvs/green/bin"
EnvironmentFile=/opt/tsh_erp/shared/env/prod.env
ExecStart=/opt/tsh_erp/venvs/green/bin/celery -A app.celery.celery_app flower \
    --port=5555 \
    --basic_auth=admin:${FLOWER_PASSWORD}
Restart=always

[Install]
WantedBy=multi-user.target
```

**Access:** http://erp.tsh.sale:5555

**Features:**
- Real-time task monitoring
- Worker status
- Task history
- Task retry/revoke
- Statistics & charts

#### 5.2 Task Monitoring API

**File:** `app/routers/admin/celery_monitor.py`

```python
@router.get("/celery/stats")
async def get_celery_stats():
    """Get Celery worker and task statistics"""
    i = celery_app.control.inspect()

    return {
        "active_tasks": i.active(),
        "scheduled_tasks": i.scheduled(),
        "reserved_tasks": i.reserved(),
        "registered_tasks": i.registered(),
        "stats": i.stats(),
    }

@router.get("/celery/tasks")
async def get_recent_tasks(limit: int = 100):
    """Get recent task executions"""
    # Query from result backend
    return get_task_history(limit=limit)

@router.post("/celery/tasks/{task_id}/retry")
async def retry_failed_task(task_id: str):
    """Retry a failed task"""
    AsyncResult(task_id, app=celery_app).retry()
    return {"status": "retrying"}
```

#### 5.3 Health Checks

```python
@router.get("/health/celery")
async def celery_health_check():
    """Check if Celery workers are responding"""
    try:
        i = celery_app.control.inspect()
        active_workers = i.active()

        if not active_workers:
            return {"status": "unhealthy", "reason": "No active workers"}

        return {
            "status": "healthy",
            "workers": len(active_workers),
            "active_tasks": sum(len(tasks) for tasks in active_workers.values())
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

---

## 📊 Implementation Timeline

### Week 1: Core Infrastructure

**Day 1-2: Setup**
- [ ] Install Celery and dependencies
- [ ] Configure Celery app
- [ ] Create base task classes
- [ ] Set up systemd services
- [ ] Test basic task execution

**Day 3-4: Email Tasks**
- [ ] Create email task definitions
- [ ] Integrate with existing email service
- [ ] Update order/invoice endpoints
- [ ] Test email queue
- [ ] Monitor performance

**Day 5-6: Zoho Tasks**
- [ ] Create Zoho sync tasks
- [ ] Update Zoho integration points
- [ ] Test sync queue
- [ ] Handle error scenarios
- [ ] Monitor API usage

### Week 2: Scheduling & Monitoring

**Day 7-8: Scheduled Tasks**
- [ ] Configure Celery Beat
- [ ] Create report tasks
- [ ] Create maintenance tasks
- [ ] Test scheduled execution
- [ ] Verify cron schedules

**Day 9-10: Monitoring**
- [ ] Install and configure Flower
- [ ] Create monitoring API
- [ ] Set up health checks
- [ ] Create alerting rules
- [ ] Test monitoring dashboard

---

## 🔍 Testing Strategy

### Unit Tests:
```python
def test_send_email_task():
    """Test email task execution"""
    result = send_order_confirmation_email.delay(order_id=123)
    assert result.get(timeout=10) == "email_sent"

def test_zoho_sync_retry():
    """Test Zoho sync retry logic"""
    with mock.patch('zoho_api.create_contact', side_effect=ZohoAPIException):
        result = sync_customer_to_zoho.delay(customer_id=456)
        assert result.status == 'RETRY'
```

### Integration Tests:
- Test end-to-end order creation with email
- Test Zoho sync with real API (staging)
- Test scheduled task execution
- Test worker restart recovery

### Performance Tests:
- Measure API response time improvement
- Test worker throughput
- Test concurrent task handling
- Stress test with high load

---

## 📈 Success Metrics

### Performance:
- **Order Creation API:** < 500ms (currently ~2500ms with email)
- **Customer Update API:** < 300ms (currently ~1500ms with Zoho sync)
- **Email Queue Processing:** < 30 seconds per email
- **Zoho Sync Processing:** < 2 minutes per entity

### Reliability:
- **Email Success Rate:** > 99%
- **Zoho Sync Success Rate:** > 95%
- **Task Retry Success:** > 90%
- **Worker Uptime:** > 99.9%

### Monitoring:
- **Active Workers:** Always >= 1
- **Failed Tasks:** < 1% of total
- **Queue Length:** < 1000 at any time
- **Average Task Time:** < 5 minutes

---

## 🚀 Deployment Plan

### Staging Deployment (Day 11):
1. Deploy to staging server
2. Run comprehensive tests
3. Monitor for 24 hours
4. Fix any issues

### Production Deployment (Day 12):
1. Deploy during low-traffic window
2. Start with 1 worker
3. Monitor closely for 2 hours
4. Scale to 4 workers if stable
5. Monitor for 24 hours

### Rollback Plan:
- Keep synchronous code as fallback
- Feature flag for async processing
- Can disable workers without affecting app

---

## 💰 Resource Requirements

### Server Resources:
- **Celery Workers:** 1-4 workers (1GB RAM each)
- **Redis:** Already running (increase memory to 512MB)
- **Flower:** Minimal (~100MB RAM)

### External Services:
- **Email:** Existing SMTP server
- **Zoho API:** Existing account (monitor rate limits)

### Development Time:
- **Backend:** 10 days (1 developer)
- **Testing:** 2 days
- **Deployment:** 1 day
- **Total:** ~2 weeks

---

## 🎯 Phase 2B Deliverables

### Code:
- [ ] Celery app configuration
- [ ] 15+ background tasks
- [ ] Email queue integration
- [ ] Zoho queue integration
- [ ] Scheduled tasks
- [ ] Monitoring API
- [ ] Health checks

### Documentation:
- [ ] Task definitions
- [ ] Deployment guide
- [ ] Monitoring guide
- [ ] Troubleshooting guide
- [ ] API documentation

### Infrastructure:
- [ ] Celery worker service
- [ ] Celery beat service
- [ ] Flower monitoring
- [ ] Health checks
- [ ] Alerting setup

---

## ⚠️ Risks & Mitigation

### Risk 1: Task Failures
**Mitigation:**
- Automatic retry with exponential backoff
- Failed task logging and alerting
- Manual retry capability

### Risk 2: Queue Buildup
**Mitigation:**
- Monitor queue length
- Scale workers dynamically
- Set task priorities

### Risk 3: Worker Crashes
**Mitigation:**
- Systemd auto-restart
- Health monitoring
- Multiple workers for redundancy

### Risk 4: Email/Zoho API Limits
**Mitigation:**
- Rate limiting in tasks
- Queue backpressure
- Fallback to sync if queue fails

---

## 📚 References

- **Celery Documentation:** https://docs.celeryproject.org/
- **Flower Documentation:** https://flower.readthedocs.io/
- **Redis Documentation:** https://redis.io/documentation
- **Best Practices:** https://docs.celeryproject.org/en/stable/userguide/tasks.html#best-practices

---

**Plan Status:** ✅ Complete - Ready for Implementation
**Next Step:** Begin Day 1 - Celery Setup
**Expected Completion:** 2 weeks from start

🤖 Generated with [Claude Code](https://claude.com/claude-code)
