# TSH ERP - Docker & GitHub Workflow Deployment Standards

**Version:** 1.0.0
**Last Updated:** 2025-11-17
**Status:** MANDATORY for all deployments

---

## Executive Summary

TSH ERP uses a **Docker-first deployment strategy** with **GitHub Actions CI/CD automation**. This document defines the mandatory standards for all deployments.

---

## Core Principles

### 1. Docker-First Architecture
- **Every service runs in its own container**
- All containers connect through shared Docker networks
- Docker Compose orchestrates multi-container applications
- Consistent environments: dev → staging → production

### 2. GitHub Actions Automation
- **CI/CD pipeline for every code push**
- Automated testing before deployment
- Automated building of Docker images
- Automated deployment via SSH
- Automated health checks and notifications

### 3. Environment Separation
- **Staging Environment**: `develop` branch → 167.71.58.65
- **Production Environment**: `main` branch → 167.71.39.50
- Environment-specific configuration files (.env.staging, .env.production)

---

## Deployment Architecture

### Current Implementation (SUPERIOR to basic proposal)

```
TSH ERP Deployment Pipeline
============================

[Code Push] → [Test] → [Build] → [Deploy] → [Health Check] → [Smoke Test] → [Notify]
                                      ↓
                              [Automatic Rollback on Failure]
```

### Key Features:
- **Blue-Green Deployment** for production (zero-downtime)
- **Automatic Rollback** if smoke tests fail
- **Database Backups** before production deployments
- **Multi-stage validation** (tests → build → deploy → verify)
- **Comprehensive notifications** via Telegram

---

## Docker Standards

### Container Structure
```yaml
Required Services:
  - tsh_erp_app          # FastAPI backend (port 8000 internal)
  - tsh_postgres         # PostgreSQL database (port 5432 internal)
  - tsh_redis            # Redis cache (port 6379 internal)
  - tsh_neurolink        # Notification service (port 8002 internal)
  - tds_admin_dashboard  # TDS Dashboard (port 3000 internal)

Optional Services:
  - tsh_worker           # Background workers (Celery)
  - tsh_flower           # Worker monitoring

Port Mapping:
  Staging:
    - Backend: 8004:8000
    - PostgreSQL: 5434:5432
    - Redis: 6380:6379
    - NeuroLink: 8003:8002
    - TDS Dashboard: 3001:3000

  Production:
    - Backend: 8001:8000 (blue) or 8011:8000 (green)
    - PostgreSQL: 5432:5432
    - Redis: 6379:6379
    - NeuroLink: 8002:8002
```

### Docker Compose Files
```
Current Structure (Recommended):
├── docker-compose.staging.yml     # Staging-specific configuration
├── docker-compose.production.yml  # Production-specific configuration
├── docker-compose.yml             # Base/development configuration
├── .env.staging                   # Staging environment variables
└── .env.production                # Production environment variables

Rationale:
- Separate compose files allow environment-specific resource limits
- Different port mappings avoid conflicts on shared servers
- Environment-specific build args and configurations
- Better control over service profiles
```

### Image Tagging Strategy
```bash
# Tag Format: service:environment-commit_sha
tsh-erp:staging-abc123def
tsh-erp:production-v2025.11.17-abc123
tsh-neurolink:staging-abc123def
tds-admin-dashboard:staging-abc123def

# Version tracking in .env
VERSION=staging-$(git rev-parse --short HEAD)
VERSION=production-v$(date +%Y.%m.%d)-$(git rev-parse --short HEAD)
```

---

## GitHub Workflow Standards

### Required Secrets

```yaml
# SSH Access
STAGING_SSH_KEY        # Private key for staging server (khaleel@167.71.58.65)
PROD_SSH_KEY           # Private key for production server (root@167.71.39.50)

# Docker Registry (Future Enhancement)
DOCKER_USERNAME        # For GHCR: github_username
DOCKER_TOKEN           # GitHub PAT with packages:write scope

# Notifications
TELEGRAM_BOT_TOKEN     # Bot token for deployment notifications
TELEGRAM_CHAT_ID       # Chat/group ID for notifications

# AWS (Backups)
AWS_ACCESS_KEY_ID      # For S3 backup storage
AWS_SECRET_ACCESS_KEY  # AWS secret key
AWS_S3_BUCKET          # Backup bucket name
AWS_REGION             # Default: eu-north-1

# Database
POSTGRES_PASSWORD      # Database password (URL-encoded if special chars)
```

### Workflow Structure

```yaml
# File: .github/workflows/deploy-staging.yml
name: Deploy to Staging
on:
  push:
    branches: [develop]
  workflow_dispatch:

jobs:
  test:        # Pre-deployment validation
  build:       # Docker image construction
  deploy:      # SSH deployment execution
  smoke-tests: # Post-deployment validation
  notify:      # Team notification
```

```yaml
# File: .github/workflows/deploy-production.yml
name: Deploy to Production (Blue-Green)
on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  determine-version:  # Version tagging
  pre-deployment:     # Validation checks
  backup-database:    # Data safety
  deploy:             # Blue-green deployment
  smoke-tests:        # Post-deployment validation
  rollback:           # Automatic failure recovery
  notify:             # Team notification
```

---

## Deployment Commands

### Standard Deployment Flow
```bash
# 1. SSH into server
ssh $DEPLOY_USER@$DEPLOY_HOST

# 2. Navigate to project
cd $DEPLOY_PATH

# 3. Pull latest code
git fetch origin
git checkout $BRANCH
git pull origin $BRANCH

# 4. Update dependencies (if needed)
source .venv/bin/activate
pip install -r requirements.txt --quiet

# 5. Build and start services
export VERSION=staging-$COMMIT_SHA
docker compose -f docker-compose.$ENV.yml pull || true
docker compose -f docker-compose.$ENV.yml up -d --build

# 6. Run migrations (if applicable)
docker compose exec app alembic upgrade head

# 7. Verify health
curl -sf http://localhost:$PORT/health
```

### Rollback Procedure
```bash
# 1. Identify previous working version
git log --oneline -10

# 2. Checkout previous version
git checkout $PREVIOUS_COMMIT

# 3. Restore dependencies
pip install -r requirements.txt --quiet

# 4. Restart services
docker compose -f docker-compose.$ENV.yml up -d --build

# 5. Verify rollback
curl -sf https://$DOMAIN/health
```

---

## Environment-Specific Configuration

### Staging (.env.staging)
```bash
ENVIRONMENT=staging
DEBUG=false
UVICORN_WORKERS=2

# Database
POSTGRES_DB=tsh_erp_staging
POSTGRES_USER=tsh_admin
POSTGRES_PASSWORD=TSH@2025Secure!Staging
DATABASE_URL=postgresql://tsh_admin:TSH%402025Secure%21Staging@tsh_postgres_staging:5432/tsh_erp_staging

# Redis
REDIS_URL=redis://redis_staging:6379/0

# Resource Limits
cpus: '1'
memory: 1G
```

### Production (.env.production)
```bash
ENVIRONMENT=production
DEBUG=false
UVICORN_WORKERS=4

# Database
POSTGRES_DB=tsh_erp_production
POSTGRES_USER=tsh_app_user
POSTGRES_PASSWORD=TSH@2025Secure!Production
DATABASE_URL=postgresql://tsh_app_user:TSH%402025Secure%21Production@tsh_postgres:5432/tsh_erp_production

# Redis
REDIS_URL=redis://redis:6379/0

# Resource Limits
cpus: '2'
memory: 2G

# Blue-Green
ACTIVE_DEPLOYMENT_SLOT=blue
```

---

## Security Standards

### Critical Requirements
1. **Never store credentials in code** - Use environment variables and GitHub Secrets
2. **SSH keys must have restricted permissions** - `chmod 600 ~/.ssh/id_rsa`
3. **Database passwords must be URL-encoded** - Special characters (@, !, #) need encoding
4. **Backups before production deployments** - Always backup before major changes
5. **Health checks mandatory** - Verify services are operational after deployment

### Container Security
```dockerfile
# Run as non-root user
USER appuser

# Minimal base images
FROM python:3.11-slim

# No sensitive data in layers
COPY --chown=appuser:appuser . .

# Read-only filesystem where possible
volumes:
  - type: tmpfs
    target: /tmp
```

---

## Monitoring & Observability

### Health Checks
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Required Health Endpoints
- `/health` - Basic health status
- `/docs` - API documentation
- `/openapi.json` - OpenAPI specification

### Notifications
- **Telegram alerts** for deployment success/failure
- **Email notifications** for critical failures (future)
- **Webhook integrations** for monitoring dashboards (future)

---

## Future Enhancements

### GitHub Container Registry (GHCR) Integration
```yaml
# Push images to GHCR for version management
- name: Login to GHCR
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}

- name: Build and Push
  uses: docker/build-push-action@v5
  with:
    push: true
    tags: ghcr.io/${{ github.repository }}/tsh-erp:${{ github.sha }}
```

Benefits:
- Versioned image storage
- Easy rollback to any previous version
- Reduced build times (pull instead of build)
- Better audit trail

### Unified Docker Compose (Optional)
```yaml
# Single docker-compose.yml with profiles
profiles:
  - staging
  - production

# Usage:
docker compose --profile staging up -d
docker compose --profile production up -d
```

---

## Compliance Checklist

### Every Deployment MUST:
- [ ] Run automated tests (lint, type-check, unit tests)
- [ ] Build Docker images successfully
- [ ] SSH to target server securely
- [ ] Pull latest code from appropriate branch
- [ ] Build/Pull Docker images
- [ ] Start services with proper environment
- [ ] Run database migrations (if applicable)
- [ ] Perform health checks
- [ ] Execute smoke tests
- [ ] Send deployment notification
- [ ] Support rollback capability

### Production Deployments MUST Also:
- [ ] Backup database before deployment
- [ ] Use blue-green deployment strategy
- [ ] Automatically rollback on failure
- [ ] Verify public endpoint accessibility
- [ ] Update deployment tracking

---

## Common Issues & Solutions

### Issue: DATABASE_URL with special characters
```bash
# Problem: @ and ! in password break URL parsing
DATABASE_URL=postgresql://user:TSH@2025Secure!@host/db  # WRONG

# Solution: URL-encode special characters
DATABASE_URL=postgresql://user:TSH%402025Secure%21@host/db  # CORRECT
# @ → %40
# ! → %21
# # → %23
```

### Issue: Port conflicts on shared server
```yaml
# Solution: Use environment-specific ports
staging:
  postgres: 5434:5432  # Not 5432:5432 (conflicts with production)
  backend: 8004:8000   # Not 8001:8000 (conflicts with production)
```

### Issue: Docker build cache not refreshing
```bash
# Solution: Force rebuild
docker compose build --no-cache
# or
docker compose up -d --build --force-recreate
```

### Issue: SQLAlchemy model conflicts
```python
# Solution: Ensure unique model class names
# If duplicate classes exist, rename with prefix:
class AdvancedUserSession(Base):  # Not just UserSession
    __tablename__ = "advanced_user_sessions"
```

---

## References

- GitHub Actions Documentation: https://docs.github.com/en/actions
- Docker Compose Documentation: https://docs.docker.com/compose/
- Blue-Green Deployment Pattern: https://martinfowler.com/bliki/BlueGreenDeployment.html
- GitHub Container Registry: https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry

---

**This document is the authoritative source for TSH ERP deployment standards. All CI/CD configurations, Docker setups, and deployment procedures MUST comply with these standards.**

---

*Document Created: 2025-11-17*
*Author: Claude Code (Senior Software Engineer)*
*Next Review: 2025-12-17*
