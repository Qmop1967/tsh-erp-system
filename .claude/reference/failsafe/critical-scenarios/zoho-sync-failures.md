# Zoho Sync Failure Scenarios

**Purpose:** Emergency procedures for TDS Core Zoho sync failures
**Last Updated:** 2025-11-14
**Load via:** @docs/reference/failsafe/critical-scenarios/zoho-sync-failures.md

---

## 🔴 Scenario: TDS Core Zoho Sync Stopped Working

### Symptoms

```yaml
Error Messages:
  - "Zoho API authentication failed"
  - "Access token expired"
  - "Rate limit exceeded"
  - "Connection timeout to Zoho APIs"
  - "Invalid organization ID"

User Impact:
  - Products not syncing from Zoho
  - Orders not updating
  - Inventory data stale (> 15 minutes)
  - Price changes not reflected
  - New products missing
```

---

## 🚨 Immediate Response

### STOP (Don't Make It Worse)

```yaml
❌ DON'T:
  - Regenerate tokens without documenting old ones
  - Restart TDS Core repeatedly (rate limit)
  - Modify Zoho credentials without testing
  - Delete sync logs (need for diagnosis)
  - Bypass TDS Core (direct Zoho access)
```

### ASSESS (Diagnose Quickly)

```yaml
Check TDS Core Dashboard:
  - Navigate to: https://tds.tsh.sale
  - Check sync status
  - Review error logs
  - Verify last successful sync timestamp

Possible Causes:
  1. Token Expired
     - Zoho access token expired (60 days)
     - Refresh token expired (never expires but can be revoked)
     - Organization ID changed

  2. Rate Limit
     - API calls exceeded Zoho limits
     - Too frequent sync attempts
     - Concurrent requests limit

  3. Network Issues
     - TDS Core server unreachable
     - Zoho APIs unreachable
     - Firewall blocking outbound connections

  4. Configuration Error
     - Wrong credentials in .env
     - Organization ID changed
     - API endpoint changed
```

### ALERT USER IF

```yaml
🚨 HIGH PRIORITY - Alert If:
  □ Sync stopped for > 1 hour
  □ Products/orders not updating
  □ Token regeneration needed
  □ Data inconsistency detected

Message:
"⚠️ HIGH: Zoho sync has stopped. Last successful sync: [timestamp]
 Impact: Product/order data may be stale
 Investigating: [what you're checking]
 ETA: Will update in 15 minutes"
```

---

## 🔍 Diagnostic Steps

### Step 1: Check TDS Core Status

```bash
# Check TDS Core service
ssh root@167.71.39.50
systemctl status tds-core

# Check TDS Core logs
tail -100 /var/www/tds-core/logs/tds_core.log

# Check TDS Core health endpoint
curl https://tds.tsh.sale/api/health
```

### Step 2: Check Zoho Token Status

```bash
# SSH to production
ssh root@167.71.39.50

# Check TDS Core .env for token
cat /var/www/tds-core/.env | grep ZOHO

# Test Zoho API connectivity
curl -H "Authorization: Zoho-oauthtoken $ZOHO_ACCESS_TOKEN" \
  "https://www.zohoapis.com/books/v3/items?organization_id=$ZOHO_ORG_ID"
```

### Step 3: Check Sync Logs

```bash
# View detailed sync logs
tail -200 /var/www/tds-core/logs/sync_operations.log

# Check for specific errors
grep -i "error\|failed\|exception" /var/www/tds-core/logs/tds_core.log | tail -50

# Check sync statistics
curl https://tds.tsh.sale/api/sync/stats
```

### Step 4: Check Database Sync Status

```bash
# Check last successful sync timestamps
PGPASSWORD='TSH@2025Secure!Production' psql \
  -h localhost \
  -U tsh_app_user \
  -d tsh_erp_production \
  -c "SELECT MAX(zoho_last_synced_at) as last_sync FROM products;"

# Check products needing sync
PGPASSWORD='TSH@2025Secure!Production' psql \
  -h localhost \
  -U tsh_app_user \
  -d tsh_erp_production \
  -c "SELECT COUNT(*) FROM products WHERE zoho_last_synced_at < NOW() - INTERVAL '1 hour';"
```

---

## 🛠️ Fix Implementation

### Fix 1: Token Expired (Most Common)

**If:** Access token expired error

**Solution:**

```bash
# 1. Generate new access token from Zoho
# Navigate to: https://api-console.zoho.com/
# Generate new access token for TSH organization

# 2. Update TDS Core .env
ssh root@167.71.39.50
cd /var/www/tds-core
nano .env

# Update:
# ZOHO_CLIENT_ID=<your_client_id>
# ZOHO_CLIENT_SECRET=<your_client_secret>
# ZOHO_ACCESS_TOKEN=<new_access_token>
# ZOHO_REFRESH_TOKEN=<refresh_token>
# ZOHO_ORG_ID=<org_id>

# 3. Restart TDS Core
systemctl restart tds-core

# 4. Verify sync resumes
tail -f /var/www/tds-core/logs/tds_core.log
```

### Fix 2: Rate Limit Exceeded

**If:** "Rate limit exceeded" error

**Solution:**

```yaml
Immediate:
  1. Stop sync temporarily (let rate limit reset)
  2. Wait 5-10 minutes
  3. Resume sync with reduced frequency

Long-term:
  1. Adjust sync frequency in TDS Core config
     - Change from 15 minutes to 30 minutes
     - Implement exponential backoff

  2. Optimize API calls
     - Use incremental sync (only changed records)
     - Batch API requests
     - Cache frequently accessed data

Code Fix:
  # tds_core/config.py
  SYNC_INTERVAL_MINUTES = 30  # Increase from 15
  MAX_API_CALLS_PER_MINUTE = 100  # Respect Zoho limits
```

### Fix 3: Network/Connectivity Issues

**If:** Connection timeout or unreachable errors

**Solution:**

```bash
# 1. Check TDS Core can reach Zoho APIs
ssh root@167.71.39.50
curl -I https://www.zohoapis.com/books/v3/

# 2. Check DNS resolution
nslookup www.zohoapis.com

# 3. Check firewall rules
iptables -L -n | grep 443

# 4. Test with curl
curl -v https://www.zohoapis.com/books/v3/items?organization_id=$ZOHO_ORG_ID \
  -H "Authorization: Zoho-oauthtoken $ZOHO_ACCESS_TOKEN"

# 5. Restart TDS Core
systemctl restart tds-core
```

### Fix 4: Configuration Error

**If:** Invalid organization ID or wrong credentials

**Solution:**

```bash
# 1. Verify credentials
ssh root@167.71.39.50
cd /var/www/tds-core
cat .env | grep ZOHO

# 2. Test each credential
# Test organization ID:
curl "https://www.zohoapis.com/books/v3/settings/organizations" \
  -H "Authorization: Zoho-oauthtoken $ZOHO_ACCESS_TOKEN"

# 3. Fix .env if needed
nano .env
# Update with correct values

# 4. Restart
systemctl restart tds-core

# 5. Monitor logs
tail -f /var/www/tds-core/logs/tds_core.log
```

---

## ✅ Verification

**After fix, verify:**

```bash
# 1. TDS Core service running
systemctl status tds-core

# 2. No errors in logs
tail -50 /var/www/tds-core/logs/tds_core.log | grep -i error

# 3. Sync operations working
curl https://tds.tsh.sale/api/sync/stats

# 4. Products being synced
PGPASSWORD='TSH@2025Secure!Production' psql \
  -h localhost \
  -U tsh_app_user \
  -d tsh_erp_production \
  -c "SELECT COUNT(*) FROM products WHERE zoho_last_synced_at > NOW() - INTERVAL '20 minutes';"

# 5. New products appearing
# Check Zoho for recent product, verify it appears in TSH ERP

# 6. Dashboard shows green status
# Navigate to: https://tds.tsh.sale
# Verify: All sync operations showing "SUCCESS"
```

---

## 🔄 Prevention

### Monitoring

```yaml
Setup Alerts:
  - Sync hasn't run in > 30 minutes
  - Sync error rate > 5%
  - Token expiring in < 7 days
  - API rate limit warnings
  - TDS Core service down

Dashboard Checks (Daily):
  - https://tds.tsh.sale (TDS Core dashboard)
  - Sync success rate
  - Last successful sync timestamp
  - Error log review
```

### Best Practices

```yaml
Token Management:
  ✅ Set calendar reminder for token expiration (60 days)
  ✅ Document token generation procedure
  ✅ Store refresh token securely
  ✅ Test token before it expires

Sync Configuration:
  ✅ Appropriate sync frequency (15-30 minutes)
  ✅ Implement incremental sync
  ✅ Use exponential backoff on errors
  ✅ Respect Zoho API rate limits
  ✅ Log all sync operations

Error Handling:
  ✅ Graceful degradation (continue on single item failure)
  ✅ Retry logic with backoff
  ✅ Alert on repeated failures
  ✅ Detailed error logging
```

### Zoho API Rate Limits

```yaml
Zoho Books API Limits:
  - 100 API calls per minute
  - 10,000 API calls per day (free plan)
  - 100,000 API calls per day (paid plan)

TSH ERP Sync Strategy:
  - Sync every 15-30 minutes
  - ~4 API calls per sync
  - ~384 API calls per day (well under limit)

If Rate Limited:
  - Increase sync interval
  - Implement caching
  - Use webhooks (future enhancement)
```

---

## 📝 Common Errors Reference

```yaml
Error: "Invalid access token"
  Cause: Token expired or revoked
  Fix: Regenerate token from Zoho console

Error: "Invalid organization_id"
  Cause: Wrong org ID in configuration
  Fix: Verify org ID in Zoho settings, update .env

Error: "Rate limit exceeded"
  Cause: Too many API calls
  Fix: Wait 5-10 minutes, reduce sync frequency

Error: "Connection timeout"
  Cause: Network issue or Zoho API down
  Fix: Check connectivity, wait if Zoho API issue

Error: "Invalid_code"
  Cause: Authorization code expired during token generation
  Fix: Regenerate authorization code (valid for 1 minute only)

Error: "SSL certificate verify failed"
  Cause: SSL certificate issue
  Fix: Update CA certificates, check system time
```

---

## 🚨 Emergency Fallback

**If sync cannot be fixed quickly:**

```yaml
Temporary Solution:
  1. Enable "Manual Sync Mode"
     - Users notified data may be stale
     - Critical operations continue
     - Manual refresh for urgent data

  2. Communicate Impact
     - "Product prices may be stale"
     - "New products delayed"
     - "Inventory not real-time"

  3. Set Expectations
     - ETA for fix
     - Update frequency
     - Manual workaround if needed

Never:
  ❌ Bypass TDS Core (direct Zoho access)
  ❌ Disable sync completely without notice
  ❌ Allow stale data > 4 hours without alert
```

---

## 🔗 Related Resources

```yaml
Documentation:
  - TDS Core architecture: @docs/TDS_MASTER_ARCHITECTURE.md
  - Zoho integration guide: @docs/ZOHO_INTEGRATION.md
  - Sync troubleshooting: @docs/TDS_TROUBLESHOOTING.md

External:
  - Zoho API Console: https://api-console.zoho.com/
  - Zoho Books API Docs: https://www.zoho.com/books/api/v3/
  - Zoho Inventory API Docs: https://www.zoho.com/inventory/api/v1/
```

---

**Related Scenarios:**
- Database failures: @docs/reference/failsafe/critical-scenarios/database-failures.md
- API errors: @docs/reference/failsafe/critical-scenarios/api-errors.md
- Recovery procedures: @docs/reference/failsafe/recovery-procedures.md
