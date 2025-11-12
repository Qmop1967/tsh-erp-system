# Failsafe Protocol - System Failure Recovery

**Purpose:** Define exactly what Claude Code should do during system failures, errors, and degraded conditions.

**Last Updated:** 2025-11-12

---

## 🎯 Core Principle

**When systems fail, STABILITY and DATA INTEGRITY are priority #1.**

Never make things worse by:
- Panicking and making random changes
- Deploying "fixes" without testing
- Ignoring errors hoping they'll resolve
- Bypassing safety mechanisms
- Making irreversible data changes

---

## 🚨 Failure Response Framework

### Immediate Response Checklist

When ANY failure occurs:

```yaml
1. STOP & ASSESS (Don't Act Immediately):
   □ What exactly failed? (specific component)
   □ Is this affecting users right now? (production down?)
   □ Is data at risk? (corruption, loss)
   □ What's the blast radius? (how many users affected)

2. ALERT KHALEEL (If Critical):
   □ Production system down
   □ Data corruption detected
   □ Security breach suspected
   □ Financial transaction failures
   □ Zoho sync completely broken (no data for hours)

3. GATHER EVIDENCE (Don't Guess):
   □ Check logs (backend, TDS Core, GitHub Actions)
   □ Check system status (VPS, database, APIs)
   □ Check recent changes (git log, deployments)
   □ Document exact error messages

4. CONTAIN DAMAGE (If Possible):
   □ Stop failing process (if causing more damage)
   □ Switch to degraded mode (if available)
   □ Prevent data corruption (stop writes if risky)
   □ Isolate affected component

5. DIAGNOSE ROOT CAUSE (Apply REASONING_PATTERNS.md):
   □ Use Root-Cause Analysis pattern
   □ Don't fix symptoms, find actual cause
   □ Test hypotheses systematically

6. IMPLEMENT FIX (Safely):
   □ Test fix in staging first (if time permits)
   □ Apply minimal change needed
   □ Have rollback ready
   □ Monitor closely after fix
```

---

## 🔴 Critical Failure Scenarios

### Scenario 1: PostgreSQL Database Connection Failed

**Symptoms:**
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError)
FATAL: remaining connection slots are reserved...
```

#### Immediate Response

```yaml
STOP:
□ Don't restart services repeatedly (makes it worse)
□ Don't try to "force" connections

ASSESS:
□ Connection pool exhausted? (too many concurrent connections)
□ Database server down? (VPS crashed, PostgreSQL stopped)
□ Network issue? (VPS unreachable)
□ Authentication issue? (credentials changed)

ALERT KHALEEL IF:
□ Production database completely unreachable
□ Database server crashed
□ Data corruption suspected

CONTAIN:
□ If connection pool exhausted: implement connection limit
□ If too many queries: add rate limiting
□ If specific endpoint: disable that endpoint temporarily

DIAGNOSE:
# Check database server status
ssh root@167.71.39.50 "systemctl status postgresql"

# Check active connections
PGPASSWORD='TSH@2025Secure!Production' psql -h localhost -U tsh_app_user -d tsh_erp_production -c "SELECT count(*) FROM pg_stat_activity;"

# Check connection pool settings
cat app/database.py | grep pool_size

# Check recent errors
tail -100 /var/log/postgresql/postgresql-*.log

FIX (Based on diagnosis):
1. Connection pool exhausted → Increase pool_size or add connection cleanup
2. Database server down → Restart PostgreSQL service
3. Network issue → Check VPS network connectivity
4. Too many concurrent requests → Add rate limiting
```

#### Recovery Steps

```bash
# Option 1: Restart PostgreSQL (if server issue)
ssh root@167.71.39.50 "systemctl restart postgresql"

# Option 2: Kill idle connections (if pool exhausted)
PGPASSWORD='TSH@2025Secure!Production' psql -h localhost -U tsh_app_user -d tsh_erp_production -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
AND state_change < NOW() - INTERVAL '5 minutes';
"

# Option 3: Increase connection pool (if capacity issue)
# Edit app/database.py:
# engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=40)

# Verify recovery
curl https://erp.tsh.sale/health
```

---

### Scenario 2: GitHub Actions Deployment Failed

**Symptoms:**
```
GitHub Actions workflow "Deploy to Production" failed
Exit code: 1
```

#### Immediate Response

```yaml
STOP:
□ Don't push more commits hoping it fixes itself
□ Don't manually SSH and "fix" production

ASSESS:
□ Which component failed? (backend, frontend, TDS Core)
□ Build failure? (syntax error, dependency issue)
□ Test failure? (tests failing)
□ Deployment failure? (VPS unreachable, permission issue)
□ Is production currently broken or still on old version?

ALERT KHALEEL IF:
□ Production is down (old version broken, new version not deployed)
□ Can't rollback automatically

CONTAIN:
□ If production is still on old (working) version: no immediate action needed
□ If production is broken: prepare rollback

DIAGNOSE:
# Check GitHub Actions logs
gh run list --limit 5
gh run view <run-id> --log-failed

# Check which step failed
# Common failures:
# - Tests failed → Fix tests
# - Build failed → Fix code/dependencies
# - Deploy failed → VPS/permission issue
# - Smoke test failed → Deployment broke something

FIX (Based on diagnosis):
1. Tests failed → Fix failing tests, commit, push
2. Build failed → Fix syntax/import errors, commit, push
3. Deploy failed → Check VPS accessibility, disk space, permissions
4. Smoke test failed → Rollback and fix issue in staging first
```

#### Recovery Steps

```bash
# Option 1: Fix and re-deploy
# 1. Fix the issue locally
# 2. Test locally
# 3. Commit and push
# 4. Monitor new GitHub Actions run

# Option 2: Rollback to previous version
git revert <commit-hash>
git push origin main

# Option 3: Manual rollback on VPS (emergency only)
ssh root@167.71.39.50
cd /var/www/tsh-erp
git log --oneline -5  # Find last working commit
git checkout <last-working-commit>
sudo systemctl restart tsh-erp
sudo systemctl restart nginx

# Verify recovery
curl https://erp.tsh.sale/health
curl https://consumer.tsh.sale/
```

---

### Scenario 3: TDS Core Zoho Sync Stopped Working

**Symptoms:**
```
TDS Dashboard shows:
- Last sync: 3 hours ago (should be every 15 minutes)
- Sync status: Failed
- Error: 401 Unauthorized
```

#### Immediate Response

```yaml
STOP:
□ Don't restart TDS Core repeatedly (might make rate limit worse)
□ Don't bypass TDS Core and access Zoho directly

ASSESS:
□ Authentication failure? (token expired)
□ Rate limit hit? (too many API calls)
□ Network issue? (can't reach Zoho APIs)
□ Zoho service down? (rare but possible)
□ Bug in TDS Core? (recent code change)

ALERT KHALEEL IF:
□ Sync broken for > 4 hours (data getting stale)
□ Orders can't be processed due to stale data
□ Token refresh failing repeatedly

CONTAIN:
□ If token expired: refresh token
□ If rate limit: slow down sync frequency temporarily
□ If bug: rollback TDS Core to previous version

DIAGNOSE:
# Check TDS Core logs
ssh root@167.71.39.50
cd /var/www/tds-core
tail -100 logs/tds_core.log

# Check TDS Dashboard
curl https://tds.tsh.sale/api/sync/status

# Test Zoho API connectivity (via TDS Core)
# DO NOT test directly - must go through TDS Core

# Check token expiration
# Tokens expire every 1 hour (access token) or 3 months (refresh token)

FIX (Based on diagnosis):
1. Token expired → Refresh token via TDS Core
2. Rate limit → Reduce sync frequency temporarily
3. Network issue → Check VPS network, Zoho status
4. Bug → Rollback TDS Core code
```

#### Recovery Steps

```bash
# Option 1: Refresh Zoho tokens (most common)
ssh root@167.71.39.50
cd /var/www/tds-core
python scripts/refresh_zoho_tokens.py

# Verify tokens refreshed
cat .env | grep ZOHO_ACCESS_TOKEN

# Restart TDS Core
sudo systemctl restart tds-core

# Option 2: Reduce sync frequency (if rate limit)
# Edit TDS Core config:
# SYNC_INTERVAL=30  # minutes (instead of 15)
sudo systemctl restart tds-core

# Option 3: Rollback TDS Core (if bug)
cd /var/www/tds-core
git log --oneline -5
git checkout <last-working-commit>
sudo systemctl restart tds-core

# Verify recovery
curl https://tds.tsh.sale/api/sync/status
# Should show: "Last sync: < 20 minutes ago, Status: Success"
```

---

### Scenario 4: Production API Returning 500 Errors

**Symptoms:**
```
Multiple endpoints returning:
HTTP 500 Internal Server Error
```

#### Immediate Response

```yaml
STOP:
□ Don't deploy new code hoping it fixes itself
□ Don't restart services without diagnosing

ASSESS:
□ All endpoints affected or specific ones?
□ When did it start? (after deployment? specific time?)
□ Error pattern? (always fail or intermittent?)
□ Logs showing specific error? (check backend logs)

ALERT KHALEEL IF:
□ All critical operations failing (orders, payments)
□ Affecting all users
□ Data corruption suspected

CONTAIN:
□ If specific endpoint: disable that endpoint temporarily
□ If recent deployment caused it: prepare rollback
□ If database issue: stop write operations if risky

DIAGNOSE:
# Check backend logs
ssh root@167.71.39.50
cd /var/www/tsh-erp
tail -100 logs/backend.log | grep ERROR

# Check specific error
curl -v https://erp.tsh.sale/api/products
# Look at response body for stack trace

# Common causes:
# - Unhandled exception (bug in code)
# - Database connection lost
# - Missing environment variable
# - Disk space full
# - Memory exhausted

FIX (Based on diagnosis):
1. Bug in code → Rollback to previous version
2. Database issue → Fix database connection
3. Environment variable missing → Add to .env, restart
4. Disk space full → Clean up logs/temp files
5. Memory exhausted → Restart service, investigate memory leak
```

#### Recovery Steps

```bash
# Quick diagnostics
ssh root@167.71.39.50

# Check disk space
df -h
# If > 90% full: clean up logs
find /var/log -name "*.log" -mtime +7 -delete

# Check memory
free -h
# If memory exhausted: restart services

# Check service status
systemctl status tsh-erp

# Check logs for specific error
journalctl -u tsh-erp -n 100 --no-pager

# If deployment caused issue: rollback
cd /var/www/tsh-erp
git log --oneline -5
git checkout <last-working-commit>
sudo systemctl restart tsh-erp

# Verify recovery
curl https://erp.tsh.sale/health
```

---

### Scenario 5: Data Corruption Detected

**Symptoms:**
```
- Orders showing wrong products
- Stock levels negative
- Client data mixed up
- Financial totals don't match
```

#### Immediate Response

```yaml
STOP EVERYTHING:
🚨 CRITICAL: Data integrity compromised
□ Stop all write operations immediately
□ Don't try to "fix" data manually
□ Don't run migrations or scripts

ALERT KHALEEL IMMEDIATELY:
□ This requires human decision
□ May need database restore from backup
□ Legal/business implications

CONTAIN:
□ Stop backend services (prevent more corruption)
sudo systemctl stop tsh-erp

□ Stop TDS Core (prevent Zoho sync)
sudo systemctl stop tds-core

□ Make database backup immediately (even corrupted)
pg_dump -h localhost -U tsh_app_user tsh_erp_production > /tmp/corrupted_backup_$(date +%Y%m%d_%H%M%S).sql

DIAGNOSE (Carefully):
□ When did corruption start? (specific time)
□ What changed? (deployment, migration, manual edit)
□ Scope of corruption? (all records or subset)
□ Root cause? (bug, manual error, sync issue)

# Check recent database changes
\d+ orders  # Check schema
SELECT * FROM orders ORDER BY updated_at DESC LIMIT 10;

# Check recent code changes
git log --since="24 hours ago" --oneline

# Check recent migrations
alembic history | head -5

RECOVERY OPTIONS (Wait for Khaleel):
Option 1: Restore from AWS S3 backup
- Check backup age (acceptable data loss?)
- Restore to staging first, verify
- Then restore to production

Option 2: Rollback specific migration
- If migration caused corruption
- Test rollback in staging first

Option 3: Manual data fix
- Only if corruption scope is small and identified
- Script the fix, test in staging
- Apply carefully with transaction

DO NOT PROCEED WITHOUT KHALEEL APPROVAL
```

---

## 🟡 Non-Critical Failure Scenarios

### Scenario 6: Single Endpoint Slow (> 5 seconds)

**Symptoms:**
```
/api/products endpoint taking 8 seconds
Users complaining about slowness
```

#### Response (Non-Urgent)

```yaml
ASSESS:
□ Which endpoint?
□ How slow? (2s vs. 10s vs. timeout)
□ Always slow or intermittent?
□ Recent change or longstanding?

DIAGNOSE:
# Use Performance Analysis pattern from REASONING_PATTERNS.md
1. Measure current performance
2. Identify bottleneck (database, API, computation)
3. Calculate impact (how many users affected)
4. Optimize strategically

# Check database query performance
EXPLAIN ANALYZE SELECT * FROM products WHERE is_active = true;

# Look for:
- Seq Scan (missing index)
- No pagination (loading all 2,218 products)
- N+1 queries (multiple small queries)

FIX:
1. Add pagination (max 100 per page)
2. Add database index
3. Optimize query (use joins instead of N+1)
4. Cache if appropriate

# Deploy fix to staging, test, then production
```

---

### Scenario 7: Frontend Component Not Rendering

**Symptoms:**
```
React component showing blank or error
Browser console: TypeError: Cannot read property 'name' of undefined
```

#### Response (Non-Urgent)

```yaml
DIAGNOSE:
# Check browser console
# Check API response (is data structure correct?)
# Check component code (null handling?)

COMMON CAUSES:
1. API returning null/undefined
2. Missing null checks in component
3. Wrong property name
4. Async data not loaded yet

FIX:
# Add null checks
{product?.name || 'N/A'}

# Or use optional chaining
{product && product.name}

# Or show loading state
{loading ? <Spinner /> : <ProductDisplay product={product} />}

# Test locally, deploy to staging, then production
```

---

## 🛡️ Safe-Mode Operations

### When Normal Operations Fail

**Degraded Mode Capabilities:**

```yaml
If Database Unreachable:
□ Return cached data (if available)
□ Return 503 Service Unavailable (don't fake data)
□ Queue writes for later (if safe)
□ Show maintenance message to users

If Zoho Sync Broken:
□ Continue using last synced data
□ Show "data may be outdated" warning
□ Allow manual sync trigger
□ Don't block critical operations (orders can still be created locally)

If VPS Overloaded:
□ Disable non-critical endpoints temporarily
□ Reduce sync frequency
□ Serve static cached pages
□ Scale up VPS if budget allows

If Specific Service Down:
□ Disable that feature gracefully
□ Don't break entire application
□ Show user-friendly error message
□ Log for investigation
```

---

## 📋 Recovery Verification Checklist

### After Any Fix

```yaml
Before Marking Issue Resolved:
□ Root cause identified and fixed (not just symptom)
□ Tested in staging (if time permitted)
□ Deployed to production
□ Monitored for 30+ minutes (ensure stability)
□ All health checks passing:
  ✓ curl https://erp.tsh.sale/health → 200 OK
  ✓ curl https://consumer.tsh.sale/ → 200 OK
  ✓ curl https://tds.tsh.sale/api/sync/status → Success

□ No new errors in logs
□ Performance acceptable
□ Users can complete critical operations:
  ✓ Login
  ✓ View products
  ✓ Create orders
  ✓ View reports

□ Documentation updated (if new failure pattern discovered)
□ Khaleel informed of resolution
```

---

## 🔄 Backup & Restore Procedures

### Database Backup

**Automatic Backups:**
```bash
# Daily automated backup to AWS S3
# Location: s3://tsh-erp-backups/database/
# Retention: 30 days

# Check latest backup
aws s3 ls s3://tsh-erp-backups/database/ --recursive | sort | tail -5
```

**Manual Backup:**
```bash
# Before risky operations, create manual backup
ssh root@167.71.39.50
pg_dump -h localhost -U tsh_app_user tsh_erp_production | gzip > /tmp/manual_backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Upload to S3
aws s3 cp /tmp/manual_backup_*.sql.gz s3://tsh-erp-backups/database/manual/
```

### Database Restore

**⚠️ CRITICAL: Only with Khaleel approval**

```bash
# Step 1: Download backup from S3
aws s3 cp s3://tsh-erp-backups/database/backup_YYYYMMDD.sql.gz /tmp/

# Step 2: Extract
gunzip /tmp/backup_YYYYMMDD.sql.gz

# Step 3: STOP all services
sudo systemctl stop tsh-erp
sudo systemctl stop tds-core

# Step 4: Restore (REPLACES ALL DATA)
psql -h localhost -U tsh_app_user -d tsh_erp_production < /tmp/backup_YYYYMMDD.sql

# Step 5: Restart services
sudo systemctl start tsh-erp
sudo systemctl start tds-core

# Step 6: Verify
curl https://erp.tsh.sale/health
PGPASSWORD='TSH@2025Secure!Production' psql -h localhost -U tsh_app_user -d tsh_erp_production -c "SELECT COUNT(*) FROM products;"
```

---

## 🚨 Emergency Contacts & Resources

### Khaleel Contact
```yaml
When to Alert Immediately:
🚨 Production completely down
🚨 Data corruption detected
🚨 Security breach suspected
🚨 Financial transaction failures
🚨 Cannot restore service within 30 minutes

Method: [Khaleel will specify preferred contact method]
```

### System Resources

```yaml
VPS Access:
Host: 167.71.39.50
User: root
Access: SSH key

Database:
Host: localhost (on VPS)
Database: tsh_erp_production
User: tsh_app_user
Password: [in .env file]

AWS S3:
Bucket: tsh-erp-backups
Region: eu-north-1
Backups: /database/ folder

GitHub:
Repository: https://github.com/Qmop1967/tsh-erp-system
Actions: Deployment logs and history

Zoho:
Organization: 748369814
Books: https://books.zoho.com/app#/home/dashboard/748369814
Inventory: https://inventory.zoho.com/app#/home/748369814
Access: Via TDS Core ONLY
```

---

## 📚 Failure Pattern Knowledge Base

**Purpose:** Comprehensive error catalog for fast diagnosis and recovery. Use this as first reference when encountering errors.

**Structure:** Error Pattern → Root Cause → Solution → Related Template → Preventive Rule

---

### Category 1: Database Errors

#### Error 1.1: Connection Pool Exhausted

**Error Message:**
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError)
FATAL: remaining connection slots are reserved for non-replication superuser connections
```

**Root Cause:**
- Too many concurrent database connections (> pool_size + max_overflow)
- Connection leaks (connections not properly closed)
- Sudden traffic spike
- Long-running queries holding connections

**Solution:**
```bash
# Immediate fix: Kill idle connections
PGPASSWORD='TSH@2025Secure!Production' psql -h localhost -U tsh_app_user -d tsh_erp_production -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
AND state_change < NOW() - INTERVAL '10 minutes';
"

# Long-term fix: Increase pool size (app/database.py)
engine = create_engine(
    DATABASE_URL,
    pool_size=30,          # Was 20
    max_overflow=50,       # Was 40
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True
)
```

**Related Template:**
- CODE_TEMPLATES.md → Template 9.3: Connection Pool Configuration

**Preventive Rule:**
- ARCHITECTURE_RULES.md: Always use context managers (with statements) for database sessions
- Monitor active connections: `SELECT count(*) FROM pg_stat_activity;`
- Set up alerts when connections > 80% of pool_size

---

#### Error 1.2: N+1 Query Performance Issue

**Error Message:**
```
API response time: 8.5 seconds (expected < 500ms)
Database logs showing 500+ SELECT queries for single endpoint
```

**Root Cause:**
- Missing eager loading (joinedload/selectinload)
- Accessing relationships in loops
- Common in list endpoints with related data

**Solution:**
```python
# ❌ BAD: N+1 queries
orders = db.query(Order).limit(100).all()
for order in orders:
    client_name = order.client.name  # 100 additional queries!

# ✅ GOOD: Eager loading
from sqlalchemy.orm import joinedload, selectinload

orders = db.query(Order).options(
    joinedload(Order.client),              # Load clients (1 query)
    selectinload(Order.items).             # Load items (1 query)
        joinedload(OrderItem.product)      # Load products (joined)
).limit(100).all()

# Result: 2-3 queries instead of 500+
```

**Related Template:**
- CODE_TEMPLATES.md → Template 7.3: Efficient Eager Loading
- PERFORMANCE_OPTIMIZATION.md → Section: N+1 Query Prevention

**Preventive Rule:**
- ALWAYS use eager loading for relationships accessed in loops
- Test endpoints with realistic data (> 100 records)
- Add SQL query logging in development: `echo=True` in create_engine

---

#### Error 1.3: Deadlock Detected

**Error Message:**
```
psycopg2.extensions.TransactionRollbackError: deadlock detected
DETAIL: Process 1234 waits for ShareLock on transaction 5678
```

**Root Cause:**
- Two transactions locking rows in different orders
- Common in order processing + stock updates
- Race condition between concurrent requests

**Solution:**
```python
# ❌ BAD: Locks in inconsistent order
def process_order_bad(order_id):
    order = db.query(Order).filter_by(id=order_id).first()  # Lock order
    product = db.query(Product).filter_by(id=order.product_id).first()  # Lock product
    # Process...

# ✅ GOOD: Use SELECT FOR UPDATE with consistent ordering
def process_order_good(order_id):
    # Always lock in same order: products first, then orders
    product = db.query(Product).filter_by(id=product_id)\
        .with_for_update().first()  # Explicit row lock

    order = db.query(Order).filter_by(id=order_id)\
        .with_for_update().first()

    # Update stock atomically
    product.actual_available_stock -= order.quantity
    db.commit()
```

**Related Template:**
- CODE_TEMPLATES.md → Template 7.5: Transaction Locking Patterns

**Preventive Rule:**
- Use SELECT FOR UPDATE for concurrent operations
- Lock resources in consistent order (alphabetical by table name)
- Keep transactions short (< 1 second)

---

#### Error 1.4: Missing Index on Large Table

**Error Message:**
```
EXPLAIN ANALYZE showing:
Seq Scan on products (cost=0.00..4521.18 rows=2218 width=850) (actual time=2.347..125.482 rows=2218 loops=1)
```

**Root Cause:**
- No index on frequently queried column
- Table scan instead of index scan
- Common on search fields, foreign keys, filter fields

**Solution:**
```sql
-- Identify missing indexes
EXPLAIN ANALYZE
SELECT * FROM products WHERE category_id = 5;
-- If shows "Seq Scan" → missing index

-- Create index
CREATE INDEX idx_products_category_id ON products(category_id);

-- Verify improvement
EXPLAIN ANALYZE
SELECT * FROM products WHERE category_id = 5;
-- Should now show "Index Scan" with much lower cost

-- Common indexes for TSH ERP (products table)
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_is_active ON products(is_active);
CREATE INDEX idx_products_name ON products(name);
CREATE INDEX idx_products_name_ar ON products(name_ar);

-- Compound index for common filter combinations
CREATE INDEX idx_products_active_category ON products(is_active, category_id);
```

**Related Template:**
- PERFORMANCE_OPTIMIZATION.md → Section: Database Indexing Strategy

**Preventive Rule:**
- ALWAYS index foreign keys
- Index columns used in WHERE, ORDER BY, JOIN
- For tables > 1,000 rows: review indexes monthly
- TSH scale (2,218+ products): indexes are mandatory

---

#### Error 1.5: Foreign Key Constraint Violation

**Error Message:**
```
sqlalchemy.exc.IntegrityError: (psycopg2.errors.ForeignKeyViolation)
insert or update on table "orders" violates foreign key constraint "fk_orders_client_id"
DETAIL: Key (client_id)=(999) is not present in table "clients"
```

**Root Cause:**
- Trying to insert/update with non-existent foreign key
- Client/product/user deleted but referenced elsewhere
- Race condition (record deleted between validation and insert)

**Solution:**
```python
# ❌ BAD: No validation
def create_order(client_id, product_id):
    order = Order(client_id=client_id, product_id=product_id)
    db.add(order)
    db.commit()  # May fail with ForeignKeyViolation

# ✅ GOOD: Validate existence first
def create_order(client_id, product_id, db: Session):
    # Validate client exists
    client = db.query(Client).filter_by(id=client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Validate product exists
    product = db.query(Product).filter_by(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Now safe to create order
    order = Order(client_id=client_id, product_id=product_id)
    db.add(order)
    db.commit()
```

**Related Template:**
- CODE_TEMPLATES.md → Template 2.3: Create with Validation
- CODE_TEMPLATES.md → Template 5.1: Validation Error Response

**Preventive Rule:**
- ALWAYS validate foreign key existence before insert/update
- Use Pydantic schemas with validation
- Consider soft deletes (is_active=False) instead of hard deletes

---

### Category 2: Zoho Sync Errors

#### Error 2.1: Zoho API 401 Unauthorized

**Error Message:**
```
TDS Core logs:
ERROR: Zoho API request failed
Status: 401 Unauthorized
Response: {"code": 57, "message": "Invalid OAuth Token"}
```

**Root Cause:**
- Access token expired (valid for 1 hour)
- Refresh token expired (valid for 3 months)
- Token revoked manually in Zoho console
- Clock skew between VPS and Zoho servers

**Solution:**
```bash
# Step 1: Check token age
ssh root@167.71.39.50
cd /var/www/tds-core
cat .env | grep ZOHO_ACCESS_TOKEN_EXPIRY
# If expired, refresh

# Step 2: Refresh access token
python scripts/refresh_zoho_tokens.py

# Step 3: Verify refresh worked
cat .env | grep ZOHO_ACCESS_TOKEN
# Should see new token

# Step 4: Restart TDS Core
sudo systemctl restart tds-core

# Step 5: Verify sync resumed
curl https://tds.tsh.sale/api/sync/status
# Should show recent sync time
```

**If refresh token also expired (rare):**
```bash
# Need manual re-authorization (contact Khaleel)
# This requires browser-based OAuth flow
# Khaleel must visit Zoho, authorize app, get new tokens
```

**Related Template:**
- CODE_TEMPLATES.md → Template 3.1: Sync Products from Zoho (via TDS Core)

**Preventive Rule:**
- Automate token refresh every 50 minutes (before 1-hour expiry)
- Monitor token expiry in TDS Dashboard
- Alert if refresh fails 3 times consecutively

---

#### Error 2.2: Zoho API 429 Rate Limit Exceeded

**Error Message:**
```
TDS Core logs:
ERROR: Zoho API request failed
Status: 429 Too Many Requests
Response: {"code": 4820, "message": "Rate limit exceeded. Please try after 60 seconds."}
```

**Root Cause:**
- Exceeded Zoho API rate limits
- Zoho Books: 200 requests per minute per organization
- Zoho Inventory: 100 requests per minute per organization
- Sync frequency too high (e.g., every 5 minutes with 300+ API calls)

**Solution:**
```bash
# Immediate: Pause sync temporarily
ssh root@167.71.39.50
sudo systemctl stop tds-core

# Wait 60 seconds
sleep 60

# Reduce sync frequency (tds-core/.env)
nano /var/www/tds-core/.env
# Change: SYNC_INTERVAL=30  (was 15 minutes)

# Implement exponential backoff in TDS Core
# (Khaleel to implement in TDS Core code)

# Restart with new settings
sudo systemctl start tds-core
```

**Long-term optimization:**
```python
# TDS Core optimization: Batch requests
# ❌ BAD: 2,218 individual product requests
for product_id in product_ids:
    product = zoho.get_item(product_id)  # 2,218 API calls!

# ✅ GOOD: Batch 200 products per request
# Zoho supports pagination: per_page=200
products = zoho.get_items(page=1, per_page=200)  # 12 API calls for 2,218 products
```

**Related Template:**
- PERFORMANCE_OPTIMIZATION.md → Section: Zoho API Optimization

**Preventive Rule:**
- Batch Zoho requests (max 200 items per page)
- Sync interval >= 15 minutes (TSH current scale)
- Monitor API usage in TDS Dashboard
- Implement exponential backoff on rate limit errors

---

#### Error 2.3: Zoho Data Mismatch (Stock Levels Wrong)

**Error Message:**
```
TDS Dashboard alert:
Product SKU "ABC123": Zoho stock = 50, ERP stock = 30
Mismatch detected in 15 products
```

**Root Cause:**
- Sync delay (Zoho updated but TDS hasn't synced yet)
- Manual edit in Zoho after last sync
- TDS Core failed to sync specific items (partial sync failure)
- Different stock calculation rules (available vs. on-hand)

**Solution:**
```bash
# Step 1: Check last sync time
curl https://tds.tsh.sale/api/sync/status
# If > 20 minutes ago, sync may be stuck

# Step 2: Force immediate sync
curl -X POST https://tds.tsh.sale/api/sync/trigger \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Step 3: Verify specific product
PGPASSWORD='TSH@2025Secure!Production' psql -h localhost -U tsh_app_user -d tsh_erp_production -c "
SELECT sku, name, actual_available_stock, zoho_item_id
FROM products
WHERE sku = 'ABC123';
"

# Step 4: Check Zoho directly (via TDS Core API)
curl https://tds.tsh.sale/api/zoho/item/$ZOHO_ITEM_ID

# Step 5: If mismatch persists, manual reconciliation
# Update ERP to match Zoho (source of truth in Phase 1)
```

**Related Template:**
- CODE_TEMPLATES.md → Template 3.2: Handle Sync Conflicts

**Preventive Rule:**
- Zoho is source of truth in Phase 1 (read-only)
- Sync interval: 15 minutes (balance freshness vs. rate limits)
- Add "Last synced" timestamp to product display
- Alert on sync delays > 30 minutes

---

### Category 3: API & Backend Errors

#### Error 3.1: Pydantic Validation Error (Missing Required Field)

**Error Message:**
```
fastapi.exceptions.RequestValidationError:
[
  {
    "loc": ["body", "name_ar"],
    "msg": "field required",
    "type": "value_error.missing"
  }
]
```

**Root Cause:**
- Client didn't send required field
- Frontend form missing Arabic field input
- Common mistake: forgetting Arabic fields (name_ar, description_ar)

**Solution:**
```python
# Backend schema (already correct if this error occurs)
class ProductCreate(BaseModel):
    name: str
    name_ar: str  # Required
    description: Optional[str] = None
    description_ar: Optional[str] = None
    sku: str
    price: float

# Fix frontend to include Arabic field
# React/Flutter: Add name_ar input field to form
<TextField
  label="Name (Arabic)"
  value={nameAr}
  onChange={(e) => setNameAr(e.target.value)}
  required
/>
```

**Related Template:**
- CODE_TEMPLATES.md → Template 4.1: Pydantic Schema with Arabic Fields
- CODE_TEMPLATES.md → Template 2.3: Create with Bilingual Fields

**Preventive Rule:**
- ARCHITECTURE_RULES.md: ALWAYS include Arabic fields on user-facing models
- Required Arabic fields: name_ar, description_ar
- Validate Arabic input not empty (not just Latin transliteration)
- Show error message in user's language

---

#### Error 3.2: JWT Token Expired or Invalid

**Error Message:**
```
HTTP 401 Unauthorized
{"detail": "Could not validate credentials"}
```

**Root Cause:**
- JWT token expired (default: 30 minutes)
- Token malformed (corrupted in storage)
- Token signature invalid (SECRET_KEY changed)
- User logged out but token still in browser

**Solution:**
```python
# Backend: Check token expiration logic (app/dependencies.py)
from datetime import datetime, timedelta
from jose import jwt, JWTError

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id: int = payload.get("sub")

        # Check expiration (JWT library does this automatically)
        # If expired, JWTError raised

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

# Frontend: Implement token refresh
// When 401 received, try refresh token
if (error.response.status === 401) {
  const newToken = await refreshAccessToken();
  if (newToken) {
    // Retry original request with new token
  } else {
    // Redirect to login
    window.location.href = '/login';
  }
}
```

**Related Template:**
- CODE_TEMPLATES.md → Template 1.1: Protected API Endpoint
- CODE_TEMPLATES.md → Template 1.4: JWT Token Generation

**Preventive Rule:**
- Access token expiry: 30 minutes (balance security vs. UX)
- Refresh token expiry: 7 days
- Implement automatic token refresh (frontend)
- Clear tokens on logout

---

#### Error 3.3: CORS Error (Frontend Can't Call API)

**Error Message:**
```
Browser console:
Access to fetch at 'https://erp.tsh.sale/api/products' from origin 'https://consumer.tsh.sale'
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

**Root Cause:**
- CORS not configured in FastAPI
- Origin not in allowed list
- Preflight OPTIONS request failing
- Common when adding new frontend domain

**Solution:**
```python
# Backend: Configure CORS (app/main.py)
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://erp.tsh.sale",
        "https://consumer.tsh.sale",
        "https://shop.tsh.sale",
        "https://staging.erp.tsh.sale",
        "https://staging.consumer.tsh.sale",
        "http://localhost:3000",  # Development
        "http://localhost:8080",  # Flutter web dev
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)
```

**Related Template:**
- ARCHITECTURE_RULES.md → Section: CORS Configuration

**Preventive Rule:**
- Add all frontend domains to CORS allowed_origins
- Include staging domains
- Include localhost for development
- Test from each frontend domain after CORS changes

---

#### Error 3.4: 500 Internal Server Error (Unhandled Exception)

**Error Message:**
```
HTTP 500 Internal Server Error
Backend logs:
Traceback (most recent call last):
  File "app/routers/products.py", line 45, in get_product
    product.category.name  # AttributeError: 'NoneType' object has no attribute 'name'
```

**Root Cause:**
- Unhandled exception (None check missing)
- Accessing relationship that wasn't loaded
- Database query returned None
- Type error, key error, attribute error

**Solution:**
```python
# ❌ BAD: No null checks
@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter_by(id=product_id).first()
    category_name = product.category.name  # Crashes if product or category is None!
    return {"product": product, "category": category_name}

# ✅ GOOD: Proper error handling
@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter_by(id=product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Load relationship if needed
    category_name = product.category.name if product.category else "Uncategorized"

    return {"product": product, "category": category_name}

# ✅ BETTER: Use try/except for unexpected errors
@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    try:
        product = db.query(Product).filter_by(id=product_id).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        category_name = product.category.name if product.category else "Uncategorized"

        return {"product": product, "category": category_name}

    except HTTPException:
        raise  # Re-raise HTTP exceptions

    except Exception as e:
        # Log error for debugging
        logger.error(f"Error fetching product {product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

**Related Template:**
- CODE_TEMPLATES.md → Template 5.1: Validation Error Response
- CODE_TEMPLATES.md → Template 5.2: Database Error Response

**Preventive Rule:**
- ALWAYS check if query result is None before accessing
- Use try/except for operations that might fail
- NEVER let exceptions bubble up to user (return 500 with generic message)
- Log detailed errors server-side for debugging

---

### Category 4: Deployment & Infrastructure Errors

#### Error 4.1: GitHub Actions Deployment Failed (Tests)

**Error Message:**
```
GitHub Actions:
❌ Run tests
   pytest tests/ --cov=app
   FAILED tests/test_products.py::test_create_product - AssertionError
   Error: Process completed with exit code 1.
```

**Root Cause:**
- Test failure due to code change
- Test environment setup issue (missing dependency, wrong database)
- Test database not clean (previous test data interfering)
- Flaky test (intermittent failure)

**Solution:**
```bash
# Step 1: Run tests locally to diagnose
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem
source venv/bin/activate  # or source .venv/bin/activate
pytest tests/test_products.py::test_create_product -v

# Step 2: Check test output for specific failure
# Common issues:
# - AssertionError: expected != actual → Logic bug
# - FixtureLookupError: fixture not found → Test setup issue
# - DatabaseError: → Test database not clean

# Step 3: Fix the test or code
# If code is wrong: fix code
# If test is wrong: update test
# If test is flaky: improve test reliability

# Step 4: Re-run tests locally
pytest tests/ --cov=app

# Step 5: Commit fix and push
git add .
git commit -m "fix: resolve test failure in test_create_product"
git push origin develop
```

**Related Template:**
- CODE_TEMPLATES.md → Template 8: Testing Patterns

**Preventive Rule:**
- Run tests locally before pushing: `pytest tests/`
- Use test fixtures for clean database state
- Mock external dependencies (Zoho API, S3, etc.)
- Tests should be deterministic (no randomness, no time-dependent logic)

---

#### Error 4.2: Disk Space Full on VPS

**Error Message:**
```
ssh root@167.71.39.50 "df -h"
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda1        50G   49G  512M  99% /

Backend logs:
OSError: [Errno 28] No space left on device
```

**Root Cause:**
- Log files not rotating (growing indefinitely)
- Backup files accumulating
- Uploaded images not cleaned
- Database WAL files accumulating

**Solution:**
```bash
# Step 1: Identify what's using space
ssh root@167.71.39.50
du -sh /* | sort -rh | head -10
# Look for large directories

# Step 2: Common culprits and fixes

# Option A: Clean old logs (> 7 days)
find /var/log -name "*.log" -mtime +7 -delete
find /var/www/tsh-erp/logs -name "*.log" -mtime +7 -delete
find /var/www/tds-core/logs -name "*.log" -mtime +7 -delete

# Option B: Clean old backups (local ones, S3 is safe)
find /tmp -name "*.sql.gz" -mtime +7 -delete

# Option C: Clean Docker images (if using Docker)
docker system prune -a --volumes -f

# Option D: Vacuum PostgreSQL (reclaim space)
sudo -u postgres vacuumdb --all --full --analyze

# Step 3: Setup log rotation (prevent future)
cat > /etc/logrotate.d/tsh-erp <<EOF
/var/www/tsh-erp/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0644 www-data www-data
    sharedscripts
    postrotate
        systemctl reload tsh-erp > /dev/null 2>&1 || true
    endscript
}
EOF

# Step 4: Verify space freed
df -h
```

**Related Template:**
- ARCHITECTURE_RULES.md → Section: VPS Maintenance

**Preventive Rule:**
- Setup log rotation (keep 7 days)
- Monitor disk space (alert at 80%)
- Backups to S3 only (not local storage)
- Clean temp files weekly

---

#### Error 4.3: SSL Certificate Expired

**Error Message:**
```
Browser:
Your connection is not private
NET::ERR_CERT_DATE_INVALID

curl https://erp.tsh.sale:
curl: (60) SSL certificate problem: certificate has expired
```

**Root Cause:**
- Let's Encrypt certificate expired (every 90 days)
- Automatic renewal failed (certbot not running)
- VPS was down during renewal window
- Domain DNS issue preventing renewal

**Solution:**
```bash
# Step 1: Check certificate expiry
ssh root@167.71.39.50
certbot certificates
# Look for "INVALID: Expired"

# Step 2: Renew certificate manually
certbot renew --force-renewal

# Step 3: Reload nginx
systemctl reload nginx

# Step 4: Verify renewal
echo | openssl s_client -connect erp.tsh.sale:443 2>/dev/null | openssl x509 -noout -dates
# Should show:
# notBefore=...
# notAfter=... (90 days from now)

# Step 5: Test in browser
curl https://erp.tsh.sale/health
# Should work without SSL error
```

**Preventive Rule:**
- Setup automatic renewal (certbot timer enabled)
- Monitor certificate expiry (alert 30 days before)
- Test renewal monthly: `certbot renew --dry-run`

---

### Category 5: Performance Errors

#### Error 5.1: API Endpoint Timeout (> 30 seconds)

**Error Message:**
```
Frontend:
Error: timeout of 30000ms exceeded

Backend logs:
Request to /api/reports/sales started at 14:32:01
No completion logged (still running at 14:32:45)
```

**Root Cause:**
- Query too complex (multiple joins, no indexes)
- Fetching too much data (no pagination, loading all 2,218 products)
- CPU-intensive operation (complex calculation)
- External API call timeout (Zoho API)

**Solution:**
```python
# Diagnose: Check query performance
from sqlalchemy import text

# Log the actual SQL query
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Run EXPLAIN ANALYZE on slow query
result = db.execute(text("""
    EXPLAIN ANALYZE
    SELECT orders.*, clients.name, products.name
    FROM orders
    JOIN clients ON orders.client_id = clients.id
    JOIN order_items ON orders.id = order_items.order_id
    JOIN products ON order_items.product_id = products.id
    WHERE orders.created_at >= '2025-01-01'
"""))

# Look for:
# - Seq Scan (missing index)
# - High cost numbers (> 10000)
# - Long execution time (> 100ms)

# Fix strategies:
# 1. Add pagination
@router.get("/reports/sales")
def sales_report(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db)
):
    # Add pagination
    offset = (page - 1) * limit

    orders = db.query(Order).filter(
        Order.created_at >= start_date,
        Order.created_at <= end_date
    ).offset(offset).limit(limit).all()

    return {"items": orders, "page": page, "limit": limit}

# 2. Move to background job (if > 5 seconds)
from fastapi import BackgroundTasks

@router.post("/reports/sales/generate")
def generate_sales_report(
    start_date: date,
    end_date: date,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    # Queue report generation
    background_tasks.add_task(
        generate_report_task,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )

    return {"message": "Report generation started. You'll receive an email when ready."}

# 3. Add caching (for read-heavy reports)
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=100)
def get_daily_sales_cached(date_str: str):
    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    # ... expensive query ...
    return result

# Cache for 1 hour
CACHE_EXPIRY = timedelta(hours=1)
```

**Related Template:**
- PERFORMANCE_OPTIMIZATION.md → Section: API Optimization
- CODE_TEMPLATES.md → Template 2.2: List with Pagination

**Preventive Rule:**
- Operations > 5 seconds → Move to background job
- Reports > 10 seconds → Generate offline, email link
- ALWAYS paginate (max 100 for web, 50 for mobile)
- Add indexes on filter fields

---

### Category 6: Mobile App Errors

#### Error 6.1: Flutter App White Screen on Launch

**Error Message:**
```
Flutter console:
════════ Exception caught by widgets library ════════
The following assertion was thrown building MaterialApp:
```

**Root Cause:**
- Unhandled exception in app initialization
- Missing API endpoint (backend not deployed)
- Network connectivity issue
- Incompatible API response format (backend updated, app not)

**Solution:**
```dart
// Add error boundary in main.dart
void main() {
  // Catch Flutter framework errors
  FlutterError.onError = (FlutterErrorDetails details) {
    FlutterError.presentError(details);
    // Log to error tracking service (e.g., Sentry)
  };

  // Catch Dart errors outside Flutter framework
  runZonedGuarded(
    () => runApp(MyApp()),
    (error, stackTrace) {
      // Log to error tracking service
      print('Uncaught error: $error');
    },
  );
}

// Add error handling in API client
class ApiClient {
  Future<Product> getProduct(int id) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/products/$id'),
        headers: {'Authorization': 'Bearer $token'},
      );

      if (response.statusCode == 200) {
        return Product.fromJson(jsonDecode(response.body));
      } else if (response.statusCode == 404) {
        throw NotFoundException('Product not found');
      } else {
        throw ApiException('Server error: ${response.statusCode}');
      }

    } on SocketException {
      throw NetworkException('No internet connection');
    } on TimeoutException {
      throw NetworkException('Request timeout');
    } catch (e) {
      throw ApiException('Unknown error: $e');
    }
  }
}

// Show user-friendly error screen
class ErrorScreen extends StatelessWidget {
  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 64, color: Colors.red),
            SizedBox(height: 16),
            Text(message, style: TextStyle(fontSize: 18)),
            SizedBox(height: 24),
            ElevatedButton(
              onPressed: onRetry,
              child: Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }
}
```

**Related Template:**
- CODE_TEMPLATES.md → Template 6.2: Mobile-Optimized Response

**Preventive Rule:**
- Add global error boundary in Flutter app
- Show user-friendly error messages (not stack traces)
- Implement retry logic for network errors
- Version API responses (detect incompatible changes)

---

### Category 7: Arabic & RTL Errors

#### Error 7.1: Arabic Text Rendering Incorrectly (LTR instead of RTL)

**Error Message:**
```
Visual issue:
Expected: "منتجات المكتب" (right-to-left)
Actual: "بتكملا تاجتنم" (reversed, left-to-right)
```

**Root Cause:**
- Missing `dir="rtl"` attribute on HTML element
- CSS not configured for RTL
- Unicode bidi controls missing
- Font doesn't support Arabic properly

**Solution:**
```html
<!-- Frontend: Add RTL support (React) -->
<html dir="rtl" lang="ar">
<head>
  <meta charset="UTF-8">
  <style>
    /* RTL-specific styles */
    body[dir="rtl"] {
      direction: rtl;
      text-align: right;
    }

    /* Override specific elements that should stay LTR */
    .ltr {
      direction: ltr;
      text-align: left;
    }
  </style>
</head>
<body>
  <div className="product-name">{product.name_ar}</div>
  <div className="product-sku ltr">{product.sku}</div> <!-- SKUs stay LTR -->
</body>
</html>
```

```dart
// Flutter: Add RTL support
MaterialApp(
  // Set app direction based on locale
  localizationsDelegates: [
    GlobalMaterialLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
  ],
  supportedLocales: [
    Locale('en', 'US'),
    Locale('ar', 'IQ'),
  ],

  // Build app with RTL support
  builder: (context, child) {
    return Directionality(
      textDirection: TextDirection.rtl,  // Force RTL
      child: child!,
    );
  },

  home: HomePage(),
)

// Text widget with Arabic
Text(
  product.nameAr,
  textDirection: TextDirection.rtl,
  textAlign: TextAlign.right,
  style: TextStyle(
    fontFamily: 'Cairo',  // Arabic-friendly font
  ),
)
```

**Related Template:**
- ARCHITECTURE_RULES.md → Section: Arabic & RTL Implementation
- CODE_TEMPLATES.md → Template 4.2: RTL Layout Component

**Preventive Rule:**
- ALWAYS set `dir="rtl"` for Arabic content
- Use Arabic-friendly fonts (Cairo, Amiri, Tajawal)
- Test with real Arabic text (not Lorem Ipsum)
- Keep codes/SKUs LTR (use `.ltr` class)

---

### Error Pattern Quick Reference Table

| Error Code | Category | Quick Solution | Reference |
|------------|----------|----------------|-----------|
| ERR-DB-001 | Connection pool exhausted | Kill idle connections, increase pool_size | Error 1.1 |
| ERR-DB-002 | N+1 queries | Add joinedload/selectinload | Error 1.2 |
| ERR-DB-003 | Deadlock | Use SELECT FOR UPDATE | Error 1.3 |
| ERR-DB-004 | Missing index | CREATE INDEX on queried columns | Error 1.4 |
| ERR-DB-005 | Foreign key violation | Validate existence before insert | Error 1.5 |
| ERR-ZOHO-001 | 401 Unauthorized | Refresh access token | Error 2.1 |
| ERR-ZOHO-002 | 429 Rate limit | Reduce sync frequency, batch requests | Error 2.2 |
| ERR-ZOHO-003 | Data mismatch | Force sync, update from Zoho | Error 2.3 |
| ERR-API-001 | Pydantic validation | Add missing field to request | Error 3.1 |
| ERR-API-002 | JWT expired | Refresh token or re-login | Error 3.2 |
| ERR-API-003 | CORS error | Add origin to allowed_origins | Error 3.3 |
| ERR-API-004 | 500 error | Add null checks, error handling | Error 3.4 |
| ERR-DEPLOY-001 | Tests failed | Fix test or code, re-run locally | Error 4.1 |
| ERR-DEPLOY-002 | Disk full | Clean logs, setup rotation | Error 4.2 |
| ERR-DEPLOY-003 | SSL expired | Renew certificate manually | Error 4.3 |
| ERR-PERF-001 | API timeout | Add pagination, move to background | Error 5.1 |
| ERR-MOBILE-001 | White screen | Add error boundary, check API | Error 6.1 |
| ERR-ARABIC-001 | RTL rendering | Add dir="rtl", use Arabic fonts | Error 7.1 |

---

## 🔍 How to Use This Knowledge Base

### When You Encounter an Error:

**Step 1: Search by Error Message**
- Copy exact error message
- Search this file for error message keywords
- Example: Search for "ForeignKeyViolation" → finds Error 1.5

**Step 2: Read Error Pattern**
- Understand root cause (WHY it happened)
- Review solution steps
- Check related templates for code examples

**Step 3: Apply Solution**
- Follow solution steps systematically
- Test fix in staging first
- Verify recovery completely

**Step 4: Document New Patterns**
- If error not in this knowledge base, add it
- Follow same format: Error → Root Cause → Solution → Template → Prevention

### When Implementing New Features:

**Review Preventive Rules**
- Before coding, check preventive rules for similar errors
- Example: Adding new list endpoint → Review ERR-PERF-001 prevention (pagination)
- Proactively implement preventions (cheaper than fixing later)

---

## ✅ Failsafe Protocol Success Metrics

**I'm handling failures well when:**
- ✅ I don't panic or make things worse
- ✅ I alert Khaleel for critical issues immediately
- ✅ I diagnose root cause before attempting fixes
- ✅ I test fixes in staging when possible
- ✅ I have rollback ready before deploying fixes
- ✅ I verify recovery thoroughly
- ✅ I document new failure patterns
- ✅ Systems recover quickly and completely

**I need to improve when:**
- ❌ I make random changes hoping something works
- ❌ I deploy untested "fixes" to production
- ❌ I don't alert Khaleel for critical issues
- ❌ I fix symptoms without finding root cause
- ❌ I don't have rollback plan
- ❌ I don't verify recovery thoroughly
- ❌ Same failure happens repeatedly

---

**END OF FAILSAFE_PROTOCOL.md**

*When systems fail, follow this protocol. Stability and data integrity first. Always.*
