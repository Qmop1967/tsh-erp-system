# Task Patterns - Operational Workflows for Claude Code

**Structured workflows for recurring task types**
**Last Updated:** 2025-11-12

---

## 🎯 Purpose

This file provides **step-by-step workflows** for different types of tasks, ensuring consistency, quality, and alignment with project vision. Every task type has a clear reasoning chain and sequence.

---

## 📋 Task Categories

```
🧩 Feature Implementation
🐛 Bug Fix
🧠 Refactor / Optimization
🧾 Documentation Update
🔄 Deployment / CI/CD Task
🔍 Investigation / Research
🧪 Testing
🔐 Security Enhancement
```

---

## 🧩 Feature Implementation

### When to Use
- Adding new functionality
- Building new API endpoints
- Creating new UI components
- Implementing business logic

### Pre-Action Checklist

**Before starting ANY feature implementation, verify:**

```yaml
✅ Understanding Check:
□ I understand WHAT needs to be built (specific requirement)
□ I understand WHY (business value, strategic goal)
□ I understand WHO will use this (user roles)
□ I understand WHERE it fits (which module/component)
□ I understand WHEN it's needed (urgency level)

✅ Context Verification:
□ Does this align with PROJECT_VISION.md strategic goals?
□ Is this part of Zoho sync logic or local ERP logic?
□ Which Zoho migration phase are we in? (Phase 1: read-only)
□ Which environment? (development = deploy anytime)
□ Current git branch? (should be develop or feature/*)

✅ Module Impact Assessment:
□ Which module does this impact?
  - Sales (orders, invoices, payments)
  - Inventory (products, stock, warehouses)
  - HR (users, salespeople, commissions)
  - Clients (wholesale clients, partner salesmen)
  - Reporting (analytics, dashboards)
  - TDS Core (Zoho sync operations)

✅ Arabic & Localization:
□ Does this have user-facing text? (YES = needs Arabic)
□ Does this create/modify database fields? (add name_ar, description_ar)
□ Does UI need RTL layout support? (always yes for Arabic)
□ Which language is primary for this feature? (Arabic)

✅ Authentication & Authorization:
□ Who should access this feature? (all users, specific roles, admins only)
□ Does this modify data? (YES = requires authentication)
□ Does this access sensitive data? (YES = requires RBAC check)
□ Which roles should have access? (admin, manager, salesperson, client)

✅ Integration Points:
□ Does this interact with Zoho? (YES = must use TDS Core)
□ Does this require real-time data? (or is cached acceptable)
□ Does this integrate with existing features? (which ones)
□ Does this require mobile app changes? (which of the 8 apps)

✅ Performance & Scale:
□ Will this handle 500+ clients?
□ Will this handle 2,218+ products?
□ Will this handle 30+ daily orders?
□ Does this need pagination? (> 100 records = yes)
□ Does this need database indexes? (queries on large tables)

✅ Dependencies Check:
□ Are there similar features already? (search codebase first)
□ What existing code can be reused? (services, models, schemas)
□ What external dependencies needed? (new Python packages)
□ What database changes required? (migrations)
```

**Decision Point: Proceed ONLY if all checks pass.**

### Step-by-Step Workflow

#### Step 1: Context & Alignment (MANDATORY)
```yaml
Actions:
  1. Read PROJECT_VISION.md
     - Confirm this feature aligns with business purpose
     - Check current Zoho migration phase constraints
     - Verify scale requirements (500+ clients, 2,218+ products)

  2. Read ARCHITECTURE_RULES.md
     - Verify tech stack compatibility
     - Check design patterns to follow
     - Review naming conventions

  3. Ask Clarifying Questions
     - Who will use this feature? (which user role)
     - What's the business outcome?
     - Any performance requirements?
     - Mobile, web, or both?
     - Arabic support needed? (always yes, but confirm UI requirements)

Decision Point: Proceed only after alignment confirmed
```

#### Step 2: Search Existing Code (MANDATORY)
```yaml
Actions:
  1. Search for similar functionality
     - Use Grep tool to search codebase
     - Check /app/routers/, /app/services/, /scripts/
     - Look for existing patterns

  2. Evaluate: Enhance vs Create New
     - If similar exists: Enhance existing code
     - If unique: Create new following patterns

Example Commands:
  grep -r "commission" app/services/
  grep -r "product.*list" app/routers/
  find . -name "*wholesale*" -type f
```

#### Step 3: Plan & Design
```yaml
Actions:
  1. Create TodoWrite list if complex (3+ steps)
  2. Design API contract (if backend)
     - Endpoint path: /api/v1/resource
     - Request/response schemas
     - Authentication required
     - RBAC roles allowed

  3. Design database changes (if needed)
     - New tables or columns
     - Indexes required
     - Migration plan

  4. Design UI flow (if frontend)
     - Screen layout
     - User interactions
     - Arabic RTL considerations
```

#### Step 4: Implementation
```yaml
Backend (FastAPI):
  1. Create Pydantic schema in app/schemas/
  2. Create/update SQLAlchemy model in app/models/
  3. Create service layer in app/services/
  4. Create router/endpoint in app/routers/
  5. Add input validation
  6. Add error handling
  7. Add authentication/authorization
  8. Include Arabic fields (name_ar, description_ar)
  9. Add docstrings with business context

Frontend (React/Flutter):
  1. Create component/widget
  2. Implement state management
  3. Add API integration
  4. Implement RTL layout for Arabic
  5. Add loading states
  6. Add error handling
  7. Add validation
  8. Ensure mobile responsiveness

Code Quality:
  - Follow naming conventions
  - Add type hints (Python/TypeScript)
  - Write clear docstrings
  - Comment complex business logic
  - No hardcoded values (use constants)
```

#### Step 5: Testing
```yaml
Actions:
  1. Test locally
     - Happy path
     - Error cases
     - Edge cases
     - Arabic text input
     - Large datasets (pagination)

  2. Test integration
     - API endpoints respond correctly
     - Database operations work
     - Frontend displays data correctly

  3. Test with real scenarios
     - Use production-like data volume
     - Test with actual user workflows
```

#### Step 6: Documentation
```yaml
Actions:
  1. API Documentation (FastAPI auto-generates)
     - Verify OpenAPI docs are clear
     - Add detailed descriptions

  2. Code Documentation
     - Docstrings for functions/classes
     - Inline comments for complex logic
     - Business context explained

  3. Update CHANGELOG.md (if significant feature)
     - Add to "Unreleased" section
     - Describe what was added
```

#### Step 7: Deployment
```yaml
Actions:
  1. Commit with clear message
     - git add .
     - git commit -m "feat: add wholesale client credit limit checking"

  2. Push to develop (staging)
     - git push origin develop

  3. Monitor deployment
     - gh run watch <run-id>

  4. Verify on staging
     - Test the feature on staging.erp.tsh.sale
     - Get Khaleel's approval

  5. Create PR for production
     - gh pr create --base main --head develop
     - Include testing results

Decision Point: Only mark complete after staging verification
```

### Quality Gates (Must Pass)
```yaml
✅ Feature aligns with PROJECT_VISION.md
✅ Follows patterns in ARCHITECTURE_RULES.md
✅ Searched for existing similar code
✅ Arabic support included (if user-facing)
✅ Input validation implemented
✅ Error handling implemented
✅ Authentication/authorization checked
✅ Tested locally with edge cases
✅ Documented (docstrings + comments)
✅ Verified on staging
```

---

## 🐛 Bug Fix

### When to Use
- Something is broken
- Error reports from users
- Test failures
- Unexpected behavior

### Pre-Action Checklist

**Before starting ANY bug fix, verify:**

```yaml
✅ Bug Verification:
□ Can I reproduce the bug? (specific steps to reproduce)
□ What is the EXACT error or unexpected behavior?
□ Is this always happening or intermittent?
□ Which environment? (local, staging, production)
□ When did this start? (recent deployment? always been there?)

✅ Severity Assessment:
□ Impact level:
  - CRITICAL: Production down, data corruption, security breach
  - HIGH: Core features broken, many users affected
  - MEDIUM: Some features broken, subset of users affected
  - LOW: Minor issue, workaround available

□ Urgency level:
  - IMMEDIATE: Fix now (use Emergency Mode if production down)
  - URGENT: Fix within hours (affects business operations)
  - NORMAL: Fix within days (scheduled work)
  - LOW: Fix when convenient (nice-to-have)

✅ User Impact:
□ How many users affected? (all 500+ clients or specific users)
□ Which user roles affected? (admin, manager, salesperson, client)
□ Which workflows blocked? (order creation, payments, reports)
□ Can users work around it? (yes = lower priority)

✅ Root Cause Hypothesis:
□ Recent code changes? (check git log last 7 days)
□ Recent deployment? (check GitHub Actions)
□ Database issue? (connection, migration, data integrity)
□ External service issue? (Zoho, VPS, network)
□ Environment issue? (env variables, configuration)
□ Data-specific issue? (only happens with certain data)

✅ Evidence Gathering:
□ Error logs available? (backend logs, TDS Core logs)
□ Stack trace available? (full error details)
□ Recent commits reviewed? (git log --since="3 days ago")
□ Database state checked? (query to verify data)
□ User actions known? (what did they do before error)

✅ Fix Strategy:
□ Root cause or symptom? (fix root cause, not just symptom)
□ Quick fix or proper fix? (quick if critical, proper otherwise)
□ Rollback possible? (if recent deployment caused it)
□ Safe to fix now? (or wait for maintenance window)
□ Test environment available? (staging to verify fix)
```

**Decision Point: Understand root cause before implementing fix.**

### Step-by-Step Workflow

#### Step 1: Reproduce & Diagnose
```yaml
Actions:
  1. Reproduce the bug
     - Follow exact steps to trigger
     - Note environment (local, staging, production)
     - Capture error messages

  2. Collect information
     - Check logs (journalctl, browser console)
     - Check database state
     - Check recent code changes (git log)

  3. Identify root cause
     - Use debugging tools
     - Add temporary logging if needed
     - Understand the "why" not just "what"

Example:
  "The error occurs because we're trying to create an order
   for a customer_id that doesn't exist. Root cause: Customer
   was deleted but we didn't verify existence before order creation."
```

#### Step 2: Assess Impact
```yaml
Questions:
  1. Severity
     - Critical: Production down, data loss
     - High: Core feature broken
     - Medium: Minor feature broken
     - Low: Cosmetic issue

  2. Scope
     - How many users affected?
     - Which functionality impacted?
     - Data integrity at risk?

  3. Urgency
     - Immediate: Production critical
     - High: Should fix today
     - Medium: Fix in next sprint
     - Low: Backlog

Decision: Prioritize accordingly
```

#### Step 3: Design Fix
```yaml
Actions:
  1. Determine fix approach
     - Band-aid fix vs proper solution
     - Any side effects?
     - Need database migration?

  2. Check for similar bugs
     - Search codebase for same pattern
     - Fix in multiple places if needed

  3. Plan prevention
     - Add validation to prevent recurrence
     - Add test case
     - Update documentation if needed
```

#### Step 4: Implement Fix
```yaml
Actions:
  1. Write the fix
     - Minimal changes (don't refactor unrelated code)
     - Clear, focused solution
     - Add comments explaining the fix

  2. Add prevention
     - Input validation
     - Error handling
     - Database constraints
     - Test case

  3. Verify fix works
     - Test the exact scenario that failed
     - Test related scenarios
     - Ensure no regression
```

#### Step 5: Deploy & Verify
```yaml
For Critical Bugs:
  1. Hotfix branch from main
     - git checkout main
     - git checkout -b hotfix/critical-bug-name

  2. Implement and test fix

  3. Push to develop first (quick staging test)
     - git push origin develop
     - Quick verification on staging

  4. Create PR to main (expedited)
     - gh pr create --base main --head develop --label "hotfix"
     - Fast-track approval

  5. Monitor production closely
     - Verify fix deployed
     - Monitor for 15-30 minutes
     - Check error logs

For Non-Critical Bugs:
  1. Regular workflow through develop → staging → main
  2. Thorough testing on staging
  3. Normal PR process
```

### Quality Gates (Must Pass)
```yaml
✅ Root cause identified and understood
✅ Fix tested with original failure scenario
✅ No regression (other features still work)
✅ Prevention mechanism added (validation/test)
✅ Impact assessed accurately
✅ Verified on staging before production
```

---

## 🧠 Refactor / Optimization

### When to Use
- Code is messy or hard to understand
- Performance issues
- Technical debt
- Duplicate code

### Step-by-Step Workflow

#### Step 1: Measure First (MANDATORY)
```yaml
Actions:
  1. Establish baseline
     - Current performance metrics
     - Current code complexity
     - Current test coverage

  2. Identify problem
     - What specifically is wrong?
     - How do we know it's a problem?
     - What's the impact?

Example:
  ❌ BAD: "Let's optimize the product endpoint"
  ✅ GOOD: "Product endpoint takes 2.3s for 2,218 products.
           Target is <500ms. Current query does N+1 selects."

Rule: Never optimize without measurement
```

#### Step 2: Plan Refactor
```yaml
Actions:
  1. Define goal
     - What will improve?
     - How will we measure success?
     - What's the target metric?

  2. Assess risk
     - How much code affected?
     - Can we break it down into smaller changes?
     - Do we need feature flags?

  3. Test strategy
     - Existing tests should still pass
     - Add new tests if coverage gaps
     - How to verify no regression?
```

#### Step 3: Implement Changes
```yaml
Actions:
  1. Make incremental changes
     - Small, testable steps
     - Commit frequently
     - Don't refactor + add features simultaneously

  2. Maintain behavior
     - Same inputs → same outputs
     - No breaking changes to API contracts
     - Backward compatible

  3. Improve clarity
     - Better variable names
     - Clearer function decomposition
     - Remove code duplication
     - Add comments for complex logic
```

#### Step 4: Measure After (MANDATORY)
```yaml
Actions:
  1. Verify improvement
     - Measure same metrics as baseline
     - Did we achieve the goal?
     - Any side effects?

  2. Document results
     - Before: X
     - After: Y
     - Improvement: Z%

Example:
  "Optimized product list endpoint:
   - Before: 2.3s for 2,218 products
   - After: 180ms with pagination + indexes
   - Improvement: 92% faster
   - Method: Added pagination, indexed category_id and is_active"
```

### Quality Gates (Must Pass)
```yaml
✅ Baseline measured before changes
✅ Goal clearly defined with target metric
✅ All existing tests still pass
✅ Improvement measured and documented
✅ No breaking changes introduced
✅ Code is clearer/simpler after refactor
```

---

## 🧾 Documentation Update

### When to Use
- Adding/updating project documentation
- Updating .claude/ system files
- Writing guides or READMEs
- API documentation updates

### Step-by-Step Workflow

#### Step 1: Identify Need
```yaml
Questions:
  1. What's outdated or missing?
  2. Who is the audience?
     - Developers (current or future)
     - AI agents (like me)
     - End users
     - System administrators

  3. What's the goal?
     - Onboarding
     - Troubleshooting
     - Reference
     - Tutorial
```

#### Step 2: Research Content
```yaml
Actions:
  1. Gather accurate information
     - Check current codebase
     - Verify configurations
     - Test procedures
     - Check URLs/links

  2. Review existing documentation
     - What's already documented?
     - What can be enhanced?
     - What's contradictory?
```

#### Step 3: Write Content
```yaml
Structure:
  1. Title and purpose
  2. Prerequisites (if applicable)
  3. Step-by-step instructions
  4. Examples
  5. Troubleshooting (if applicable)
  6. Related documentation links

Style:
  - Clear, concise language
  - Use code blocks for commands/code
  - Use bullet points for lists
  - Use headers for sections
  - Add diagrams if helpful

For .claude/ files:
  - Follow existing format
  - Update "Last Updated" date
  - Maintain consistent structure
  - Cross-reference other files
```

#### Step 4: Verify Accuracy
```yaml
Actions:
  1. Test all commands/procedures
     - Copy-paste commands and run them
     - Verify they work as documented
     - Check all links are valid

  2. Review for clarity
     - Would a new developer understand this?
     - Are there ambiguous instructions?
     - Are examples helpful?

  3. Check consistency
     - Aligns with other documentation?
     - Same terminology used?
     - No contradictions?
```

#### Step 5: Update Related Docs
```yaml
Actions:
  1. Update cross-references
     - Link to new documentation
     - Update indexes or tables of contents
     - Update CHANGELOG_AI.md (if .claude/ file)

  2. Archive obsolete docs
     - Move to /archived/ if outdated
     - Update links pointing to old docs
```

### Quality Gates (Must Pass)
```yaml
✅ All commands/procedures tested
✅ All links verified
✅ Clear and concise writing
✅ Appropriate for target audience
✅ Cross-references updated
✅ "Last Updated" date current
```

---

## 🔄 Deployment / CI/CD Task

### When to Use
- Deploying to staging or production
- Updating CI/CD workflows
- Infrastructure changes
- Environment configuration

### Step-by-Step Workflow

#### Step 1: Pre-Deployment Checklist
```yaml
Must Verify:
  1. All components ready
     - [ ] Backend API
     - [ ] ERP Admin Frontend
     - [ ] Consumer App (Flutter Web)
     - [ ] TDS Core Worker
     - [ ] TDS Dashboard

  2. Tests passing
     - [ ] Local tests pass
     - [ ] CI tests pass
     - [ ] Linting passes

  3. Dependencies checked
     - [ ] requirements.txt up to date
     - [ ] package.json up to date
     - [ ] pubspec.yaml up to date

  4. Environment variables
     - [ ] .env.production up to date on VPS
     - [ ] GitHub Secrets configured
     - [ ] No secrets in code

  5. Database migrations
     - [ ] Migrations created
     - [ ] Migrations tested locally
     - [ ] Backup plan ready
```

#### Step 2: Deploy to Staging FIRST
```yaml
Actions:
  1. Push to develop branch
     - git push origin develop

  2. Monitor GitHub Actions
     - gh run list --limit 5
     - gh run watch <run-id>

  3. Verify staging deployment
     - curl https://staging.erp.tsh.sale/health
     - curl https://staging.consumer.tsh.sale/
     - Manual testing of changes

  4. Get approval from Khaleel
     - Demonstrate working features
     - Confirm readiness for production

Decision Point: Do NOT proceed to production without staging verification
```

#### Step 3: Production Deployment
```yaml
Actions:
  1. Create Pull Request
     - gh pr create --base main --head develop
     - Title: "Deploy: [Feature Name] to Production"
     - Description:
       * What changed
       * Staging verification results
       * Any special notes

  2. Review and merge
     - Review code changes
     - Khaleel approves
     - Merge PR (triggers production deployment)

  3. Monitor deployment
     - gh run watch <run-id>
     - Watch for any errors

  4. Verify ALL components
     - Backend: curl https://erp.tsh.sale/health
     - Frontend: curl https://erp.tsh.sale/
     - Consumer: curl https://consumer.tsh.sale/
     - TDS Dashboard: curl https://erp.tsh.sale/tds-admin/

  5. Post-deployment monitoring
     - Monitor for 15-30 minutes
     - Check error logs
     - Watch for user reports
```

#### Step 4: Rollback Plan (If Needed)
```yaml
If deployment fails:
  1. Assess severity
     - Is production completely down?
     - Is data at risk?
     - Can users still work?

  2. Quick rollback options
     - Blue-green switch on VPS
     - Git revert + redeploy
     - Restore from backup (last resort)

  3. Execute rollback
     - ssh root@167.71.39.50
     - bash /opt/tsh_erp/bin/switch_deployment.sh

  4. Investigate and fix
     - Diagnose what went wrong
     - Fix in develop branch
     - Test thoroughly
     - Redeploy
```

### Quality Gates (Must Pass)
```yaml
✅ All components deployed (not just one)
✅ Staging verified before production
✅ All health checks passing
✅ All URLs returning 200 OK
✅ Database migrations applied successfully
✅ No errors in logs
✅ Khaleel approved deployment
```

---

## 🔍 Investigation / Research

### When to Use
- Understanding existing code
- Researching best practices
- Evaluating technologies
- Exploring codebase structure

### Step-by-Step Workflow

#### Step 1: Define Question
```yaml
Actions:
  1. Clarify what you're looking for
     - Specific: "How do we calculate commissions?"
     - Not vague: "How does money work?"

  2. Define success criteria
     - What information would answer the question?
     - How deep do we need to go?
```

#### Step 2: Search Strategy
```yaml
Tools to Use:
  1. Grep for code search
     - Search for keywords
     - Find similar patterns

  2. Read for file exploration
     - Read relevant files
     - Understand context

  3. Task tool for complex searches
     - Use Explore agent for thorough investigation
     - Specify thoroughness level

Example:
  "I need to find how wholesale pricing is calculated"

  1. grep -r "wholesale.*price" app/
  2. grep -r "commission" app/services/
  3. Read files found
  4. Trace function calls
```

#### Step 3: Document Findings
```yaml
Actions:
  1. Summarize what you found
     - Clear explanation
     - File locations (with line numbers)
     - How it works

  2. Provide examples
     - Actual code snippets
     - Usage examples

  3. Note any issues
     - Bugs found
     - Inconsistencies
     - Improvement opportunities

Example Response:
  "Wholesale pricing is calculated in app/services/pricing.py:45

   The calculate_wholesale_price() function applies:
   1. Base product price
   2. Volume discount (>100 units = 10% off)
   3. Client-specific discount from customers table

   Current implementation doesn't account for seasonal discounts
   mentioned in PROJECT_VISION.md."
```

### Quality Gates (Must Pass)
```yaml
✅ Question clearly defined
✅ Searched thoroughly (not just first result)
✅ Findings documented with file paths and line numbers
✅ Answer is actionable
✅ Related issues noted
```

---

## 🧪 Testing

### When to Use
- Writing new tests
- Fixing failing tests
- Improving test coverage
- Integration testing

### Step-by-Step Workflow

#### Step 1: Identify What to Test
```yaml
Test Types:
  1. Unit Tests
     - Individual functions/methods
     - Business logic
     - Data transformations

  2. Integration Tests
     - API endpoints
     - Database operations
     - Service interactions

  3. End-to-End Tests
     - Complete user workflows
     - Multi-component interactions
```

#### Step 2: Write Tests
```yaml
Test Structure (AAA Pattern):
  1. Arrange: Setup test data and environment
  2. Act: Execute the code being tested
  3. Assert: Verify expected outcome

Example (Python/pytest):
  def test_wholesale_price_calculation():
      # Arrange
      product = Product(price=100.00)
      client = Client(discount_percent=15)
      quantity = 150

      # Act
      final_price = calculate_wholesale_price(product, client, quantity)

      # Assert
      assert final_price == 72.25  # 100 - 15% - 10% (volume)

Test Coverage:
  - Happy path (expected input)
  - Edge cases (boundary values)
  - Error cases (invalid input)
  - Arabic text (for user-facing features)
```

#### Step 3: Run Tests
```yaml
Actions:
  1. Run locally first
     - pytest tests/
     - npm test
     - flutter test

  2. Fix any failures
     - Understand why test failed
     - Fix code or fix test (if test was wrong)

  3. Verify coverage
     - pytest --cov=app tests/
     - Aim for >80% coverage on critical paths
```

#### Step 4: Integration with CI
```yaml
Actions:
  1. Ensure tests run in CI
     - GitHub Actions should run tests
     - Tests must pass before merge

  2. Keep tests fast
     - Unit tests < 1 second each
     - Integration tests < 5 seconds each
     - Mock external services (Zoho APIs)
```

### Quality Gates (Must Pass)
```yaml
✅ Tests follow AAA pattern
✅ Tests are clear and focused
✅ Tests cover happy path + edge cases + errors
✅ Tests run quickly
✅ All tests pass locally
✅ Tests pass in CI
```

---

## 🔐 Security Enhancement

### When to Use
- Adding security features
- Fixing security vulnerabilities
- Implementing authentication/authorization
- Security audits

### Step-by-Step Workflow

#### Step 1: Assess Current State
```yaml
Actions:
  1. Review security posture
     - Authentication in place?
     - Authorization enforced?
     - Input validation?
     - SQL injection prevention?
     - XSS prevention?
     - CSRF protection?

  2. Identify vulnerabilities
     - Use security scanning tools
     - Review code for common issues
     - Check dependencies for CVEs
```

#### Step 2: Design Security Enhancement
```yaml
Questions:
  1. What threat are we addressing?
  2. What's the security boundary?
  3. What's the user impact?
  4. Performance implications?

Security Layers:
  1. Authentication (Who are you?)
  2. Authorization (What can you do?)
  3. Input Validation (Is this safe?)
  4. Output Encoding (Can't inject)
  5. Audit Logging (Who did what?)
```

#### Step 3: Implement Securely
```yaml
Best Practices:
  1. Use established libraries
     - Don't roll your own crypto
     - Use FastAPI security utilities
     - Use SQLAlchemy (prevents SQL injection)

  2. Defense in depth
     - Multiple layers of security
     - Fail securely (deny by default)

  3. Validate everything
     - Never trust user input
     - Validate on backend (not just frontend)
     - Use Pydantic schemas

  4. Follow OWASP Top 10
     - Injection
     - Broken Authentication
     - Sensitive Data Exposure
     - XML External Entities (XXE)
     - Broken Access Control
     - Security Misconfiguration
     - Cross-Site Scripting (XSS)
     - Insecure Deserialization
     - Using Components with Known Vulnerabilities
     - Insufficient Logging & Monitoring
```

#### Step 4: Test Security
```yaml
Actions:
  1. Test attack scenarios
     - Try to bypass authentication
     - Try SQL injection
     - Try XSS attacks
     - Try unauthorized access

  2. Security scanning
     - Run bandit (Python security linter)
     - Run npm audit (Node.js)
     - Check dependencies

  3. Penetration testing
     - Manual testing of security controls
     - Automated security scans
```

#### Step 5: Document & Monitor
```yaml
Actions:
  1. Document security measures
     - What's protected
     - How it's protected
     - Assumptions made

  2. Set up monitoring
     - Failed login attempts
     - Unusual access patterns
     - Security events logged

  3. Incident response plan
     - What to do if breach detected
     - Who to contact
     - How to contain
```

### Quality Gates (Must Pass)
```yaml
✅ Threat clearly identified
✅ Security best practices followed
✅ Input validation implemented
✅ Authentication/authorization enforced
✅ SQL injection prevented (using ORM)
✅ XSS prevented (output encoding)
✅ Security tests pass
✅ No hardcoded secrets
✅ Audit logging in place
```

---

## 📊 Task Pattern Selection Decision Tree

```
Start
  ↓
Is this adding new functionality?
  Yes → 🧩 Feature Implementation
  No → Continue
  ↓
Is something broken?
  Yes → 🐛 Bug Fix
  No → Continue
  ↓
Is this improving code quality or performance?
  Yes → 🧠 Refactor / Optimization
  No → Continue
  ↓
Is this updating documentation?
  Yes → 🧾 Documentation Update
  No → Continue
  ↓
Is this deploying changes?
  Yes → 🔄 Deployment / CI/CD Task
  No → Continue
  ↓
Are you searching/understanding code?
  Yes → 🔍 Investigation / Research
  No → Continue
  ↓
Are you writing/fixing tests?
  Yes → 🧪 Testing
  No → Continue
  ↓
Is this security-related?
  Yes → 🔐 Security Enhancement
  No → Ask Khaleel for clarification
```

---

## ✅ Universal Quality Principles

These apply to **ALL** task types:

```yaml
Before Starting:
  - [ ] Read PROJECT_VISION.md (understand business context)
  - [ ] Read ARCHITECTURE_RULES.md (follow patterns)
  - [ ] Search existing code (enhance before creating)
  - [ ] Ask clarifying questions (if uncertain)

During Work:
  - [ ] Follow naming conventions
  - [ ] Include Arabic support (if user-facing)
  - [ ] Add validation and error handling
  - [ ] Write clear docstrings and comments
  - [ ] Test as you go

Before Completing:
  - [ ] Tested locally
  - [ ] Code is clean and readable
  - [ ] Documentation updated (if needed)
  - [ ] Committed with clear message
  - [ ] Deployed to staging (if deployment task)
  - [ ] Verified working
```

---

## 🎯 Success Indicators

You're using task patterns effectively when:

- ✅ You follow the same steps consistently for each task type
- ✅ You don't skip steps (especially context loading)
- ✅ Quality gates are met before marking complete
- ✅ Khaleel doesn't have to repeat instructions
- ✅ Features work correctly first time
- ✅ Code follows established patterns
- ✅ Documentation stays updated

---

**END OF TASK PATTERNS**

Use this file as your operational handbook. Every task should follow its appropriate pattern for consistency and quality.
