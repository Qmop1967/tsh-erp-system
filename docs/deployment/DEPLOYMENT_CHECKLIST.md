# 🚀 TSH ERP Monolithic Unification - Deployment Checklist

**Date:** November 4, 2025
**Branch:** `feature/monolithic-unification`
**Target Environment:** Production (`erp.tsh.sale`)

---

## ✅ Pre-Deployment Checklist

### 1. Code Review & Testing

- [x] All code committed to `feature/monolithic-unification` branch
- [x] Application imports successfully without errors
- [x] All routers load correctly
- [x] Background workers initialize properly
- [ ] Local testing completed
  - [ ] Test `/health` endpoint
  - [ ] Test `/api/zoho/dashboard/health` endpoint
  - [ ] Test `/api/mobile/home` endpoint (BFF)
  - [ ] Test webhook processing
- [ ] Review git log for all changes
  ```bash
  git log --oneline feature/monolithic-unification --not main
  ```

### 2. Database Preparation

- [ ] **Backup current production database**
  ```bash
  PGPASSWORD="TSH@2025Secure!Production" pg_dump \
    -h localhost \
    -U tsh_app_user \
    -d tsh_erp \
    --no-owner --no-acl \
    > backup_before_bff_migration_$(date +%Y%m%d_%H%M%S).sql
  ```

- [ ] **Run migration script**
  ```bash
  PGPASSWORD="TSH@2025Secure!Production" psql \
    "postgresql://tsh_app_user:TSH@2025Secure!Production@localhost:5432/postgres" \
    -f migrations/create_bff_models.sql
  ```

- [ ] **Verify tables created**
  ```sql
  SELECT table_name FROM information_schema.tables
  WHERE table_schema = 'public'
  AND table_name IN ('promotions', 'carts', 'cart_items', 'reviews', 'customer_addresses')
  ORDER BY table_name;
  ```

### 3. Dependencies Check

- [ ] Verify `asyncpg` is installed for async database support
  ```bash
  pip list | grep asyncpg
  # If not installed: pip install asyncpg
  ```

- [ ] Check all Python dependencies
  ```bash
  pip check
  ```

### 4. Environment Variables

- [ ] Verify `.env` file has all required variables:
  ```bash
  # Check these exist:
  DATABASE_URL
  ZOHO_CLIENT_ID
  ZOHO_CLIENT_SECRET
  ZOHO_REFRESH_TOKEN
  ZOHO_ORGANIZATION_ID
  WEBHOOK_API_KEY (optional)
  TDS_BATCH_SIZE (default: 10)
  TDS_QUEUE_POLL_INTERVAL_MS (default: 1000)
  TDS_LOCK_TIMEOUT_SECONDS (default: 300)
  TDS_MAX_RETRY_ATTEMPTS (default: 5)
  ```

---

## 🔄 Deployment Steps

### Step 1: Merge to Main Branch

```bash
# Switch to main
git checkout main

# Pull latest changes
git pull origin main

# Merge feature branch
git merge feature/monolithic-unification

# Push to remote
git push origin main
```

### Step 2: Deploy to Production Server

```bash
# SSH to production server
ssh root@167.71.39.50

# Navigate to project directory
cd /root/TSH_ERP_Ecosystem

# Pull latest code
git pull origin main

# Activate virtual environment (if using)
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Run database migrations
PGPASSWORD="TSH@2025Secure!Production" psql \
  "postgresql://tsh_app_user:TSH@2025Secure!Production@localhost:5432/postgres" \
  -f migrations/create_bff_models.sql
```

### Step 3: Restart Service

```bash
# Check current service status
systemctl status tsh_erp

# Restart the service
systemctl restart tsh_erp

# Verify service started successfully
systemctl status tsh_erp

# Check logs for any errors
journalctl -u tsh_erp -f --no-pager -n 50
```

### Step 4: Verify Deployment

```bash
# 1. Check main health endpoint
curl https://erp.tsh.sale/health

# Expected response:
# {"status": "healthy", "message": "النظام يعمل بشكل طبيعي"}

# 2. Check Zoho integration health
curl https://erp.tsh.sale/api/zoho/dashboard/health

# Expected: Should return health status with queue statistics

# 3. Check Mobile BFF endpoints
curl https://erp.tsh.sale/api/mobile/home

# Expected: Should return home page data structure

# 4. Check background workers in logs
journalctl -u tsh_erp -n 100 | grep -i "worker"

# Expected to see: "Zoho sync workers started successfully"
```

---

## 🔍 Post-Deployment Verification

### 1. API Endpoints Check

- [ ] **Main endpoints working:**
  - `GET /health` - Returns healthy status
  - `GET /docs` - Swagger UI loads

- [ ] **Zoho Integration endpoints:**
  - `GET /api/zoho/dashboard/health`
  - `GET /api/zoho/dashboard/stats`
  - `POST /api/zoho/webhooks/products` (test with sample payload)

- [ ] **Mobile BFF endpoints:**
  - `GET /api/mobile/home`
  - `GET /api/mobile/products/{id}`
  - `GET /api/mobile/search?q=test`
  - `GET /api/mobile/checkout?customer_id=1`

### 2. Database Verification

```sql
-- Check new tables exist and have proper structure
SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns
     WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
AND table_name IN ('promotions', 'carts', 'cart_items', 'reviews', 'customer_addresses');

-- Check Zoho sync tables
SELECT status, COUNT(*)
FROM tds_sync_queue
GROUP BY status;

-- Check if any sample promotions were created
SELECT id, title, is_active FROM promotions LIMIT 5;
```

### 3. Background Workers Check

- [ ] Workers started successfully (check logs)
- [ ] Workers processing queue items
- [ ] No worker errors in logs
- [ ] Queue processing rate acceptable

```bash
# Check worker activity
journalctl -u tsh_erp --since "5 minutes ago" | grep -i "worker\|queue\|processing"
```

### 4. Performance Check

- [ ] Response times acceptable (<500ms for most endpoints)
- [ ] Memory usage normal
- [ ] CPU usage normal
- [ ] No database connection pool exhaustion

```bash
# Check system resources
top
htop

# Check database connections
PGPASSWORD="TSH@2025Secure!Production" psql \
  "postgresql://tsh_app_user:TSH@2025Secure!Production@localhost:5432/postgres" \
  -c "SELECT count(*) as active_connections FROM pg_stat_activity WHERE datname = 'postgres';"
```

---

## 🔙 Rollback Plan (If Issues Occur)

### Quick Rollback Steps

If critical issues are discovered:

```bash
# 1. SSH to production
ssh root@167.71.39.50

# 2. Revert to previous commit
cd /root/TSH_ERP_Ecosystem
git log --oneline -10  # Find commit before merge
git reset --hard <previous-commit-hash>

# 3. Restart service
systemctl restart tsh_erp

# 4. Verify rollback
curl https://erp.tsh.sale/health

# 5. Restore database if needed
# PGPASSWORD="TSH@2025Secure!Production" psql \
#   "postgresql://..." \
#   < backup_before_bff_migration_YYYYMMDD_HHMMSS.sql
```

### Database Rollback (If Needed)

Only if database migration caused issues:

```sql
-- Drop new tables (CAREFUL!)
BEGIN;

DROP TABLE IF EXISTS cart_items CASCADE;
DROP TABLE IF EXISTS carts CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS customer_addresses CASCADE;
DROP TABLE IF EXISTS promotions CASCADE;

-- Only commit if you're sure
-- COMMIT;
ROLLBACK;  -- Use this to safely cancel
```

---

## 📊 Monitoring Post-Deployment

### First 24 Hours

Monitor these metrics:

1. **Application Logs:**
   ```bash
   journalctl -u tsh_erp -f
   ```

2. **Error Rate:**
   - Check for increase in 500 errors
   - Monitor failed webhook processing

3. **Performance:**
   - Response times for key endpoints
   - Database query performance
   - Worker processing rate

4. **Resource Usage:**
   - CPU: Should stay below 70%
   - Memory: Should stay below 80%
   - Disk I/O
   - Network traffic

### Key Metrics to Track

- [ ] Webhook events received per hour
- [ ] Webhook processing success rate (>95%)
- [ ] Queue depth (should stay low)
- [ ] Dead letter queue items (should be minimal)
- [ ] Worker processing time (avg <1s per item)
- [ ] API response times
- [ ] Mobile BFF usage (new endpoint traffic)

---

## 🎯 Success Criteria

Deployment is successful if:

- [x] All services start without errors
- [x] Health endpoints return "healthy"
- [x] Background workers are running
- [x] No critical errors in logs
- [x] All API endpoints responding
- [x] Database migrations applied successfully
- [x] Zoho webhook processing works
- [x] Mobile BFF endpoints accessible
- [x] Response times acceptable
- [x] No increase in error rate

---

## 📞 Troubleshooting

### Issue: Workers Not Starting

**Symptoms:** No worker logs, webhooks pile up in queue

**Solution:**
```bash
# Check worker errors
journalctl -u tsh_erp -n 200 | grep -i "worker\|error"

# Verify asyncpg installed
pip list | grep asyncpg

# Check database connectivity
PGPASSWORD="TSH@2025Secure!Production" psql \
  "postgresql://tsh_app_user:TSH@2025Secure!Production@localhost:5432/postgres" \
  -c "SELECT 1"
```

### Issue: BFF Endpoints 404

**Symptoms:** `/api/mobile/*` returns 404

**Solution:**
```bash
# Check if BFF router is enabled in main.py
grep -n "mobile_bff_router" app/main.py

# Should see:
# from app.bff.mobile import router as mobile_bff_router
# app.include_router(mobile_bff_router, prefix="/api/mobile", ...)

# Check for import errors
python3 -c "from app.main import app; print('OK')"
```

### Issue: Database Migration Failed

**Symptoms:** Tables not created, migration errors

**Solution:**
```bash
# Check if tables already exist
PGPASSWORD="TSH@2025Secure!Production" psql \
  "postgresql://..." \
  -c "\dt promotions"

# If exists but structure wrong, drop and recreate
# BE CAREFUL - This deletes data!
# DROP TABLE promotions CASCADE;

# Then re-run migration
```

### Issue: High Memory Usage

**Symptoms:** Memory usage >80%, slow responses

**Solution:**
```bash
# Check memory usage
free -h

# Check worker count (might be too many)
grep "num_workers" app/main.py

# Reduce workers if needed (edit and restart)
# init_worker_manager(num_workers=1)  # Reduce from 2 to 1

# Restart service
systemctl restart tsh_erp
```

---

## 📝 Post-Deployment Tasks

After successful deployment:

- [ ] Update team on deployment completion
- [ ] Document any issues encountered
- [ ] Update Flutter apps to use BFF endpoints
- [ ] Monitor for 48 hours
- [ ] Archive old TDS Core service (if applicable)
- [ ] Update documentation links
- [ ] Train team on Event Bus usage
- [ ] Plan next phase (modular architecture)

---

## 📚 Additional Resources

- **Unification Summary:** `UNIFICATION_COMPLETE.md`
- **Event Bus Guide:** `EVENT_BUS_EXAMPLES.md`
- **Architecture Plan:** `MODULAR_MONOLITH_ARCHITECTURE_PLAN.md`
- **BFF Plan:** `BFF_ARCHITECTURE_PLAN.md`
- **API Documentation:** `https://erp.tsh.sale/docs`

---

**Generated with** 🤖 [Claude Code](https://claude.com/claude-code)
