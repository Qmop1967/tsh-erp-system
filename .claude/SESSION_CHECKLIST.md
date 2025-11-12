# Session Checklist - Practical Performance Metrics

**Purpose:** Simple, actionable checklist for every session with measurable success criteria.

**Last Updated:** 2025-11-12

---

## 🚀 Session Start (0-2 minutes)

### Rapid Context Load
```yaml
□ Read AI_CONTEXT_RULES.md (know how to interpret files)
□ Read PROJECT_VISION.md (business context internalized)
□ Check current git branch (develop, feature/*, or main)
□ Review last 3 commits (git log --oneline -3)
□ Verify working directory clean (git status)
```

**Success Criteria:** ✅ Completed in < 2 minutes, ready to work

---

## 💬 Communication Check

### First Interaction
```yaml
□ Greet Khaleel professionally
□ Confirm current project phase (Zoho Migration Phase 1)
□ Ask what we're working on today
□ Listen to full request before responding
```

**Good First Message:**
```
"Hi Khaleel! I've loaded the TSH ERP context. We're in Zoho Migration
Phase 1 (read-only sync from Books + Inventory via TDS Core).
What would you like to work on today?"
```

**Bad First Message:**
```
"Hello! I've read PROJECT_VISION.md which says you have 500+ clients
and 2,218+ products and you're using FastAPI with Flutter and..."
```

---

## 🎯 Task Initiation

### Before Starting Work
```yaml
□ Clarify requirements (ask 1-3 questions if unclear)
□ Search existing code FIRST (don't create duplicates)
□ Create todo list if task has 3+ steps
□ Confirm understanding with Khaleel
```

**Decision Tree:**
```
Is requirement 100% clear?
├─ YES → Search existing code
└─ NO → Ask clarifying questions (max 3)

Does similar functionality exist?
├─ YES → Enhance existing (PREFERRED)
└─ NO → Create new (only if necessary)

Is task complex (3+ steps)?
├─ YES → Create todo list
└─ NO → Execute directly
```

---

## 🔍 Code Search Protocol (MANDATORY)

### Before Creating Anything New
```bash
# Step 1: Search for similar files
find . -name "*keyword*" -type f | grep -v node_modules | grep -v .git

# Step 2: Search for similar functions
grep -r "def similar_function" app/ --include="*.py"

# Step 3: Search for similar patterns
grep -r "class SimilarModel" app/models/ --include="*.py"

# Step 4: Check existing endpoints
grep -r "@router" app/routers/ --include="*.py"
```

**Checklist:**
```yaml
□ Searched for similar files (find command)
□ Searched for similar functions (grep in /app/)
□ Searched for similar patterns (grep in /models/)
□ Searched existing API endpoints (grep in /routers/)
□ Confirmed: No duplicate functionality exists
```

**Only proceed with NEW code if all searches return no suitable existing code.**

---

## 📝 Implementation Quality Gates

### While Writing Code

#### ✅ **MUST HAVE** (Non-Negotiable)
```yaml
□ Arabic support included (name_ar, description_ar fields)
□ Input validation (Pydantic schemas)
□ Error handling (try/except with proper logging)
□ Type hints (all function parameters and returns)
□ Authentication check (current_user dependency)
□ Role-based authorization (RBAC decorator if needed)
```

#### ✅ **SHOULD HAVE** (Strongly Recommended)
```yaml
□ Database transaction handling (commit/rollback)
□ Pagination for lists (max 100 items per page)
□ Logging for important operations
□ Clear variable names (self-documenting code)
□ Business logic in /services/ not /routers/
```

#### ✅ **NICE TO HAVE** (If Time Permits)
```yaml
□ Unit tests for business logic
□ API documentation (docstrings)
□ Performance optimization (if needed)
□ Code comments for complex logic
```

---

## 🧪 Testing Protocol

### Before Marking Task Complete

#### Backend (FastAPI) Changes
```yaml
□ Syntax check (python -m py_compile file.py)
□ Import check (can the module be imported?)
□ Database migration (if models changed)
□ Manual endpoint test (curl or Postman)
□ Check logs for errors
```

#### Frontend (React/Flutter) Changes
```yaml
□ Syntax check (build command)
□ Console errors check (browser/Flutter DevTools)
□ UI renders correctly
□ Arabic RTL layout works
□ Mobile responsive (Flutter: test on web)
```

#### TDS Core / Background Job Changes
```yaml
□ Syntax check
□ Test run with sample data
□ Check TDS dashboard for errors
□ Verify Zoho API not accessed directly (must go through TDS Core)
```

---

## 🚨 Critical Violations Check (NEVER SKIP)

### Before ANY Commit
```yaml
□ NO direct Zoho API calls (MUST use TDS Core)
□ NO write operations to Zoho in Phase 1 (read-only)
□ NO missing Arabic fields (name_ar, description_ar)
□ NO bypassing authentication
□ NO ignoring RBAC (role checks)
□ NO skipping input validation
□ NO hardcoded credentials
□ NO SQL injection vulnerabilities (use parameterized queries)
```

**If ANY violation detected: STOP and FIX immediately.**

---

## ✅ Output Validation (Before Marking Complete)

### Consolidated Quality Gates

**Before marking ANY task as complete, verify ALL applicable criteria:**

#### 1. Logical Coherence & Correctness

```yaml
Code Logic:
□ Logic is sound and achieves intended purpose
□ No obvious bugs or flaws
□ Edge cases handled (null values, empty lists, invalid input)
□ Error conditions handled gracefully
□ No infinite loops or potential deadlocks
□ No race conditions (for concurrent operations)

Business Logic:
□ Implements correct business rules
□ Calculations are accurate (pricing, commissions, taxes)
□ Workflow follows business process correctly
□ State transitions are valid
□ Data integrity maintained

Algorithm Efficiency:
□ Algorithm complexity acceptable for scale (O(n) or O(n log n) preferred)
□ No unnecessary nested loops (O(n²) avoided if possible)
□ Appropriate data structures used (dict for lookups, list for sequences)
□ Database queries optimized (no N+1 queries)
```

#### 2. Architecture & Pattern Compliance

```yaml
Architectural Rules:
□ Follows patterns from ARCHITECTURE_RULES.md
□ Tech stack constraints respected (FastAPI, Flutter, PostgreSQL)
□ Separation of concerns maintained:
  - /routers/ = API endpoints only
  - /services/ = business logic
  - /models/ = database models
  - /schemas/ = Pydantic schemas
□ No direct Zoho API access (must use TDS Core)
□ Authentication via Depends(get_current_user)
□ Authorization via require_role() decorator

Code Quality:
□ DRY principle (no duplicate code in 3+ places)
□ Clear variable/function names (self-documenting)
□ Appropriate abstraction level
□ No magic numbers (use constants)
□ No commented-out code (remove or explain)
□ Type hints on all functions (def func(x: int) -> str:)
```

#### 3. Bilingual & Localization

```yaml
Arabic Language Support:
□ name_ar field included (if name field exists)
□ description_ar field included (if description field exists)
□ address_ar field included (if address field exists)
□ All user-facing text has Arabic equivalent
□ Database schema includes Arabic columns
□ API responses include Arabic fields

UI/UX Considerations:
□ RTL layout works correctly (Arabic)
□ LTR layout works correctly (English)
□ Both languages testable and functional
□ Arabic text displays correctly (UTF-8 encoding)
□ No hardcoded English-only text in UI
□ Language switching works (if applicable)
```

#### 4. Scalability for TSH ERP Scale

```yaml
Client Scale (500+ wholesale clients):
□ Works with 500+ clients in database
□ Client list paginated (max 100 per page)
□ Client searches use database indexes
□ No performance degradation at current scale

Product Scale (2,218+ products):
□ Works with 2,218+ products in database
□ Product list paginated (max 100 per page)
□ Product searches use database indexes
□ Inventory operations efficient at this scale

Order Volume (30+ daily orders):
□ Order creation handles concurrent requests
□ Order processing doesn't block other operations
□ Database transactions prevent race conditions
□ Audit trail maintained for all orders

Future Scale (10x growth):
□ Algorithm scales to 5,000+ clients
□ Database queries scale to 20,000+ products
□ Performance acceptable at 10x current load
□ No hardcoded limits that break at scale
```

#### 5. Security & Data Integrity

```yaml
Authentication & Authorization:
□ Sensitive endpoints require authentication
□ Admin operations require role check (RBAC)
□ Data modification operations verify ownership
□ API tokens/sessions validated properly

Input Validation:
□ All user input validated (Pydantic schemas)
□ SQL injection prevented (parameterized queries)
□ XSS prevented (sanitized output)
□ File uploads validated (type, size, content)

Data Protection:
□ No credentials in code (use environment variables)
□ No sensitive data in logs (passwords, tokens)
□ No sensitive data in API responses (password hashes)
□ Database connections secure (SSL if applicable)
□ Data deletion/modification has safeguards

Zoho Sync Integrity:
□ NO direct Zoho API access (must use TDS Core)
□ Read-only operations in Phase 1 (no writes to Zoho)
□ Data sync maintains referential integrity
□ Sync errors handled gracefully
```

#### 6. Testing & Verification

```yaml
Manual Testing:
□ Feature works as expected (happy path)
□ Edge cases tested (empty data, max values, invalid input)
□ Error cases tested (network failure, invalid data)
□ Multiple user roles tested (if applicable)
□ Arabic language tested (if UI changes)

Integration Testing:
□ API endpoints respond correctly (status codes, data format)
□ Database operations work (create, read, update, delete)
□ Frontend displays data correctly
□ Mobile apps work (if applicable)

Performance Testing:
□ Response time acceptable (< 500ms for normal operations)
□ Database queries fast (< 1 second)
□ Pagination works correctly
□ No memory leaks (for long-running processes)

Staging Verification:
□ Deployed to staging successfully
□ Tested on staging environment
□ No errors in staging logs
□ All health checks pass
```

#### 7. Documentation & Maintainability

```yaml
Code Documentation:
□ Docstrings on functions/classes (what it does, params, returns)
□ Complex logic explained with comments
□ Business context documented (why this logic exists)
□ TODO comments removed or tracked

API Documentation:
□ OpenAPI/Swagger docs accurate
□ Request/response examples clear
□ Authentication requirements documented
□ Error responses documented

Knowledge Transfer:
□ No "magic" code that only I understand
□ Future developers can maintain this
□ Patterns are clear and consistent
□ Dependencies documented (why library X chosen)
```

#### 8. Deployment Readiness

```yaml
Pre-Deployment:
□ All code committed (git status clean)
□ Commit message clear (follows conventional commits)
□ Requirements.txt updated (if new packages)
□ Database migration created (if schema changes)
□ Environment variables documented (if new ones added)

Rollback Plan:
□ Change is reversible (can rollback if needed)
□ Database migration reversible (down migration exists)
□ Rollback time estimated (< 5 minutes ideal)
□ Data loss risk assessed (none or acceptable)

Monitoring:
□ Logs will capture errors
□ Metrics will show performance
□ Alerts configured (if critical feature)
□ TDS Dashboard will show sync status (if Zoho-related)
```

### Output Validation Checklist Summary

**Quick Validation:**
```yaml
□ Logic is correct and handles edge cases
□ Follows ARCHITECTURE_RULES.md patterns
□ Arabic support included (name_ar, description_ar)
□ Scales to 500+ clients, 2,218+ products, 30+ daily orders
□ Security checks passed (auth, validation, no Zoho bypass)
□ Tested manually and verified on staging
□ Documented (docstrings, comments)
□ Deployment ready (committed, migrated, rollback plan)
```

**If ANY criterion fails: FIX before marking complete.**

### Human-Readable & Clarity Check

**Ask yourself:**
```yaml
Clarity Questions:
□ Can Khaleel understand what this does? (business owner perspective)
□ Can future developers understand this? (maintainability)
□ Can users understand the UI/error messages? (usability)
□ Is the API response intuitive? (developer experience)

Readability:
□ Code reads like prose (clear intent)
□ Variable names are descriptive (not x, y, tmp)
□ Function names describe action (get_active_products, not gp)
□ No abbreviations unless obvious (id ok, usr not ok)
□ Consistent style throughout
```

### Final Validation Statement

**Before marking task complete, mentally state:**

```
"I have verified:
✓ Logic is correct and efficient
✓ Architecture rules followed
✓ Arabic support included
✓ Scales to current + 10x volume
✓ Security checks passed
✓ Tested and works on staging
✓ Documented for future maintainers
✓ Ready for production deployment

This output is production-ready and meets all quality standards."
```

**Only mark complete if you can honestly make this statement.**

---

## 🚀 Deployment Checklist

### Before Deploying to Staging (develop branch)

#### Pre-Deployment Verification
```yaml
□ All code changes committed
□ Git status clean (no uncommitted files)
□ Requirements.txt updated (if new packages added)
□ .env file checked (no sensitive data in git)
□ Migrations created (if database changed)
```

#### Component Completeness Check
```yaml
□ Backend API ready (/app/)
□ ERP Admin Frontend ready (/apps/erp-admin/ - if changed)
□ Consumer App ready (/apps/consumer/ - if changed)
□ TDS Core Worker ready (/tds_core/ - if changed)
□ TDS Dashboard ready (/apps/tds_dashboard/ - if changed)
```

**RULE: Deploy ALL changed components together. NEVER deploy partial components.**

#### Deployment Execution
```bash
# Step 1: Push to develop branch (triggers staging deployment)
git push origin develop

# Step 2: Monitor GitHub Actions
gh run list --limit 3
gh run watch <latest-run-id>

# Step 3: Verify staging deployment
curl https://staging.erp.tsh.sale/health
curl https://staging.consumer.tsh.sale/

# Step 4: Check all staging URLs
# - staging.erp.tsh.sale (ERP Admin)
# - staging.consumer.tsh.sale (Consumer App)
# - staging.tds.tsh.sale (TDS Dashboard)
```

#### Post-Deployment Verification
```yaml
□ All staging URLs accessible
□ Health endpoints return 200 OK
□ TDS dashboard shows no errors
□ Database migrations applied successfully
□ Background jobs running (check TDS dashboard)
```

#### Notify Khaleel
```
"Staging deployment complete:
- ERP Admin: https://staging.erp.tsh.sale
- Consumer: https://staging.consumer.tsh.sale
- TDS Dashboard: https://staging.tds.tsh.sale

All health checks passed. Ready for your testing."
```

---

## 📊 Session Success Metrics

### At End of Session, Check:

#### ✅ Efficiency Metrics
```yaml
Did I...
□ Complete the requested task(s)?
□ Search existing code before creating new?
□ Ask relevant questions (not obvious ones)?
□ Deploy to staging successfully (if applicable)?
□ Update todo list throughout (if used)?
```

#### ✅ Quality Metrics
```yaml
Did I...
□ Include Arabic support in ALL user-facing features?
□ Add proper error handling?
□ Follow established patterns (not reinvent)?
□ Test before marking complete?
□ Avoid security vulnerabilities?
```

#### ✅ Collaboration Metrics
```yaml
Did I...
□ Communicate progress clearly?
□ Explain decisions when relevant?
□ Ask for clarification when uncertain?
□ Avoid repeating context back unnecessarily?
□ Provide actionable next steps to Khaleel?
```

#### ✅ Constraint Adherence
```yaml
Did I...
□ NEVER suggest changing tech stack?
□ NEVER bypass TDS Core for Zoho operations?
□ NEVER deploy partial components?
□ NEVER ignore Arabic RTL requirements?
□ ALWAYS follow deployment workflow?
```

---

## 🎯 Red Flags - Session Quality Issues

### Warning Signs (Fix These Immediately)

**🚩 Khaleel Had to Repeat Context**
```
Why: I didn't load PROJECT_VISION.md or misunderstood requirements
Fix: Re-read PROJECT_VISION.md, apologize, correct approach
```

**🚩 Created Duplicate Functionality**
```
Why: I didn't search existing code first
Fix: Remove duplicate, enhance existing code instead
```

**🚩 Forgot Arabic Support**
```
Why: I didn't check ARCHITECTURE_RULES.md Arabic requirements
Fix: Add name_ar, description_ar fields immediately, update database
```

**🚩 Deployed Only Backend Without Frontend**
```
Why: I ignored COMPLETE_PROJECT_DEPLOYMENT_RULES.md
Fix: Deploy missing components immediately, verify all URLs
```

**🚩 Suggested Technology Change**
```
Why: I ignored tech stack constraints in PROJECT_VISION.md
Fix: Retract suggestion, work within FastAPI+Flutter+PostgreSQL
```

**🚩 Bypassed TDS Core for Zoho Access**
```
Why: I didn't understand Zoho sync architecture
Fix: CRITICAL - Remove direct API calls, route through TDS Core
```

---

## 🏆 Perfect Session Example

### Timeline
```
00:00 - Session Start
├─ 00:01 - Loaded AI_CONTEXT_RULES.md + PROJECT_VISION.md
├─ 00:02 - Checked git status, branch, recent commits
├─ 00:03 - Greeted Khaleel, asked what we're working on
└─ 00:04 - Ready to work

00:05 - Task Received: "Add feature to track commission for salesmen"
├─ 00:06 - Asked clarifying questions:
│         - "Which salesman type? Travel salespeople or partner salesmen?"
│         - "Should this integrate with existing order system?"
│         - "Do we need historical commission calculation?"
├─ 00:10 - Khaleel clarified: "Travel salespeople, yes integrate, no historical"
└─ 00:11 - Confirmed understanding

00:12 - Searched Existing Code
├─ 00:13 - Found existing commission logic in app/services/commission.py
├─ 00:14 - Found salesman model in app/models/salesman.py
├─ 00:15 - Found order tracking in app/models/order.py
└─ 00:16 - Decision: ENHANCE existing commission.py, don't create new

00:17 - Created Todo List (5 steps)
├─ 1. Add commission_rate field to salesman model
├─ 2. Update commission calculation in services
├─ 3. Add API endpoint to view commission
├─ 4. Create database migration
└─ 5. Test and deploy to staging

00:18 - Implementation Started
├─ Marked "Add commission_rate field" as in_progress
├─ Added field with name_ar support
├─ Added validation (0-100% range)
├─ Marked complete, moved to next task
└─ ... (repeated for all tasks)

01:30 - All Implementation Complete
├─ All tests passed
├─ No violations detected
└─ Ready to deploy

01:35 - Deployment to Staging
├─ Committed with clear message
├─ Pushed to develop branch
├─ Monitored GitHub Actions
├─ Verified all staging URLs
└─ Notified Khaleel

01:45 - Session End
├─ Task complete
├─ Staging working
├─ Khaleel testing
└─ Awaiting feedback for production deployment
```

**Success Metrics for This Session:**
- ✅ 100% task completion
- ✅ 0 constraint violations
- ✅ Enhanced existing code (didn't duplicate)
- ✅ Arabic support included
- ✅ Deployed successfully
- ✅ Clear communication
- ✅ Khaleel didn't have to repeat context

---

## 📋 Quick Checklist Print Version

### START
```
□ Load context (AI_CONTEXT_RULES, PROJECT_VISION)
□ Check git (branch, status, recent commits)
□ Greet + Ask what we're working on
```

### WORK
```
□ Clarify if unclear
□ Search existing code FIRST
□ Create todo if complex (3+ steps)
□ Include Arabic support
□ Add error handling
□ Add validation
□ Test before marking complete
```

### DEPLOY
```
□ Check: ALL components ready
□ Push to develop (staging)
□ Monitor GitHub Actions
□ Verify staging URLs
□ Notify Khaleel
```

### CHECK
```
□ No duplicate code created
□ No Arabic forgotten
□ No partial deployment
□ No TDS Core bypass
□ No tech stack suggestions
□ Khaleel didn't repeat context
```

---

## 🎓 Learning from Mistakes

### Mistake Log Template

When I make a mistake, document it here (mental note for session):

```markdown
**Mistake:** [What I did wrong]
**Why:** [Root cause]
**Impact:** [What broke / what was affected]
**Fix:** [How I corrected it]
**Lesson:** [What pattern to follow next time]
**Prevention:** [Checklist item to add]
```

**Example:**
```markdown
**Mistake:** Created new product endpoint without checking existing code
**Why:** Didn't search app/routers/ first
**Impact:** Duplicate functionality, wasted 20 minutes
**Fix:** Removed new code, enhanced existing endpoint
**Lesson:** ALWAYS search before creating (find + grep)
**Prevention:** Added "Code Search Protocol" to mandatory checklist
```

---

## 🔄 Continuous Improvement

### After Every 5 Sessions, Review:

```yaml
Patterns to Reinforce:
□ What went well consistently?
□ What mistakes stopped recurring?
□ What processes became faster?

Patterns to Improve:
□ What mistakes repeated?
□ What caused delays?
□ What confused Khaleel?

Documentation Updates Needed:
□ Should any checklist items be added?
□ Should any examples be clarified?
□ Should any new patterns be documented?
```

**Suggest updates to Khaleel when patterns emerge.**

---

## 📞 Emergency Protocols

### When Things Go Wrong

#### 🚨 **Production is Down**
```yaml
IMMEDIATE:
1. Alert Khaleel immediately
2. Check GitHub Actions for failed deployment
3. Check VPS health: curl https://erp.tsh.sale/health
4. Check database connectivity
5. Propose rollback if deployment-related

DO NOT:
- Panic
- Make changes without Khaleel's approval
- Deploy "fixes" without testing
```

#### 🚨 **Zoho Sync Failed**
```yaml
IMMEDIATE:
1. Check TDS Dashboard: staging.tds.tsh.sale or tds.tsh.sale
2. Check TDS Core logs
3. Identify which API (Books or Inventory)
4. Check if rate limit, auth, or data issue
5. Report to Khaleel with details

DO NOT:
- Access Zoho APIs directly
- Bypass TDS Core
- Retry without understanding root cause
```

#### 🚨 **Data Corruption Risk**
```yaml
IMMEDIATE:
1. STOP all write operations
2. Alert Khaleel immediately
3. Document exactly what happened
4. Check AWS S3 backup availability
5. Wait for Khaleel's decision

DO NOT:
- Attempt to fix data directly
- Continue operations
- Guess at solution
```

---

**END OF SESSION_CHECKLIST.md**

*Use this checklist at the start, during, and end of EVERY session for consistent quality.*
