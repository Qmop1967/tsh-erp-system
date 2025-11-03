# TSH ERP Deployment Safety Rules

## CRITICAL: Production Deployment Policy

### Rule #1: NO DIRECT DEPLOYMENT TO PRODUCTION
**All production deployments MUST go through GitHub CI/CD pipeline ONLY.**

### Rule #2: STAGING-FIRST DEPLOYMENT WORKFLOW
**All changes MUST be deployed to staging (develop branch) first, verified, then promoted to production (main branch).**

### Prohibited Actions:
1. ❌ Direct SSH to production VPS for deployment
2. ❌ Direct rsync/scp of files to production
3. ❌ Direct database changes on production
4. ❌ Manual service restarts on production (except emergencies)
5. ❌ Direct git pull on production server
6. ❌ Running deployment scripts manually on production
7. ❌ Pushing directly to main branch from local development
8. ❌ Force pushing to any branch (git push -f)
9. ❌ Skipping staging verification before production

### Allowed Actions:
1. ✅ Push code to develop branch (staging)
2. ✅ Monitor staging deployment via GitHub Actions
3. ✅ Test and verify on staging environment
4. ✅ Create Pull Request from develop to main (after staging verification)
5. ✅ Merge to main branch via GitHub (triggers production CI/CD)
6. ✅ Monitor GitHub Actions workflow
7. ✅ Read-only SSH access for monitoring/debugging
8. ✅ View logs and system status

### Proper Deployment Flow:
```
Local Development
    ↓
Git Commit & Push to develop branch (STAGING)
    ↓
GitHub Actions CI/CD → Deploy to Staging Server
    ↓
Manual Testing & Verification on Staging
    ↓
Create Pull Request: develop → main
    ↓
Review & Approve PR
    ↓
Merge to main branch (PRODUCTION)
    ↓
GitHub Actions CI/CD → Deploy to Production Server
    ↓
Automated Health Checks & Verification
```

### Production Server Details:
- **VPS IP:** 167.71.39.50
- **Domains:** erp.tsh.sale, consumer.tsh.sale, shop.tsh.sale
- **Deployment Method:** GitHub Actions CI/CD ONLY

### Emergency Procedures:
In case of critical production issues:
1. Check GitHub Actions logs first
2. SSH for read-only investigation
3. If rollback needed, use GitHub Actions
4. Document all emergency actions

### Claude Code Instructions:
**Claude Code should NEVER execute these commands:**
- `ssh root@167.71.39.50` followed by deployment commands
- `rsync` or `scp` to 167.71.39.50
- `git push origin main` (direct push to production branch)
- `git push -f` or `git push --force` (force push)
- Any command that modifies production files/database
- Manual service restarts on production

**Claude Code SHOULD:**
- Help with local development and testing
- Prepare code for GitHub push to **develop** branch
- Guide users to use staging-first workflow
- Push commits to `develop` branch only: `git push origin develop`
- Monitor deployment through GitHub Actions
- Help debug by reading logs only
- Remind users to verify on staging before production
- Assist with creating Pull Requests from develop to main

**Deployment Commands Allowed by Claude Code:**
```bash
# ✅ Push to staging (develop branch)
git push origin develop

# ✅ Monitor deployments
gh run list
gh run watch <run-id>

# ✅ View status
gh workflow list
gh pr list

# ❌ BLOCKED: Push to production
git push origin main  # This will be DENIED
```

### Branch Strategy:
- **develop** → Staging environment (automated deployment)
- **main** → Production environment (automated deployment after PR merge)
- **feature/** → Development branches (no automated deployment)

### Environment Mapping:
| Branch | Environment | Server | Auto-Deploy | Verification |
|--------|-------------|--------|-------------|--------------|
| develop | Staging | VPS:8002 | ✅ Yes | Manual testing required |
| main | Production | VPS:8001 | ✅ Yes | Automated health checks |
| feature/* | Local | localhost | ❌ No | Developer testing |

---
**Last Updated:** November 3, 2025
**Enforcement:** Mandatory for all deployments
**Automated Protection:** Enforced via .claude/settings.local.json
