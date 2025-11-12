# GitHub Workflows Reference Guide

Quick reference for all GitHub Actions workflows in the TSH ERP Ecosystem.

## Workflow Summary Table

| Workflow | File | Trigger | Duration | Purpose |
|----------|------|---------|----------|---------|
| Main CI | `ci.yml` | Push, PR | 8-12 min | Code quality, tests, build |
| Docker Build | `docker-build.yml` | workflow_call | 5-8 min | Reusable Docker builder |
| Security Scan | `security-scan.yml` | Daily, manual | 10-15 min | Vulnerability scanning |
| Schema Drift | `schema-drift-check.yml` | Daily, manual | 2-3 min | Database schema validation |
| E2E Tests | `e2e-tests.yml` | Manual, daily | 15-20 min | End-to-end testing |
| Deploy Production | `deploy-production.yml` | Manual only | 15-20 min | Production deployment |
| Next.js CI | `nextjs-ci.yml` | Push, PR | 8-10 min | Frontend pipeline |
| Flutter CI | `flutter-ci.yml` | Push, PR | 20-30 min | Mobile app builds |
| Performance Test | `performance-test.yml` | Weekly, manual | 5-10 min | Load testing |
| GHCR Cleanup | `cleanup-ghcr.yml` | Weekly | 3-5 min | Registry maintenance |
| DevOps Report | `weekly-devops-report.yml` | Weekly | 3-5 min | Metrics reporting |
| Validate Secrets | `validate-secrets.yml` | workflow_call | 1-2 min | Secret validation |
| Notify | `notify.yml` | workflow_call | < 1 min | Notification system |
| Dependabot Auto-Merge | `dependabot-auto-merge.yml` | PR event | 2-3 min | Auto-merge safe updates |

## Detailed Workflow Reference

### 1. Main CI Pipeline (`ci.yml`)

#### Trigger Events
```yaml
on:
  push:
    branches: [main, develop, staging]
  pull_request:
    branches: [main, develop]
  workflow_dispatch:
```

#### Jobs

##### `validate-secrets`
- **Purpose**: Ensure all required secrets are configured
- **Duration**: 1-2 min
- **Failures**: Missing critical secrets

##### `code-quality`
- **Purpose**: Lint and format checking
- **Tools**: ruff, black, isort, bandit
- **Duration**: 2-3 min
- **Failures**: Linting errors, security issues

##### `unit-tests`
- **Purpose**: Run isolated unit tests
- **Coverage**: Target 80%+
- **Duration**: 3-5 min
- **Failures**: Test failures, low coverage

##### `integration-tests`
- **Purpose**: Test with real database and cache
- **Services**: PostgreSQL 15, Redis 7
- **Duration**: 5-7 min
- **Failures**: Service connection, test failures

##### `service-validation`
- **Purpose**: Validate service dependencies
- **Checks**: env vars, dependencies, network, health, API
- **Duration**: 2-3 min
- **Failures**: Service misconfiguration

##### `build-and-push`
- **Purpose**: Build Docker images and push to GHCR
- **Services**: app, neurolink, tds-admin
- **Duration**: 10-15 min
- **Failures**: Build errors, registry issues

##### `notify`
- **Purpose**: Send success/failure notifications
- **Channels**: Telegram, Email
- **Duration**: < 1 min

#### Environment Variables
```yaml
env:
  PYTHON_VERSION: '3.11'
  POETRY_VERSION: '1.7.0'
  DOCKER_BUILDKIT: 1
```

#### Secrets Required
- `GITHUB_TOKEN` (automatic)
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

#### Manual Trigger
```bash
gh workflow run ci.yml
gh workflow run ci.yml --ref feature-branch
```

---

### 2. Docker Build (`docker-build.yml`)

#### Usage
```yaml
jobs:
  build-app:
    uses: ./.github/workflows/docker-build.yml
    with:
      service_name: app
      dockerfile_path: ./Dockerfile
      build_context: .
      push_to_registry: true
    secrets: inherit
```

#### Inputs
- `service_name` (required): Service name (app, neurolink, tds-admin)
- `dockerfile_path` (optional): Path to Dockerfile (default: `./Dockerfile`)
- `build_context` (optional): Build context path (default: `.`)
- `push_to_registry` (optional): Push to GHCR (default: `true`)
- `build_args` (optional): Additional build arguments

#### Outputs
- `image_tag`: Full image tag (e.g., `ghcr.io/qmop1967/tsh-erp/app:v1.2.3`)
- `image_digest`: SHA256 digest of built image

#### Features
- Semantic versioning from git tags
- Layer caching with GitHub Actions cache
- Multi-platform support (planned)
- Automatic tagging (commit SHA, branch, latest)

---

### 3. Security Scan (`security-scan.yml`)

#### Trigger Events
```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_dispatch:
    inputs:
      scan_type: [all, docker, filesystem, dependencies]
      fail_on_severity: [LOW, MEDIUM, HIGH, CRITICAL]
  workflow_call:
```

#### Scan Types

##### Docker Image Scanning
```bash
trivy image tsh-erp-app:latest \
  --severity MEDIUM,HIGH,CRITICAL \
  --format sarif \
  --output docker-scan.sarif
```

##### Filesystem Scanning
```bash
trivy fs . \
  --skip-dirs node_modules,.git \
  --severity HIGH,CRITICAL
```

##### Python Dependencies
```bash
safety check --json
bandit -r app/ -f json
```

#### SARIF Upload
Results are uploaded to GitHub Security tab for tracking.

#### Manual Trigger
```bash
# Scan everything
gh workflow run security-scan.yml -f scan_type=all

# Scan Docker images only
gh workflow run security-scan.yml \
  -f scan_type=docker \
  -f fail_on_severity=CRITICAL
```

---

### 4. Schema Drift Check (`schema-drift-check.yml`)

#### Trigger Events
```yaml
on:
  schedule:
    - cron: '0 1 * * *'  # Daily at 1 AM UTC
  workflow_dispatch:
    inputs:
      environment: [staging, production]
      fail_on_drift: [true, false]
  workflow_call:
```

#### Comparison Process
1. Connect to remote database (staging/production)
2. Create local database from SQLAlchemy models
3. Compare schemas using `migra`
4. Classify drift severity
5. Generate migration suggestions
6. Notify on CRITICAL drift

#### Severity Classification
```python
CRITICAL_PATTERNS = [
    r'DROP TABLE',
    r'DROP COLUMN',
    r'ALTER COLUMN.*DROP'
]

MAJOR_PATTERNS = [
    r'ALTER TABLE',
    r'ADD CONSTRAINT',
    r'CREATE TABLE',
    r'ADD COLUMN'
]
```

#### Manual Trigger
```bash
# Check production (fail on drift)
gh workflow run schema-drift-check.yml \
  -f environment=production \
  -f fail_on_drift=true

# Check staging (warning only)
gh workflow run schema-drift-check.yml \
  -f environment=staging \
  -f fail_on_drift=false
```

---

### 5. E2E Tests (`e2e-tests.yml`)

#### Test Categories

##### Authentication Tests
- User login/logout
- Token refresh
- Permission validation
- Session management

##### API Tests
- CRUD operations
- Validation rules
- Error handling
- Rate limiting

##### Business Logic Tests
- Order processing
- Inventory management
- Payment processing
- Report generation

#### Service Containers
```yaml
services:
  postgres:
    image: postgres:15-alpine
    env:
      POSTGRES_PASSWORD: testpass
    options: >-
      --health-cmd pg_isready
      --health-interval 10s

  redis:
    image: redis:7-alpine
    options: >-
      --health-cmd "redis-cli ping"
      --health-interval 10s
```

#### Manual Trigger
```bash
# Run all E2E tests
gh workflow run e2e-tests.yml

# Run specific test type
gh workflow run e2e-tests.yml -f test_type=api
```

---

### 6. Production Deployment (`deploy-production.yml`)

#### Deployment Flow
```
Pre-Checks → Backup DB → Deploy → Smoke Tests → [Success/Rollback]
```

#### Pre-Deployment Checks
1. Secret validation (deployment scope)
2. Schema drift check (fail on critical)
3. Security scan (fail on critical vulnerabilities)

#### Backup Process
1. Create timestamped PostgreSQL dump
2. Compress with gzip
3. Store locally (/backups/database)
4. Upload to S3 (if configured)
5. Cleanup old backups (> 30 days)

#### Deployment Steps
1. SSH to production server
2. Save current version for rollback
3. Pull latest code
4. Update dependencies
5. Run database migrations
6. Restart services with docker-compose
7. Wait for health checks

#### Smoke Tests
```python
tests = [
    ('/health', 200),
    ('/docs', 200),
    ('/openapi.json', 200),
    ('/api/auth/login', [401, 422])  # Should reject invalid credentials
]
```

#### Rollback Triggers
- Smoke test failure
- Health check timeout
- Service startup failure

#### Manual Trigger
```bash
# Deploy latest main
gh workflow run deploy-production.yml

# Deploy specific version
gh workflow run deploy-production.yml -f version=v1.2.3

# Skip tests (not recommended)
gh workflow run deploy-production.yml \
  -f skip_tests=true \
  -f skip_backup=true
```

#### Monitoring Deployment
```bash
# Watch real-time logs
gh run watch

# Check specific run
gh run view <run-id> --log
```

---

### 7. Next.js CI (`nextjs-ci.yml`)

#### Jobs

##### Setup
- Install pnpm
- Cache pnpm store
- Install dependencies

##### Lint
- ESLint checks
- Prettier formatting
- TypeScript errors

##### Type Check
- Run `tsc --noEmit`
- Validate type definitions

##### Test
- Jest unit tests
- Coverage reporting
- Component tests

##### Build
- Production build
- Environment variables
- Static optimization

##### Bundle Analysis
- Analyze bundle size
- Track largest files
- Size threshold alerts (> 5MB)

#### Configuration
```yaml
env:
  NODE_VERSION: '20'
  PNPM_VERSION: '8'

inputs:
  working_directory:
    default: './tds-admin-dashboard'
```

---

### 8. Flutter CI (`flutter-ci.yml`)

#### Dynamic App Discovery
```python
# Finds all apps with pubspec.yaml
mobile_apps_dir = Path('mobile_apps')
apps = [app.name for app in mobile_apps_dir.iterdir()
        if (app / 'pubspec.yaml').exists()]
```

#### Matrix Strategy
```yaml
strategy:
  matrix:
    app: [tsh_sales, tsh_inventory, tsh_warehouse, ...]
```

#### Jobs

##### Discover Apps
- Scans mobile_apps/ directory
- Creates build matrix
- Filters by input (if specified)

##### Analyze
- flutter doctor
- flutter pub get
- flutter analyze
- dart format check

##### Test
- flutter test --coverage
- Upload coverage reports

##### Build Android
- Setup Java 17 + Gradle cache
- flutter build apk --release
- Split APKs per ABI
- Analyze APK sizes

##### Build iOS (Disabled)
- Requires macOS runner ($$$)
- Enable by removing `false &&` condition

#### Manual Trigger
```bash
# Build all apps for Android
gh workflow run flutter-ci.yml

# Build specific app
gh workflow run flutter-ci.yml \
  -f app_name=tsh_sales \
  -f build_platform=android

# Build for iOS (expensive!)
gh workflow run flutter-ci.yml \
  -f app_name=tsh_inventory \
  -f build_platform=ios
```

---

### 9. Performance Testing (`performance-test.yml`)

#### Locust Configuration
```yaml
inputs:
  target_url: URL to test
  users: Concurrent users (default: 100)
  spawn_rate: Users/second (default: 10)
  run_time: Duration (default: '5m')
  test_scenario: [all, api_basic, api_heavy, web_browsing]
```

#### Test Scenarios

##### API Basic (Lightweight)
- View products list
- View customers
- Search products
- View product details
- Health checks

##### API Heavy (Complex)
- Generate sales reports
- Create sales orders
- Inventory valuation
- Dashboard statistics

##### Web Browsing
- Homepage
- API docs
- OpenAPI spec
- Health checks

#### Results Analysis
```python
# Metrics collected
- Total requests
- Failed requests
- Success rate (%)
- Average response time (ms)
- P95 response time (ms)
- Requests per second
```

#### Performance Thresholds
- **Excellent**: > 99.5% success rate
- **Good**: > 95% success rate
- **Acceptable**: > 90% success rate
- **Poor**: < 90% success rate

#### Manual Trigger
```bash
# Test staging with 100 users for 5 minutes
gh workflow run performance-test.yml \
  -f target_url=https://staging.erp.tsh.sale \
  -f users=100 \
  -f spawn_rate=10 \
  -f run_time=5m

# Heavy load test (200 users, 10 minutes)
gh workflow run performance-test.yml \
  -f target_url=https://staging.erp.tsh.sale \
  -f users=200 \
  -f run_time=10m \
  -f test_scenario=api_heavy
```

---

### 10. GHCR Cleanup (`cleanup-ghcr.yml`)

#### Retention Policy
- Delete images older than 30 days
- Keep last 10 versions per service
- Protect tagged versions:
  - `latest`
  - `production`
  - `staging`
  - `v*.*.*` (semantic versions)

#### Services Cleaned
- `ghcr.io/qmop1967/tsh-erp/app`
- `ghcr.io/qmop1967/tsh-erp/neurolink`
- `ghcr.io/qmop1967/tsh-erp/tds-admin`

#### Manual Trigger
```bash
# Run cleanup now
gh workflow run cleanup-ghcr.yml

# Dry run (see what would be deleted)
gh workflow run cleanup-ghcr.yml -f dry_run=true
```

---

### 11. Weekly DevOps Report (`weekly-devops-report.yml`)

#### Metrics Collected

##### Git Activity
- Total commits
- Unique contributors
- Files changed
- Lines added/deleted
- Net change

##### Pull Requests
- PRs opened
- PRs merged
- PRs closed (not merged)

##### Issues
- Issues opened
- Issues closed

##### CI/CD Workflows
- Total runs
- Successful runs
- Failed runs
- Success rate (%)

##### Dependencies
- Dependabot PRs opened
- Dependabot PRs merged

#### Report Output
1. **GitHub Issue**: Full Markdown report with tables
2. **Telegram**: Summary notification
3. **Artifact**: JSON metrics file

#### Health Assessment
- **Excellent**: > 95% CI success rate
- **Good**: 85-95% success rate
- **Acceptable**: 70-85% success rate
- **Needs Improvement**: < 70% success rate

#### Manual Trigger
```bash
# Generate report for last 7 days
gh workflow run weekly-devops-report.yml

# Custom date range (30 days)
gh workflow run weekly-devops-report.yml -f days_back=30
```

---

### 12. Validate Secrets (`validate-secrets.yml`)

#### Validation Scopes

##### Deployment Scope
```yaml
required_secrets:
  - PROD_HOST
  - PROD_SSH_KEY
  - PROD_DB_PASSWORD
  - PROD_DB_USER
  - PROD_DB_NAME
```

##### Security Scope
```yaml
required_secrets:
  - AWS_ACCESS_KEY_ID
  - AWS_SECRET_ACCESS_KEY
  - GITHUB_TOKEN
```

##### Integration Scope
```yaml
required_secrets:
  - ZOHO_CLIENT_ID
  - ZOHO_CLIENT_SECRET
  - ZOHO_REFRESH_TOKEN
  - TELEGRAM_BOT_TOKEN
```

#### Usage in Workflows
```yaml
jobs:
  validate:
    uses: ./.github/workflows/validate-secrets.yml
    with:
      environment: production
      check_scope: deployment
    secrets: inherit
```

---

### 13. Notification System (`notify.yml`)

#### Channels

##### Telegram
```yaml
inputs:
  telegram_message: Markdown-formatted message
  telegram_parse_mode: Markdown or HTML
```

##### Email (Planned)
```yaml
inputs:
  email_to: Recipient email
  email_subject: Email subject
  email_body: HTML body
```

#### Usage
```yaml
jobs:
  notify-success:
    needs: build
    if: success()
    uses: ./.github/workflows/notify.yml
    with:
      telegram_message: |
        ✅ Build successful
        Branch: ${{ github.ref_name }}
    secrets: inherit
```

---

### 14. Dependabot Auto-Merge (`dependabot-auto-merge.yml`)

#### Auto-Merge Criteria
1. PR from `dependabot[bot]`
2. CI checks pass
3. One of:
   - Patch version update (1.2.3 → 1.2.4)
   - Development dependency
   - Minor update of dev dependency

#### Process
1. Dependabot creates PR
2. CI runs automatically
3. If CI passes and criteria met:
   - Add `automerge` label
   - Approve PR
   - Enable auto-merge
   - PR merges when ready

#### Manual Override
```bash
# Disable auto-merge for specific PR
gh pr edit <pr-number> --remove-label automerge

# Manually merge
gh pr merge <pr-number> --squash
```

---

## Workflow Dependency Graph

```
deploy-production.yml
  ├── validate-secrets.yml
  ├── schema-drift-check.yml
  └── security-scan.yml

ci.yml
  ├── validate-secrets.yml
  ├── docker-build.yml (× 3 services)
  └── notify.yml

e2e-tests.yml
  └── (standalone)

security-scan.yml
  └── (standalone)

flutter-ci.yml
  └── (standalone, matrix)

nextjs-ci.yml
  └── (standalone)

performance-test.yml
  └── (standalone)
```

## Quick Command Reference

```bash
# List all workflows
gh workflow list

# Run workflow
gh workflow run <workflow-name>

# Run with inputs
gh workflow run <workflow-name> -f key=value

# View workflow
gh workflow view <workflow-name>

# Enable/disable workflow
gh workflow enable <workflow-name>
gh workflow disable <workflow-name>

# List recent runs
gh run list --workflow=<workflow-name> --limit 10

# Watch run in real-time
gh run watch

# View run logs
gh run view <run-id> --log

# Download run artifacts
gh run download <run-id>

# Re-run workflow
gh run rerun <run-id>

# Cancel run
gh run cancel <run-id>
```

---

**Last Updated**: 2025-01-11
**Version**: 1.0.0
