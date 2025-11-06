# GitHub Actions - Automated Deployment Setup

**Date**: November 2, 2024
**Purpose**: Configure automated deployments to production server

---

## 📋 Prerequisites Complete

✅ Production server deployed and running
✅ Blue/green deployment configured
✅ SSH keys generated
✅ Deployment scripts tested

---

## 🔑 GitHub Secrets Configuration

Go to your GitHub repository:
**Settings → Secrets and variables → Actions → New repository secret**

Add these **4 secrets**:

### 1. PROD_HOST
```
167.71.39.50
```

### 2. PROD_USER
```
root
```

### 3. PROD_SSH_PORT
```
22
```

### 4. PROD_SSH_KEY

Copy the **ENTIRE private key** below (including the BEGIN and END lines):

```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACDUKBMjX5C2YbHv6rA0MfndmaDMrWI/G4eKq+0phnAgCgAAAKBd2z3aXds9
2gAAAAtzc2gtZWQyNTUxOQAAACDUKBMjX5C2YbHv6rA0MfndmaDMrWI/G4eKq+0phnAgCg
AAAEABjdI3wMxNLO5bEalaoI+laT+WlOWRo98B1HPH/zB8iNQoEyNfkLZhse/qsDQx+d2Z
oMytYj8bh4qr7SmGcCAKAAAAF2dpdGh1Yi1hY3Rpb25zQHRzaC5zYWxlAQIDBAUG
-----END OPENSSH PRIVATE KEY-----
```

**⚠️ IMPORTANT**: This private key must be kept secret! Only add it to GitHub Secrets, never commit it to the repository.

---

## 🚀 How Automated Deployment Works

### Trigger
Push to `main` branch automatically triggers deployment

```bash
git add .
git commit -m "Update API endpoint"
git push origin main
```

### Workflow Steps

The `.github/workflows/ci-deploy.yml` workflow will:

1. **Run Tests** (5-10 minutes)
   - Lint code (ruff)
   - Type checking (mypy)
   - Security scan (bandit)
   - Unit tests (pytest)

2. **Deploy to Production** (if tests pass)
   - SSH to production server
   - Run `/opt/tsh_erp/bin/deploy.sh main`
   - Deploy to idle instance (blue or green)
   - Run health checks
   - Switch Nginx traffic
   - Zero downtime deployment

3. **Notify Results**
   - GitHub Actions will show success/failure
   - Check status in Actions tab

---

## 📊 Monitor Deployment

### Check Deployment Status

Go to your GitHub repository:
**Actions tab → Latest workflow run**

You'll see:
- ✅ Tests passed/failed
- ✅ Deployment succeeded/failed
- 📋 Deployment logs

### Check Live Server

After deployment completes:

```bash
# Check service status
ssh root@167.71.39.50 "systemctl status tsh_erp-blue tsh_erp-green"

# Test API
curl http://167.71.39.50/health | python3 -m json.tool

# View logs
ssh root@167.71.39.50 "journalctl -u tsh_erp-green -f"
```

---

## 🔄 Manual Deployment (Fallback)

If GitHub Actions fails or you need manual control:

```bash
# SSH to server
ssh root@167.71.39.50

# Run deployment
bash /opt/tsh_erp/bin/deploy.sh main

# Or rollback if needed
bash /opt/tsh_erp/bin/rollback.sh
```

---

## 🎯 Deployment Process Overview

### Current State
- **Active**: Green instance (port 8002)
- **Standby**: Blue instance (ready)

### After Next Deployment
1. Code pulls to blue instance
2. Blue starts on port 8001
3. Health checks verify blue is ready
4. Nginx switches from green (8002) to blue (8001)
5. Green becomes standby
6. **Zero downtime** - users never notice

### Future Deployments
Alternates between blue and green, always keeping one instance ready for rollback

---

## 🧪 Testing Automated Deployment

### Test the Setup

1. **Make a small change**:
   ```bash
   # Edit a file
   echo "# Test deployment" >> tds_core/README.md
   ```

2. **Commit and push**:
   ```bash
   git add .
   git commit -m "Test automated deployment"
   git push origin main
   ```

3. **Watch GitHub Actions**:
   - Go to Actions tab
   - Click on the running workflow
   - Watch tests and deployment progress

4. **Verify deployment**:
   ```bash
   # Check API responds
   curl http://167.71.39.50/health

   # Check which instance is active
   ssh root@167.71.39.50 "readlink /etc/nginx/upstreams/tsh_erp_active.conf"
   ```

---

## ⚠️ Important Notes

### SSH Key Security
- **Never commit** the private key to the repository
- **Only store** it in GitHub Secrets
- The public key is already added to server's `authorized_keys`

### Deployment Requirements
- Tests must pass before deployment
- Health checks must succeed
- If anything fails, deployment stops (safe)

### Rollback
- Instant rollback available: `bash /opt/tsh_erp/bin/rollback.sh`
- Previous version kept running until new version is verified
- Can rollback within seconds if issues detected

---

## 📝 Workflow File Location

The GitHub Actions workflow is defined in:
```
.github/workflows/ci-deploy.yml
```

You can customize:
- Which branches trigger deployment (currently: `main`)
- Test steps
- Deployment steps
- Notification settings

---

## ✅ Verification Checklist

After setting up GitHub Secrets:

- [ ] All 4 secrets added to GitHub repository
- [ ] PROD_SSH_KEY contains the complete private key (including BEGIN/END lines)
- [ ] Made a test commit to main branch
- [ ] GitHub Actions workflow started
- [ ] Tests passed
- [ ] Deployment succeeded
- [ ] API responds at http://167.71.39.50
- [ ] Service is running on server

---

## 🆘 Troubleshooting

### "Permission denied (publickey)"
- Check PROD_SSH_KEY secret is set correctly
- Verify you copied the **entire** private key including BEGIN/END lines

### "Connection refused"
- Check PROD_HOST is `167.71.39.50`
- Check PROD_SSH_PORT is `22`
- Verify firewall allows port 22

### "Health check failed"
- Check service is running: `systemctl status tsh_erp-green`
- View logs: `journalctl -u tsh_erp-green -n 50`
- Deployment will rollback automatically

### Tests failing
- Run tests locally: `pytest tests/`
- Fix failing tests before pushing
- GitHub Actions won't deploy if tests fail (safety feature)

---

## 📞 Quick Reference

### GitHub Secrets
- PROD_HOST: `167.71.39.50`
- PROD_USER: `root`
- PROD_SSH_PORT: `22`
- PROD_SSH_KEY: (private key from this document)

### Server Commands
```bash
# Deploy manually
bash /opt/tsh_erp/bin/deploy.sh main

# Rollback
bash /opt/tsh_erp/bin/rollback.sh

# Check status
systemctl status tsh_erp-blue tsh_erp-green

# View logs
journalctl -u tsh_erp-green -f
```

### Test Endpoints
```bash
curl http://167.71.39.50/health
curl http://167.71.39.50/queue/stats
```

---

**Setup Complete!** 🎉

Once you add the secrets to GitHub, every push to `main` will automatically:
1. Run all tests
2. Deploy to production (if tests pass)
3. Switch traffic with zero downtime
4. Keep previous version ready for instant rollback

**Production API**: http://167.71.39.50
**Status**: Ready for automated deployments
