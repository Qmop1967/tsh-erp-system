# TSH ERP System - Deployment Guide

## Automated Deployment via GitHub Actions

The TSH ERP system is configured for automated deployment to your VPS using GitHub Actions. Deployments are triggered automatically when code is pushed to the `main` branch.

## Setup Instructions

### 1. Add GitHub Secrets

Before the first deployment, you need to add the following secrets to your GitHub repository:

1. Go to your GitHub repository: https://github.com/Qmop1967/tsh-erp-system
2. Click on **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add the following three secrets:

#### VPS_SSH_KEY
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACCWuRnyF7zQ/Yycv11Tyw/PGeWqhYu7RPZmDB8yZ+qdCAAAAKDXXh+y114f
sgAAAAtzc2gtZWQyNTUxOQAAACCWuRnyF7zQ/Yycv11Tyw/PGeWqhYu7RPZmDB8yZ+qdCA
AAAED1I48tPVz1poqdrGczZ10OJYyqFj6cJOXPBQ1UIAbGbZa5GfIXvND9jJy/XVPLD88Z
5aqFi7tE9mYMHzJn6p0IAAAAFmdpdGh1Yi1hY3Rpb25zQHRzaC1lcnABAgMEBQYH
-----END OPENSSH PRIVATE KEY-----
```

#### VPS_HOST
```
167.71.39.50
```

#### VPS_USER
```
root
```

### 2. Deployment Workflow

The deployment workflow (`.github/workflows/ci-cd.yml`) will:

1. **Run Tests**: Execute backend, frontend, and mobile tests
2. **Security Scan**: Run Bandit, Safety, and secret scanning
3. **Deploy** (only on `main` branch):
   - SSH into the VPS
   - Pull latest code from GitHub
   - Run the blue-green deployment script
   - Verify the deployment with health checks

### 3. Triggering a Deployment

To deploy to production:

```bash
# Make sure you're on develop branch
git checkout develop

# Merge develop into main
git checkout main
git merge develop

# Push to GitHub (this triggers the deployment)
git push origin main
```

The deployment will:
- Take approximately 5-10 minutes
- Use blue-green deployment for zero downtime
- Automatically rollback if health checks fail

### 4. Monitoring Deployment

You can monitor the deployment progress at:
https://github.com/Qmop1967/tsh-erp-system/actions

Or using the GitHub CLI:
```bash
gh run watch
```

### 5. Deployment Architecture

**Blue-Green Deployment:**
- Two application instances run on ports 8001 (blue) and 8002 (green)
- Nginx proxies traffic to the active instance
- During deployment, the idle instance is updated and tested
- If successful, traffic switches to the new instance
- Old instance remains as backup for quick rollback

**Services:**
- `tsh_erp-blue` - Blue instance (port 8001)
- `tsh_erp-green` - Green instance (port 8002)
- `nginx` - Reverse proxy and SSL termination

### 6. Manual Deployment (Alternative)

If you need to deploy manually:

```bash
# SSH into the VPS
ssh root@167.71.39.50

# Navigate to application directory
cd /opt/tsh_erp

# Pull latest code
git pull origin main

# Run deployment script
bash /opt/tsh_erp/bin/deploy.sh
```

### 7. Verifying Deployment

After deployment, verify the application is running:

```bash
# Check active service
ssh root@167.71.39.50 "systemctl status tsh_erp-blue tsh_erp-green"

# Check health endpoint
curl https://erp.tsh.sale/health
```

### 8. Rollback Procedure

If a deployment fails, the blue-green deployment automatically keeps the previous version running. To manually rollback:

```bash
ssh root@167.71.39.50

# Check which instance is active
cat /opt/tsh_erp/current_deployment.txt

# If green (8002) is active but broken, switch back to blue
sudo sed -i 's/proxy_pass http:\/\/127.0.0.1:8002/proxy_pass http:\/\/127.0.0.1:8001/' /etc/nginx/sites-available/tsh_erp
sudo nginx -t && sudo systemctl reload nginx
echo "8001" > /opt/tsh_erp/current_deployment.txt
```

### 9. Troubleshooting

**Deployment fails at SSH step:**
- Verify GitHub secrets are correctly set
- Check VPS is accessible: `ssh root@167.71.39.50`
- Ensure SSH key is authorized on VPS

**Health check fails:**
- Check application logs: `journalctl -u tsh_erp-green -n 50`
- Verify database connection in `/opt/tsh_erp/.env`
- Check port availability: `netstat -tuln | grep 800`

**Tests fail before deployment:**
- Review test output in GitHub Actions logs
- Fix failing tests before merging to main

## Security Notes

- SSH private key is stored as a GitHub secret (encrypted)
- Only users with repository access can trigger deployments
- All deployments are logged and auditable
- Secrets are never exposed in logs

## Contact

For deployment issues, contact the DevOps team or check the logs at:
- GitHub Actions: https://github.com/Qmop1967/tsh-erp-system/actions
- VPS Logs: `ssh root@167.71.39.50 'journalctl -u tsh_erp-* -n 100'`
