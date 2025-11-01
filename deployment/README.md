# TSH ERP - CI/CD Deployment System

## 🎯 Overview

Production-ready CI/CD system with:
- ✅ **Zero-downtime** blue/green deployments
- ✅ **Automated testing** (lint, type-check, security, unit tests)
- ✅ **Database safety** (backup, staging test, transactional migrations)
- ✅ **Health-gated** traffic switching
- ✅ **Instant rollback** capability
- ✅ **No containers** - Pure Ubuntu + systemd + virtualenv

---

## 📁 Files Created

```
deployment/
├── nginx/
│   ├── tsh_erp.conf              # Main Nginx configuration
│   ├── tsh_erp_blue.conf         # Blue upstream
│   └── tsh_erp_green.conf        # Green upstream
├── systemd/
│   ├── tsh_erp-blue.service      # Blue systemd service
│   └── tsh_erp-green.service     # Green systemd service
├── scripts/
│   ├── deploy.sh                 # Main deployment script
│   ├── rollback.sh               # Rollback to previous version
│   ├── healthcheck.sh            # Health check utility
│   └── switch_upstream.sh        # Manual traffic switcher
├── env/
│   ├── prod.env.example          # Production environment template
│   └── staging.env.example       # Staging environment template
├── docs/
│   ├── CI_CD_SETUP_GUIDE.md      # Complete setup guide
│   └── QUICK_REFERENCE.md        # Quick command reference
└── README.md                      # This file

.github/
└── workflows/
    └── ci-deploy.yml              # GitHub Actions workflow

tds_core/
└── health_endpoint.py             # Health check endpoints for FastAPI
```

---

## 🚀 Quick Start

### 1. Server Setup (One-Time)

```bash
# SSH to your server
ssh root@your-server-ip

# Run setup commands from CI_CD_SETUP_GUIDE.md
# This includes:
#   - Installing dependencies
#   - Creating directory structure
#   - Configuring Nginx
#   - Setting up systemd services
#   - Deploying scripts
```

### 2. Configure GitHub

```bash
# Add these secrets to GitHub repository:
# Settings → Secrets and variables → Actions

PROD_HOST=your-server-ip
PROD_USER=root
PROD_SSH_KEY=<contents of private key>
PROD_SSH_PORT=22
```

### 3. Deploy

```bash
# Push to main branch
git add .
git commit -m "feat: new feature"
git push origin main

# GitHub Actions will:
#   1. Run tests
#   2. Deploy to server if tests pass
#   3. Switch traffic with zero downtime
```

---

## 📚 Documentation

- **[CI_CD_SETUP_GUIDE.md](docs/CI_CD_SETUP_GUIDE.md)** - Complete setup instructions
- **[QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)** - Quick command reference

---

## 🔄 Deployment Flow

```
1. Developer pushes to main
2. GitHub Actions triggers
3. Run tests (lint, type-check, security, unit)
4. SSH to production server
5. Run deploy.sh:
   ├─ Determine idle color (blue/green)
   ├─ Sync code from GitHub
   ├─ Create venv + install dependencies
   ├─ Backup production database
   ├─ Test migrations on staging database
   ├─ Start idle service
   ├─ Health check /ready endpoint
   ├─ Switch Nginx upstream → zero downtime!
   ├─ Run migrations on production database
   └─ Stop old service
6. Deployment complete ✅
```

---

## ⚡ Quick Commands

### Deploy
```bash
bash /opt/tsh_erp/bin/deploy.sh main
```

### Rollback
```bash
bash /opt/tsh_erp/bin/rollback.sh
```

### Check Status
```bash
# Which color is active?
readlink /etc/nginx/upstreams/tsh_erp_active.conf

# Service status
systemctl status tsh_erp-blue tsh_erp-green

# Health check
curl http://localhost/health
```

### View Logs
```bash
# Deployment logs
tail -f /opt/tsh_erp/shared/logs/api/deploy_*.log

# Application logs
journalctl -u tsh_erp-blue -f
```

---

## 🎯 Key Features

### Blue/Green Deployment
- Two identical environments (blue and green)
- One serves traffic, one is idle
- Deploy to idle → test → switch traffic
- Previous version remains ready for instant rollback

### Health Checks
- `/ready` - Simple readiness check
- `/health` - Detailed health with database check
- Deployment waits for health before switching traffic

### Database Safety
- Auto-backup before every deployment
- Test migrations on staging database first
- Transactional migrations (rollback on error)
- Backward-compatible migration policy

### Instant Rollback
- One command: `bash /opt/tsh_erp/bin/rollback.sh`
- Switches back to previous version
- No data loss
- Takes ~10 seconds

---

## 🛠 Technology Stack

- **Server**: Ubuntu 20.04+ (systemd)
- **Web Server**: Nginx (reverse proxy)
- **App Server**: Python 3.11+ + uvicorn
- **Database**: PostgreSQL 14+
- **CI/CD**: GitHub Actions
- **Deployment**: Bash scripts
- **Process Manager**: systemd

---

## 📊 Architecture

```
Internet
    ↓
Nginx (Port 80/443)
    ├─ /etc/nginx/upstreams/tsh_erp_active.conf → symlink
    ↓
    ├─ Blue:  127.0.0.1:8001  ← tsh_erp-blue.service
    └─ Green: 127.0.0.1:8002  ← tsh_erp-green.service
           ↓
    PostgreSQL (Port 5432)
```

---

## 🔐 Security

- Environment variables stored securely in `/opt/tsh_erp/shared/env/`
- SSH key-based authentication
- GitHub Secrets for CI/CD credentials
- Database backups before migrations
- Firewall configured (UFW)
- Optional: SSL/TLS with Let's Encrypt

---

## 📈 Monitoring

### Logs
- **Deployment**: `/opt/tsh_erp/shared/logs/api/`
- **Application**: `journalctl -u tsh_erp-blue`
- **Nginx**: `/var/log/nginx/`

### Metrics
- systemd service status
- Health endpoints
- Database connection pool
- Response times via Nginx logs

### Alerts (Optional)
- Slack/Discord/Telegram webhooks
- Email notifications
- Sentry for error tracking

---

## 🆘 Troubleshooting

### Deployment Failed?
```bash
# Check logs
tail -100 /opt/tsh_erp/shared/logs/api/deploy_*.log

# Check service
journalctl -u tsh_erp-blue -n 50
```

### Need to Rollback?
```bash
bash /opt/tsh_erp/bin/rollback.sh
```

### Service Won't Start?
```bash
# Check status
systemctl status tsh_erp-blue

# Check logs
journalctl -u tsh_erp-blue -n 100

# Try restart
sudo systemctl restart tsh_erp-blue
```

See **[CI_CD_SETUP_GUIDE.md](docs/CI_CD_SETUP_GUIDE.md)** for detailed troubleshooting.

---

## 📞 Support

1. Check **[QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)** for common commands
2. Review **[CI_CD_SETUP_GUIDE.md](docs/CI_CD_SETUP_GUIDE.md)** for detailed help
3. Check logs: `tail -f /opt/tsh_erp/shared/logs/api/*.log`
4. Contact DevOps team

---

## 🔄 Update This System

To update the CI/CD system itself:

1. Modify files in `deployment/` directory
2. Copy updated files to server
3. Test with manual deployment
4. Update documentation

---

## 📝 Version History

- **v1.0.0** (November 2024) - Initial release
  - Blue/green deployment
  - GitHub Actions integration
  - Health checks
  - Database safety
  - Rollback capability

---

## 📄 License

Internal use - TSH ERP System

---

**Created**: November 2024
**Status**: Production Ready ✅
**Maintained by**: TSH DevOps Team
