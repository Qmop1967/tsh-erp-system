# Direct Deployment Workflow

**TSH ERP System - Production Deployment Guide**

This document describes the **primary and recommended** deployment workflow for the TSH ERP System, which deploys code **directly from the development environment to production** without going through GitHub.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Deployment Workflow](#deployment-workflow)
4. [Step-by-Step Guide](#step-by-step-guide)
5. [Rollback Procedures](#rollback-procedures)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Overview

### Deployment Architecture

```
┌─────────────────────────┐
│  Development Machine    │
│  (Local Environment)    │
│                         │
│  - Code changes         │
│  - Testing              │
│  - Validation           │
└───────────┬─────────────┘
            │
            │ rsync over SSH
            │ (Direct transfer)
            │
            ▼
┌─────────────────────────┐
│  Production VPS         │
│  (tsh-vps)              │
│                         │
│  - Docker rebuild       │
│  - Service restart      │
│  - Health verification  │
└─────────────────────────┘
```

### Why Direct Deployment?

1. **Speed**: No intermediate steps, deploy in seconds
2. **Simplicity**: One command deployment
3. **Control**: Direct visibility into what's being deployed
4. **Reliability**: No dependency on external services (GitHub)
5. **Flexibility**: Easy to rollback or test specific changes

---

## Prerequisites

### 1. SSH Configuration

Ensure SSH access to production is configured:

```bash
# Test SSH connection
ssh tsh-vps

# If not configured, run:
./scripts/setup_local_ssh_config.sh
```

Your `~/.ssh/config` should have:

```
Host tsh-vps
    HostName 45.76.203.47
    User root
    IdentityFile ~/.ssh/id_rsa
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

### 2. Required Tools

- **rsync**: For file synchronization
- **ssh**: For remote access
- **docker** (on production): For containerization
- **git**: For version control (optional, for tracking)

### 3. Permissions

- SSH key authentication to production server
- Write permissions on production directory: `/home/deploy/TSH_ERP_Ecosystem`
- Docker permissions on production server

---

## Deployment Workflow

### Standard Deployment Flow

```bash
# 1. Make your code changes on development machine
vim app/bff/routers/tds.py

# 2. Test locally (optional but recommended)
docker compose up --build

# 3. Deploy directly to production
./scripts/deploy_direct_to_production.sh
```

That's it! The script handles everything automatically.

---

## Step-by-Step Guide

### Phase 1: Pre-Deployment

**On your development machine:**

```bash
# Navigate to project directory
cd /path/to/TSH_ERP_Ecosystem

# Check current status
git status

# Review what will be deployed
git diff

# Optional: Commit changes locally for tracking
git add .
git commit -m "feat: Add new feature"
```

### Phase 2: Deployment

```bash
# Run the direct deployment script
./scripts/deploy_direct_to_production.sh
```

**The script will:**

1. ✅ Validate SSH connection to production
2. ✅ Show you what will be deployed
3. ✅ Ask for confirmation
4. ✅ Sync files using rsync (excluding unnecessary files)
5. ✅ Clear Python cache on production
6. ✅ Rebuild Docker containers
7. ✅ Restart services
8. ✅ Verify health check

**Example output:**

```
╔══════════════════════════════════════════════════════════════════╗
║         DIRECT DEPLOYMENT TO PRODUCTION                          ║
╚══════════════════════════════════════════════════════════════════╝

[1/6] Pre-deployment validation...
✅ Pre-deployment validation passed

[2/6] Checking for changes...
   Current branch: develop
   Last commit: 54724fd - fix(tds): Use sync_entity method
   Modified files: 2

[3/6] Deployment confirmation...
   This will deploy the following to production:
   Source: /Users/khaleelal-mulla/TSH_ERP_Ecosystem
   Target: tsh-vps:/home/deploy/TSH_ERP_Ecosystem

   Continue with deployment? (yes/no): yes

[4/6] Syncing files to production...
✅ Files synced successfully

[5/6] Rebuilding production environment...
   Clearing Python cache...
   Rebuilding Docker containers...
   Restarting containers...
✅ Production environment rebuilt

[6/6] Verifying deployment...
✅ Deployment successful - Service is healthy

╔══════════════════════════════════════════════════════════════════╗
║                 DEPLOYMENT COMPLETED SUCCESSFULLY                 ║
╚══════════════════════════════════════════════════════════════════╝

   TDS Version: 3.0.0
   Status: HEALTHY
   Production URL: https://erp.tsh.sale

🚀 Production deployment complete!
```

### Phase 3: Post-Deployment Verification

```bash
# Verify TDS health
ssh tsh-vps "curl -s http://localhost:8000/api/bff/tds/health"

# Check Docker logs
ssh tsh-vps "docker logs tsh_erp_app --tail 50"

# Monitor in real-time
ssh tsh-vps "docker logs -f tsh_erp_app"
```

---

## Rollback Procedures

### Quick Rollback

If deployment fails or causes issues:

```bash
# Option 1: Rollback using git (if you committed)
git log --oneline  # Find the previous commit hash
git checkout <previous-commit-hash>
./scripts/deploy_direct_to_production.sh

# Option 2: Restore from backup
ssh tsh-vps "cd /home/deploy && ls -la"  # Find backup
ssh tsh-vps "cd /home/deploy && cp -r TSH_ERP_Ecosystem_backup_YYYYMMDD TSH_ERP_Ecosystem"
ssh tsh-vps "cd /home/deploy/TSH_ERP_Ecosystem && docker compose restart app"
```

### Manual Rollback

```bash
# SSH to production
ssh tsh-vps

# Stop services
cd /home/deploy/TSH_ERP_Ecosystem
docker compose down

# Restore previous version
# (copy from backup or re-deploy previous version)

# Restart services
docker compose up -d

# Verify
curl http://localhost:8000/api/bff/tds/health
```

---

## Best Practices

### 1. Test Before Deploying

```bash
# Always test locally first
docker compose build
docker compose up

# Run tests
pytest

# Verify health check
curl http://localhost:8000/api/bff/tds/health
```

### 2. Deploy During Low Traffic

- Prefer off-peak hours
- Inform team before deployment
- Monitor for 10-15 minutes post-deployment

### 3. Keep Backups

```bash
# Create manual backup before risky deployments
ssh tsh-vps "cd /home/deploy && cp -r TSH_ERP_Ecosystem TSH_ERP_Ecosystem_backup_$(date +%Y%m%d_%H%M%S)"
```

### 4. Use Git for Tracking (Optional)

Even though deployment is direct, use git for tracking:

```bash
# Track all changes
git add .
git commit -m "feat: describe your changes"

# Optional: Push to GitHub for backup
git push origin develop
```

### 5. Monitor After Deployment

```bash
# Watch logs for 5 minutes
ssh tsh-vps "docker logs -f tsh_erp_app"

# Check for errors
ssh tsh-vps "docker logs tsh_erp_app | grep -i error"

# Verify metrics
curl https://erp.tsh.sale/api/bff/tds/health
curl https://erp.tsh.sale/api/bff/tds/auto-healing/stats
```

---

## Troubleshooting

### Issue: SSH Connection Failed

```bash
# Error: Cannot connect to production server

# Solution 1: Check SSH config
cat ~/.ssh/config | grep -A 5 tsh-vps

# Solution 2: Test connection
ssh -v tsh-vps

# Solution 3: Re-setup SSH
./scripts/setup_local_ssh_config.sh
```

### Issue: Rsync Permission Denied

```bash
# Error: rsync: permission denied

# Solution: Check permissions on production
ssh tsh-vps "ls -la /home/deploy/TSH_ERP_Ecosystem"

# Fix permissions
ssh tsh-vps "sudo chown -R deploy:deploy /home/deploy/TSH_ERP_Ecosystem"
```

### Issue: Docker Build Failed

```bash
# Error: Docker build failed

# Solution 1: Check logs
ssh tsh-vps "cd /home/deploy/TSH_ERP_Ecosystem && docker compose logs"

# Solution 2: Rebuild manually
ssh tsh-vps "cd /home/deploy/TSH_ERP_Ecosystem && docker compose build --no-cache app"

# Solution 3: Clear Docker cache
ssh tsh-vps "docker system prune -af"
```

### Issue: Service Unhealthy

```bash
# Error: Service health check failed

# Check container status
ssh tsh-vps "docker ps -a | grep tsh_erp"

# Check logs
ssh tsh-vps "docker logs tsh_erp_app --tail 100"

# Restart container
ssh tsh-vps "cd /home/deploy/TSH_ERP_Ecosystem && docker compose restart app"
```

### Issue: Files Not Syncing

```bash
# Error: Some files not appearing on production

# Solution 1: Check exclude patterns in script
cat scripts/deploy_direct_to_production.sh | grep "EXCLUDE_PATTERNS"

# Solution 2: Force sync
rsync -avz --delete /path/to/local/file tsh-vps:/home/deploy/TSH_ERP_Ecosystem/path/

# Solution 3: Manual file copy
scp /path/to/local/file tsh-vps:/home/deploy/TSH_ERP_Ecosystem/path/
```

---

## Quick Reference

### Essential Commands

```bash
# Deploy to production
./scripts/deploy_direct_to_production.sh

# Check production status
ssh tsh-vps "curl -s http://localhost:8000/api/bff/tds/health"

# View production logs
ssh tsh-vps "docker logs tsh_erp_app --tail 50"

# Restart production service
ssh tsh-vps "cd /home/deploy/TSH_ERP_Ecosystem && docker compose restart app"

# Access production shell
ssh tsh-vps
```

### File Locations

| Location | Description |
|----------|-------------|
| `/home/deploy/TSH_ERP_Ecosystem` | Production code directory |
| `/var/log/tsh-erp.log` | Application logs |
| `~/.ssh/config` | SSH configuration |
| `scripts/deploy_direct_to_production.sh` | Deployment script |

---

## Support

For issues or questions:

1. Check this documentation first
2. Review deployment script: `scripts/deploy_direct_to_production.sh`
3. Check production logs: `ssh tsh-vps "docker logs tsh_erp_app"`
4. Contact senior developer

---

**Last Updated**: November 9, 2025
**Version**: 1.0.0
**Status**: Production Ready ✅
