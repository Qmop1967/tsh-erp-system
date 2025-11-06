# 🚀 TDS Integration Deployment Checklist

## قائمة التحقق من نشر TDS

**Project:** TSH ERP Ecosystem
**Date:** November 6, 2025
**Version:** 2.0.2

---

## 📋 Pre-Deployment Checklist

### 1. Code Review ✅

- [x] Stock sync service implemented (`app/tds/integrations/zoho/stock_sync.py`)
- [x] Unified CLI created (`scripts/unified_stock_sync.py`)
- [x] Router updated to TDS (`app/routers/zoho_bulk_sync.py`)
- [x] Exports updated (`app/tds/integrations/zoho/__init__.py`)
- [x] All code follows style guidelines
- [x] Type hints added throughout
- [x] Docstrings complete

### 2. Testing ⏳

#### Unit Tests
- [x] Stock sync service tests created
- [x] Router endpoint tests created
- [x] Mock fixtures created
- [ ] All unit tests passing
- [ ] Code coverage >= 80%

#### Integration Tests
- [ ] Stock sync integration tests run
- [ ] Router integration tests run
- [ ] End-to-end tests pass
- [ ] Performance tests pass

#### Manual Testing
- [ ] Stock sync - full mode
- [ ] Stock sync - incremental mode
- [ ] Stock sync - specific items
- [ ] Stock sync - low stock
- [ ] Stock sync - warehouse
- [ ] Stock sync - summary
- [ ] Products bulk sync API
- [ ] Customers bulk sync API
- [ ] Price lists sync API
- [ ] Sync all API

### 3. Environment Configuration

#### Required Environment Variables
```bash
# Verify these are set in production
ZOHO_CLIENT_ID=<your_value>
ZOHO_CLIENT_SECRET=<your_value>
ZOHO_REFRESH_TOKEN=<your_value>
ZOHO_ORGANIZATION_ID=<your_value>
```

- [ ] All environment variables set in staging
- [ ] All environment variables set in production
- [ ] Credentials validated and working
- [ ] Token refresh tested

### 4. Documentation

- [x] Stock sync documentation complete
- [x] Router integration documentation complete
- [x] Phase 2 summary created
- [x] API examples provided
- [ ] Internal wiki updated
- [ ] Team notified of changes

---

## 🧪 Testing Phase

### Unit Tests
```bash
# Run unit tests
pytest tests/tds/test_stock_sync.py -m unit -v
pytest tests/tds/test_zoho_bulk_sync_router.py -m unit -v

# Check coverage
pytest tests/tds/ --cov=app/tds/integrations/zoho/stock_sync --cov-report=html
pytest tests/tds/ --cov=app/routers/zoho_bulk_sync --cov-report=html
```

**Expected Results:**
- [ ] All unit tests pass (100%)
- [ ] Code coverage >= 80%
- [ ] No critical errors or warnings

### Integration Tests
```bash
# Run integration tests (requires credentials)
pytest tests/tds/ -m integration -v

# Or run specific test
pytest tests/tds/test_stock_sync.py::test_real_stock_summary -v
```

**Expected Results:**
- [ ] All integration tests pass
- [ ] API connections successful
- [ ] Data sync working correctly

### Manual Testing

#### Test 1: Stock Sync CLI
```bash
# Test summary
python scripts/unified_stock_sync.py --summary

# Test small batch
python scripts/unified_stock_sync.py --mode incremental --batch-size 10
```

**Expected:** ✅ Summary displays, small sync completes

#### Test 2: Products Sync API
```bash
curl -X POST "http://localhost:8000/api/zoho/bulk-sync/products" \
  -H "Content-Type: application/json" \
  -d '{
    "incremental": true,
    "batch_size": 10,
    "active_only": true
  }'
```

**Expected:** ✅ Returns success with stats

#### Test 3: Health Check
```bash
curl http://localhost:8000/api/zoho/bulk-sync/status
```

**Expected:** ✅ Returns healthy status

---

## 🏗️ Staging Deployment

### 1. Pre-Deployment

**Database Backup**
```bash
# Backup production database before deployment
PGPASSWORD="Zcbbm.97531tsh" pg_dump \
  "postgresql://postgres.trjjglxhteqnzmyakxhe:Zcbbm.97531tsh@aws-1-eu-north-1.pooler.supabase.com:5432/postgres" \
  > backup_pre_tds_$(date +%Y%m%d_%H%M%S).sql
```

- [ ] Database backup created
- [ ] Backup verified and stored securely

**Code Backup**
```bash
# Tag current production version
git tag -a v2.0.1-pre-tds -m "Pre-TDS integration backup"
git push origin v2.0.1-pre-tds
```

- [ ] Git tag created
- [ ] Tag pushed to repository

### 2. Deploy to Staging

**Update Code**
```bash
# Pull latest code
git checkout main
git pull origin main

# Install dependencies (if any new)
pip install -r requirements.txt
```

- [ ] Code updated in staging
- [ ] Dependencies installed

**Restart Services**
```bash
# Restart the backend service
sudo systemctl restart tsh-erp-backend

# Or if using PM2/other process manager
pm2 restart tsh-erp-backend
```

- [ ] Backend restarted
- [ ] Services healthy

### 3. Verify Staging

**Health Checks**
```bash
# Check API health
curl http://staging.tsh.sale/api/health
curl http://staging.tsh.sale/api/zoho/bulk-sync/status
```

- [ ] Health endpoint responds
- [ ] Bulk sync status healthy

**Functionality Tests**
```bash
# Test stock sync
python scripts/unified_stock_sync.py --summary

# Test products sync
curl -X POST "http://staging.tsh.sale/api/zoho/bulk-sync/products" \
  -H "Content-Type: application/json" \
  -d '{"incremental": true, "batch_size": 10}'
```

- [ ] Stock sync works
- [ ] API endpoints work
- [ ] No errors in logs

### 4. Monitor Staging (24-48 hours)

**Log Monitoring**
```bash
# Monitor application logs
tail -f /var/log/tsh-erp/backend.log

# Monitor error logs
grep -i error /var/log/tsh-erp/backend.log
```

- [ ] No critical errors
- [ ] Performance acceptable
- [ ] Memory usage normal
- [ ] CPU usage normal

**Metrics to Watch:**
- Request success rate >= 99%
- Average response time < 500ms
- Error rate < 1%
- Token refresh working
- Connection pooling effective

---

## 🚀 Production Deployment

### 1. Pre-Production Checklist

- [ ] All staging tests passed
- [ ] 24-48 hour monitoring complete
- [ ] No critical issues found
- [ ] Stakeholders notified
- [ ] Deployment window scheduled
- [ ] Rollback plan ready

### 2. Deployment Window

**Recommended Time:** Low traffic period (e.g., 2 AM - 4 AM)

**Steps:**

1. **Notify Team** (30 minutes before)
   ```
   Subject: TDS Integration Deployment
   Time: [deployment time]
   Duration: ~15 minutes
   Impact: Minimal (no downtime expected)
   ```

2. **Create Backup**
   ```bash
   # Database backup
   PGPASSWORD="Zcbbm.97531tsh" pg_dump \
     "postgresql://postgres.trjjglxhteqnzmyakxhe:Zcbbm.97531tsh@aws-1-eu-north-1.pooler.supabase.com:5432/postgres" \
     > backup_prod_$(date +%Y%m%d_%H%M%S).sql

   # Tag current version
   git tag -a v2.0.1 -m "Pre-TDS integration production"
   git push origin v2.0.1
   ```

   - [ ] Database backup created
   - [ ] Git tag created

3. **Deploy Code**
   ```bash
   # SSH to production server
   ssh production-server

   # Navigate to project
   cd /var/www/tsh-erp

   # Pull latest code
   git checkout main
   git pull origin main

   # Install dependencies
   pip install -r requirements.txt
   ```

   - [ ] Code deployed
   - [ ] Dependencies installed

4. **Restart Services**
   ```bash
   # Restart backend
   sudo systemctl restart tsh-erp-backend

   # Verify service is running
   sudo systemctl status tsh-erp-backend
   ```

   - [ ] Backend restarted
   - [ ] Service status healthy

5. **Verify Deployment**
   ```bash
   # Health check
   curl https://erp.tsh.sale/api/health
   curl https://erp.tsh.sale/api/zoho/bulk-sync/status

   # Test stock sync
   python scripts/unified_stock_sync.py --summary
   ```

   - [ ] Health checks pass
   - [ ] Stock sync works
   - [ ] API responds correctly

6. **Monitor (First 2 Hours)**
   ```bash
   # Watch logs in real-time
   tail -f /var/log/tsh-erp/backend.log

   # Check for errors
   grep -i error /var/log/tsh-erp/backend.log | tail -20
   ```

   - [ ] No critical errors
   - [ ] No performance issues
   - [ ] Token refresh working

### 3. Post-Deployment Verification

**Smoke Tests** (Run immediately after deployment)
```bash
# Test 1: Health Check
curl https://erp.tsh.sale/api/health

# Test 2: Bulk Sync Status
curl https://erp.tsh.sale/api/zoho/bulk-sync/status

# Test 3: Stock Summary
python scripts/unified_stock_sync.py --summary

# Test 4: Small Incremental Sync
python scripts/unified_stock_sync.py --mode incremental --batch-size 10

# Test 5: Products Sync API
curl -X POST "https://erp.tsh.sale/api/zoho/bulk-sync/products" \
  -H "Content-Type: application/json" \
  -d '{"incremental": true, "batch_size": 10}'
```

**Expected Results:**
- [ ] All health checks pass
- [ ] Stock sync completes successfully
- [ ] API returns valid responses
- [ ] No errors in logs

---

## 📊 Post-Deployment Monitoring

### First 24 Hours

**Monitor Every 2 Hours:**
- [ ] Application logs
- [ ] Error rates
- [ ] Response times
- [ ] Memory usage
- [ ] CPU usage
- [ ] Token refresh events
- [ ] Sync success rates

**Key Metrics:**
```bash
# Check logs
tail -100 /var/log/tsh-erp/backend.log

# Check error rate
grep -c ERROR /var/log/tsh-erp/backend.log

# Check sync events
grep "stock.sync" /var/log/tsh-erp/backend.log
```

### First Week

**Daily Monitoring:**
- [ ] Review error logs
- [ ] Check sync statistics
- [ ] Monitor API performance
- [ ] Verify token refresh
- [ ] Check resource usage

**Weekly Report:**
- Total syncs performed
- Success rate
- Average sync duration
- Error count and types
- Performance metrics

---

## 🔄 Archive Legacy Code

**After 1 Week of Successful Production Operation:**

### 1. Create Archive Directory
```bash
mkdir -p archived/zoho_integration/stock_sync
mkdir -p archived/scripts/stock_sync
```

### 2. Move Legacy Services
```bash
# Move legacy stock sync service
git mv app/services/zoho_stock_sync.py archived/zoho_integration/stock_sync/

# Move legacy scripts
git mv scripts/sync_zoho_stock.py archived/scripts/stock_sync/
git mv scripts/tds_sync_stock.py archived/scripts/stock_sync/
git mv scripts/sync_stock_from_zoho_inventory.py archived/scripts/stock_sync/
git mv scripts/test_stock_sync_direct.py archived/scripts/stock_sync/
git mv scripts/run_stock_sync.sh archived/scripts/stock_sync/
```

### 3. Create Archive README
```bash
cat > archived/README.md << 'EOF'
# Archived Code

This directory contains legacy code that has been replaced by the TDS unified integration.

**Archived on:** [Date]
**Replaced by:** TDS unified Zoho integration

## Stock Sync
- **Legacy Files:** 9 files, ~1,300 lines
- **Replaced By:** `app/tds/integrations/zoho/stock_sync.py` + `scripts/unified_stock_sync.py`
- **Reason:** Consolidation, code reduction, unified architecture

**Do not use files in this directory for new development.**
EOF
```

### 4. Commit Archive
```bash
git add archived/
git commit -m "Archive legacy stock sync services - replaced by TDS"
git push origin main
```

- [ ] Archive directory created
- [ ] Legacy files moved
- [ ] Archive documented
- [ ] Changes committed

---

## ⚠️ Rollback Plan

**If Critical Issues Occur:**

### 1. Immediate Rollback
```bash
# Revert to previous tag
git checkout v2.0.1

# Reinstall dependencies
pip install -r requirements.txt

# Restart services
sudo systemctl restart tsh-erp-backend
```

### 2. Restore Database (if needed)
```bash
# Restore from backup
PGPASSWORD="Zcbbm.97531tsh" psql \
  "postgresql://postgres.trjjglxhteqnzmyakxhe:Zcbbm.97531tsh@aws-1-eu-north-1.pooler.supabase.com:5432/postgres" \
  < backup_prod_[timestamp].sql
```

### 3. Verify Rollback
```bash
# Test endpoints
curl https://erp.tsh.sale/api/health

# Test stock sync with old script
python scripts/sync_zoho_stock.py
```

### 4. Investigate and Fix
- Review error logs
- Identify root cause
- Create fix
- Test in staging
- Redeploy when ready

---

## 📞 Support Contacts

**Technical Lead:** Khaleel Al-Mulla
**Email:** khaleel@tsh.sale

**For Issues:**
1. Check logs: `/var/log/tsh-erp/backend.log`
2. Review deployment checklist
3. Check rollback plan
4. Contact technical lead

---

## ✅ Deployment Sign-Off

### Testing Phase
- [ ] All tests passed
- [ ] Code reviewed
- [ ] Documentation complete

**Signed by:** ________________
**Date:** ________________

### Staging Deployment
- [ ] Deployed successfully
- [ ] Verified working
- [ ] 24-48 hour monitoring complete

**Signed by:** ________________
**Date:** ________________

### Production Deployment
- [ ] Deployed successfully
- [ ] Smoke tests passed
- [ ] Monitoring in place

**Signed by:** ________________
**Date:** ________________

### Post-Deployment
- [ ] 24-hour monitoring complete
- [ ] No critical issues
- [ ] Legacy code archived

**Signed by:** ________________
**Date:** ________________

---

**Status:** Ready for Deployment
**Version:** 2.0.2
**Created by:** Claude Code & Khaleel Al-Mulla
**Date:** November 6, 2025

---

# 🚀 Good Luck with the Deployment!
