# GitHub Workflow Auto-Deployment Setup

## Overview

This document explains the automated deployment workflow that triggers production deployment after staging tests pass successfully.

## Workflow Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Developer pushes to develop/staging branch              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Staging Workflow Runs                                    │
│    - Code Quality Checks                                    │
│    - Database Validation                                    │
│    - Consumer Price List Validation                         │
│    - Unit & Integration Tests                               │
│    - Flutter App Validation                                 │
│    - Data Consistency Check                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ✅ PASS                  ❌ FAIL
         │                       │
         ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│ 3. Create PR to  │    │ Stop - No        │
│    Main Branch   │    │ Production       │
│                  │    │ Deployment      │
└────────┬─────────┘    └──────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Auto-Merge PR (if ENABLE_AUTO_MERGE=true)               │
│    OR Manual Merge Required                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Code Merged to Main                                      │
│    → Triggers Production Workflow                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Production Deployment                                    │
│    - Pre-Deployment Validation                              │
│    - Database Backup                                        │
│    - Data Consistency Check                                 │
│    - Migration Preview                                      │
│    - Service Health Check                                   │
│    - Deploy to Production                                   │
│    - Post-Deployment Monitoring                             │
└─────────────────────────────────────────────────────────────┘
```

## Configuration

### Required GitHub Secrets

1. **Staging Secrets** (for staging workflow):
   - `STAGING_HOST` - Staging server hostname/IP
   - `STAGING_USER` - SSH username for staging
   - `STAGING_SSH_KEY` - SSH private key for staging
   - `STAGING_API_URL` - Staging API URL (optional)
   - `STAGING_DB_URL` - Staging database URL (optional)

2. **Production Secrets** (for production workflow):
   - `PROD_HOST` - Production server hostname/IP (167.71.39.50)
   - `PROD_USER` - SSH username (root)
   - `PROD_SSH_KEY` - SSH private key for production
   - `PROD_SSH_PORT` - SSH port (default: 22)
   - `DB_PASSWORD` - Production database password
   - `DB_USER` - Production database user (tsh_admin)
   - `DB_NAME` - Production database name (tsh_erp)
   - `PRODUCTION_DB_URL` - Production database connection string

3. **Zoho Secrets** (for validation):
   - `ZOHO_ORG_ID` - Zoho organization ID
   - `ZOHO_ACCESS_TOKEN` - Zoho API access token

4. **Optional Auto-Merge Secret**:
   - `ENABLE_AUTO_MERGE` - Set to `"true"` to enable automatic PR merging (default: `"false"`)

### Setting Up Auto-Merge (Optional)

To enable automatic merging of PRs after staging tests pass:

1. Go to GitHub repository → Settings → Secrets and variables → Actions
2. Add a new secret:
   - Name: `ENABLE_AUTO_MERGE`
   - Value: `true`
3. Save the secret

**⚠️ Warning**: Auto-merge will automatically merge PRs to main without manual review. Only enable this if you trust your staging tests completely.

## Workflow Files

### 1. `.github/workflows/deploy-staging.yml`

**Triggers:**
- Push to `develop` or `staging` branches
- Pull requests to `develop` or `staging`
- Manual workflow dispatch

**Stages:**
1. Code Quality & Security Checks
2. Database Schema Validation
3. Consumer Price List Validation (NEW - Critical)
4. Unit & Integration Tests
5. Deploy to Staging Server
6. Flutter Consumer App Validation
7. Data Consistency Check
8. Create PR to Main (if all tests pass)
9. Auto-Merge PR (if enabled)

**Output:**
- Creates PR to main branch if staging tests pass
- Production workflow triggers automatically when PR is merged

### 2. `.github/workflows/intelligent-production.yml`

**Triggers:**
- Push to `main` branch (manual deployment)
- Staging workflow completion (`workflow_run` event)
- Pull requests to `main` (validation only)

**Stages:**
1. Pre-Deployment Validation
   - Verify staging tests passed
   - Check for debug code
   - Security scan
2. Database Backup & Validation
3. Production Data Consistency Check
4. Migration Preview
5. Service Health Check
6. Deploy to Production (Blue-Green)
7. Post-Deployment Monitoring
8. Deployment Summary

**Safety Features:**
- Automatic rollback on failure
- Database backup before deployment
- Health checks after deployment
- Monitoring for 2 minutes post-deployment

## How It Works

### Automatic Deployment Flow

1. **Developer pushes to develop/staging**:
   ```bash
   git push origin develop
   ```

2. **Staging workflow runs automatically**:
   - All validation checks run
   - If all pass → PR created to main
   - If auto-merge enabled → PR auto-merges
   - If auto-merge disabled → Manual merge required

3. **When code is merged to main**:
   - Production workflow triggers automatically
   - Deploys to production server
   - Runs all safety checks

### Manual Deployment Flow

If you need to deploy directly to production without staging:

```bash
git checkout main
git pull origin main
git push origin main
```

This will trigger the production workflow directly (bypasses staging).

## Monitoring

### View Workflow Runs

1. Go to GitHub repository → Actions tab
2. View "🚀 Deploy to Staging" workflow for staging runs
3. View "🎯 Intelligent Production Deployment" workflow for production runs

### Check Deployment Status on Server

```bash
# SSH to production server
ssh root@167.71.39.50

# Check current deployment
cd /home/deploy/TSH_ERP_Ecosystem
git log --oneline -5
git status

# Check service status
docker ps
docker logs tsh_erp_app --tail 50

# Check health endpoint
curl https://erp.tsh.sale/health
```

## Troubleshooting

### Staging Tests Fail

If staging tests fail, production deployment will NOT trigger. Check:
1. Code quality issues
2. Database migration problems
3. Consumer price list validation failures
4. Test failures
5. Flutter app validation issues

### Production Deployment Doesn't Trigger

**Possible causes:**
1. Staging workflow didn't complete successfully
2. PR wasn't merged to main
3. `workflow_run` trigger not working (check GitHub Actions permissions)
4. Production workflow is disabled

**Solution:**
- Check GitHub Actions → Workflows → Check if workflows are enabled
- Verify staging workflow completed successfully
- Ensure PR was merged to main branch
- Check workflow run logs for errors

### Auto-Merge Not Working

**Check:**
1. `ENABLE_AUTO_MERGE` secret is set to `"true"` (string, not boolean)
2. PR was created successfully (check workflow logs)
3. Branch protection rules allow auto-merge
4. PR has required approvals (if configured)

## Best Practices

1. **Always test on staging first**: Never push directly to main
2. **Review PRs before merging**: Even with auto-merge enabled, review critical changes
3. **Monitor production after deployment**: Check logs and health endpoints
4. **Keep staging environment in sync**: Ensure staging mirrors production
5. **Use feature branches**: Create feature branches → develop → staging → main

## Current Server Status

**Production Server:** 167.71.39.50
**Deployment Directory:** `/home/deploy/TSH_ERP_Ecosystem`
**Current Branch on Server:** `main`
**Last Commit:** Check with `git log --oneline -1` on server

## Next Steps

1. ✅ Staging workflow configured
2. ✅ Production workflow configured
3. ✅ Auto-trigger from staging to production configured
4. ⚠️ Set `ENABLE_AUTO_MERGE` secret to `"true"` if you want automatic PR merging
5. ⚠️ Ensure all required GitHub secrets are configured
6. ✅ Test the workflow by pushing to develop/staging branch

---

**Last Updated:** November 2025
**Status:** ✅ Configured and Ready








