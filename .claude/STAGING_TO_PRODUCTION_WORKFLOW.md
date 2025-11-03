# TSH ERP: Staging to Production Workflow

## Overview
This document describes the mandatory staging-first deployment workflow for the TSH ERP Ecosystem. All changes must pass through staging before reaching production.

---

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEVELOPMENT PHASE                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: Local Development & Testing                            │
│ - Work on feature branch or develop branch locally             │
│ - Run tests locally: pytest, flutter test, npm test            │
│ - Verify changes work on localhost                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: Push to Develop Branch (STAGING)                       │
│ Command: git push origin develop                               │
│ Status: ✅ ALLOWED by Claude Code                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: Automated Staging Deployment                           │
│ Trigger: Push to develop branch                                │
│ Workflow: ci-deploy.yml → deploy-staging job                   │
│ Actions:                                                        │
│   ✓ Run tests and security checks                              │
│   ✓ Deploy to staging server (VPS:8002)                        │
│   ✓ Automated health check                                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: Manual Staging Verification ⚠️ CRITICAL                │
│ Test on staging environment:                                    │
│ - Backend API: https://staging.erp.tsh.sale (VPS:8002)         │
│ - Consumer App: https://staging.consumer.tsh.sale              │
│                                                                 │
│ Verification Checklist:                                         │
│ □ All features work as expected                                │
│ □ No errors in console/logs                                    │
│ □ API endpoints respond correctly                              │
│ □ Database migrations applied successfully                     │
│ □ Performance is acceptable                                    │
│ □ Security checks passed                                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────────────┐
                    │ Staging OK?     │
                    └─────────────────┘
                       ↓          ↓
                     YES         NO
                       ↓          ↓
                       ↓    Fix issues → Back to Step 1
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: Create Pull Request (develop → main)                   │
│ Command: gh pr create --base main --head develop               │
│ Title: "Deploy [Feature Name] to Production"                   │
│ Description:                                                    │
│   - What changed                                                │
│   - Staging verification results                               │
│   - Any special deployment notes                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 6: Pull Request Review & Approval                         │
│ - Code review by team lead                                     │
│ - Verify staging test results                                  │
│ - Check for any breaking changes                               │
│ - Approve and merge via GitHub UI                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 7: Automated Production Deployment                        │
│ Trigger: Merge to main branch                                  │
│ Workflow: ci-deploy.yml → deploy job                           │
│ Actions:                                                        │
│   ✓ Run tests and security checks                              │
│   ✓ Deploy to production server (VPS:8001)                     │
│   ✓ Blue-green deployment (zero downtime)                      │
│   ✓ Automated health check                                     │
│   ✓ Rollback on failure                                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 8: Production Verification                                │
│ Automated checks:                                               │
│ ✓ Health endpoint responds: /health                            │
│ ✓ Services running: systemctl status tsh-erp                   │
│ ✓ No errors in logs                                            │
│                                                                 │
│ Manual verification:                                            │
│ - Test critical user flows on production                       │
│ - Monitor error rates for first 15 minutes                     │
│ - Check performance metrics                                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────────────┐
                    │ Production OK?  │
                    └─────────────────┘
                       ↓          ↓
                     YES         NO
                       ↓          ↓
                       ↓    Rollback via GitHub Actions
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT COMPLETE ✅                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Commands Reference

### For Claude Code (Development)

```bash
# ✅ ALLOWED: Push to staging
git add .
git commit -m "feat: add new feature"
git push origin develop

# ✅ ALLOWED: Monitor deployment
gh run list --limit 5
gh run watch <run-id>

# ✅ ALLOWED: Check workflow status
gh workflow list
gh workflow view "CI/CD - Test and Deploy to Production"

# ❌ BLOCKED: Direct push to production
git push origin main  # This will be DENIED by Claude Code
```

### For Manual Operations (Developer)

```bash
# Create PR from develop to main (after staging verification)
gh pr create --base main --head develop \
  --title "Deploy: [Feature Name] to Production" \
  --body "Staging verified ✅ Ready for production"

# Monitor PR status
gh pr list
gh pr view <pr-number>

# Merge PR (triggers production deployment)
gh pr merge <pr-number> --squash
```

### For Emergency Rollback

```bash
# Via GitHub Actions (recommended)
gh workflow run "CI/CD - Test and Deploy to Production" \
  --ref <previous-commit-sha>

# Direct on VPS (emergency only, requires approval)
ssh root@167.71.39.50
sudo systemctl restart tsh-erp
# Or use blue-green switch
bash /opt/tsh_erp/bin/switch_deployment.sh
```

---

## Environment Details

### Staging Environment
- **Branch:** develop
- **Server:** VPS Port 8002
- **URL:** https://staging.erp.tsh.sale (if configured)
- **Purpose:** Pre-production testing and verification
- **Auto-Deploy:** ✅ Yes (on push to develop)
- **Database:** Staging database (isolated from production)

### Production Environment
- **Branch:** main
- **Server:** VPS Port 8001
- **URLs:**
  - Backend API: https://erp.tsh.sale
  - Consumer App: https://consumer.tsh.sale
  - Shop: https://shop.tsh.sale
- **Purpose:** Live customer-facing environment
- **Auto-Deploy:** ✅ Yes (on merge to main)
- **Database:** Production database (127 MB, 57 tables, 2,218 products)

---

## CI/CD Workflow Configuration

### Workflow File: `.github/workflows/ci-deploy.yml`

**Key Jobs:**

1. **test** - Runs on all pushes to develop and main
   - Python linting (ruff)
   - Type checking (mypy)
   - Security scan (bandit)
   - Unit tests (pytest)

2. **deploy-staging** - Runs on push to develop branch
   - Deploys to staging server (VPS:8002)
   - Runs health check
   - Notifies on success/failure

3. **deploy** - Runs on push to main branch (production)
   - Deploys to production server (VPS:8001)
   - Uses blue-green deployment strategy
   - Runs health check
   - Auto-rollback on failure

---

## Safety Mechanisms

### 1. Claude Code Restrictions
Configured in `.claude/settings.local.json`:
```json
{
  "permissions": {
    "allow": ["Bash(git push origin develop)"],
    "deny": [
      "Bash(git push origin main)",
      "Bash(git push -f:*)",
      "Bash(rsync:*root@167.71.39.50:*)"
    ]
  }
}
```

### 2. Branch Protection (GitHub)
Recommended settings for main branch:
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass (CI tests)
- ✅ Require branches to be up to date
- ✅ Include administrators in restrictions
- ❌ Disable force push
- ❌ Disable branch deletion

### 3. Automated Health Checks
All deployments include:
- Health endpoint verification
- Service status check
- Log analysis for errors
- Automatic rollback on failure

---

## Verification Checklist

### Staging Verification (Before Creating PR)
- [ ] Application starts without errors
- [ ] All API endpoints respond correctly
- [ ] Database migrations applied successfully
- [ ] Frontend loads and renders properly
- [ ] Authentication and authorization work
- [ ] Key user flows tested
- [ ] No console errors
- [ ] Performance acceptable
- [ ] Logs show no critical errors

### Production Verification (After Deployment)
- [ ] Health check passes: `curl https://erp.tsh.sale/health`
- [ ] Consumer app accessible: `curl https://consumer.tsh.sale`
- [ ] Backend API responding correctly
- [ ] Services running: `systemctl status tsh-erp`
- [ ] No errors in logs (last 100 lines)
- [ ] Database connections healthy
- [ ] Key user flows tested on production
- [ ] Monitor error rates for 15 minutes

---

## Common Scenarios

### Scenario 1: New Feature Development
```bash
# 1. Work locally on feature
git checkout -b feature/new-dashboard
# ... make changes ...
npm run test
npm run build

# 2. Merge to develop and push
git checkout develop
git merge feature/new-dashboard
git push origin develop

# 3. Wait for staging deployment
gh run list --limit 1

# 4. Test on staging
# ... manual testing ...

# 5. Create PR to main
gh pr create --base main --head develop

# 6. After PR merge, monitor production deployment
gh run watch <run-id>
```

### Scenario 2: Hotfix for Production
```bash
# 1. Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug

# 2. Fix the bug
# ... make changes ...
npm run test

# 3. Push to develop first (staging)
git checkout develop
git merge hotfix/critical-bug
git push origin develop

# 4. Quick verification on staging
# ... test the fix ...

# 5. Create PR to main (expedited)
gh pr create --base main --head develop \
  --title "Hotfix: Critical bug fix" \
  --label "hotfix"

# 6. Fast-track review and merge
```

### Scenario 3: Rollback Production
```bash
# Option 1: Revert commit on main
git revert <problematic-commit-sha>
git push origin main
# This triggers new production deployment with reverted changes

# Option 2: Emergency on-server rollback (requires approval)
# Use blue-green deployment switch
ssh root@167.71.39.50
bash /opt/tsh_erp/bin/switch_deployment.sh
```

---

## Best Practices

### Do's ✅
1. Always test locally before pushing to develop
2. Push to develop (staging) for every change
3. Thoroughly verify on staging before creating PR
4. Write descriptive PR descriptions with test results
5. Monitor deployments through GitHub Actions
6. Keep develop and main branches in sync
7. Document any special deployment requirements
8. Use semantic commit messages

### Don'ts ❌
1. Never push directly to main branch
2. Never use force push (`git push -f`)
3. Never skip staging verification
4. Never deploy manually to production
5. Never merge without PR review
6. Never deploy without running tests
7. Never ignore failing health checks
8. Never make database changes without migrations

---

## Troubleshooting

### Staging Deployment Fails
```bash
# 1. Check GitHub Actions logs
gh run view <run-id> --log-failed

# 2. Check staging server logs
ssh root@167.71.39.50
journalctl -u tsh_erp-green -n 50

# 3. Fix the issue locally
# 4. Push to develop again
```

### Production Deployment Fails
```bash
# 1. Check if rollback happened automatically
gh run view <run-id>

# 2. If not rolled back, trigger manual rollback
ssh root@167.71.39.50
bash /opt/tsh_erp/bin/switch_deployment.sh

# 3. Investigate the issue
# 4. Fix and redeploy through staging first
```

### PR Blocked or Conflicts
```bash
# 1. Sync develop with main
git checkout develop
git pull origin main
git push origin develop

# 2. Resolve conflicts locally
git checkout develop
git merge main
# ... resolve conflicts ...
git push origin develop

# 3. Recreate PR if needed
```

---

## Monitoring and Alerts

### GitHub Actions Monitoring
```bash
# List recent runs
gh run list --limit 10

# Watch specific run
gh run watch <run-id>

# View failed runs
gh run list --status failure --limit 5

# Rerun failed workflow
gh run rerun <run-id>
```

### Server Monitoring
```bash
# Check service status
ssh root@167.71.39.50 "systemctl status tsh-erp"

# Check logs
ssh root@167.71.39.50 "journalctl -u tsh-erp -n 100"

# Check health endpoint
curl https://erp.tsh.sale/health

# Check disk space
ssh root@167.71.39.50 "df -h"
```

---

## Contacts and Support

**For Deployment Issues:**
- Check GitHub Actions logs first
- Review this workflow document
- Contact system administrator if emergency

**Emergency Contacts:**
- System Admin: [Contact Info]
- DevOps Lead: [Contact Info]
- On-call Engineer: [Contact Info]

---

**Document Version:** 1.0
**Last Updated:** November 3, 2025
**Maintained By:** TSH ERP DevOps Team
**Review Frequency:** Quarterly or after major changes
