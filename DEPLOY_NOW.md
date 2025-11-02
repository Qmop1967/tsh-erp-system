# 🚀 Deploy to Server - Quick Start Guide

**Repository**: Qmop1967/tsh-erp-system
**Production Server**: 167.71.39.50 (DigitalOcean Frankfurt)
**Status**: Ready to Deploy

---

## Overview

This repository has a complete CI/CD deployment system configured for zero-downtime blue/green deployment to your production server. This guide will help you complete the deployment setup.

---

## 📋 Prerequisites Checklist

Before deploying, ensure you have:

- [x] Production server running at 167.71.39.50
- [x] GitHub Actions workflow configured (`.github/workflows/ci-deploy.yml`)
- [x] Deployment scripts ready in `deployment/scripts/`
- [ ] GitHub Secrets configured (see below)
- [ ] Server deployment infrastructure set up (see below)

---

## 🔑 Step 1: Configure GitHub Secrets

To enable automated deployment via GitHub Actions, you need to add the following secrets to your repository:

### How to Add Secrets:
1. Go to: https://github.com/Qmop1967/tsh-erp-system/settings/secrets/actions
2. Click "New repository secret"
3. Add each of the following secrets:

### Required Secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `PROD_HOST` | `167.71.39.50` | Production server IP address |
| `PROD_USER` | `root` | SSH user for deployment |
| `PROD_SSH_PORT` | `22` | SSH port (default is 22) |
| `PROD_SSH_KEY` | *Private SSH Key* | See instructions below |

### Generating SSH Key for GitHub Actions:

SSH into your production server and run:

```bash
# SSH to production server
ssh root@167.71.39.50

# Generate deployment SSH key
ssh-keygen -t ed25519 -C "github-actions@tsh-erp" -f ~/.ssh/github_deploy_key -N ""

# Display the private key (copy this to GitHub Secrets as PROD_SSH_KEY)
cat ~/.ssh/github_deploy_key

# Add public key to authorized_keys
cat ~/.ssh/github_deploy_key.pub >> ~/.ssh/authorized_keys

# Set proper permissions
chmod 600 ~/.ssh/authorized_keys
```

Copy the **entire private key** (including the `-----BEGIN OPENSSH PRIVATE KEY-----` and `-----END OPENSSH PRIVATE KEY-----` lines) and add it as the `PROD_SSH_KEY` secret in GitHub.

---

## 🖥️ Step 2: Set Up Server Infrastructure

If you haven't already set up the server deployment infrastructure, follow these steps:

### 2.1. Create Directory Structure

```bash
# SSH to server
ssh root@167.71.39.50

# Create deployment directories
sudo mkdir -p /opt/tsh_erp/{releases/{blue,green},shared/{env,logs/api},venvs,bin}
sudo mkdir -p /opt/backups

# Set ownership (if running as non-root user)
sudo chown -R $USER:$USER /opt/tsh_erp /opt/backups

# Create Nginx upstream directory
sudo mkdir -p /etc/nginx/upstreams
```

### 2.2. Copy Deployment Scripts

From your local machine:

```bash
# Copy deployment scripts to server
scp deployment/scripts/*.sh root@167.71.39.50:/tmp/

# SSH to server and move scripts to /opt/tsh_erp/bin/
ssh root@167.71.39.50
sudo mv /tmp/*.sh /opt/tsh_erp/bin/
sudo chmod +x /opt/tsh_erp/bin/*.sh
```

### 2.3. Copy Nginx Configuration

```bash
# Copy Nginx configs
scp deployment/nginx/tsh_erp.conf root@167.71.39.50:/tmp/
scp deployment/nginx/tsh_erp_blue.conf root@167.71.39.50:/tmp/
scp deployment/nginx/tsh_erp_green.conf root@167.71.39.50:/tmp/

# SSH to server and configure Nginx
ssh root@167.71.39.50

# Move configs to proper locations
sudo mv /tmp/tsh_erp.conf /etc/nginx/sites-available/
sudo mv /tmp/tsh_erp_blue.conf /etc/nginx/upstreams/
sudo mv /tmp/tsh_erp_green.conf /etc/nginx/upstreams/

# Enable site and set initial upstream
sudo ln -s /etc/nginx/sites-available/tsh_erp.conf /etc/nginx/sites-enabled/
sudo ln -sfn /etc/nginx/upstreams/tsh_erp_blue.conf /etc/nginx/upstreams/tsh_erp_active.conf

# Test and reload Nginx
sudo nginx -t
sudo systemctl reload nginx
```

### 2.4. Copy Systemd Services

```bash
# Copy systemd service files
scp deployment/systemd/tsh_erp-blue.service root@167.71.39.50:/tmp/
scp deployment/systemd/tsh_erp-green.service root@167.71.39.50:/tmp/

# SSH to server
ssh root@167.71.39.50

# Install services
sudo mv /tmp/tsh_erp-*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tsh_erp-blue.service
sudo systemctl enable tsh_erp-green.service
```

### 2.5. Configure Environment Variables

```bash
# SSH to server
ssh root@167.71.39.50

# Create production environment file
sudo nano /opt/tsh_erp/shared/env/prod.env
```

Add your production configuration:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://khaleel:Zcbbm.97531tsh@localhost:5432/tsh_erp
DATABASE_NAME=tsh_erp
DATABASE_USER=khaleel
DATABASE_PASSWORD=YOUR_DB_PASSWORD
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Application Settings
ENV=production
DEBUG=False
LOG_LEVEL=INFO
APP_VERSION=1.0.0

# API Configuration
API_PORT_BLUE=8001
API_PORT_GREEN=8002
API_HOST=0.0.0.0

# Security
SECRET_KEY=YOUR_SECURE_SECRET_KEY_HERE
ALGORITHM=HS256

# CORS
CORS_ORIGINS="http://167.71.39.50,http://erp.tsh.sale,https://erp.tsh.sale"
```

**Important**: Update the passwords and secret keys with secure values!

Set proper permissions:
```bash
sudo chmod 600 /opt/tsh_erp/shared/env/prod.env
```

---

## 🎯 Step 3: Deploy Options

You have two ways to deploy:

### Option A: Automated Deployment via GitHub Actions (Recommended)

Once GitHub Secrets are configured:

```bash
# From your local machine
git add .
git commit -m "Deploy to production"
git push origin main
```

GitHub Actions will automatically:
1. ✅ Run tests (linting, type checking, security scan, unit tests)
2. ✅ SSH to production server
3. ✅ Execute deployment script
4. ✅ Deploy to idle instance (blue/green)
5. ✅ Run health checks
6. ✅ Switch traffic with zero downtime
7. ✅ Report status

**Total deployment time**: ~6-8 minutes from push to live

### Option B: Manual Deployment

If you prefer manual control or GitHub Actions aren't available:

```bash
# SSH to production server
ssh root@167.71.39.50

# Run deployment script
bash /opt/tsh_erp/bin/deploy.sh main

# The script will:
# 1. Determine active instance (blue/green)
# 2. Deploy to idle instance
# 3. Create Python virtual environment
# 4. Install dependencies
# 5. Backup database
# 6. Test migrations on staging
# 7. Start new instance
# 8. Run health checks
# 9. Switch Nginx traffic
# 10. Apply production migrations
# 11. Stop old instance

# Verify deployment
curl http://167.71.39.50/health
systemctl status tsh_erp-blue
systemctl status tsh_erp-green
```

---

## ✅ Step 4: Verify Deployment

After deployment, verify everything is working:

### Check API Health
```bash
curl http://167.71.39.50/health | python3 -m json.tool
```

Expected response:
```json
{
  "status": "healthy",
  "database": {
    "status": "healthy",
    "latency_ms": 16.84
  },
  "queue": {
    "pending": 0,
    "processing": 0,
    "failed": 0
  }
}
```

### Check Active Instance
```bash
ssh root@167.71.39.50 'readlink /etc/nginx/upstreams/tsh_erp_active.conf'
# Should show: /etc/nginx/upstreams/tsh_erp_blue.conf or tsh_erp_green.conf
```

### Check Service Status
```bash
ssh root@167.71.39.50 'systemctl status tsh_erp-blue tsh_erp-green'
```

### View Logs
```bash
# Deployment logs
ssh root@167.71.39.50 'tail -f /opt/tsh_erp/shared/logs/api/deploy_*.log'

# Application logs
ssh root@167.71.39.50 'journalctl -u tsh_erp-blue -f'
ssh root@167.71.39.50 'journalctl -u tsh_erp-green -f'
```

---

## 🔄 Rollback Procedure

If something goes wrong after deployment:

```bash
# SSH to server
ssh root@167.71.39.50

# Instant rollback (takes ~10 seconds)
bash /opt/tsh_erp/bin/rollback.sh

# This will:
# 1. Switch Nginx back to previous instance
# 2. Start previous service if stopped
# 3. Stop current service
```

---

## 📊 Deployment Workflow

```
┌─────────────────────────────────────────┐
│  Developer pushes to main branch        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  GitHub Actions: Run Tests              │
│  - Linting (ruff)                       │
│  - Type checking (mypy)                 │
│  - Security scan (bandit)               │
│  - Unit tests (pytest)                  │
└──────────────┬──────────────────────────┘
               │
               ▼ (if tests pass)
┌─────────────────────────────────────────┐
│  GitHub Actions: SSH to Server          │
│  - Connect via SSH                      │
│  - Execute deployment script            │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Server: Blue/Green Deployment          │
│  - Determine active instance            │
│  - Deploy to idle instance              │
│  - Run health checks                    │
│  - Switch Nginx traffic                 │
│  - Zero downtime cutover                │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  ✅ Deployment Complete                 │
│  - New version live                     │
│  - Previous version as backup           │
│  - Instant rollback available           │
└─────────────────────────────────────────┘
```

---

## 🆘 Troubleshooting

### GitHub Actions Deployment Fails

**Check**: Secrets are configured correctly
```bash
# Verify in GitHub: Settings → Secrets and variables → Actions
```

**Check**: SSH key is valid
```bash
# Test SSH connection manually
ssh -i ~/.ssh/github_deploy_key root@167.71.39.50
```

### Manual Deployment Fails

**Check deployment logs**:
```bash
ssh root@167.71.39.50 'tail -100 /opt/tsh_erp/shared/logs/api/deploy_*.log'
```

**Check service logs**:
```bash
ssh root@167.71.39.50 'journalctl -u tsh_erp-blue -n 50'
ssh root@167.71.39.50 'journalctl -u tsh_erp-green -n 50'
```

### Health Check Failing

**Test directly**:
```bash
ssh root@167.71.39.50 'curl http://localhost:8001/ready'
ssh root@167.71.39.50 'curl http://localhost:8002/ready'
```

**Check if service is running**:
```bash
ssh root@167.71.39.50 'systemctl is-active tsh_erp-blue'
ssh root@167.71.39.50 'systemctl is-active tsh_erp-green'
```

### Database Connection Issues

**Test database**:
```bash
ssh root@167.71.39.50 'PGPASSWORD="YOUR_PASSWORD" psql -h localhost -U khaleel -d tsh_erp -c "SELECT 1"'
```

---

## 📚 Additional Documentation

For more detailed information, see:

1. **DEPLOYMENT_GUIDE.md** - Comprehensive deployment instructions
2. **DEPLOYMENT_STATUS.md** - Current production status
3. **GITHUB_ACTIONS_SETUP.md** - CI/CD automation details
4. **deployment/docs/QUICK_REFERENCE.md** - Quick command reference

---

## 🎯 Quick Commands Reference

### Deploy
```bash
# Automated (push to main)
git push origin main

# Manual
ssh root@167.71.39.50 'bash /opt/tsh_erp/bin/deploy.sh main'
```

### Check Status
```bash
curl http://167.71.39.50/health
ssh root@167.71.39.50 'systemctl status tsh_erp-blue tsh_erp-green'
```

### Rollback
```bash
ssh root@167.71.39.50 'bash /opt/tsh_erp/bin/rollback.sh'
```

### View Logs
```bash
ssh root@167.71.39.50 'journalctl -u tsh_erp-green -f'
```

---

## ✅ Final Checklist

Before considering deployment complete:

- [ ] GitHub Secrets configured
- [ ] Server infrastructure set up
- [ ] Environment variables configured
- [ ] Nginx configured and running
- [ ] Systemd services enabled
- [ ] Database accessible
- [ ] First deployment completed successfully
- [ ] Health check passing
- [ ] Logs clean (no errors)
- [ ] Rollback procedure tested

---

**Production Server**: 167.71.39.50
**Repository**: https://github.com/Qmop1967/tsh-erp-system
**Status**: Ready to Deploy 🚀

---

*For support or questions, refer to the comprehensive documentation in the repository.*
