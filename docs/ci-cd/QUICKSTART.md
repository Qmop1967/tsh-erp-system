# CI/CD Quick Start Guide

## Current Status

✅ **PR #4 Merged** - All 34 workflow files are now in the `develop` branch
✅ **Workflows Triggered** - GitHub Actions attempted to run all workflows
⚠️ **Workflows Failed** - Missing required secrets (expected behavior)

## Why Workflows Failed

The workflows are failing because **required GitHub secrets are not configured yet**. This is normal and expected! The workflows are designed to fail fast if secrets are missing to protect your infrastructure.

### Already Configured Secrets ✅

```
PROD_HOST
PROD_SSH_KEY
PROD_SSH_PORT
PROD_USER
STAGING_HOST
STAGING_SSH_KEY
STAGING_USER
VPS_SSH_KEY
ZOHO_CLIENT_ID
ZOHO_CLIENT_SECRET
ZOHO_ORGANIZATION_ID
ZOHO_REFRESH_TOKEN
```

### Missing Critical Secrets ⚠️

```
TELEGRAM_BOT_TOKEN         # Required for notifications
TELEGRAM_CHAT_ID           # Required for notifications
PROD_DB_USER               # Required for database operations
PROD_DB_NAME               # Required for database operations
PROD_DB_PASSWORD           # Required for database operations
STAGING_DB_USER            # Required for testing
STAGING_DB_NAME            # Required for testing
STAGING_DB_PASSWORD        # Required for testing
```

## Quick Setup (5 Minutes)

### Option 1: Interactive Setup (Recommended)

Run the provided configuration script:

```bash
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem
./scripts/configure-github-secrets.sh
```

This script will guide you through setting up all required secrets interactively.

### Option 2: Manual Setup

Set secrets one by one using GitHub CLI:

#### 1. Database Credentials

```bash
# Production Database
gh secret set PROD_DB_USER -b "tsh_app_user"
gh secret set PROD_DB_NAME -b "tsh_erp_production"
gh secret set PROD_DB_PASSWORD  # Will prompt for password

# Staging Database
gh secret set STAGING_DB_USER -b "tsh_app_user"
gh secret set STAGING_DB_NAME -b "tsh_erp_staging"
gh secret set STAGING_DB_PASSWORD  # Will prompt for password
```

#### 2. Telegram Notifications

```bash
# Get Telegram Bot Token from @BotFather
gh secret set TELEGRAM_BOT_TOKEN

# Get your chat ID (send message to @userinfobot)
gh secret set TELEGRAM_CHAT_ID -b "YOUR_CHAT_ID"
```

#### 3. Optional: AWS S3 for Backups

```bash
gh secret set AWS_ACCESS_KEY_ID
gh secret set AWS_SECRET_ACCESS_KEY
gh secret set AWS_REGION -b "eu-north-1"
gh secret set AWS_S3_BUCKET -b "tsh-erp-backups"
```

### Option 3: Get Telegram Bot Token

If you don't have a Telegram bot yet:

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the prompts to create your bot
4. Copy the bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. Create a group or use direct message
6. Add your bot to the group
7. Send a message to the group
8. Get chat ID from: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`

```bash
# Set the secrets
gh secret set TELEGRAM_BOT_TOKEN -b "YOUR_BOT_TOKEN"
gh secret set TELEGRAM_CHAT_ID -b "YOUR_CHAT_ID"
```

## Verify Configuration

After setting secrets, verify they're configured:

```bash
# List all secrets
gh secret list

# Should show at least:
# - TELEGRAM_BOT_TOKEN
# - TELEGRAM_CHAT_ID
# - PROD_DB_USER
# - PROD_DB_NAME
# - PROD_DB_PASSWORD
# - STAGING_DB_USER
# - STAGING_DB_NAME
# - STAGING_DB_PASSWORD
```

## Test the CI/CD Pipeline

### 1. Trigger a Simple Workflow

Start with a workflow that doesn't require many secrets:

```bash
# Trigger the main CI workflow
gh workflow run ci.yml

# Watch it run in real-time
gh run watch
```

### 2. Monitor the Run

```bash
# List recent runs
gh run list --limit 5

# View specific run
gh run view <run-id>

# View logs
gh run view <run-id> --log
```

### 3. Check Telegram

You should receive a notification in your Telegram chat when the workflow completes!

## Expected Results

After configuring secrets:

### ✅ Working Workflows

These workflows should start passing:

- **Main CI** - Code quality, tests, builds
- **Code Quality** - Linting, formatting
- **Unit Tests** - Fast unit tests
- **Docker Build** - Container image builds
- **Notifications** - Telegram messages

### ⚠️ Partially Working

These may still have warnings but won't fail:

- **Integration Tests** - May warn about missing test data
- **Service Validation** - May warn about missing services
- **Security Scan** - May find vulnerabilities to fix

### ❌ Expected to Skip

These workflows won't run on develop branch (designed for specific triggers):

- **Deploy Production** - Manual trigger only
- **Weekly DevOps Report** - Runs Mondays at 9 AM
- **GHCR Cleanup** - Runs Sundays at 3 AM
- **Performance Test** - Manual or scheduled only

## Troubleshooting

### Workflow Still Failing?

1. **Check secret names**:
   ```bash
   gh secret list
   ```
   Ensure names match exactly (case-sensitive)

2. **Check workflow logs**:
   ```bash
   gh run list --limit 1
   gh run view <run-id> --log
   ```

3. **Re-trigger workflow**:
   ```bash
   gh workflow run ci.yml
   ```

### Common Issues

#### Issue: "Secret not found"

```bash
# Solution: Set the missing secret
gh secret set SECRET_NAME
```

#### Issue: "Database connection failed"

```bash
# Solution: Verify database credentials
gh secret set PROD_DB_PASSWORD  # Update password
```

#### Issue: "Telegram notification failed"

```bash
# Solution: Test your bot token
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"

# Should return bot information
# If not, regenerate token from @BotFather
```

## Next Steps After Secrets Are Configured

### 1. Let CI Run Automatically

Once secrets are configured, CI will automatically run on:
- Every push to `main`, `develop`, `feature/*`, `hotfix/*`
- Every pull request to `main` or `develop`

### 2. Enable Scheduled Workflows

These will run automatically:
- **Daily Security Scans** - 2:00 AM UTC
- **Daily Schema Drift Checks** - 1:00 AM UTC
- **Weekly DevOps Reports** - Mondays 9:00 AM UTC
- **Weekly Container Cleanup** - Sundays 3:00 AM UTC
- **Weekly Performance Tests** - Sundays 2:00 AM UTC

### 3. Test Manual Workflows

```bash
# Test schema drift check
gh workflow run schema-drift-check.yml \
  -f environment=staging \
  -f fail_on_drift=false

# Test security scan
gh workflow run security-scan.yml \
  -f scan_type=docker \
  -f fail_on_severity=CRITICAL

# Test performance
gh workflow run performance-test.yml \
  -f target_url=https://staging.erp.tsh.sale \
  -f users=50 \
  -f run_time=2m
```

### 4. Monitor in Telegram

All workflow events will be sent to your Telegram chat:
- ✅ Successful builds
- ❌ Failed builds
- ⚠️ Security alerts
- 📊 Weekly reports
- 🚀 Deployments

## Complete Documentation

For full documentation, see:

- **Main Guide**: `docs/ci-cd/README.md`
- **Workflow Reference**: `docs/ci-cd/workflow-reference.md`
- **Best Practices**: `docs/ci-cd/best-practices.md`
- **Secrets Setup**: `docs/ci-cd/github-secrets-setup.md`

## Getting Help

If you encounter issues:

1. Check the documentation in `docs/ci-cd/`
2. Review workflow logs: `gh run view --log`
3. Check Telegram notifications for errors
4. Review workflow file: `.github/workflows/<workflow-name>.yml`

## Summary

**What happened:**
1. ✅ PR #4 merged successfully to `develop`
2. ✅ All 34 workflow files are now active
3. ⚠️ Workflows failed due to missing secrets (expected)
4. 📝 This quickstart guide created to help you configure secrets

**What you need to do:**
1. Configure missing secrets (5 minutes)
2. Verify secrets are set
3. Trigger a test workflow
4. Monitor in Telegram

**What happens next:**
1. CI runs automatically on every push/PR
2. Security scans run daily
3. Reports sent weekly
4. Deployments available on demand

---

**Ready to go?** Run the configuration script:

```bash
./scripts/configure-github-secrets.sh
```

Or configure manually:

```bash
gh secret set TELEGRAM_BOT_TOKEN
gh secret set TELEGRAM_CHAT_ID
gh secret set PROD_DB_PASSWORD
gh secret set STAGING_DB_PASSWORD
```

Then test:

```bash
gh workflow run ci.yml && gh run watch
```

You're all set! 🚀
