# GitHub Workflows - TEMPORARILY DISABLED

**Status:** DISABLED
**Activated:** 2025-11-17
**Reason:** TEMPORARY DEVELOPMENT MODE

---

## Overview

All GitHub Actions workflows in this directory are **TEMPORARILY DISABLED** as part of the TSH ERP Ecosystem's Temporary Development Mode.

---

## What This Means

1. **No automated CI/CD pipelines** will run on push, pull request, or any other trigger
2. **No automatic deployments** to staging or production
3. **No automated testing** via GitHub Actions
4. **No PR-triggered workflows**

---

## Current Deployment Method

During this temporary mode, deployment is done via **Direct Docker Commands** on the development server:

```bash
# SSH to server
ssh root@167.71.39.50

# Deploy all services
cd /var/www/tsh-erp && docker-compose up -d --build
```

Or use the deployment script:
```bash
./scripts/deploy_direct_docker.sh deploy all
```

---

## Why Workflows Are Disabled

- **Fast Development Cycles**: No CI/CD wait times
- **Real Data Testing**: Direct connection to production database (READ-ONLY)
- **Simplified Pipeline**: Direct Docker builds and restarts
- **Safe by Design**: Database is READ-ONLY, all writes happen in Zoho only

---

## Re-enabling Workflows

These workflows will be **RE-ENABLED ONLY** when Khaleel sends an explicit instruction such as:

- "Re-enable GitHub CI/CD workflows"
- "Switch back to standard deployment workflow"
- "Activate production pipelines"

Until such instruction is received, **DO NOT** enable or modify these workflows.

---

## Disabled Workflows

### CI/CD Pipelines (DISABLED)
- `ci.yml` - Main CI pipeline
- `ci-deploy.yml` - CI with deployment
- `ci-test-simple.yml` - Simple CI tests
- `deploy-staging.yml` - Staging deployment
- `deploy-production.yml` - Production deployment

### Build Workflows (DISABLED)
- `docker-build.yml` - Docker image building
- `build-and-push-ghcr.yml` - Build and push to GitHub Container Registry
- `flutter-ci.yml` - Flutter CI
- `nextjs-ci.yml` - Next.js CI

### Testing Workflows (DISABLED)
- `e2e-tests.yml` - End-to-end tests
- `performance-test.yml` - Performance tests
- `zoho-integration-test.yml` - Zoho integration tests

### Security & Validation (DISABLED)
- `security-scan.yml` - Security scanning
- `schema-drift-check.yml` - Database schema validation
- `validate-secrets.yml` - Secrets validation

### Utility Workflows (DISABLED)
- `notify.yml` - Notifications
- `dependabot-auto-merge.yml` - Dependabot auto-merge
- `cleanup-ghcr.yml` - Container registry cleanup

---

## Important Notes

1. **Git operations still work** - You can still push, pull, and create PRs
2. **No workflows trigger** - Pushes and PRs won't trigger any automation
3. **Manual deployment required** - All deployments must be done via Docker commands
4. **Database is READ-ONLY** - Safe for development

---

## Contact

For questions about this temporary mode, contact the project owner (Khaleel).

---

**Last Updated:** 2025-11-17
**Mode Status:** TEMPORARY DEVELOPMENT MODE ACTIVE
**Re-enablement:** Awaiting explicit instruction from Khaleel
