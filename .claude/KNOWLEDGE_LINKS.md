# Knowledge Links - Operational Resources

**Quick access to all TSH ERP operational resources**
**Last Updated:** 2025-11-12

---

## 🎯 Purpose

This file provides direct links to operational systems, dashboards, documentation, and tools for quick access during development and deployment.

---

## 🔗 GitHub Repository

### Main Repository
```
Repository: https://github.com/Qmop1967/tsh-erp-system
Owner: Qmop1967
Visibility: Private
```

### Branches
```yaml
Main Branches:
  - main: Production branch
    URL: https://github.com/Qmop1967/tsh-erp-system/tree/main
    Protection: Requires PR + approval

  - develop: Staging branch
    URL: https://github.com/Qmop1967/tsh-erp-system/tree/develop
    Auto-Deploy: staging.erp.tsh.sale

Feature Branches:
  - feature/*: Development branches
  - hotfix/*: Emergency fixes
  - bugfix/*: Bug fixes
```

### Quick Links
```
📍 Repository Home:     https://github.com/Qmop1967/tsh-erp-system
📍 Pull Requests:       https://github.com/Qmop1967/tsh-erp-system/pulls
📍 Issues:              https://github.com/Qmop1967/tsh-erp-system/issues
📍 Actions (CI/CD):     https://github.com/Qmop1967/tsh-erp-system/actions
📍 Settings:            https://github.com/Qmop1967/tsh-erp-system/settings
📍 Branches:            https://github.com/Qmop1967/tsh-erp-system/branches
📍 Commits:             https://github.com/Qmop1967/tsh-erp-system/commits
📍 Secrets:             https://github.com/Qmop1967/tsh-erp-system/settings/secrets/actions
```

---

## 🚀 CI/CD Pipelines (GitHub Actions)

### Workflows
```
📍 All Workflows:       https://github.com/Qmop1967/tsh-erp-system/actions
📍 Recent Runs:         https://github.com/Qmop1967/tsh-erp-system/actions/runs
📍 Workflow Files:      .github/workflows/
```

### Key Workflows
```yaml
ci-deploy.yml:
  - Triggers: Push to develop, merge to main
  - Jobs: test, deploy-staging, deploy-production
  - URL: https://github.com/Qmop1967/tsh-erp-system/actions/workflows/ci-deploy.yml

ci.yml:
  - Triggers: Push to branches, PRs
  - Jobs: Comprehensive CI tests
  - URL: https://github.com/Qmop1967/tsh-erp-system/actions/workflows/ci.yml

deploy-production.yml:
  - Triggers: Manual or merge to main
  - Jobs: Production deployment
  - URL: https://github.com/Qmop1967/tsh-erp-system/actions/workflows/deploy-production.yml

flutter-ci.yml:
  - Triggers: Changes to Flutter apps
  - Jobs: Flutter build and test
  - URL: https://github.com/Qmop1967/tsh-erp-system/actions/workflows/flutter-ci.yml

security-scan.yml:
  - Triggers: Scheduled and manual
  - Jobs: Security vulnerability scanning
  - URL: https://github.com/Qmop1967/tsh-erp-system/actions/workflows/security-scan.yml

Manual Actions:
  - View logs: gh run view <run-id> --log
  - Watch live: gh run watch <run-id>
  - Rerun: gh run rerun <run-id>
  - List runs: gh run list --limit 10
```

---

## 🖥️ VPS Servers (DigitalOcean)

### Production Server
```yaml
Provider: DigitalOcean
IP Address: 167.71.39.50
Location: Europe (EU-North-1)
OS: Ubuntu (latest LTS)
Purpose: Production environment
```

### Staging Server
```yaml
Provider: DigitalOcean
IP Address: 167.71.58.65
Hostname: tsh-erp-staging
Location: Europe
OS: Ubuntu 22.04.4 LTS
Purpose: Staging environment
User: khaleel
Password: Zcbm.97531tsh
```

### SSH Access
```bash
# Production server
ssh root@167.71.39.50

# Staging server
ssh khaleel@167.71.58.65

# Or using configured host (if set up)
ssh tsh-vps-prod      # Production
ssh tsh-vps-staging   # Staging

# SSH Config Location
~/.ssh/config

# SSH Key Location
~/.ssh/tsh_vps
~/.ssh/github_actions_tsh_erp
```

### Server Directories
```yaml
Production Backend:
  - Path: /opt/tsh_erp/releases/blue/
  - Service: tsh_erp-blue
  - Port: 8001
  - Alt Service: tsh_erp-green (blue-green deployment)

Staging Backend:
  - Path: /srv/tsh-staging/
  - Service: tsh_erp-staging
  - Port: 8002

Frontend (ERP Admin):
  - Production: /var/www/erp.tsh.sale/
  - Staging: /var/www/staging.erp.tsh.sale/

Consumer App (Flutter Web):
  - Production: /var/www/consumer.tsh.sale/
  - Staging: /var/www/staging.consumer.tsh.sale/

TDS Core:
  - Path: /opt/tds_core/
  - Service: tds-core-worker
  - Purpose: Zoho Books + Inventory sync orchestrator

Database:
  - Host: localhost
  - Port: 5432
  - Database: tsh_erp_production
  - User: tsh_app_user
```

### Server Management Commands
```bash
# Check services
systemctl status tsh_erp-blue
systemctl status tsh_erp-green
systemctl status tds-core-worker

# View logs
journalctl -u tsh_erp-blue -f
journalctl -u tsh_erp-blue -n 100
journalctl -u tds-core-worker -f

# Restart services
systemctl restart tsh_erp-blue
systemctl restart tds-core-worker

# Check disk space
df -h

# Check memory
free -h

# Check processes
ps aux | grep python
ps aux | grep uvicorn

# Check Docker containers (if using)
docker ps
docker-compose ps
```

### DigitalOcean Dashboard
```
📍 DigitalOcean Login:  https://cloud.digitalocean.com/
📍 Droplet Dashboard:   https://cloud.digitalocean.com/droplets
📍 Monitoring:          https://cloud.digitalocean.com/monitoring
📍 Networking:          https://cloud.digitalocean.com/networking
📍 Backups:             https://cloud.digitalocean.com/images/backups
```

---

## 🌐 Production URLs

### Live Applications
```yaml
Backend API:
  - URL: https://erp.tsh.sale
  - API Docs: https://erp.tsh.sale/docs
  - ReDoc: https://erp.tsh.sale/redoc
  - Health Check: https://erp.tsh.sale/health
  - Port: 8001 (internal)

ERP Admin Dashboard:
  - URL: https://erp.tsh.sale
  - Framework: React 18+
  - Purpose: ERP management interface

Consumer Web Shop:
  - URL: https://consumer.tsh.sale
  - Framework: Flutter Web
  - Purpose: Customer-facing shopping

Shop:
  - URL: https://shop.tsh.sale
  - Purpose: [Add specific purpose]

TDS Dashboard:
  - URL: https://erp.tsh.sale/tds-admin/
  - Purpose: Zoho Books + Inventory sync monitoring
  - Sync Status: https://erp.tsh.sale/tds-admin/sync
  - Statistics: https://erp.tsh.sale/tds-admin/statistics
  - Alerts: https://erp.tsh.sale/tds-admin/alerts
```

### Staging URLs
```yaml
Backend API:
  - URL: https://staging.erp.tsh.sale
  - Server: 167.71.58.65 (dedicated staging server)
  - Direct: http://167.71.58.65:8002
  - API Docs: https://staging.erp.tsh.sale/docs
  - Health Check: https://staging.erp.tsh.sale/health
  - Port: 8002

ERP Admin:
  - URL: https://staging.erp.tsh.sale
  - Server: 167.71.58.65

Consumer App:
  - URL: https://staging.consumer.tsh.sale
  - Server: 167.71.58.65
```

---

## 🗄️ Database

### PostgreSQL Production
```yaml
Host: localhost (on VPS 167.71.39.50)
Port: 5432
Database: tsh_erp_production
User: tsh_app_user
Password: [Stored in .env.production on VPS]

Connection String:
  postgresql://tsh_app_user:[password]@localhost:5432/tsh_erp_production
```

### PostgreSQL Development (Local/Docker)
```yaml
Host: localhost (or tsh_postgres if using Docker)
Port: 5432
Database: tsh_erp_production
User: tsh_app_user
Password: changeme123 (dev only)

Connection String:
  postgresql://tsh_app_user:changeme123@localhost:5432/tsh_erp_production
```

### Database Management
```bash
# Connect to production database (on VPS)
PGPASSWORD='TSH@2025Secure!Production' psql -h localhost -U tsh_app_user -d tsh_erp_production

# Connect to development database (local)
PGPASSWORD='changeme123' psql -h localhost -U tsh_app_user -d tsh_erp_production

# Quick queries
PGPASSWORD='changeme123' psql -h localhost -U tsh_app_user -d tsh_erp_production -c "SELECT COUNT(*) as total_products FROM products;"

PGPASSWORD='changeme123' psql -h localhost -U tsh_app_user -d tsh_erp_production -c "SELECT COUNT(*) as total_customers FROM customers;"

# Backup (manual)
pg_dump -h localhost -U tsh_app_user -d tsh_erp_production > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
psql -h localhost -U tsh_app_user -d tsh_erp_production < backup_file.sql
```

### Database Statistics
```yaml
Current Stats (as of PROJECT_VISION.md):
  - Total Tables: 57
  - Database Size: 127 MB
  - Total Products: 2,218+
  - Total Customers: 500+ (wholesale clients)
```

---

## ☁️ AWS Services

### AWS S3 (Backups)
```yaml
Service: Amazon S3
Bucket: tsh-erp-backups
Region: eu-north-1 (Stockholm)
Purpose: Database backups and restore
```

### AWS Console
```
📍 AWS Console:         https://console.aws.amazon.com/
📍 S3 Console:          https://s3.console.aws.amazon.com/s3/buckets/tsh-erp-backups?region=eu-north-1
📍 S3 Bucket URL:       s3://tsh-erp-backups/
📍 IAM Console:         https://console.aws.amazon.com/iam/
📍 CloudWatch Logs:     https://console.aws.amazon.com/cloudwatch/
```

### Backup Configuration
```yaml
Frequency: Daily (automated via scripts)
Retention: 30 days
Location: s3://tsh-erp-backups/
Backup Script: scripts/backup_to_s3.sh (if exists)
AWS Region: eu-north-1

GitHub Secrets Required:
  - AWS_ACCESS_KEY_ID
  - AWS_SECRET_ACCESS_KEY
  - AWS_REGION: eu-north-1
  - AWS_S3_BUCKET: tsh-erp-backups
```

---

## 🔄 Zoho Integration

### Zoho Books
```yaml
Organization ID: 748369814
API Base URL: https://www.zohoapis.com/books/v3/
API Documentation: https://www.zoho.com/books/api/v3/

Data Types:
  - Invoices and bills
  - Payments and receipts
  - Customers and vendors
  - Financial transactions
  - Accounts and ledgers
  - Tax calculations

Access: Via TDS Core ONLY (never direct)
```

### Zoho Inventory
```yaml
Organization ID: 748369814
API Base URL: https://www.zohoapis.com/inventory/v1/
API Documentation: https://www.zoho.com/inventory/api/v1/

Data Types:
  - Products (2,218+ items)
  - Stock levels (real-time)
  - Warehouses (multiple locations)
  - Inventory adjustments
  - Stock transfers
  - Product images

Access: Via TDS Core ONLY (never direct)
```

### Zoho Console
```
📍 Zoho Books:          https://books.zoho.com/app#/home/dashboard/748369814
📍 Zoho Inventory:      https://inventory.zoho.com/app#/home/748369814
📍 Zoho API Console:    https://api-console.zoho.com/
📍 Zoho Developer:      https://www.zoho.com/developer/
📍 OAuth Tokens:        https://accounts.zoho.com/
```

### TDS Dashboard (Sync Monitoring)
```
📍 TDS Dashboard:       https://erp.tsh.sale/tds-admin/
📍 Sync Status:         https://erp.tsh.sale/tds-admin/sync
📍 Sync Statistics:     https://erp.tsh.sale/tds-admin/statistics
📍 Sync Logs:           https://erp.tsh.sale/tds-admin/alerts
📍 Settings:            https://erp.tsh.sale/tds-admin/settings
```

---

## 📱 Mobile Apps

### App Store (iOS)
```
Note: Replace with actual URLs when apps are published

📍 TSH Admin App:           [App Store URL - Coming soon]
📍 Admin Mobile App:        [App Store URL - Coming soon]
📍 TSH HR Mobile App:       [App Store URL - Coming soon]
📍 TSH Retailer Shop App:   [App Store URL - Coming soon]
📍 TSH Inventory App:       [App Store URL - Coming soon]
📍 Travel Salesperson App:  [App Store URL - Coming soon]
📍 Wholesale Client App:    [App Store URL - Coming soon]
📍 TSH Consumer App:        [App Store URL - Coming soon]
📍 Partner Salesman App:    [App Store URL - Coming soon]
```

### Google Play Store (Android)
```
Note: Replace with actual URLs when apps are published

📍 TSH Admin App:           [Play Store URL - Coming soon]
📍 Admin Mobile App:        [Play Store URL - Coming soon]
📍 TSH HR Mobile App:       [Play Store URL - Coming soon]
📍 TSH Retailer Shop App:   [Play Store URL - Coming soon]
📍 TSH Inventory App:       [Play Store URL - Coming soon]
📍 Travel Salesperson App:  [Play Store URL - Coming soon]
📍 Wholesale Client App:    [Play Store URL - Coming soon]
📍 TSH Consumer App:        [Play Store URL - Coming soon]
📍 Partner Salesman App:    [Play Store URL - Coming soon]
```

### App Testing
```
📍 TestFlight (iOS):        [TestFlight URL when set up]
📍 Firebase App Dist:       [Firebase URL if used]
```

### Mobile App Directories
```
Local Development:
  /Users/khaleelal-mulla/TSH_ERP_Ecosystem/mobile/flutter_apps/
    ├── 01_tsh_admin_app/
    ├── 02_admin_mobile_app/
    ├── 03_tsh_hr_mobile_app/
    ├── 04_tsh_retailer_shop_app/
    ├── 05_tsh_inventory_management_app/
    ├── 06_travel_salesperson_app/
    ├── 07_wholesale_client_app/
    ├── 08_partner_salesman_app/
    └── 10_tsh_consumer_app/
```

---

## 🛠️ Development Tools

### IDE & Editors
```yaml
Primary IDE: Cursor (AI-powered IDE)
Project Path: /Users/khaleelal-mulla/TSH_ERP_Ecosystem/
Settings: .cursor/ and .vscode/ (Cursor uses VS Code settings)
Extensions:
  - Python
  - Pylance
  - Flutter
  - Dart
  - Docker
  - PostgreSQL
  - GitLens
  - ESLint
  - Prettier
```

### Local Development
```yaml
Backend:
  - Local URL: http://localhost:8000
  - API Docs: http://localhost:8000/docs
  - ReDoc: http://localhost:8000/redoc
  - Database: localhost:5432 (or tsh_postgres if Docker)

Frontend (ERP Admin):
  - Local URL: http://localhost:3000
  - Dev Server: npm run dev
  - Directory: /apps/erp-admin/ (or frontend/)

Consumer App:
  - Local URL: http://localhost:3001
  - Dev Server: flutter run -d chrome
  - Directory: /mobile/flutter_apps/10_tsh_consumer_app/

Docker Compose:
  - Command: docker-compose up
  - Profiles: dev, proxy, core
  - Compose File: docker-compose.yml
  - Development: docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Package Managers
```yaml
Python:
  - pip / pip3
  - Virtual Environment: .venv/
  - Requirements: requirements.txt
  - Activate: source .venv/bin/activate

Node.js:
  - npm
  - Package file: package.json
  - Lock file: package-lock.json

Flutter:
  - flutter pub get
  - pubspec.yaml
```

---

## 📊 Monitoring & Analytics

### Server Monitoring
```
📍 DigitalOcean Monitoring: https://cloud.digitalocean.com/monitoring
📍 Droplet Graphs:          https://cloud.digitalocean.com/droplets/[your-droplet-id]/graphs
📍 Metrics Dashboard:       https://cloud.digitalocean.com/monitoring/dashboards

DigitalOcean Monitoring Features:
  - CPU usage tracking
  - Memory usage tracking
  - Disk I/O monitoring
  - Network bandwidth monitoring
  - Load average tracking
  - Alert policies (can be configured)

Note: For additional monitoring, consider adding:
  - Uptime monitoring (UptimeRobot - free tier available)
  - Error tracking (Sentry - free tier available)
  - Log aggregation (Papertrail - free tier available)
```

### Application Monitoring
```
Currently: Using DigitalOcean built-in monitoring

Future Enhancement Options:
  - API Performance: New Relic (free tier), DataDog (trial)
  - Error Tracking: Sentry.io (free tier for 5K events/month)
  - Log Aggregation: Papertrail (free tier for 50MB/month)
  - Uptime Monitoring: UptimeRobot (free tier for 50 monitors)
```

### Health Checks
```bash
# Production health checks
curl https://erp.tsh.sale/health
curl -I https://consumer.tsh.sale/
curl -I https://shop.tsh.sale/

# Staging health checks
curl https://staging.erp.tsh.sale/health
curl -I https://staging.consumer.tsh.sale/

# TDS Core health
curl https://erp.tsh.sale/tds-admin/sync
```

---

## 📚 Documentation

### Internal Documentation
```
📍 Project README:      /README.md
📍 Architecture Docs:   /docs/architecture/
📍 API Documentation:   /docs/api/
📍 Deployment Docs:     /docs/deployment/
📍 Integration Docs:    /docs/integrations/
📍 .claude/ System:     /.claude/ (AI context system)
```

### External Documentation
```
📍 FastAPI Docs:        https://fastapi.tiangolo.com/
📍 Flutter Docs:        https://flutter.dev/docs
📍 React Docs:          https://react.dev/
📍 PostgreSQL Docs:     https://www.postgresql.org/docs/15/
📍 Docker Docs:         https://docs.docker.com/
📍 Zoho Books API:      https://www.zoho.com/books/api/v3/
📍 Zoho Inventory API:  https://www.zoho.com/inventory/api/v1/
📍 SQLAlchemy Docs:     https://docs.sqlalchemy.org/
📍 Pydantic Docs:       https://docs.pydantic.dev/
```

### Knowledge Base
```
📍 GitHub Wiki:         https://github.com/Qmop1967/tsh-erp-system/wiki (if set up)
📍 Notion:              [Notion workspace URL if used]
📍 Google Docs:         [Google Drive folder URL if used]
📍 Confluence:          [Confluence space URL if used]
```

---

## 🔐 Credentials & Secrets

### Important Notes
```
⚠️  NEVER commit credentials to Git
⚠️  Credentials stored in:
    - Local: .env (git-ignored)
    - Production: .env.production on VPS
    - GitHub: GitHub Secrets (for Actions)

Access Locations:
- Local .env file: /Users/khaleelal-mulla/TSH_ERP_Ecosystem/.env
- VPS .env file: /opt/tsh_erp/releases/blue/.env.production
- GitHub Secrets: https://github.com/Qmop1967/tsh-erp-system/settings/secrets/actions
```

### GitHub Secrets Management
```
📍 GitHub Secrets:      https://github.com/Qmop1967/tsh-erp-system/settings/secrets/actions

Required Secrets:
  - VPS_SSH_KEY
  - VPS_HOST (167.71.39.50)
  - VPS_USER (root)
  - AWS_ACCESS_KEY_ID
  - AWS_SECRET_ACCESS_KEY
  - AWS_REGION (eu-north-1)
  - AWS_S3_BUCKET (tsh-erp-backups)
  - DATABASE_URL
  - SECRET_KEY
  - ZOHO_CLIENT_ID
  - ZOHO_CLIENT_SECRET
  - ZOHO_REFRESH_TOKEN
  - ZOHO_ORGANIZATION_ID (748369814)

Manage via CLI:
  gh secret list
  gh secret set SECRET_NAME
  gh secret delete SECRET_NAME
```

---

## 🌐 Domain Management

### Domain Provider
```yaml
Provider: Namecheap
Domains:
  - erp.tsh.sale
  - consumer.tsh.sale
  - shop.tsh.sale
  - staging.erp.tsh.sale
  - staging.consumer.tsh.sale
  - tsh.sale (root domain)
```

### DNS Management
```
📍 Namecheap Dashboard: https://ap.www.namecheap.com/
📍 Domain List:         https://ap.www.namecheap.com/domains/list/
📍 DNS Management:      https://ap.www.namecheap.com/domains/domaincontrolpanel/tsh.sale/advancedns

DNS Records (Current Configuration):
  Production:
    - A Record: erp.tsh.sale → 167.71.39.50
    - A Record: consumer.tsh.sale → 167.71.39.50
    - A Record: shop.tsh.sale → 167.71.39.50

  Staging:
    - A Record: staging.erp.tsh.sale → 167.71.58.65
    - A Record: staging.consumer.tsh.sale → 167.71.58.65
```

### SSL Certificates
```yaml
Provider: Let's Encrypt (free)
Certificate Manager: Certbot (on VPS)
Renewal: Automatic (every 90 days)
Check Certificate: https://www.ssllabs.com/ssltest/

Certbot Commands (on VPS):
  - List certificates: certbot certificates
  - Renew: certbot renew
  - Test renewal: certbot renew --dry-run
```

---

## 🚨 Emergency Contacts & Procedures

### Emergency Procedures

#### Production Down:
```bash
1. Check health endpoint
   curl https://erp.tsh.sale/health

2. SSH to VPS
   ssh root@167.71.39.50

3. Check service status
   systemctl status tsh_erp-blue

4. Check logs (last 100 lines)
   journalctl -u tsh_erp-blue -n 100

5. Restart service if needed
   systemctl restart tsh_erp-blue

6. Verify restoration
   curl https://erp.tsh.sale/health

7. If still down, check blue-green switch
   bash /opt/tsh_erp/bin/switch_deployment.sh
```

#### Database Issues:
```bash
1. Check database connection
   PGPASSWORD='[pwd]' psql -h localhost -U tsh_app_user -d tsh_erp_production -c "SELECT 1;"

2. Check disk space
   df -h

3. Check PostgreSQL status
   systemctl status postgresql

4. Review PostgreSQL logs
   journalctl -u postgresql -n 100

5. Restore from AWS S3 backup if corrupted
   [See backup restore procedure]
```

#### Zoho Sync Failures:
```bash
1. Check TDS Dashboard
   Open: https://erp.tsh.sale/tds-admin/

2. Review sync logs
   Click on "Alerts" or "Logs" tab

3. Check TDS Core service
   ssh root@167.71.39.50
   systemctl status tds-core-worker
   journalctl -u tds-core-worker -n 100

4. Restart TDS Core if needed
   systemctl restart tds-core-worker

5. Manual sync trigger (if available)
   Via TDS Dashboard interface
```

### Contacts
```yaml
Project Owner:        Khaleel Al-Mulla
System Administrator: [Add contact if different]
Database Admin:       [Add contact]
DevOps Lead:          [Add contact]
Emergency Phone:      [Add emergency contact number]
```

---

## 📝 Quick Command Reference

### GitHub CLI (gh)
```bash
# Repository
gh repo view Qmop1967/tsh-erp-system

# Pull requests
gh pr list
gh pr create --base main --head develop --title "Deploy to Production"
gh pr view [number]
gh pr merge [number] --squash

# GitHub Actions
gh run list --limit 10
gh run watch [run-id]
gh run view [run-id] --log
gh workflow list
gh workflow view ci-deploy.yml

# Secrets
gh secret list
gh secret set SECRET_NAME
```

### Git Commands
```bash
# Status and info
git status
git log --oneline -10
git branch
git remote -v

# Push to staging
git add .
git commit -m "feat: add new feature"
git push origin develop

# Create PR (after pushing to develop)
gh pr create --base main --head develop --title "Deploy: Feature Name"

# Pull latest
git pull origin develop
```

### Server Commands (via SSH)
```bash
# SSH to Production VPS
ssh root@167.71.39.50

# SSH to Staging VPS
ssh khaleel@167.71.58.65

# Production Services
systemctl status tsh_erp-blue
systemctl restart tsh_erp-blue
systemctl status tds-core-worker
journalctl -u tsh_erp-blue -f
journalctl -u tsh_erp-blue -n 100

# Staging Services
ssh khaleel@167.71.58.65
systemctl status tsh_erp-staging  # Check staging service
journalctl -u tsh_erp-staging -f   # View staging logs

# Production Database
PGPASSWORD='TSH@2025Secure!Production' psql -h localhost -U tsh_app_user -d tsh_erp_production

# Staging Database (on staging server)
ssh khaleel@167.71.58.65
PGPASSWORD='[staging_password]' psql -h localhost -U tsh_app_user -d tsh_erp_staging

# Quick queries
PGPASSWORD='TSH@2025Secure!Production' psql -h localhost -U tsh_app_user -d tsh_erp_production -c "SELECT COUNT(*) FROM products;"

# System health
df -h
free -h
top
htop
```

### Health Checks
```bash
# Production
curl https://erp.tsh.sale/health
curl -I https://consumer.tsh.sale/
curl -I https://shop.tsh.sale/

# Staging
curl https://staging.erp.tsh.sale/health
curl -I https://staging.consumer.tsh.sale/

# TDS Sync Status
curl https://erp.tsh.sale/tds-admin/sync
```

### Docker Commands
```bash
# Local development
docker-compose up
docker-compose up -d  # Detached mode
docker-compose down
docker-compose logs -f backend
docker-compose ps

# On VPS (if using Docker)
docker ps
docker logs tsh_backend_container
docker exec -it tsh_backend_container bash
```

---

## 🔄 Regular Maintenance

### Daily
- [ ] Check GitHub Actions for failed runs
- [ ] Monitor TDS Dashboard for sync status
- [ ] Review error logs if any issues reported
- [ ] Verify production health endpoints

### Weekly
- [ ] Review AWS S3 backups
- [ ] Check server disk space (df -h)
- [ ] Review performance metrics
- [ ] Check for dependency updates (Dependabot)

### Monthly
- [ ] Review and clean old git branches
- [ ] Update dependencies (security patches)
- [ ] Review and optimize database queries
- [ ] Check SSL certificate expiration (auto-renewed)
- [ ] Review AWS costs and usage

---

## 📌 Bookmarks to Keep Handy

### Most Frequently Used
```
1. GitHub Repository:     https://github.com/Qmop1967/tsh-erp-system
2. GitHub Actions:        https://github.com/Qmop1967/tsh-erp-system/actions
3. Production Health:     https://erp.tsh.sale/health
4. Staging Health:        https://staging.erp.tsh.sale/health
5. TDS Dashboard:         https://erp.tsh.sale/tds-admin/
6. API Docs:              https://erp.tsh.sale/docs
7. Production SSH:        ssh root@167.71.39.50
8. Staging SSH:           ssh khaleel@167.71.58.65
9. GitHub Secrets:        https://github.com/Qmop1967/tsh-erp-system/settings/secrets/actions
10. AWS S3 Console:       https://s3.console.aws.amazon.com/s3/buckets/tsh-erp-backups?region=eu-north-1
11. Zoho Books:           https://books.zoho.com/app#/home/dashboard/748369814
12. Zoho Inventory:       https://inventory.zoho.com/app#/home/748369814
```

---

**Note:** This file contains operational links and non-sensitive information. Keep it updated when URLs or infrastructure changes.

**Security Reminder:** This file is in `.claude/` which should be git-ignored. Never commit actual credentials or sensitive information to version control.

**Last Updated:** 2025-11-12 by Claude Code
