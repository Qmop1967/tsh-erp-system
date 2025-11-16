# Recovery Procedures & Verification

**Purpose:** Post-incident recovery verification and backup/restore procedures
**Last Updated:** 2025-11-14
**Load via:** @docs/reference/failsafe/recovery-procedures.md

---

## ✅ Recovery Verification Checklist

**After ANY incident resolution, verify ALL of these:**

### 1. Core System Health

```bash
# Production API responding
curl https://erp.tsh.sale/health
# Expected: {"status": "healthy"}

# Staging API responding
curl https://staging.erp.tsh.sale/health
# Expected: {"status": "healthy"}

# TDS Core responding
curl https://tds.tsh.sale/api/health
# Expected: {"status": "healthy", "zoho_sync": "active"}

# Database accessible
PGPASSWORD='TSH@2025Secure!Production' psql \
  -h localhost -U tsh_app_user -d tsh_erp_production \
  -c "SELECT 1;"
# Expected: Returns 1
```

### 2. Critical Functionality Tests

```bash
# Products list loads (paginated)
curl "https://erp.tsh.sale/api/v1/products/list?page=1&limit=10"
# Expected: JSON response with products

# Authentication works
curl -X POST "https://erp.tsh.sale/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@tsh.sale","password":"test123"}'
# Expected: Returns access token

# Database queries fast
time PGPASSWORD='TSH@2025Secure!Production' psql \
  -h localhost -U tsh_app_user -d tsh_erp_production \
  -c "SELECT COUNT(*) FROM products WHERE is_active = true;"
# Expected: < 100ms
```

### 3. Zoho Sync Status

```bash
# Check sync is running
curl https://tds.tsh.sale/api/sync/stats
# Expected: last_sync < 20 minutes ago

# Check products synced recently
PGPASSWORD='TSH@2025Secure!Production' psql \
  -h localhost -U tsh_app_user -d tsh_erp_production \
  -c "SELECT MAX(zoho_last_synced_at) FROM products;"
# Expected: Timestamp < 30 minutes ago
```

### 4. No Errors in Logs

```bash
# Check backend logs (no recent errors)
tail -50 /var/www/tsh-erp/logs/backend.log | grep -i error
# Expected: No recent ERROR or CRITICAL

# Check TDS Core logs
tail -50 /var/www/tds-core/logs/tds_core.log | grep -i error
# Expected: No recent errors

# Check system logs
journalctl -u tsh-erp -n 50 | grep -i error
# Expected: No recent errors
```

### 5. Performance Normal

```bash
# API response times acceptable
time curl "https://erp.tsh.sale/api/v1/products/list?page=1&limit=100"
# Expected: < 500ms

# Database query performance
PGPASSWORD='TSH@2025Secure!Production' psql \
  -h localhost -U tsh_app_user -d tsh_erp_production \
  -c "EXPLAIN ANALYZE SELECT * FROM products WHERE is_active = true LIMIT 100;"
# Expected: Execution time < 50ms
```

### 6. User Functionality

```bash
# Users can login (test with test account)
# Expected: Successful login

# Users can view products
# Expected: Products display correctly

# Users can create orders (test in staging)
# Expected: Order created successfully

# Mobile apps can sync
# Expected: Apps receive data
```

---

## 🔄 Backup Procedures

### Daily Automated Backup

```bash
# Backup script location
/var/www/scripts/backup_database.sh

# Manual backup command
pg_dump -h localhost -U tsh_app_user \
  -d tsh_erp_production \
  -F c -b -v \
  -f /var/backups/tsh_erp_$(date +%Y%m%d_%H%M%S).dump

# Upload to AWS S3
aws s3 cp /var/backups/tsh_erp_*.dump \
  s3://tsh-erp-backups/database/ \
  --region eu-north-1
```

### Backup Verification

```bash
# List recent backups
ls -lh /var/backups/tsh_erp_*.dump | tail -5

# Check backup file size (should be ~100-150 MB)
du -h /var/backups/tsh_erp_latest.dump

# Verify backup integrity
pg_restore -l /var/backups/tsh_erp_latest.dump | head -20
# Expected: Lists database objects

# Check S3 backups
aws s3 ls s3://tsh-erp-backups/database/ --region eu-north-1 | tail -10
```

### Backup Retention

```yaml
Local Backups (/var/backups/):
  - Daily backups: Keep 30 days
  - Weekly backups: Keep 12 weeks
  - Monthly backups: Keep 12 months

AWS S3 Backups:
  - Daily backups: Keep 90 days
  - Weekly backups: Keep 1 year
  - Monthly backups: Keep 7 years

Automated Cleanup:
  - Runs daily at 3:00 AM
  - Removes backups older than retention policy
  - Logs cleanup operations
```

---

## 🔙 Restore Procedures

### Pre-Restore Checklist

```yaml
Before restoring from backup:
  □ Document current database state
  □ Create emergency backup of current database
  □ Verify backup file integrity
  □ Confirm backup timestamp is correct
  □ Alert all users of planned downtime
  □ Stop all services accessing database
  □ Have rollback plan ready
```

### Database Restore (Full)

```bash
# 1. Stop services
systemctl stop tsh-erp
systemctl stop tds-core

# 2. Create emergency backup of current state
pg_dump -h localhost -U tsh_app_user \
  -d tsh_erp_production \
  -F c -b -v \
  -f /var/backups/emergency_backup_$(date +%Y%m%d_%H%M%S).dump

# 3. Drop existing database (CAUTION!)
PGPASSWORD='TSH@2025Secure!Production' psql \
  -h localhost -U postgres \
  -c "DROP DATABASE tsh_erp_production;"

# 4. Recreate database
PGPASSWORD='TSH@2025Secure!Production' psql \
  -h localhost -U postgres \
  -c "CREATE DATABASE tsh_erp_production OWNER tsh_app_user;"

# 5. Restore from backup
pg_restore -h localhost -U tsh_app_user \
  -d tsh_erp_production \
  -v /var/backups/tsh_erp_backup.dump

# 6. Verify restore
PGPASSWORD='TSH@2025Secure!Production' psql \
  -h localhost -U tsh_app_user \
  -d tsh_erp_production \
  -c "SELECT COUNT(*) FROM products;"
# Expected: ~2,218 products

# 7. Restart services
systemctl start tsh-erp
systemctl start tds-core

# 8. Verify system functional
curl https://erp.tsh.sale/health
```

### Selective Table Restore

```bash
# If only specific table needs restore:

# 1. Restore single table from backup
pg_restore -h localhost -U tsh_app_user \
  -d tsh_erp_production \
  -t products \
  -v /var/backups/tsh_erp_backup.dump

# 2. Verify table data
PGPASSWORD='TSH@2025Secure!Production' psql \
  -h localhost -U tsh_app_user \
  -d tsh_erp_production \
  -c "SELECT COUNT(*) FROM products;"
```

### Point-in-Time Recovery

```bash
# PostgreSQL WAL-based recovery (if configured)

# 1. Stop PostgreSQL
systemctl stop postgresql

# 2. Restore base backup
# (Base backup from last night)

# 3. Apply WAL files up to desired point
# Configure recovery.conf with:
# restore_command = 'cp /var/lib/postgresql/15/main/pg_wal/%f %p'
# recovery_target_time = '2025-11-14 10:30:00'

# 4. Start PostgreSQL (recovery mode)
systemctl start postgresql

# 5. Verify recovery point
# PostgreSQL will stop at specified time
```

---

## 🏥 Health Check Endpoints

### Production Health Checks

```yaml
Backend:
  URL: https://erp.tsh.sale/health
  Expected: {"status": "healthy", "database": "connected"}
  Response Time: < 100ms

TDS Core:
  URL: https://tds.tsh.sale/api/health
  Expected: {"status": "healthy", "zoho_sync": "active"}
  Response Time: < 200ms

Database:
  Command: PGPASSWORD='...' psql -c "SELECT 1;"
  Expected: Returns 1
  Response Time: < 50ms
```

### Detailed Health Check

```bash
# Backend detailed health
curl https://erp.tsh.sale/health/detailed
# Returns:
# {
#   "status": "healthy",
#   "database": {
#     "status": "connected",
#     "connections": 15,
#     "response_time_ms": 45
#   },
#   "redis": {
#     "status": "connected",
#     "memory_used": "52MB"
#   },
#   "disk_space": {
#     "total": "50GB",
#     "used": "25GB",
#     "available": "25GB",
#     "percent": 50
#   }
# }
```

---

## 📊 Monitoring After Recovery

### First Hour After Recovery

```yaml
Monitor Every 5 Minutes:
  □ API response times
  □ Error rate
  □ Database connections
  □ Memory usage
  □ Disk I/O

Check:
  □ No new errors in logs
  □ All services running
  □ Zoho sync active
  □ Users can access system
  □ Performance normal
```

### First 24 Hours After Recovery

```yaml
Monitor Every Hour:
  □ System stability
  □ Error trends
  □ Performance metrics
  □ User feedback
  □ Data consistency

Check:
  □ No recurring errors
  □ Sync operations normal
  □ Database performance stable
  □ No unusual resource usage
```

---

## 📝 Post-Recovery Documentation

### Incident Report (Required)

```yaml
Document:
  - What failed
  - Root cause
  - Timeline of events
  - Fix applied
  - Verification steps
  - Prevention measures
  - Lessons learned

Save To:
  - /TSH/PORTAL/ENGINEERING/INCIDENTS/[date]_incident_report.md
  - Update: @docs/reference/failsafe/failure-patterns.md
```

### Update Monitoring

```yaml
After Every Incident:
  - Add monitoring for root cause
  - Set up alerts to detect early
  - Update runbooks with learnings
  - Share with team
  - Test incident response
```

---

## ✅ Recovery Success Criteria

**System is fully recovered when:**

```yaml
Technical:
  ✅ All services running
  ✅ No errors in logs
  ✅ Performance normal (< 500ms)
  ✅ Database accessible
  ✅ Zoho sync active
  ✅ All health checks green

Functional:
  ✅ Users can login
  ✅ Users can view products
  ✅ Users can create orders
  ✅ Mobile apps functional
  ✅ Reports generating
  ✅ Admin functions working

Business:
  ✅ No data loss
  ✅ No transaction failures
  ✅ Customers not impacted
  ✅ Operations normal
  ✅ Stakeholders informed
```

---

**Related Procedures:**
- Response framework: @docs/reference/failsafe/response-framework.md
- Critical scenarios: @docs/reference/failsafe/critical-scenarios/
- Failure patterns: @docs/reference/failsafe/failure-patterns.md
