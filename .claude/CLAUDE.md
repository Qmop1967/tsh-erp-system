# TSH ERP Ecosystem - Claude Code Context

**Version:** 3.0.0
**Last Updated:** 2025-11-14
**Schema Version:** 2.0.0
**Auto-loaded every session - Keep this file under 500 lines**

---

## 📌 Version History

```yaml
v3.0.0 (2025-11-14):
  - Added version tracking system
  - Enhanced dynamic state integration
  - Improved MCP configuration references
  - Added change log tracking

v2.1.0 (2025-11-13):
  - Updated deployment workflows
  - Enhanced authorization framework documentation
  - Improved performance thresholds

v2.0.0 (2025-11-12):
  - Restructured to core/reference architecture
  - Optimized for prompt caching (under 500 lines)
  - Added lazy loading with @docs/ references

v1.0.0 (2025-11-01):
  - Initial comprehensive context file

v3.1.0 (2025-11-17):
  - ACTIVATED TEMPORARY DEVELOPMENT MODE
  - Disabled GitHub CI/CD pipelines
  - Disabled Staging environment
  - Enabled direct Docker deployment
  - Real database connection (read-only)
```

---

## TEMPORARY DEVELOPMENT MODE - ACTIVE

**CRITICAL: The following changes are in effect until explicitly disabled by Khaleel:**

```yaml
Status: TEMPORARY DEVELOPMENT MODE ACTIVE
Activated: 2025-11-17
Full Details: @.claude/TEMPORARY_DEVELOPMENT_MODE.md

What's DISABLED:
  - GitHub Actions workflows (ALL)
  - Staging environment (167.71.58.65)
  - Automated CI/CD pipelines
  - PR-triggered deployments

What's ENABLED:
  - Direct Docker deployment on 167.71.39.50
  - Real database connection (READ-ONLY)
  - Fast local development
  - Direct container builds

Deployment Command:
  ssh root@167.71.39.50
  cd /var/www/tsh-erp && docker-compose up -d --build

Database: READ-ONLY (safe - all writes happen in Zoho only)
```

**This mode will remain active until Khaleel sends explicit re-enablement instruction.**

---

## 🎯 Core Facts (Cache-Friendly - Never Change)

```yaml
Project: TSH ERP Ecosystem
Purpose: Import-distribution-retail ERP for Iraq market
Company: TSH (Single tenant, not SaaS)
Status: Production system running real business

Tech Stack (IMMUTABLE):
  Backend: FastAPI + Python 3.9+ + PostgreSQL 12+ + SQLAlchemy
  Frontend: React 18 (ERP Admin) + Flutter Web (Consumer)
  Mobile: Flutter 3.0+ (8 specialized apps)
  Infrastructure: Docker + Nginx (GitHub Actions DISABLED - Temporary Mode)
  Backup: AWS S3 (tsh-erp-backups, eu-north-1)

Servers:
  Development: 167.71.39.50 (user: root, Direct Docker Deployment)
  Staging: 167.71.58.65 (DISABLED - Temporary Mode)

Deployment Mode: DIRECT DOCKER (GitHub CI/CD Disabled)

Current Phase: Zoho Migration Phase 1
  Status: Read-only sync from Zoho Books + Zoho Inventory
  Sync: TDS Core orchestrates ALL Zoho operations
  Write to Zoho: NO (Phase 1 restriction)

Scale (Remember Always):
  Clients: 500+ wholesale clients (30 orders/day)
  Products: 2,218+ active products
  Salesmen: 100+ partner salesmen, 12 travel sales ($35K USD/week)
  Database: 57 tables, 127 MB production data
  Mobile Apps: 8 Flutter applications

Languages: Arabic (PRIMARY) + English (secondary)
Currency: IQD (Iraqi Dinar)
RTL: Required for all UI
```

---

## 🚨 Authorization Framework (CRITICAL - NON-NEGOTIABLE)

**TSH ERP uses HYBRID AUTHORIZATION: RBAC + ABAC + RLS**

Every endpoint, service, and database query MUST implement ALL THREE layers:

```python
# ✅ CORRECT: All three layers present
@router.get("/orders")
async def get_orders(
    user: User = Depends(require_role([...])),           # RBAC Layer
    abac: User = Depends(check_abac_permission(...)),    # ABAC Layer
    db: Session = Depends(get_db)
):
    service = OrderService(db, user)  # RLS Layer
    return await service.get_orders()

# ❌ WRONG: Missing layers (Security Violation!)
@router.get("/orders")
async def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()  # Missing all 3 layers!
```

**Why This Matters:**
- Wholesale clients must ONLY see their own orders
- Travel salespersons must ONLY see assigned customers
- Inventory managers must ONLY see their warehouse
- Time-based access (retail staff during work hours only)
- Location-based access (warehouse restrictions)

**For Full Details:** @docs/AUTHORIZATION_FRAMEWORK.md

---

## ❌ NEVER Do This (Architecture Violations)

```yaml
Critical Violations (STOP IMMEDIATELY):
❌ Violate engineering standards (@docs/core/engineering-standards.md)
❌ Access Zoho Books/Inventory APIs directly (MUST use TDS Core)
❌ Write to Zoho in Phase 1 (read-only restriction)
❌ Deploy backend without frontend (ALL components together)
❌ Push directly to main branch (develop → staging first)
❌ Change tech stack (FastAPI/Flutter/PostgreSQL fixed)
❌ Bypass authentication (require get_current_user)
❌ Hardcode credentials (use environment variables)
❌ Skip Arabic fields (name_ar, description_ar mandatory)

Data Integrity Violations:
❌ Forget Arabic RTL support
❌ Skip input validation (always use Pydantic schemas)
❌ Ignore RBAC (check roles for sensitive operations)
❌ Return > 100 records without pagination
❌ Create N+1 query patterns (use joinedload)
❌ Query without indexes on large tables (2,218+ products)
❌ Skip staging verification before production
❌ Use Twilio or Firebase (TSH NeuroLink handles ALL communications)
```

---

## ✅ ALWAYS Do This (Best Practices)

```yaml
Code Quality:
✅ Search existing code before creating new (grep, find, Task tool)
✅ Include Arabic fields (name_ar, description_ar) on ALL user-facing models
✅ Paginate lists (max 100 per page for tables > 100 rows)
✅ Add indexes on foreign keys and search fields
✅ Use parameterized queries (prevent SQL injection)
✅ Add error handling (try/except with proper logging)
✅ Write docstrings for all functions
✅ Use Pydantic schemas for input validation

Architecture:
✅ Route ALL Zoho operations through TDS Core (app/tds/)
✅ Authenticate sensitive endpoints (Depends(get_current_user))
✅ Authorize admin operations (require_role(["admin", "manager"]))
✅ Implement all 3 authorization layers (RBAC + ABAC + RLS)
✅ Deploy ALL components together (backend + frontend + TDS)
✅ Test on staging (develop branch) before production (main branch)
✅ Use TSH NeuroLink for ALL notifications and communications

Deployment (TEMPORARY DEVELOPMENT MODE):
✅ SSH to development server (ssh root@167.71.39.50)
✅ Pull latest code (git pull origin develop)
✅ Build and restart Docker containers (docker-compose up -d --build)
✅ Verify health endpoints (curl http://localhost:8000/health)
✅ Check container logs (docker-compose logs -f)
❌ GitHub Actions DISABLED - Do not use gh run commands
❌ Staging environment DISABLED - Do not use 167.71.58.65
```

---

## 🎯 Quick Decision Trees

### Should I Create New Code or Enhance Existing?
```
Start → Search existing code (Grep/Glob/Task tool)
  ├─→ Found similar? → YES → Enhance existing ✅
  ├─→ Found similar? → NO → Create new ✅
  └─→ Not sure? → Use Task tool with Explore agent
```

### Should I Ask the User?
```
Start → Is this business logic?
  ├─→ YES → Ask user ✅
  └─→ NO → Is there ONE clear technical solution?
      ├─→ YES → Implement ✅
      └─→ NO (multiple options) → Ask user ✅
```

### Should I Optimize This Code?
```
Start → Is it slow? (>2 seconds)
  ├─→ NO → Don't optimize (premature) ❌
  └─→ YES → Does it affect many users?
      ├─→ NO → Low priority (defer) ⏸️
      └─→ YES → Optimize now ✅ (measure → optimize → verify)
```

---

## 📋 Most Common Commands (TEMPORARY DEVELOPMENT MODE)

### Git Operations
```bash
# Check status and branch
git status && git branch

# Recent commits
git log --oneline -10

# Push to develop (version control only, NO CI/CD)
git push origin develop
```

### Docker Deployment (TEMPORARY MODE)
```bash
# SSH to development server
ssh root@167.71.39.50

# Deploy all services
cd /var/www/tsh-erp && docker-compose up -d --build

# Restart specific service
docker-compose restart backend

# Check container status
docker ps

# View logs
docker-compose logs -f backend
docker-compose logs -f tds-core
```

### Verification (TEMPORARY MODE)
```bash
# Health checks (on server)
curl http://localhost:8000/health
curl http://localhost:8001/api/health  # TDS Core
curl http://localhost:8002/health      # BFF

# Database check
PGPASSWORD='TSH@2025Secure!Production' psql -h localhost -U tsh_app_user \
  -d tsh_erp_production -c "SELECT COUNT(*) FROM products WHERE is_active = true;"
```

### Server Access
```bash
# SSH to production (requires approval)
ssh root@167.71.39.50

# Check backend logs
ssh root@167.71.39.50 "tail -100 /var/www/tsh-erp/logs/backend.log"

# Check TDS Core status
curl https://tds.tsh.sale/api/health
```

---

## 📚 File References (Lazy Loading with @docs/)

**For detailed context, use @docs/ prefix to load on-demand:**

### Core Documentation (High Priority - Auto-Loaded)
- `@docs/CLAUDE.md` - **THIS FILE** - Main context (auto-loaded every session)
- `@docs/core/engineering-standards.md` - **GLOBAL STANDARDS** (Architecture • Security • Coding • Testing)
- `@docs/core/project-context.md` - Full business context and scale
- `@docs/core/architecture.md` - Technical patterns and constraints
- `@docs/core/workflows.md` - Common development workflows
- `@docs/PROJECT_VISION.md` - Business vision and core principles
- `@docs/QUICK_REFERENCE.md` - 60-second context refresh

### Security & Authorization (CRITICAL)
- `@docs/AUTHORIZATION_FRAMEWORK.md` - **3-layer security** (RBAC + ABAC + RLS)
- `@docs/ARCHITECTURE_RULES.md` - Technical constraints and patterns
- `@docs/AI_CONTEXT_RULES.md` - AI-specific rules and guidelines

### Deployment & Operations
- `@docs/DEPLOYMENT_STANDARDS.md` - **MANDATORY** Docker & GitHub CI/CD standards (NEW)
- `@docs/DEPLOYMENT_GUIDE.md` - Complete deployment procedures
- `@docs/DOCKER_DEPLOYMENT_GUIDE.md` - Container deployment specifics
- `@docs/FAILSAFE_PROTOCOL.md` - Emergency procedures and recovery
- `@docs/STAGING_TO_PRODUCTION_WORKFLOW.md` - Deployment workflow
- `@docs/SERVER_INFRASTRUCTURE.md` - Server details and access

### Integration & Systems
- `@docs/NEUROLINK_SYSTEM.md` - TSH NeuroLink unified communications
- `@docs/TDS_MASTER_ARCHITECTURE.md` - Zoho sync orchestration
- `@docs/PHASE_1_REQUIREMENTS.md` - Current phase requirements

### Code Patterns & Templates
- `@docs/CODE_TEMPLATES.md` - Reusable code patterns and examples
- `@docs/reference/code-templates/` - Detailed code templates by category
  - `authentication.md` - Auth patterns
  - `crud-operations.md` - CRUD patterns
  - `pagination.md` - Pagination patterns
  - `error-handling.md` - Error handling
  - `database-optimization.md` - DB optimization
  - `arabic-bilingual.md` - Arabic/RTL support
  - `testing.md` - Testing patterns
  - `zoho-sync.md` - Zoho integration patterns

### Problem-Solving & Reasoning
- `@docs/REASONING_PATTERNS.md` - Problem-solving frameworks
- `@docs/TASK_PATTERNS.md` - Task execution patterns
- `@docs/reference/failsafe/` - Failsafe procedures
  - `README.md` - Failsafe overview
  - `response-framework.md` - Response patterns
  - `recovery-procedures.md` - Recovery steps
  - `critical-scenarios/` - Specific failure scenarios

### AI Guidelines & Best Practices
- `@docs/reference/ai-guidelines/` - AI-specific guidelines
  - `ai-context-core.md` - Context management
  - `ai-operation-modes.md` - Operation modes
  - `ai-session-recovery.md` - Session recovery
  - `ai-monitoring.md` - Monitoring patterns
  - `ai-learning.md` - Learning patterns

### Quick Start & Reference
- `@docs/QUICK_START.md` - Quick start guide
- `@docs/QUICK_REFERENCE.md` - 60-second context refresh
- `@docs/SESSION_START.md` - Session start checklist
- `@docs/SESSION_CHECKLIST.md` - Session checklist
- `@docs/WORKING_TOGETHER.md` - Collaboration guidelines

### Knowledge & Resources
- `@docs/KNOWLEDGE_PORTAL.md` - Knowledge navigation hub
- `@docs/KNOWLEDGE_LINKS.md` - URLs and external resources
- `@docs/DOCUMENTATION_INDEX.md` - Complete documentation index
- `@docs/DOCUMENTATION_STANDARDS.md` - Documentation standards

### Agent System (Advanced)
- `@docs/AGENTS_INDEX.md` - Agent system overview
- `@docs/AGENT_ROUTING_SYSTEM.md` - Agent routing
- `@docs/AGENT_SYSTEM_SUMMARY.md` - Agent system summary
- `@docs/agents/` - Individual agent definitions

### Performance & Optimization
- `@docs/PERFORMANCE_OPTIMIZATION.md` - Performance guidelines
- `@docs/OPTIMIZATION_SUMMARY.md` - Optimization summary

### Commands & Scripts
- `@docs/SCRIPTS_QUICK_START.md` - Scripts quick start
- `@docs/commands/` - Command definitions
  - `start-work.md` - Start work command
  - `end-work.md` - End work command
  - `context-handoff.md` - Context handoff
  - `reload-context.md` - Reload context

### State & Configuration
- `@docs/state/current-phase.json` - Current project phase state
- `@docs/settings.local.json` - Local settings (if exists)
- `@docs/credentials.local.md` - **CONFIDENTIAL** Server credentials (gitignored, local only)

### Legacy Files (Reference Only)
- Original files in `.claude.backup/` for reference
- Use new consolidated structure above

---

## 🎬 Session Start Checklist (Quick Orientation)

```yaml
1. Context Loaded:
   ✓ This CLAUDE.md file (auto-loaded)
   ✓ Current phase: Zoho Migration Phase 1
   ✓ Authorization framework: RBAC + ABAC + RLS
   ✓ Scale awareness: 500+ clients, 2,218+ products

2. Current State:
   - Check git status and current branch
   - Review recent commits (git log --oneline -5)
   - Verify no uncommitted critical changes

3. Ready to Work:
   - Ask user what we're working on today
   - Load relevant @docs/ files if needed
   - Search existing code before creating new
   - Remember: ALL operations need 3 authorization layers
```

---

## 🚨 Emergency Protocols (Quick Actions)

### Production Down (TEMPORARY MODE)
```bash
1. SSH to server: ssh root@167.71.39.50
2. Check Docker containers: docker ps
3. Check container logs: docker-compose logs --tail=100
4. Restart containers: docker-compose restart
5. Rebuild if needed: docker-compose up -d --build
6. Check health: curl http://localhost:8000/health
7. Follow: @docs/FAILSAFE_PROTOCOL.md
```

### Zoho Sync Failure
```bash
1. Check dashboard: https://tds.tsh.sale
2. Check logs: tail -100 /var/www/tds-core/logs/tds_core.log
3. Check token expiration (regenerate if needed)
4. Restart TDS Core: systemctl restart tds-core
5. Monitor sync status on dashboard
```

### Database Issues
```bash
1. Check connections: SELECT count(*) FROM pg_stat_activity;
2. Check locks: SELECT * FROM pg_locks WHERE NOT granted;
3. Restart PostgreSQL: systemctl restart postgresql
4. Alert user if data corruption suspected
```

---

## 🎯 Performance Thresholds (When to Act)

```yaml
Pagination: > 100 records → MUST paginate
Indexing: > 1,000 rows → MUST index foreign keys and search fields
Background Jobs: > 5 seconds → Move to background job (Celery)
Caching: Read:Write ratio > 10:1 → Consider caching
Response Time:
  < 500ms → Good ✅
  500ms - 2s → Investigate ⚠️
  > 2s → Optimize immediately 🚨
```

---

## 🔄 Current Project State (Dynamic - Loaded from State File)

```yaml
# ✅ ENHANCED: Now reads from .claude/state/current-phase.json
# For complete current state, reference: @.claude/state/current-phase.json

Quick Reference (from state file v2.0.0):
  Phase: Zoho Migration Phase 1 (v1.2.0) - 65% complete
  Can Write to Zoho: NO (Phase 1 restriction)
  Last Updated: 2025-11-17T00:00:00Z

  🚨 DEPLOYMENT MODE: TEMPORARY DEVELOPMENT MODE
  Environment Mode: Direct Docker (GitHub CI/CD DISABLED)

  Environments:
    Development: 167.71.39.50 (Direct Docker) - ACTIVE
    Staging: 167.71.58.65 (DISABLED - Temporary Mode)
    GitHub Actions: DISABLED
    CI/CD Pipelines: DISABLED

  Integration Health:
    ✅ Zoho Books: healthy (last sync: 12:45)
    ✅ Zoho Inventory: healthy (last sync: 12:45)
    ✅ TDS Core v2.1.0: operational
    ✅ TSH NeuroLink v1.0.0: operational

  Sync Status:
    ✅ Products: 2,218 active (complete)
    ✅ Stock Levels: 99% accuracy (complete)
    ⚠️  Customers: 500+ (needs verification)
    ⏸️  Vendors: pending (Phase 2)
    🔄 Sales Orders: in progress (testing)
    ⏸️  Invoices: pending (Phase 2)
    ⏸️  Payments: pending (Phase 2)

# To update state, edit: .claude/state/current-phase.json
# State file includes: feature_flags, scale_metrics, milestones, change_log
```

---

## 💡 Success Indicators (How I Know I'm Doing Well)

```yaml
✅ User doesn't have to repeat context
✅ I search before creating new code
✅ I never forget Arabic fields or RTL support
✅ I never forget the 3 authorization layers
✅ I deploy all components together
✅ I test on staging first
✅ Features work correctly first time
✅ User feels productive working with me

❌ Red Flags (Need Improvement):
❌ User repeats same context
❌ I create duplicate functionality
❌ I forget Arabic fields or authorization layers
❌ I deploy partial components
❌ I skip staging testing
❌ Same bugs appear repeatedly
```

---

## 🧠 Context Refresh Protocol

**If I'm confused or lost:**
1. Re-read this CLAUDE.md (you are here)
2. Check `@docs/core/project-context.md` for business context
3. Check `@docs/core/architecture.md` for technical rules
4. Check `@docs/QUICK_REFERENCE.md` for quick facts
5. Ask user for clarification on specific point

**If user mentions major change:**
- "We've moved to Phase 2" → Re-read `@docs/core/project-context.md`
- "Now in production mode" → Re-read `@docs/DEPLOYMENT_GUIDE.md`
- "Architecture changed" → Re-read `@docs/core/architecture.md`

---

## 📊 Project Scale Awareness (Always Remember)

```
Users in System:
├─ 500+ wholesale clients (B2B)
├─ 100+ partner salesmen (social media sellers)
├─ 12 travel salespersons ($35K USD weekly)
├─ 30+ daily retail customers (B2C)
└─ Multiple warehouse staff + office admin

Daily Operations:
├─ 30 wholesale orders/day
├─ 30 retail transactions/day
├─ Multi-million IQD transaction volume
└─ Real-time GPS tracking for field teams

Technical Footprint:
├─ 2,218+ active products (growing)
├─ 57 database tables (127 MB)
├─ 8 specialized Flutter mobile apps
├─ 198+ BFF API endpoints
├─ 82 utility scripts
└─ Multiple integrations (Zoho Books, Zoho Inventory, WhatsApp)
```

This scale means:
- Pagination is MANDATORY (not optional)
- Database indexes are CRITICAL (not nice-to-have)
- Performance matters (thousands of users affected)
- Security is paramount (real revenue at stake)
- Arabic support is PRIMARY (not secondary)

---

**END OF CLAUDE.MD**

*This file is automatically loaded every session. Keep it under 500 lines for optimal prompt caching. For detailed documentation, use @docs/ references.*

*Backup of original configuration: `.claude.backup/`*
