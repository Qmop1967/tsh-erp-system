# Secret Rotation Checklist - 2025-11-11 17:28:43

## Pre-Rotation Checklist

- [ ] All team members notified
- [ ] Low-traffic window scheduled (6-8 hours)
- [ ] Access to console.anthropic.com verified
- [ ] Access to platform.openai.com verified
- [ ] Access to api-console.zoho.com verified
- [ ] SSH access to production server verified
- [ ] SSH access to staging server verified
- [ ] Current .env files backed up: `/Users/khaleelal-mulla/TSH_ERP_Ecosystem/backups/rotation_20251111_172843`
- [ ] All services status checked (healthy)

---

## Phase 1: Anthropic API Key (30 minutes)

### 1.1 Revoke Old Key
- [ ] Login to https://console.anthropic.com/settings/keys
- [ ] Locate current key: `sk-ant-api03-UW08Cdn1Qnx...`
- [ ] Click "Revoke" button
- [ ] Confirm revocation

### 1.2 Generate New Key
- [ ] Click "Create Key"
- [ ] Name: `TSH-ERP-Production-Nov2025`
- [ ] Copy new key immediately
- [ ] Save to password manager

### 1.3 Update Production
```bash
ssh root@167.71.39.50
cd /opt/tsh_erp
nano .env.production

# Update line:
ANTHROPIC_API_KEY=<NEW_KEY_HERE>

# Restart service
docker-compose restart app

# Test
curl https://erp.tsh.sale/health
```

### 1.4 Update Development
```bash
# On local machine
nano .env

# Update line:
ANTHROPIC_API_KEY=<NEW_KEY_HERE>
```

- [ ] Production updated and tested
- [ ] Development updated
- [ ] Old key confirmed revoked

---

## Phase 2: OpenAI API Key (30 minutes)

### 2.1 Revoke Old Key
- [ ] Login to https://platform.openai.com/api-keys
- [ ] Locate current key: `sk-proj-p9xXSKnoaEw7SA...`
- [ ] Click "Revoke" button
- [ ] Confirm revocation

### 2.2 Generate New Key
- [ ] Click "Create new secret key"
- [ ] Name: `TSH-ERP-Production-Nov2025`
- [ ] Set rate limits (if available)
- [ ] Copy new key immediately
- [ ] Save to password manager

### 2.3 Update Production
```bash
ssh root@167.71.39.50
cd /opt/tsh_erp
nano .env.production

# Update line:
OPENAI_API_KEY=<NEW_KEY_HERE>

# Restart service
docker-compose restart app

# Test
curl https://erp.tsh.sale/health
```

### 2.4 Update Development
```bash
# On local machine
nano .env

# Update line:
OPENAI_API_KEY=<NEW_KEY_HERE>
```

- [ ] Production updated and tested
- [ ] Development updated
- [ ] Old key confirmed revoked

---

## Phase 3: JWT Secret Key (30 minutes)

⚠️ **WARNING:** This will log out ALL users!

### 3.1 Update Production
```bash
ssh root@167.71.39.50
cd /opt/tsh_erp
nano .env.production

# Update line:
SECRET_KEY=7DWLY5JZEYPafjMSnnxGkT6pCQz1EAhqwmwdoc3x38sUM52k9WPZKdX9ORjPVkHbfBsnF_gh0J-2ZUqRAHmCHQ

# Restart service
docker-compose restart app

# Verify
docker-compose logs app | grep -i "started"
```

### 3.2 Update Staging
```bash
ssh khaleel@167.71.58.65
cd /opt/tsh_erp
nano .env.staging

# Update line:
SECRET_KEY=7DWLY5JZEYPafjMSnnxGkT6pCQz1EAhqwmwdoc3x38sUM52k9WPZKdX9ORjPVkHbfBsnF_gh0J-2ZUqRAHmCHQ

# Restart service
docker-compose restart app
```

### 3.3 Update Development
```bash
# On local machine
nano .env

# Update line:
SECRET_KEY=7DWLY5JZEYPafjMSnnxGkT6pCQz1EAhqwmwdoc3x38sUM52k9WPZKdX9ORjPVkHbfBsnF_gh0J-2ZUqRAHmCHQ
```

### 3.4 Test Authentication
```bash
# Test login endpoint
curl -X POST https://erp.tsh.sale/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'

# Should return new JWT token
```

- [ ] Production updated
- [ ] Staging updated
- [ ] Development updated
- [ ] Authentication tested
- [ ] Users notified to re-login

---

## Phase 4: Database Passwords (1 hour)

### 4.1 Production Database
```bash
ssh root@167.71.39.50

# Change PostgreSQL password
sudo -u postgres psql
ALTER USER tsh_admin WITH PASSWORD 'r*$L6phIUZ0n&mCx5A8*bvtgsbt8PYvF';
\q

# Update .env
cd /opt/tsh_erp
nano .env.production

# Update line:
POSTGRES_PASSWORD=r*$L6phIUZ0n&mCx5A8*bvtgsbt8PYvF

# Update docker-compose if needed
nano docker-compose.yml

# Restart services
docker-compose restart postgres app

# Test connection
docker-compose exec app python3 -c "from app.db.database import engine; print('Connected:', engine)"
```

### 4.2 Staging Database
```bash
ssh khaleel@167.71.58.65

# Change PostgreSQL password
sudo -u postgres psql
ALTER USER tsh_admin WITH PASSWORD '#v1DXE&M#*cJdfCI$#fHZ0UUR03oRGuQ';
\q

# Update .env
cd /opt/tsh_erp
nano .env.staging

# Update line:
POSTGRES_PASSWORD=#v1DXE&M#*cJdfCI$#fHZ0UUR03oRGuQ

# Restart services
docker-compose restart postgres app
```

- [ ] Production database password changed
- [ ] Production .env updated
- [ ] Production connection tested
- [ ] Staging database password changed
- [ ] Staging .env updated
- [ ] Staging connection tested

---

## Phase 5: Zoho Books API (2 hours)

### 5.1 Regenerate Client Secret
- [ ] Login to https://api-console.zoho.com/
- [ ] Navigate to your application
- [ ] Click "Regenerate Secret"
- [ ] Copy new CLIENT_SECRET
- [ ] Save to password manager

### 5.2 Generate New Refresh Token
```bash
# On local machine
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem

# Run regeneration script
python3 scripts/regenerate_zoho_token.py

# Follow OAuth flow
# Copy new REFRESH_TOKEN
```

### 5.3 Update Production
```bash
ssh root@167.71.39.50
cd /opt/tsh_erp
nano .env.production

# Update lines:
ZOHO_CLIENT_SECRET=<NEW_SECRET>
ZOHO_REFRESH_TOKEN=<NEW_TOKEN>

# Clear ZOHO_ACCESS_TOKEN (will regenerate)
ZOHO_ACCESS_TOKEN=

# Restart service
docker-compose restart app

# Test Zoho sync
docker-compose logs app | grep -i "zoho"
```

### 5.4 Update Development
```bash
# On local machine
nano .env

# Update lines:
ZOHO_CLIENT_SECRET=<NEW_SECRET>
ZOHO_REFRESH_TOKEN=<NEW_TOKEN>
```

- [ ] Client secret regenerated
- [ ] New refresh token obtained
- [ ] Production updated and tested
- [ ] Development updated
- [ ] Zoho sync verified

---

## Phase 6: Git History Cleanup (2 hours)

⚠️ **WARNING:** This rewrites git history! Team must re-clone!

### 6.1 Backup Repository
```bash
cd /Users/khaleelal-mulla
cp -r TSH_ERP_Ecosystem TSH_ERP_Ecosystem_BACKUP_20251111
```

### 6.2 Install git-filter-repo
```bash
brew install git-filter-repo
```

### 6.3 Remove .env Files
```bash
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem

# Remove .env files from ALL commits
git filter-repo --path .env --path .env.production --path .env.staging --invert-paths

# Verify
git log --all --full-history -- .env
# Should return nothing
```

### 6.4 Force Push
```bash
# Update remote
git remote add origin git@github.com:Qmop1967/tsh-erp-system.git

# Force push (DESTRUCTIVE!)
git push --force --all origin
git push --force --tags origin
```

### 6.5 Notify Team
```
Subject: URGENT: Re-clone TSH ERP Repository

Team,

Git history has been rewritten to remove exposed credentials.

ACTION REQUIRED:
1. Backup any uncommitted local changes
2. Delete your local repository
3. Fresh clone: git clone <repo-url>
4. Restore your local .env file from backup

Timeline: Complete by [DATE]
```

- [ ] Repository backed up locally
- [ ] git-filter-repo installed
- [ ] .env files removed from history
- [ ] Changes force-pushed to remote
- [ ] Team notified to re-clone

---

## Phase 7: GitHub Secrets (1 hour)

### 7.1 Configure Repository Secrets
```bash
# Using gh CLI
gh auth login

# Add secrets
gh secret set PROD_HOST --body "167.71.39.50"
gh secret set PROD_USER --body "root"
gh secret set PROD_SSH_KEY < ~/.ssh/id_rsa

# API Keys
gh secret set ANTHROPIC_API_KEY --body "<NEW_KEY>"
gh secret set OPENAI_API_KEY --body "<NEW_KEY>"

# Zoho
gh secret set ZOHO_CLIENT_ID --body "1000.RYRPK7578ZRKN6K4HKNF4LKL2CC9IQ"
gh secret set ZOHO_CLIENT_SECRET --body "<NEW_SECRET>"
gh secret set ZOHO_REFRESH_TOKEN --body "<NEW_TOKEN>"
gh secret set ZOHO_ORGANIZATION_ID --body "748369814"

# Database
gh secret set POSTGRES_PASSWORD_PROD --body "r*$L6phIUZ0n&mCx5A8*bvtgsbt8PYvF"
gh secret set POSTGRES_PASSWORD_STAGING --body "#v1DXE&M#*cJdfCI$#fHZ0UUR03oRGuQ"

# JWT
gh secret set JWT_SECRET_KEY --body "7DWLY5JZEYPafjMSnnxGkT6pCQz1EAhqwmwdoc3x38sUM52k9WPZKdX9ORjPVkHbfBsnF_gh0J-2ZUqRAHmCHQ"

# Verify
gh secret list
```

### 7.2 Update Workflow Files
- [ ] Review `.github/workflows/*.yml`
- [ ] Ensure secrets are referenced correctly
- [ ] Test workflow runs

- [ ] All secrets added to GitHub
- [ ] Workflows updated
- [ ] Test deployment successful

---

## Phase 8: Verification (1 hour)

### 8.1 Production Services
```bash
# Health check
curl https://erp.tsh.sale/health

# API docs
curl https://erp.tsh.sale/docs

# Test endpoints
curl https://erp.tsh.sale/api/v1/products
curl https://erp.tsh.sale/api/bff/consumer/dashboard
```

### 8.2 Staging Services
```bash
curl https://staging.erp.tsh.sale/health
curl https://staging.erp.tsh.sale/docs
```

### 8.3 Zoho Sync
```bash
ssh root@167.71.39.50
cd /opt/tsh_erp
docker-compose logs app | grep -i "zoho" | tail -50

# Check TDS status
curl http://localhost:8001/health
```

### 8.4 AI Features
```bash
# Test Anthropic
curl -X POST https://erp.tsh.sale/api/v1/ai/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"message":"Hello"}'

# Test OpenAI (if applicable)
```

### 8.5 Mobile Apps
- [ ] Test iOS consumer app
- [ ] Test Android consumer app
- [ ] Test admin app
- [ ] Verify authentication
- [ ] Check BFF endpoints

### 8.6 Logs Review
```bash
# Check for errors
ssh root@167.71.39.50
docker-compose logs --tail=100 app | grep -i "error"

# Should be clean (no credential-related errors)
```

- [ ] All production endpoints responding
- [ ] All staging endpoints responding
- [ ] Zoho sync working
- [ ] AI features working
- [ ] Mobile apps working
- [ ] No errors in logs

---

## Post-Rotation Checklist

- [ ] All services verified as healthy
- [ ] Old credentials confirmed revoked/changed
- [ ] New credentials saved to password manager
- [ ] Team notified of completion
- [ ] Documentation updated
- [ ] Backups verified: `/Users/khaleelal-mulla/TSH_ERP_Ecosystem/backups/rotation_20251111_172843`
- [ ] Monitoring enabled for any issues

---

## Rollback Procedure (If Needed)

If something goes wrong:

1. **Stop making changes**
2. **Restore from backup:**
   ```bash
   cd /opt/tsh_erp
   cp /Users/khaleelal-mulla/TSH_ERP_Ecosystem/backups/rotation_20251111_172843/.env.production .env.production
   docker-compose restart app
   ```
3. **Check logs:**
   ```bash
   docker-compose logs app
   ```
4. **Notify team**
5. **Document issue**
6. **Retry with fix**

---

## Timeline Summary

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Phase 1: Anthropic | 30 min | 0:30 |
| Phase 2: OpenAI | 30 min | 1:00 |
| Phase 3: JWT | 30 min | 1:30 |
| Phase 4: Database | 1 hour | 2:30 |
| Phase 5: Zoho | 2 hours | 4:30 |
| Phase 6: Git History | 2 hours | 6:30 |
| Phase 7: GitHub Secrets | 1 hour | 7:30 |
| Phase 8: Verification | 1 hour | 8:30 |

**Total Time:** 8.5 hours (includes buffer)

---

## Success Criteria

✅ **Rotation Complete When:**
- All old credentials revoked/changed
- All services running with new credentials
- .env files removed from git history
- GitHub Secrets configured
- No errors in logs
- Mobile apps working
- Team notified and re-cloned
- Backups verified

---

**Generated:** 2025-11-11 17:28:43
**Secrets Location:** `/Users/khaleelal-mulla/TSH_ERP_Ecosystem/backups/rotation_20251111_172843/new_secrets.json`
**Backup Location:** `/Users/khaleelal-mulla/TSH_ERP_Ecosystem/backups/rotation_20251111_172843/`

🚀 **Ready to execute!**
