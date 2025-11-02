# 🚀 TSH ERP System - Deployment Guide

**Repository**: Qmop1967/tsh-erp-system  
**Production Server**: 167.71.39.50 (DigitalOcean Frankfurt)  
**Deployment Status**: ✅ **READY TO DEPLOY**

---

## 🎉 Deployment System is Ready!

Your deployment configuration is complete. You can now deploy to your production server with zero downtime.

---

## 📋 Quick Start (3 Simple Steps)

### Step 1: Configure GitHub Secrets (5 minutes)

Go to: https://github.com/Qmop1967/tsh-erp-system/settings/secrets/actions

Add these 4 secrets:

| Secret Name | Value |
|-------------|-------|
| `PROD_HOST` | `167.71.39.50` |
| `PROD_USER` | `root` |
| `PROD_SSH_PORT` | `22` |
| `PROD_SSH_KEY` | Your SSH private key (see below) |

**To generate SSH key:**
```bash
ssh root@167.71.39.50
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_deploy_key -N ""
cat ~/.ssh/github_deploy_key  # Copy this entire output to PROD_SSH_KEY
cat ~/.ssh/github_deploy_key.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### Step 2: Verify Server is Ready (Optional)

```bash
# Check if server is ready for deployment
./deployment/scripts/check-server-ready.sh 167.71.39.50 root
```

This will verify:
- ✅ SSH connectivity
- ✅ Directory structure
- ✅ Deployment scripts
- ✅ Dependencies (Python, PostgreSQL, Nginx)

### Step 3: Deploy!

**Option A: Automated Deployment (Recommended)**
```bash
git push origin main
```

That's it! GitHub Actions will:
1. ✅ Run tests
2. ✅ Deploy to server
3. ✅ Switch traffic with zero downtime

**Option B: Manual Deployment**
```bash
./deployment/scripts/trigger-deploy.sh
```

---

## 🎯 What This Deployment System Provides

### Zero-Downtime Deployment
- Blue/Green deployment strategy
- One instance serves traffic while the other is updated
- Instant traffic switching via Nginx
- No service interruption

### Automated Testing
- Code linting (ruff)
- Type checking (mypy)
- Security scanning (bandit)
- Unit tests (pytest)
- Only deploys if all tests pass

### Safety Features
- Database backup before each deployment
- Test migrations on staging database first
- Health checks before traffic switching
- Instant rollback capability (~10 seconds)
- Previous version kept running until new version verified

### Monitoring & Logging
- Deployment logs in `/opt/tsh_erp/shared/logs/api/`
- Application logs via `journalctl`
- Health check endpoints
- Service status monitoring

---

## 📊 Deployment Architecture

```
Developer
    ↓
Git Push to main
    ↓
GitHub Actions (Automated)
    ├─ Run Tests
    ├─ SSH to Server
    └─ Execute deploy.sh
        ↓
Production Server (167.71.39.50)
    ├─ Nginx (Port 80/443)
    │   └─ Upstream Switching
    │       ├─ Blue Instance (Port 8001)
    │       └─ Green Instance (Port 8002)
    └─ PostgreSQL Database
```

---

## 🔧 Deployment Tools

### 1. Automated Deployment (GitHub Actions)
File: `.github/workflows/ci-deploy.yml`

Triggers on: Push to `main` branch

**Process:**
1. Runs all tests
2. If tests pass → SSH to production
3. Executes deployment script
4. Reports success/failure

**Time:** ~6-8 minutes from push to live

### 2. Manual Deployment Script
File: `deployment/scripts/trigger-deploy.sh`

**Usage:**
```bash
./deployment/scripts/trigger-deploy.sh
```

**Features:**
- Interactive confirmation
- SSH connectivity check
- Real-time deployment progress
- Error reporting

### 3. Server Readiness Check
File: `deployment/scripts/check-server-ready.sh`

**Usage:**
```bash
./deployment/scripts/check-server-ready.sh 167.71.39.50 root
```

**Checks:**
- SSH connectivity
- Directory structure
- Deployment scripts installed
- Dependencies (Python, PostgreSQL, Nginx)
- Configuration files
- Services status

---

## 📚 Documentation

Your repository includes comprehensive documentation:

| Document | Purpose | Lines |
|----------|---------|-------|
| **DEPLOY_NOW.md** | Quick deployment guide | 367 |
| **DEPLOYMENT_READY.md** | Action required summary | 213 |
| **DEPLOYMENT_GUIDE.md** | Complete deployment manual | 592 |
| **DEPLOYMENT_STATUS.md** | Current production status | 343 |
| **deployment/README.md** | CI/CD system overview | 317 |

---

## 🔄 Common Commands

### Deploy
```bash
# Automated
git push origin main

# Manual
./deployment/scripts/trigger-deploy.sh
```

### Check Status
```bash
# API health
curl http://167.71.39.50/health

# Service status
ssh root@167.71.39.50 'systemctl status tsh_erp-blue tsh_erp-green'

# Which instance is active?
ssh root@167.71.39.50 'readlink /etc/nginx/upstreams/tsh_erp_active.conf'
```

### View Logs
```bash
# Deployment logs
ssh root@167.71.39.50 'tail -f /opt/tsh_erp/shared/logs/api/deploy_*.log'

# Application logs
ssh root@167.71.39.50 'journalctl -u tsh_erp-blue -f'
ssh root@167.71.39.50 'journalctl -u tsh_erp-green -f'
```

### Rollback
```bash
ssh root@167.71.39.50 'bash /opt/tsh_erp/bin/rollback.sh'
```

---

## 🆘 Troubleshooting

### GitHub Actions Fails

**Check:**
1. GitHub Secrets are configured correctly
2. SSH key is valid: `ssh -i ~/.ssh/github_deploy_key root@167.71.39.50`
3. View workflow logs in GitHub Actions tab

### Deployment Fails

**Check:**
```bash
# Deployment logs
ssh root@167.71.39.50 'tail -100 /opt/tsh_erp/shared/logs/api/deploy_*.log'

# Service logs
ssh root@167.71.39.50 'journalctl -u tsh_erp-blue -n 50'

# Rollback if needed
ssh root@167.71.39.50 'bash /opt/tsh_erp/bin/rollback.sh'
```

### Health Check Fails

**Check:**
```bash
# Test endpoints
ssh root@167.71.39.50 'curl http://localhost:8001/ready'
ssh root@167.71.39.50 'curl http://localhost:8002/ready'

# Service status
ssh root@167.71.39.50 'systemctl is-active tsh_erp-blue'
```

---

## 🔐 Security Features

- ✅ SSH key-based authentication
- ✅ GitHub Secrets encryption
- ✅ Environment variables secured (chmod 600)
- ✅ Database backups before migrations
- ✅ Firewall configured (UFW - ports 22, 80, 443)
- ✅ No sensitive data in repository

---

## 📊 What Happens During Deployment

```
1. GitHub Actions detects push to main
2. Runs tests (linting, type-check, security, unit tests)
3. If tests pass → SSH to production server
4. Server determines active instance (blue or green)
5. Deploys to idle instance:
   ├─ Clones latest code
   ├─ Creates Python virtual environment
   ├─ Installs dependencies
   ├─ Backs up production database
   ├─ Tests migrations on staging database
   ├─ Starts new instance
   ├─ Runs health checks (30s timeout)
   └─ If healthy → continues
6. Switches Nginx traffic to new instance (zero downtime!)
7. Applies database migrations to production
8. Stops old instance (kept for rollback)
9. ✅ Deployment complete!
```

**Total time:** 6-8 minutes  
**Downtime:** 0 seconds

---

## ✅ Deployment Checklist

Before deploying:

- [ ] GitHub Secrets configured
- [ ] Server passes readiness check
- [ ] Code changes committed
- [ ] Tests pass locally (optional)

After deploying:

- [ ] Check health endpoint: `curl http://167.71.39.50/health`
- [ ] Verify logs are clean
- [ ] Test key functionality
- [ ] Monitor for errors

---

## 🎯 Next Steps

1. **Configure GitHub Secrets** (see Step 1 above)
2. **Verify server readiness** (optional): `./deployment/scripts/check-server-ready.sh 167.71.39.50 root`
3. **Deploy**: `git push origin main`

---

## 📞 Need Help?

1. **Quick answers**: See `DEPLOYMENT_READY.md`
2. **Complete guide**: See `DEPLOY_NOW.md`
3. **Troubleshooting**: See `DEPLOYMENT_GUIDE.md`
4. **Current status**: See `DEPLOYMENT_STATUS.md`

---

## 🎉 You're Ready!

Your deployment system is fully configured and tested. The infrastructure is ready, the scripts are validated, and the documentation is complete.

**All you need to do is:**
1. Add GitHub Secrets (5 minutes)
2. Push to main

That's it! Your code will be deployed to production with zero downtime. 🚀

---

**Production Server**: http://167.71.39.50  
**Health Check**: http://167.71.39.50/health  
**Status**: ✅ Ready to Deploy

---

*Happy Deploying! 🎊*
