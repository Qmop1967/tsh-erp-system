# Security Scanning with Trivy

Automated vulnerability scanning for Docker images, dependencies, and filesystems using Trivy.

## Overview

The security scanning system provides comprehensive vulnerability detection across:
- **Docker images** - Base images and application containers
- **Python dependencies** - requirements.txt packages
- **Filesystem** - Source code, configuration files, secrets
- **Misconfigurations** - Infrastructure as Code issues

Powered by [Trivy](https://github.com/aquasecurity/trivy), an open-source comprehensive security scanner.

## Features

- Daily automated security scans at 3 AM UTC
- On-demand manual scanning via GitHub UI
- Scan triggered on Dockerfile or requirements.txt changes
- Multiple output formats (Table, JSON, SARIF)
- GitHub Security tab integration via SARIF upload
- Telegram alerts for critical/high vulnerabilities
- Configurable severity thresholds
- 90-day artifact retention for audit trails
- Detailed vulnerability reports with remediation guidance

## Scan Types

### 1. Filesystem Scan
Scans the entire codebase for:
- **Vulnerabilities** in dependencies
- **Secrets** accidentally committed (API keys, passwords, tokens)
- **Misconfigurations** in IaC files (Kubernetes, Docker, Terraform)

**Coverage:**
- All source files
- Configuration files
- Infrastructure as Code
- Excludes: `.git`, `.venv`, `node_modules`, test coverage

### 2. Python Dependencies Scan
Targeted scan of `requirements.txt` for:
- Known CVEs in Python packages
- Outdated packages with security patches
- Dependency chain vulnerabilities

### 3. Docker Image Scan
Scans built Docker images for:
- Base image vulnerabilities (OS packages)
- Application layer vulnerabilities
- Configuration issues
- Exposed secrets

## Severity Levels

| Severity | Description | Action Required |
|----------|-------------|-----------------|
| 🔴 **CRITICAL** | Actively exploited or easily exploitable vulnerabilities | **Immediate** - Patch within 24 hours |
| 🟠 **HIGH** | Serious vulnerabilities requiring prompt attention | **Urgent** - Patch within 7 days |
| 🟡 **MEDIUM** | Moderate risk vulnerabilities | **Scheduled** - Patch within 30 days |
| ⚪ **LOW** | Minor issues or theoretical vulnerabilities | **Optional** - Track and fix when convenient |

## Usage

### Manual Scan via GitHub Actions

1. Go to **Actions** → **Security Scanning**
2. Click **Run workflow**
3. Configure scan parameters:
   - **Scan Type**: `all`, `docker`, or `filesystem`
   - **Minimum Severity**: Report vulnerabilities at this level or higher
   - **Fail On Severity**: Fail the workflow on this severity or higher

**Example configurations:**

```yaml
# Comprehensive scan, fail on HIGH or CRITICAL
Scan Type: all
Minimum Severity: MEDIUM
Fail On Severity: HIGH

# Docker-only scan, fail on CRITICAL only
Scan Type: docker
Minimum Severity: LOW
Fail On Severity: CRITICAL

# Filesystem scan, report everything
Scan Type: filesystem
Minimum Severity: LOW
Fail On Severity: CRITICAL
```

### Integrate into CI Pipeline

Add security scanning to your CI workflow:

```yaml
name: CI with Security Scan

jobs:
  security-scan:
    uses: ./.github/workflows/security-scan.yml
    with:
      scan_type: all
      severity: MEDIUM
      fail_on_severity: HIGH
    secrets: inherit

  deploy:
    needs: security-scan
    if: needs.security-scan.outputs.vulnerabilities_found == 'false'
    # ... deployment steps
```

### Pre-Deployment Validation

```yaml
jobs:
  pre-deploy-checks:
    uses: ./.github/workflows/security-scan.yml
    with:
      scan_type: docker
      severity: LOW  # Report everything
      fail_on_severity: HIGH  # Block on HIGH/CRITICAL
    secrets: inherit

  deploy-production:
    needs: pre-deploy-checks
    # Only deploy if no HIGH/CRITICAL vulnerabilities
```

### Scheduled Scans

The workflow automatically runs daily at 3 AM UTC to catch newly disclosed vulnerabilities.

## Scan Results

### GitHub Security Tab

SARIF results are automatically uploaded to GitHub's Security tab:
1. Go to repository **Security** → **Code scanning alerts**
2. View all detected vulnerabilities
3. Filter by severity, type, or status
4. Track remediation progress

### Artifacts

All scan results are uploaded as artifacts (90-day retention):
- `filesystem-scan.txt` - Human-readable filesystem scan
- `filesystem-scan.json` - Machine-readable filesystem scan
- `filesystem-scan.sarif` - GitHub Security format
- `python-deps-scan.txt` - Python dependencies report
- `python-deps-scan.json` - Python dependencies JSON
- `docker-scan.txt` - Docker image report
- `docker-scan.json` - Docker image JSON
- `docker-scan.sarif` - Docker SARIF format
- `security-scan-summary.json` - Aggregated summary

### Download Artifacts

```bash
# List artifacts for a workflow run
gh run view <run-id> --log

# Download all artifacts
gh run download <run-id>

# Download specific artifact
gh run download <run-id> -n trivy-scan-results
```

## Telegram Notifications

Automatic notifications are sent when **HIGH** or **CRITICAL** vulnerabilities are detected:

**Notification includes:**
- Severity level and emoji
- Vulnerability counts by severity
- Branch and commit information
- Link to detailed report

**Example:**
```
🔴 Security Alert - CRITICAL

🛡️ Vulnerabilities Detected

Severity Breakdown:
• 🔴 Critical: 2
• 🟠 High: 5
• 🟡 Medium: 12
• ⚪ Low: 8

🌿 Branch: main
📝 Commit: abc1234

⚠️ Action Required:
Review and patch vulnerabilities

🔗 View Report
```

## Remediation Workflow

### 1. Review Scan Results

Access the scan report:
```bash
# Download latest scan
gh run list --workflow=security-scan.yml --limit 1
gh run view <run-id>
gh run download <run-id> -n trivy-scan-results
```

### 2. Analyze Vulnerabilities

Review `security-scan-summary.json`:
```json
{
  "total": 27,
  "by_severity": {
    "CRITICAL": 2,
    "HIGH": 5,
    "MEDIUM": 12,
    "LOW": 8
  },
  "vulnerabilities_found": true
}
```

View details in `*-scan.txt` files for human-readable reports.

### 3. Prioritize Fixes

**Triage order:**
1. 🔴 CRITICAL - Immediate action
2. 🟠 HIGH - Urgent (within 7 days)
3. 🟡 MEDIUM - Scheduled (within 30 days)
4. ⚪ LOW - Optional

**Consider:**
- Exploitability (publicly known exploits?)
- Exposure (internet-facing component?)
- Data sensitivity (access to PII/credentials?)
- Workarounds available (can we mitigate risk?)

### 4. Apply Patches

#### Python Dependencies
```bash
# Update specific package
pip install --upgrade <package-name>

# Update requirements.txt
pip freeze > requirements.txt

# Test thoroughly
pytest tests/

# Commit
git add requirements.txt
git commit -m "security: Update <package> to patch CVE-XXXX-XXXXX"
```

#### Docker Base Image
```dockerfile
# Before
FROM python:3.11

# After - Use specific patched version
FROM python:3.11.8-slim-bookworm
```

#### Application Code
Follow Trivy's remediation guidance in the scan report.

### 5. Verify Fix

```bash
# Run security scan locally
docker build -t tsh-erp-app:test .
trivy image tsh-erp-app:test --severity HIGH,CRITICAL

# Or trigger GitHub workflow
gh workflow run security-scan.yml -f scan_type=all
```

### 6. Document

Create security advisory if needed:
1. Repository → **Security** → **Advisories**
2. **New draft security advisory**
3. Document vulnerability and fix
4. Publish to inform users

## Best Practices

### 1. Regular Scanning
- ✅ Run daily automated scans
- ✅ Scan before every production deployment
- ✅ Scan on dependency updates
- ✅ Monitor GitHub Security tab weekly

### 2. Rapid Response
- 🔴 CRITICAL: Patch within 24 hours
- 🟠 HIGH: Patch within 7 days
- 🟡 MEDIUM: Patch within 30 days

### 3. Defense in Depth
Security scanning is one layer. Also implement:
- **Secret management** - Use environment variables, not hardcoded secrets
- **Principle of least privilege** - Minimize permissions
- **Network segmentation** - Isolate sensitive components
- **Regular backups** - Ensure data recovery capability
- **Incident response plan** - Know what to do when compromised

### 4. Keep Dependencies Updated
```bash
# Check for updates weekly
pip list --outdated

# Update non-breaking changes
pip install --upgrade <package>

# Test after updates
pytest tests/
```

### 5. Minimize Attack Surface
```dockerfile
# Use minimal base images
FROM python:3.11-slim  # Not python:3.11

# Remove unnecessary packages
RUN apt-get purge -y --auto-remove <unused-package>

# Run as non-root user
USER app
```

## Troubleshooting

### False Positives

**Problem:** Vulnerability reported but not applicable

**Solutions:**
1. Verify vulnerability applies to your use case
2. Check if affected code path is unreachable
3. Add Trivy ignore rule:

```yaml
# .trivyignore
# Ignore specific CVE with justification
CVE-2023-12345  # Not applicable - affected module not used
```

### Scan Timeout

**Problem:** Scan takes too long and times out

**Solutions:**
1. Increase timeout in workflow:
```yaml
jobs:
  trivy-scan:
    timeout-minutes: 30  # Increase from 20
```

2. Split scans:
```yaml
jobs:
  scan-filesystem:
    uses: ./.github/workflows/security-scan.yml
    with:
      scan_type: filesystem

  scan-docker:
    uses: ./.github/workflows/security-scan.yml
    with:
      scan_type: docker
```

### Database Outdated

**Problem:** Trivy database is outdated

**Solution:** Trivy auto-updates, but you can force:
```bash
trivy image --download-db-only
trivy image <image-name>
```

### SARIF Upload Failed

**Problem:** Cannot upload to GitHub Security

**Solutions:**
1. Ensure `security-events: write` permission
2. Check SARIF file is valid:
```bash
cat filesystem-scan.sarif | jq .
```

## Integration Examples

### Slack Notification

```yaml
- name: Send Slack notification
  if: steps.scan-results.outputs.critical_count > 0
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "🔴 Critical vulnerabilities found in ${{ github.repository }}",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Security Alert*\n${{ steps.scan-results.outputs.critical_count }} critical vulnerabilities detected"
            }
          }
        ]
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### Jira Ticket Creation

```yaml
- name: Create Jira ticket for vulnerabilities
  if: steps.scan-results.outputs.high_count > 0
  uses: atlassian/gajira-create@v3
  with:
    project: SEC
    issuetype: Bug
    summary: "Security vulnerabilities detected in ${{ github.repository }}"
    description: |
      ${{ steps.scan-results.outputs.critical_count }} CRITICAL
      ${{ steps.scan-results.outputs.high_count }} HIGH

      Report: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
```

## Related Documentation

- [GitHub Secrets Setup](./github-secrets-setup.md)
- [Docker Build Workflow](./docker-workflows.md)
- [Deployment Security](./deployment-security.md)
- [CI/CD Pipeline Overview](./README.md)

## Resources

- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [CVE Database](https://cve.mitre.org/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [GitHub Security Features](https://docs.github.com/en/code-security)

---

**Version:** 1.0.0
**Last Updated:** 2025-01-11
**Maintained by:** TSH DevOps Team
