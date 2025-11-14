# Database Failure Scenarios

**Purpose:** Emergency procedures for PostgreSQL database failures
**Last Updated:** 2025-11-14
**Load via:** @docs/reference/failsafe/critical-scenarios/database-failures.md

---

## 🔴 Scenario: PostgreSQL Database Connection Failed

### Symptoms

```yaml
Error Messages:
  - sqlalchemy.exc.OperationalError: (psycopg2.OperationalError)
  - FATAL: remaining connection slots are reserved...
  - FATAL: password authentication failed
  - could not connect to server: Connection refused
  - server closed the connection unexpectedly

User Impact:
  - Production API completely down
  - All database operations failing
  - Users cannot access system
  - Data operations blocked
```

---

## 🚨 Immediate Response

### STOP (Don't Make It Worse)

```yaml
❌ DON'T:
  - Restart services repeatedly (makes it worse)
  - Try to "force" connections
  - Deploy "fixes" without testing
  - Modify database configuration blindly
  - Delete connection pool settings
```

### ASSESS (Diagnose Quickly)

```yaml
Possible Causes:
  1. Connection pool exhausted
     - Too many concurrent connections
     - Connections not being released
     - Connection leak in application

  2. Database server down
     - VPS crashed
     - PostgreSQL service stopped
     - Out of memory (OOM killer)
     - Disk full

  3. Network issue
     - VPS unreachable
     - Firewall blocking connections
     - DNS resolution failed

  4. Authentication issue
     - Credentials changed
     - Password expired
     - User permissions revoked
     - SSL certificate expired
```

### ALERT USER IF

```yaml
🚨 CRITICAL - Alert Immediately:
  □ Production database completely unreachable
  □ Database server crashed
  □ Data corruption suspected
  □ Security breach suspected

Message:
"🚨 CRITICAL: PostgreSQL database is unreachable. Production is down.
 Error: [exact error message]
 Investigating: [what you're checking]
 ETA: Will update in 5 minutes"
```

---

## 🔍 Diagnostic Steps

### Step 1: Check Database Connectivity

```bash
# Try to connect to database
PGPASSWORD='TSH@2025Secure!Production' psql \
  -h localhost \
  -U tsh_app_user \
  -d tsh_erp_production \
  -c "SELECT 1;"

# If fails, check PostgreSQL service
systemctl status postgresql

# Check PostgreSQL logs
tail -100 /var/log/postgresql/postgresql-15-main.log

# Check if port is listening
netstat -tlnp | grep 5432
```

### Step 2: Check Connection Pool

```bash
# Check current connections
PGPASSWORD='TSH@2025Secure!Production' psql \
  -h localhost \
  -U tsh_app_user \
  -d tsh_erp_production \
  -c "SELECT count(*) as active_connections FROM pg_stat_activity;"

# Check max connections
PGPASSWORD='TSH@2025Secure!Production' psql \
  -h localhost \
  -U tsh_app_user \
  -d tsh_erp_production \
  -c "SHOW max_connections;"

# View active connections by application
PGPASSWORD='TSH@2025Secure!Production' psql \
  -h localhost \
  -U tsh_app_user \
  -d tsh_erp_production \
  -c "SELECT application_name, count(*) FROM pg_stat_activity GROUP BY application_name;"
```

### Step 3: Check Server Resources

```bash
# Check disk space
df -h

# Check memory usage
free -h

# Check if PostgreSQL is running
ps aux | grep postgres

# Check system logs for OOM killer
dmesg | grep -i "out of memory"
```

---

## 🛠️ Fix Implementation

### Fix 1: Connection Pool Exhausted

**If:** Too many connections, application not releasing them

**Solution:**

```yaml
1. Restart Application (releases connections):
   ssh root@167.71.39.50
   systemctl restart tsh-erp

2. Verify Connection Pool Settings:
   Check: backend/.env
   Look for: SQLALCHEMY_POOL_SIZE, SQLALCHEMY_MAX_OVERFLOW

3. Adjust if Needed:
   # Recommended settings for TSH ERP:
   SQLALCHEMY_POOL_SIZE=20
   SQLALCHEMY_MAX_OVERFLOW=40
   SQLALCHEMY_POOL_RECYCLE=3600

4. Monitor Connections:
   Watch for connection leaks in application logs
```

### Fix 2: Database Service Stopped

**If:** PostgreSQL service not running

**Solution:**

```bash
# Start PostgreSQL
ssh root@167.71.39.50
systemctl start postgresql

# Check status
systemctl status postgresql

# Enable auto-start
systemctl enable postgresql

# Verify can connect
PGPASSWORD='TSH@2025Secure!Production' psql \
  -h localhost \
  -U tsh_app_user \
  -d tsh_erp_production \
  -c "SELECT 1;"
```

### Fix 3: Disk Full

**If:** Disk space at 100%

**Solution:**

```bash
# Check disk usage
df -h

# Find large files/directories
du -sh /var/* | sort -h | tail -10

# Clear old logs (if safe)
journalctl --vacuum-time=7d

# Clear PostgreSQL WAL logs (if safe)
# CAUTION: Only if replication not enabled
# sudo -u postgres pg_archivecleanup /var/lib/postgresql/15/main/pg_wal

# Restart PostgreSQL after freeing space
systemctl restart postgresql
```

### Fix 4: Out of Memory (OOM)

**If:** PostgreSQL killed by OOM

**Solution:**

```bash
# Check OOM events
dmesg | grep -i "killed process"

# Check PostgreSQL memory settings
PGPASSWORD='TSH@2025Secure!Production' psql \
  -h localhost \
  -U postgres \
  -c "SHOW shared_buffers; SHOW work_mem; SHOW maintenance_work_mem;"

# Restart PostgreSQL
systemctl restart postgresql

# If recurring, adjust PostgreSQL memory settings
# Edit: /etc/postgresql/15/main/postgresql.conf
# Reduce: shared_buffers, work_mem
```

---

## ✅ Verification

**After fix, verify:**

```bash
# 1. Database is accessible
PGPASSWORD='TSH@2025Secure!Production' psql \
  -h localhost \
  -U tsh_app_user \
  -d tsh_erp_production \
  -c "SELECT COUNT(*) FROM products WHERE is_active = true;"

# 2. Application can connect
curl https://erp.tsh.sale/health

# 3. API endpoints work
curl https://erp.tsh.sale/api/v1/products/list?page=1&limit=10

# 4. Connection count normal
PGPASSWORD='TSH@2025Secure!Production' psql \
  -h localhost \
  -U tsh_app_user \
  -d tsh_erp_production \
  -c "SELECT count(*) FROM pg_stat_activity;"

# 5. No errors in logs
tail -50 /var/www/tsh-erp/logs/backend.log
```

---

## 🔄 Prevention

### Monitoring

```yaml
Setup Alerts:
  - Connection count > 80% of max_connections
  - Disk usage > 80%
  - Memory usage > 90%
  - PostgreSQL service down
  - Query response time > 1 second

Monitor:
  - Connection pool metrics
  - Slow queries
  - Disk space trends
  - Memory usage trends
```

### Best Practices

```yaml
Application:
  ✅ Use connection pooling (SQLAlchemy)
  ✅ Close connections explicitly
  ✅ Set connection timeouts
  ✅ Implement connection retry logic
  ✅ Monitor connection metrics

Database:
  ✅ Regular VACUUM and ANALYZE
  ✅ Monitor table bloat
  ✅ Set reasonable max_connections
  ✅ Configure appropriate memory settings
  ✅ Regular backups (automated)

Infrastructure:
  ✅ Monitor disk space (alert at 80%)
  ✅ Monitor memory (alert at 90%)
  ✅ Set up log rotation
  ✅ Configure auto-restart on crash
  ✅ Regular server maintenance
```

---

## 📝 Incident Report Template

```yaml
Incident: Database Connection Failure
Date: [YYYY-MM-DD HH:MM:SS]
Duration: [X minutes/hours]
Severity: CRITICAL

Root Cause:
  - [Exact cause identified]

Impact:
  - Production down for [X minutes]
  - [Number] users affected
  - [Specific features] unavailable

Timeline:
  - [HH:MM] Issue detected
  - [HH:MM] Root cause identified
  - [HH:MM] Fix applied
  - [HH:MM] Service restored
  - [HH:MM] Verification complete

Fix Applied:
  - [Exact changes made]

Prevention:
  - [Monitoring added]
  - [Configuration changed]
  - [Process improved]

Lessons Learned:
  - [What worked well]
  - [What to improve]
  - [Action items]
```

---

## 🚨 Rollback Plan

**If fix doesn't work or makes it worse:**

```bash
# 1. Restore from backup (if database corrupted)
# See: @docs/reference/failsafe/recovery-procedures.md

# 2. Revert configuration changes
cp /etc/postgresql/15/main/postgresql.conf.backup \
   /etc/postgresql/15/main/postgresql.conf
systemctl restart postgresql

# 3. Restart with default settings
systemctl restart postgresql

# 4. Switch to read-only mode (if needed)
# Allows users to view data while fixing writes
```

---

**Related Scenarios:**
- Performance issues: @docs/reference/failsafe/critical-scenarios/performance-issues.md
- Data corruption: @docs/reference/failsafe/critical-scenarios/data-corruption.md
- Recovery procedures: @docs/reference/failsafe/recovery-procedures.md
