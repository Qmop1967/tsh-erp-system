# 🌐 TSH ERP Server Infrastructure - CRITICAL REFERENCE

**⚠️ READ THIS FIRST BEFORE ANY DEPLOYMENT OR SERVER OPERATION**

---

## 🚨 CRITICAL: Two Separate Servers

### ⚠️ NEVER CONFUSE THESE TWO SERVERS - THEY ARE COMPLETELY DIFFERENT!

```
┌─────────────────────────────────────────────────────────────┐
│                    STAGING SERVER                           │
│  IP: 167.71.58.65 (DIFFERENT FROM PRODUCTION!)             │
│  User: khaleel                                              │
│  Password: Zcbm.97531tsh                                    │
│  Branch: develop                                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    PRODUCTION SERVER                        │
│  IP: 167.71.39.50 (DIFFERENT FROM STAGING!)                │
│  User: root                                                 │
│  Password: Zcbbm.97531tsh                                   │
│  Branch: main                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📍 Complete Server Details

### 🟦 STAGING SERVER (Pre-Production Testing)

```yaml
Purpose: Testing changes before production
Provider: DigitalOcean
Location: Europe
OS: Ubuntu 22.04.4 LTS
Hostname: tsh-erp-staging

Connection:
  IP Address: 167.71.58.65
  SSH User: khaleel
  SSH Password: Zcbm.97531tsh
  SSH Command: ssh khaleel@167.71.58.65

URLs:
  Backend API: https://staging.erp.tsh.sale
  Direct Access: http://167.71.58.65:8002
  API Docs: https://staging.erp.tsh.sale/docs
  Health Check: https://staging.erp.tsh.sale/health
  Consumer App: https://staging.consumer.tsh.sale

Git:
  Branch: develop
  Deployment: Auto-deploy on push to develop

Database:
  Host: localhost (on staging server)
  Port: 5432
  Database: tsh_erp_staging
  User: tsh_app_user
  Password: [staging_password]
  Connection: PGPASSWORD='[staging_password]' psql -h localhost -U tsh_app_user -d tsh_erp_staging

Services:
  Backend: tsh_erp-staging
  Status: systemctl status tsh_erp-staging
  Logs: journalctl -u tsh_erp-staging -f
  Restart: systemctl restart tsh_erp-staging

Project Path:
  Main: /home/khaleel/tsh-erp (or check with pwd after SSH)
  Note: May be in different location - verify on first SSH
```

---

### 🟩 PRODUCTION SERVER (Live Customer-Facing)

```yaml
Purpose: Live production environment with real customers
Provider: DigitalOcean
Location: Europe
OS: Ubuntu 22.04.4 LTS
Hostname: tsh-erp-production

Connection:
  IP Address: 167.71.39.50
  SSH User: root
  SSH Password: Zcbbm.97531tsh
  SSH Command: ssh root@167.71.39.50

URLs:
  Backend API: https://erp.tsh.sale
  ERP Admin: https://erp.tsh.sale
  Consumer App: https://consumer.tsh.sale
  Shop: https://shop.tsh.sale
  API Docs: https://erp.tsh.sale/docs
  Health Check: https://erp.tsh.sale/health
  TDS Dashboard: https://erp.tsh.sale/tds-admin/

Git:
  Branch: main
  Deployment: Auto-deploy on merge to main
  Path: /opt/tsh-erp

Database:
  Host: localhost (on production server)
  Port: 5432
  Database: tsh_erp_production
  User: tsh_app_user
  Password: TSH@2025Secure!Production
  Connection: PGPASSWORD='TSH@2025Secure!Production' psql -h localhost -U tsh_app_user -d tsh_erp_production
  Size: 127 MB, 57 tables, 2,218+ products

Services:
  Backend: tsh_erp-blue (blue-green deployment)
  Status: systemctl status tsh_erp-blue
  Logs: journalctl -u tsh_erp-blue -f
  Restart: systemctl restart tsh_erp-blue
  TDS Worker: tds-core-worker

Docker Containers:
  - tsh_erp_app (port 8000)
  - tsh_neurolink (port 8002)
  - tsh_postgres (port 5432)
  - tsh_redis (port 6379)

Project Path:
  Main: /opt/tsh-erp
  Releases: /opt/tsh-erp/releases/blue and /opt/tsh-erp/releases/green
```

---

## 🔄 Deployment Flow

```
Local Development
    ↓
git push origin develop
    ↓
STAGING SERVER (167.71.58.65)
    ↓
Manual Testing & Verification
    ↓
Create PR: develop → main
    ↓
Merge to main
    ↓
PRODUCTION SERVER (167.71.39.50)
```

---

## ⚡ Quick Commands Reference

### Staging Server (167.71.58.65)

```bash
# SSH to staging
ssh khaleel@167.71.58.65

# Check service status
ssh khaleel@167.71.58.65 "systemctl status tsh_erp-staging"

# View logs
ssh khaleel@167.71.58.65 "journalctl -u tsh_erp-staging -n 50"

# Check health
curl https://staging.erp.tsh.sale/health

# Check git status
ssh khaleel@167.71.58.65 "cd /home/khaleel/tsh-erp && git branch && git log -1"

# Database query
ssh khaleel@167.71.58.65 "PGPASSWORD='[password]' psql -h localhost -U tsh_app_user -d tsh_erp_staging -c 'SELECT COUNT(*) FROM products;'"
```

### Production Server (167.71.39.50)

```bash
# SSH to production
ssh root@167.71.39.50

# Check service status
ssh root@167.71.39.50 "systemctl status tsh_erp-blue"

# View logs
ssh root@167.71.39.50 "journalctl -u tsh_erp-blue -n 50"

# Check health
curl https://erp.tsh.sale/health

# Check git status
ssh root@167.71.39.50 "cd /opt/tsh-erp && git branch && git log -1"

# Database query
ssh root@167.71.39.50 "PGPASSWORD='TSH@2025Secure!Production' psql -h localhost -U tsh_app_user -d tsh_erp_production -c 'SELECT COUNT(*) FROM products;'"

# Docker containers
ssh root@167.71.39.50 "docker ps"
```

---

## 🚫 Common Mistakes to Avoid

### ❌ WRONG: Checking staging on production IP
```bash
# DON'T DO THIS
ssh root@167.71.39.50  # This is production, not staging!
```

### ✅ CORRECT: Check staging on staging IP
```bash
# DO THIS
ssh khaleel@167.71.58.65  # Correct staging server
```

### ❌ WRONG: Using root user for staging
```bash
# DON'T DO THIS
ssh root@167.71.58.65  # Wrong user for staging
```

### ✅ CORRECT: Use khaleel user for staging
```bash
# DO THIS
ssh khaleel@167.71.58.65  # Correct user
```

---

## 🎯 Decision Matrix: Which Server Should I Check?

| Scenario | Server to Check | IP Address | Branch |
|----------|----------------|------------|--------|
| Just pushed to `develop` branch | STAGING | 167.71.58.65 | develop |
| Testing before production | STAGING | 167.71.58.65 | develop |
| Need to verify staging deployment | STAGING | 167.71.58.65 | develop |
| Just merged PR to `main` | PRODUCTION | 167.71.39.50 | main |
| Customer-facing issue | PRODUCTION | 167.71.39.50 | main |
| Live system verification | PRODUCTION | 167.71.39.50 | main |

---

## 📋 Pre-Operation Checklist

**Before ANY server operation, ask yourself:**

1. ✅ Am I working with staging or production?
2. ✅ What is the correct IP address?
   - Staging: 167.71.58.65
   - Production: 167.71.39.50
3. ✅ What is the correct SSH user?
   - Staging: khaleel
   - Production: root
4. ✅ What branch should be deployed?
   - Staging: develop
   - Production: main
5. ✅ Do I need to check staging first before production?
   - Answer: YES, ALWAYS!

---

## 🧠 Memory Aid

**Remember the IPs by the last two digits:**

- **Staging (167.71.58.65)**: Ends in **65** → **6+5=11** → **DEVelop** has 11 letters (close enough)
- **Production (167.71.39.50)**: Ends in **50** → **5+0=5** → **MAIN** has 4 letters (close to 5)

**Or remember by user:**

- **khaleel** → **Staging** (167.71.58.65)
- **root** → **Production** (167.71.39.50)

---

## 📱 Quick Status Check Script

```bash
#!/bin/bash
# save as: check_both_servers.sh

echo "========================================="
echo "🟦 STAGING SERVER (167.71.58.65)"
echo "========================================="
echo "Health: $(curl -s -o /dev/null -w '%{http_code}' https://staging.erp.tsh.sale/health)"
ssh khaleel@167.71.58.65 "echo 'SSH: ✅ Connected' && systemctl is-active tsh_erp-staging || echo 'Service not found'"
echo ""

echo "========================================="
echo "🟩 PRODUCTION SERVER (167.71.39.50)"
echo "========================================="
echo "Health: $(curl -s -o /dev/null -w '%{http_code}' https://erp.tsh.sale/health)"
ssh root@167.71.39.50 "echo 'SSH: ✅ Connected' && systemctl is-active tsh_erp-blue"
echo ""
```

---

**Last Updated:** November 13, 2025
**Priority:** CRITICAL - Load this file FIRST in every session
**Review Frequency:** Every deployment or server operation

**🚨 WHEN IN DOUBT: CHECK THIS FILE FIRST! 🚨**
