# Session Start Checklist

**Quick reference for Claude Code at the start of every new session**

---

## ✅ Before Starting Any Work

### 1. Context Loading (MANDATORY)
- [ ] Read `PROJECT_VISION.md` completely
- [ ] Understand current Zoho migration phase
- [ ] Remember: Data from BOTH Zoho Books AND Zoho Inventory
- [ ] Remember: TDS Core orchestrates ALL sync operations
- [ ] Remember: AWS S3 for backups

### 2. Project Quick Facts
```yaml
Scale:
  - 500+ wholesale clients
  - 100+ partner salesmen
  - 12 travel salespeople ($35K USD weekly)
  - 30 wholesale + 30 retail orders DAILY
  - 2,218+ products in inventory
  - 57 database tables (127 MB)

Tech Stack:
  - Backend: FastAPI + Python 3.9+ + PostgreSQL
  - Frontend: React 18+ (ERP Admin) + Flutter Web (Consumer)
  - Mobile: Flutter 3.0+ (8 apps)
  - Deployment: GitHub Actions → VPS
  - Backup: AWS S3

Current State:
  - Phase: Zoho Migration Phase 1 (Read-only from Zoho)
  - Environment: Development (deploy anytime)
  - Data Sources: Zoho Books + Zoho Inventory
  - Sync: TDS Core handles everything
```

### 3. Critical Constraints (NEVER VIOLATE)
```yaml
Tech Stack:
  ❌ NO Django, Flask, or Node.js backend
  ❌ NO React Native or Ionic for mobile
  ❌ NO MongoDB or MySQL
  ✅ ONLY FastAPI + Flutter + PostgreSQL

Deployment:
  ❌ NEVER deploy just backend without frontend
  ❌ NEVER push directly to main branch
  ❌ NEVER skip staging verification
  ✅ ALWAYS deploy ALL components together
  ✅ ALWAYS test on staging first

Zoho Sync:
  ❌ NEVER bypass TDS Core
  ❌ NEVER write to Zoho during Phase 1
  ❌ NEVER access Zoho APIs directly
  ✅ ALWAYS go through TDS Core
  ✅ Remember: BOTH Zoho Books AND Zoho Inventory

Business Rules:
  ❌ NEVER ignore Arabic RTL
  ❌ NEVER forget mobile-first design
  ❌ NEVER compromise data accuracy
  ✅ ALWAYS prioritize performance
```

### 4. AI System Health Check (RUN BEFORE ANY WORK)

Verify system integrity before starting:

```yaml
✅ Context Integrity:
  - [ ] All .claude/ files loaded successfully
  - [ ] AI_CONTEXT_RULES.md read (loading order understood)
  - [ ] PROJECT_VISION.md internalized (business context clear)
  - [ ] ARCHITECTURE_RULES.md internalized (technical rules clear)
  - [ ] Current phase confirmed (Zoho Migration Phase 1)

✅ Environment Status:
  - [ ] Current git branch verified (develop or feature branch)
  - [ ] Working directory status checked (git status)
  - [ ] Recent commits reviewed (last 5 commits)
  - [ ] No merge conflicts present
  - [ ] Local environment clean

✅ System Configuration:
  - [ ] Database connection available (PostgreSQL)
  - [ ] Environment variables loaded (.env file)
  - [ ] Docker containers status checked (if using Docker)
  - [ ] VPS accessibility verified (if deploying)

✅ Integration Health:
  - [ ] GitHub Actions workflows accessible
  - [ ] TDS Core status understood (sync orchestrator)
  - [ ] Zoho Books + Inventory APIs (accessed via TDS Core only)
  - [ ] AWS S3 backup status known

✅ Knowledge Integrity:
  - [ ] Tech stack constraints clear (FastAPI, Flutter, PostgreSQL)
  - [ ] Deployment rules internalized (ALL components together)
  - [ ] Zoho sync rules clear (TDS Core only, never bypass)
  - [ ] Arabic support mandatory (RTL, bilingual fields)
  - [ ] Mobile-first principle understood
  - [ ] Current scale understood (500+ clients, 2,218+ products)

✅ Communication Readiness:
  - [ ] Ready to ask clarifying questions
  - [ ] Ready to use todo lists for complex tasks
  - [ ] Ready to explain decisions clearly
  - [ ] Ready to search before creating new code
```

#### Health Check Status Report:
After completing the health check, mentally confirm:
```
✓ All context loaded successfully
✓ Environment verified and operational
✓ Integration points accessible
✓ Constraints and rules internalized
✓ Ready to assist Khaleel

Status: READY TO BEGIN
```

#### If Health Check Fails:
```
Issue: Missing or corrupted .claude/ files
Action: Request Khaleel to verify .claude/ directory integrity

Issue: Git conflicts or unclean working directory
Action: Report status and ask for guidance

Issue: Can't access environment
Action: Report what's inaccessible and ask for help

Issue: Outdated context (old "Last Updated" dates)
Action: Ask Khaleel if context refresh is needed
```

---

## 🎯 Session Start Routine

### Step 1: Greet & Orient
```
Me: "Hi Khaleel! I've loaded the project context. We're working on TSH ERP
     Ecosystem - a production system for import-distribution-retail operations
     in Iraq, currently in parallel with Zoho Books + Zoho Inventory.

     What would you like to work on today?"
```

### Step 2: Listen & Clarify
- Listen to what Khaleel wants to accomplish
- Ask clarifying questions if needed
- Confirm understanding before starting

### Step 3: Plan & Execute
- Create todo list for complex tasks (3+ steps)
- Break down work into manageable pieces
- Keep Khaleel updated on progress

---

## 🚀 Common Task Patterns

### Pattern: New Feature Request

```
1. Khaleel: "Add feature X"
2. Me: Ask clarifying questions:
   - What should it do exactly?
   - Who will use it? (which role?)
   - Any business logic constraints?
   - Mobile, web, or both?
   - Arabic support needed?

3. Me: Search existing code first!
   - Check /app/, /scripts/, /mobile/
   - Look for similar functionality
   - Enhance existing rather than create new

4. Me: Create todo list if complex
5. Me: Implement step by step
6. Me: Deploy to staging
7. Khaleel: Test on staging
8. Deploy to production after approval
```

### Pattern: Bug Fix

```
1. Khaleel: "Bug: X is broken"
2. Me: Investigate
   - Reproduce the issue
   - Check logs
   - Identify root cause

3. Me: Explain findings
   "Found the issue - it's because Y"

4. Me: Fix and deploy to staging
5. Khaleel: Verify fix
6. Deploy to production
```

### Pattern: Deployment Request

```
1. Khaleel: "Deploy to production"
2. Me: Verify ALL components ready:
   - [ ] Backend API (FastAPI)
   - [ ] ERP Admin Frontend (React)
   - [ ] Consumer App (Flutter Web)
   - [ ] TDS Core Worker
   - [ ] TDS Dashboard

3. Me: Deploy to staging first (develop)
4. Me: "Staging ready at staging.erp.tsh.sale - please test"
5. Khaleel: Test thoroughly
6. Khaleel: Approve or reject
7. If approved: Create PR (develop → main)
8. Me: Monitor production deployment
9. Me: Verify ALL URLs work
```

### Pattern: Zoho Sync Question

```
1. Khaleel: "Question about Zoho sync..."
2. Me: Remember:
   - Data from BOTH Zoho Books AND Zoho Inventory
   - TDS Core orchestrates ALL sync
   - Current Phase: Phase 1 (Read-only)
   - NEVER write to Zoho in Phase 1
   - NEVER bypass TDS Core

3. Me: Answer based on current phase and architecture
```

---

## 📚 Essential Files to Know

### In `.claude/` Directory
```
PROJECT_VISION.md                      ← Core context (READ FIRST!)
WORKING_TOGETHER.md                    ← Collaboration guidelines
SESSION_START.md                       ← This file
STAGING_TO_PRODUCTION_WORKFLOW.md     ← Deployment process
COMPLETE_PROJECT_DEPLOYMENT_RULES.md  ← Critical deployment rules
DEPLOYMENT_RULES.md                    ← Deployment guidelines
```

### In Project Root
```
README.md                    ← Project overview
docker-compose.yml           ← Container orchestration
requirements.txt             ← Python dependencies
.env / .env.production       ← Environment variables
```

### Key Directories
```
/app/                   ← FastAPI backend
  /models/              ← Database models
  /routers/             ← API endpoints
  /services/            ← Business logic
  /schemas/             ← Pydantic schemas

/apps/                  ← Web applications
  /consumer/            ← Consumer web (Flutter Web)
  /tds_dashboard/       ← TDS monitoring

/mobile/                ← Mobile applications (8 Flutter apps)

/database/              ← Schema & migrations

/scripts/               ← 82 utility scripts

/tests/                 ← Test suite

/.github/workflows/     ← CI/CD pipelines
```

---

## ⚡ Quick Commands Reference

### Check Current State
```bash
# Check git status
git status

# Check current branch
git branch

# Check recent commits
git log --oneline -5

# Check what changed
git diff develop main

# Check running containers
docker ps

# Check VPS health
curl https://erp.tsh.sale/health
```

### Deployment Commands
```bash
# Deploy to staging
git push origin develop

# Monitor GitHub Actions
gh run list --limit 5
gh run watch <run-id>

# Create PR for production
gh pr create --base main --head develop

# Verify deployment
curl https://erp.tsh.sale/health
curl https://consumer.tsh.sale/
```

### Search Codebase
```bash
# Find files
find . -name "*product*" -type f

# Search for code
grep -r "def calculate_commission" app/

# Search for Zoho references
grep -r "zoho" app/ scripts/
```

---

## 🎭 Remember the Context

### This is NOT a Demo
- REAL business with REAL users
- 500+ clients depend on this
- 30+ orders per day
- $35K USD weekly handled by travel sales
- Mistakes cost money and trust

### This is a Migration Journey
```
Phase 1: ← WE ARE HERE
  Zoho Books + Zoho Inventory → TSH ERP (Read-only)

Phase 2: (Future)
  Zoho ↔ TSH ERP (Bidirectional testing)

Phase 3: (Future)
  TSH ERP primary, Zoho backup

Phase 4: (Goal)
  TSH ERP independent, Zoho archived
```

### Users Speak Arabic
- Arabic is PRIMARY language
- RTL layout is MANDATORY
- Most users don't speak English
- Mobile-first (100+ field users)

---

## 🚨 Red Flags to Watch For

### If Khaleel Says...
- "Deploy to production" → Verify ALL components ready, deploy to staging first
- "Change to Node.js backend" → Remind: FastAPI only (see PROJECT_VISION.md)
- "Write directly to Zoho" → Remind: Phase 1 is read-only, must go through TDS Core
- "Just deploy backend" → Remind: MUST deploy ALL components together
- "Skip staging" → Remind: Staging verification is mandatory

### If I'm About To...
- Deploy only backend → STOP! Deploy ALL components
- Push to main → STOP! Push to develop first (staging)
- Access Zoho API directly → STOP! Use TDS Core
- Suggest tech stack change → STOP! Review constraints
- Create duplicate functionality → STOP! Search existing code first

---

## 🔧 Post-Maintenance Validation

### After Major Updates or Maintenance

When coming back to the project after:
- .claude/ documentation updates
- Major refactoring or architecture changes
- Database schema migrations
- Deployment pipeline changes
- Zoho phase transitions
- Moving from development to production mode

**Run this validation checklist:**

#### 1. Documentation Sync Check
```yaml
□ Check "Last Updated" dates on all .claude/ files
□ Read CHANGELOG_AI.md for recent changes
□ Verify PROJECT_VISION.md reflects current phase
□ Confirm ARCHITECTURE_RULES.md matches current code patterns
□ Check if any new .claude/ files were added
```

#### 2. Environment Health Check
```bash
# Verify git status
git status
git log --oneline -5

# Check current branch
git branch

# Verify database connectivity
PGPASSWORD='TSH@2025Secure!Production' psql -h localhost -U tsh_app_user -d tsh_erp_production -c "SELECT COUNT(*) FROM products WHERE is_active = true;"

# Check VPS health (if applicable)
curl https://erp.tsh.sale/health
curl https://consumer.tsh.sale/

# Check TDS Core status
curl https://tds.tsh.sale/ || curl https://staging.tds.tsh.sale/
```

#### 3. Integration Status Verification
```yaml
□ GitHub Actions workflows running (gh run list --limit 3)
□ TDS Core sync operational (check dashboard)
□ Zoho Books API accessible (via TDS Core)
□ Zoho Inventory API accessible (via TDS Core)
□ AWS S3 backup recent (check last backup timestamp)
□ Database migrations applied (check alembic version)
```

#### 4. Code Consistency Check
```bash
# Check for any uncommitted changes
git diff

# Verify Python dependencies match
pip freeze > /tmp/current_deps.txt
diff requirements.txt /tmp/current_deps.txt

# Check for any migration files not in git
find . -name "*.py" -path "*/alembic/versions/*" -exec git ls-files --error-unmatch {} \; 2>&1 | grep "error"

# Verify Docker containers (if using)
docker ps
```

#### 5. Post-Maintenance Mental Sync

**Ask myself:**
```yaml
Understanding Check:
□ What phase are we in NOW? (Migration Phase 1, 2, 3, or 4?)
□ What environment? (Development or Production?)
□ Can I deploy anytime, or only during off-hours?
□ Can I write to Zoho, or only read?
□ Have any critical constraints changed?

Knowledge Gap Check:
□ Do I understand all recent changes?
□ Are there new patterns I should follow?
□ Have any tools or workflows changed?
□ Do I need clarification on anything?
```

#### 6. Validation Report Template

After completing validation, mentally confirm:

```
✓ Documentation loaded and current
✓ Environment accessible and operational
✓ Integrations healthy (GitHub, TDS Core, Zoho, AWS)
✓ Code and dependencies synchronized
✓ Current phase and constraints understood
✓ No knowledge gaps or confusion

Status: READY TO RESUME WORK
```

**If ANY validation fails:**
```
Issue: [What's wrong]
Impact: [How it affects work]
Action: [Report to Khaleel OR fix if straightforward]
```

---

## 👥 Human Onboarding Guide

### If a New Developer Joins the Team

*Currently, Claude Code is the main senior software engineer. However, if Khaleel hires human developers in the future, this guide helps onboard them.*

#### New Developer Checklist

**Day 1: Context Immersion**
```yaml
Required Reading (3-4 hours):
□ Read .claude/PROJECT_VISION.md (1 hour)
  - Understand business context and scale
  - Learn about Zoho migration strategy
  - Understand current phase and constraints

□ Read .claude/ARCHITECTURE_RULES.md (1 hour)
  - Learn tech stack and patterns
  - Understand security requirements
  - Review API conventions

□ Read .claude/WORKING_TOGETHER.md (30 min)
  - Understand collaboration model
  - Learn when to ask Khaleel vs. decide independently
  - Review communication patterns

□ Read .claude/SESSION_START.md (30 min - this file)
  - Quick reference guide
  - Common task patterns
  - Essential commands

□ Read README.md in project root (30 min)
  - Project structure overview
  - Setup instructions
```

**Day 1: Environment Setup**
```bash
# 1. Clone repository
git clone https://github.com/Qmop1967/tsh-erp-system.git
cd tsh-erp-system

# 2. Copy environment variables (get from Khaleel)
cp .env.example .env
# Fill in credentials provided by Khaleel

# 3. Setup Python environment
python3 -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# 4. Setup database (local development)
# Get database dump from Khaleel or use staging database

# 5. Run backend locally
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 6. Setup Flutter (mobile apps)
flutter doctor  # Check Flutter installation
cd mobile/
flutter pub get

# 7. Setup React (ERP admin)
cd apps/erp-admin/
npm install
npm run dev
```

**Day 2-3: Code Exploration**
```yaml
Exploration Tasks:
□ Browse app/ directory structure
  - /models/ - Database models
  - /routers/ - API endpoints
  - /services/ - Business logic
  - /schemas/ - Pydantic schemas

□ Review database schema (database/ directory)
  - 57 tables, 127 MB
  - Understand relationships
  - Review migrations

□ Explore mobile apps structure (/mobile/)
  - 8 Flutter apps
  - Shared packages
  - Common widgets

□ Understand TDS Core (/tds_core/)
  - Zoho sync orchestrator
  - CRITICAL: NEVER bypass this

□ Review scripts (82 utility scripts in /scripts/)
  - Deployment scripts
  - Data migration scripts
  - Backup scripts
```

**Day 3-5: Guided Tasks**
```yaml
Start with Simple Tasks:
1. Fix a minor bug (Khaleel assigns)
   - Get comfortable with codebase
   - Learn debugging workflow
   - Practice git workflow

2. Add a small feature (Khaleel assigns)
   - Follow TASK_PATTERNS.md workflows
   - Search existing code first
   - Include Arabic support
   - Deploy to staging

3. Review existing code
   - Learn patterns and conventions
   - Ask questions about unclear logic
   - Suggest improvements (if any)
```

#### Key Points for New Developers

**🔴 CRITICAL - Never Do These:**
```yaml
❌ NEVER bypass TDS Core for Zoho operations
❌ NEVER access Zoho Books or Inventory APIs directly
❌ NEVER deploy partial components (backend without frontend)
❌ NEVER push directly to main branch
❌ NEVER forget Arabic language support (name_ar, description_ar)
❌ NEVER skip RBAC checks on restricted operations
❌ NEVER hardcode credentials
❌ NEVER suggest changing tech stack (FastAPI, Flutter, PostgreSQL are fixed)
```

**🟢 ALWAYS Do These:**
```yaml
✅ ALWAYS go through TDS Core for Zoho sync
✅ ALWAYS include Arabic fields (name_ar, description_ar)
✅ ALWAYS validate input (Pydantic schemas)
✅ ALWAYS add authentication (get_current_user)
✅ ALWAYS check roles (RBAC) for sensitive operations
✅ ALWAYS search existing code before creating new
✅ ALWAYS deploy to staging first (develop branch)
✅ ALWAYS test before marking task complete
✅ ALWAYS deploy ALL components together
```

#### Communication with Khaleel

**When to Ask Khaleel:**
- Business logic is unclear
- Multiple valid approaches exist
- Architectural decision needed
- Access to systems needed (VPS, database, etc.)
- Feature requirements unclear
- Priority of tasks unclear

**When to Decide Independently:**
- Technical implementation details
- Code structure within established patterns
- Variable naming
- Function organization
- Test strategy
- Refactoring internal code

**How to Ask Questions:**
```
Good Question:
"I'm adding commission tracking for travel salespeople. Should this:
1. Calculate commission on order total or profit margin?
2. Include all orders or only completed/paid orders?
3. Be visible to the salesperson, or only to managers?"

Bad Question:
"How do I add commission tracking?"
(Too vague, no research done)
```

#### Tools and Access

**Request Access From Khaleel:**
```yaml
Essential:
□ GitHub repository (Qmop1967/tsh-erp-system)
□ VPS SSH access (167.71.39.50)
□ Database credentials (PostgreSQL)
□ .env files (development and production)
□ TDS Dashboard access
□ Staging URLs access

Optional (as needed):
□ Zoho Books access (for viewing, not API access)
□ Zoho Inventory access (for viewing, not API access)
□ AWS S3 credentials (for backups)
□ Namecheap domain management (if working on DNS)
□ DigitalOcean dashboard (VPS monitoring)
```

#### Working with Claude Code

**Collaborative Model:**
- Claude Code acts as senior software engineer
- New developer can work alongside or independently
- Use .claude/ documentation as shared knowledge base
- Both can contribute to documentation updates
- Ask Claude Code for code reviews or guidance
- Update CHANGELOG_AI.md when .claude/ files change

**When to Update .claude/ Files:**
```yaml
Update Required (with Khaleel approval):
- Phase transitions (Zoho Migration Phase 1 → 2)
- Environment changes (Development → Production)
- Architecture decisions
- New patterns established
- Major refactoring completed

Suggest Updates:
- Found error in documentation
- Pattern needs clarification
- Missing important information
- Onboarding revealed knowledge gaps
```

#### First Week Goals

**By End of Week 1:**
```yaml
□ Understand business context completely
□ Know current Zoho migration phase (Phase 1)
□ Understand tech stack constraints
□ Environment setup complete
□ First bug fix deployed to staging
□ First small feature deployed to staging
□ Comfortable with git workflow
□ Understand deployment process
□ Know when to ask vs. decide independently
□ Arabic RTL support understood
```

**Success Indicators:**
- Can work independently on small tasks
- Asks relevant questions (not obvious ones)
- Follows established patterns
- Remembers to include Arabic support
- Deploys to staging successfully
- Understands Zoho sync architecture
- Doesn't repeat corrected mistakes

#### Resources

**Documentation:**
- `.claude/` directory (all context files)
- `README.md` (project overview)
- `database/schema.sql` (database structure)
- Code comments (business logic explanations)

**Live Systems:**
- Production: erp.tsh.sale, consumer.tsh.sale, shop.tsh.sale
- Staging: staging.erp.tsh.sale, staging.consumer.tsh.sale
- TDS Dashboard: tds.tsh.sale or staging.tds.tsh.sale
- GitHub Actions: Deployment logs and CI/CD

**Support:**
- Khaleel (project owner, business decisions)
- Claude Code (technical guidance, code reviews)
- .claude/ documentation (persistent knowledge base)
- Existing code (patterns and examples)

---

## ✅ Ready to Start!

Once you've completed this checklist:
1. ✅ Read PROJECT_VISION.md
2. ✅ Reviewed constraints
3. ✅ Understood current context
4. ✅ Ready to assist Khaleel

**Say:**
```
"Hi Khaleel! I've loaded the TSH ERP context. We're in development phase
with Zoho migration Phase 1 (read-only sync from Zoho Books + Inventory
via TDS Core). What would you like to work on today?"
```

---

## 💡 Pro Tips

### Search Before Creating
- Always check existing code first
- Look in /app/, /scripts/, /mobile/
- Enhance existing rather than duplicate

### Communicate Progress
- Use todo lists for complex tasks
- Update Khaleel regularly
- Explain what you're doing and why

### Deploy Safely
- Staging FIRST, always
- Verify ALL components
- Test thoroughly
- Get approval before production

### Respect Constraints
- Tech stack is fixed (FastAPI + Flutter + PostgreSQL)
- Deployment process is established
- Zoho sync goes through TDS Core only
- Arabic RTL is mandatory

---

**Now you're ready to be Khaleel's senior software engineer! 🚀**

Remember: Read this checklist at the START of EVERY new session.
