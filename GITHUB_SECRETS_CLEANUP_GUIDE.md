# GitHub Secrets Cleanup Guide

**Date:** January 2025  
**Purpose:** Remove staging-related secrets from GitHub repository

## Overview

Since we've removed all staging configurations, we should also clean up the staging-related secrets from GitHub repository settings. This guide will walk you through the process.

## Steps to Remove Staging Secrets

### 1. Navigate to GitHub Repository Settings

1. Go to your GitHub repository: `https://github.com/YOUR_USERNAME/TSH_ERP_Ecosystem`
2. Click on **Settings** tab (top menu)
3. In the left sidebar, click on **Secrets and variables** → **Actions**

### 2. Identify Staging Secrets to Remove

Look for these secrets (they may or may not exist):

- ❌ `STAGING_HOST`
- ❌ `STAGING_USER`
- ❌ `STAGING_SSH_KEY`
- ❌ `STAGING_SSH_PORT`
- ❌ `STAGING_API_URL`
- ❌ `STAGING_DB_URL`

### 3. Remove Each Secret

For each staging secret found:

1. Click on the secret name
2. Click the **Delete** button (or trash icon)
3. Confirm deletion

**Note:** You can also use the GitHub CLI if you prefer:

```bash
# List all secrets (to see what exists)
gh secret list

# Delete staging secrets (if they exist)
gh secret delete STAGING_HOST
gh secret delete STAGING_USER
gh secret delete STAGING_SSH_KEY
gh secret delete STAGING_SSH_PORT
gh secret delete STAGING_API_URL
gh secret delete STAGING_DB_URL
```

### 4. Verify Required Production Secrets Exist

Make sure these **production secrets** are configured:

✅ **Required Production Secrets:**
- `PROD_HOST` - Production server IP (167.71.39.50)
- `PROD_USER` - SSH username (root)
- `PROD_SSH_KEY` - SSH private key
- `PROD_SSH_PORT` - SSH port (22, optional)
- `PROD_DB_URL` - Production database connection string
- `PROD_API_URL` - Production API URL (optional, defaults to https://erp.tsh.sale)
- `DB_PASSWORD` - Production database password
- `DB_USER` - Production database user
- `DB_NAME` - Production database name

✅ **Zoho Secrets (for validation):**
- `ZOHO_ORG_ID` - Zoho organization ID
- `ZOHO_ACCESS_TOKEN` - Zoho API access token

## Verification

After removing staging secrets:

1. **Test the workflow:**
   - Make a small change to `main` branch
   - Push to trigger the production workflow
   - Check GitHub Actions → "🎯 Production Deployment"
   - Verify it runs without errors

2. **Check workflow logs:**
   - If you see any references to `STAGING_*` secrets, they should be safely ignored
   - The workflow should only use `PROD_*` secrets

## What Happens If Secrets Are Missing?

- **If staging secrets are missing:** ✅ **Good** - They're not needed anymore
- **If production secrets are missing:** ❌ **Bad** - Deployment will fail

The workflow will show clear error messages if required production secrets are missing.

## Summary

✅ **Staging secrets removed** - No longer needed  
✅ **Production secrets verified** - All required secrets exist  
✅ **Workflow tested** - Production deployment works  

---

**Status:** Ready to clean up secrets from GitHub

**Next:** Follow the steps above to remove staging secrets from GitHub repository settings.

