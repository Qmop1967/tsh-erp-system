# GitHub Secrets Setup Guide

This document provides a comprehensive guide for setting up GitHub secrets and environment configuration for the TSH ERP Ecosystem CI/CD pipeline.

## Table of Contents
- [Overview](#overview)
- [GitHub Environments](#github-environments)
- [Required Secrets](#required-secrets)
- [Setup Instructions](#setup-instructions)
- [Security Best Practices](#security-best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

GitHub Secrets are encrypted environment variables that store sensitive information like API keys, passwords, and tokens. They are essential for:
- Deployment automation
- External API integrations (Zoho, AWS, etc.)
- Notifications (Telegram, Email)
- Container registry authentication

---

## GitHub Environments

The TSH ERP project uses three environments:

### 1. Production Environment
- **Name:** `production`
- **URL:** https://erp.tsh.sale
- **Protection Rules:**
  - Require 2 manual approvals before deployment
  - Restrict to `main` branch only
  - Deployment timeout: 30 minutes

### 2. Staging Environment
- **Name:** `staging`
- **URL:** https://staging.erp.tsh.sale
- **Protection Rules:**
  - Auto-deploy from `develop` branch
  - No manual approval required
  - Deployment timeout: 20 minutes

### 3. Development Environment
- **Name:** `development`
- **URL:** Local or development server
- **Protection Rules:**
  - No restrictions
  - Used for testing workflows

---

## Required Secrets

### SSH Access Secrets

#### Production Server
```
PROD_HOST=167.71.39.50
PROD_USER=root
PROD_SSH_KEY=<private-ssh-key-content>
PROD_SSH_PORT=22  # Optional, defaults to 22
```

#### Staging Server
```
STAGING_HOST=167.71.58.65
STAGING_USER=khaleel
STAGING_SSH_KEY=<private-ssh-key-content>
STAGING_SSH_PORT=22  # Optional
```

**How to Generate SSH Keys:**
```bash
# On your local machine
ssh-keygen -t ed25519 -C "github-actions@tsh.sale" -f ~/.ssh/github_actions_tsh_erp

# Copy the private key (this goes to GitHub Secrets)
cat ~/.ssh/github_actions_tsh_erp

# Copy the public key (this goes to server's authorized_keys)
cat ~/.ssh/github_actions_tsh_erp.pub

# Add public key to server
ssh root@167.71.39.50
mkdir -p ~/.ssh
echo "<public-key-content>" >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

---

### Zoho Integration Secrets

```
ZOHO_CLIENT_ID=<your-zoho-client-id>
ZOHO_CLIENT_SECRET=<your-zoho-client-secret>
ZOHO_REFRESH_TOKEN=<your-zoho-refresh-token>
ZOHO_ORGANIZATION_ID=748369814
ZOHO_ACCESS_TOKEN=<generated-by-tds-core>  # Optional
```

**How to Get Zoho Credentials:**
1. Log in to [Zoho API Console](https://api-console.zoho.com/)
2. Create a new Self Client application
3. Generate authorization code with scopes: `ZohoBooks.fullaccess.all`
4. Exchange authorization code for refresh token
5. Store credentials in GitHub Secrets

**TDS Core handles token refresh automatically**, so you only need to set the refresh token once.

---

### Database Secrets

#### Application Database Connection
```
DATABASE_URL=postgresql://user:password@host:5432/database
REDIS_URL=redis://:password@host:6379/0
```

**Format:**
- PostgreSQL: `postgresql://[user]:[password]@[host]:[port]/[database]`
- Redis: `redis://:[password]@[host]:[port]/[db]`

**Example:**
```
DATABASE_URL=postgresql://tsh_app_user:TSH@2025Secure!Production@localhost:5432/tsh_erp_production
REDIS_URL=redis://:your-redis-password@localhost:6379/0
```

#### Schema Drift Detection Database Secrets

**Production Database (Read-Only Access Recommended):**
```
PROD_DB_HOST=167.71.39.50
PROD_DB_PORT=5432
PROD_DB_NAME=tsh_erp_production
PROD_DB_USER=tsh_app_user
PROD_DB_PASSWORD=<production-database-password>
```

**Staging Database:**
```
STAGING_DB_HOST=167.71.58.65
STAGING_DB_PORT=5432
STAGING_DB_NAME=tsh_erp_staging
STAGING_DB_USER=tsh_app_user
STAGING_DB_PASSWORD=<staging-database-password>
```

**Security Note:** For schema drift detection, it's recommended to create a read-only database user:

```sql
-- Create read-only user for schema drift checks
CREATE USER schema_checker WITH PASSWORD '<secure-password>';
GRANT CONNECT ON DATABASE tsh_erp_production TO schema_checker;
GRANT USAGE ON SCHEMA public TO schema_checker;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO schema_checker;

-- Allow access to schema metadata
GRANT SELECT ON information_schema.tables TO schema_checker;
GRANT SELECT ON information_schema.columns TO schema_checker;
```

---

### AWS S3 Secrets (for Database Backups)

```
AWS_ACCESS_KEY_ID=<your-aws-access-key>
AWS_SECRET_ACCESS_KEY=<your-aws-secret-key>
AWS_S3_BUCKET=tsh-erp-backups
AWS_REGION=eu-north-1  # Optional, defaults to us-east-1
```

**How to Create AWS Credentials:**
1. Log in to AWS Console
2. Go to IAM → Users → Create User
3. Attach policy: `AmazonS3FullAccess` (or create custom policy)
4. Generate access key
5. Store in GitHub Secrets

**Recommended Custom S3 Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::tsh-erp-backups",
        "arn:aws:s3:::tsh-erp-backups/*"
      ]
    }
  ]
}
```

---

### Security & Authentication Secrets

```
JWT_SECRET_KEY=<64-character-random-string>
SECRET_KEY=<32-character-random-string>  # For general encryption
```

**How to Generate Secure Keys:**
```bash
# Generate JWT secret key (64 chars)
openssl rand -hex 64

# Generate secret key (32 chars)
openssl rand -hex 32

# Alternative using Python
python3 -c "import secrets; print(secrets.token_hex(64))"
```

---

### Notification Secrets

#### Telegram Bot
```
TELEGRAM_BOT_TOKEN=<your-bot-token>
TELEGRAM_CHAT_ID=<your-chat-id>
```

**How to Set Up Telegram Bot:**
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow instructions
3. Copy the bot token (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
4. Add bot to your group/channel
5. Get chat ID:
   ```bash
   # Send a message to the bot, then run:
   curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   # Look for "chat":{"id":<CHAT_ID>}
   ```

#### Email SMTP
```
EMAIL_SMTP_HOST=smtp.gmail.com  # Or your SMTP server
EMAIL_SMTP_PORT=465             # 587 for TLS, 465 for SSL
EMAIL_SMTP_USER=devops@tsh.sale
EMAIL_SMTP_PASSWORD=<app-password>
EMAIL_NOTIFICATION_TO=khaleel@tsh.sale,management@tsh.sale
EMAIL_NOTIFICATION_FROM=github-actions@tsh.sale
```

**Gmail App Password Setup:**
1. Enable 2-Factor Authentication on your Google account
2. Go to Google Account → Security → App passwords
3. Generate app password for "Mail"
4. Use the generated 16-character password

---

### Code Coverage & Quality

```
CODECOV_TOKEN=<your-codecov-token>  # Optional but recommended
```

**How to Get Codecov Token:**
1. Sign up at [codecov.io](https://codecov.io)
2. Add your repository
3. Copy the upload token
4. Add to GitHub Secrets

---

## Setup Instructions

### Step 1: Access GitHub Settings
1. Navigate to your repository on GitHub
2. Go to **Settings** → **Secrets and variables** → **Actions**

### Step 2: Create Environments
1. Go to **Settings** → **Environments**
2. Click **New environment**
3. Create three environments: `production`, `staging`, `development`
4. Configure protection rules (see [GitHub Environments](#github-environments))

### Step 3: Add Repository Secrets
1. Click **New repository secret**
2. Enter secret name and value
3. Click **Add secret**
4. Repeat for all secrets listed above

### Step 4: Add Environment-Specific Secrets
1. Go to **Settings** → **Environments**
2. Click on an environment (e.g., `production`)
3. Scroll to **Environment secrets**
4. Add environment-specific secrets (e.g., `PROD_HOST` for production)

### Step 5: Verify Secrets
Run this workflow to verify secrets are configured correctly:
```bash
# Trigger the secret validation workflow
gh workflow run ci.yml --ref develop
```

---

## Security Best Practices

### 1. Secret Rotation
- **SSH Keys:** Rotate every 6 months
- **API Tokens:** Rotate every 3 months
- **Database Passwords:** Rotate quarterly
- **JWT Secret:** Rotate annually

### 2. Access Control
- Limit who can view/modify secrets (repository admins only)
- Use environment protection rules for production
- Require code reviews before merging to `main`

### 3. Avoid Hardcoding
- Never commit secrets to code
- Use `.env` files locally (add to `.gitignore`)
- Always use `${{ secrets.SECRET_NAME }}` in workflows

### 4. Audit Logging
- Regularly review GitHub Actions logs
- Monitor for unauthorized access attempts
- Enable GitHub security alerts

### 5. Encryption
- All GitHub Secrets are encrypted at rest
- Secrets are not exposed in workflow logs
- Use `::add-mask::` for additional masking in outputs

---

## Secret Organization

### Repository-Level Secrets
Use for secrets shared across all environments:
- `CODECOV_TOKEN`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `EMAIL_SMTP_HOST`
- `EMAIL_SMTP_USER`
- `EMAIL_SMTP_PASSWORD`

### Environment-Level Secrets
Use for environment-specific secrets:
- **Production:**
  - `PROD_HOST`
  - `PROD_USER`
  - `PROD_SSH_KEY`
  - `DATABASE_URL` (production DB)
  - `ZOHO_ORGANIZATION_ID`

- **Staging:**
  - `STAGING_HOST`
  - `STAGING_USER`
  - `STAGING_SSH_KEY`
  - `DATABASE_URL` (staging DB)

---

## Troubleshooting

### Issue: Deployment fails with "Permission denied (publickey)"
**Solution:**
1. Verify SSH key is correctly formatted (no extra spaces/newlines)
2. Ensure public key is in server's `~/.ssh/authorized_keys`
3. Check SSH key permissions on server (`chmod 600 ~/.ssh/authorized_keys`)
4. Test SSH connection manually:
   ```bash
   ssh -i /path/to/private_key user@host
   ```

### Issue: Zoho API returns "invalid_token"
**Solution:**
1. Refresh token may have expired (check Zoho console)
2. Verify `ZOHO_CLIENT_ID` and `ZOHO_CLIENT_SECRET` are correct
3. Regenerate refresh token if needed
4. Ensure TDS Core is running and handling token refresh

### Issue: Telegram notifications not received
**Solution:**
1. Verify bot token is correct
2. Ensure bot is added to the group/channel
3. Check chat ID is correct (positive for private chats, negative for groups)
4. Test bot manually:
   ```bash
   curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/sendMessage" \
     -d chat_id="<CHAT_ID>" \
     -d text="Test message"
   ```

### Issue: Docker build fails with authentication error
**Solution:**
1. Verify `GITHUB_TOKEN` has `packages: write` permission
2. Check GitHub Container Registry access
3. Ensure repository visibility allows package access
4. Re-authenticate to GHCR:
   ```bash
   echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
   ```

### Issue: Database connection fails
**Solution:**
1. Verify `DATABASE_URL` format is correct
2. Check database server is accessible from GitHub Actions runners
3. Ensure firewall allows connections from GitHub's IP ranges
4. Test connection locally:
   ```bash
   psql "postgresql://user:pass@host:5432/dbname" -c "SELECT 1"
   ```

---

## Secrets Checklist

Use this checklist to ensure all secrets are configured:

### SSH Access
- [ ] `PROD_HOST`
- [ ] `PROD_USER`
- [ ] `PROD_SSH_KEY`
- [ ] `STAGING_HOST`
- [ ] `STAGING_USER`
- [ ] `STAGING_SSH_KEY`

### Zoho Integration
- [ ] `ZOHO_CLIENT_ID`
- [ ] `ZOHO_CLIENT_SECRET`
- [ ] `ZOHO_REFRESH_TOKEN`
- [ ] `ZOHO_ORGANIZATION_ID`

### Database & Cache
- [ ] `DATABASE_URL` (production)
- [ ] `DATABASE_URL` (staging)
- [ ] `REDIS_URL` (production)
- [ ] `REDIS_URL` (staging)

### AWS S3
- [ ] `AWS_ACCESS_KEY_ID`
- [ ] `AWS_SECRET_ACCESS_KEY`
- [ ] `AWS_S3_BUCKET`

### Security
- [ ] `JWT_SECRET_KEY`
- [ ] `SECRET_KEY`

### Notifications
- [ ] `TELEGRAM_BOT_TOKEN`
- [ ] `TELEGRAM_CHAT_ID`
- [ ] `EMAIL_SMTP_HOST`
- [ ] `EMAIL_SMTP_USER`
- [ ] `EMAIL_SMTP_PASSWORD`

### Optional
- [ ] `CODECOV_TOKEN`
- [ ] `EMAIL_NOTIFICATION_TO`
- [ ] `EMAIL_NOTIFICATION_FROM`

---

## Quick Reference

### Accessing Secrets in Workflows
```yaml
steps:
  - name: Use secret
    run: echo "Value: ${{ secrets.SECRET_NAME }}"
    env:
      API_KEY: ${{ secrets.API_KEY }}
```

### Accessing Secrets in Shell Scripts
```bash
#!/bin/bash
# Secrets are passed as environment variables
echo "Deploying to $PROD_HOST"
ssh $PROD_USER@$PROD_HOST "cd /app && git pull"
```

### Conditional Secrets
```yaml
steps:
  - name: Deploy (only if secrets exist)
    if: ${{ secrets.PROD_SSH_KEY != '' }}
    run: ./deploy.sh
```

---

## Support

For questions or issues related to GitHub secrets:
- **Documentation:** https://docs.github.com/en/actions/security-guides/encrypted-secrets
- **TSH ERP Team:** devops@tsh.sale
- **GitHub Issues:** https://github.com/tsh-erp/ecosystem/issues

---

**Last Updated:** 2025-01-11
**Version:** 1.0.0
**Maintained by:** TSH DevOps Team
