# TSH ERP Deployment Safety Rules

## CRITICAL: Production Deployment Policy

### Rule #1: NO DIRECT DEPLOYMENT TO PRODUCTION
**All production deployments MUST go through GitHub CI/CD pipeline ONLY.**

### Prohibited Actions:
1. ❌ Direct SSH to production VPS for deployment
2. ❌ Direct rsync/scp of files to production
3. ❌ Direct database changes on production
4. ❌ Manual service restarts on production (except emergencies)
5. ❌ Direct git pull on production server
6. ❌ Running deployment scripts manually on production

### Allowed Actions:
1. ✅ Push code to GitHub repository
2. ✅ Merge to main branch (triggers CI/CD)
3. ✅ Monitor GitHub Actions workflow
4. ✅ Read-only SSH access for monitoring/debugging
5. ✅ View logs and system status

### Proper Deployment Flow:
```
Local Development → Git Commit → Push to GitHub →
GitHub Actions CI/CD → Automated Tests →
Automated Security Scan → Automated Deployment to VPS
```

### Production Server Details:
- **VPS IP:** 167.71.39.50
- **Domains:** erp.tsh.sale, consumer.tsh.sale, shop.tsh.sale
- **Deployment Method:** GitHub Actions CI/CD ONLY

### Emergency Procedures:
In case of critical production issues:
1. Check GitHub Actions logs first
2. SSH for read-only investigation
3. If rollback needed, use GitHub Actions
4. Document all emergency actions

### Claude Code Instructions:
**Claude Code should NEVER execute these commands in production context:**
- `ssh root@167.71.39.50` followed by deployment commands
- `rsync` or `scp` to 167.71.39.50
- `git push` directly to production server
- Any command that modifies production files/database
- Manual service restarts on production

**Claude Code SHOULD:**
- Help with local development and testing
- Prepare code for GitHub push
- Guide users to use GitHub CI/CD
- Monitor deployment through GitHub Actions
- Help debug by reading logs only

---
**Last Updated:** November 3, 2025
**Enforcement:** Mandatory for all deployments
