# Quick Reference - 60-Second TSH ERP Context

**Purpose:** Ultra-fast information lookup for session start and rapid orientation.

**Last Updated:** 2025-11-12

---

## ⚡ 30-Second Project Overview

```yaml
Project: TSH ERP Ecosystem
Purpose: Import-distribution-retail ERP for Iraq market
Mode: Development (deploy anytime to staging/production)
Phase: Zoho Migration Phase 1 (read-only from Books + Inventory)

Current Scale:
  Users: 500+ wholesale clients, 100+ salesmen, 12 travel sales ($35K USD/week)
  Data: 2,218+ products, 30+ daily orders, 57 database tables (127 MB)

Tech Stack:
  Backend: FastAPI + Python 3.9+ + PostgreSQL 12+
  Frontend: React 18 (ERP Admin) + Flutter Web (Consumer)
  Mobile: Flutter 3.0+ (8 apps)
  Deployment: GitHub Actions → TWO SERVERS (see below)
  Backup: AWS S3 (tsh-erp-backups, eu-north-1)
  Sync: TDS Core orchestrates ALL Zoho operations

🚨 CRITICAL SERVERS (DON'T MIX THEM UP!):
  Staging:    167.71.58.65 (user: khaleel, develop branch)
  Production: 167.71.39.50 (user: root, main branch)
  📖 Full Details: SERVER_INFRASTRUCTURE.md

Critical Rules:
  ❌ NEVER: Bypass TDS Core, forget Arabic, deploy partial, skip staging
  ✅ ALWAYS: Paginate > 100, authenticate ops, use Pydantic, test first
```

---

## 🚫 NEVER Do This

```yaml
Architecture Violations:
❌ Access Zoho Books/Inventory APIs directly (MUST use TDS Core)
❌ Write to Zoho in Phase 1 (read-only)
❌ Deploy backend without frontend (deploy ALL components)
❌ Push directly to main (push to develop first)
❌ Suggest changing tech stack (FastAPI/Flutter/PostgreSQL fixed)

Data Integrity Violations:
❌ Forget Arabic fields (name_ar, description_ar mandatory)
❌ Skip input validation (always use Pydantic)
❌ Bypass authentication (require get_current_user)
❌ Ignore RBAC (check roles for sensitive ops)
❌ Hardcode credentials (use environment variables)

Performance Violations:
❌ Return > 100 records without pagination
❌ Query without indexes on large tables
❌ Create N+1 query patterns (use joinedload)
❌ Skip staging verification
```

---

## ✅ ALWAYS Do This

```yaml
Code Quality:
✅ Search existing code before creating new
✅ Include Arabic fields (name_ar, description_ar) on user-facing models
✅ Paginate lists (max 100 per page)
✅ Add indexes on foreign keys and search fields
✅ Use parameterized queries (prevent SQL injection)
✅ Add error handling (try/except)
✅ Write docstrings for functions

Architecture:
✅ Go through TDS Core for ALL Zoho operations
✅ Authenticate sensitive endpoints (Depends(get_current_user))
✅ Authorize admin ops (require_role(["admin"]))
✅ Validate input (Pydantic schemas)
✅ Deploy ALL components together
✅ Test on staging before production

Deployment:
✅ Push to develop branch (staging)
✅ Monitor GitHub Actions
✅ Verify staging URLs work
✅ Get Khaleel approval
✅ Create PR (develop → main)
✅ Monitor production deployment
```

---

## 🎯 Decision Trees (Visual)

### Should I Create New Code or Enhance Existing?

```
Start
  │
  ├─→ Search existing code (grep, find)
  │     │
  │     ├─→ Found similar?
  │     │     │
  │     │     ├─→ YES → Enhance existing ✅
  │     │     │
  │     │     └─→ NO  → Create new ✅
  │     │
  │     └─→ Not sure → Use Task tool with Explore agent
```

### Should I Optimize This?

```
Start
  │
  ├─→ Is it slow? (> 2 seconds)
  │     │
  │     ├─→ NO → Don't optimize (premature) ❌
  │     │
  │     └─→ YES → Does it affect many users?
  │             │
  │             ├─→ NO → Low priority (defer) ⏸️
  │             │
  │             └─→ YES → Optimize now ✅
  │                     │
  │                     └─→ Measure → Optimize → Verify
```

### Should I Ask Khaleel?

```
Start
  │
  ├─→ Is this business logic?
  │     │
  │     ├─→ YES → Ask Khaleel ✅
  │     │
  │     └─→ NO → Is there one clear technical solution?
  │             │
  │             ├─→ YES → Implement ✅
  │             │
  │             └─→ NO (multiple options) → Ask Khaleel ✅
```

---

## 📋 10 Most Common Commands

### Git Operations
```bash
# 1. Check status
git status

# 2. Check current branch
git branch

# 3. Recent commits
git log --oneline -5

# 4. Push to staging
git push origin develop

# 5. Create PR for production
gh pr create --base main --head develop
```

### Deployment
```bash
# 6. Monitor GitHub Actions
gh run list --limit 3
gh run watch <run-id>

# 7. Verify staging
curl https://staging.erp.tsh.sale/health

# 8. Verify production
curl https://erp.tsh.sale/health
```

### Debugging
```bash
# 9. Check backend logs (VPS)
ssh root@167.71.39.50 "tail -100 /var/www/tsh-erp/logs/backend.log"

# 10. Check database connectivity
PGPASSWORD='TSH@2025Secure!Production' psql -h localhost -U tsh_app_user -d tsh_erp_production -c "SELECT COUNT(*) FROM products WHERE is_active = true;"
```

---

## 🗺️ Directory Structure (Essential Paths)

```
TSH_ERP_Ecosystem/
│
├── .claude/                    ← AI context files (read first!)
│   ├── PROJECT_VISION.md       ← Business context (supreme authority)
│   ├── ARCHITECTURE_RULES.md   ← Technical constraints
│   ├── CODE_TEMPLATES.md       ← Reusable patterns
│   └── QUICK_REFERENCE.md      ← This file
│
├── app/                        ← FastAPI backend
│   ├── models/                 ← Database models (SQLAlchemy)
│   ├── routers/                ← API endpoints
│   ├── services/               ← Business logic
│   └── schemas/                ← Pydantic validation
│
├── apps/
│   ├── consumer/               ← Flutter Web (Consumer)
│   └── tds_dashboard/          ← TDS Core monitoring
│
├── mobile/                     ← 8 Flutter mobile apps
│
├── scripts/                    ← 82 utility scripts
│
├── database/                   ← Schema & migrations
│
└── .github/workflows/          ← CI/CD pipelines
```

---

## 🔗 Key URLs

```yaml
Production:
  ERP Admin: https://erp.tsh.sale
  Consumer: https://consumer.tsh.sale
  Shop: https://shop.tsh.sale
  TDS Dashboard: https://tds.tsh.sale

Staging:
  ERP Admin: https://staging.erp.tsh.sale
  Consumer: https://staging.consumer.tsh.sale
  TDS Dashboard: https://staging.tds.tsh.sale

External:
  GitHub: https://github.com/Qmop1967/tsh-erp-system
  Zoho Books: https://books.zoho.com/app#/home/dashboard/748369814
  Zoho Inventory: https://inventory.zoho.com/app#/home/748369814

VPS:
  IP: 167.71.39.50
  User: root
  Access: SSH key
```

---

## 📊 Scale Thresholds (When to Act)

```yaml
Pagination:
  > 100 records → MUST paginate

Indexing:
  > 1,000 rows → MUST index foreign keys and search fields

Background Jobs:
  > 5 seconds → Move to background job (Celery)

Caching:
  Read:Write > 10:1 → Consider caching

Response Time:
  > 500ms → Investigate (good = < 500ms)
  > 2s → Optimize immediately (unacceptable)
```

---

## 🎯 Common Task Quick Starts

### New Feature
```yaml
1. Read PROJECT_VISION.md & ARCHITECTURE_RULES.md
2. Search existing code (grep, find)
3. Ask clarifying questions if unclear
4. Create todo list if complex (3+ steps)
5. Implement with Arabic support
6. Test locally
7. Deploy to staging
8. Get approval
9. Deploy to production
```

### Bug Fix
```yaml
1. Reproduce bug (exact steps)
2. Check logs (backend, TDS Core)
3. Check recent commits (git log --since="3 days ago")
4. Apply Root-Cause Analysis (REASONING_PATTERNS.md)
5. Fix root cause (not symptom)
6. Test fix
7. Deploy to staging
8. Verify fix
9. Deploy to production
```

### Deploy to Production
```yaml
1. Verify ALL components ready
2. Push to develop (staging)
3. Test thoroughly on staging
4. Get Khaleel approval
5. Create PR (develop → main)
6. Monitor GitHub Actions
7. Verify production URLs
8. Monitor for issues
```

---

## 🚨 Emergency Contacts & Quick Actions

### Production Down
```yaml
1. Check VPS health: curl https://erp.tsh.sale/health
2. Check GitHub Actions: gh run list --limit 3
3. SSH to VPS: ssh root@167.71.39.50
4. Check service status: systemctl status tsh-erp
5. Check logs: journalctl -u tsh-erp -n 100
6. Alert Khaleel immediately
7. Follow FAILSAFE_PROTOCOL.md
```

### Zoho Sync Stopped
```yaml
1. Check TDS Dashboard: https://tds.tsh.sale
2. Check TDS Core logs: tail -100 /var/www/tds-core/logs/tds_core.log
3. Check token expiration (refresh if needed)
4. Restart TDS Core: systemctl restart tds-core
5. Monitor sync status
```

### Database Issues
```yaml
1. Check connections: SELECT count(*) FROM pg_stat_activity;
2. Check for locks: SELECT * FROM pg_locks WHERE NOT granted;
3. Restart PostgreSQL: systemctl restart postgresql
4. Alert Khaleel if data corruption suspected
```

---

## 💡 Success Indicators

```yaml
I'm working effectively when:
✅ I don't ask Khaleel to repeat context
✅ I search before creating new code
✅ I never forget Arabic fields
✅ I deploy all components together
✅ I test on staging first
✅ Features work correctly first time
✅ Khaleel feels productive working with me

Red flags (need improvement):
❌ Khaleel repeats same context
❌ I create duplicate functionality
❌ I forget Arabic fields
❌ I deploy partial components
❌ I skip staging testing
❌ Same bugs appear repeatedly
```

---

## 📚 Where to Find More Info

```yaml
Business Context: PROJECT_VISION.md (500 lines)
Technical Rules: ARCHITECTURE_RULES.md (600 lines)
How We Work: WORKING_TOGETHER.md (400 lines)
Session Start: SESSION_START.md (800 lines, includes health check)
Task Workflows: TASK_PATTERNS.md (1,100 lines)
Thinking Patterns: REASONING_PATTERNS.md (1,200 lines)
Error Recovery: FAILSAFE_PROTOCOL.md (800 lines)
Code Examples: CODE_TEMPLATES.md (2,500 lines)
Performance: PERFORMANCE_OPTIMIZATION.md (1,000 lines)
Full Index: KNOWLEDGE_PORTAL.md
```

---

## 🔄 Quick Context Refresh

**If I'm confused or lost:**

1. Re-read this QUICK_REFERENCE.md (2 minutes)
2. Check PROJECT_VISION.md for business context
3. Check ARCHITECTURE_RULES.md for technical rules
4. Check KNOWLEDGE_PORTAL.md for navigation
5. Ask Khaleel for clarification

**If Khaleel mentions phase transition:**

```
"We've moved to Phase 2" → Re-read PROJECT_VISION.md
"Now in production mode" → Re-read DEPLOYMENT_RULES.md
"Architecture changed" → Re-read ARCHITECTURE_RULES.md
```

---

**END OF QUICK_REFERENCE.MD**

*Scannable in < 60 seconds. Bookmark this for fast context loading.*
