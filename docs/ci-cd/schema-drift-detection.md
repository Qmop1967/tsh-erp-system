# Database Schema Drift Detection

Automated detection of schema differences between SQLAlchemy models and production/staging databases.

## Overview

Schema drift occurs when the database schema diverges from the application's ORM models. This can happen due to:
- Manual database changes not reflected in code
- Migrations not applied to production
- Code changes deployed without running migrations
- Direct SQL modifications to production database

The schema drift detection system helps prevent deployment issues by:
- Comparing SQLAlchemy models with actual database schema
- Detecting missing tables, columns, constraints, and indexes
- Classifying drift severity (critical, major, minor)
- Alerting via Telegram on drift detection
- Generating migration scripts to fix drift

## Architecture

### Components

1. **GitHub Workflow** (`.github/workflows/schema-drift-check.yml`)
   - Runs daily at 2 AM UTC
   - Can be triggered manually or called from other workflows
   - Compares production/staging database with local models
   - Sends notifications on drift detection

2. **Local Script** (`scripts/check_schema_drift.py`)
   - CLI tool for developers
   - Check schema drift locally before pushing
   - Generate Alembic migrations
   - Export drift reports

3. **Migra Tool**
   - PostgreSQL schema comparison tool
   - Generates SQL diff between databases
   - Detects all types of schema changes

## Usage

### GitHub Workflow

#### Manual Trigger
```bash
# Check production database
gh workflow run schema-drift-check.yml -f environment=production -f fail_on_drift=false

# Check staging database
gh workflow run schema-drift-check.yml -f environment=staging -f fail_on_drift=true
```

#### Scheduled Runs
The workflow runs automatically every day at 2 AM UTC to check production database.

#### Pre-Deployment Integration
Call the workflow before deployment:

```yaml
jobs:
  check-drift:
    uses: ./.github/workflows/schema-drift-check.yml
    with:
      environment: production
      fail_on_drift: true
    secrets: inherit

  deploy:
    needs: check-drift
    if: needs.check-drift.outputs.drift_detected == 'false'
    # ... deployment steps
```

### Local Script

#### Basic Usage
```bash
# Check production database
python scripts/check_schema_drift.py --env production

# Check staging database
python scripts/check_schema_drift.py --env staging

# Generate Alembic migration if drift detected
python scripts/check_schema_drift.py --env production --generate-migration

# Export report to JSON
python scripts/check_schema_drift.py --env production --export drift-report.json
```

#### Environment Variables
Set database credentials in your environment:

```bash
# Production
export PROD_DB_HOST=167.71.39.50
export PROD_DB_PORT=5432
export PROD_DB_NAME=tsh_erp_production
export PROD_DB_USER=tsh_app_user
export PROD_DB_PASSWORD=<password>

# Staging
export STAGING_DB_HOST=167.71.58.65
export STAGING_DB_PORT=5432
export STAGING_DB_NAME=tsh_erp_staging
export STAGING_DB_USER=tsh_app_user
export STAGING_DB_PASSWORD=<password>
```

Or use a `.env` file:
```bash
# Load from .env file
source .env.production
python scripts/check_schema_drift.py --env production
```

### Exit Codes
- `0` - No drift or minor drift
- `1` - Major drift detected
- `2` - Critical drift detected

## Drift Severity Classification

### Critical Drift 🔴
**Actions that could cause data loss or application failure:**
- `DROP TABLE` - Removing entire tables
- `DROP COLUMN` - Removing columns
- `ALTER COLUMN ... DROP NOT NULL` - Removing NOT NULL constraints
- `DROP CONSTRAINT ... FOREIGN KEY` - Removing foreign keys

**Required Actions:**
1. Review all DROP operations carefully
2. Create database backup before applying changes
3. Generate and review Alembic migration
4. Test migration on staging environment first
5. Schedule maintenance window for production

### Major Drift 🟠
**Actions that require careful planning:**
- `ALTER TABLE ... ADD COLUMN ... NOT NULL` - Adding required columns
- `ALTER COLUMN ... TYPE` - Changing column types
- `ADD CONSTRAINT ... FOREIGN KEY` - Adding foreign keys
- `DROP INDEX` - Removing indexes
- `ALTER COLUMN ... SET NOT NULL` - Adding NOT NULL constraints

**Required Actions:**
1. Review schema changes
2. Generate Alembic migration
3. Test on staging environment
4. Deploy during low-traffic period

### Minor Drift 🟡
**Actions that are safe but should be tracked:**
- `ALTER TABLE ... ADD COLUMN` - Adding nullable columns
- `CREATE TABLE` - Adding new tables
- `CREATE INDEX` - Adding indexes
- `ALTER TABLE ... DROP CONSTRAINT ... CHECK` - Removing check constraints
- `COMMENT ON` - Updating comments

**Required Actions:**
1. Review changes at convenience
2. Generate migration when ready
3. Can be deployed with next regular release

## Drift Report

The system generates comprehensive drift reports with:

### Summary
- Environment (production/staging)
- Drift detected (yes/no)
- Severity level (none/minor/major/critical)
- Change counts by severity

### SQL Differences
Complete SQL script showing all differences between schemas:
```sql
-- Example drift output
ALTER TABLE "products" ADD COLUMN "new_field" text;
DROP TABLE "old_table";
CREATE INDEX "idx_products_sku" ON "products" ("sku");
```

### Recommendations
Specific actions to take based on drift severity.

### Artifacts
- `schema-diff.sql` - Full SQL diff
- `drift-report.json` - Structured report data
- `drift-summary.md` - Human-readable summary

Artifacts are retained for 90 days in GitHub Actions.

## Notifications

### Telegram Alerts

When drift is detected, a Telegram message is sent with:
- Severity emoji (🔴 Critical, 🟠 Major, 🟡 Minor)
- Environment (production/staging)
- Change breakdown
- Branch and commit information
- Link to full report

**Example:**
```
🔴 Schema Drift Alert - CRITICAL

🗃️ Environment: production
📊 Severity: critical

Changes Detected:
• 🔴 Critical: 2
• 🟠 Major: 1
• 🟡 Minor: 3

🌿 Branch: main
📝 Commit: abc1234

⚠️ Action Required:
Review schema differences and generate migration

🔗 View Full Report
```

### Email Alerts (Optional)
Email notifications can be configured in the workflow.

## Best Practices

### 1. Check Before Deployment
Always check for drift before deploying to production:
```bash
python scripts/check_schema_drift.py --env production
```

### 2. Use Read-Only Database User
Create a dedicated read-only user for schema checks:
```sql
CREATE USER schema_checker WITH PASSWORD '<secure-password>';
GRANT CONNECT ON DATABASE tsh_erp_production TO schema_checker;
GRANT SELECT ON information_schema.tables TO schema_checker;
GRANT SELECT ON information_schema.columns TO schema_checker;
```

### 3. Review Drift Reports Regularly
- Check daily scheduled drift reports
- Address critical drift immediately
- Plan major drift fixes during maintenance windows
- Track minor drift for next release

### 4. Maintain Migration History
- Never modify production database manually
- Always use Alembic migrations
- Test migrations on staging first
- Keep migration files in version control

### 5. Monitor Drift Trends
- Track drift reports over time
- Identify patterns of drift
- Improve deployment processes to prevent drift

## Troubleshooting

### Connection Refused
**Problem:** Cannot connect to remote database
```
❌ Failed to connect to production database
Error: connection refused
```

**Solutions:**
1. Check firewall rules allow GitHub Actions IPs
2. Verify database credentials in GitHub Secrets
3. Ensure database is running and accessible
4. Check SSH tunnel if using one

### migra Not Found
**Problem:** `migra` command not found
```
❌ migra command not found
```

**Solution:**
```bash
pip install migra==3.0.1663481299
```

### Timeout During Comparison
**Problem:** Schema comparison times out
```
❌ migra command timed out
```

**Solutions:**
1. Increase timeout in workflow (default: 30s)
2. Check database performance
3. Optimize complex queries in schema
4. Consider running during off-peak hours

### False Positives
**Problem:** Drift detected but schemas appear identical

**Solutions:**
1. Check for timezone differences in columns
2. Review sequence values (auto-increment)
3. Verify enum types match exactly
4. Check collation and character sets

### Permission Denied
**Problem:** Cannot access schema metadata
```
❌ permission denied for table information_schema.columns
```

**Solution:**
Grant schema metadata access:
```sql
GRANT SELECT ON information_schema.tables TO schema_checker;
GRANT SELECT ON information_schema.columns TO schema_checker;
```

## Integration Examples

### Pre-Deployment Check
```yaml
name: Deploy to Production

on:
  workflow_dispatch:

jobs:
  drift-check:
    name: Check Schema Drift
    uses: ./.github/workflows/schema-drift-check.yml
    with:
      environment: production
      fail_on_drift: true
    secrets: inherit

  deploy:
    name: Deploy Application
    needs: drift-check
    if: needs.drift-check.outputs.drift_detected == 'false'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        run: |
          echo "Deploying to production..."
```

### CI Pipeline Integration
```yaml
name: CI Pipeline

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Run tests
        run: pytest

  drift-check:
    needs: test
    uses: ./.github/workflows/schema-drift-check.yml
    with:
      environment: staging
      fail_on_drift: false  # Don't block CI
    secrets: inherit
```

### Local Pre-Commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check for schema drift before committing model changes
if git diff --cached --name-only | grep -q "app/models/"; then
    echo "Model changes detected, checking schema drift..."
    python scripts/check_schema_drift.py --env staging

    if [ $? -eq 2 ]; then
        echo "❌ Critical schema drift detected!"
        echo "Fix drift before committing model changes"
        exit 1
    fi
fi
```

## Related Documentation

- [GitHub Secrets Setup](./github-secrets-setup.md)
- [Alembic Migration Guide](../database/migrations.md)
- [Deployment Workflows](./deployment-workflows.md)
- [CI/CD Pipeline Overview](./README.md)

---

**Version:** 1.0.0
**Last Updated:** 2025-01-11
**Maintained by:** TSH DevOps Team
