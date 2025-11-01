# How to Guarantee Webhook Problems Don't Repeat

## ✅ Already Implemented (DONE)

### 1. **Fixed Duplicate Webhook Handling** ✅
**File:** `services/inbox_service.py` + `main.py`

**What was fixed:**
- Added `IntegrityError` exception handling
- Duplicates now return HTTP 200 (success) instead of 500 (error)
- Zoho stops retrying when it receives success response

**How it prevents problems:**
- Database constraint violations are caught gracefully
- No more 500 errors for duplicate webhooks
- Zoho won't keep retrying forever

**Testing:**
```bash
# Send same webhook twice - both should succeed
curl -X POST https://erp.tsh.sale/api/tds/webhooks/products \
  -H "Content-Type: application/json" \
  -d '{"item": {"item_id": "test123", "name": "Test Product"}}'

# Second call with same data should return success
curl -X POST https://erp.tsh.sale/api/tds/webhooks/products \
  -H "Content-Type: application/json" \
  -d '{"item": {"item_id": "test123", "name": "Test Product"}}'
```

---

## 🔄 Ongoing Monitoring (SET UP THESE)

### 2. **Automated Monitoring** ⚠️ ACTION REQUIRED

**Step 1: Install jq (JSON processor)**
```bash
ssh root@167.71.39.50
apt-get update && apt-get install -y jq
```

**Step 2: Set up cron job for monitoring**
```bash
# Edit crontab
crontab -e

# Add this line (runs every 5 minutes):
*/5 * * * * /opt/tds_core/scripts/monitor_webhooks.sh >> /var/log/tds-core/monitor-cron.log 2>&1
```

**Step 3: Configure email alerts**
```bash
# Set your email for alerts
export ALERT_EMAIL="your-email@example.com"
echo 'export ALERT_EMAIL="your-email@example.com"' >> ~/.bashrc
```

**What this does:**
- Checks webhook health every 5 minutes
- Sends email if health score drops below 70
- Logs duplicate rates, success rates, and issues
- Alerts you before Zoho starts failing

---

### 3. **Manual Health Checks** (Daily/Weekly)

**Daily Check (Takes 30 seconds):**
```bash
# Check overall health
curl -s https://erp.tsh.sale/api/tds/webhooks/health?hours=24 | python3 -m json.tool

# Look for:
# - health_score > 90 (good)
# - issues array (should be empty or minimal)
# - duplicate_rate < 5%
```

**Weekly Check:**
```bash
# Check for accumulating duplicates
curl -s https://erp.tsh.sale/api/tds/webhooks/duplicates?hours=168 | python3 -m json.tool

# Look for:
# - duplicate_event_groups < 10
# - retry_count < 5 per event
```

---

### 4. **Run Automated Tests** (Monthly)

**Install test dependencies** (one-time setup):
```bash
cd /opt/tds_core
pip install pytest pytest-asyncio httpx
```

**Run tests:**
```bash
cd /opt/tds_core
pytest tests/test_webhook_handling.py -v

# All tests should PASS
# Especially: test_duplicate_webhook_returns_success
```

**If any test fails:**
1. Check the error message
2. Refer to `WEBHOOK_TROUBLESHOOTING.md`
3. Fix the issue immediately
4. Re-run tests to confirm

---

## 📊 Key Metrics to Watch

### Health Score
- **90-100**: Excellent, no action needed
- **70-89**: Warning, investigate issues
- **50-69**: Unhealthy, fix problems immediately
- **0-49**: Critical, all hands on deck

### Duplicate Rate
- **<5%**: Normal (Zoho occasionally retries)
- **5-10%**: Elevated, monitor closely
- **>10%**: Problem! Check response times and errors

### Success Rate
- **>95%**: Excellent
- **90-95%**: Good
- **<90%**: Poor, investigate failures

### Processing Time
- **<1 second**: Excellent
- **1-5 seconds**: Good
- **5-10 seconds**: Slow, optimize
- **>10 seconds**: Too slow! Zoho will retry

---

## 🚨 Early Warning Signs

Watch for these patterns in your monitoring:

### 1. **Increasing Duplicate Rate**
```
# If you see this trend:
Day 1: 2% duplicates
Day 2: 5% duplicates
Day 3: 8% duplicates
```
**Action:** Check server performance and database

### 2. **Slow Processing Times**
```
# If average time increases:
Week 1: 0.5s average
Week 2: 2.0s average
Week 3: 5.0s average
```
**Action:** Optimize database queries, add indexes

### 3. **Dead Letter Queue Growing**
```
# If DLQ accumulates:
Monday: 2 events
Wednesday: 5 events
Friday: 12 events
```
**Action:** Review and manually retry failed events

---

## 🔧 Prevention Checklist

Complete this checklist monthly:

### Infrastructure
- [ ] Server has >20GB free disk space
- [ ] Database backups are running
- [ ] Log rotation is configured
- [ ] Monitoring cron job is active

### Application
- [ ] Latest webhook fixes are deployed
- [ ] All automated tests pass
- [ ] Health score is >90
- [ ] Duplicate rate is <5%

### Zoho Configuration
- [ ] Webhook URL is correct: `https://erp.tsh.sale/api/tds/webhooks/products`
- [ ] Retry limit is 3-5 attempts
- [ ] Timeout is 30 seconds
- [ ] No recent "failure" logs in Zoho

### Monitoring
- [ ] Cron job running every 5 minutes
- [ ] Email alerts configured and working
- [ ] Weekly health checks performed
- [ ] Monthly tests completed

---

## 🎯 Quick Reference

### Endpoints to Bookmark
- **Health Dashboard**: https://erp.tsh.sale/api/tds/webhooks/health
- **Duplicate Analysis**: https://erp.tsh.sale/api/tds/webhooks/duplicates
- **Queue Stats**: https://erp.tsh.sale/api/tds/queue/stats
- **API Docs**: https://erp.tsh.sale/api/tds/docs

### Files to Know
- **Troubleshooting Guide**: `/opt/tds_core/WEBHOOK_TROUBLESHOOTING.md`
- **Monitor Script**: `/opt/tds_core/scripts/monitor_webhooks.sh`
- **Test Suite**: `/opt/tds_core/tests/test_webhook_handling.py`
- **Main Fix**: `/opt/tds_core/services/inbox_service.py`

### Commands to Remember
```bash
# Check service status
systemctl status tds-core-api.service

# View recent logs
journalctl -u tds-core-api.service --since '10 minutes ago'

# Restart service (if needed)
systemctl restart tds-core-api.service

# Test webhook manually
curl -X POST https://erp.tsh.sale/api/tds/webhooks/products \
  -H "Content-Type: application/json" \
  -d '{"item": {"item_id": "test", "name": "Test"}}'
```

---

## 📝 Summary

To guarantee webhook problems don't repeat, you need **3 layers of defense**:

1. **Prevention** (Already Done ✅)
   - Fixed duplicate handling
   - Return success for duplicates
   - Proper error handling

2. **Detection** (Set Up Now ⚠️)
   - Automated monitoring every 5 minutes
   - Email alerts for problems
   - Daily/weekly health checks

3. **Response** (Use When Needed 🔧)
   - Troubleshooting guide
   - Automated tests
   - Recovery procedures

**Most Important:** Set up the automated monitoring cron job. This is your early warning system that will catch problems before they become critical.

---

**Last Updated:** 2025-11-01
**Next Review:** 2025-12-01
