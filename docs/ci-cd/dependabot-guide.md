# Dependabot Automated Dependency Updates

Automated dependency management with Dependabot for Python, Docker, GitHub Actions, npm, and Flutter.

## Overview

Dependabot automatically:
- Monitors dependencies for new versions
- Creates pull requests for updates
- Groups related updates together
- Prioritizes security updates
- Auto-merges safe updates after CI passes

## Supported Ecosystems

### 1. Python (pip) - Backend Dependencies
**Schedule:** Every Monday at 8:00 AM AST
**Location:** `/requirements.txt`
**Auto-merge:** Patch updates only

**Grouping:**
- Minor and patch updates grouped together
- Major updates as separate PRs

### 2. Docker - Container Base Images
**Schedule:** Every Tuesday at 8:00 AM AST
**Locations:** `/Dockerfile`, `/app/neurolink/Dockerfile`
**Auto-merge:** Patch updates only

**Monitored images:**
- `python:3.11` base image
- All multi-stage build images
- Service-specific images

### 3. GitHub Actions - Workflow Dependencies
**Schedule:** Every Wednesday at 8:00 AM AST
**Location:** `/.github/workflows/*.yml`
**Auto-merge:** All updates (actions are sandboxed)

**Grouped updates:**
- All GitHub Actions updated together
- Single PR for all action version bumps

### 4. npm - Next.js Frontend
**Schedule:** Every Thursday at 8:00 AM AST
**Location:** `/tds-admin-dashboard/package.json`
**Auto-merge:** Patch dev dependencies only

**Grouping:**
- Production dependencies grouped separately
- Development dependencies (@types/*, eslint, etc.) grouped together

### 5. Flutter - Mobile Apps
**Schedule:** Every Friday at 8:00 AM AST
**Location:** `/mobile_apps/tsh_sales/pubspec.yaml`
**Auto-merge:** Patch updates only

**Grouping:**
- All Flutter packages grouped together
- Uses "widen" strategy for version ranges

## Auto-Merge Rules

Dependabot PRs are automatically merged when:

### ✅ Safe for Auto-Merge

1. **Patch Updates** (`x.x.PATCH`)
   - All package ecosystems
   - Examples: `1.2.3` → `1.2.4`
   - Rationale: Bug fixes only, backward compatible

2. **Minor Dev Dependencies** (`x.MINOR.x`)
   - Development dependencies only
   - Examples: `eslint`, `@types/*`, `pytest`
   - Rationale: No production impact

3. **GitHub Actions** (all updates)
   - Any version bump
   - Rationale: Sandboxed execution, safe

4. **Docker Patches** (`x.x.PATCH`)
   - Base image patch updates
   - Example: `python:3.11.7` → `python:3.11.8`
   - Rationale: Security and bug fixes

### ⚠️ Requires Manual Review

1. **Major Updates** (`MAJOR.x.x`)
   - Breaking changes possible
   - Examples: `2.5.0` → `3.0.0`
   - Review: Check changelog for breaking changes

2. **Minor Production Dependencies** (`x.MINOR.x`)
   - New features, potential issues
   - Examples: Production npm packages
   - Review: Test thoroughly before merging

3. **Docker Minor/Major** (`x.MINOR.x` or `MAJOR.x.x`)
   - Significant base image changes
   - Review: Rebuild and test all services

## Auto-Merge Workflow

### Process Flow

```
Dependabot creates PR
        ↓
Check update type
        ↓
    ┌───────┴──────────┐
    ↓                  ↓
Safe update?      Manual review
    ↓                  ↓
Run CI tests       Add comment
    ↓                  ↓
CI passed?         Wait for human
    ↓
Auto-approve
    ↓
Enable auto-merge
    ↓
Merge when ready
    ↓
Send notification
```

### CI Integration

Auto-merge waits for:
- ✅ Code quality checks
- ✅ Unit tests
- ✅ Integration tests
- ✅ Security scans
- ✅ Docker build tests

Only merges if **all checks pass**.

## Configuration

### Dependabot Config (`.github/dependabot.yml`)

```yaml
version: 2

updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "08:00"
      timezone: "Asia/Riyadh"
    open-pull-requests-limit: 10
    groups:
      minor-and-patch:
        update-types:
          - "minor"
          - "patch"
```

### Update Frequency

| Day | Ecosystem | Time | Limit |
|-----|-----------|------|-------|
| Monday | Python (pip) | 08:00 AST | 10 PRs |
| Tuesday | Docker | 08:00 AST | 5 PRs |
| Wednesday | GitHub Actions | 08:00 AST | 5 PRs |
| Thursday | npm (Next.js) | 08:00 AST | 15 PRs |
| Friday | Flutter (pub) | 08:00 AST | 10 PRs |

### Security Updates

**Always created immediately**, regardless of:
- Schedule
- PR limits
- Grouping rules

Example:
```
🔴 CRITICAL security update for package-name
Created: Immediately
Auto-merge: After CI passes
```

## Managing Dependabot PRs

### View All Dependabot PRs

```bash
# List all open Dependabot PRs
gh pr list --author "dependabot[bot]" --state open

# List by label
gh pr list --label "dependencies"

# View specific ecosystem
gh pr list --label "python"
```

### Manual Merge

```bash
# Review PR
gh pr view <pr-number>

# Check CI status
gh pr checks <pr-number>

# Approve and merge
gh pr review --approve <pr-number>
gh pr merge --squash <pr-number>
```

### Disable for Specific Dependency

Add to `.github/dependabot.yml`:

```yaml
# Ignore specific package
ignore:
  - dependency-name: "package-name"
    versions: ["x.x.x"]

# Ignore all major updates for package
ignore:
  - dependency-name: "package-name"
    update-types: ["version-update:semver-major"]
```

### Close Unwanted PR

```bash
# Close specific Dependabot PR
gh pr close <pr-number> --comment "Not needed"

# Reopen later with comment
@dependabot reopen
```

## Dependabot Commands

Comment on Dependabot PRs to control behavior:

### Rebase PR
```
@dependabot rebase
```
Rebases PR onto latest base branch.

### Recreate PR
```
@dependabot recreate
```
Closes and reopens PR with latest changes.

### Merge PR
```
@dependabot merge
```
Merges PR after CI passes (if you have permissions).

### Squash PR
```
@dependabot squash and merge
```
Squashes commits and merges.

### Ignore Updates
```
@dependabot ignore this major version
@dependabot ignore this minor version
@dependabot ignore this dependency
```

### Set Milestone
```
@dependabot set milestone <milestone-name>
```

## Best Practices

### 1. Review Weekly
- Check Dependabot PRs every week
- Prioritize security updates
- Group-review minor/patch updates

### 2. Test Before Merging
Major/minor updates:
```bash
# Checkout PR locally
gh pr checkout <pr-number>

# Run tests
pytest tests/
npm test

# Test manually in development
```

### 3. Keep CI Green
- Dependabot relies on CI to validate updates
- Fix flaky tests immediately
- Maintain high test coverage

### 4. Monitor After Merge
After auto-merge:
- Check deployment logs
- Monitor error rates
- Watch for regressions

### 5. Update Groups Wisely
Too many dependencies in one group:
- ❌ Hard to debug if something breaks
- ❌ Large PR review burden

Too few dependencies per group:
- ❌ Too many PRs to review
- ❌ Merge conflicts between PRs

Sweet spot: **5-10 related packages per group**

## Troubleshooting

### PR Conflicts

**Problem:** Dependabot PR has merge conflicts

**Solution:**
```bash
@dependabot rebase
```
Dependabot will rebase the PR automatically.

### CI Failures

**Problem:** Dependabot PR fails CI

**Solution:**
1. Review CI logs
2. If legitimate failure, close PR:
   ```
   @dependabot ignore this version
   ```
3. If flaky test, rerun CI:
   ```
   @dependabot recreate
   ```

### Too Many PRs

**Problem:** Dependabot opens 20+ PRs at once

**Solution:**
1. Lower `open-pull-requests-limit` in config
2. Increase grouping:
   ```yaml
   groups:
     all-updates:
       patterns: ["*"]
   ```

### Auto-Merge Not Working

**Problem:** Safe updates not auto-merging

**Check:**
1. CI must pass (all checks)
2. Branch protection rules allow it
3. Check workflow logs:
   ```bash
   gh run list --workflow=dependabot-auto-merge.yml
   ```

### Security Alert Not Fixed

**Problem:** Security alert exists but no Dependabot PR

**Solutions:**
1. Check if fix is available:
   - Repository → Security → Dependabot alerts
2. Manually update if no fix:
   ```bash
   pip install --upgrade <package>
   ```
3. Add to ignore list if false positive

## Integration with CI/CD

### Pre-Deployment Check

```yaml
name: Deploy Production

jobs:
  check-dependencies:
    runs-on: ubuntu-latest
    steps:
      - name: Check for open Dependabot PRs
        run: |
          OPEN_PRS=$(gh pr list --author "dependabot[bot]" --json number | jq length)

          if [ $OPEN_PRS -gt 0 ]; then
            echo "⚠️  Warning: $OPEN_PRS open Dependabot PRs"
            echo "Consider merging updates before deployment"
          fi
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Post-Merge Validation

```yaml
on:
  pull_request:
    types: [closed]

jobs:
  validate:
    if: github.event.pull_request.merged == true && github.actor == 'dependabot[bot]'
    runs-on: ubuntu-latest
    steps:
      - name: Run smoke tests
        run: |
          # Run critical smoke tests
          pytest tests/smoke/
```

## Notifications

### Telegram Notifications

Auto-merged PRs trigger notification:
```
🤖 Dependabot Auto-Merge

📦 Dependency: `fastapi`
🔄 Update: `0.104.0` → `0.104.1`
📊 Type: version-update:semver-patch

✅ Auto-approved and merged after CI passed

🔗 View PR
```

### Email Notifications (GitHub)

Configure in GitHub settings:
- Repository → Settings → Notifications
- Enable "Dependabot alerts"
- Enable "Pull request updates"

## Security Features

### Vulnerability Scanning

Dependabot integrates with:
- GitHub Security Advisories
- CVE database
- npm advisory database
- RubySec advisory database

### Private Dependency Access

For private registries, add secrets:
```yaml
# .github/dependabot.yml
registries:
  npm-private:
    type: npm-registry
    url: https://npm.pkg.github.com
    token: ${{ secrets.NPM_TOKEN }}
```

### Compliance

Dependabot helps with:
- OWASP dependency check compliance
- SOC 2 requirements
- GDPR data protection (updated libraries)
- Audit trail (PR history)

## Metrics and Monitoring

### Track Update Velocity

```bash
# Merged Dependabot PRs in last 30 days
gh pr list \
  --author "dependabot[bot]" \
  --state merged \
  --search "merged:>=$(date -d '30 days ago' +%Y-%m-%d)" \
  --json number \
  | jq length
```

### Security Update Response Time

```bash
# Time from security alert to merge
gh api /repos/Qmop1967/tsh-erp-system/dependabot/alerts \
  | jq '.[] | select(.state == "fixed") | .fixed_at - .created_at'
```

## Related Documentation

- [GitHub Secrets Setup](./github-secrets-setup.md)
- [Security Scanning](./security-scanning.md)
- [CI/CD Pipeline Overview](./README.md)
- [Pull Request Guidelines](../../PULL_REQUEST_TEMPLATE.md)

## Resources

- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)

---

**Version:** 1.0.0
**Last Updated:** 2025-01-11
**Maintained by:** TSH DevOps Team
