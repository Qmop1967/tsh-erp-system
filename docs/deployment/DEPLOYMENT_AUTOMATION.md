# Automated Deployment System

## Overview

The TSH ERP system uses GitHub Actions for fully automated CI/CD deployment to production. Every push to the `main` branch triggers automated testing, deployment, and verification.

## Architecture

```
┌─────────────────┐
│  GitHub Push    │
│   (main branch) │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│     GitHub Actions Workflow          │
│  (.github/workflows/ci-deploy.yml)   │
└────────┬──────────────┬──────────────┘
         │              │
         ▼              ▼
┌──────────────┐  ┌──────────────┐
│  Test Job    │  │  Deploy Job  │
│  (parallel)  │  │  (sequential)│
└──────────────┘  └──────┬───────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  SSH to Production   │
              │  (appleboy/ssh-action)│
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Deployment Steps    │
              │  1. Pull code        │
              │  2. Install deps     │
              │  3. Restart service  │
              │  4. Health checks    │
              └──────────────────────┘
```

## Deployment Workflow

### Trigger Conditions
- **Branch:** `main` (production) or `develop` (staging)
- **Event:** `push` or `pull_request`
- **Automatic:** Yes, runs on every qualifying push

### Job 1: Run Tests and Security Checks

Runs in parallel with deployment preparation:

1. **Code Linting** (ruff)
   ```bash
   ruff check . --output-format=github
   ```
   - Checks Python code style
   - Identifies unused imports
   - Non-blocking (continue-on-error: true)

2. **Type Checking** (mypy)
   ```bash
   mypy . --ignore-missing-imports --no-strict-optional
   ```
   - Static type analysis
   - Non-blocking

3. **Security Scan** (bandit)
   ```bash
   bandit -r . -f json -o bandit-report.json
   ```
   - Scans for security vulnerabilities
   - Generates JSON and screen reports
   - Non-blocking

4. **Unit Tests** (pytest)
   ```bash
   pytest tests/ -v --cov=. --cov-report=term --cov-report=xml
   ```
   - Runs all unit tests
   - Generates coverage reports
   - Non-blocking (allows deployment even if tests fail)

5. **Coverage Upload** (Codecov)
   - Uploads coverage reports to Codecov
   - Tracks test coverage over time

### Job 2: Deploy to Production Server

Only runs if:
- Tests job completed (success or failure)
- Branch is `main`
- Event is `push`

#### Deployment Steps (6-phase process)

```yaml
[1/6] Navigate to application directory
cd /home/deploy/TSH_ERP_Ecosystem

[2/6] Pull latest code
git fetch origin
git reset --hard origin/main

[3/6] Activate virtual environment
source venv/bin/activate

[4/6] Install/update dependencies
pip install --upgrade pip
pip install -r requirements.txt

[5/6] Check for database migrations
# Note: Migrations managed manually (not automated)
# Future: Will support automated migrations

[6/6] Restart TSH ERP service
systemctl restart tsh-erp
```

#### Health Verification

After deployment, the system performs comprehensive health checks:

1. **Systemd Service Status**
   ```bash
   systemctl is-active --quiet tsh-erp
   ```
   - Verifies service is running
   - Exits with error if service is down

2. **Backend API Health Check**
   ```bash
   curl -f http://127.0.0.1:8000/health
   ```
   - Tests internal API endpoint
   - Returns: `{"status": "healthy", "message": "النظام يعمل بشكل طبيعي"}`
   - Critical: Deployment fails if unhealthy

3. **Public Endpoint Check**
   ```bash
   curl -f https://erp.tsh.sale/health
   ```
   - Tests public HTTPS endpoint through nginx
   - Warning only (non-blocking)

## SSH Configuration

### Required GitHub Secrets

Configure these in GitHub repository settings → Secrets and variables → Actions:

#### Production Secrets
- `PROD_HOST` - Production server hostname/IP (e.g., `167.71.39.50`)
- `PROD_USER` - SSH username (e.g., `root`)
- `PROD_SSH_KEY` - Private SSH key for authentication
- `PROD_SSH_PORT` - SSH port (default: `22`)

#### Staging Secrets (optional)
- `STAGING_HOST` - Staging server hostname/IP
- `STAGING_USER` - SSH username
- `STAGING_SSH_KEY` - Private SSH key
- `STAGING_SSH_PORT` - SSH port (default: `22`)

### Setting Secrets via CLI

```bash
# Set production secrets
gh secret set PROD_HOST --body "167.71.39.50"
gh secret set PROD_USER --body "root"
gh secret set PROD_SSH_KEY < ~/.ssh/production_key
gh secret set PROD_SSH_PORT --body "22"
```

### SSH Key Generation

```bash
# Generate new SSH key for deployment
ssh-keygen -t ed25519 -C "github-actions-deployment" -f ~/.ssh/tsh_deploy

# Add public key to server
ssh-copy-id -i ~/.ssh/tsh_deploy.pub root@167.71.39.50

# Add private key to GitHub secrets
gh secret set PROD_SSH_KEY < ~/.ssh/tsh_deploy
```

## Server Setup

### Prerequisites

The production server must have:

1. **Directory Structure**
   ```
   /home/deploy/TSH_ERP_Ecosystem/
   ├── app/                  # Application code
   ├── venv/                 # Python virtual environment
   ├── requirements.txt      # Python dependencies
   └── .git/                 # Git repository
   ```

2. **Systemd Service** (`/etc/systemd/system/tsh-erp.service`)
   ```ini
   [Unit]
   Description=TSH ERP FastAPI Backend
   After=network.target

   [Service]
   Type=notify
   User=root
   WorkingDirectory=/home/deploy/TSH_ERP_Ecosystem
   Environment="PATH=/home/deploy/TSH_ERP_Ecosystem/venv/bin"
   ExecStart=/home/deploy/TSH_ERP_Ecosystem/venv/bin/gunicorn app.main:app \
       --workers 4 \
       --worker-class uvicorn.workers.UvicornWorker \
       --bind 127.0.0.1:8000 \
       --access-logfile /var/log/tsh-erp/access.log \
       --error-logfile /var/log/tsh-erp/error.log
   Restart=on-failure
   RestartSec=10s

   [Install]
   WantedBy=multi-user.target
   ```

3. **Log Directory**
   ```bash
   mkdir -p /var/log/tsh-erp
   chmod 755 /var/log/tsh-erp
   ```

4. **Nginx Configuration** (optional, for HTTPS)
   ```nginx
   server {
       listen 443 ssl http2;
       server_name erp.tsh.sale;

       ssl_certificate /etc/letsencrypt/live/erp.tsh.sale/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/erp.tsh.sale/privkey.pem;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

### Initial Server Setup

```bash
# 1. SSH to server
ssh root@167.71.39.50

# 2. Create deployment directory
mkdir -p /home/deploy

# 3. Clone repository
cd /home/deploy
git clone https://github.com/Qmop1967/tsh-erp-system.git TSH_ERP_Ecosystem

# 4. Set up Python virtual environment
cd TSH_ERP_Ecosystem
python3.11 -m venv venv
source venv/bin/activate

# 5. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 6. Configure systemd service
cp deployment/tsh-erp.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable tsh-erp
systemctl start tsh-erp

# 7. Verify service
systemctl status tsh-erp
curl http://127.0.0.1:8000/health
```

## Monitoring Deployments

### View Deployment Status

```bash
# List recent deployment runs
gh run list --limit 5

# Watch current deployment
gh run watch

# View specific deployment
gh run view 19112160480

# View deployment logs
gh run view 19112160480 --log
```

### Check Production Health

```bash
# Quick health check
curl https://erp.tsh.sale/health

# Service status
ssh root@167.71.39.50 "systemctl status tsh-erp"

# Recent logs
ssh root@167.71.39.50 "tail -50 /var/log/tsh-erp/error.log"

# Active workers
ssh root@167.71.39.50 "ps aux | grep gunicorn"
```

## Troubleshooting

### Common Issues

#### 1. ImportError on Deployment

**Symptom:** Service crashes with `ImportError: cannot import name 'X'`

**Cause:** Missing schema exports or circular imports

**Solution:**
```bash
# Check error logs
ssh root@167.71.39.50 "tail -100 /var/log/tsh-erp/error.log"

# Fix imports locally
# Add missing exports to __init__.py
# Test locally first
python -c "from app.main import app"

# Commit and push fix
git add .
git commit -m "fix: Add missing exports"
git push origin main
```

#### 2. Service Won't Start

**Symptom:** Deployment completes but service is inactive

**Cause:** Application startup errors

**Solution:**
```bash
# Check service status
ssh root@167.71.39.50 "systemctl status tsh-erp --no-pager"

# Check error logs
ssh root@167.71.39.50 "journalctl -u tsh-erp -n 50"

# Try starting manually
ssh root@167.71.39.50 "cd /home/deploy/TSH_ERP_Ecosystem && source venv/bin/activate && gunicorn app.main:app"
```

#### 3. Health Check Timeout

**Symptom:** Deployment fails at health check step

**Cause:** Application takes too long to start

**Solution:** Increase wait time in workflow:
```yaml
# Wait for service to start
sleep 7  # Increase to 10 or 15 if needed
```

#### 4. Permission Denied

**Symptom:** `systemctl restart tsh-erp` fails with permission denied

**Cause:** SSH user doesn't have systemctl privileges

**Solution:**
```bash
# Add user to sudo group or use root
PROD_USER=root

# Or configure sudoers
echo "deploy ALL=(ALL) NOPASSWD: /bin/systemctl restart tsh-erp" | sudo tee /etc/sudoers.d/tsh-deploy
```

### Rollback Procedure

If a deployment breaks production:

```bash
# 1. SSH to server
ssh root@167.71.39.50

# 2. Navigate to app directory
cd /home/deploy/TSH_ERP_Ecosystem

# 3. Find last working commit
git log --oneline -10

# 4. Reset to last working commit
git reset --hard <commit-hash>

# 5. Restart service
systemctl restart tsh-erp

# 6. Verify
systemctl status tsh-erp
curl http://127.0.0.1:8000/health
```

## Performance Metrics

### Typical Deployment Times

- **Tests Job:** ~1.5 minutes
- **Dependency Installation:** ~2-3 minutes
- **Service Restart:** ~5-7 seconds
- **Health Check Wait:** ~7 seconds
- **Total Deployment:** ~3-4 minutes

### Resource Usage

Production service (4 workers):
- **Memory:** ~950 MB
- **CPU:** 30-40 seconds startup
- **Tasks:** 33 processes
- **Workers:** 4 Gunicorn + 1 master

## Best Practices

### 1. Always Test Locally First

```bash
# Before pushing to main
python -m pytest tests/
python -m ruff check .
python -m mypy .
python -c "from app.main import app"
```

### 2. Use Feature Branches

```bash
# Create feature branch
git checkout -b feature/new-endpoint

# Make changes and test
# ...

# Push to GitHub for review
git push origin feature/new-endpoint

# Create PR (triggers tests but not deployment)
gh pr create

# Merge to main only after review
gh pr merge --squash
```

### 3. Monitor After Deployment

```bash
# Watch deployment
gh run watch

# Check health immediately
curl https://erp.tsh.sale/health

# Monitor logs for errors
ssh root@167.71.39.50 "tail -f /var/log/tsh-erp/error.log"
```

### 4. Keep Dependencies Updated

```bash
# Update dependencies locally
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt

# Test with updated dependencies
python -m pytest tests/

# Commit and deploy
git add requirements.txt
git commit -m "chore: Update dependencies"
git push origin main
```

## Future Improvements

### Planned Enhancements

1. **Automated Database Migrations**
   - Currently: Migrations run manually
   - Future: Alembic migrations in deployment pipeline
   - Challenge: Handling migration failures gracefully

2. **Blue-Green Deployment**
   - Zero-downtime deployments
   - Run new version alongside old version
   - Switch traffic after health checks pass

3. **Automated Rollback**
   - Detect deployment failures automatically
   - Rollback to previous version
   - Notify team of failures

4. **Deployment Notifications**
   - Slack/Discord/Telegram notifications
   - Alert on deployment success/failure
   - Include deployment metrics

5. **Canary Deployments**
   - Deploy to subset of servers first
   - Monitor metrics before full rollout
   - Automatic rollback on anomalies

## Related Documentation

- [GitHub Actions Workflow File](../.github/workflows/ci-deploy.yml)
- [Backend Architecture](./ARCHITECTURE.md)
- [API Documentation](https://erp.tsh.sale/docs)
- [Manual Deployment Scripts](../deployment/)

## Support

For deployment issues:
1. Check logs: `/var/log/tsh-erp/error.log`
2. Review workflow runs: https://github.com/Qmop1967/tsh-erp-system/actions
3. Contact: kha93ahm@gmail.com
