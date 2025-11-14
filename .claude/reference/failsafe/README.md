# Failsafe Protocol - System Failure Recovery

**Purpose:** Emergency response procedures for system failures and degraded conditions
**Last Updated:** 2025-11-14
**Load via:** @docs/reference/failsafe/[scenario].md

---

## 🚨 When to Use This

**Load failsafe protocols when:**
- Production system is down or degraded
- Data corruption detected
- Critical services failing
- Emergency recovery needed
- Diagnosing system failures

**DON'T load when:**
- Everything is working normally
- Implementing new features
- Regular development work

---

## 📂 Protocol Structure

### 🎯 Core Response Framework
**File:** `response-framework.md`
**Load:** `@docs/reference/failsafe/response-framework.md`

**Contains:**
- Core failsafe principles
- Immediate response checklist
- When to alert user
- Evidence gathering steps
- Damage containment strategies

**When to Load:**
- ANY system failure occurs
- Before diagnosing issues
- Emergency situation

---

### 🔴 Critical Failure Scenarios

**Directory:** `critical-scenarios/`

Each scenario includes:
- Symptoms and detection
- Immediate response steps
- Diagnostic procedures
- Fix implementation
- Verification steps
- Prevention measures

#### Database Failures
**File:** `critical-scenarios/database-failures.md`
**Load:** `@docs/reference/failsafe/critical-scenarios/database-failures.md`

**Covers:**
- PostgreSQL connection failures
- Connection pool exhausted
- Database server down
- Query timeouts
- Transaction deadlocks

**When to Load:**
- Database connection errors
- "remaining connection slots" errors
- Database performance issues

---

#### Deployment Failures
**File:** `critical-scenarios/deployment-failures.md`
**Load:** `@docs/reference/failsafe/critical-scenarios/deployment-failures.md`

**Covers:**
- GitHub Actions deployment failures
- Docker build failures
- Service startup failures
- Rollback procedures

**When to Load:**
- Deployment workflow fails
- Production deployment issues
- Service won't start after deployment

---

#### Zoho Sync Failures
**File:** `critical-scenarios/zoho-sync-failures.md`
**Load:** `@docs/reference/failsafe/critical-scenarios/zoho-sync-failures.md`

**Covers:**
- TDS Core sync stopped
- Zoho API errors
- Token expiration
- Data sync delays

**When to Load:**
- Zoho sync not running
- TDS Core dashboard shows errors
- Product/order sync delayed

---

#### API Errors (500s)
**File:** `critical-scenarios/api-errors.md`
**Load:** `@docs/reference/failsafe/critical-scenarios/api-errors.md`

**Covers:**
- Production API returning 500 errors
- Unhandled exceptions
- Service crashes
- Memory issues

**When to Load:**
- API endpoints returning 500
- Multiple users reporting errors
- Service crashes

---

#### Data Corruption
**File:** `critical-scenarios/data-corruption.md`
**Load:** `@docs/reference/failsafe/critical-scenarios/data-corruption.md`

**Covers:**
- Detecting data corruption
- Stopping data loss
- Restore procedures
- Data validation

**When to Load:**
- Incorrect data reported
- Data integrity issues
- Suspected corruption

---

#### Performance Issues
**File:** `critical-scenarios/performance-issues.md`
**Load:** `@docs/reference/failsafe/critical-scenarios/performance-issues.md`

**Covers:**
- Slow endpoints (> 5 seconds)
- Query optimization
- Performance degradation
- Resource exhaustion

**When to Load:**
- Endpoints timing out
- Slow response times
- Performance complaints

---

#### Frontend Issues
**File:** `critical-scenarios/frontend-issues.md`
**Load:** `@docs/reference/failsafe/critical-scenarios/frontend-issues.md`

**Covers:**
- React/Flutter not rendering
- White screen errors
- Component failures
- API integration issues

**When to Load:**
- Frontend not loading
- Components broken
- UI rendering issues

---

### 🟡 Non-Critical Scenarios

**File:** `non-critical-scenarios.md`
**Load:** `@docs/reference/failsafe/non-critical-scenarios.md`

**Contains:**
- Single user errors
- Minor service degradation
- Temporary glitches
- Non-urgent issues

**When to Load:**
- Issues affecting < 5% of users
- Non-blocking problems
- Informational errors

---

### 🛡️ Safe-Mode Operations

**File:** `safe-mode-operations.md`
**Load:** `@docs/reference/failsafe/safe-mode-operations.md`

**Contains:**
- What you CAN do during failures
- What you CANNOT do
- Read-only access patterns
- Emergency overrides

**When to Load:**
- During active incident
- When making emergency changes
- Before risky operations

---

### 🔄 Recovery Procedures

**File:** `recovery-procedures.md`
**Load:** `@docs/reference/failsafe/recovery-procedures.md`

**Contains:**
- Recovery verification checklist
- Backup procedures
- Restore procedures
- Post-recovery validation

**When to Load:**
- After fixing issues
- Before declaring incident resolved
- Planning backup/restore

---

### 🚨 Emergency Resources

**File:** `emergency-contacts.md`
**Load:** `@docs/reference/failsafe/emergency-contacts.md`

**Contains:**
- Server access information
- Database credentials location
- Health check URLs
- Emergency commands

**When to Load:**
- Need server access
- Need credentials
- Emergency operations

---

### 📚 Failure Pattern Knowledge Base

**File:** `failure-patterns.md`
**Load:** `@docs/reference/failsafe/failure-patterns.md`

**Contains:**
- Common error patterns
- Historical failures
- Root causes database
- Solutions that worked

**When to Load:**
- Diagnosing unknown issues
- Similar errors seen before
- Learning from past incidents

---

## 🎯 Quick Decision Tree

```
Is production down?
├─ YES → Load response-framework.md
│         Then load relevant critical scenario
│
└─ NO → Is data at risk?
    ├─ YES → Load data-corruption.md
    │
    └─ NO → Is it affecting users?
        ├─ YES → Load relevant critical scenario
        │
        └─ NO → Load non-critical-scenarios.md
```

---

## 🚨 Emergency Quick Reference

### Production Down
```bash
1. Load: response-framework.md
2. Check: curl https://erp.tsh.sale/health
3. Check: gh run list --limit 3
4. Load appropriate scenario from critical-scenarios/
```

### Database Issues
```bash
1. Load: critical-scenarios/database-failures.md
2. Check: PGPASSWORD='...' psql -h localhost -c "SELECT 1;"
3. Follow scenario diagnostic steps
```

### Zoho Sync Issues
```bash
1. Load: critical-scenarios/zoho-sync-failures.md
2. Check: https://tds.tsh.sale (TDS Core dashboard)
3. Check logs: tail -100 /var/www/tds-core/logs/tds_core.log
4. Follow scenario recovery steps
```

---

## ⚡ Core Principles

**When ANY failure occurs:**

```yaml
1. STOP & ASSESS (Don't panic)
2. ALERT USER if critical
3. GATHER EVIDENCE (logs, errors)
4. CONTAIN DAMAGE (prevent worse)
5. DIAGNOSE ROOT CAUSE
6. IMPLEMENT FIX (safely)
7. VERIFY RECOVERY
8. DOCUMENT INCIDENT
```

**Never:**
- Make random changes hoping it works
- Deploy fixes without testing
- Ignore errors hoping they resolve
- Bypass safety mechanisms
- Make irreversible data changes

**Always:**
- Test fixes in staging first (when possible)
- Have rollback plan ready
- Document what you do
- Verify recovery completely

---

## 📊 Severity Levels

```yaml
🔴 CRITICAL (Load immediately):
- Production completely down
- Data corruption
- Security breach
- Financial transaction failures

🟠 HIGH (Load within 15 minutes):
- Partial service outage
- Zoho sync stopped
- Major performance degradation

🟡 MEDIUM (Load within 1 hour):
- Single endpoint failing
- Minor performance issues
- Non-critical service down

🟢 LOW (Can wait):
- Single user issues
- Cosmetic problems
- Optional features broken
```

---

## 🎓 Using Failsafe Protocols

### During Active Incident

1. **Load Core Framework First**
   ```
   @docs/reference/failsafe/response-framework.md
   ```

2. **Identify Scenario**
   - Match symptoms to scenario
   - Load specific scenario file

3. **Follow Steps Exactly**
   - Don't skip steps
   - Document actions taken
   - Verify each step

4. **Recovery Verification**
   ```
   @docs/reference/failsafe/recovery-procedures.md
   ```

### After Incident

1. **Document lessons learned**
2. **Update failure-patterns.md** if new pattern
3. **Implement prevention measures**
4. **Update monitoring/alerts**

---

## ✅ Success Metrics

**Good Failure Response:**
```yaml
✅ Incident contained quickly (< 30 minutes)
✅ Root cause identified correctly
✅ Fix implemented safely
✅ No additional damage caused
✅ Full recovery verified
✅ Prevention measures added
✅ User kept informed
```

**Poor Failure Response:**
```yaml
❌ Panic and random changes
❌ Made situation worse
❌ Deployed untested fixes
❌ Caused data loss
❌ Forgot to verify recovery
❌ Repeated same mistake
```

---

**Related Documentation:**
- Core workflows: @docs/core/workflows.md
- Deployment guide: @docs/DEPLOYMENT_GUIDE.md
- Security patterns: @docs/core/architecture.md
- TDS Core: @docs/TDS_MASTER_ARCHITECTURE.md
