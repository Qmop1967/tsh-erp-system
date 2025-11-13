# AI Context Rules - Meta-Guide for Claude Code

**How to read, interpret, and use the .claude/ knowledge base**
**Last Updated:** 2025-11-12

---

## 🎯 Purpose of This File

This file is the **meta-context guide** - it tells you (Claude Code) HOW to use all the other documentation files in this directory. Think of it as the "instruction manual for the instruction manuals."

---

## 📚 File Loading Order (Priority Hierarchy)

At the start of EVERY new session, load files in this exact order:

### 1. **AI_CONTEXT_RULES.md** (This File) - FIRST
**Priority: CRITICAL**
- Read this FIRST to understand how to interpret everything else
- Defines the framework for understanding the project

### 2. **PROJECT_VISION.md** - HIGHEST AUTHORITY
**Priority: CRITICAL**
- This is the **supreme authority** on business context
- Contains the "why" behind every decision
- All other files must align with this vision
- If any conflict arises, PROJECT_VISION.md wins

### 3. **SESSION_START.md** - QUICK REFERENCE
**Priority: HIGH**
- Quick checklist and facts
- Read after PROJECT_VISION.md for rapid orientation
- Use as a "quick refresh" guide

### 4. **ARCHITECTURE_RULES.md** - TECHNICAL AUTHORITY
**Priority: HIGH**
- Technical constraints and patterns
- "How" to implement the "what" from PROJECT_VISION.md
- If conflicts with PROJECT_VISION.md, ask Khaleel for clarification

### 4.5. **ZOHO_SYNC_RULES.md** - ZOHO SYNC AUTHORITY
**Priority: CRITICAL**
- MANDATORY Zoho sync procedures
- ALL Zoho operations MUST go through TDS Core
- Image download requirements
- Stock data handling
- NEVER bypass these rules

### 4.6. **CONSUMER_APP_TROUBLESHOOTING.md** - CONSUMER APP FIXES
**Priority: CRITICAL**
- Consumer app "Failed to load products" issue
- Price data migration procedures
- ALWAYS check product_prices table after deployment
- Two pricing systems bridge (product_prices ↔ price_list_items)
- Emergency fix procedures

### 4.7. **PRODUCT_DATA_VERIFICATION.md** - PRODUCT DATA TESTING
**Priority: CRITICAL**
- MANDATORY verification after every sync
- Test stock, prices, and images in ALL apps
- Consumer app, Admin app, and API verification
- Critical test products and procedures
- Automated verification scripts
- Common issues and fixes

### 5. **WORKING_TOGETHER.md** - COLLABORATION GUIDE
**Priority: MEDIUM**
- How Khaleel and I work together
- When to ask questions, when to decide
- Communication patterns

### 6. **Deployment Files** (As Needed)
**Priority: MEDIUM** - Load when working on deployment
- STAGING_TO_PRODUCTION_WORKFLOW.md
- COMPLETE_PROJECT_DEPLOYMENT_RULES.md
- DEPLOYMENT_RULES.md
- README_DEPLOYMENT.md

### 7. **KNOWLEDGE_LINKS.md** - OPERATIONAL LINKS
**Priority: LOW** - Load when needing specific resources
- GitHub URLs
- Server access
- Monitoring dashboards

---

## 🧠 Context Interpretation Rules

### Rule 1: Never Summarize - Always Internalize
**DON'T:**
- "I've read PROJECT_VISION.md which says..."
- Summarize back to Khaleel what I learned

**DO:**
- Internalize the context completely
- Act based on that context
- Only mention specific facts when relevant to current task

**Example:**
```
❌ BAD: "I see from PROJECT_VISION.md that you have 500+ clients"
✅ GOOD: "This feature needs to handle 500+ wholesale clients efficiently"
```

### Rule 2: Infer Actionable Rules
**DON'T:**
- Just store information passively
- Wait for explicit instructions on every detail

**DO:**
- Derive operational rules from context
- Apply them proactively

**Example from PROJECT_VISION.md:**
```
Context: "Data comes from BOTH Zoho Books AND Zoho Inventory"

Inferred Rules:
- When syncing products, check Zoho Inventory API
- When syncing invoices, check Zoho Books API
- TDS Core must handle BOTH APIs
- Never assume all data is in one place
```

### Rule 3: Connect Related Context
**DON'T:**
- Treat each file as isolated
- Apply rules in silos

**DO:**
- Connect business context (PROJECT_VISION.md) with technical rules (ARCHITECTURE_RULES.md)
- Understand WHY rules exist (business reasons)

**Example:**
```
PROJECT_VISION.md: "500+ wholesale clients place 30 orders daily"
ARCHITECTURE_RULES.md: "Use pagination, max 100 items per page"

Connected Understanding:
→ 500+ clients means large datasets
→ 30 daily orders means frequent writes
→ Pagination is required for performance
→ Database indexes are critical
```

### Rule 4: Maintain Temporal Awareness
**DON'T:**
- Forget that the project evolves
- Apply outdated context

**DO:**
- Note "Last Updated" dates on files
- Recognize current phase (Zoho Migration Phase 1)
- Understand we're in development (deploy anytime)
- Know that constraints may change as project matures

**Current State Awareness:**
```yaml
Date: 2025-11-12
Phase: Zoho Migration Phase 1 (Read-only from Zoho)
Environment: Development (deploy anytime)
Scale: 500+ clients, 2,218+ products, 30+ daily orders
Status: Parallel operation with Zoho Books + Zoho Inventory
```

---

## ⚖️ Conflict Resolution Hierarchy

When documents appear to conflict:

### Level 1: PROJECT_VISION.md (Supreme Authority)
- Business requirements
- Strategic direction
- Scale and constraints
- Zoho migration phases

**If PROJECT_VISION.md says it, it's LAW.**

### Level 2: ARCHITECTURE_RULES.md (Technical Authority)
- Implementation patterns
- Code conventions
- Security patterns
- Tech stack decisions

**If ARCHITECTURE_RULES.md conflicts with PROJECT_VISION.md:**
→ Ask Khaleel for clarification
→ Default to PROJECT_VISION.md until clarified

### Level 3: WORKING_TOGETHER.md (Process Authority)
- Collaboration patterns
- Communication guidelines
- Decision-making framework

### Level 4: Deployment Files (Operational Authority)
- Deployment procedures
- Environment configurations

### Level 5: KNOWLEDGE_LINKS.md (Reference Only)
- URLs and links
- No decision-making authority

### Example Conflict Resolution:
```
Scenario: ARCHITECTURE_RULES.md says "Use PostgreSQL" but I think MongoDB
          would be better for product data.

Resolution:
1. Check PROJECT_VISION.md → "PostgreSQL 12+ (single source of truth)"
2. Check ARCHITECTURE_RULES.md → "PostgreSQL only (NO MongoDB)"
3. Both align → PostgreSQL is the answer
4. Do NOT suggest MongoDB, even if technically valid

Result: Follow established architecture.
```

```
Scenario: PROJECT_VISION.md says "Deploy anytime during development" but
          STAGING_TO_PRODUCTION_WORKFLOW.md says "Avoid business hours"

Resolution:
1. Check current phase → Development phase
2. PROJECT_VISION.md (higher authority) says deploy anytime
3. Workflow file applies to production phase (future)
4. Current context: Development phase

Result: Deploy anytime is correct for NOW.
```

---

## 🔄 Context Refresh Events

Certain events should trigger a full re-read of context:

### Trigger Events (When to Re-Load Everything):

1. **Khaleel explicitly says:**
   - "We've moved to Phase 2 of Zoho migration"
   - "We're now in production"
   - "The architecture has changed"
   - "Re-read the vision"

2. **Major structural changes:**
   - New .claude/ files appear
   - PROJECT_VISION.md has newer "Last Updated" date
   - Tech stack changes (would be very rare)

3. **Phase transitions:**
   - Moving from Development to Production mode
   - Moving from Zoho Phase 1 to Phase 2
   - Major deployment milestones

4. **Error patterns suggesting outdated context:**
   - Repeated corrections from Khaleel on same topic
   - Suggestions that violate known constraints
   - Confusion about current state

### How to Refresh:
```
1. Acknowledge: "Let me re-read the project context..."
2. Load: Read all .claude/ files in priority order
3. Synthesize: Connect new information
4. Confirm: "I've updated my context. Ready to continue."
```

---

## 🚨 Error Handling and Recovery

### When Encountering Errors

#### Error Type 1: Runtime/Build Errors
```
Behavior:
1. Analyze the error immediately
2. Check logs and stack traces
3. Identify root cause
4. Propose solution with explanation
5. Implement fix
6. Verify fix works

DO NOT:
- Panic or give up
- Make random changes hoping it works
- Skip testing the fix
```

#### Error Type 2: Deployment Failures
```
Behavior:
1. Check GitHub Actions logs
2. Identify which component failed (backend, frontend, TDS Core)
3. Determine if it's code, config, or infrastructure issue
4. Propose rollback if critical
5. Fix root cause
6. Re-deploy to staging first

DO NOT:
- Deploy to production without fixing
- Ignore failing tests
- Assume "it will work next time"
```

#### Error Type 3: Zoho Sync Failures
```
Behavior:
1. Check TDS Core logs and dashboard
2. Identify which Zoho API (Books or Inventory)
3. Check if it's rate limit, authentication, or data issue
4. Verify current migration phase constraints
5. Propose fix through TDS Core (never bypass)

DO NOT:
- Access Zoho APIs directly
- Bypass TDS Core
- Ignore sync failures
```

#### Error Type 4: Context/Understanding Errors
```
Behavior:
1. Acknowledge confusion: "I'm not clear on..."
2. Reference what I think I know
3. Ask Khaleel for clarification
4. Update mental model
5. Confirm understanding

DO NOT:
- Guess and proceed
- Assume without asking
- Contradict established patterns without reason
```

### Escalation Flow
```
Level 1: Self-Resolution (< 5 minutes)
- Syntax errors
- Simple typos
- Clear bug fixes

Level 2: Explanation + Fix (5-15 minutes)
- Logic errors
- Integration issues
- Performance problems
→ Explain what happened and how to fix

Level 3: Discussion Required (> 15 minutes)
- Architecture questions
- Business logic uncertainty
- Multiple solution paths
→ Present options and ask Khaleel

Level 4: Immediate Escalation
- Production is down
- Data corruption risk
- Security vulnerability
- Critical sync failure
→ Alert Khaleel immediately
```

### Logging and Issue Tracking
```
When encountering errors:
1. Log clearly what happened
2. Document steps to reproduce
3. Explain root cause
4. Document the fix
5. Add to knowledge base if recurring

For recurring issues:
- Update ARCHITECTURE_RULES.md with prevention pattern
- Add to SESSION_START.md checklist
- Inform Khaleel for documentation update
```

---

## 🎯 AI Behavioral Boundaries

### Absolute Rules (NEVER Violate):

#### 1. Tech Stack Integrity
```yaml
NEVER suggest:
  - Replacing FastAPI with Django/Flask/Node.js
  - Replacing PostgreSQL with MongoDB/MySQL
  - Replacing Flutter with React Native/Ionic
  - Adding new frameworks without explicit approval

ALWAYS:
  - Work within established stack
  - Enhance existing architecture
  - Optimize current choices
```

#### 2. Zoho Sync Integrity
```yaml
NEVER:
  - Access Zoho Books API directly
  - Access Zoho Inventory API directly
  - Bypass TDS Core for sync operations
  - Write to Zoho during Phase 1

ALWAYS:
  - Go through TDS Core for ALL Zoho operations
  - Respect current migration phase constraints
  - Remember data comes from BOTH Zoho products
```

#### 3. Deployment Integrity
```yaml
NEVER:
  - Deploy only backend without frontend
  - Push directly to main branch
  - Skip staging verification
  - Deploy without testing all components

ALWAYS:
  - Deploy ALL components together
  - Test on staging first (develop branch)
  - Verify ALL URLs after deployment
  - Follow established workflow
```

#### 4. Data Integrity
```yaml
NEVER:
  - Ignore Arabic language support
  - Skip input validation
  - Bypass authentication
  - Ignore role-based permissions

ALWAYS:
  - Include Arabic (name_ar, description_ar)
  - Support RTL layout
  - Validate all inputs
  - Enforce RBAC
```

### Communication Rules

#### When Uncertain:
```
DO:
✅ "I need clarification on..."
✅ "Should I... or...?"
✅ "Based on X, I think we should Y. Confirm?"
✅ Reference PROJECT_VISION.md or ARCHITECTURE_RULES.md

DON'T:
❌ Guess silently and proceed
❌ Make up requirements
❌ Assume business logic
```

#### When Explaining:
```
DO:
✅ Use clear, concise language
✅ Explain WHY, not just WHAT
✅ Reference context when relevant
✅ Provide code examples

DON'T:
❌ Be overly verbose
❌ Repeat documentation back
❌ Use jargon without explanation
```

#### When Suggesting Optimizations:
```
DO:
✅ Provide performance justification
✅ Explain trade-offs
✅ Show before/after examples
✅ Estimate impact

DON'T:
❌ Suggest optimizations without measurement
❌ Optimize prematurely
❌ Change working code without reason
```

---

## 💾 Memory Continuity Strategy

### What I Remember (Within Session):
- Everything discussed in current conversation
- Files I've read
- Code I've written
- Decisions made

### What I DON'T Remember (Between Sessions):
- Previous conversations
- Yesterday's work
- Past decisions not in documentation

### How to Maintain Continuity:

#### Start of Each Session:
```
1. Load .claude/ files in priority order
2. Check current git branch and recent commits
3. Review any changes to .claude/ files
4. Ask Khaleel what we're working on today
5. Build mental model of current state
```

#### During the Session:
```
1. Update todo list for complex tasks
2. Document important decisions in code comments
3. Suggest documentation updates when appropriate
```

#### End of Session (If Applicable):
```
1. Mark all todos complete or pending
2. Commit code with clear messages
3. Suggest updating .claude/ files if major decisions made
```

### Context Preservation Checklist:
```
For Khaleel (to help me remember next session):
- [ ] Update PROJECT_VISION.md if business context changed
- [ ] Update ARCHITECTURE_RULES.md if patterns changed
- [ ] Write clear git commit messages
- [ ] Document decisions in code comments
- [ ] Update .env or config if needed

For Claude (me):
- [ ] Write clear, self-documenting code
- [ ] Add comments explaining business logic
- [ ] Document API endpoints with OpenAPI
- [ ] Create migration notes if database changed
```

---

## 🔄 Automatic Session Recovery Protocol

### When Sessions Split or Reset

Claude Code sessions can reset or split automatically. When this happens:

**Detection Signals:**
```yaml
I've lost context when:
- Previous messages are not visible
- I don't remember recent work
- Conversation history appears truncated
- New session without seeing /CLAUDE.md prompt
```

**Automatic Recovery Steps:**
```yaml
1. Detect Context Loss:
   - Notice that previous conversation is missing
   - Acknowledge: "I notice this is a new session or context was reset"

2. Immediate Context Reload:
   - Read .claude/AI_CONTEXT_RULES.md (this file)
   - Read .claude/PROJECT_VISION.md
   - Read .claude/QUICK_REFERENCE.md
   - Read .claude/ARCHITECTURE_RULES.md

3. Reconstruct Current State:
   - Check git status (last commits)
   - Check current branch
   - Check for any uncommitted changes
   - Review recent git log

4. Ask for Minimal Recap:
   - "I've reloaded context from .claude/ files. We're working on TSH ERP
      (Phase 1 Zoho migration, FastAPI+Flutter+PostgreSQL).

      I see recent commits show [summary from git log].

      What were we working on, and should I continue or start something new?"

5. Resume Work:
   - Khaleel provides brief context
   - No need to repeat information from .claude/ files
   - Continue from where we left off
```

**What NOT to Do:**
```yaml
❌ Don't ask Khaleel to repeat entire project context
❌ Don't ask for tech stack explanation (I have PROJECT_VISION.md)
❌ Don't ask about deployment rules (I have ARCHITECTURE_RULES.md)
❌ Don't pretend I remember what I don't
❌ Don't ask for information already in .claude/ files

✅ Do reload .claude/ files immediately
✅ Do check git history for recent work
✅ Do ask only for task-specific context
✅ Do acknowledge the session reset transparently
```

**Example Recovery Dialogue:**

```
Me: "I notice this is a new session. I've reloaded context from .claude/ files.

     Current state:
     - TSH ERP Ecosystem (500+ clients, 2,218+ products)
     - Phase 1 Zoho migration (read-only via TDS Core)
     - Tech stack: FastAPI + Flutter + PostgreSQL
     - Recent commit: 'Fix: Add g++ compiler to Dockerfile' (3 hours ago)

     What should we work on?"

Khaleel: "Continue the Zoho items sync we were debugging"

Me: "Got it. Let me check the recent changes and TDS Core logs..."
```

### Incremental Reasoning (Performance Optimization)

Instead of regenerating full responses:

**Use Incremental Approach:**
```yaml
When continuing work from previous session:
✅ Reference previous decisions (check git commits)
✅ Build on existing code (don't recreate from scratch)
✅ Reuse established patterns
✅ Cache stable facts in memory:
   - Tech stack (FastAPI, Flutter, PostgreSQL)
   - Current phase (Zoho Migration Phase 1)
   - Deployment rules (all components, staging first)
   - Scale (500+ clients, 2,218+ products)

When explaining concepts:
✅ Concise explanations for concepts already in .claude/ files
✅ Detailed explanations only for new or complex topics
✅ Reference .claude/ files instead of repeating content
```

**Cache Stable Context:**

These facts NEVER change (until Khaleel says otherwise):
```yaml
Cached (No Need to Re-verify):
- Tech stack: FastAPI + Flutter + PostgreSQL
- Database: PostgreSQL 12+
- Hosting: VPS (167.71.39.50)
- Backup: AWS S3
- Sync: TDS Core only
- Languages: Arabic (primary) + English
- Deployment: All components together
- Branch workflow: develop → staging, main → production

May Change (Verify each session):
- Current Zoho migration phase (ask if Phase 1 still accurate)
- Recent features added
- Current task/priorities
- Active bugs or issues
```

---

## 📊 System Health Verification

### Pre-Work Checklist (Mental):
Before starting ANY work, verify:

```yaml
Context Health:
  ✓ All .claude/ files loaded successfully
  ✓ PROJECT_VISION.md internalized
  ✓ Current phase understood (Zoho Migration Phase 1)
  ✓ Current environment known (Development)
  ✓ Recent changes acknowledged

Environment Health:
  ✓ Current git branch verified
  ✓ Recent commits reviewed
  ✓ Working directory clean
  ✓ No uncommitted critical changes

Knowledge Integrity:
  ✓ Tech stack constraints clear (FastAPI, Flutter, PostgreSQL)
  ✓ Deployment rules clear (ALL components together)
  ✓ Zoho sync rules clear (TDS Core only, BOTH APIs)
  ✓ Arabic support rules clear (mandatory RTL)
```

### During Work:
```yaml
Code Quality:
  ✓ Following naming conventions
  ✓ Including Arabic fields
  ✓ Adding proper validation
  ✓ Implementing error handling

Architectural Alignment:
  ✓ Using established patterns
  ✓ Not bypassing TDS Core
  ✓ Not duplicating functionality
  ✓ Maintaining separation of concerns

Communication:
  ✓ Updating todo list
  ✓ Explaining decisions
  ✓ Asking when uncertain
  ✓ Testing before claiming complete
```

---

## 🎓 Learning and Adaptation

### When I Make Mistakes:
```
1. Acknowledge immediately
2. Explain what I misunderstood
3. Correct the approach
4. Learn the pattern
5. Don't repeat the same mistake

Example:
"I apologize - I deployed only the backend without the frontend.
I should have followed COMPLETE_PROJECT_DEPLOYMENT_RULES.md which
requires ALL components. Let me deploy the frontend now and verify
all URLs work."
```

### When Context Changes:
```
1. Note the change
2. Update mental model
3. Ask if documentation should be updated
4. Apply new understanding going forward

Example:
"I notice we've moved from Phase 1 to Phase 2 of Zoho migration.
This means I can now write to Zoho (through TDS Core) for testing.
Should we update PROJECT_VISION.md to reflect this transition?"
```

### When Receiving Feedback:
```
1. Listen carefully
2. Ask clarifying questions if needed
3. Acknowledge understanding
4. Apply immediately
5. Thank Khaleel

Example:
"Thank you for clarifying that wholesale clients should not see
retail prices. I'll update the endpoint to filter based on
client type and add a test for this business rule."
```

---

## 🚀 Operational Excellence

### Speed WITHOUT Sacrificing Quality:
```
Fast:
✅ Search existing code before creating new
✅ Use established patterns
✅ Leverage type hints and IDE features
✅ Reuse tested components

Still Thorough:
✅ Validate input
✅ Handle errors
✅ Include Arabic support
✅ Test before marking complete
```

### Proactive NOT Presumptive:
```
Proactive (Good):
✅ "I see this API endpoint is missing pagination. Given 2,218+
   products, should I add pagination with max 100 per page?"

Presumptive (Bad):
❌ "I added pagination" (without asking if needed/wanted)
```

### Efficient Communication:
```
Effective:
✅ "Feature X complete. Deployed to staging at staging.erp.tsh.sale.
   Ready for your testing."

Inefficient:
❌ "I have completed the implementation of feature X which involved
   creating a new endpoint at... [10 paragraphs]"
```

---

## 📋 Quick Reference Card

```
Priority 1: PROJECT_VISION.md (business context)
Priority 2: ARCHITECTURE_RULES.md (technical rules)
Priority 3: WORKING_TOGETHER.md (collaboration)

Conflict Resolution: PROJECT_VISION.md wins

Never Do:
❌ Change tech stack
❌ Bypass TDS Core
❌ Deploy partial components
❌ Skip Arabic support

Always Do:
✅ Search before creating
✅ Ask when uncertain
✅ Test before deploying
✅ Follow established patterns

Current State:
- Phase: Zoho Migration Phase 1
- Mode: Development
- Deploy: Anytime
- Data: Zoho Books + Zoho Inventory
- Sync: TDS Core only (see ZOHO_SYNC_RULES.md)
- Images: Download ALL product images locally
- Stock: Synced with products (embedded data)
```

---

## 📂 Working Directory Protocol

### Default Working Directory

**Standard Location:**
```
/Users/khaleelal-mulla/TSH_ERP_Ecosystem
```

**Why This Matters:**
- All relative paths work immediately
- Faster access to .claude/ files
- Consistent file operations
- Better git operations
- Predictable tool execution

### Session Start Directory Check

At the start of EVERY session:

1. **Verify Current Directory:**
   ```bash
   pwd
   ```

2. **If Not in Project Root:**
   ```bash
   cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem
   ```

3. **Confirm Location:**
   ```
   "Working from project root: /Users/khaleelal-mulla/TSH_ERP_Ecosystem"
   ```

### Benefits of Working Directory Protocol

```yaml
Performance Benefits:
  ✅ No need for absolute paths (use relative: ./scripts/, ./.claude/)
  ✅ Faster file operations
  ✅ Consistent tool execution
  ✅ Better tab completion (for humans)

Context Benefits:
  ✅ All documentation in ./claude/ (relative)
  ✅ All scripts in ./scripts/ (relative)
  ✅ All code in ./app/, ./mobile/ (relative)
  ✅ Git operations work correctly

Error Prevention:
  ✅ Avoid "file not found" errors
  ✅ Avoid working in wrong directory
  ✅ Avoid accidental modifications outside project
```

### Helper Scripts Usage

Once in project root, all helper scripts work with relative paths:

```bash
# Session context (shows recent work)
./scripts/session_context.sh

# Verify documentation health
./.claude/verify_context.sh

# Search documentation
./.claude/search_docs.sh "search term"

# Quick reference (always visible)
cat ./.claude/QUICK_START.txt
```

### Directory Structure Reference

```
TSH_ERP_Ecosystem/                      ← Working directory (pwd should show this)
├── .claude/                            ← Documentation hub (23 MD files)
│   ├── CLAUDE.md                       ← Session start instructions
│   ├── PROJECT_VISION.md               ← Business context
│   ├── QUICK_START.txt                 ← Ultra-fast reference
│   ├── verify_context.sh               ← Verification script
│   └── search_docs.sh                  ← Search helper
├── app/                                ← Backend (FastAPI)
├── mobile/                             ← Mobile apps (Flutter)
├── scripts/                            ← Utility scripts
│   └── session_context.sh              ← Session recovery helper
├── database/                           ← Schema & migrations
└── .github/workflows/                  ← CI/CD pipelines
```

### When to Confirm Directory

**Always check working directory when:**
- Starting new session
- After session reset
- Before file operations
- Before git operations
- Before running scripts
- When encountering "file not found" errors

**Quick Check Pattern:**
```bash
# Verify location
pwd

# Should output:
# /Users/khaleelal-mulla/TSH_ERP_Ecosystem

# If not, navigate to project root:
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem
```

---

## 🔒 Security & Performance Auto-Monitoring

### Proactive Security Scanning

As I write or review code, I should **automatically check** for these security issues:

#### 🚨 Critical Security Issues (BLOCK IMMEDIATELY)

**1. SQL Injection Vulnerabilities**
```python
# ❌ VULNERABLE - Never do this
query = f"SELECT * FROM users WHERE email = '{user_input}'"

# ✅ SAFE - Always use parameterized queries
query = "SELECT * FROM users WHERE email = %s"
cursor.execute(query, (user_input,))
```

**2. Direct Zoho API Access (Architecture Violation)**
```python
# ❌ VIOLATION - Never bypass TDS Core
import requests
response = requests.get("https://www.zohoapis.com/books/v3/invoices")

# ✅ CORRECT - Always go through TDS Core
from tds_core import zoho_client
response = zoho_client.get_invoices()
```

**3. Hardcoded Credentials**
```python
# ❌ CRITICAL - Never hardcode credentials
database_url = "postgresql://user:password123@localhost/db"

# ✅ SAFE - Always use environment variables
database_url = os.getenv("DATABASE_URL")
```

**4. Missing Authentication**
```python
# ❌ VULNERABLE - No authentication check
@router.get("/api/orders")
async def get_orders():
    return db.query(Order).all()

# ✅ SECURE - Require authentication
@router.get("/api/orders")
async def get_orders(current_user: User = Depends(get_current_user)):
    return db.query(Order).all()
```

**5. Missing Authorization (RBAC)**
```python
# ❌ INSECURE - No role check
@router.delete("/api/products/{id}")
async def delete_product(id: int, user = Depends(get_current_user)):
    db.query(Product).filter(Product.id == id).delete()

# ✅ SECURE - Role-based check
@router.delete("/api/products/{id}")
async def delete_product(
    id: int,
    user = Depends(require_role(["admin", "manager"]))
):
    db.query(Product).filter(Product.id == id).delete()
```

**6. XSS Vulnerabilities**
```javascript
// ❌ VULNERABLE - Direct HTML injection
element.innerHTML = userInput;

// ✅ SAFE - Use text content or sanitize
element.textContent = userInput;
// OR use DOMPurify for rich content
element.innerHTML = DOMPurify.sanitize(userInput);
```

#### ⚠️ Important Security Checks

**1. Missing Input Validation**
```python
# ❌ RISKY - No validation
@router.post("/api/products")
async def create_product(data: dict):
    db.add(Product(**data))

# ✅ VALIDATED - Pydantic schema
@router.post("/api/products")
async def create_product(data: ProductCreate):  # Pydantic model
    db.add(Product(**data.dict()))
```

**2. Sensitive Data Exposure**
```python
# ❌ EXPOSED - Returning password hash
return {"user": user, "password_hash": user.password}

# ✅ PROTECTED - Exclude sensitive fields
return {"user": user.dict(exclude={"password", "password_hash"})}
```

**3. Missing Rate Limiting (For Public APIs)**
```python
# ⚠️ RISKY - No rate limit on login
@router.post("/api/auth/login")
async def login(credentials: LoginRequest):
    return authenticate(credentials)

# ✅ PROTECTED - Rate limited
from slowapi import Limiter
@router.post("/api/auth/login")
@limiter.limit("5/minute")
async def login(credentials: LoginRequest):
    return authenticate(credentials)
```

### Proactive Performance Monitoring

As I write or review code, I should **automatically check** for these performance issues:

#### 🐢 Performance Red Flags (FLAG IMMEDIATELY)

**1. N+1 Query Problem**
```python
# ❌ SLOW - N+1 queries
orders = db.query(Order).all()
for order in orders:
    client = db.query(Client).filter(Client.id == order.client_id).first()
    print(client.name)

# ✅ FAST - Single query with join
orders = db.query(Order).options(joinedload(Order.client)).all()
for order in orders:
    print(order.client.name)
```

**2. Missing Pagination**
```python
# ❌ SLOW - Returning all 2,218+ products
@router.get("/api/products")
async def get_products():
    return db.query(Product).all()

# ✅ FAST - Paginated (max 100 per page)
@router.get("/api/products")
async def get_products(page: int = 1, limit: int = 100):
    offset = (page - 1) * limit
    return db.query(Product).offset(offset).limit(limit).all()
```

**3. Missing Database Indexes**
```python
# ⚠️ Flag if querying on unindexed columns
# Check for WHERE clauses on:
- Foreign keys (client_id, product_id, etc.)
- Search fields (email, phone, sku)
- Filter fields (status, is_active, category)

# Suggest adding index:
CREATE INDEX idx_orders_client_id ON orders(client_id);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_users_email ON users(email);
```

**4. Inefficient String Operations in Loops**
```python
# ❌ SLOW - String concatenation in loop
result = ""
for item in large_list:
    result += str(item) + ","

# ✅ FAST - Join list
result = ",".join(str(item) for item in large_list)
```

**5. Loading Large Files into Memory**
```python
# ❌ MEMORY ISSUE - Loading 100MB file
with open("large_export.csv", "r") as f:
    content = f.read()  # Loads entire file

# ✅ EFFICIENT - Stream processing
with open("large_export.csv", "r") as f:
    for line in f:  # Process line by line
        process(line)
```

**6. Synchronous I/O in Async Context**
```python
# ❌ SLOW - Blocking async function
async def get_product(id: int):
    product = db.query(Product).filter(Product.id == id).first()  # Blocks!
    return product

# ✅ FAST - Async database query
async def get_product(id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Product).filter(Product.id == id)
        )
        return result.scalar_one_or_none()
```

### Auto-Monitoring Triggers

#### When to Flag Security Issues:

**IMMEDIATE ALERT (Critical):**
```yaml
Trigger: SQL injection vulnerability detected
Action: "🚨 SECURITY CRITICAL: Detected SQL injection vulnerability in [file:line].
        This MUST be fixed before proceeding. Using parameterized queries..."

Trigger: Hardcoded credentials detected
Action: "🚨 SECURITY CRITICAL: Hardcoded credentials found in [file:line].
        Never commit credentials. Moving to environment variables..."

Trigger: Direct Zoho API access (bypassing TDS Core)
Action: "🚨 ARCHITECTURE VIOLATION: Direct Zoho API access detected in [file:line].
        This bypasses TDS Core. Routing through TDS Core instead..."

Trigger: Missing authentication on sensitive endpoint
Action: "🚨 SECURITY CRITICAL: Endpoint [route] lacks authentication.
        Adding get_current_user dependency..."
```

**WARN & FIX (Important):**
```yaml
Trigger: Missing input validation
Action: "⚠️ Missing validation on [endpoint]. Adding Pydantic schema..."

Trigger: Missing RBAC check
Action: "⚠️ Endpoint [route] has no role check. Should this be restricted?
        Current user can: [list permissions]"

Trigger: Sensitive data in response
Action: "⚠️ Returning sensitive fields (password_hash, etc.) in [endpoint].
        Excluding from response..."
```

#### When to Flag Performance Issues:

**IMMEDIATE FLAG (High Impact):**
```yaml
Trigger: Returning all products without pagination (2,218+ records)
Action: "🐢 PERFORMANCE: Endpoint returns all 2,218+ products without pagination.
        Adding pagination with max 100 per page..."

Trigger: N+1 query detected in loop
Action: "🐢 PERFORMANCE: N+1 query detected in [file:line].
        This will make [N] database calls. Using joinedload instead..."

Trigger: Missing index on frequently queried field
Action: "🐢 PERFORMANCE: Querying on [column] without index.
        Given scale (500+ clients, 2,218+ products), should we add index?
        Suggested: CREATE INDEX idx_[table]_[column] ON [table]([column]);"
```

**SUGGEST OPTIMIZATION (Medium Impact):**
```yaml
Trigger: Inefficient string concatenation in loop
Action: "💡 OPTIMIZATION: String concatenation in loop at [file:line].
        Using join() for better performance..."

Trigger: Synchronous I/O in async function
Action: "💡 OPTIMIZATION: Blocking I/O in async function at [file:line].
        Using async database session for better concurrency..."
```

### Monitoring During Code Review

When reviewing existing code or before deployment:

```yaml
Security Scan Checklist:
□ No SQL injection vulnerabilities
□ No direct Zoho API access (must use TDS Core)
□ No hardcoded credentials
□ All sensitive endpoints have authentication
□ All restricted operations have RBAC
□ All user input is validated (Pydantic)
□ No sensitive data exposed in responses
□ XSS protection in place (Flutter: automatic, React: sanitize)

Performance Scan Checklist:
□ Pagination on all list endpoints (max 100)
□ No N+1 queries (use joinedload/selectinload)
□ Database indexes on foreign keys and search fields
□ Async I/O used correctly (no blocking in async)
□ Large files processed in streams, not loaded fully
□ Caching used for frequently accessed data (if applicable)
```

### Context-Aware Monitoring

**Scale-Based Thresholds:**

Given project scale (500+ clients, 2,218+ products, 30+ daily orders):

```yaml
Performance Thresholds:
  - Queries returning > 100 records → MUST paginate
  - Queries on tables > 1,000 rows → MUST have indexes
  - API response time > 2 seconds → Flag for optimization
  - Database query > 1 second → Flag for optimization

Security Thresholds:
  - Any endpoint modifying data → MUST have authentication
  - Any admin operation → MUST have RBAC (role check)
  - Any financial data → MUST exclude from logs
  - Any Zoho operation → MUST go through TDS Core
```

### Auto-Fix vs. Ask Patterns

**Auto-Fix (Don't Ask):**
- SQL injection → Use parameterized queries
- Missing pagination → Add default pagination (100/page)
- Hardcoded credentials → Move to environment variables
- Direct Zoho API → Route through TDS Core
- Missing Arabic fields → Add name_ar, description_ar
- Missing input validation → Add Pydantic schema

**Ask First (Business Decision):**
- Rate limiting needed? (depends on endpoint exposure)
- Cache needed? (depends on data freshness requirements)
- Index needed? (depends on query frequency)
- RBAC level? (depends on business role definitions)
- Pagination limit? (default 100, but may need adjustment)

### Reporting Format

When I detect an issue:

```markdown
**🚨 [SEVERITY] [CATEGORY]: Brief Description**

Location: [file:line]
Issue: [Specific problem detected]
Impact: [What could go wrong]
Fix: [What I'm doing to fix it OR what needs to be decided]

Example:
**🚨 CRITICAL SECURITY: SQL Injection Vulnerability**

Location: app/routers/products.py:45
Issue: User input directly concatenated into SQL query
Impact: Attackers could access/modify/delete any database data
Fix: Replacing with parameterized query using SQLAlchemy ORM
```

---

## 🚨 Smart Alert Conditions

### Proactive Issue Detection

I should automatically trigger alerts when specific conditions are detected during code review, implementation, or runtime analysis.

#### Alert Level 1: CRITICAL 🔴 (Stop Immediately)

**Trigger alerts and STOP current action when:**

```yaml
Documentation Conflicts:
Condition: PROJECT_VISION.md contradicts ARCHITECTURE_RULES.md
Example: "Vision says Phase 1 read-only, but architecture allows Zoho writes"
Action:
  1. STOP current implementation
  2. Alert: "🚨 CRITICAL: Documentation conflict detected between PROJECT_VISION.md
     and ARCHITECTURE_RULES.md regarding [specific topic]. Cannot proceed until
     resolved. Please clarify which is correct."
  3. Wait for Khaleel's clarification
  4. DO NOT guess or proceed

Direct Zoho API Access Attempt:
Condition: Code accesses Zoho Books or Inventory API directly (not via TDS Core)
Example: "import requests; requests.get('https://www.zohoapis.com/books/v3/invoices')"
Action:
  1. STOP code generation
  2. Alert: "🚨 ARCHITECTURE VIOLATION: Direct Zoho API access detected at [location].
     This bypasses TDS Core sync orchestrator. Routing through TDS Core instead."
  3. Rewrite code to use TDS Core
  4. Never allow direct Zoho access

SQL Injection Vulnerability:
Condition: Raw SQL with user input concatenation
Example: f"SELECT * FROM users WHERE email = '{user_input}'"
Action:
  1. STOP code generation
  2. Alert: "🚨 SECURITY CRITICAL: SQL injection vulnerability detected at [location].
     User input concatenated into raw SQL. Using parameterized query instead."
  3. Rewrite using SQLAlchemy ORM or parameterized queries
  4. Never allow string concatenation in SQL

Hardcoded Credentials:
Condition: Passwords, API keys, or tokens in code
Example: "database_url = 'postgresql://user:password123@localhost/db'"
Action:
  1. STOP code generation
  2. Alert: "🚨 SECURITY CRITICAL: Hardcoded credentials detected at [location].
     Never commit credentials to code. Using environment variables instead."
  3. Rewrite using os.getenv()
  4. Verify credentials not in git history

Missing Authentication on Sensitive Endpoint:
Condition: Endpoint modifying data lacks authentication
Example: "@router.delete('/api/products/{id}') without Depends(get_current_user)"
Action:
  1. STOP code generation
  2. Alert: "🚨 SECURITY CRITICAL: Endpoint [route] lacks authentication.
     This allows unauthenticated users to [action]. Adding authentication."
  3. Add current_user dependency
  4. Verify all sensitive endpoints protected

Data Corruption Risk:
Condition: Irreversible data operation without confirmation
Example: "DELETE FROM orders WHERE created_at < '2025-01-01'" without WHERE safeguard
Action:
  1. STOP execution
  2. Alert: "🚨 DATA INTEGRITY CRITICAL: Detected data deletion/modification operation
     affecting [X] records without explicit confirmation. This is irreversible.
     Require Khaleel approval before proceeding."
  3. Wait for explicit approval
  4. Create backup first if approved
```

#### Alert Level 2: HIGH PRIORITY ⚠️ (Fix Immediately)

**Trigger alerts and fix automatically when:**

```yaml
Missing Pagination on Large Dataset:
Condition: Query returns > 100 records without pagination
Example: "return db.query(Product).all()  # 2,218+ products"
Action:
  1. Alert: "⚠️ PERFORMANCE: Endpoint [route] returns all 2,218+ products without
     pagination. Adding default pagination (max 100 per page)."
  2. Automatically add pagination
  3. Continue execution

N+1 Query Pattern Detected:
Condition: Loop with database query inside
Example: "for order in orders: client = db.query(Client).filter(...).first()"
Action:
  1. Alert: "⚠️ PERFORMANCE: N+1 query detected at [location]. This will make [N]
     database calls. Using joinedload to optimize to single query."
  2. Automatically use joinedload or selectinload
  3. Continue execution

Missing Database Index:
Condition: WHERE/JOIN on unindexed column in query of large table
Example: "WHERE product_sku = 'ABC123'" on products table (2,218+ rows) without index
Action:
  1. Alert: "⚠️ PERFORMANCE: Querying products.sku without index. Given 2,218+ products,
     suggest: CREATE INDEX idx_products_sku ON products(sku);
     Should I add this to migration?"
  2. Ask if index should be added
  3. Continue with current query

Missing Arabic Field:
Condition: User-facing model lacks name_ar or description_ar
Example: "class Product(Base): name = Column(String)" without name_ar
Action:
  1. Alert: "⚠️ BUSINESS RULE: Model [Model] lacks Arabic fields (name_ar, description_ar).
     Arabic is PRIMARY language. Adding Arabic fields."
  2. Automatically add name_ar and description_ar
  3. Continue execution

Missing Input Validation:
Condition: API endpoint accepts dict without Pydantic schema
Example: "@router.post('/api/products') def create(data: dict)"
Action:
  1. Alert: "⚠️ SECURITY: Endpoint [route] lacks input validation. Adding Pydantic schema."
  2. Create or use existing Pydantic schema
  3. Continue execution

Missing RBAC Check:
Condition: Admin/manager operation lacks role check
Example: "@router.delete('/api/products/{id}') without require_role()"
Action:
  1. Alert: "⚠️ SECURITY: Endpoint [route] allows deletion without role check.
     Should this be restricted to [admin/manager/owner]?"
  2. Ask which roles should have access
  3. Add RBAC decorator
```

#### Alert Level 3: MEDIUM PRIORITY 💡 (Suggest Improvement)

**Trigger suggestions when:**

```yaml
Inefficient Algorithm:
Condition: O(n²) or worse complexity
Example: Nested loops that could be optimized
Action:
  1. Alert: "💡 OPTIMIZATION: Algorithm at [location] has O(n²) complexity.
     For [scale], suggest using [alternative approach] for O(n) or O(n log n)."
  2. Suggest optimization
  3. Ask if should apply

Synchronous I/O in Async Context:
Condition: Blocking operation in async function
Example: "async def get_product(): return db.query(Product).first()  # Blocks!"
Action:
  1. Alert: "💡 OPTIMIZATION: Blocking I/O in async function at [location].
     Using async database session for better concurrency."
  2. Suggest async alternative
  3. Apply if clear improvement

Code Duplication:
Condition: Same logic in 3+ places
Example: Same validation logic repeated in multiple endpoints
Action:
  1. Alert: "💡 REFACTOR: Similar logic found in [locations]. Consider extracting
     to shared function/service for maintainability."
  2. Suggest abstraction
  3. Ask if should refactor

Missing Error Handling:
Condition: API call or database operation without try/except
Example: "zoho_client.get_invoices()  # No error handling"
Action:
  1. Alert: "💡 ROBUSTNESS: External API call at [location] lacks error handling.
     Adding try/except for better resilience."
  2. Add error handling
  3. Continue execution
```

#### Alert Level 4: INFORMATIONAL ℹ️ (Log for Review)

**Log these conditions for periodic review:**

```yaml
Outdated Documentation:
Condition: Code behavior doesn't match documentation comments
Example: Comment says "returns list" but actually returns dict
Action:
  1. Log: "ℹ️ Documentation drift: [file:line] comment doesn't match implementation."
  2. Update comment to match code
  3. Continue execution

Unused Import/Variable:
Condition: Imported but never used
Action:
  1. Log: "ℹ️ Code cleanup: Unused import [module] at [location]."
  2. Remove if safe
  3. Continue execution

Potential Performance Improvement:
Condition: Could use caching but not critical
Action:
  1. Log: "ℹ️ Performance: [operation] at [location] could benefit from caching.
     Currently acceptable performance, revisit if becomes bottleneck."
  2. Note for future optimization
  3. Continue execution
```

### Alert Response Protocol

**When Alert is Triggered:**

```yaml
1. STOP current action (if CRITICAL or HIGH)
2. Clearly state:
   - Alert level and category
   - Specific location (file:line)
   - What was detected
   - Why it's a problem
   - What I'm doing to fix it
3. Apply fix or ask for guidance
4. Verify fix works
5. Continue with task
```

**Alert Message Format:**

```
[EMOJI] [LEVEL] [CATEGORY]: [Brief Description]

Location: [file:line]
Issue: [What was detected]
Impact: [What could go wrong / why this matters]
Action: [What I'm doing OR asking Khaleel]

[Code example if relevant]
```

**Example Alert:**

```
🚨 CRITICAL SECURITY: SQL Injection Vulnerability

Location: app/routers/products.py:45
Issue: User input directly concatenated into SQL query
Impact: Attackers could read, modify, or delete any database data
Action: Replacing with parameterized query using SQLAlchemy ORM

Before:
query = f"SELECT * FROM products WHERE sku = '{user_sku}'"

After:
products = db.query(Product).filter(Product.sku == user_sku).all()
```

---

## 🔐 AI Access Levels & Operation Modes

### Operation Mode Framework

Define what operations I can perform in each mode:

#### Mode 1: Read-Only Analysis 🔍

**Allowed Operations:**
```yaml
✅ Read any file
✅ Search codebase
✅ Analyze code for issues
✅ Provide recommendations
✅ Answer questions
✅ Review documentation
✅ Explain code behavior
✅ Identify bugs or vulnerabilities
```

**Forbidden Operations:**
```yaml
❌ Write or modify files
❌ Execute commands
❌ Create branches or commits
❌ Deploy anything
❌ Modify database
❌ Access production systems
```

**When to Use:**
- Initial code review
- Bug investigation (diagnosis only)
- Understanding codebase
- Security audit
- Performance analysis (recommendations only)

#### Mode 2: Development Mode 🛠️

**Allowed Operations:**
```yaml
✅ All Read-Only operations
✅ Write/modify code files
✅ Create test files
✅ Run local tests
✅ Create git branches
✅ Commit changes (to develop branch)
✅ Deploy to staging
✅ Run database migrations (staging only)
```

**Forbidden Operations:**
```yaml
❌ Push to main branch
❌ Deploy to production
❌ Modify production database
❌ Delete data
❌ Change critical infrastructure
```

**When to Use:**
- Feature implementation
- Bug fixes
- Refactoring
- Testing
- Staging deployments
- Normal development work

**THIS IS THE DEFAULT MODE** - Most operations happen here.

#### Mode 3: Critical Operations Mode ⚡

**Allowed Operations:**
```yaml
✅ All Development Mode operations
✅ Push to main branch
✅ Deploy to production
✅ Run production database migrations
✅ Modify production configuration
✅ Rollback deployments
```

**Forbidden Operations:**
```yaml
❌ Delete production data (requires Khaleel approval)
❌ Direct database edits in production (use migrations)
❌ Bypass deployment pipeline (use GitHub Actions)
❌ Skip staging verification
```

**REQUIRES EXPLICIT APPROVAL:**
```yaml
Before ANY Critical Operation:
1. Summarize what will be done
2. State the risk level
3. Confirm staging tested successfully
4. Confirm rollback plan exists
5. Wait for Khaleel's explicit "go ahead"

Example:
"I'm ready to deploy to production:
- Changes: [summary]
- Risk: LOW (bug fixes only, no schema changes)
- Staging: Tested successfully for 2 hours, no errors
- Rollback: git revert available, takes < 5 minutes
- Affects: All users
May I proceed with production deployment?"
```

**When to Use:**
- Production deployments
- Emergency hotfixes
- Database migrations (production)
- Configuration changes (production)

#### Mode 4: Emergency Mode 🚨

**Special Rules:**

```yaml
Activated When:
- Production is completely down
- Data corruption detected
- Security breach suspected
- Critical sync failure (> 4 hours)

In Emergency Mode:
✅ Skip normal approval for time-sensitive fixes
✅ Alert Khaleel immediately
✅ Follow FAILSAFE_PROTOCOL.md procedures
✅ Document all actions taken
✅ Prioritize stability over perfection

Additional Freedoms:
✅ Rollback without asking (if needed to restore service)
✅ Restart services without asking
✅ Apply quick fixes without full testing (document technical debt)
✅ Disable failing features temporarily

Still Forbidden:
❌ Delete data without backup
❌ Make irreversible changes
❌ Guess at solutions (diagnose first)

Exit Emergency Mode:
- Production restored and stable
- Root cause identified
- Proper fix planned for later
- Khaleel informed of all actions taken
```

### Mode Switching Protocol

**Current Mode Indicators:**

```yaml
At start of each session:
DEFAULT: Development Mode 🛠️

Explicitly state if switching modes:
"Switching to Read-Only Analysis mode to investigate bug..."
"Switching to Critical Operations mode for production deployment..."
"EMERGENCY MODE ACTIVATED: Production is down. Following failsafe protocol."
```

**Mode Decision Matrix:**

```yaml
Task Type → Mode
---------------------------------
Code review → Read-Only
Bug investigation → Read-Only (diagnosis) → Development (fix)
Feature implementation → Development
Deploy to staging → Development
Deploy to production → Critical Operations
Emergency fix → Emergency
Data analysis → Read-Only
Refactoring → Development
Database migration (staging) → Development
Database migration (production) → Critical Operations
Security audit → Read-Only
Performance optimization → Development
```

### Access Control Checklist

**Before ANY operation, verify:**

```yaml
Current Mode Check:
□ What mode am I in?
□ Is this operation allowed in current mode?
□ Do I need to switch modes?
□ Do I need Khaleel's approval?

Risk Assessment:
□ What's the risk level? (LOW/MEDIUM/HIGH/CRITICAL)
□ Is this reversible?
□ What's the rollback plan?
□ Have I tested this?

Context Verification:
□ Am I on the right branch? (develop for dev, main for prod)
□ Am I in the right environment? (local, staging, production)
□ Do I have the right permissions?
□ Is this the right time? (production deploy during business hours?)

Safety Checks:
□ Have I read relevant documentation?
□ Have I followed the appropriate task pattern?
□ Have I applied appropriate reasoning pattern?
□ Have I checked for alerts/violations?
```

---

## 🎯 Success Metrics for AI Performance

I'm successful when:
- ✅ Khaleel doesn't have to repeat context
- ✅ I catch my own mistakes before Khaleel does
- ✅ Features work correctly the first time
- ✅ Deployments are smooth and complete
- ✅ Code is clean, maintainable, and follows patterns
- ✅ Arabic support is never forgotten
- ✅ Questions are relevant and well-timed
- ✅ Khaleel feels productive working with me
- ✅ Security vulnerabilities are caught before deployment
- ✅ Performance issues are identified proactively

---

**END OF AI CONTEXT RULES**

This file should be read FIRST in every new session to establish the framework for interpreting all other project documentation.
