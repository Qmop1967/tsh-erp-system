# Webhook Troubleshooting Guide

## Table of Contents
1. [Quick Diagnosis](#quick-diagnosis)
2. [Common Issues](#common-issues)
3. [Monitoring & Prevention](#monitoring--prevention)
4. [Step-by-Step Debugging](#step-by-step-debugging)
5. [Recovery Procedures](#recovery-procedures)

---

## Quick Diagnosis

### Check Webhook Health
```bash
curl http://localhost:8001/webhooks/health?hours=24 | jq
```

**Look for:**
- `health_score` < 70 = Issues need attention
- `issues` array = Specific problems detected
- `recommendations` = Actions to take

### Check for Duplicates
```bash
curl http://localhost:8001/webhooks/duplicates?hours=24 | jq
```

**Signs of problems:**
- `duplicate_event_groups` > 10 = Zoho retrying excessively
- `retry_count` > 5 = Persistent delivery failures

---

## Common Issues

### 1. Webhook Returns 500 Error

**Symptoms:**
- Zoho shows "Failure" status
- Server logs show `IntegrityError` or `500 Internal Server Error`

**Causes:**
- Duplicate webhook handling not working
- Database connection issues
- Unhandled exceptions in processing

**Solution:**
```bash
# Check recent errors in logs
journalctl -u tds-core-api.service --since '10 minutes ago' | grep ERROR

# Verify duplicate handling is working
curl -X POST http://localhost:8001/webhooks/products \
  -H "Content-Type: application/json" \
  -d '{"item": {"item_id": "test123", "name": "Test"}}' | jq

# Send same webhook again - should return success
curl -X POST http://localhost:8001/webhooks/products \
  -H "Content-Type: application/json" \
  -d '{"item": {"item_id": "test123", "name": "Test"}}' | jq

# Both should return {"success": true}
```

**Fix:**
1. Ensure `services/inbox_service.py` has `IntegrityError` handling
2. Restart service: `systemctl restart tds-core-api.service`
3. Clear old duplicate entries if needed

---

### 2. High Duplicate Rate (>10%)

**Symptoms:**
- Many duplicate webhook deliveries
- Zoho webhook logs show multiple retries
- Duplicate rate above 10% in health metrics

**Causes:**
- API returning non-2xx status codes
- Slow response times (>5 seconds)
- Network issues between Zoho and server

**Solution:**
```bash
# Check response times
journalctl -u tds-core-api.service | grep "POST /webhooks/products" | tail -20

# Look for slow responses (>1000ms)
# Example: "← POST /webhooks/products [202] 5234.56ms" = Too slow!

# Check database performance
psql -U tsh_erp -d tsh_erp -c "
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
       n_tup_ins, n_tup_upd, n_tup_del
FROM pg_stat_user_tables
WHERE tablename LIKE 'tds_%'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

**Fix:**
1. Optimize database queries
2. Add database indexes if needed
3. Increase worker processes in config
4. Configure Zoho webhook retry settings

---

### 3. Webhooks Not Being Processed

**Symptoms:**
- Events stuck in PENDING status
- Dead letter queue accumulating
- Processing success rate < 90%

**Causes:**
- Processor worker not running
- Database connection lost
- Invalid data causing processing failures

**Solution:**
```bash
# Check queue status
curl http://localhost:8001/queue/stats | jq

# Look for:
# - High "pending" count
# - Low processing rate

# Check dead letter queue
curl http://localhost:8001/dashboard/dead-letter?limit=10 | jq

# Check recent errors
curl http://localhost:8001/dashboard/recent-events?status_filter=failed | jq

# Manually retry failed events
FAILED_EVENT_ID="..." # Get from dead letter queue
curl -X POST "http://localhost:8001/dashboard/dead-letter/${FAILED_EVENT_ID}/retry" | jq
```

**Fix:**
1. Check processor service is running
2. Review error logs for common failure patterns
3. Fix data validation issues
4. Manually retry dead letter events

---

### 4. Database Constraint Violations

**Symptoms:**
- Error: `duplicate key value violates unique constraint "tds_inbox_events_idempotency_key_key"`
- Webhooks failing with 500 error

**Causes:**
- Race condition in duplicate checking
- IntegrityError not being caught

**Solution:**
This should be fixed automatically by the code, but if it persists:

```python
# Verify fix is deployed in services/inbox_service.py:
# Lines 99-111 should have:
except IntegrityError as e:
    await self.db.rollback()
    if "idempotency_key" in str(e):
        logger.info(f"Duplicate event caught by database: {idempotency_key}")
        raise ValueError(f"Duplicate event: {idempotency_key}")
```

```bash
# Restart service to apply fix
systemctl restart tds-core-api.service

# Test duplicate handling
curl -X POST http://localhost:8001/webhooks/products \
  -H "Content-Type: application/json" \
  -d '{"item": {"item_id": "test456", "name": "Test Product"}}' | jq

# Send again - should return success
curl -X POST http://localhost:8001/webhooks/products \
  -H "Content-Type: application/json" \
  -d '{"item": {"item_id": "test456", "name": "Test Product"}}' | jq
```

---

## Monitoring & Prevention

### 1. Set Up Automated Monitoring

```bash
# Install monitoring script
cp scripts/monitor_webhooks.sh /opt/tds_core/scripts/
chmod +x /opt/tds_core/scripts/monitor_webhooks.sh

# Add to crontab (runs every 5 minutes)
crontab -e
# Add line:
*/5 * * * * /opt/tds_core/scripts/monitor_webhooks.sh

# Configure email alerts
export ALERT_EMAIL="your-email@example.com"
```

### 2. Run Automated Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run webhook tests
cd /opt/tds_core
pytest tests/test_webhook_handling.py -v

# Expected output: All tests PASSED
```

### 3. Monitor Key Metrics

**Daily checks:**
```bash
# Health score (should be >90)
curl -s http://localhost:8001/webhooks/health?hours=24 | jq '.metrics.health_score'

# Success rate (should be >95%)
curl -s http://localhost:8001/webhooks/health?hours=24 | jq '.metrics.processing_stats.success_rate'

# Duplicate rate (should be <5%)
curl -s http://localhost:8001/webhooks/health?hours=24 | jq '.metrics.inbox_stats.duplicate_rate'
```

**Weekly checks:**
```bash
# Dead letter queue (should be empty or <5)
curl -s http://localhost:8001/queue/stats | jq '.by_status.DEAD_LETTER'

# Failed events trend
curl -s http://localhost:8001/webhooks/health?hours=168 | jq '.metrics.failure_analysis.failed_events'
```

---

## Step-by-Step Debugging

### When Zoho Shows "Failure"

1. **Check server logs immediately:**
   ```bash
   journalctl -u tds-core-api.service --since '5 minutes ago' --no-pager | tail -100
   ```

2. **Look for the webhook request:**
   ```
   → POST /webhooks/products
   ← POST /webhooks/products [500] 19.48ms
   ```

3. **Find the error:**
   ```
   sqlalchemy.exc.IntegrityError: duplicate key value violates...
   OR
   ValueError: Invalid data format
   OR
   HTTPException: 500 Internal Server Error
   ```

4. **Get the webhook payload from Zoho:**
   - Go to Zoho Books → Settings → Automation → Workflow → Webhook Logs
   - Find the failed webhook
   - Copy the request body

5. **Test locally:**
   ```bash
   curl -X POST http://localhost:8001/webhooks/products \
     -H "Content-Type: application/json" \
     -d '<paste-webhook-payload>' | jq
   ```

6. **Check database state:**
   ```sql
   -- Check if event already exists
   SELECT * FROM tds_inbox_events
   WHERE source_entity_id = '<item_id_from_webhook>'
   ORDER BY received_at DESC LIMIT 5;

   -- Check processing status
   SELECT * FROM tds_sync_queue
   WHERE source_entity_id = '<item_id_from_webhook>'
   ORDER BY queued_at DESC LIMIT 5;
   ```

7. **Fix and verify:**
   - Apply appropriate fix from "Common Issues" section
   - Test with same payload again
   - Should return `{"success": true}`

---

## Recovery Procedures

### Clear Duplicate Event Backlog

If many duplicates accumulated:

```sql
-- Find duplicate events (same idempotency key)
SELECT idempotency_key, COUNT(*) as count
FROM tds_inbox_events
GROUP BY idempotency_key
HAVING COUNT(*) > 1
ORDER BY count DESC
LIMIT 20;

-- Keep only the first occurrence (oldest)
WITH ranked_events AS (
  SELECT id,
         ROW_NUMBER() OVER (PARTITION BY idempotency_key ORDER BY received_at ASC) as rn
  FROM tds_inbox_events
)
DELETE FROM tds_inbox_events
WHERE id IN (
  SELECT id FROM ranked_events WHERE rn > 1
);
```

### Retry All Dead Letter Events

```bash
# Get all dead letter event IDs
DEAD_EVENTS=$(curl -s http://localhost:8001/dashboard/dead-letter?limit=100 | jq -r '.events[].id')

# Retry each one
for EVENT_ID in $DEAD_EVENTS; do
  echo "Retrying event: $EVENT_ID"
  curl -X POST "http://localhost:8001/dashboard/dead-letter/${EVENT_ID}/retry"
  sleep 1
done
```

### Force Resync from Zoho

If webhooks are completely broken:

```bash
# Trigger manual sync for specific entity type
curl -X POST http://localhost:8001/sync/manual \
  -H "Content-Type: application/json" \
  -d '{
    "entity_type": "product",
    "priority": "high"
  }' | jq
```

---

## Prevention Checklist

✅ **Automated Monitoring**
- [ ] Cron job running every 5 minutes
- [ ] Email alerts configured
- [ ] Health metrics reviewed daily

✅ **Testing**
- [ ] Automated tests passing
- [ ] Duplicate handling tested monthly
- [ ] Load testing performed quarterly

✅ **Infrastructure**
- [ ] Database backups enabled
- [ ] Sufficient disk space (>20GB free)
- [ ] Logs rotated automatically

✅ **Zoho Configuration**
- [ ] Webhook retry limit: 3-5 attempts
- [ ] Timeout: 30 seconds
- [ ] Authentication configured

✅ **Code Quality**
- [ ] Latest fixes deployed
- [ ] Error handling comprehensive
- [ ] Logging detailed enough for debugging

---

## Emergency Contacts

- **Primary Admin:** [Your email]
- **Database Admin:** [DB admin email]
- **Zoho Support:** [Zoho support contact]

## Useful Links

- API Documentation: http://localhost:8001/docs
- Webhook Health: http://localhost:8001/webhooks/health
- Queue Stats: http://localhost:8001/queue/stats
- Zoho Webhook Logs: https://books.zoho.com/app#/settings/automation/logs/webhook

---

**Last Updated:** 2025-11-01
**Version:** 1.0
