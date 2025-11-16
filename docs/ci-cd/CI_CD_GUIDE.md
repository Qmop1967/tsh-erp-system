# CI/CD Guide

**Complete Continuous Integration & Deployment Guide for TSH ERP**
Last Updated: November 13, 2025

---

## Table of Contents
1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [GitHub Actions Setup](#github-actions-setup)
4. [Workflow Reference](#workflow-reference)
5. [Security & Secrets](#security--secrets)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Overview

### What is TSH ERP CI/CD?

The TSH ERP CI/CD system provides automated testing, building, and deployment using GitHub Actions. Every code change is automatically:
- ✅ Tested
- ✅ Built
- ✅ Security scanned
- ✅ Deployed to staging (develop branch)
- ✅ Deployed to production (main branch, after PR approval)

### CI/CD Architecture

```
Developer
    ↓ (git push)
GitHub Repository
    ↓ (triggers)
┌──────────────────────────────────────┐
│      GitHub Actions Workflows        │
├──────────────────────────────────────┤
│  1. Code Quality Checks              │
│     • Linting (Ruff, ESLint)         │
│     • Type checking (mypy, TSC)      │
│     • Code formatting (Black, Prettier)│
│                                      │
│  2. Security Scanning                │
│     • Dependency vulnerabilities     │
│     • Secret detection               │
│     • License compliance             │
│                                      │
│  3. Automated Testing                │
│     • Unit tests (pytest, Jest)      │
│     • Integration tests              │
│     • E2E tests (Playwright)         │
│                                      │
│  4. Build Artifacts                  │
│     • Docker images                  │
│     • Frontend bundles               │
│     • Flutter web apps               │
│                                      │
│  5. Deploy to Environment            │
│     • develop → Staging (auto)       │
│     • main → Production (after PR)   │
└──────────────────────────────────────┘
    ↓
Target Environment (VPS)
```

### Environments

| Branch | Environment | Auto-Deploy | URL |
|--------|-------------|-------------|-----|
| **develop** | Staging | ✅ Yes | staging.erp.tsh.sale |
| **main** | Production | ✅ After PR merge | erp.tsh.sale |
| **feature/** | Local | ❌ No | localhost |

---

## Quick Start

### Prerequisites

1. **Repository Access**
   - Write access to TSH ERP repository
   - GitHub account with 2FA enabled

2. **Local Setup**
   - Git configured
   - SSH key added to GitHub
   - Repository cloned locally

### 5-Minute Setup

**Step 1: Configure GitHub Secrets**

Go to: `https://github.com/your-org/tsh-erp/settings/secrets/actions`

Add the following secrets:

```bash
# VPS Access
VPS_HOST=167.71.39.50
VPS_SSH_KEY=<your-private-key>
VPS_USER=root

# Database
POSTGRES_PASSWORD=<secure-password>
DATABASE_URL=postgresql://user:pass@host:5432/db

# Application
JWT_SECRET=<random-secret>
SECRET_KEY=<random-secret>

# Zoho Integration
ZOHO_CLIENT_ID=<zoho-client-id>
ZOHO_CLIENT_SECRET=<zoho-client-secret>
ZOHO_REFRESH_TOKEN=<zoho-refresh-token>
ZOHO_ORGANIZATION_ID=748369814

# Supabase (if used)
SUPABASE_URL=<supabase-url>
SUPABASE_KEY=<supabase-anon-key>
```

**Step 2: Test Workflow**

```bash
# Create a test branch
git checkout -b feature/test-ci

# Make a small change
echo "# Test" >> README.md

# Commit and push
git add .
git commit -m "test: CI/CD setup"
git push origin feature/test-ci

# Watch the workflow
gh run watch
```

**Step 3: Deploy to Staging**

```bash
# Merge to develop
git checkout develop
git merge feature/test-ci
git push origin develop

# Monitor deployment
gh run watch

# Verify staging
curl https://staging.erp.tsh.sale/health
```

**Step 4: Deploy to Production**

```bash
# Create PR
gh pr create --base main --head develop \
  --title "Deploy to production" \
  --body "Description of changes"

# After review, merge
gh pr merge <pr-number>

# Monitor production deployment
gh run watch

# Verify production
curl https://erp.tsh.sale/health
```

---

## GitHub Actions Setup

### Workflow Files

TSH ERP uses these GitHub Actions workflows:

```
.github/workflows/
├── test.yml                    # Run tests on PR
├── lint.yml                    # Code quality checks
├── security-scan.yml           # Security scanning
├── deploy-staging.yml          # Deploy to staging (develop)
├── deploy-production.yml       # Deploy to production (main)
├── build-mobile.yml            # Build Flutter apps
└── dependabot-auto-merge.yml   # Auto-merge dependency updates
```

### Key Workflows

#### 1. Test Workflow (`test.yml`)

**Triggers:** Pull requests, pushes to develop/main

```yaml
name: Test
on:
  pull_request:
  push:
    branches: [develop, main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: pytest tests/

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install
      - run: npm test
```

#### 2. Deploy to Staging (`deploy-staging.yml`)

**Triggers:** Push to develop branch

```yaml
name: Deploy to Staging
on:
  push:
    branches: [develop]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      # Build Docker images
      - name: Build
        run: docker-compose build

      # Deploy to staging server
      - name: Deploy
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd /var/www/tsh-erp-staging
            git pull origin develop
            docker-compose up -d --build

      # Health check
      - name: Verify deployment
        run: |
          curl -f https://staging.erp.tsh.sale/health || exit 1
```

#### 3. Deploy to Production (`deploy-production.yml`)

**Triggers:** Push to main branch (via PR merge)

```yaml
name: Deploy to Production
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production  # Requires manual approval
    steps:
      - uses: actions/checkout@v3

      # All tests must pass
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest tests/

      # Blue-green deployment
      - name: Deploy
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd /var/www/tsh-erp
            ./scripts/blue-green-deploy.sh

      # Smoke tests
      - name: Post-deployment tests
        run: |
          curl -f https://erp.tsh.sale/health || exit 1
          # Additional smoke tests...
```

---

## Workflow Reference

### Common Commands

```bash
# List recent runs
gh run list

# Watch specific run
gh run watch <run-id>

# View run logs
gh run view <run-id> --log

# Re-run failed jobs
gh run rerun <run-id>

# Cancel running workflow
gh run cancel <run-id>

# List workflows
gh workflow list

# Manually trigger workflow
gh workflow run deploy-staging.yml
```

### Workflow Status

Check workflow status:
```bash
# Via CLI
gh run list --workflow=deploy-production.yml

# Via API
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/your-org/tsh-erp/actions/runs
```

### Debugging Failed Workflows

**1. Check logs:**
```bash
gh run view <run-id> --log-failed
```

**2. Common failure reasons:**
- Secret not configured
- Test failures
- Deployment script errors
- Network connectivity issues

**3. Re-run with debug logging:**
```yaml
# Add to workflow
env:
  ACTIONS_STEP_DEBUG: true
  ACTIONS_RUNNER_DEBUG: true
```

---

## Security & Secrets

### Managing Secrets

**Add Secret:**
```bash
gh secret set SECRET_NAME
# Paste secret value when prompted
```

**List Secrets:**
```bash
gh secret list
```

**Delete Secret:**
```bash
gh secret delete SECRET_NAME
```

### Secret Best Practices

1. ✅ **Never commit secrets to code**
2. ✅ **Rotate secrets regularly** (quarterly)
3. ✅ **Use environment-specific secrets**
4. ✅ **Limit secret access** (use environments)
5. ✅ **Audit secret usage**

### Required Secrets

See [github-secrets-setup.md](./github-secrets-setup.md) for the complete list.

**Critical Secrets:**
- `VPS_SSH_KEY` - SSH private key for deployment
- `POSTGRES_PASSWORD` - Database password
- `JWT_SECRET` - JWT signing secret
- `ZOHO_CLIENT_SECRET` - Zoho OAuth secret

### Security Scanning

Automatic security scans on every PR:

**1. Dependency Scanning:**
```yaml
# .github/workflows/security-scan.yml
- name: Dependency Check
  uses: pyupio/safety@v1
  with:
    api-key: ${{ secrets.SAFETY_API_KEY }}
```

**2. Secret Scanning:**
```yaml
- name: TruffleHog Scan
  uses: trufflesecurity/trufflehog@main
```

**3. Container Scanning:**
```yaml
- name: Trivy Scan
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ghcr.io/your-org/tsh-erp:latest
```

See [security-scanning.md](./security-scanning.md) for details.

---

## Best Practices

### 1. Branch Strategy

```
main (production)
  ← PR ← develop (staging)
           ← feature/new-feature
           ← bugfix/fix-something
           ← hotfix/critical-fix
```

**Rules:**
- ✅ Feature branches from `develop`
- ✅ Hotfix branches from `main`
- ✅ Always PR to develop first
- ✅ Test on staging before production
- ❌ Never push directly to `main`

### 2. Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
feat: add new customer dashboard
fix: resolve invoice calculation bug
docs: update deployment guide
chore: upgrade dependencies
test: add integration tests for orders
```

### 3. Pull Requests

**PR Checklist:**
- [ ] Tests passing
- [ ] No security warnings
- [ ] Documentation updated
- [ ] Tested on staging
- [ ] Reviewed by teammate
- [ ] No merge conflicts

**PR Template:**
```markdown
## Changes
<!-- Describe what changed -->

## Testing
<!-- How was this tested -->

## Checklist
- [ ] Tests pass
- [ ] Staging verified
- [ ] Docs updated
```

### 4. Testing Strategy

```
┌─────────────────────────────────┐
│   Unit Tests (70%)              │
│   • Fast feedback               │
│   • Run on every commit         │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│   Integration Tests (20%)       │
│   • API endpoint tests          │
│   • Database integration        │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│   E2E Tests (10%)               │
│   • Critical user flows         │
│   • Run before production       │
└─────────────────────────────────┘
```

### 5. Deployment Windows

**Staging:** Anytime (automated)

**Production:**
- Preferred: Tuesday-Thursday, 10 AM - 4 PM
- Avoid: Fridays, weekends, holidays
- Emergency: Anytime with approval

### 6. Rollback Strategy

**Automated Rollback:**
```yaml
# If health check fails, rollback
- name: Health Check
  run: |
    if ! curl -f https://erp.tsh.sale/health; then
      ./scripts/rollback.sh
      exit 1
    fi
```

**Manual Rollback:**
```bash
# Revert to previous commit
git revert HEAD
git push origin main

# Or use blue-green switch
ssh user@vps "./scripts/switch-to-blue.sh"
```

---

## Troubleshooting

### Common Issues

#### 1. Deployment Fails with SSH Error

**Symptom:**
```
Permission denied (publickey)
```

**Solution:**
```bash
# Verify SSH key is correct
gh secret list | grep SSH

# Test SSH connection
ssh -i ~/.ssh/deploy_key user@vps

# Re-add SSH key if needed
gh secret set VPS_SSH_KEY < ~/.ssh/deploy_key
```

#### 2. Tests Pass Locally, Fail in CI

**Symptom:**
```
Tests fail in GitHub Actions but pass locally
```

**Solution:**
```bash
# Check Python version matches
python --version  # Should match CI version

# Check environment variables
# CI may be missing .env vars

# Run tests in Docker (matches CI)
docker-compose run api pytest
```

#### 3. Docker Build Fails

**Symptom:**
```
Error building Docker image
```

**Solution:**
```bash
# Check Dockerfile syntax
docker build -t test .

# Clear build cache
docker builder prune

# Check disk space on runner
# May need to clean up old images
```

#### 4. Deployment Timeout

**Symptom:**
```
Deployment times out after 10 minutes
```

**Solution:**
```yaml
# Increase timeout in workflow
timeout-minutes: 30

# Or optimize deployment
# - Use Docker layer caching
# - Parallelize steps
# - Reduce image size
```

### Debug Mode

Enable debug logging in workflow:

```yaml
env:
  ACTIONS_STEP_DEBUG: true
  ACTIONS_RUNNER_DEBUG: true
```

View detailed logs:
```bash
gh run view <run-id> --log
```

---

## Advanced Topics

### Schema Drift Detection

See [schema-drift-detection.md](./schema-drift-detection.md)

Automatic detection of database schema changes:
```yaml
- name: Check Schema Drift
  run: |
    alembic check
    # Fails if migrations needed
```

### Dependabot Configuration

See [dependabot-guide.md](./dependabot-guide.md)

Automatic dependency updates:
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
```

### Intelligent CI/CD

See [INTELLIGENT_CICD_SYSTEM.md](./INTELLIGENT_CICD_SYSTEM.md)

- Selective test execution
- Parallel job optimization
- Smart caching
- Predictive failure detection

---

## Metrics & Monitoring

### CI/CD Metrics

Track these metrics:

- **Deployment Frequency:** How often we deploy
- **Lead Time:** Code commit to production
- **MTTR:** Mean time to recover from failure
- **Change Failure Rate:** % of deployments causing issues

### Monitoring Dashboard

View CI/CD health:
```bash
gh api repos/your-org/tsh-erp/actions/runs \
  --jq '.workflow_runs[] | {name: .name, status: .conclusion}'
```

### Alerts

Set up notifications:
1. GitHub → Settings → Notifications → Actions
2. Enable email/Slack for failed workflows
3. Configure PagerDuty for production failures

---

## Related Documentation

- **Deployment Guide:** [DEPLOYMENT_GUIDE.md](../../.claude/DEPLOYMENT_GUIDE.md)
- **Security Guide:** [SECURITY_IMPLEMENTATION_GUIDE.md](../security/SECURITY_IMPLEMENTATION_GUIDE.md)
- **Docker Guide:** [DOCKER_DEPLOYMENT_GUIDE.md](../../.claude/DOCKER_DEPLOYMENT_GUIDE.md)

---

## Appendix

### GitHub Actions Cheat Sheet

```bash
# Workflows
gh workflow list                    # List all workflows
gh workflow run <workflow>          # Trigger workflow
gh workflow view <workflow>         # View workflow details

# Runs
gh run list                         # List recent runs
gh run watch                        # Watch latest run
gh run view <run-id>               # View run details
gh run rerun <run-id>              # Re-run workflow
gh run cancel <run-id>             # Cancel workflow

# Secrets
gh secret list                      # List secrets
gh secret set <name>               # Set secret
gh secret delete <name>            # Delete secret
```

### Useful Links

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [GitHub CLI Docs](https://cli.github.com/manual/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**Status:** ✅ Active
**Last Updated:** November 13, 2025
**Maintainer:** DevOps Team
**Next Review:** February 2026
