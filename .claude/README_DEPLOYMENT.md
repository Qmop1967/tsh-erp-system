# TSH ERP - Deployment Policy & Procedures

## PRODUCTION DEPLOYMENT POLICY

### ⚠️ CRITICAL RULE: NO DIRECT DEPLOYMENT
**ALL production deployments MUST go through GitHub CI/CD pipeline.**

Direct deployment to production VPS (167.71.39.50) is **STRICTLY PROHIBITED**.

---

## Claude Code Safety Configuration

The following safety measures have been configured in `.claude/settings.local.json`:

### 🚫 Denied Actions:
- `rsync` to production server (167.71.39.50)
- `scp` to production server (167.71.39.50)

### ⚠️ Ask Before Execution:
- Any `ssh` connection to production server (167.71.39.50)
  - Allowed for monitoring/debugging only
  - NOT for deployment actions

### ✅ Allowed Actions:
- GitHub Actions commands (`gh run`, `gh workflow`)
- Git push to main branch (triggers CI/CD)
- Local development commands
- Flutter development commands

---

## Proper Deployment Flow

```
┌─────────────────┐
│ Local Dev       │
│ Environment     │
└────────┬────────┘
         │
         ├──> Code Changes
         ├──> Testing
         ├──> Git Commit
         │
         ▼
┌─────────────────┐
│ Git Push to     │
│ GitHub          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GitHub Actions  │
│ CI/CD Pipeline  │
├─────────────────┤
│ • Run Tests     │
│ • Security Scan │
│ • Build         │
│ • Deploy        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Production VPS  │
│ 167.71.39.50    │
├─────────────────┤
│ • erp.tsh.sale  │
│ • consumer.     │
│   tsh.sale      │
│ • shop.tsh.sale │
└─────────────────┘
```

---

## How to Deploy to Production

### Step 1: Develop & Test Locally
```bash
# Work on your feature branch
git checkout -b feature/your-feature

# Make changes and test locally
flutter run -d chrome  # For Flutter apps
# OR
npm run dev           # For React frontend

# Commit your changes
git add .
git commit -m "Your commit message"
```

### Step 2: Push to GitHub
```bash
# Push your branch
git push origin feature/your-feature

# Create Pull Request on GitHub
# Review and merge to main branch
```

### Step 3: Automatic Deployment
```bash
# Once merged to main, GitHub Actions automatically:
# 1. Runs all tests
# 2. Performs security scans
# 3. Builds the application
# 4. Deploys to production VPS
# 5. Runs health checks
# 6. Sends deployment notification
```

### Step 4: Monitor Deployment
```bash
# Watch deployment progress
gh run watch

# Or view in browser
# https://github.com/Qmop1967/tsh-erp-system/actions
```

---

## Monitoring Production (Read-Only)

You can SSH to production for **monitoring/debugging only**:

```bash
# View logs
ssh root@167.71.39.50 "journalctl -u tsh_erp-* -n 50"

# Check service status
ssh root@167.71.39.50 "systemctl status tsh_erp-blue tsh_erp-green"

# View Nginx status
ssh root@167.71.39.50 "systemctl status nginx"

# Check disk space
ssh root@167.71.39.50 "df -h"

# View application logs
ssh root@167.71.39.50 "tail -f /var/log/tsh-erp/*.log"
```

**⚠️ IMPORTANT:** Do NOT run deployment commands during SSH sessions.

---

## Emergency Rollback

In case of critical issues:

```bash
# View recent deployments
gh run list --workflow=ci-cd.yml --limit 5

# Trigger manual rollback via GitHub Actions
# (if rollback workflow is configured)

# OR contact DevOps team immediately
```

---

## What Claude Code Will Do

When you ask Claude Code to deploy:

1. ✅ **Will help** prepare code for GitHub push
2. ✅ **Will help** create commits and push to GitHub
3. ✅ **Will help** monitor GitHub Actions deployment
4. ✅ **Will help** debug by reading production logs (SSH read-only)
5. ❌ **Will NOT** run rsync/scp to production
6. ❌ **Will NOT** directly modify production files
7. ⚠️ **Will ASK** before any SSH connection to production

---

## Deployment Checklist

Before requesting deployment:

- [ ] All tests passing locally
- [ ] Code reviewed by team member
- [ ] Documentation updated
- [ ] Database migrations prepared (if needed)
- [ ] Environment variables configured
- [ ] Feature flags set correctly
- [ ] Rollback plan identified

---

## Reference Files

- **Deployment Rules:** `.claude/DEPLOYMENT_RULES.md`
- **Settings:** `.claude/settings.local.json`
- **CI/CD Config:** `.github/workflows/ci-cd.yml`
- **Main Deployment Guide:** `DEPLOYMENT.md`

---

## Production Environment Details

- **VPS IP:** 167.71.39.50
- **Provider:** DigitalOcean
- **Location:** Frankfurt
- **OS:** Ubuntu 22.04 LTS
- **Domains:**
  - erp.tsh.sale (Main ERP)
  - consumer.tsh.sale (Consumer App)
  - shop.tsh.sale (Online Store)

---

## Need Help?

1. Check GitHub Actions logs: https://github.com/Qmop1967/tsh-erp-system/actions
2. View production logs (SSH read-only)
3. Contact DevOps team
4. Review this guide: `.claude/README_DEPLOYMENT.md`

---

**Last Updated:** November 3, 2025
**Policy Version:** 1.0
**Enforcement:** Mandatory
