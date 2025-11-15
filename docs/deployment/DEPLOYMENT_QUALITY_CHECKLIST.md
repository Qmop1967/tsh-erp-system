# TSH ERP Deployment Quality Checklist

**Version:** 1.0.0
**Last Updated:** 2025-11-15
**Purpose:** Comprehensive checklist for production-ready deployments

---

## Pre-Deployment Checklist

### Code Quality
- [ ] All linting checks pass (Ruff)
- [ ] Type checking passes (MyPy)
- [ ] Security scan passes (Bandit)
- [ ] Unit tests pass (>80% coverage)
- [ ] Integration tests pass
- [ ] No TODO or FIXME comments in critical paths

### Documentation
- [ ] API documentation is up-to-date
- [ ] CHANGELOG.md updated with new features/fixes
- [ ] Environment variable changes documented
- [ ] Migration scripts documented
- [ ] Rollback procedures verified

### Environment Parity
- [ ] Staging environment matches production configuration
- [ ] Database schemas are identical (use schema-drift-check)
- [ ] Environment variables validated
- [ ] Secrets configured and rotated
- [ ] SSL certificates valid and not expiring soon

### Database
- [ ] Alembic migrations tested on staging
- [ ] Migrations are reversible
- [ ] Database backup completed (< 30 minutes old)
- [ ] Backup uploaded to AWS S3
- [ ] Migration rollback procedure tested

### Docker & Infrastructure
- [ ] All Docker images build successfully
- [ ] Image sizes optimized (< 500MB for backend)
- [ ] Health checks configured for all services
- [ ] Resource limits set appropriately
- [ ] No hardcoded credentials in images

### Blue-Green Deployment
- [ ] Both slots can run simultaneously
- [ ] Health check endpoints respond correctly
- [ ] Nginx configuration updated and tested
- [ ] Zero-downtime deployment verified on staging
- [ ] Rollback procedure tested on staging

---

## Deployment Execution Checklist

### Pre-Deployment Actions
- [ ] Notify team in Telegram about deployment
- [ ] Set maintenance window (if required)
- [ ] Verify staging deployment succeeded
- [ ] Review recent commits for breaking changes
- [ ] Confirm all GitHub Actions workflows passed

### During Deployment
- [ ] Monitor GitHub Actions workflow progress
- [ ] Watch server logs for errors
- [ ] Monitor database connection pool
- [ ] Check Redis connectivity
- [ ] Verify SSL certificate validity

### Health Checks
- [ ] `/health` endpoint returns 200 OK
- [ ] `/docs` API documentation accessible
- [ ] `/openapi.json` returns valid spec
- [ ] Database connectivity confirmed
- [ ] Redis connectivity confirmed
- [ ] NeuroLink service healthy
- [ ] TDS Dashboard accessible

### Smoke Tests
- [ ] Authentication endpoints respond correctly
- [ ] Product listing works
- [ ] Customer login succeeds
- [ ] Order creation functional
- [ ] Inventory updates working
- [ ] Real-time notifications operational

---

## Post-Deployment Checklist

### Verification (First 15 minutes)
- [ ] All health checks pass
- [ ] Public endpoint responds (https://erp.tsh.sale)
- [ ] Consumer app works (https://consumer.tsh.sale)
- [ ] TDS Dashboard accessible (https://tds.tsh.sale)
- [ ] No errors in application logs
- [ ] No database connection errors
- [ ] Redis cache operational

### Monitoring (First hour)
- [ ] Response times < 500ms for 95% of requests
- [ ] Error rate < 0.1%
- [ ] CPU usage < 60%
- [ ] Memory usage < 70%
- [ ] Database connections < 80% of pool
- [ ] No webhook delivery failures

### Business Validation
- [ ] Test wholesale order creation
- [ ] Test retail sale transaction
- [ ] Verify inventory synchronization
- [ ] Check salesperson GPS tracking
- [ ] Confirm WhatsApp notifications working
- [ ] Verify Zoho sync operational (via TDS Core)

### Communication
- [ ] Send deployment success notification
- [ ] Update team on any issues encountered
- [ ] Document any manual interventions required
- [ ] Update deployment log

---

## Rollback Triggers

**Immediate rollback if:**
- Health checks fail for > 2 minutes
- Error rate > 5%
- Database connection failures
- Critical functionality broken (orders, authentication)
- Response time degradation > 300%
- Security vulnerability detected

**Consider rollback if:**
- Minor feature not working as expected
- Non-critical error rate increase
- Performance degradation < 200%
- User complaints > 10 in first hour

---

## Rollback Procedure

### Automatic Rollback (CI/CD)
1. GitHub Actions detects failure
2. Stops new deployment slot
3. Switches Nginx back to previous slot
4. Verifies health checks pass
5. Sends alert notification

### Manual Rollback
```bash
# SSH to production server
ssh root@167.71.39.50

# Navigate to deployment directory
cd /opt/tsh-erp

# Run rollback script
./scripts/deployment/rollback.sh

# Verify health
curl https://erp.tsh.sale/health
```

**Rollback SLA:** < 2 minutes from decision to working state

---

## Environment-Specific Checklists

### Staging Deployment
- [ ] Deployed to correct server (167.71.58.65)
- [ ] Using staging SSH key
- [ ] Deployed from `develop` branch
- [ ] Using staging database
- [ ] Staging environment variables loaded
- [ ] Debug mode enabled
- [ ] Test data populated

### Production Deployment
- [ ] Deployed to correct server (167.71.39.50)
- [ ] Using production SSH key
- [ ] Deployed from `main` branch
- [ ] Using production database
- [ ] Production environment variables loaded
- [ ] Debug mode disabled
- [ ] Real-time monitoring active

---

## Performance Thresholds

### Response Times
| Endpoint Category | Target | Warning | Critical |
|-------------------|--------|---------|----------|
| Health checks     | < 100ms | > 200ms | > 500ms |
| Read operations   | < 300ms | > 600ms | > 1000ms |
| Write operations  | < 500ms | > 1000ms | > 2000ms |
| Search queries    | < 400ms | > 800ms | > 1500ms |

### Resource Utilization
| Resource | Normal | Warning | Critical |
|----------|--------|---------|----------|
| CPU      | < 50% | > 70% | > 85% |
| Memory   | < 60% | > 75% | > 90% |
| Disk I/O | < 50% | > 70% | > 85% |
| DB Connections | < 60% | > 80% | > 95% |

---

## Security Checklist

### Pre-Deployment Security
- [ ] Secrets rotated regularly (< 90 days)
- [ ] No credentials in git history
- [ ] SSL certificates valid (> 30 days remaining)
- [ ] Security headers configured (HSTS, CSP)
- [ ] Rate limiting enabled
- [ ] CORS properly configured

### Post-Deployment Security
- [ ] Authentication working correctly
- [ ] RBAC permissions enforced
- [ ] API key validation working
- [ ] No exposed sensitive endpoints
- [ ] Audit logs capturing events
- [ ] Intrusion detection active

---

## Troubleshooting Quick Reference

### Common Issues

#### Issue: Health check fails
```bash
# Check service status
docker ps
docker logs tsh_erp_app_blue --tail 100

# Check database connectivity
docker exec tsh_postgres pg_isready

# Check Redis connectivity
docker exec tsh_redis redis-cli ping
```

#### Issue: Nginx not routing traffic
```bash
# Test nginx configuration
nginx -t

# Check upstream status
curl http://localhost:8001/health  # Blue slot
curl http://localhost:8011/health  # Green slot

# Reload nginx
nginx -s reload
```

#### Issue: Database migration fails
```bash
# Check current revision
docker exec tsh_erp_app_blue alembic current

# View migration history
docker exec tsh_erp_app_blue alembic history

# Rollback one migration
docker exec tsh_erp_app_blue alembic downgrade -1
```

---

## Deployment Metrics

### Track These Metrics
- Deployment frequency (target: 1-2 per week)
- Deployment duration (target: < 10 minutes)
- Success rate (target: > 95%)
- Rollback rate (target: < 5%)
- Mean time to recovery (target: < 2 minutes)
- Change failure rate (target: < 5%)

### Continuous Improvement
- Review failed deployments weekly
- Update checklist based on incidents
- Automate manual verification steps
- Improve rollback speed and reliability
- Enhance monitoring and alerting

---

## Sign-Off

### Deployment Approval Required From:
- [ ] Technical Lead
- [ ] DevOps Engineer
- [ ] QA Team
- [ ] Product Owner (for major releases)

### Post-Deployment Review:
- Deployment Date: _________________
- Deployed By: _________________
- Deployment Duration: _________________
- Issues Encountered: _________________
- Rollback Required: Yes / No
- Lessons Learned: _________________

---

**Remember:**
- Production serves 500+ real clients
- Multi-million IQD daily revenue
- Zero-downtime is mandatory
- Always test on staging first
- When in doubt, rollback

**Last Updated:** 2025-11-15
**Next Review:** 2025-12-15
