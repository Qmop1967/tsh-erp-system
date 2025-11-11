# TSH ERP CI/CD System Documentation

Comprehensive CI/CD pipeline using GitHub Actions for the TSH ERP Ecosystem.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Workflows](#workflows)
- [Getting Started](#getting-started)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Monitoring](#monitoring)

## Overview

The TSH ERP CI/CD system provides automated building, testing, security scanning, and deployment capabilities across three environments:

- **Development** - Local Mac environment for feature development
- **Staging** - Remote server (167.71.58.65) for integration testing
- **Production** - Production server (167.71.39.50) for live deployment

### Key Features

- **Automated Testing**: Unit, integration, and E2E tests with pytest
- **Security First**: Continuous vulnerability scanning with Trivy
- **Schema Validation**: Automated drift detection before deployment
- **Performance Testing**: Load testing with Locust
- **Mobile CI**: Flutter matrix builds for 11 mobile apps
- **Frontend CI**: Next.js pipeline with bundle analysis
- **Auto Rollback**: Automatic rollback on deployment failure
- **Weekly Reports**: DevOps metrics and health assessments

### Technology Stack

- **CI/CD Platform**: GitHub Actions
- **Container Registry**: GitHub Container Registry (GHCR)
- **Testing**: pytest, factory_boy, Faker
- **Security**: Trivy, Bandit, Safety
- **Performance**: Locust
- **Notifications**: Telegram Bot API
- **Monitoring**: GitHub Insights (Grafana/Prometheus planned)

## Architecture

### Branching Strategy (GitFlow)

```
main (production)
  └── develop (staging)
       ├── feature/* (development)
       ├── hotfix/* (urgent fixes)
       └── release/* (release preparation)
```

### Workflow Hierarchy

```
┌─────────────────────────────────────┐
│     Main CI Pipeline (ci.yml)       │
│  ┌───────────────────────────────┐  │
│  │  Code Quality & Linting       │  │
│  │  Unit Tests                   │  │
│  │  Integration Tests            │  │
│  │  Build & Push Docker Images   │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
              │
              ├─── Reusable Workflows
              │    ├── docker-build.yml
              │    ├── validate-secrets.yml
              │    ├── schema-drift-check.yml
              │    └── notify.yml
              │
              ├─── Specialized Pipelines
              │    ├── nextjs-ci.yml
              │    ├── flutter-ci.yml
              │    ├── security-scan.yml
              │    ├── e2e-tests.yml
              │    └── performance-test.yml
              │
              └─── Deployment & Ops
                   ├── deploy-production.yml
                   ├── weekly-devops-report.yml
                   └── cleanup-ghcr.yml
```

### Service Architecture

```
┌──────────────────────────────────────────────────┐
│               TSH ERP Ecosystem                  │
├──────────────────────────────────────────────────┤
│  App (FastAPI)     - Main backend API           │
│  Neurolink         - AI/ML service               │
│  TDS Core v3.1.0   - Zoho Books sync engine     │
│  PostgreSQL 15     - Primary database            │
│  Redis 7           - Cache & sessions            │
│  TDS Admin         - Next.js admin dashboard     │
│  11 Flutter Apps   - Mobile frontends            │
└──────────────────────────────────────────────────┘
```

## Workflows

### Core Workflows

#### 1. Main CI Pipeline (`ci.yml`)

**Triggers**: Push to main/develop, PRs
**Jobs**:
- Secret validation
- Code quality (ruff, black, isort, bandit)
- Unit tests with coverage
- Integration tests (PostgreSQL + Redis)
- Service dependency validation
- Docker image build and push
- Notification on success/failure

**Usage**:
```bash
# Automatically runs on push
git push origin develop

# Or trigger manually
gh workflow run ci.yml
```

**Duration**: ~8-12 minutes

#### 2. Security Scanning (`security-scan.yml`)

**Triggers**: Daily at 2 AM UTC, manual, workflow_call
**Scans**:
- Docker image vulnerabilities (Trivy)
- Python dependencies (Safety)
- Code security issues (Bandit)
- Filesystem vulnerabilities

**Usage**:
```bash
# Manual trigger
gh workflow run security-scan.yml

# Called from other workflows
uses: ./.github/workflows/security-scan.yml
with:
  scan_type: docker
  fail_on_severity: CRITICAL
```

**Output**: SARIF reports uploaded to GitHub Security tab

#### 3. Schema Drift Detection (`schema-drift-check.yml`)

**Triggers**: Daily at 1 AM UTC, before deployments
**Checks**:
- Compares production/staging DB schema with ORM models
- Detects missing migrations
- Classifies drift severity (CRITICAL, MAJOR, MINOR)

**Usage**:
```bash
# Check production drift
gh workflow run schema-drift-check.yml \
  -f environment=production \
  -f fail_on_drift=true

# Check staging drift (non-blocking)
gh workflow run schema-drift-check.yml \
  -f environment=staging \
  -f fail_on_drift=false
```

**Severity Levels**:
- **CRITICAL**: DROP TABLE, DROP COLUMN, data loss
- **MAJOR**: ALTER TABLE, ADD CONSTRAINT, schema changes
- **MINOR**: CREATE INDEX, comments, cosmetic changes

#### 4. E2E Testing (`e2e-tests.yml`)

**Triggers**: Manual, scheduled (daily)
**Tests**:
- Authentication flows
- Business logic (inventory, sales, purchasing)
- API endpoints
- Integration points

**Usage**:
```bash
# Run full E2E suite
gh workflow run e2e-tests.yml

# Run specific test type
gh workflow run e2e-tests.yml -f test_type=api
```

**Test Categories**:
- Authentication (login, logout, token refresh)
- API (CRUD operations, validation)
- Business (order processing, inventory management)

#### 5. Production Deployment (`deploy-production.yml`)

**Triggers**: Manual only (safety measure)
**Steps**:
1. Pre-deployment checks (secrets, schema, security)
2. Database backup (local + S3)
3. Code deployment with zero-downtime
4. Database migrations
5. Service restart
6. Smoke tests
7. Auto-rollback on failure

**Usage**:
```bash
# Deploy latest main branch
gh workflow run deploy-production.yml

# Deploy specific version
gh workflow run deploy-production.yml \
  -f version=v1.2.3

# Skip backup (not recommended)
gh workflow run deploy-production.yml \
  -f skip_backup=true
```

**Rollback Process**:
- Automatic on smoke test failure
- Restores previous git commit
- Reverts dependencies
- Restarts services
- Verifies health

### Frontend & Mobile Workflows

#### 6. Next.js CI (`nextjs-ci.yml`)

**Triggers**: Push to tds-admin-dashboard/, PRs
**Jobs**:
- Setup and dependency caching (pnpm)
- ESLint and Prettier checks
- TypeScript type checking
- Unit/integration tests
- Production build
- Bundle size analysis

**Features**:
- pnpm caching for faster installs
- Next.js build cache
- Bundle size tracking
- Automatic artifact upload

#### 7. Flutter CI (`flutter-ci.yml`)

**Triggers**: Push to mobile_apps/, PRs
**Jobs**:
- App discovery (auto-detects Flutter apps)
- Code analysis (flutter analyze)
- Format checking (dart format)
- Unit tests with coverage
- Android APK build (debug + release)
- iOS build (disabled by default - expensive)

**Matrix Strategy**:
Automatically builds all apps in `mobile_apps/`:
- tsh_sales
- tsh_inventory
- tsh_warehouse
- tsh_delivery
- (+ 7 more apps)

**Usage**:
```bash
# Build all apps
gh workflow run flutter-ci.yml

# Build specific app
gh workflow run flutter-ci.yml \
  -f app_name=tsh_sales \
  -f build_platform=android
```

#### 8. Performance Testing (`performance-test.yml`)

**Triggers**: Weekly (Sundays 2 AM), manual
**Test Scenarios**:
- API Basic: Lightweight operations (products, customers)
- API Heavy: Complex queries (reports, analytics)
- Web Browsing: Frontend navigation

**Configuration**:
```bash
# Test staging with 100 users for 5 minutes
gh workflow run performance-test.yml \
  -f target_url=https://staging.erp.tsh.sale \
  -f users=100 \
  -f spawn_rate=10 \
  -f run_time=5m
```

**Locust Scenarios**:
- `APIBasicUser`: Product/customer viewing, search
- `APIHeavyUser`: Sales orders, reports, dashboard
- `WebBrowsingUser`: Docs, homepage, health checks

### Maintenance Workflows

#### 9. GHCR Cleanup (`cleanup-ghcr.yml`)

**Triggers**: Weekly (Sundays 3 AM), manual
**Actions**:
- Deletes images older than 30 days
- Keeps last 10 versions per service
- Protects tagged versions (latest, v*.*.*)

#### 10. Weekly DevOps Report (`weekly-devops-report.yml`)

**Triggers**: Weekly (Mondays 9 AM), manual
**Metrics**:
- Commit activity and contributors
- Pull request statistics
- Issue tracking
- Workflow success rates
- Code change analysis
- Dependabot activity

**Output**:
- GitHub issue with full report
- Telegram notification with summary
- Downloadable JSON metrics

#### 11. Dependabot Auto-Merge (`dependabot-auto-merge.yml`)

**Triggers**: Dependabot PRs
**Auto-Merge Criteria**:
- Patch version updates
- Development dependencies
- CI passes successfully
- From dependabot[bot]

## Getting Started

### Prerequisites

1. **GitHub CLI** installed and authenticated
2. **GitHub Secrets** configured (see [github-secrets-setup.md](github-secrets-setup.md))
3. **SSH Access** to staging and production servers
4. **Telegram Bot** for notifications (optional)

### Initial Setup

#### 1. Configure GitHub Secrets

```bash
# Required secrets (50+ total)
gh secret set PROD_SSH_KEY < ~/.ssh/id_rsa
gh secret set PROD_HOST -b "167.71.39.50"
gh secret set PROD_DB_PASSWORD -b "your-password"
gh secret set TELEGRAM_BOT_TOKEN -b "your-token"
gh secret set TELEGRAM_CHAT_ID -b "your-chat-id"

# See full list in github-secrets-setup.md
```

#### 2. Verify Workflows

```bash
# List all workflows
gh workflow list

# Check workflow status
gh workflow view ci.yml

# View recent runs
gh run list --workflow=ci.yml --limit 5
```

#### 3. Run Initial Validation

```bash
# Validate secrets
gh workflow run validate-secrets.yml \
  -f environment=production \
  -f check_scope=deployment

# Check schema drift
gh workflow run schema-drift-check.yml \
  -f environment=staging

# Run security scan
gh workflow run security-scan.yml \
  -f scan_type=all
```

### Daily Development Workflow

#### Feature Development

```bash
# 1. Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/new-feature

# 2. Make changes and commit
git add .
git commit -m "Add new feature"

# 3. Push and create PR
git push origin feature/new-feature
gh pr create --base develop --title "Add new feature"

# 4. CI automatically runs
# - Code quality checks
# - Unit tests
# - Integration tests
# - Docker build

# 5. Merge PR after approval
gh pr merge --squash
```

#### Hotfix Process

```bash
# 1. Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-fix

# 2. Fix issue and test locally
git add .
git commit -m "Fix critical issue"

# 3. Push and create PR to main
git push origin hotfix/critical-fix
gh pr create --base main --title "Hotfix: Critical issue"

# 4. After CI passes, merge to main
gh pr merge --squash

# 5. Deploy to production
gh workflow run deploy-production.yml

# 6. Merge back to develop
git checkout develop
git merge main
git push origin develop
```

### Deployment Process

#### Staging Deployment

```bash
# Staging deploys automatically on merge to develop
git checkout develop
git merge feature/new-feature
git push origin develop

# CI runs and deploys to staging server
# Monitor at: https://staging.erp.tsh.sale
```

#### Production Deployment

```bash
# 1. Merge develop to main
git checkout main
git pull origin main
git merge develop
git push origin main

# 2. Verify pre-deployment checks
gh workflow run deploy-production.yml --ref main

# 3. Monitor deployment
gh run watch

# 4. Check deployment status
curl https://erp.tsh.sale/health
```

## Best Practices

### Writing Tests

#### Unit Tests

```python
# tests/unit/test_service.py
import pytest
from app.services.product import ProductService

def test_get_product_by_id(db_session, sample_product):
    """Test retrieving product by ID"""
    service = ProductService(db_session)
    product = service.get_by_id(sample_product.id)

    assert product is not None
    assert product.id == sample_product.id
    assert product.sku == sample_product.sku
```

#### Integration Tests

```python
# tests/integration/test_product_api.py
def test_create_product_endpoint(client, auth_headers):
    """Test product creation via API"""
    response = client.post(
        "/api/products",
        json={
            "name": "Test Product",
            "sku": "TEST-001",
            "unit_price": 99.99
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Product"
```

#### E2E Tests

```python
# tests/e2e/test_order_flow.py
def test_complete_order_flow(api_client, seed_data):
    """Test full order creation and fulfillment"""
    # 1. Login
    auth_response = api_client.post("/api/auth/login", ...)
    token = auth_response.json()["access_token"]

    # 2. Create order
    order_response = api_client.post("/api/sales/orders", ...)
    order_id = order_response.json()["id"]

    # 3. Process payment
    payment_response = api_client.post(f"/api/payments/{order_id}", ...)

    # 4. Verify inventory updated
    inventory_response = api_client.get("/api/inventory", ...)
    assert inventory_response.json()["available_stock"] < seed_data["initial_stock"]
```

### Code Quality

#### Linting Rules

```bash
# Run linters locally before committing
ruff check .                    # Fast linter
black --check .                 # Code formatting
isort --check-only .            # Import sorting
bandit -r app/                  # Security linting
```

#### Pre-Commit Hooks

Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Run code quality checks before commit

echo "Running code quality checks..."

# Linting
ruff check . || exit 1
black --check . || exit 1
isort --check-only . || exit 1

# Unit tests
pytest tests/unit -x || exit 1

echo "All checks passed!"
```

### Docker Best Practices

#### Optimize Build Time

```dockerfile
# Use layer caching effectively
FROM python:3.11-slim

# Install system dependencies first (rarely changes)
RUN apt-get update && apt-get install -y ...

# Copy requirements before code (changes less frequently)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code last
COPY ./app ./app
```

#### Multi-Stage Builds

```dockerfile
# Builder stage
FROM python:3.11 as builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
COPY ./app ./app
CMD ["uvicorn", "app.main:app"]
```

### Security Best Practices

#### Secret Management

```bash
# NEVER commit secrets
git secrets --install            # Install git-secrets
git secrets --register-aws       # Add AWS patterns

# Use GitHub secrets
gh secret set SECRET_NAME -b "value"

# Rotate secrets regularly
gh secret set SECRET_NAME -b "new-value"
```

#### Dependency Updates

```bash
# Review Dependabot PRs weekly
gh pr list --label dependencies

# Check for security advisories
gh api repos/:owner/:repo/vulnerability-alerts

# Update critical dependencies immediately
pip install --upgrade package-name
```

### Performance Optimization

#### Test Performance

```bash
# Run performance tests before major releases
gh workflow run performance-test.yml \
  -f target_url=https://staging.erp.tsh.sale \
  -f users=200 \
  -f run_time=10m

# Review results
gh run view --log
```

#### Database Optimization

```bash
# Check for N+1 queries
pytest tests/ --profile

# Run migrations on staging first
gh workflow run deploy-staging.yml

# Monitor query performance
python scripts/analyze_slow_queries.py
```

## Troubleshooting

### Common Issues

#### 1. CI Pipeline Failing on Tests

**Symptoms**: Tests pass locally but fail in CI

**Causes**:
- Missing environment variables
- Database state issues
- Timing/race conditions

**Solutions**:
```bash
# Check CI logs
gh run view --log

# Run tests with same conditions as CI
docker-compose -f docker-compose.test.yml up -d
pytest tests/ -v

# Reset test database
docker-compose down -v
docker-compose up -d
```

#### 2. Docker Build Failing

**Symptoms**: "failed to solve with frontend dockerfile.v0"

**Causes**:
- Missing files in build context
- Network issues pulling base images
- Build cache corruption

**Solutions**:
```bash
# Build locally to reproduce
docker build -t test-build .

# Clear build cache
docker builder prune -a

# Use no-cache build
docker build --no-cache -t test-build .
```

#### 3. Deployment Rollback

**Symptoms**: Smoke tests failing after deployment

**Causes**:
- Database migration issues
- Missing environment variables
- Service configuration errors

**Actions**:
- Rollback triggers automatically
- Check rollback logs:
```bash
gh run view --log
```

- Manual rollback if needed:
```bash
ssh root@167.71.39.50
cd /opt/tsh-erp
git checkout previous-version
docker-compose restart
```

#### 4. Schema Drift Detected

**Symptoms**: Schema drift workflow reports CRITICAL drift

**Causes**:
- Missing Alembic migrations
- Manual database changes
- Out-of-sync ORM models

**Solutions**:
```bash
# Generate migration
alembic revision --autogenerate -m "Fix schema drift"

# Review migration
cat alembic/versions/latest_migration.py

# Test on staging
alembic upgrade head

# Commit and deploy
git add alembic/versions/
git commit -m "Add migration for schema drift"
```

#### 5. GHCR Authentication Issues

**Symptoms**: "unauthorized: authentication required"

**Causes**:
- Expired GITHUB_TOKEN
- Missing GHCR permissions
- Wrong registry URL

**Solutions**:
```bash
# Re-authenticate
echo ${{ secrets.GITHUB_TOKEN }} | docker login ghcr.io -u ${{ github.actor }} --password-stdin

# Check token permissions
gh auth status

# Verify registry access
docker pull ghcr.io/qmop1967/tsh-erp/app:latest
```

### Debugging Workflows

#### View Workflow Logs

```bash
# List recent runs
gh run list --workflow=ci.yml --limit 10

# View specific run
gh run view <run-id> --log

# Download logs
gh run download <run-id>
```

#### Re-run Failed Jobs

```bash
# Re-run failed jobs only
gh run rerun <run-id> --failed

# Re-run entire workflow
gh run rerun <run-id>
```

#### Debug Mode

```bash
# Enable debug logging in workflow
gh workflow run ci.yml --ref feature-branch
# Then add to workflow:
env:
  ACTIONS_RUNNER_DEBUG: true
  ACTIONS_STEP_DEBUG: true
```

### Getting Help

#### GitHub Actions Logs

1. Go to Actions tab: https://github.com/Qmop1967/tsh-erp-system/actions
2. Click on failed workflow run
3. Click on failed job
4. Expand failed step
5. Review error messages

#### Database Logs

```bash
# Production database logs
ssh root@167.71.39.50
docker logs postgres-container --tail 100

# Application logs
docker logs tsh-erp-app --tail 100 -f
```

#### Telegram Notifications

All CI/CD events are reported to Telegram:
- Build failures
- Deployment status
- Security alerts
- Weekly reports

Check your configured Telegram chat for real-time updates.

## Monitoring

### GitHub Insights

#### Workflow Usage

```bash
# View workflow runs
gh run list --limit 50

# Workflow statistics
gh api repos/:owner/:repo/actions/workflows/:workflow_id/timing
```

#### Security Alerts

Navigate to: Repository → Security → Code scanning alerts

Review:
- Dependabot alerts (dependencies)
- Code scanning (Trivy, Bandit)
- Secret scanning

### Key Metrics

#### CI/CD Performance

- **Build Time**: Target < 10 minutes
- **Test Coverage**: Target > 80%
- **Deployment Frequency**: 2-3 times per week
- **Change Failure Rate**: Target < 15%
- **Mean Time to Recovery**: Target < 1 hour

#### Workflow Success Rates

```bash
# From weekly DevOps report
- Excellent: > 95% success rate
- Good: 85-95% success rate
- Acceptable: 70-85% success rate
- Needs Improvement: < 70% success rate
```

### Grafana & Prometheus (Planned)

Phase 5.4 will add:
- Real-time metrics dashboard
- Alert rules for:
  - Build failures
  - Deployment issues
  - Performance degradation
  - Security vulnerabilities
- Historical trend analysis

## Additional Resources

### Documentation

- [GitHub Secrets Setup](github-secrets-setup.md)
- [Workflow Reference](workflows/)
- [Test Data Guide](../testing/test-data-guide.md)
- [Deployment Guide](deployment-guide.md)

### External Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest Documentation](https://docs.pytest.org/)
- [Locust Documentation](https://docs.locust.io/)

### Support Channels

- **GitHub Discussions**: For questions and community support
- **GitHub Issues**: For bug reports and feature requests
- **Telegram**: Real-time notifications and alerts
- **Email**: Weekly DevOps reports

---

**Last Updated**: 2025-01-11
**Maintained by**: TSH DevOps Team
**Version**: 1.0.0
