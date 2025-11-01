# TSH ERP - Production Deployment Status

**Server**: 167.71.39.50 (DigitalOcean - Frankfurt)
**Date**: November 2, 2024
**OS**: Ubuntu 22.04.5 LTS

---

## ✅ Completed Steps

### 1. Server Connection
- ✅ SSH access verified
- ✅ Server: root@167.71.39.50
- ✅ Hostname: ubuntu-s-2vcpu-4gb-fra1-01

### 2. Dependencies Installed
- ✅ Python 3.10.12
- ✅ PostgreSQL 17.6
- ✅ Nginx 1.18.0
- ✅ Git 2.34.1
- ✅ python3-venv, python3-pip
- ✅ rsync, curl
- ✅ certbot, python3-certbot-nginx

### 3. Directory Structure Created
```
/opt/tsh_erp/
├── releases/
│   ├── blue/
│   └── green/
├── shared/
│   ├── env/
│   └── logs/api/
├── venvs/
└── bin/
    ├── deploy.sh
    ├── rollback.sh
    ├── healthcheck.sh
    └── switch_upstream.sh

/opt/backups/
/etc/nginx/upstreams/
```

### 4. Deployment Files Copied
- ✅ Nginx configuration
- ✅ Systemd services (blue & green)
- ✅ Deployment scripts

### 5. Services Configured
- ✅ tsh_erp-blue.service enabled
- ✅ tsh_erp-green.service enabled
- ✅ Nginx configured and running

---

## 🔄 Next Steps Required

### 1. Create Production Environment File

```bash
ssh root@167.71.39.50

cat > /opt/tsh_erp/shared/env/prod.env << 'EOF'
# Database (Supabase)
DATABASE_URL=postgresql://postgres.trjjglxhteqnzmyakxhe:Zcbbm.97531tsh@aws-1-eu-north-1.pooler.supabase.com:5432/postgres

# Application
ENV=production
DEBUG=False
LOG_LEVEL=INFO
APP_VERSION=1.0.0

# API
API_HOST=0.0.0.0
API_PORT_BLUE=8001
API_PORT_GREEN=8002

# Security
SECRET_KEY=CHANGE_THIS_TO_STRONG_RANDOM_KEY
ALGORITHM=HS256

# CORS
CORS_ORIGINS=["http://167.71.39.50", "http://erp.tsh.sale", "https://erp.tsh.sale"]
EOF

chmod 600 /opt/tsh_erp/shared/env/prod.env
```

### 2. Update Deployment Script with Repo URL

```bash
ssh root@167.71.39.50
nano /opt/tsh_erp/bin/deploy.sh

# Update this line (around line 15):
REPO="https://github.com/YOUR_USERNAME/TSH_ERP_Ecosystem.git"
# Change to your actual GitHub repo URL
```

### 3. Run First Deployment

```bash
ssh root@167.71.39.50
bash /opt/tsh_erp/bin/deploy.sh main
```

This will:
1. Clone code to blue directory
2. Create virtual environment
3. Install dependencies from requirements.txt
4. Start blue service on port 8001
5. Run health checks
6. Switch Nginx to blue

### 4. Verify Deployment

```bash
# Check service status
systemctl status tsh_erp-blue

# Test endpoints
curl http://167.71.39.50/ready
curl http://167.71.39.50/health
curl http://167.71.39.50/queue/stats

# Check logs
journalctl -u tsh_erp-blue -f
```

### 5. Setup Firewall

```bash
ssh root@167.71.39.50

ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw --force enable
ufw status
```

### 6. Setup SSL/TLS (Optional but Recommended)

If you have a domain pointing to 167.71.39.50:

```bash
ssh root@167.71.39.50

# Update Nginx server_name with your domain
nano /etc/nginx/sites-available/tsh_erp.conf
# Change: server_name erp.tsh.sale www.tsh.sale;
# To your actual domain

# Get SSL certificate
certbot --nginx -d erp.tsh.sale -d www.tsh.sale

# Test auto-renewal
certbot renew --dry-run
```

### 7. Configure GitHub Actions

Add these secrets to your GitHub repository (Settings → Secrets):

- `PROD_HOST`: `167.71.39.50`
- `PROD_USER`: `root`
- `PROD_SSH_KEY`: (contents of private SSH key)
- `PROD_SSH_PORT`: `22`

To generate deployment key:

```bash
ssh root@167.71.39.50
ssh-keygen -t ed25519 -C "github-actions@tsh.sale" -f ~/.ssh/github_deploy -N ""
cat ~/.ssh/github_deploy  # Copy this to GitHub Secrets
cat ~/.ssh/github_deploy.pub >> ~/.ssh/authorized_keys
```

---

## 📝 Manual Deployment Commands

```bash
# Deploy latest from main
ssh root@167.71.39.50
bash /opt/tsh_erp/bin/deploy.sh main

# Rollback if needed
bash /opt/tsh_erp/bin/rollback.sh

# Check active instance
readlink /etc/nginx/upstreams/tsh_erp_active.conf

# View deployment logs
tail -f /opt/tsh_erp/shared/logs/api/deploy_*.log
```

---

## 🚨 Important Notes

1. **Database**: Currently using Supabase PostgreSQL. No local PostgreSQL setup needed.

2. **Ports**:
   - Blue instance: 8001
   - Green instance: 8002
   - Nginx: 80, 443

3. **GitHub Repo**: Update the REPO variable in deploy.sh with your actual repository URL

4. **Domain**: Update Nginx configuration if you want to use a custom domain

5. **Backups**: Automatic backups will be created in `/opt/backups/` before each deployment

---

## 📊 Current Server Status

```
Server IP: 167.71.39.50
Location: Frankfurt, Germany
OS: Ubuntu 22.04.5 LTS
RAM: 4GB
CPUs: 2
Disk: Available

Services:
✅ Nginx - Running
✅ PostgreSQL 17.6 - Running (but not used, using Supabase)
⏹️  tsh_erp-blue - Not started (waiting for first deployment)
⏹️  tsh_erp-green - Not started
```

---

## 🎯 Next Action

**Run the first deployment:**

```bash
# 1. SSH to server
ssh root@167.71.39.50

# 2. Create prod.env file (see step 1 above)

# 3. Update deploy.sh with GitHub repo URL

# 4. Run deployment
bash /opt/tsh_erp/bin/deploy.sh main

# 5. Verify it's working
curl http://167.71.39.50/health
```

---

**Status**: Ready for first deployment
**Blocking**: Need to create prod.env and update deploy.sh with GitHub repo URL
