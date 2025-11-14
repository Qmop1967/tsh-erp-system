# Failsafe Response Framework

**Purpose:** Core principles and immediate response procedures for ALL system failures
**Last Updated:** 2025-11-14
**Load via:** @docs/reference/failsafe/response-framework.md

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

## 🚨 Immediate Response Checklist

**When ANY failure occurs, follow this exact sequence:**

### 1. STOP & ASSESS (Don't Act Immediately)

```yaml
Questions to Answer:
□ What exactly failed? (specific component)
□ Is this affecting users right now? (production down?)
□ Is data at risk? (corruption, loss)
□ What's the blast radius? (how many users affected)
□ When did it start? (check logs for timestamp)
```

**PAUSE before taking action. Rushing makes things worse.**

---

### 2. ALERT USER (If Critical)

```yaml
Alert IMMEDIATELY if:
□ Production system completely down
□ Data corruption detected
□ Security breach suspected
□ Financial transaction failures
□ Zoho sync completely broken (no data for hours)
□ Revenue-impacting outage

Say:
"🚨 CRITICAL: [Component] is down. [Impact]. I'm investigating and will provide updates every 15 minutes."

Don't Say:
"There might be an issue..." (too vague)
"I'm not sure what's happening..." (unprofessional)
```

---

### 3. GATHER EVIDENCE (Don't Guess)

```yaml
Collect Information:
□ Exact error messages (copy full text)
□ Timestamps (when did it start?)
□ Affected components (what's failing?)
□ Recent changes (deployments, config changes)
□ System status (CPU, memory, disk)
□ Log files (backend, TDS Core, database)

Commands to Run:
# Check system health
curl https://erp.tsh.sale/health
curl https://tds.tsh.sale/api/health

# Check recent deployments
gh run list --limit 5

# Check logs
tail -100 /var/www/tsh-erp/logs/backend.log
tail -100 /var/www/tds-core/logs/tds_core.log

# Check database
PGPASSWORD='TSH@2025Secure!Production' psql -h localhost \
  -U tsh_app_user -d tsh_erp_production -c "SELECT COUNT(*) FROM products;"
```

---

### 4. CONTAIN DAMAGE (If Possible)

```yaml
Prevent Worse Damage:
□ Stop failing process (if causing cascading failures)
□ Switch to degraded mode (if available)
□ Prevent data corruption (stop writes if risky)
□ Isolate affected component
□ Rate limit if overload

Examples:
- If API endpoint causing crashes → Disable endpoint temporarily
- If background job failing → Pause job scheduler
- If database writes corrupting data → Enable read-only mode
- If deployment failed → Rollback immediately
```

---

### 5. DIAGNOSE ROOT CAUSE

```yaml
Use Systematic Approach:
□ What changed recently? (deployments, config, data)
□ What do logs say? (exact error messages)
□ Can you reproduce? (in staging/locally)
□ What's the pattern? (intermittent vs consistent)

Apply Root-Cause Analysis:
1. State the problem clearly
2. List possible causes
3. Test each hypothesis
4. Identify true root cause
5. Don't fix symptoms, fix root cause

Reference: @docs/reference/reasoning-patterns.md
```

---

### 6. IMPLEMENT FIX (Safely)

```yaml
Safe Fix Implementation:
□ Test fix in staging first (if time permits)
□ Apply minimal change needed
□ Have rollback plan ready
□ Document what you're changing
□ Monitor closely after fix
□ One change at a time (don't batch fixes)

If Emergency (Production Down):
- May skip staging if critical
- But MUST document what you do
- And MUST be able to rollback
- Alert user before applying fix
```

---

### 7. VERIFY RECOVERY

```yaml
Verification Checklist:
□ Core functionality works (test critical paths)
□ No new errors in logs
□ Performance normal (response times)
□ All services running
□ Zoho sync operating (if relevant)
□ Users can access system

Load Full Verification:
@docs/reference/failsafe/recovery-procedures.md
```

---

### 8. DOCUMENT INCIDENT

```yaml
Record:
□ What failed (symptoms, impact)
□ Root cause (actual problem)
□ Fix applied (exact changes)
□ Verification (how you confirmed recovery)
□ Prevention (how to avoid in future)
□ Duration (start to resolution)

Update Knowledge Base:
@docs/reference/failsafe/failure-patterns.md
```

---

## 🔴 Severity Assessment Matrix

### CRITICAL (Act Immediately)

```yaml
Indicators:
- Production completely inaccessible
- All users affected
- Data corruption in progress
- Security breach active
- Revenue-impacting failure

Response Time: < 15 minutes
Alert User: Immediately
Max Resolution Time: 2 hours
```

### HIGH (Act Within 15 Minutes)

```yaml
Indicators:
- Partial service outage
- 20%+ users affected
- Zoho sync stopped
- Major performance degradation
- Critical feature broken

Response Time: < 15 minutes
Alert User: Yes
Max Resolution Time: 4 hours
```

### MEDIUM (Act Within 1 Hour)

```yaml
Indicators:
- Single endpoint failing
- < 5% users affected
- Minor performance issues
- Non-critical service down
- Workaround available

Response Time: < 1 hour
Alert User: If noticed
Max Resolution Time: 1 business day
```

### LOW (Can Wait)

```yaml
Indicators:
- Single user issue
- Cosmetic problem
- Optional feature broken
- No user impact

Response Time: < 1 business day
Alert User: Only if asks
Max Resolution Time: 1 week
```

---

## 🛡️ What You CAN Do During Failures

```yaml
✅ SAFE OPERATIONS (Always Allowed):
- Read logs
- Query database (SELECT only)
- Check system status
- Restart services
- Rollback deployments
- Enable maintenance mode
- Disable failing components
- Scale resources (if needed)
- Contact user for guidance

✅ CONDITIONAL (If Necessary):
- Modify configuration
- Apply emergency patches
- Database writes (if safe)
- Schema changes (if critical)

⚠️ ASK FIRST:
- Permanent data deletion
- Schema changes (unless critical)
- Major architectural changes
- Anything irreversible
```

---

## ❌ What You CANNOT Do During Failures

```yaml
❌ NEVER DO:
- Panic and make random changes
- Deploy untested code to production
- Bypass security mechanisms
- Delete data without backup
- Make multiple changes at once
- Ignore errors hoping they resolve
- Skip verification steps
- Forget to alert user
- Blame external services without proof
- Give up and suggest "reinstall everything"
```

---

## 📋 Emergency Command Reference

### System Health Checks

```bash
# Production API health
curl https://erp.tsh.sale/health

# Staging API health
curl https://staging.erp.tsh.sale/health

# TDS Core health
curl https://tds.tsh.sale/api/health

# Database check
PGPASSWORD='TSH@2025Secure!Production' psql -h localhost \
  -U tsh_app_user -d tsh_erp_production \
  -c "SELECT COUNT(*) FROM products WHERE is_active = true;"
```

### Service Management

```bash
# SSH to production
ssh root@167.71.39.50

# Check service status
systemctl status tsh-erp
systemctl status tds-core
systemctl status postgresql
systemctl status nginx

# Restart services
systemctl restart tsh-erp
systemctl restart tds-core

# View logs
journalctl -u tsh-erp -n 100 -f
journalctl -u tds-core -n 100 -f
```

### Deployment Checks

```bash
# Recent GitHub Actions
gh run list --limit 5

# Watch current deployment
gh run watch <run-id>

# View failed workflow
gh run view <run-id> --log-failed
```

---

## 🔄 Escalation Path

```
You (Claude Code)
    ↓ (If can't resolve in 30 minutes)
Alert User
    ↓ (If needs server access or critical decisions)
User Takes Over
    ↓ (If beyond user's expertise)
External Expert (if needed)
```

**Key Point:** Don't waste time trying impossible fixes. Escalate when needed.

---

## ✅ Response Success Indicators

**Good Response:**
```yaml
✅ Incident contained quickly (< 30 min)
✅ Root cause identified correctly
✅ Fix tested before applying
✅ No additional damage caused
✅ Full recovery verified
✅ User kept informed
✅ Documented for future
```

**Poor Response:**
```yaml
❌ Panic and random changes
❌ Made situation worse
❌ Deployed untested fixes
❌ Caused data loss
❌ Forgot to verify
❌ User found out from customers
❌ Repeated same mistake
```

---

## 🎓 After Incident Resolution

```yaml
Post-Incident Actions:
1. Verify complete recovery
2. Document incident thoroughly
3. Update failure patterns knowledge base
4. Identify prevention measures
5. Implement monitoring/alerts (if missing)
6. Update relevant documentation
7. Share lessons learned

Don't Forget:
- What went well
- What went wrong
- What to improve
- How to prevent
```

---

**Related Documentation:**
- Critical scenarios: @docs/reference/failsafe/critical-scenarios/
- Recovery procedures: @docs/reference/failsafe/recovery-procedures.md
- Failure patterns: @docs/reference/failsafe/failure-patterns.md
- Emergency contacts: @docs/reference/failsafe/emergency-contacts.md
