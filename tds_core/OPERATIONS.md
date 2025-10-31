# TDS Core - Operations Guide

## Overview

This guide covers day-to-day operations, monitoring, troubleshooting, and management of TDS Core.

**Production URL:** https://api.tsh.sale/tds/
**Dashboard:** https://api.tsh.sale/tds/dashboard/
**Server:** 167.71.39.50

---

## Table of Contents

1. [Service Management](#service-management)
2. [Monitoring Dashboard](#monitoring-dashboard)
3. [Queue Management](#queue-management)
4. [Alert Management](#alert-management)
5. [Manual Interventions](#manual-interventions)
6. [Common Operations](#common-operations)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## Service Management

### Starting and Stopping Services

```bash
# SSH into server
ssh root@167.71.39.50

# Check service status
systemctl status tds-core-api
systemctl status tds-core-worker

# Start services
systemctl start tds-core-api
systemctl start tds-core-worker

# Stop services
systemctl stop tds-core-api
systemctl stop tds-core-worker

# Restart services
systemctl restart tds-core-api
systemctl restart tds-core-worker

# Graceful reload (API only - no downtime)
systemctl reload tds-core-api
```

### Viewing Logs

```bash
# Real-time API logs
journalctl -u tds-core-api -f

# Real-time Worker logs
journalctl -u tds-core-worker -f

# Last 100 lines
journalctl -u tds-core-api -n 100

# Errors only
journalctl -u tds-core-api -p err -f

# Specific time range
journalctl -u tds-core-api --since "2024-10-31 10:00:00" --until "2024-10-31 11:00:00"

# Export to file
journalctl -u tds-core-api --since "1 hour ago" > /tmp/api-logs.txt
```

### Service Health Check

```bash
# Quick health check
curl https://api.tsh.sale/tds/health

# Expected response:
{
  "status": "healthy",
  "app_name": "TDS_Core",
  "version": "1.0.0",
  "timestamp": "2024-10-31T10:00:00.000000"
}
```

---

## Monitoring Dashboard

### Dashboard Endpoints

All dashboard endpoints are available at `https://api.tsh.sale/tds/dashboard/`

#### 1. System Metrics

**Endpoint:** `GET /dashboard/metrics`

**Purpose:** Get comprehensive system health overview

**Response:**
```json
{
  "timestamp": "2024-10-31T10:00:00.000000",
  "queue": {
    "by_status": {
      "pending": 150,
      "processing": 5,
      "retry": 10,
      "completed": 45000,
      "dead_letter": 25
    },
    "oldest_pending_age_seconds": 120.5,
    "dead_letter_count": 25
  },
  "processing": {
    "last_hour": {
      "total_processed": 1250,
      "succeeded": 1235,
      "failed": 15,
      "success_rate_percent": 98.8,
      "avg_duration_seconds": 2.34
    }
  },
  "database": {
    "table_sizes": [...],
    "active_connections": 12
  },
  "active_alerts": [...]
}
```

**Usage:**
```bash
# Get current metrics
curl https://api.tsh.sale/tds/dashboard/metrics

# Pretty print with jq
curl -s https://api.tsh.sale/tds/dashboard/metrics | jq .
```

#### 2. Queue Statistics

**Endpoint:** `GET /dashboard/queue-stats`

**Purpose:** Detailed queue breakdown by status

**Response:**
```json
{
  "pending": 150,
  "processing": 5,
  "retry": 10,
  "completed": 45000,
  "dead_letter": 25,
  "total": 45190
}
```

#### 3. Recent Events

**Endpoint:** `GET /dashboard/recent-events?limit=50&status_filter=failed`

**Parameters:**
- `limit` (optional): Number of events to return (default: 50)
- `status_filter` (optional): Filter by status (pending, processing, retry, completed, dead_letter)

**Purpose:** View recent sync events for monitoring and debugging

**Response:**
```json
[
  {
    "id": "uuid",
    "event_type": "contact.created",
    "entity_id": "12345",
    "status": "completed",
    "attempt_count": 1,
    "priority": 1,
    "queued_at": "2024-10-31T09:55:00.000000",
    "started_at": "2024-10-31T09:55:02.000000",
    "completed_at": "2024-10-31T09:55:04.000000",
    "error_message": null
  }
]
```

**Usage:**
```bash
# Get last 50 events
curl https://api.tsh.sale/tds/dashboard/recent-events?limit=50

# Get failed events only
curl https://api.tsh.sale/tds/dashboard/recent-events?status_filter=dead_letter

# Get pending events
curl https://api.tsh.sale/tds/dashboard/recent-events?status_filter=pending
```

#### 4. Dead Letter Queue

**Endpoint:** `GET /dashboard/dead-letter?limit=50`

**Purpose:** View permanently failed events that require manual intervention

**Response:**
```json
[
  {
    "id": "uuid",
    "original_queue_id": "uuid",
    "event_type": "contact.created",
    "entity_id": "12345",
    "payload": {...},
    "attempt_count": 3,
    "last_error": "Database connection timeout",
    "moved_to_dlq_at": "2024-10-31T09:00:00.000000",
    "retry_count": 0,
    "last_retry_at": null
  }
]
```

**Usage:**
```bash
# Get dead letter events
curl https://api.tsh.sale/tds/dashboard/dead-letter

# Get with details
curl -s https://api.tsh.sale/tds/dashboard/dead-letter | jq '.[0]'
```

---

## Queue Management

### Understanding Queue Status

**Status Flow:**
```
PENDING → PROCESSING → COMPLETED
    ↓          ↓
  RETRY ← ← FAILED
    ↓
DEAD_LETTER (after 3 attempts)
```

**Status Definitions:**
- **PENDING** - Newly queued, waiting for worker
- **PROCESSING** - Currently being processed by worker
- **RETRY** - Failed, scheduled for retry
- **COMPLETED** - Successfully processed
- **DEAD_LETTER** - Permanently failed after max retries

### Monitoring Queue Health

**Key Metrics to Watch:**

1. **Pending Queue Size**
   - Normal: < 100 events
   - Warning: 100-500 events
   - Critical: > 500 events

2. **Processing Events**
   - Normal: 1-10 events (depending on concurrency)
   - Warning: Stuck at same number for >5 minutes

3. **Dead Letter Queue**
   - Normal: < 10 events
   - Warning: 10-50 events
   - Critical: > 50 events

4. **Success Rate**
   - Healthy: > 95%
   - Warning: 90-95%
   - Critical: < 90%

**Check Queue Status:**
```bash
# Via API
curl -s https://api.tsh.sale/tds/dashboard/queue-stats | jq .

# Via Database
ssh root@167.71.39.50
psql -h aws-1-eu-north-1.pooler.supabase.com \
     -U postgres.trjjglxhteqnzmyakxhe \
     -d postgres \
     -c "SELECT status, COUNT(*) FROM tds_sync_queue GROUP BY status;"
```

### Queue Backlog Resolution

**If pending queue is growing:**

1. **Check worker is running:**
   ```bash
   systemctl status tds-core-worker
   ```

2. **Check worker logs for errors:**
   ```bash
   journalctl -u tds-core-worker -n 100
   ```

3. **Increase worker concurrency (temporary):**
   ```bash
   # Edit .env
   nano /opt/tds_core/.env
   # Change: WORKER_CONCURRENCY=10

   # Restart worker
   systemctl restart tds-core-worker
   ```

4. **Monitor processing rate:**
   ```bash
   # Watch queue size decrease
   watch -n 5 'curl -s https://api.tsh.sale/tds/dashboard/queue-stats | jq .pending'
   ```

---

## Alert Management

### Viewing Active Alerts

**Endpoint:** `GET /dashboard/metrics` (includes active_alerts array)

**Alert Severity Levels:**
- **critical** - Immediate action required
- **warning** - Should be addressed soon
- **info** - Informational only

**Common Alerts:**

| Alert Title | Severity | Threshold | Action |
|-------------|----------|-----------|--------|
| Queue Backlog Critical | critical | >1000 pending | Increase worker concurrency |
| Queue Backlog Warning | warning | >500 pending | Monitor, may need scaling |
| High Dead Letter Queue | critical | >100 DLQ | Investigate failures, manual retry |
| Elevated Dead Letter Queue | warning | >50 DLQ | Review error patterns |
| Stuck Events Detected | warning | Events processing >1hr | Check worker health |
| High Failure Rate | critical | >10% failures | Investigate root cause |
| Elevated Failure Rate | warning | >5% failures | Monitor error logs |

### Acknowledging Alerts

**Endpoint:** `POST /dashboard/alerts/{alert_id}/acknowledge`

**Purpose:** Mark alert as acknowledged (stops notifications)

**Usage:**
```bash
# Get alert ID from metrics endpoint
ALERT_ID=$(curl -s https://api.tsh.sale/tds/dashboard/metrics | jq -r '.active_alerts[0].id')

# Acknowledge alert
curl -X POST https://api.tsh.sale/tds/dashboard/alerts/$ALERT_ID/acknowledge

# Response:
{
  "success": true,
  "message": "Alert acknowledged"
}
```

---

## Manual Interventions

### Retrying Failed Events

**Endpoint:** `POST /dashboard/dead-letter/{event_id}/retry`

**Purpose:** Move event from dead letter queue back to processing queue

**Process:**
1. Identify failed event
2. Investigate root cause
3. Fix underlying issue
4. Retry event manually

**Usage:**
```bash
# Step 1: Get dead letter events
curl -s https://api.tsh.sale/tds/dashboard/dead-letter | jq '.[] | {id, event_type, last_error}'

# Step 2: Identify event to retry
EVENT_ID="uuid-of-failed-event"

# Step 3: Retry event
curl -X POST https://api.tsh.sale/tds/dashboard/dead-letter/$EVENT_ID/retry

# Response:
{
  "success": true,
  "message": "Event moved from DLQ to processing queue",
  "queue_id": "new-uuid"
}

# Step 4: Monitor processing
curl -s https://api.tsh.sale/tds/dashboard/recent-events | jq ".[] | select(.id == \"$EVENT_ID\")"
```

**When to Retry:**
- Transient errors (network timeout, database connection)
- After fixing data issues in source system
- After deploying bug fixes

**When NOT to Retry:**
- Invalid data that can't be fixed
- Duplicate entries
- Business logic errors without fix

### Bulk Retry Operations

**For multiple failed events:**

```bash
# Get all DLQ event IDs
DLQ_IDS=$(curl -s https://api.tsh.sale/tds/dashboard/dead-letter | jq -r '.[].id')

# Retry each (be careful - ensure root cause is fixed!)
for EVENT_ID in $DLQ_IDS; do
  echo "Retrying $EVENT_ID..."
  curl -X POST https://api.tsh.sale/tds/dashboard/dead-letter/$EVENT_ID/retry
  sleep 1  # Rate limiting
done
```

### Purging Old Events

**Clean up completed events older than 30 days:**

```sql
-- SSH to server and connect to database
ssh root@167.71.39.50

PGPASSWORD="your-password" psql \
  -h aws-1-eu-north-1.pooler.supabase.com \
  -U postgres.trjjglxhteqnzmyakxhe \
  -d postgres

-- Delete old completed events
DELETE FROM tds_sync_queue
WHERE status = 'completed'
  AND completed_at < NOW() - INTERVAL '30 days';

-- Delete old inbox events (already processed)
DELETE FROM tds_inbox_events
WHERE processed = true
  AND processed_at < NOW() - INTERVAL '30 days';

-- Vacuum to reclaim space
VACUUM ANALYZE tds_sync_queue;
VACUUM ANALYZE tds_inbox_events;
```

---

## Common Operations

### Daily Health Check

**Morning routine:**

```bash
# 1. Check service status
ssh root@167.71.39.50 "systemctl status tds-core-api tds-core-worker"

# 2. Check system metrics
curl -s https://api.tsh.sale/tds/dashboard/metrics | jq '{
  pending: .queue.by_status.pending,
  processing: .queue.by_status.processing,
  dlq: .queue.dead_letter_count,
  success_rate: .processing.last_hour.success_rate_percent,
  alerts: (.active_alerts | length)
}'

# 3. Check for new alerts
curl -s https://api.tsh.sale/tds/dashboard/metrics | jq '.active_alerts'

# 4. Review recent errors
ssh root@167.71.39.50 "journalctl -u tds-core-worker -p err --since '24 hours ago'"
```

### Weekly Review

```bash
# 1. Review dead letter queue
curl -s https://api.tsh.sale/tds/dashboard/dead-letter | jq 'group_by(.event_type) | map({event_type: .[0].event_type, count: length})'

# 2. Check database growth
ssh root@167.71.39.50
psql ... -c "
SELECT
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE tablename LIKE 'tds_%'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"

# 3. Review processing performance
curl -s https://api.tsh.sale/tds/dashboard/metrics | jq '.processing.last_hour'
```

### Investigating Specific Event

```bash
# Get event details by ID
EVENT_ID="your-event-id"

# Check queue status
psql ... -c "SELECT * FROM tds_sync_queue WHERE id = '$EVENT_ID';"

# Check inbox (original webhook)
psql ... -c "SELECT * FROM tds_inbox_events WHERE event_id = '$EVENT_ID';"

# Check sync logs
psql ... -c "SELECT * FROM tds_sync_logs WHERE queue_id = '$EVENT_ID' ORDER BY created_at DESC;"

# Check if in DLQ
psql ... -c "SELECT * FROM tds_dead_letter_queue WHERE original_queue_id = '$EVENT_ID';"
```

---

## Troubleshooting

### Problem: High Queue Backlog

**Symptoms:**
- Pending queue >500 events
- Events taking long time to process
- Alert: "Queue Backlog Warning/Critical"

**Diagnosis:**
```bash
# Check worker status
systemctl status tds-core-worker

# Check worker logs
journalctl -u tds-core-worker -n 100

# Check processing rate
curl -s https://api.tsh.sale/tds/dashboard/metrics | jq '.processing.last_hour'
```

**Solutions:**

1. **Worker not running:**
   ```bash
   systemctl start tds-core-worker
   ```

2. **Worker slow/stuck:**
   ```bash
   systemctl restart tds-core-worker
   ```

3. **Need more capacity:**
   ```bash
   # Increase concurrency in .env
   WORKER_CONCURRENCY=10
   systemctl restart tds-core-worker
   ```

### Problem: High Failure Rate

**Symptoms:**
- Success rate <95%
- Growing dead letter queue
- Alert: "High Failure Rate"

**Diagnosis:**
```bash
# Get recent failures
curl -s https://api.tsh.sale/tds/dashboard/dead-letter?limit=10 | jq '.[].last_error'

# Check error patterns
journalctl -u tds-core-worker -p err --since "1 hour ago"

# Group errors by type
curl -s https://api.tsh.sale/tds/dashboard/dead-letter | jq 'group_by(.last_error) | map({error: .[0].last_error, count: length})'
```

**Common Causes:**

1. **Database connection issues:**
   ```bash
   # Check database connectivity
   psql -h aws-1-eu-north-1.pooler.supabase.com ... -c "SELECT 1;"

   # Check connection pool
   curl -s https://api.tsh.sale/tds/dashboard/metrics | jq '.database'
   ```

2. **Invalid webhook data:**
   - Review payload in DLQ events
   - Check Zoho Books webhook configuration
   - Update entity handlers if needed

3. **Handler bugs:**
   - Review error logs for stack traces
   - Deploy fixes
   - Retry failed events

### Problem: Events Stuck in Processing

**Symptoms:**
- Events in "processing" status for >1 hour
- Alert: "Stuck Events Detected"

**Diagnosis:**
```bash
# Find stuck events
psql ... -c "
SELECT id, event_type, started_at, NOW() - started_at as duration
FROM tds_sync_queue
WHERE status = 'processing'
  AND started_at < NOW() - INTERVAL '1 hour';
"
```

**Solutions:**

1. **Worker crashed during processing:**
   ```bash
   # Reset stuck events to pending
   psql ... -c "
   UPDATE tds_sync_queue
   SET status = 'pending', started_at = NULL
   WHERE status = 'processing'
     AND started_at < NOW() - INTERVAL '1 hour';
   "

   # Restart worker
   systemctl restart tds-core-worker
   ```

2. **Long-running handler:**
   - Identify handler causing delay
   - Optimize handler code
   - Add timeout to handler

### Problem: Database Connection Pool Exhausted

**Symptoms:**
- Errors: "connection pool exhausted"
- API slow or timing out
- Worker unable to process

**Diagnosis:**
```bash
# Check active connections
psql ... -c "SELECT count(*) FROM pg_stat_activity WHERE datname = 'postgres';"

# Check pool stats
curl -s https://api.tsh.sale/tds/dashboard/metrics | jq '.database.active_connections'
```

**Solutions:**

1. **Increase pool size:**
   ```bash
   # Edit .env
   DATABASE_POOL_SIZE=20
   DATABASE_MAX_OVERFLOW=40

   # Restart services
   systemctl restart tds-core-api tds-core-worker
   ```

2. **Close idle connections:**
   ```sql
   -- Kill idle connections (careful in production)
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE datname = 'postgres'
     AND state = 'idle'
     AND state_change < NOW() - INTERVAL '1 hour';
   ```

---

## Best Practices

### Monitoring

- **Check dashboard daily** for health overview
- **Set up external monitoring** (UptimeRobot, Pingdom) for API health endpoint
- **Review logs weekly** for error patterns
- **Acknowledge alerts promptly** to maintain clean alert queue

### Queue Management

- **Keep pending queue <100** for optimal performance
- **Investigate DLQ events weekly** and retry when possible
- **Purge old completed events monthly** to maintain performance
- **Monitor success rate** - target >98%

### Manual Interventions

- **Always investigate before retrying** DLQ events
- **Fix root cause first** before bulk retries
- **Document manual interventions** for future reference
- **Test fixes in staging** when possible

### Deployment

- **Deploy during low traffic** periods
- **Monitor for 15 minutes** after deployment
- **Keep rollback ready** (previous code backup)
- **Check metrics before and after** deployment

### Performance

- **Monitor queue age** - pending events should process within minutes
- **Watch processing duration** - should average <5 seconds
- **Keep database connections reasonable** - <50% of max
- **Review slow queries** periodically

### Security

- **Rotate credentials quarterly**
- **Review access logs monthly**
- **Keep dependencies updated**
- **Monitor for suspicious activity**

---

## Emergency Procedures

### Total System Failure

```bash
# 1. Check all services
ssh root@167.71.39.50
systemctl status tds-core-api tds-core-worker

# 2. Check database connectivity
psql -h aws-1-eu-north-1.pooler.supabase.com ... -c "SELECT 1;"

# 3. Check logs for errors
journalctl -u tds-core-api -n 50
journalctl -u tds-core-worker -n 50

# 4. Restart all services
systemctl restart tds-core-api tds-core-worker

# 5. Verify health
curl https://api.tsh.sale/tds/health

# 6. Monitor metrics
curl -s https://api.tsh.sale/tds/dashboard/metrics | jq .
```

### Data Loss / Corruption

```bash
# 1. Stop services immediately
systemctl stop tds-core-api tds-core-worker

# 2. Assess damage
psql ... -c "SELECT COUNT(*) FROM tds_sync_queue;"

# 3. Restore from backup if needed
pg_restore ... /opt/backups/latest.backup

# 4. Restart services
systemctl start tds-core-api tds-core-worker

# 5. Verify integrity
curl -s https://api.tsh.sale/tds/dashboard/metrics | jq .
```

---

## Contacts

**System Administrator:** [contact-info]
**Database Administrator:** [contact-info]
**Development Team:** [contact-info]

**Escalation Path:**
1. Check documentation and logs
2. Attempt standard troubleshooting
3. Contact system administrator
4. Escalate to development team if needed

---

## Additional Resources

- **API Documentation:** https://api.tsh.sale/tds/docs
- **Deployment Guide:** DEPLOYMENT.md
- **Architecture Diagram:** [link-to-diagram]
- **Runbook Repository:** [link-to-runbook]
