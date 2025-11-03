# TSH ERP - Complete Project Deployment Rules

## ⚠️ CRITICAL RULE: DEPLOY ALL COMPONENTS TOGETHER

**When deploying to production or staging, ALL project components MUST be deployed, not just the backend!**

---

## 📦 TSH ERP Complete Project Components

The TSH ERP Ecosystem consists of **MULTIPLE** components that work together. ALL components must be synchronized:

### 1. **Backend API (Python/FastAPI)**
- **Location:** `/app/` and `/tds_core/`
- **Deployment:** VPS via GitHub Actions
- **Port:** 8000 (production), 8002 (staging)
- **URL:** https://erp.tsh.sale/api
- **Service:** `tsh-erp` / `tsh_erp-blue` / `tsh_erp-green`

### 2. **ERP Admin Frontend (React/TypeScript)**
- **Location:** `/frontend/`
- **Deployment:** VPS static files via Nginx
- **Build Command:** `npm run build`
- **Output:** `/frontend/dist/`
- **URL:** https://erp.tsh.sale
- **Serves:** ERP management interface

### 3. **Consumer App (Flutter Web)**
- **Location:** `/mobile/flutter_apps/10_tsh_consumer_app/`
- **Deployment:** VPS static files via Nginx
- **Build Command:** `flutter build web --release`
- **Output:** `/mobile/flutter_apps/10_tsh_consumer_app/build/web/`
- **URL:** https://consumer.tsh.sale
- **Serves:** Customer-facing shopping interface

### 4. **Admin Mobile App (Flutter)**
- **Location:** `/mobile/flutter_apps/01_tsh_admin_app/`
- **Deployment:** App Store / Play Store (manual)
- **Platform:** iOS & Android
- **Purpose:** Mobile admin management

### 5. **TDS Dashboard**
- **Location:** `/tds_dashboard/`
- **Deployment:** VPS static files via Nginx
- **Purpose:** Zoho sync monitoring dashboard

### 6. **TDS Core Worker**
- **Location:** `/tds_core/`
- **Deployment:** VPS background service
- **Service:** `tds-core-worker`
- **Purpose:** Zoho Books webhook processing

---

## 🚨 THE PROBLEM THAT OCCURRED

### What Went Wrong:
When the user requested to deploy to production by merging develop to main:
- ✅ Backend API was deployed (Python FastAPI)
- ❌ Consumer App (Flutter Web) was NOT deployed
- ❌ ERP Admin Frontend may not have been deployed
- **Result:** Production consumer.tsh.sale showed old code, different from development

### Why This Happened:
1. **CI/CD workflows only deploy the Python backend** (`/app/` and `/tds_core/`)
2. **No Flutter build step** in the deployment pipeline
3. **No frontend build step** in the deployment pipeline
4. **No verification** that all components match the deployed commit

---

## ✅ MANDATORY DEPLOYMENT CHECKLIST

**Before ANY deployment (staging or production), Claude Code MUST:**

### Pre-Deployment Verification:
- [ ] Identify which components have changes in the commit
- [ ] Check if Flutter Consumer App has changes
- [ ] Check if ERP Admin Frontend has changes
- [ ] Check if Backend API has changes
- [ ] Check if TDS Core has changes

### Deployment Execution:
- [ ] Deploy Backend API (Python/FastAPI)
- [ ] Build and deploy ERP Admin Frontend (React)
- [ ] Build and deploy Consumer App (Flutter Web)
- [ ] Deploy TDS Core Worker if changed
- [ ] Deploy TDS Dashboard if changed

### Post-Deployment Verification:
- [ ] Verify Backend API health: `curl https://erp.tsh.sale/health`
- [ ] Verify ERP Admin loads: `curl https://erp.tsh.sale/`
- [ ] Verify Consumer App loads: `curl https://consumer.tsh.sale/`
- [ ] Check all URLs return HTTP 200
- [ ] Verify deployed version matches git commit

---

## 🔧 REQUIRED CI/CD WORKFLOW UPDATES

The deployment workflows MUST include these steps:

### For Production (main branch):
```yaml
jobs:
  deploy-production:
    steps:
      # 1. Deploy Backend
      - name: Deploy Backend API
        run: |
          bash /opt/tsh_erp/bin/deploy.sh main

      # 2. Build and Deploy ERP Admin Frontend
      - name: Build ERP Admin Frontend
        run: |
          cd /opt/tsh_erp/releases/blue/frontend
          npm install
          npm run build

      - name: Deploy ERP Admin Frontend
        run: |
          rsync -av /opt/tsh_erp/releases/blue/frontend/dist/ /var/www/erp.tsh.sale/

      # 3. Build and Deploy Consumer App
      - name: Build Consumer App (Flutter Web)
        run: |
          cd /opt/tsh_erp/releases/blue/mobile/flutter_apps/10_tsh_consumer_app
          flutter build web --release

      - name: Deploy Consumer App
        run: |
          rsync -av /opt/tsh_erp/releases/blue/mobile/flutter_apps/10_tsh_consumer_app/build/web/ /var/www/consumer.tsh.sale/

      # 4. Verify ALL Deployments
      - name: Verify All Components
        run: |
          curl -f https://erp.tsh.sale/health || exit 1
          curl -f https://erp.tsh.sale/ | grep -q "<!DOCTYPE html>" || exit 1
          curl -f https://consumer.tsh.sale/ | grep -q "flutter" || exit 1
```

### For Staging (develop branch):
Same structure, but deploy to staging paths and domains.

---

## 📋 DEPLOYMENT PATHS ON VPS

### Production (main branch):
```
Backend:     /opt/tsh_erp/releases/blue/        → https://erp.tsh.sale/api
Frontend:    /var/www/erp.tsh.sale/             → https://erp.tsh.sale/
Consumer:    /var/www/consumer.tsh.sale/        → https://consumer.tsh.sale/
TDS Core:    /opt/tds_core/                     → Background worker
```

### Staging (develop branch):
```
Backend:     /srv/tsh-staging/                  → Port 8002
Frontend:    /var/www/staging.erp.tsh.sale/     → https://staging.erp.tsh.sale/
Consumer:    /var/www/staging.consumer.tsh.sale/ → https://staging.consumer.tsh.sale/
TDS Core:    /srv/tsh-staging/tds_core/         → Background worker
```

---

## 🎯 CLAUDE CODE MANDATORY ACTIONS

**When the user says:**
- "Deploy to production"
- "Push to main"
- "Merge develop to main"
- "Deploy the project"
- "Update production"

**Claude Code MUST:**

1. **Ask for confirmation** about ALL components:
   ```
   I will deploy ALL TSH ERP components to production:
   ✓ Backend API (Python/FastAPI)
   ✓ ERP Admin Frontend (React)
   ✓ Consumer App (Flutter Web)
   ✓ TDS Core Worker
   ✓ TDS Dashboard

   Do you want to proceed with COMPLETE deployment?
   ```

2. **Check for changes** in each component:
   ```bash
   git diff --name-only origin/main..origin/develop | grep -E "(^app/|^frontend/|^mobile/flutter_apps/10_tsh_consumer_app/|^tds_core/|^tds_dashboard/)"
   ```

3. **Build ALL frontend components BEFORE deploying**:
   ```bash
   # ERP Admin Frontend
   cd frontend && npm install && npm run build

   # Consumer App
   cd mobile/flutter_apps/10_tsh_consumer_app && flutter build web --release
   ```

4. **Deploy ALL components** (not just backend)

5. **Verify ALL components** are accessible and match the deployed commit

---

## ⛔ WHAT CLAUDE CODE MUST NEVER DO AGAIN

### ❌ FORBIDDEN ACTIONS:
1. **Deploy only the backend** when other components have changes
2. **Skip frontend builds** during deployment
3. **Skip consumer app builds** during deployment
4. **Assume CI/CD handles everything** without verification
5. **Complete deployment** without checking all component URLs
6. **Mark deployment as successful** without verifying ALL components

---

## ✅ CORRECT DEPLOYMENT SEQUENCE

### Step 1: Pre-Deployment Checks
```bash
# Check what changed
git diff --name-only origin/main..origin/develop

# If ANY files changed, deploy ALL components
```

### Step 2: Build Frontend Components Locally (Optional)
```bash
# ERP Admin
cd frontend
npm install
npm run build

# Consumer App
cd mobile/flutter_apps/10_tsh_consumer_app
flutter pub get
flutter build web --release
```

### Step 3: Commit and Push to Develop (Staging)
```bash
git add .
git commit -m "feat: Update all components"
git push origin develop
```

### Step 4: Verify Staging Deployment
```bash
# Wait for CI/CD to complete
gh run watch <run-id>

# Verify ALL staging components
curl -f https://staging.erp.tsh.sale/health
curl -f https://staging.erp.tsh.sale/
curl -f https://staging.consumer.tsh.sale/
```

### Step 5: Deploy to Production
```bash
# Merge to main
git checkout main
git merge develop
git push origin main

# Monitor deployment
gh run watch <run-id>
```

### Step 6: Verify Production Deployment
```bash
# Verify ALL production components
curl -f https://erp.tsh.sale/health
curl -f https://erp.tsh.sale/
curl -f https://consumer.tsh.sale/

# Check version in HTML/JS files
curl https://consumer.tsh.sale/ | grep -o 'flutter_bootstrap.js'
```

---

## 🔍 POST-DEPLOYMENT VERIFICATION COMMANDS

**Claude Code MUST run these after EVERY deployment:**

```bash
# 1. Check backend health
curl -s https://erp.tsh.sale/health | python3 -m json.tool

# 2. Check ERP Admin frontend loads
curl -s -I https://erp.tsh.sale/ | grep "HTTP/2 200"

# 3. Check Consumer App loads
curl -s -I https://consumer.tsh.sale/ | grep "HTTP/2 200"

# 4. Verify Consumer App has Flutter
curl -s https://consumer.tsh.sale/ | grep -q "flutter_bootstrap.js" && echo "✅ Consumer App deployed" || echo "❌ Consumer App NOT deployed"

# 5. Check deployed git commit on VPS
ssh root@167.71.39.50 "cd /opt/tsh_erp/releases/blue && git rev-parse HEAD"

# 6. Compare with local commit
git rev-parse HEAD

# Both should match!
```

---

## 📊 DEPLOYMENT STATUS REPORT TEMPLATE

**After deployment, Claude Code MUST provide this report:**

```markdown
# Deployment Status Report

## Deployment Details
- **Date:** [timestamp]
- **Commit:** [git commit hash]
- **Branch:** main/develop
- **Type:** Production/Staging

## Component Deployment Status

### ✅ Backend API (Python/FastAPI)
- Status: Deployed
- Health: Healthy
- URL: https://erp.tsh.sale/health
- Service: tsh_erp-blue (active)

### ✅ ERP Admin Frontend (React)
- Status: Deployed
- Build: Completed
- URL: https://erp.tsh.sale/
- HTTP Status: 200 OK

### ✅ Consumer App (Flutter Web)
- Status: Deployed
- Build: Completed
- URL: https://consumer.tsh.sale/
- HTTP Status: 200 OK
- Flutter Version: [version]

### ✅ TDS Core Worker
- Status: Deployed
- Service: tds-core-worker (active)

### ✅ TDS Dashboard
- Status: Deployed
- URL: https://erp.tsh.sale/tds-dashboard/

## Verification Results
- [ ] All URLs return HTTP 200
- [ ] All services active
- [ ] Git commit matches on VPS
- [ ] Frontend assets updated
- [ ] Flutter app loads correctly

## Issues Found
[List any issues or ❌ if deployment incomplete]
```

---

## 🚀 QUICK REFERENCE COMMANDS

### Check what needs deployment:
```bash
git diff --name-only HEAD~1 HEAD | grep -E "(^app/|^frontend/|^mobile/|^tds_)"
```

### Build all frontend components:
```bash
# ERP Admin
cd frontend && npm run build

# Consumer App
cd mobile/flutter_apps/10_tsh_consumer_app && flutter build web --release
```

### Verify all components:
```bash
curl -f https://erp.tsh.sale/health && \
curl -f https://erp.tsh.sale/ && \
curl -f https://consumer.tsh.sale/ && \
echo "✅ All components accessible"
```

---

## 📝 EXAMPLE CONVERSATION

### ❌ WRONG (What happened before):
```
User: "Please deploy to production"
Claude: *Deploys only backend*
Claude: "✅ Production deployment complete!"
Result: Backend updated, Consumer App still showing old code
```

### ✅ CORRECT (What should happen):
```
User: "Please deploy to production"
Claude: "I'll deploy ALL TSH ERP components to production:
         - Backend API (FastAPI)
         - ERP Admin Frontend (React)
         - Consumer App (Flutter Web)
         - TDS Core Worker
         - TDS Dashboard

         Checking for changes in each component..."

Claude: "Changes detected in:
         - Backend: 12 files
         - Consumer App: 5 files
         - Frontend: 3 files

         Building frontend components..."

Claude: "Deploying all components via CI/CD..."

Claude: "Verifying deployment:
         ✅ Backend: https://erp.tsh.sale/health - Healthy
         ✅ Frontend: https://erp.tsh.sale/ - HTTP 200
         ✅ Consumer: https://consumer.tsh.sale/ - HTTP 200
         ✅ Git commit matches: 6635447

         ✅ ALL components deployed successfully!"
```

---

## 🎓 WHY THIS MATTERS

### The Impact of Incomplete Deployment:
1. **Customer Experience:** Customers see old/broken Consumer App
2. **Business Operations:** Staff see old ERP Admin interface
3. **Data Inconsistency:** Frontend/Backend version mismatch
4. **Trust Issue:** "Why didn't it work when you said it was deployed?"
5. **Debugging Hell:** Hard to diagnose when components are out of sync

### The Solution:
**ALWAYS deploy ALL components together, ALWAYS verify ALL components**

---

## 🔐 RULE ENFORCEMENT

This rule is **MANDATORY** and **NON-NEGOTIABLE**.

**Claude Code will:**
1. ✅ Always check ALL components before deployment
2. ✅ Always deploy ALL components together
3. ✅ Always verify ALL components after deployment
4. ✅ Always report status of ALL components
5. ✅ Never mark deployment complete until ALL components verified

**If Claude Code cannot deploy all components:**
- ❌ DO NOT proceed with partial deployment
- ❌ DO NOT mark deployment as successful
- ✅ WARN the user about missing components
- ✅ ASK for manual intervention if needed

---

## 📅 Rule Created
**Date:** November 3, 2025
**Reason:** Consumer App not deployed to production when backend was deployed
**Priority:** CRITICAL
**Enforcement:** MANDATORY for ALL future deployments

---

**This rule must be followed for EVERY deployment, no exceptions.**
