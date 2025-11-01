# TSH ERP - CI/CD Setup Guide
## Zero-Downtime Blue/Green Deployment

**Last Updated**: November 2024
**Status**: Production Ready ✅

---

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Server Setup](#server-setup)
5. [GitHub Setup](#github-setup)
6. [Testing](#testing)
7. [Operations](#operations)
8. [Troubleshooting](#troubleshooting)

---

## Overview

This CI/CD system provides:
- ✅ **Zero-downtime deployments** via blue/green switching
- ✅ **Automated testing** (lint, type-check, security scan, unit tests)
- ✅ **Database safety** (backup before migration, test on staging first)
- ✅ **Health checks** gate traffic switching
- ✅ **Instant rollback** (one command)
- ✅ **No containers** - Pure Ubuntu + systemd + virtualenv
- ✅ **Service isolation** - Only target service restarts, others unaffected

---

## Architecture

### Directory Structure on Server
```
/opt/tsh_erp/
├── releases/
│   ├── blue/          # Blue release (port 8001)
│   └── green/         # Green release (port 8002)
├── shared/
│   ├── env/
│   │   ├── prod.env      # Production environment variables
│   │   └── staging.env   # Staging DB for migration testing
│   └── logs/
│       └── api/          # Deployment logs
├── venvs/
│   ├── blue/          # Blue Python virtual environment
│   └── green/         # Green Python virtual environment
└── bin/
    ├── deploy.sh
    ├── rollback.sh
    ├── healthcheck.sh
    └── switch_upstream.sh
```

### Flow
```
Developer
  └─ git push main → GitHub

GitHub Actions (CI)
  ├─ Lint (ruff)
  ├─ Type check (mypy)
  ├─ Security scan (bandit)
  ├─ Unit tests (pytest)
  └─ SSH → Server → deploy.sh

Server (Ubuntu)
  ├─ Determine idle color (blue/green)
  ├─ Sync code from GitHub
  ├─ Create venv + install deps
  ├─ Backup production DB (pg_dump)
  ├─ Test migrations on staging DB
  ├─ Start idle service
  ├─ Health check /ready
  ├─ Switch Nginx → idle becomes active
  ├─ Run migrations on production DB
  └─ Stop old service
```

---

## Prerequisites

### Server Requirements
- Ubuntu 20.04+ (or any systemd-based Linux)
- Python 3.11+
- PostgreSQL 14+
- Nginx
- Git
- Root or sudo access

### Local Requirements
- Git
- GitHub account with repo access
- SSH key for server access

---

## Server Setup

### Step 1: Install Dependencies

```bash
# Connect to server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install required packages
apt install -y \
    python3 \
    python3-venv \
    python3-pip \
    postgresql \
    postgresql-client \
    nginx \
    git \
    curl \
    rsync

# Verify installations
python3 --version  # Should be 3.11+
psql --version     # Should be 14+
nginx -v           # Any recent version
```

### Step 2: Create Directory Structure

```bash
# Create application directories
mkdir -p /opt/tsh_erp/{releases/{blue,green},shared/{env,logs/api},venvs,bin}

# Create backup directory
mkdir -p /opt/backups

# Set permissions (adjust user as needed)
chown -R root:root /opt/tsh_erp
chmod -R 755 /opt/tsh_erp
```

### Step 3: Configure Nginx

```bash
# Create upstream directory
mkdir -p /etc/nginx/upstreams

# Copy upstream configurations
cp /path/to/deployment/nginx/tsh_erp_blue.conf /etc/nginx/upstreams/
cp /path/to/deployment/nginx/tsh_erp_green.conf /etc/nginx/upstreams/

# Copy main site configuration
cp /path/to/deployment/nginx/tsh_erp.conf /etc/nginx/sites-available/

# Enable site
ln -s /etc/nginx/sites-available/tsh_erp.conf /etc/nginx/sites-enabled/

# Set initial active upstream to blue
ln -sfn /etc/nginx/upstreams/tsh_erp_blue.conf /etc/nginx/upstreams/tsh_erp_active.conf

# Test configuration
nginx -t

# Reload Nginx
systemctl reload nginx
```

### Step 4: Configure systemd Services

```bash
# Copy service files
cp /path/to/deployment/systemd/tsh_erp-blue.service /etc/systemd/system/
cp /path/to/deployment/systemd/tsh_erp-green.service /etc/systemd/system/

# Reload systemd
systemctl daemon-reload

# Enable services (but don't start yet)
systemctl enable tsh_erp-blue.service
systemctl enable tsh_erp-green.service
```

### Step 5: Deploy Scripts

```bash
# Copy scripts to server
cp /path/to/deployment/scripts/*.sh /opt/tsh_erp/bin/

# Make executable
chmod +x /opt/tsh_erp/bin/*.sh

# Update REPO variable in deploy.sh
sed -i 's|https://github.com/YOUR_GITHUB_USERNAME/TSH_ERP_Ecosystem.git|https://github.com/YOUR_ACTUAL_REPO.git|' /opt/tsh_erp/bin/deploy.sh
```

### Step 6: Configure Environment

```bash
# Copy example environment files
cp /path/to/deployment/env/prod.env.example /opt/tsh_erp/shared/env/prod.env
cp /path/to/deployment/env/staging.env.example /opt/tsh_erp/shared/env/staging.env

# Edit production environment
nano /opt/tsh_erp/shared/env/prod.env
# Fill in all the required values (database URL, secret key, etc.)

# Edit staging environment
nano /opt/tsh_erp/shared/env/staging.env
# Fill in staging database URL

# Secure environment files
chmod 600 /opt/tsh_erp/shared/env/*.env
```

### Step 7: Setup PostgreSQL Databases

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create production database
CREATE DATABASE tsh_erp_production;

# Create staging database
CREATE DATABASE tsh_erp_staging;

# Create user (if needed)
CREATE USER tsh_app WITH PASSWORD 'your_strong_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE tsh_erp_production TO tsh_app;
GRANT ALL PRIVILEGES ON DATABASE tsh_erp_staging TO tsh_app;

# Exit
\q
```

### Step 8: Initial Deployment

```bash
# Run first deployment manually
bash /opt/tsh_erp/bin/deploy.sh main

# Verify service is running
systemctl status tsh_erp-blue.service

# Check health
curl http://localhost:8001/ready
curl http://localhost:8001/health

# Check via Nginx
curl http://your-domain.com/ready
```

---

## GitHub Setup

### Step 1: Generate SSH Key on Server

```bash
# On server, generate SSH key for GitHub Actions
ssh-keygen -t ed25519 -C "github-actions@tsh.sale" -f ~/.ssh/github_deploy_key -N ""

# Display private key (you'll add this to GitHub Secrets)
cat ~/.ssh/github_deploy_key

# Display public key (you'll add this to server's authorized_keys if needed)
cat ~/.ssh/github_deploy_key.pub
```

### Step 2: Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

Add these secrets:
- `PROD_HOST`: Your server IP address (e.g., `164.90.220.30`)
- `PROD_USER`: SSH user (e.g., `root`)
- `PROD_SSH_KEY`: Contents of `/root/.ssh/github_deploy_key` (private key)
- `PROD_SSH_PORT`: SSH port (default: `22`)

Optional for staging:
- `STAGING_HOST`
- `STAGING_USER`
- `STAGING_SSH_KEY`
- `STAGING_SSH_PORT`

### Step 3: Push Workflow File

```bash
# From your local machine
git add .github/workflows/ci-deploy.yml
git commit -m "feat: add CI/CD workflow"
git push origin main
```

### Step 4: Verify Workflow

1. Go to GitHub → Actions tab
2. You should see the workflow running
3. Monitor the logs
4. First run will deploy to blue instance

---

## Testing

### Test Locally Before Pushing

```bash
# Lint
ruff check .

# Type check
mypy .

# Security scan
bandit -r .

# Run tests
pytest tests/ -v

# If all pass, you're ready to push
git push origin main
```

### Test Deployment Manually

```bash
# SSH to server
ssh root@your-server

# Run deployment
bash /opt/tsh_erp/bin/deploy.sh main

# Check logs
tail -f /opt/tsh_erp/shared/logs/api/deploy_*.log

# Verify services
systemctl status tsh_erp-blue
systemctl status tsh_erp-green

# Check which is active
readlink -f /etc/nginx/upstreams/tsh_erp_active.conf
```

### Test Rollback

```bash
# Trigger rollback
bash /opt/tsh_erp/bin/rollback.sh

# Verify traffic switched
curl http://localhost:8001/ready
curl http://localhost:8002/ready
```

---

## Operations

### Daily Workflow

1. **Develop locally**
   ```bash
   git checkout -b feature/new-feature
   # Make changes
   git commit -m "feat: add new feature"
   git push origin feature/new-feature
   ```

2. **Create Pull Request**
   - GitHub Actions runs tests
   - Review code
   - Merge to main

3. **Auto-Deploy**
   - Merge triggers deployment
   - Monitor GitHub Actions
   - Verify production

### Manual Operations

**Check Active Color:**
```bash
readlink -f /etc/nginx/upstreams/tsh_erp_active.conf
```

**View Logs:**
```bash
# Application logs
journalctl -u tsh_erp-blue -f
journalctl -u tsh_erp-green -f

# Deployment logs
tail -f /opt/tsh_erp/shared/logs/api/deploy_*.log

# Nginx logs
tail -f /var/log/nginx/tsh_erp_access.log
tail -f /var/log/nginx/tsh_erp_error.log
```

**Restart Services:**
```bash
sudo systemctl restart tsh_erp-blue
sudo systemctl restart tsh_erp-green
```

**Switch Colors Manually:**
```bash
bash /opt/tsh_erp/bin/switch_upstream.sh green
```

**Database Backup (Manual):**
```bash
pg_dump --file=/opt/backups/manual_backup_$(date +%F).dump \
    --format=custom \
    "$DATABASE_URL"
```

**Restore from Backup:**
```bash
pg_restore --dbname=tsh_erp_production \
    --clean \
    --if-exists \
    /opt/backups/backup_file.dump
```

---

## Troubleshooting

### Deployment Failed

**Check logs:**
```bash
tail -100 /opt/tsh_erp/shared/logs/api/deploy_*.log
```

**Common issues:**
1. **Database connection failed**
   - Check `/opt/tsh_erp/shared/env/prod.env`
   - Verify DATABASE_URL
   - Test: `psql "$DATABASE_URL" -c "SELECT 1"`

2. **Migration failed**
   - Check Alembic migrations
   - Verify staging DB exists
   - Run manually: `alembic upgrade head`

3. **Health check failed**
   - Check application logs: `journalctl -u tsh_erp-blue -n 50`
   - Verify port is listening: `netstat -tlnp | grep 8001`
   - Test directly: `curl localhost:8001/ready`

4. **Nginx configuration error**
   - Test config: `nginx -t`
   - Check upstream files exist
   - Verify symlink: `ls -l /etc/nginx/upstreams/`

### Rollback

**Automatic rollback if deployment fails:**
```bash
bash /opt/tsh_erp/bin/rollback.sh
```

**Manual rollback:**
```bash
# Stop current
systemctl stop tsh_erp-blue  # or green

# Start previous
systemctl start tsh_erp-green  # or blue

# Switch traffic
bash /opt/tsh_erp/bin/switch_upstream.sh green
```

### Service Won't Start

**Check status:**
```bash
systemctl status tsh_erp-blue
```

**View full logs:**
```bash
journalctl -u tsh_erp-blue -n 100 --no-pager
```

**Common fixes:**
1. **Port already in use:**
   ```bash
   lsof -i :8001
   kill <PID>
   ```

2. **Permission denied:**
   ```bash
   chown -R root:root /opt/tsh_erp/releases/blue
   chmod -R 755 /opt/tsh_erp/releases/blue
   ```

3. **Module not found:**
   ```bash
   source /opt/tsh_erp/venvs/blue/bin/activate
   pip install -r /opt/tsh_erp/releases/blue/requirements.txt
   ```

### Database Issues

**Check connections:**
```bash
# Active connections
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity WHERE datname='tsh_erp_production';"

# Kill connections if needed
sudo -u postgres psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='tsh_erp_production';"
```

**Verify migrations:**
```bash
cd /opt/tsh_erp/releases/blue
source /opt/tsh_erp/venvs/blue/bin/activate
alembic current
alembic history
```

---

## Security Best Practices

1. **Keep secrets secure:**
   - Never commit `.env` files
   - Use GitHub Secrets for sensitive data
   - Limit SSH key access

2. **Update regularly:**
   ```bash
   apt update && apt upgrade -y
   ```

3. **Monitor logs:**
   - Set up log rotation
   - Monitor for suspicious activity
   - Use Sentry for error tracking

4. **Firewall:**
   ```bash
   ufw allow 22/tcp    # SSH
   ufw allow 80/tcp    # HTTP
   ufw allow 443/tcp   # HTTPS
   ufw enable
   ```

5. **SSL/TLS:**
   - Use Let's Encrypt for free SSL
   - Enable HTTPS in Nginx config
   - Redirect HTTP to HTTPS

---

## Maintenance

### Regular Tasks

**Daily:**
- Monitor deployment logs
- Check application health

**Weekly:**
- Review error logs
- Check disk space: `df -h`
- Verify backups exist

**Monthly:**
- Update system packages
- Rotate old logs
- Test rollback procedure
- Review and delete old backups (keep last 30 days)

**Quarterly:**
- Security audit
- Performance review
- Capacity planning

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [systemd Documentation](https://www.freedesktop.org/software/systemd/man/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

## Support

For issues or questions:
1. Check logs first
2. Review this guide
3. Contact DevOps team
4. Create GitHub issue

---

**Document Version**: 1.0.0
**Last Review**: November 2024
**Next Review**: February 2025
