# TSH ERP Deployment Guide

**Master Reference for All Deployment Operations**
Last Updated: November 13, 2025

---

## Table of Contents
1. [Critical Deployment Rules](#critical-deployment-rules)
2. [Project Components](#project-components)
3. [Deployment Workflow](#deployment-workflow)
4. [Pre-Deployment Checklist](#pre-deployment-checklist)
5. [Post-Deployment Verification](#post-deployment-verification)
6. [Docker Deployment](#docker-deployment)
7. [Emergency Procedures](#emergency-procedures)
8. [CI/CD Configuration](#cicd-configuration)

---

## Critical Deployment Rules

### Rule #1: NO DIRECT DEPLOYMENT TO PRODUCTION
**All production deployments MUST go through GitHub CI/CD pipeline ONLY.**

### Rule #2: STAGING-FIRST DEPLOYMENT WORKFLOW
**All changes MUST be deployed to staging (develop branch) first, verified, then promoted to production (main branch).**

### Rule #3: DEPLOY ALL PROJECT COMPONENTS TOGETHER
**⚠️ CRITICAL: When deploying, ALL project components MUST be deployed together - Backend, Frontend, Consumer App, TDS Core, etc. NEVER deploy only the backend!**

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
10. ❌ **Deploying only the backend without frontend/consumer app**
11. ❌ **Marking deployment complete without verifying ALL components**

### Allowed Actions:
1. ✅ Push code to develop branch (staging)
2. ✅ Monitor staging deployment via GitHub Actions
3. ✅ Test and verify on staging environment
4. ✅ Create Pull Request from develop to main (after staging verification)
5. ✅ Merge to main branch via GitHub (triggers production CI/CD)
6. ✅ Monitor GitHub Actions workflow
7. ✅ Read-only SSH access for monitoring/debugging
8. ✅ View logs and system status

---

## Project Components

The TSH ERP Ecosystem consists of **6 main components** that work together:

### 1. Backend API (Python/FastAPI)
- **Location:** `/app/` and `/tds_core/`
- **Deployment:** VPS via GitHub Actions
- **Port:** 8000 (production), 8002 (staging)
- **URL:** https://erp.tsh.sale/api
- **Service:** `tsh-erp` / `tsh_erp-blue` / `tsh_erp-green`
- **Health Check:** `curl https://erp.tsh.sale/health`

### 2. ERP Admin Frontend (React/TypeScript)
- **Location:** `/frontend/`
- **Build Command:** `npm run build`
- **Output:** `/frontend/dist/`
- **URL:** https://erp.tsh.sale
- **Deployment:** Static files via Nginx
- **Serves:** ERP management interface

### 3. Consumer App (Flutter Web)
- **Location:** `/mobile/flutter_apps/10_tsh_consumer_app/`
- **Build Command:** `flutter build web --release`
- **Output:** `/mobile/flutter_apps/10_tsh_consumer_app/build/web/`
- **URL:** https://consumer.tsh.sale
- **Deployment:** Static files via Nginx
- **Serves:** Customer-facing shopping interface

### 4. Admin Mobile App (Flutter)
- **Location:** `/mobile/flutter_apps/01_tsh_admin_app/`
- **Deployment:** App Store / Play Store (manual)
- **Platform:** iOS & Android
- **Purpose:** Mobile admin management

### 5. TDS Dashboard
- **Location:** `/tds_dashboard/`
- **Deployment:** Static files via Nginx
- **URL:** https://erp.tsh.sale/tds-admin
- **Purpose:** Zoho sync monitoring dashboard

### 6. TDS Core Worker
- **Location:** `/tds_core/`
- **Service:** `tds-core-worker`
- **Deployment:** VPS background service
- **Purpose:** Zoho Books webhook processing

---

## Deployment Workflow

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

## Pre-Deployment Checklist

**Before ANY deployment (staging or production), verify:**

### 1. Code Quality
- [ ] All tests passing locally
- [ ] No console errors or warnings
- [ ] Code reviewed (for production deployments)
- [ ] Dependencies updated and secure

### 2. Component Changes Identification
- [ ] Identify which components have changes in the commit
- [ ] Check if Flutter Consumer App has changes
- [ ] Check if ERP Admin Frontend has changes
- [ ] Check if Backend API has changes
- [ ] Check if TDS Core has changes

### 3. Build Verification (if frontend/flutter changed)
- [ ] React frontend builds successfully: `npm run build`
- [ ] Flutter web builds successfully: `flutter build web --release`
- [ ] No build errors or warnings
- [ ] Assets properly bundled

### 4. Database Migrations
- [ ] Database migrations created if schema changed
- [ ] Migration tested on staging first
- [ ] Rollback plan prepared

### 5. Environment Variables
- [ ] All required environment variables documented
- [ ] Secrets updated in GitHub Actions if needed
- [ ] Environment-specific configs verified

---

## Post-Deployment Verification

**After deployment completes, ALWAYS verify ALL components:**

### 1. Health Checks
```bash
# Backend API
curl https://erp.tsh.sale/health

# ERP Admin Frontend
curl -I https://erp.tsh.sale/

# Consumer App
curl -I https://consumer.tsh.sale/

# TDS Dashboard
curl -I https://erp.tsh.sale/tds-admin/
```

All should return HTTP 200 status.

### 2. Functional Testing
- [ ] Login to ERP Admin works
- [ ] Backend API endpoints respond correctly
- [ ] Consumer app loads and functions
- [ ] TDS dashboard shows current sync status
- [ ] Database connections working
- [ ] Zoho webhook processing active

### 3. Version Verification
- [ ] Deployed version matches git commit hash
- [ ] All components on same version
- [ ] Change log updated

### 4. Performance Checks
- [ ] Response times acceptable
- [ ] No memory leaks
- [ ] CPU usage normal
- [ ] Database queries optimized

---

## Docker Deployment

### Production Docker Compose
See [DOCKER_DEPLOYMENT_GUIDE.md](./DOCKER_DEPLOYMENT_GUIDE.md) for detailed Docker instructions.

**Quick Reference:**
```bash
# Build containers
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Docker Services:
- **tsh-erp**: Main backend API
- **tsh-db**: PostgreSQL database
- **tsh-redis**: Redis cache
- **tsh-nginx**: Nginx reverse proxy
- **tds-worker**: TDS background worker

---

## Emergency Procedures

### In Case of Critical Production Issues:

1. **Immediate Assessment**
   - Check GitHub Actions logs first
   - Review application logs: `docker-compose logs -f`
   - Check system resources: CPU, memory, disk

2. **Investigation (Read-Only)**
   - SSH for read-only investigation
   - Query database (SELECT only)
   - Review error logs

3. **Rollback (If Needed)**
   - Revert via GitHub Actions (recommended)
   - Or use blue-green deployment switch
   - Document rollback in incident report

4. **Communication**
   - Notify stakeholders
   - Update status page
   - Document all emergency actions

### Emergency Contacts:
- **System Admin:** [Contact Info]
- **Lead Developer:** [Contact Info]
- **DevOps:** [Contact Info]

---

## CI/CD Configuration

### GitHub Actions Workflows

**Staging Deployment (.github/workflows/deploy-staging.yml)**
- Triggers on: Push to `develop` branch
- Deploys to: Staging server (port 8002)
- Includes: Backend, Frontend, Consumer App

**Production Deployment (.github/workflows/deploy-production.yml)**
- Triggers on: Merge to `main` branch
- Deploys to: Production server (port 8001)
- Includes: Backend, Frontend, Consumer App
- Requires: All tests passing

### Required GitHub Secrets:
```
VPS_HOST=167.71.39.50
VPS_SSH_KEY=<private-key>
POSTGRES_PASSWORD=<secure-password>
REDIS_PASSWORD=<secure-password>
JWT_SECRET=<jwt-secret>
ZOHO_CLIENT_ID=<zoho-client-id>
ZOHO_CLIENT_SECRET=<zoho-client-secret>
```

### Deployment Commands (Automated via CI/CD)

**Backend Deployment:**
```bash
ssh user@vps "cd /var/www/tsh-erp && git pull && docker-compose up -d --build tsh-erp"
```

**Frontend Deployment:**
```bash
cd frontend && npm install && npm run build
rsync -avz dist/ user@vps:/var/www/tsh-erp/frontend/dist/
```

**Consumer App Deployment:**
```bash
cd mobile/flutter_apps/10_tsh_consumer_app
flutter build web --release
rsync -avz build/web/ user@vps:/var/www/tsh-erp/consumer/
```

---

## Production Server Details

- **VPS IP:** 167.71.39.50
- **Domains:**
  - https://erp.tsh.sale (ERP Admin)
  - https://consumer.tsh.sale (Consumer App)
  - https://shop.tsh.sale (Mobile Shop)
- **Deployment Method:** GitHub Actions CI/CD ONLY
- **Operating System:** Ubuntu 22.04 LTS
- **Web Server:** Nginx
- **Database:** PostgreSQL 15
- **Cache:** Redis 7

---

## Claude Code Instructions

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
- **Verify ALL project components after deployment**
- **Build frontend components before deployment**
- **Check that all URLs match deployed git commit**

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

---

## Additional Resources

- **Deployment Checklist:** `docs/deployment/DEPLOYMENT_CHECKLIST.md`
- **Docker Guide:** `.claude/DOCKER_DEPLOYMENT_GUIDE.md`
- **CI/CD Guide:** `docs/ci-cd/CI_CD_GUIDE.md`
- **Maintenance Guide:** `docs/deployment/MAINTENANCE_GUIDE.md`

---

**Enforcement:** Mandatory for all deployments
**Automated Protection:** Enforced via .claude/settings.local.json
**Compliance:** Required for production stability
