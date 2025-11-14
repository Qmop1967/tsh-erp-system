# TSH ERP Ecosystem - Common Workflows

**Purpose:** Step-by-step workflows for recurring task types
**Last Updated:** 2025-11-14
**Load via:** @docs/core/workflows.md

---

## 📋 Workflow Categories

```
🧩 Feature Implementation
🐛 Bug Fix & Troubleshooting
🚀 Deployment (Staging & Production)
🔍 Investigation & Research
🧠 Refactoring & Optimization
🧾 Documentation Updates
```

---

## 🧩 Feature Implementation Workflow

### Quick Pre-Check
```yaml
Before starting ANY feature:
□ Understand WHAT, WHY, WHO, WHERE, WHEN
□ Verify alignment with PROJECT_VISION.md
□ Check current Zoho phase (Phase 1: read-only)
□ Search for similar existing functionality
□ Confirm Arabic support requirements
□ Verify authentication/authorization needs
```

### Step-by-Step Process

#### 1. Context & Alignment
```bash
# Read core context
@docs/core/project-context.md    # Business requirements
@docs/core/architecture.md        # Technical constraints

# Ask clarifying questions if needed
- Who will use this? (user roles)
- Business outcome expected?
- Performance requirements?
- Mobile, web, or both?
- Arabic UI requirements?
```

#### 2. Search Existing Code (MANDATORY)
```bash
# Search for similar functionality
grep -r "similar_feature" app/services/
grep -r "keyword" app/routers/
find . -name "*pattern*" -type f

# Decision: Enhance existing vs Create new
- Similar exists? → Enhance
- Unique need? → Create new (following patterns)
```

#### 3. Plan & Design
```yaml
For Complex Features (3+ steps):
  - Use TodoWrite tool to track tasks
  - Break into manageable steps

API Design (Backend):
  - Endpoint: /api/v1/resource-name
  - Request/Response schemas
  - Authentication required: Yes/No
  - RBAC roles: [admin, manager, salesperson]
  - Pagination needed: Yes (if > 100 records)

Database Changes:
  - New tables/columns
  - Indexes on foreign keys and search fields
  - Migration script

UI Flow (Frontend):
  - Screen layout
  - User interactions
  - Arabic RTL layout
  - Mobile responsiveness
```

#### 4. Implementation

**Backend (FastAPI):**
```python
# Order of implementation:
1. Create Pydantic schema (app/schemas/)
2. Create/update SQLAlchemy model (app/models/)
3. Create service layer (app/services/)
4. Create router/endpoint (app/routers/)
5. Add ALL 3 authorization layers (RBAC + ABAC + RLS)
6. Add input validation (Pydantic)
7. Add error handling (try/except)
8. Include Arabic fields (name_ar, description_ar)
9. Add docstrings with business context
10. Add pagination if > 100 records

# Security Checklist:
□ Authentication (get_current_user)
□ RBAC (require_role)
□ ABAC (attribute checks)
□ RLS (row-level filtering in service)
□ Input validation (Pydantic schema)
□ SQL injection prevention (ORM/parameterized queries)
```

**Frontend (React/Flutter):**
```typescript
// Order of implementation:
1. Create component/widget
2. Implement state management
3. Add API integration
4. Implement RTL layout for Arabic
5. Add loading states
6. Add error handling
7. Add form validation
8. Ensure mobile responsiveness

// RTL Support (MANDATORY):
<div dir={isArabic ? 'rtl' : 'ltr'}>
  {content}
</div>
```

#### 5. Testing
```yaml
Local Testing:
  □ Happy path works
  □ Error cases handled
  □ Edge cases covered
  □ Arabic text displays correctly
  □ RTL layout works
  □ Pagination works (if applicable)
  □ Authentication works
  □ Authorization enforced
  □ Performance acceptable (< 500ms)

Test with Production Scale:
  □ 500+ clients data
  □ 2,218+ products
  □ 30+ orders
```

#### 6. Deploy to Staging
```bash
# Push to develop branch
git add .
git commit -m "feat: Add [feature name] with Arabic support"
git push origin develop

# Monitor deployment
gh run watch

# Verify staging URLs
curl https://staging.erp.tsh.sale/health
curl https://staging.erp.tsh.sale/api/v1/your-endpoint
```

#### 7. Production Deployment
```bash
# After staging verification:
1. Get user approval
2. Create PR (develop → main)
3. Review changes
4. Merge PR
5. Monitor production deployment
6. Verify all URLs work
7. Monitor for issues (first 30 minutes)
```

---

## 🐛 Bug Fix & Troubleshooting Workflow

### Step-by-Step Process

#### 1. Reproduce Bug
```yaml
Actions:
  1. Get exact steps to reproduce
  2. Identify environment (production, staging, local)
  3. Try to reproduce locally
  4. Note error messages/logs
  5. Document expected vs actual behavior
```

#### 2. Investigate Root Cause
```bash
# Check recent changes
git log --since="3 days ago" --oneline

# Check logs
# Backend logs
ssh root@167.71.39.50 "tail -100 /var/www/tsh-erp/logs/backend.log"

# TDS Core logs
curl https://tds.tsh.sale/api/health
ssh root@167.71.39.50 "tail -100 /var/www/tds-core/logs/tds_core.log"

# Database queries
PGPASSWORD='TSH@2025Secure!Production' psql -h localhost -U tsh_app_user \
  -d tsh_erp_production -c "SELECT * FROM table WHERE condition;"

# Check for patterns
grep -r "error_keyword" app/
```

#### 3. Root-Cause Analysis
```yaml
Questions to Ask:
  - When did this start? (recent deployment? data change?)
  - Who is affected? (all users? specific role? one client?)
  - Where does it fail? (backend? frontend? database? TDS Core?)
  - What changed recently? (code? data? config? infrastructure?)

Common Root Causes:
  - Missing Arabic fields
  - Missing authorization checks
  - N+1 query performance issues
  - Missing pagination
  - Zoho sync failures
  - Missing indexes
  - Hardcoded values
  - Missing error handling
```

#### 4. Fix Implementation
```yaml
Fix the ROOT CAUSE, not symptoms:
  □ Identify exact code location
  □ Implement fix following architecture patterns
  □ Add tests to prevent regression
  □ Verify fix doesn't break other features
  □ Add logging if needed

Security Checks:
  □ Fix doesn't introduce security holes
  □ Authorization still enforced
  □ Input still validated
```

#### 5. Test & Deploy
```bash
# Test fix locally
# Test affected functionality
# Test related features

# Deploy to staging
git commit -m "fix: [Brief description of fix]"
git push origin develop

# Verify fix on staging
# Then deploy to production (if urgent)
```

---

## 🚀 Deployment Workflow

### Staging Deployment (Develop Branch)

```bash
# 1. Verify all changes committed
git status

# 2. Push to develop branch
git push origin develop

# 3. Monitor GitHub Actions
gh run list --limit 3
gh run watch <run-id>

# 4. Wait for deployment to complete

# 5. Verify staging URLs
curl https://staging.erp.tsh.sale/health
curl https://staging.consumer.tsh.sale/health
curl https://staging.tds.tsh.sale/api/health

# 6. Test all changed functionality on staging

# 7. Monitor staging for 15-30 minutes
```

### Production Deployment (Main Branch)

```bash
# Pre-Deployment Checklist:
□ All features tested on staging
□ No critical bugs found
□ All tests passing
□ User approval obtained
□ Deployment time appropriate (current phase: anytime)
□ Rollback plan ready

# 1. Create Pull Request
gh pr create --base main --head develop --title "Deploy to Production" \
  --body "Changes:
- Feature 1: [description]
- Feature 2: [description]
- Bug fixes: [description]

Staging tested: Yes
Risk level: Low/Medium/High
Rollback: Available via git revert"

# 2. Review PR
# Check diff
# Verify all components included
# Confirm tests pass

# 3. Merge PR
gh pr merge <pr-number> --squash

# 4. Monitor Deployment
gh run watch

# 5. Verify Production URLs
curl https://erp.tsh.sale/health
curl https://consumer.tsh.sale/health
curl https://shop.tsh.sale/health
curl https://tds.tsh.sale/api/health

# 6. Smoke Test Critical Paths
# - User login
# - Product list loads
# - Order creation works
# - TDS sync running

# 7. Monitor for 30-60 minutes
# Watch error logs
# Check TDS dashboard
# Monitor user reports

# 8. Rollback if Issues
git revert <commit-hash>
git push origin main
```

### Emergency Hotfix Deployment

```bash
# For critical production issues:
1. Create hotfix branch from main
   git checkout main
   git pull
   git checkout -b hotfix/critical-issue

2. Implement minimal fix
3. Test locally
4. Push to develop first (if time allows)
5. Create PR to main
6. Deploy immediately after merge
7. Monitor closely

# If production is DOWN:
- Follow @docs/FAILSAFE_PROTOCOL.md
- Prioritize stability over perfection
- Document all actions taken
- Proper fix can come later
```

---

## 🔍 Investigation & Research Workflow

### Code Investigation
```bash
# 1. Define what you're looking for
- Specific function/class
- Feature implementation
- Integration point
- Data flow

# 2. Use appropriate tools
# Search by keyword
grep -r "keyword" app/

# Find files by name
find . -name "*pattern*" -type f

# Search for class definition
grep -r "class ClassName" app/

# For complex searches, use Task tool with Explore agent
```

### Data Investigation
```bash
# 1. Connect to database
PGPASSWORD='TSH@2025Secure!Production' psql -h localhost -U tsh_app_user \
  -d tsh_erp_production

# 2. Explore data
# Count records
SELECT COUNT(*) FROM table_name;

# Find specific records
SELECT * FROM products WHERE sku = 'ABC123';

# Check data integrity
SELECT COUNT(*) FROM products WHERE name_ar IS NULL;  # Should be 0!

# 3. Document findings
```

### Zoho Sync Investigation
```bash
# 1. Check TDS Dashboard
open https://tds.tsh.sale

# 2. Check sync status
curl https://tds.tsh.sale/api/health
curl https://tds.tsh.sale/api/sync/statistics

# 3. Check TDS logs
ssh root@167.71.39.50 "tail -200 /var/www/tds-core/logs/tds_core.log"

# 4. Verify Zoho API connectivity
# Check token expiration
# Check rate limits
# Check last successful sync

# 5. Manual sync trigger (if needed)
curl -X POST https://tds.tsh.sale/api/sync/trigger \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🧠 Refactoring & Optimization Workflow

### When to Refactor
```yaml
Refactor when:
  □ Code is duplicated in 3+ places
  □ Function is > 100 lines
  □ Performance is poor (> 2 seconds)
  □ Code is hard to understand
  □ Security vulnerabilities found
  □ Architecture patterns violated

Don't refactor when:
  □ Code works and is clear
  □ No performance issues
  □ No security issues
  □ Time better spent on new features
```

### Refactoring Steps
```yaml
1. Ensure tests exist (write if missing)
2. Make small, incremental changes
3. Test after each change
4. Commit frequently
5. Document what changed and why

Common Refactoring Patterns:
  - Extract common code to service layer
  - Replace N+1 queries with joins
  - Add pagination to large datasets
  - Add database indexes
  - Extract magic numbers to constants
  - Improve error messages
  - Add Arabic field support
```

### Performance Optimization
```yaml
1. Measure first (don't optimize blindly):
   - Use profiling tools
   - Check database query times
   - Monitor API response times

2. Identify bottlenecks:
   - Slow database queries
   - N+1 query patterns
   - Missing indexes
   - Large dataset without pagination
   - Synchronous I/O in async functions

3. Apply optimizations:
   - Add database indexes
   - Use joinedload for relationships
   - Add pagination
   - Use async/await properly
   - Add caching (if appropriate)

4. Measure improvement:
   - Verify performance gains
   - Ensure no regressions
   - Document optimization
```

---

## 🧾 Documentation Update Workflow

### When to Update Docs
```yaml
Update documentation when:
  □ Adding new feature
  □ Changing architecture
  □ Moving to new phase (Zoho migration)
  □ Discovering issues with existing docs
  □ Onboarding new team member (gaps found)
```

### Documentation Priority
```yaml
High Priority:
  - CLAUDE.md (auto-loaded, most used)
  - core/project-context.md (business context)
  - core/architecture.md (technical rules)
  - README.md (project overview)

Medium Priority:
  - Specific feature guides
  - Deployment guides
  - API documentation

Low Priority:
  - Detailed code comments (in code itself)
  - Historical notes (archived/)
```

### Update Process
```bash
# 1. Identify what needs updating
# 2. Make minimal, clear changes
# 3. Update "Last Updated" date
# 4. Commit with clear message
git commit -m "docs: Update [file] to reflect [change]"

# 5. Verify links still work
# 6. Push changes
```

---

## 🔗 Common Commands Reference

### Git Commands
```bash
# Check status
git status

# Recent commits
git log --oneline -10

# Push to staging
git push origin develop

# Create production PR
gh pr create --base main --head develop
```

### Server Access
```bash
# SSH to production
ssh root@167.71.39.50

# Check service status
systemctl status tsh-erp

# View logs
tail -100 /var/www/tsh-erp/logs/backend.log
journalctl -u tsh-erp -n 100
```

### Database Queries
```bash
# Connect to database
PGPASSWORD='TSH@2025Secure!Production' psql -h localhost -U tsh_app_user -d tsh_erp_production

# Common queries
SELECT COUNT(*) FROM products WHERE is_active = true;
SELECT COUNT(*) FROM orders WHERE created_at > NOW() - INTERVAL '1 day';
SELECT * FROM users WHERE role_id = 1 LIMIT 10;
```

### Health Checks
```bash
# All services
curl https://erp.tsh.sale/health
curl https://consumer.tsh.sale/health
curl https://tds.tsh.sale/api/health

# Staging
curl https://staging.erp.tsh.sale/health
```

---

## ✅ Pre-Commit Checklist

```yaml
Before every commit:
□ Code follows naming conventions
□ Arabic fields included (name_ar, description_ar)
□ All 3 authorization layers present (RBAC + ABAC + RLS)
□ Input validation added (Pydantic)
□ Error handling added (try/except)
□ Pagination added (if > 100 records)
□ Database indexes added (foreign keys, search fields)
□ No hardcoded credentials
□ No direct Zoho API calls (use TDS Core)
□ Tests written (if applicable)
□ Tested locally
□ Clear commit message
```

---

**For More Details:**
- Business context: @docs/core/project-context.md
- Technical rules: @docs/core/architecture.md
- Code templates: @docs/reference/code-templates/
- Failsafe protocols: @docs/FAILSAFE_PROTOCOL.md
- Full task patterns: @docs/TASK_PATTERNS.md (original file)
