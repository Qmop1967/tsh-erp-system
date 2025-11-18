# Quick Reference - 60-Second TSH ERP Context

**Purpose:** Ultra-fast information lookup for session start and rapid orientation.

**Last Updated:** 2025-11-17

---

## TEMPORARY DEVELOPMENT MODE - ACTIVE

**CRITICAL NOTICE: Direct Docker Deployment - GitHub CI/CD DISABLED**

```yaml
Status: TEMPORARY DEVELOPMENT MODE
Activated: 2025-11-17
Deployment: Direct Docker commands (NO GitHub Actions)
Database: READ-ONLY production database
Staging: DISABLED
Full Details: TEMPORARY_DEVELOPMENT_MODE.md

Quick Deploy:
  ssh root@167.71.39.50
  cd /var/www/tsh-erp && docker-compose up -d --build

Re-enablement: Only on explicit instruction from Khaleel
```

---

## ⚡ 30-Second Project Overview

```yaml
Project: TSH ERP Ecosystem
Purpose: Import-distribution-retail ERP for Iraq market
Mode: TEMPORARY DEVELOPMENT MODE (Direct Docker Deployment)
Phase: Zoho Migration Phase 1 (read-only from Books + Inventory)

Current Scale:
  Users: 500+ wholesale clients, 100+ salesmen, 12 travel sales ($35K USD/week)
  Data: 2,218+ products, 30+ daily orders, 57 database tables (127 MB)

Tech Stack:
  Backend: FastAPI + Python 3.9+ + PostgreSQL 12+
  Frontend: React 18 (ERP Admin) + Flutter Web (Consumer)
  Mobile: Flutter 3.0+ (8 apps)
  Deployment: DIRECT DOCKER (GitHub Actions DISABLED)
  Backup: AWS S3 (tsh-erp-backups, eu-north-1)
  Sync: TDS Core orchestrates ALL Zoho operations

🚨 CURRENT DEPLOYMENT MODE:
  Development Server: 167.71.39.50 (Direct Docker Deployment)
  Staging: DISABLED (Temporary Mode)
  GitHub Actions: DISABLED (Temporary Mode)
  Database: READ-ONLY production database

Critical Rules:
  ❌ NEVER: Use GitHub Actions, deploy to staging, trigger CI/CD pipelines
  ❌ NEVER: Bypass TDS Core, forget Arabic, deploy partial
  ✅ ALWAYS: Deploy via Docker commands, use read-only database
  ✅ ALWAYS: Paginate > 100, authenticate ops, use Pydantic
```

---

## 🚫 NEVER Do This

```yaml
TEMPORARY MODE VIOLATIONS (CRITICAL):
❌ Enable or trigger GitHub Actions workflows
❌ Deploy to staging environment (DISABLED)
❌ Create PRs expecting automated deployment
❌ Use gh run or GitHub CI/CD commands
❌ Write to the database (READ-ONLY ENFORCED)

Architecture Violations:
❌ Access Zoho Books/Inventory APIs directly (MUST use TDS Core)
❌ Write to Zoho in Phase 1 (read-only)
❌ Deploy backend without frontend (deploy ALL components)
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
✅ Deploy ALL components together via Docker
✅ Use read-only database connection

Deployment (TEMPORARY MODE):
✅ SSH to development server (ssh root@167.71.39.50)
✅ Pull latest code (git pull origin develop)
✅ Build Docker containers (docker-compose build)
✅ Restart services (docker-compose up -d)
✅ Verify health (curl http://localhost:8000/health)
✅ Check logs (docker-compose logs -f)
❌ DO NOT use GitHub Actions or staging
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

## 📋 10 Most Common Commands (TEMPORARY MODE)

### Git Operations
```bash
# 1. Check status
git status

# 2. Check current branch
git branch

# 3. Recent commits
git log --oneline -5

# 4. Push to develop (version control only, NO CI/CD)
git push origin develop
```

### Docker Deployment (TEMPORARY MODE)
```bash
# 5. SSH to development server
ssh root@167.71.39.50

# 6. Deploy all services
cd /var/www/tsh-erp && docker-compose up -d --build

# 7. Restart specific service
docker-compose restart backend

# 8. Check container status
docker ps
```

### Verification (TEMPORARY MODE)
```bash
# 9. Check health (on server)
curl http://localhost:8000/health

# 10. View logs
docker-compose logs -f backend
```

### Debugging
```bash
# Database connectivity
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

## 🔗 Key URLs (TEMPORARY MODE)

```yaml
Development Server (Direct Docker):
  Server: 167.71.39.50
  User: root
  Deployment: Direct Docker commands
  Database: READ-ONLY production database

Local URLs (on server):
  Backend: http://localhost:8000
  TDS Core: http://localhost:8001
  BFF: http://localhost:8002

Staging (DISABLED):
  Status: SUSPENDED - Temporary Mode
  Server: 167.71.58.65 (NOT IN USE)

External:
  GitHub: https://github.com/Qmop1967/tsh-erp-system
  Zoho Books: https://books.zoho.com/app#/home/dashboard/748369814
  Zoho Inventory: https://inventory.zoho.com/app#/home/748369814

GitHub Actions: DISABLED (Temporary Mode)
CI/CD Pipelines: DISABLED (Temporary Mode)
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

### Deploy (TEMPORARY MODE)
```yaml
1. SSH to server: ssh root@167.71.39.50
2. Pull latest: cd /var/www/tsh-erp && git pull origin develop
3. Build containers: docker-compose build --no-cache
4. Restart services: docker-compose up -d
5. Verify health: curl http://localhost:8000/health
6. Check logs: docker-compose logs -f --tail=100
7. Monitor for issues
Note: NO GitHub Actions, NO staging (DISABLED)
```

---

## 🚨 Emergency Contacts & Quick Actions

### Service Down (TEMPORARY MODE)
```yaml
1. SSH to server: ssh root@167.71.39.50
2. Check containers: docker ps
3. Check logs: docker-compose logs --tail=100
4. Restart services: docker-compose restart
5. Rebuild if needed: docker-compose up -d --build
6. Verify health: curl http://localhost:8000/health
7. Follow FAILSAFE_PROTOCOL.md
```

### Zoho Sync Stopped (TEMPORARY MODE)
```yaml
1. Check TDS Core logs: docker-compose logs tds-core
2. Restart TDS Core: docker-compose restart tds-core
3. Check token expiration (refresh if needed)
4. Monitor sync status in logs
5. Verify database connectivity
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
