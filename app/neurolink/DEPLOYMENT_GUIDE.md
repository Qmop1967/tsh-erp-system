# TSH NeuroLink - Deployment & Integration Guide

## 🚀 Overview

TSH NeuroLink is the central communication and notification system for the TSH ERP Ecosystem. It provides event-driven notifications, multi-channel delivery, and contextual messaging capabilities.

## 📍 Production Endpoints

| Service | URL | Status |
|---------|-----|--------|
| **API Root** | https://erp.tsh.sale/api/neurolink/ | ✅ Operational |
| **Health Check** | https://erp.tsh.sale/api/neurolink/health | ✅ Healthy |
| **Events API** | https://erp.tsh.sale/api/neurolink/v1/events | ✅ Ready |
| **Notifications API** | https://erp.tsh.sale/api/neurolink/v1/notifications | ✅ Ready |
| **WebSocket** | wss://erp.tsh.sale/neurolink-ws | ✅ Configured |

### Docker Container

- **Container**: `tsh_neurolink`
- **Image**: `tsh-neurolink:latest`
- **Port**: 8002
- **Network**: `tsh_erp_ecosystem_tsh_network`
- **Status**: Running with 4 workers
- **Health**: Monitored via `/health` endpoint every 30s

## 🗄️ Database Schema

### Tables Created (15 total)

1. **neurolink_events** - Business events from TSH modules
2. **neurolink_notification_rules** - Rule engine configuration
3. **neurolink_notifications** - User-specific notifications
4. **neurolink_delivery_log** - Multi-channel delivery tracking
5. **neurolink_messages** - Contextual chat about events
6. **neurolink_user_preferences** - Per-user notification settings
7. **neurolink_announcements** - System-wide announcements
8. **neurolink_announcement_acknowledgments** - Acknowledgment tracking
9. **neurolink_emergency_broadcasts** - Critical emergency messages
10. **neurolink_emergency_broadcast_acknowledgments** - Emergency ACKs
11. **neurolink_campaigns** - Notification campaigns
12. **neurolink_scheduled_notifications** - Scheduled messages
13. **neurolink_topics** - Notification topics/channels
14. **neurolink_user_topic_subscriptions** - User topic subscriptions
15. **neurolink_metrics** - System performance metrics

## 🔧 Notification Rules

### Active Rules (9 configured)

| Rule Name | Source | Event Pattern | Priority | Channels |
|-----------|--------|---------------|----------|----------|
| **price_list_updated_sales_team** | TDS | price_list.updated | 100 | in_app, push, email |
| **invoice_overdue** | Invoicing | invoice.overdue | 100 | in_app, push, email |
| **sync_failed_critical** | TDS | sync.failed | 95 | in_app, push, email |
| **low_stock_alert** | Inventory | stock.low | 90 | in_app, push |
| **sync_completed_low_success** | TDS | sync.completed | 90 | in_app |
| **stock_discrepancy_large** | TDS | stock.discrepancy | 85 | in_app, email |
| **sync_completed_success** | TDS | sync.completed | 50 | in_app |
| **order_approved** | Sales | order.approved | 50 | in_app |
| **image_sync_completed** | TDS | image_sync.completed | 40 | in_app |

### Price List Update Notification

**Rule**: `price_list_updated_sales_team`

**Trigger**: When TDS completes price list sync from Zoho

**Template**:
```json
{
  "title": "💰 Price List Updated: {{price_list_name}}",
  "body": "{{products_updated}} products have been updated in {{price_list_name}}. Please review the new prices before quoting to customers.",
  "severity": "warning",
  "action_url": "/products/prices",
  "action_label": "View Updated Prices",
  "channels": ["in_app", "push", "email"],
  "recipient_roles": ["sales_rep", "sales_manager", "warehouse_manager"]
}
```

## 🔌 Integration Guide

### For TSH Modules (Event Emission)

#### 1. Import the NeuroLink Emitter

```python
from app.utils.neurolink_emitter import neurolink_emitter
```

#### 2. Emit Events

**Basic Event Emission:**
```python
await neurolink_emitter.emit_event(
    source_module="your_module",
    event_type="your.event.type",
    payload={
        "key": "value",
        "details": "event details"
    },
    severity="info",  # info, warning, error, critical
    branch_id=branch_id,
    user_id=user_id
)
```

**Price List Update Event:**
```python
await neurolink_emitter.emit_price_list_updated(
    price_list_name="Consumer Price List",
    products_updated=150,
    sync_duration=45.3,
    source="zoho",
    details={
        "total_processed": 150,
        "failed": 0,
        "success_rate": 100.0
    }
)
```

**Sync Completed Event:**
```python
await neurolink_emitter.emit_sync_completed(
    entity_type="products",
    total_processed=1250,
    successful=1234,
    failed=16,
    duration=45.3
)
```

#### 3. Event Structure

```python
{
    "source_module": str,           # Module name (e.g., "tds", "inventory")
    "event_type": str,              # Event type (e.g., "price_list.updated")
    "severity": str,                # info, warning, error, critical
    "occurred_at": datetime,        # When the event occurred
    "payload": dict,                # Event-specific data
    "producer_idempotency_key": str,  # Prevents duplicates (optional)
    "correlation_id": str,          # Groups related events (optional)
    "branch_id": int,               # Branch context (optional)
    "user_id": int,                 # User context (optional)
    "tags": List[str]               # Tags for categorization (optional)
}
```

### For Frontend Applications

#### Flutter App (Consumer App)

**1. Firebase Configuration**
```dart
// Initialize Firebase
await Firebase.initializeApp();

// Initialize notification service
final notificationService = FirebaseNotificationService();
await notificationService.initialize();

// Listen to foreground messages
FirebaseMessaging.onMessage.listen((RemoteMessage message) {
  // Handle foreground notification
  _showLocalNotification(message);
});
```

**2. Fetch User Notifications**
```dart
// GET /api/neurolink/v1/notifications/my
final response = await http.get(
  Uri.parse('$apiUrl/v1/notifications/my'),
  headers: {
    'Authorization': 'Bearer $token',
  },
);

final List<dynamic> notifications = jsonDecode(response.body);
```

**3. Mark as Read**
```dart
// PUT /api/neurolink/v1/notifications/{id}/read
await http.put(
  Uri.parse('$apiUrl/v1/notifications/$notificationId/read'),
  headers: {'Authorization': 'Bearer $token'},
);
```

**4. Acknowledge Notification**
```dart
// POST /api/neurolink/v1/notifications/{id}/acknowledge
await http.post(
  Uri.parse('$apiUrl/v1/notifications/$notificationId/acknowledge'),
  headers: {'Authorization': 'Bearer $token'},
);
```

#### React/Next.js Admin Dashboard

**1. Create Announcement**
```typescript
// POST /api/neurolink/v1/announcements
const response = await fetch('/api/neurolink/v1/announcements', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  },
  body: JSON.stringify({
    title: 'System Maintenance Notice',
    content: 'Scheduled maintenance on Sunday 2AM-4AM',
    severity: 'warning',
    target_type: 'all',
    requires_acknowledgment: true,
    delivery_channels: ['in_app', 'email', 'push'],
    publish_at: '2025-11-15T00:00:00Z',
    expires_at: '2025-11-16T00:00:00Z'
  })
});
```

**2. List Announcements**
```typescript
// GET /api/neurolink/v1/announcements
const response = await fetch('/api/neurolink/v1/announcements?status=published', {
  headers: {
    'Authorization': `Bearer ${token}`,
  },
});

const announcements = await response.json();
```

## 📊 API Endpoints

### Events API (`/v1/events`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/v1/events` | Ingest new event | ✅ Yes |
| GET | `/v1/events` | List events with filters | ✅ Yes |
| GET | `/v1/events/{id}` | Get specific event | ✅ Yes |
| GET | `/v1/events/stats/summary` | Event statistics | ✅ Yes |

### Notifications API (`/v1/notifications`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/v1/notifications/my` | Get user's notifications | ✅ Yes |
| GET | `/v1/notifications/{id}` | Get specific notification | ✅ Yes |
| PUT | `/v1/notifications/{id}/read` | Mark as read | ✅ Yes |
| POST | `/v1/notifications/{id}/acknowledge` | Acknowledge notification | ✅ Yes |
| DELETE | `/v1/notifications/{id}` | Dismiss notification | ✅ Yes |
| GET | `/v1/notifications/stats` | User notification stats | ✅ Yes |

### Announcements API (`/v1/announcements`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/v1/announcements` | Create announcement | ✅ Admin |
| GET | `/v1/announcements` | List announcements | ✅ Yes |
| GET | `/v1/announcements/{id}` | Get announcement | ✅ Yes |
| PUT | `/v1/announcements/{id}` | Update announcement | ✅ Admin |
| DELETE | `/v1/announcements/{id}` | Delete announcement | ✅ Admin |
| POST | `/v1/announcements/{id}/publish` | Publish announcement | ✅ Admin |
| POST | `/v1/announcements/{id}/acknowledge` | Acknowledge | ✅ Yes |

### System Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/health` | Health check | ❌ No |
| GET | `/` | API information | ❌ No |

## 🔐 Authentication

All API endpoints (except `/health` and `/`) require JWT authentication.

**Header Format:**
```
Authorization: Bearer <your-jwt-token>
```

**Token Source:**
- Use the same JWT token from TSH ERP authentication
- Token is issued by the main TSH ERP system
- Token contains user context (user_id, branch_id, role)

## 🎯 Use Cases

### 1. Automatic Price List Updates
When TDS syncs price lists from Zoho, sales team receives notifications automatically.

**Flow:**
1. TDS completes price list sync
2. TDS emits `price_list.updated` event
3. NeuroLink rule engine matches event
4. Notifications created for sales_rep, sales_manager, warehouse_manager roles
5. Delivered via in-app, push, and email channels

### 2. Low Stock Alerts
When inventory drops below threshold, warehouse managers receive alerts.

### 3. System Announcements
Admins can broadcast important messages to all users or specific roles/branches.

### 4. Emergency Broadcasts
Critical system messages that bypass user preferences and require acknowledgment.

### 5. Sync Failure Alerts
When TDS sync fails, technical team receives immediate critical alerts.

## 🔧 Environment Configuration

**Required Environment Variables:**

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/tsh_erp

# Redis (Event Bus)
REDIS_URL=redis://host:6379/2

# Security
JWT_SECRET_KEY=your_secret_key_here

# Email Delivery (Resend)
RESEND_API_KEY=re_xxxxxxxxxxxx

# Push Notifications (Firebase)
FIREBASE_CREDENTIALS_PATH=/app/firebase/service-account.json

# Application
ENVIRONMENT=production
DEBUG=False
```

## 🧪 Testing

### Test Event Emission from TDS

```python
# In TDS sync handler
from app.utils.neurolink_emitter import neurolink_emitter

# After successful price list sync
await neurolink_emitter.emit_price_list_updated(
    price_list_name="Consumer Price List",
    products_updated=150,
    sync_duration=45.3
)
```

### Test Health Check

```bash
curl https://erp.tsh.sale/api/neurolink/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-10T08:00:00.000000",
  "database": "connected",
  "redis": "connected"
}
```

### Check Notification Rules

```sql
SELECT id, name, source_module, event_type_pattern, is_active, priority
FROM neurolink_notification_rules
WHERE is_active = true
ORDER BY priority DESC;
```

## 📈 Monitoring

### Docker Container Status

```bash
docker ps --filter name=tsh_neurolink
```

### Container Logs

```bash
docker logs tsh_neurolink --tail 50 --follow
```

### Health Monitoring

The container includes a health check that runs every 30 seconds:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1
```

### Database Metrics

```sql
-- Total events ingested
SELECT COUNT(*) FROM neurolink_events;

-- Events by module
SELECT source_module, COUNT(*)
FROM neurolink_events
GROUP BY source_module;

-- Notifications by status
SELECT status, COUNT(*)
FROM neurolink_notifications
GROUP BY status;

-- Delivery success rate
SELECT
    channel,
    COUNT(*) as total,
    SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as delivered,
    ROUND(SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100, 2) as success_rate
FROM neurolink_delivery_log
GROUP BY channel;
```

## 🚨 Troubleshooting

### Container Not Starting

```bash
# Check logs
docker logs tsh_neurolink

# Check environment variables
docker exec tsh_neurolink env | grep -E 'DATABASE|REDIS|JWT'

# Restart container
docker restart tsh_neurolink
```

### Database Connection Issues

```bash
# Test database connectivity from container
docker exec tsh_neurolink python -c "from app.database import test_connection; import asyncio; asyncio.run(test_connection())"

# Verify DATABASE_URL
docker exec tsh_neurolink printenv DATABASE_URL
```

### Events Not Creating Notifications

1. Check if rule is active:
```sql
SELECT * FROM neurolink_notification_rules WHERE event_type_pattern = 'your.event.type';
```

2. Check if events are being received:
```sql
SELECT * FROM neurolink_events ORDER BY ingested_at DESC LIMIT 10;
```

3. Check background worker logs:
```bash
docker logs tsh_neurolink | grep "Rule Engine"
```

## 📝 Next Steps

1. **Configure API Keys**:
   - Set `RESEND_API_KEY` for email delivery
   - Add Firebase service account JSON for push notifications

2. **Test End-to-End**:
   - Trigger TDS price list sync
   - Verify notification appears in Flutter app
   - Check email delivery

3. **Create First Announcement**:
   - Access Admin Dashboard
   - Create test announcement
   - Verify delivery to users

4. **Monitor Performance**:
   - Track event ingestion rate
   - Monitor notification delivery success
   - Review system metrics

## 📞 Support

For issues or questions:
- Check container logs: `docker logs tsh_neurolink`
- Verify database schema: All 15 NeuroLink tables present
- Test health endpoint: https://erp.tsh.sale/api/neurolink/health
- Review notification rules: Check priority and active status

---

**Deployment Date**: 2025-11-10
**Version**: 1.0.0
**Status**: ✅ Production Ready
