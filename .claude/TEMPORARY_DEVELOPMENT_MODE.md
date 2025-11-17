# TEMPORARY DEVELOPMENT MODE - TSH ERP Ecosystem

**Version:** 1.0.0
**Activated:** 2025-11-17
**Status:** ACTIVE - TEMPORARY MODE

---

## CRITICAL NOTICE

**THIS IS A TEMPORARY DEVELOPMENT MODE**

GitHub CI/CD, Staging Environment, and Production Pipelines are **DISABLED** until the project owner (Khaleel) sends explicit confirmation to re-enable them.

---

## Overview

The TSH ERP Ecosystem is now operating in a **TEMPORARY DEVELOPMENT MODE** with the following characteristics:

### Key Changes

1. **Direct Docker Deployment** - All deployments done via Docker commands directly on the development server
2. **Real Database Connection** - All components connect to the REAL production database in READ-ONLY mode
3. **No GitHub CI/CD** - All GitHub Actions workflows are disabled
4. **No Staging Environment** - Staging is bypassed entirely
5. **Simplified Pipeline** - Fast, direct development without automated pipelines

---

## Why This Mode?

```yaml
Benefits:
  - Faster development cycles (no CI/CD wait time)
  - Direct testing with real production data
  - Simplified deployment process
  - Reduced complexity during active development
  - Safe due to read-only database access (Zoho-controlled writes)

Safety Guarantees:
  - Database is READ-ONLY (no write operations)
  - All writes happen in Zoho Books/Inventory only
  - TDS Core controls data synchronization
  - No risk of corrupting production data
```

---

## Deployment Workflow

### OLD Workflow (DISABLED)
```
❌ develop branch → GitHub Actions → Staging Server → Test → PR → main branch → Production
```

### NEW Workflow (ACTIVE)
```
✅ Code Changes → Direct Docker Build → Direct Docker Deploy → Real Database (Read-Only)
```

---

## Development Server

```yaml
Server: 167.71.39.50 (same as production VPS)
User: root
Database: REAL production PostgreSQL (READ-ONLY)
Deployment Method: Direct Docker commands
Branch: develop (for version control)
```

---

## Docker Deployment Commands

### Standard Deployment
```bash
# 1. Connect to server
ssh root@167.71.39.50

# 2. Pull latest code
cd /var/www/tsh-erp
git pull origin develop

# 3. Build and restart containers
docker-compose build --no-cache
docker-compose down
docker-compose up -d

# 4. Verify health
curl http://localhost:8000/health
```

### Component-Specific Deployment

#### Backend Only
```bash
docker-compose build backend
docker-compose restart backend
```

#### TDS Core Only
```bash
docker-compose build tds-core
docker-compose restart tds-core
```

#### BFF Only
```bash
docker-compose build bff
docker-compose restart bff
```

#### All Services
```bash
docker-compose down && docker-compose up -d --build
```

---

## Docker Build Optimizations

### BuildKit (ENABLED)
BuildKit provides 30-50% faster builds with parallel layer processing.

```bash
# Already enabled in /etc/environment
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Verify it's active
echo $DOCKER_BUILDKIT  # Should show "1"
```

### Cache Warming (Optional)
Pre-pull base images before deployment to save network download time.

```bash
# Run the cache warming script
./scripts/deployment/warm_cache.sh

# This pre-pulls:
# - python:3.11-slim
# - postgres:15-alpine
# - redis:7-alpine
# - nginx:alpine
# - node:18-alpine
```

### Optimized Build Command
```bash
# Fastest deployment with BuildKit and caching
DOCKER_BUILDKIT=1 docker-compose up -d --build
```

**Performance Gains:**
- Build time: Reduced by 40-60%
- Parallel layer processing
- Better cache utilization
- Smaller final images (multi-stage builds already implemented)

---

## Database Connection

### Configuration
```yaml
Host: localhost (on VPS)
Port: 5432
Database: tsh_erp_production
User: tsh_app_user
Password: TSH@2025Secure!Production
Mode: READ-ONLY (enforced by application layer)
```

### Connection String
```
postgresql://tsh_app_user:TSH@2025Secure!Production@localhost:5432/tsh_erp_production
```

### Safety Measures
```python
# All services must use this pattern:
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# READ-ONLY connection
engine = create_engine(
    DATABASE_URL,
    connect_args={"options": "-c default_transaction_read_only=on"}
)
```

---

## What's DISABLED

### GitHub Actions Workflows (ALL SUSPENDED)
```yaml
Disabled Workflows:
  - ci.yml
  - ci-deploy.yml
  - ci-test-simple.yml
  - deploy-staging.yml
  - deploy-production.yml
  - docker-build.yml
  - build-and-push-ghcr.yml
  - flutter-ci.yml
  - nextjs-ci.yml
  - e2e-tests.yml
  - performance-test.yml
  - security-scan.yml
  - zoho-integration-test.yml
  - schema-drift-check.yml
  - validate-secrets.yml
  - notify.yml
  - dependabot-auto-merge.yml
  - cleanup-ghcr.yml
```

### Staging Environment
```yaml
Status: DISABLED
Server: 167.71.58.65 (NOT IN USE)
URL: https://staging.erp.tsh.sale (NOT ACTIVE)
Reason: All development goes directly to production server with real database
```

### Automated Pipelines
```yaml
Status: ALL DISABLED
- No automatic builds on push
- No automatic tests
- No automatic deployments
- No PR-triggered workflows
```

---

## What's ENABLED

### Direct Development
```yaml
✅ Direct SSH access to production server
✅ Direct Docker commands
✅ Direct database queries (read-only)
✅ Real-time testing with production data
✅ Fast iteration cycles
```

### Real Database Access
```yaml
✅ 2,218+ real products
✅ 500+ real clients
✅ Real stock levels
✅ Real sales orders
✅ Zoho-synchronized data
```

### Version Control
```yaml
✅ Git still used for code management
✅ develop branch for development
✅ Commits tracked normally
✅ No automated triggers
```

---

## Agent Configuration Updates

### DevOps Agent
```yaml
Mode: TEMPORARY_DEVELOPMENT_MODE
Deployment: Docker-only (no GitHub Actions)
Environment: Production server with read-only database
Commands: Direct Docker build/restart
Restrictions: No CI/CD pipeline interactions
```

### Security Agent
```yaml
Mode: TEMPORARY_DEVELOPMENT_MODE
Database: Read-only (safe by design)
Monitoring: Direct log checks
Restrictions: No write operations allowed
```

### TDS Core Agent
```yaml
Mode: TEMPORARY_DEVELOPMENT_MODE
Sync: One-directional (Zoho → ERP only)
Database: Read-only connection
Deployment: Direct Docker restart
```

### BFF Agent
```yaml
Mode: TEMPORARY_DEVELOPMENT_MODE
Database: Read-only connection
Deployment: Direct Docker commands
Testing: Real production data
```

---

## Important Restrictions

### DO NOT
```yaml
❌ Enable or trigger any GitHub Actions workflow
❌ Use staging environment (167.71.58.65)
❌ Create PRs expecting automated deployment
❌ Write to the database (READ-ONLY ENFORCED)
❌ Modify Zoho data (Phase 1 restriction still applies)
❌ Assume automated testing will run
```

### DO
```yaml
✅ Deploy directly via Docker commands
✅ Test with real production data
✅ Use git for version control (without CI/CD triggers)
✅ Connect to real database for read queries
✅ Build containers directly on server
✅ Monitor logs directly on VPS
```

---

## Quick Reference Commands

### Server Access
```bash
ssh root@167.71.39.50
```

### Deploy All Services
```bash
cd /var/www/tsh-erp && docker-compose up -d --build
```

### Check Logs
```bash
docker-compose logs -f backend
docker-compose logs -f tds-core
docker-compose logs -f bff
```

### Database Query (Read-Only)
```bash
PGPASSWORD='TSH@2025Secure!Production' psql -h localhost -U tsh_app_user \
  -d tsh_erp_production -c "SELECT COUNT(*) FROM products WHERE is_active = true;"
```

### Health Check
```bash
curl http://localhost:8000/health
curl http://localhost:8001/api/health  # TDS Core
curl http://localhost:8002/health      # BFF
```

### Container Status
```bash
docker ps
docker-compose ps
```

---

## Re-enabling GitHub CI/CD and Staging

**THIS SECTION IS FOR FUTURE REFERENCE ONLY**

GitHub CI/CD pipelines and staging environment will be re-enabled ONLY when Khaleel sends explicit confirmation with instructions like:

```
"Re-enable GitHub CI/CD and staging environment"
"Switch back to standard deployment workflow"
"Activate production pipelines"
```

Until such instruction is received, this TEMPORARY DEVELOPMENT MODE remains ACTIVE.

---

## Monitoring in Temporary Mode

### Manual Health Checks
```bash
# Backend
curl http://localhost:8000/health

# TDS Core
curl http://localhost:8001/api/health

# BFF
curl http://localhost:8002/health

# Database
PGPASSWORD='TSH@2025Secure!Production' psql -h localhost -U tsh_app_user \
  -d tsh_erp_production -c "SELECT NOW();"
```

### Log Monitoring
```bash
# Real-time logs
docker-compose logs -f --tail=100

# Specific service
docker-compose logs -f backend --tail=100

# Error filtering
docker-compose logs backend 2>&1 | grep -i error
```

---

## Emergency Procedures

### If Container Fails
```bash
# 1. Check status
docker-compose ps

# 2. Check logs
docker-compose logs <service-name> --tail=100

# 3. Restart service
docker-compose restart <service-name>

# 4. Rebuild if needed
docker-compose build <service-name> --no-cache
docker-compose up -d <service-name>
```

### If Database Connection Lost
```bash
# 1. Check PostgreSQL status
systemctl status postgresql

# 2. Restart if needed
systemctl restart postgresql

# 3. Test connection
PGPASSWORD='TSH@2025Secure!Production' psql -h localhost -U tsh_app_user \
  -d tsh_erp_production -c "SELECT 1;"
```

---

## Summary

This TEMPORARY DEVELOPMENT MODE provides:

1. **Speed** - No CI/CD wait times, direct deployment
2. **Safety** - Read-only database, no write risks
3. **Simplicity** - Direct Docker commands, no pipeline complexity
4. **Real Data** - Testing with actual production data
5. **Flexibility** - Fast iteration during active development

**REMEMBER:** This mode is TEMPORARY. Standard GitHub CI/CD and staging workflows will be re-enabled upon explicit instruction.

---

**Last Updated:** 2025-11-17
**Mode Status:** ACTIVE
**Next Review:** Upon explicit instruction from Khaleel

