# TDS Dashboard & Core - Deployment Guide

**Date**: November 2, 2024
**Target**: Production Server Deployment
**Method**: CI/CD with Blue/Green Zero-Downtime

---

## 🎯 Deployment Options

You have two deployment options:

### Option 1: GitHub Actions Automated Deployment (Recommended)
- Push to `main` branch triggers automatic deployment
- Runs all tests before deploying
- Zero-downtime blue/green deployment
- Automatic rollback on failure

### Option 2: Manual Server Deployment
- SSH to server and run deployment script
- Full control over deployment process
- Good for initial setup or testing

---

## 📋 Pre-Deployment Checklist

Before deploying, ensure:

- [ ] Production server is available and accessible via SSH
- [ ] Server meets requirements (Ubuntu 20.04+, Python 3.11+, PostgreSQL, Nginx)
- [ ] Production database is set up and accessible
- [ ] GitHub repository has latest code
- [ ] All tests pass locally
- [ ] Environment variables are configured

---

## 🚀 Option 1: Automated GitHub Actions Deployment

### Step 1: Server Initial Setup (One-Time)

SSH into your production server and run these commands:

```bash
# 1. Install required packages
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip postgresql postgresql-client nginx git curl rsync

# 2. Create directory structure
sudo mkdir -p /opt/tsh_erp/{releases/{blue,green},shared/{env,logs/api},venvs,bin}
sudo mkdir -p /opt/backups
sudo chown -R $USER:$USER /opt/tsh_erp /opt/backups

# 3. Create upstream directory for Nginx
sudo mkdir -p /etc/nginx/upstreams
```

### Step 2: Copy Deployment Files to Server

From your local machine:

```bash
# Copy Nginx configurations
scp deployment/nginx/tsh_erp.conf YOUR_SERVER:/tmp/
scp deployment/nginx/tsh_erp_blue.conf YOUR_SERVER:/tmp/
scp deployment/nginx/tsh_erp_green.conf YOUR_SERVER:/tmp/

# On server, move to correct locations
ssh YOUR_SERVER
sudo mv /tmp/tsh_erp.conf /etc/nginx/sites-available/
sudo mv /tmp/tsh_erp_blue.conf /etc/nginx/upstreams/
sudo mv /tmp/tsh_erp_green.conf /etc/nginx/upstreams/
sudo ln -s /etc/nginx/sites-available/tsh_erp.conf /etc/nginx/sites-enabled/
sudo ln -sfn /etc/nginx/upstreams/tsh_erp_blue.conf /etc/nginx/upstreams/tsh_erp_active.conf

# Copy systemd services
exit # exit server
scp deployment/systemd/tsh_erp-blue.service YOUR_SERVER:/tmp/
scp deployment/systemd/tsh_erp-green.service YOUR_SERVER:/tmp/

ssh YOUR_SERVER
sudo mv /tmp/tsh_erp-*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tsh_erp-blue.service
sudo systemctl enable tsh_erp-green.service

# Copy deployment scripts
exit
scp deployment/scripts/*.sh YOUR_SERVER:/tmp/
ssh YOUR_SERVER
sudo mv /tmp/*.sh /opt/tsh_erp/bin/
sudo chmod +x /opt/tsh_erp/bin/*.sh
```

### Step 3: Configure Environment Variables

On the server:

```bash
# Create production environment file
sudo nano /opt/tsh_erp/shared/env/prod.env
```

Add your production configuration:

```env
# Database Configuration
DATABASE_NAME=tsh_erp_production
DATABASE_USER=tsh_app_user
DATABASE_PASSWORD=YOUR_SECURE_PASSWORD
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
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Zoho Integration (if needed)
ZOHO_CLIENT_ID=your_client_id
ZOHO_CLIENT_SECRET=your_client_secret
ZOHO_REFRESH_TOKEN=your_refresh_token
ZOHO_ORGANIZATION_ID=your_org_id
```

Create staging environment for migration testing:

```bash
sudo nano /opt/tsh_erp/shared/env/staging.env
```

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/tsh_erp_staging
```

Set proper permissions:

```bash
sudo chmod 600 /opt/tsh_erp/shared/env/*.env
```

### Step 4: Setup Production Database

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create databases
CREATE DATABASE tsh_erp_production;
CREATE DATABASE tsh_erp_staging;

# Create user
CREATE USER tsh_app_user WITH PASSWORD 'YOUR_SECURE_PASSWORD';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE tsh_erp_production TO tsh_app_user;
GRANT ALL PRIVILEGES ON DATABASE tsh_erp_staging TO tsh_app_user;

\q

# Run initial schema
PGPASSWORD='YOUR_PASSWORD' psql -h localhost -U tsh_app_user -d tsh_erp_production -f /path/to/schema.sql
```

### Step 5: Configure GitHub Secrets

Go to your GitHub repository:
- Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `PROD_HOST` | `your.server.ip` | Production server IP or domain |
| `PROD_USER` | `root` or your user | SSH user for deployment |
| `PROD_SSH_KEY` | Private SSH key content | For authentication |
| `PROD_SSH_PORT` | `22` | SSH port (default 22) |

To generate SSH key:

```bash
# On your server
ssh-keygen -t ed25519 -C "github-actions@tsh.sale" -f ~/.ssh/github_deploy_key -N ""

# Display private key (copy this to GitHub Secrets as PROD_SSH_KEY)
cat ~/.ssh/github_deploy_key

# Add public key to authorized_keys
cat ~/.ssh/github_deploy_key.pub >> ~/.ssh/authorized_keys
```

### Step 6: Update Deployment Script

Edit the repository URL in the deployment script:

```bash
# On server
sudo nano /opt/tsh_erp/bin/deploy.sh

# Find this line and update with your repo URL:
REPO="https://github.com/YOUR_USERNAME/TSH_ERP_Ecosystem.git"
```

### Step 7: Test Nginx Configuration

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Step 8: Run Initial Deployment

```bash
# On server, run first deployment manually
bash /opt/tsh_erp/bin/deploy.sh main

# This will:
# 1. Clone the repository to blue directory
# 2. Create virtual environment
# 3. Install dependencies
# 4. Start the blue service
# 5. Run health checks
# 6. Switch Nginx to blue
```

### Step 9: Verify Deployment

```bash
# Check service status
systemctl status tsh_erp-blue

# Check which color is active
readlink /etc/nginx/upstreams/tsh_erp_active.conf

# Test endpoints
curl http://your-domain.com/ready
curl http://your-domain.com/health
curl http://your-domain.com/queue/stats

# Check logs
tail -f /opt/tsh_erp/shared/logs/api/deploy_*.log
journalctl -u tsh_erp-blue -f
```

### Step 10: Enable Automated Deployments

Now that manual deployment works, push to GitHub to trigger automated deployment:

```bash
# From your local machine
git add .
git commit -m "Enable CI/CD deployment"
git push origin main

# GitHub Actions will:
# 1. Run tests (lint, type-check, security, unit)
# 2. SSH to production server
# 3. Run deployment script
# 4. Deploy to idle color (green)
# 5. Run health checks
# 6. Switch traffic with zero downtime
```

---

## 🔧 Option 2: Manual Deployment

If you prefer manual control or don't have GitHub Actions:

### Quick Manual Deployment

```bash
# SSH to server
ssh your-server

# Run deployment
bash /opt/tsh_erp/bin/deploy.sh main

# Or deploy specific branch
bash /opt/tsh_erp/bin/deploy.sh develop
```

### Manual Deployment Steps Explained

The deployment script performs these steps:

1. **Determine Active Color**: Checks which instance (blue/green) is currently serving traffic
2. **Stop Idle Service**: Stops the idle instance to prepare for new code
3. **Sync Code**: Pulls latest code from GitHub to idle directory
4. **Create/Update Venv**: Sets up Python virtual environment
5. **Install Dependencies**: Installs requirements.txt packages
6. **Backup Database**: Creates pg_dump backup of production DB
7. **Test Migrations**: Runs migrations on staging DB first (safety check)
8. **Start Idle Service**: Starts the newly deployed instance
9. **Health Check**: Waits for `/ready` endpoint to respond (30s timeout)
10. **Switch Traffic**: Updates Nginx symlink to point to new instance
11. **Run Migrations**: Applies migrations to production DB
12. **Stop Old Service**: Stops the previous version
13. **Cleanup**: Removes old log files

---

## 🔄 Rollback Procedure

If something goes wrong after deployment:

```bash
# Instant rollback (takes ~10 seconds)
bash /opt/tsh_erp/bin/rollback.sh

# This will:
# 1. Switch Nginx back to previous version
# 2. Start previous service if stopped
# 3. Stop current service
```

---

## 📊 Monitoring After Deployment

### Check Application Health

```bash
# Via curl
curl http://your-domain.com/health | python3 -m json.tool

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-11-02T...",
  "version": "1.0.0",
  "database": {
    "status": "connected",
    "response_time_ms": 2
  },
  "queue": {
    "pending": 0,
    "processing": 0,
    "failed": 0
  },
  "uptime_seconds": 120
}
```

### Monitor Logs

```bash
# Deployment logs
tail -f /opt/tsh_erp/shared/logs/api/deploy_*.log

# Application logs
journalctl -u tsh_erp-blue -f
journalctl -u tsh_erp-green -f

# Nginx logs
tail -f /var/log/nginx/tsh_erp_access.log
tail -f /var/log/nginx/tsh_erp_error.log
```

### Check Service Status

```bash
# Which color is active?
readlink /etc/nginx/upstreams/tsh_erp_active.conf

# Service status
systemctl status tsh_erp-blue
systemctl status tsh_erp-green

# Port check
lsof -i :8001  # Blue
lsof -i :8002  # Green
```

---

## 🎨 Deploy TDS Dashboard (Frontend)

The TDS Dashboard is a static frontend that can be deployed separately:

### Option A: Deploy with Nginx (Same Server)

```bash
# Build the dashboard
cd tds_dashboard
npm run build

# Copy build to server
scp -r dist/* YOUR_SERVER:/var/www/tds_dashboard/

# Configure Nginx
sudo nano /etc/nginx/sites-available/tds_dashboard.conf
```

Add:

```nginx
server {
    listen 80;
    server_name dashboard.tsh.sale;
    root /var/www/tds_dashboard;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass http://localhost:8001/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/tds_dashboard.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Option B: Deploy to Vercel/Netlify (Recommended for Frontend)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd tds_dashboard
vercel --prod

# Set environment variable
vercel env add VITE_TDS_API_URL production
# Enter: https://api.tsh.sale
```

---

## 🔐 Security Considerations

### Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### SSL/TLS Setup (Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Database Security

```bash
# Limit PostgreSQL to local connections only
sudo nano /etc/postgresql/*/main/pg_hba.conf

# Ensure this line exists:
host    all             all             127.0.0.1/32            md5
```

---

## ✅ Post-Deployment Verification

After deployment, verify:

1. **API Health**
   ```bash
   curl https://your-domain.com/health
   ```

2. **Dashboard Access**
   - Open https://dashboard.tsh.sale
   - Verify all components load
   - Check real-time updates working

3. **Database Connectivity**
   ```bash
   PGPASSWORD='...' psql -h localhost -U tsh_app_user -d tsh_erp_production -c "SELECT COUNT(*) FROM tds_sync_queue;"
   ```

4. **Logs Clean**
   ```bash
   journalctl -u tsh_erp-blue -n 50 --no-pager
   ```

5. **No Errors**
   - Check Nginx error log
   - Check application error log
   - Verify health endpoint returns healthy

---

## 🆘 Troubleshooting

### Deployment Failed

```bash
# Check deployment logs
tail -100 /opt/tsh_erp/shared/logs/api/deploy_*.log

# Check service logs
journalctl -u tsh_erp-blue -n 100

# Manual service start
sudo systemctl start tsh_erp-blue
sudo systemctl status tsh_erp-blue
```

### Health Check Failing

```bash
# Test directly
curl http://localhost:8001/ready
curl http://localhost:8001/health

# Check if service is running
systemctl is-active tsh_erp-blue

# Check logs for errors
journalctl -u tsh_erp-blue -n 50
```

### Database Connection Issues

```bash
# Test database connection
PGPASSWORD='...' psql -h localhost -U tsh_app_user -d tsh_erp_production -c "SELECT 1"

# Check environment file
cat /opt/tsh_erp/shared/env/prod.env | grep DATABASE
```

---

## 📞 Support

**Documentation:**
- Setup Guide: `CI_CD_SETUP_GUIDE.md`
- Quick Reference: `deployment/docs/QUICK_REFERENCE.md`
- This Guide: `DEPLOYMENT_GUIDE.md`

**Common Commands:**
```bash
# Deploy
bash /opt/tsh_erp/bin/deploy.sh main

# Rollback
bash /opt/tsh_erp/bin/rollback.sh

# Check status
systemctl status tsh_erp-blue tsh_erp-green

# View logs
tail -f /opt/tsh_erp/shared/logs/api/*.log
```

---

**Created**: November 2, 2024
**Status**: Production Ready ✅
**Deployment Method**: Blue/Green Zero-Downtime
