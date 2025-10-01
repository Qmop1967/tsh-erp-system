# 🔧 TSH ERP System - Maintenance Guide

## Daily Maintenance Tasks

### Database Backups
Run automated backups daily:
```bash
./scripts/backup_database.sh
```

Set up cron job for automatic daily backups at 2 AM:
```bash
crontab -e
# Add this line:
0 2 * * * cd /path/to/TSH_ERP_System_Local && ./scripts/backup_database.sh >> logs/backup.log 2>&1
```

### Log Monitoring
Check application logs for errors:
```bash
# Backend logs
tail -f logs/app.log

# Database logs
sudo tail -f /var/log/postgresql/postgresql-*.log

# Nginx logs (if applicable)
sudo tail -f /var/log/nginx/error.log
```

### System Health Check
Monitor system resources:
```bash
# Check disk space
df -h

# Check memory usage
free -m

# Check running processes
ps aux | grep uvicorn

# Check database connections
psql -U khaleelal-mulla -d erp_db -c "SELECT COUNT(*) FROM pg_stat_activity;"
```

## Weekly Maintenance Tasks

### Security Audit
Run security audit weekly:
```bash
./scripts/security_audit.sh
```

### Database Optimization
Analyze and vacuum database:
```bash
psql -U khaleelal-mulla -d erp_db -c "VACUUM ANALYZE;"
```

### Update Dependencies
Check for security updates:
```bash
# Python packages
source .venv/bin/activate
pip list --outdated

# Node packages
cd frontend
npm outdated
```

### Review Error Logs
Analyze error patterns:
```bash
# Find most common errors
grep ERROR logs/app.log | sort | uniq -c | sort -rn | head -20
```

## Monthly Maintenance Tasks

### Database Backup Rotation
Verify backup retention policy:
```bash
ls -lh backups/tsh_erp_backup_*.sql.gz
```

### Performance Review
Check database performance:
```bash
psql -U khaleelal-mulla -d erp_db -c "
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC 
LIMIT 10;
"
```

### Update System
Apply security patches:
```bash
# Update OS packages
sudo apt update && sudo apt upgrade  # Ubuntu/Debian
# or
brew upgrade  # macOS

# Update Python dependencies
pip install --upgrade -r config/requirements.txt

# Update frontend dependencies
cd frontend && npm update
```

### Audit User Accounts
Review active users and permissions:
```bash
psql -U khaleelal-mulla -d erp_db -c "
SELECT u.username, u.email, u.is_active, r.name as role 
FROM users u 
LEFT JOIN roles r ON u.role_id = r.id 
ORDER BY u.created_at DESC;
"
```

## Quarterly Maintenance Tasks

### Full System Backup
Create complete system backup:
```bash
# Database
./scripts/backup_database.sh

# Application files
tar -czf tsh_erp_system_backup_$(date +%Y%m%d).tar.gz \
  --exclude='.venv' \
  --exclude='node_modules' \
  --exclude='backups' \
  /path/to/TSH_ERP_System_Local/
```

### Security Penetration Testing
Conduct security assessment:
- Review access controls
- Test authentication mechanisms
- Verify data encryption
- Check for SQL injection vulnerabilities

### Disaster Recovery Test
Test backup restoration:
```bash
# Create test database
createdb erp_db_test

# Restore from backup
gunzip -c backups/latest_backup.sql.gz | psql -U khaleelal-mulla erp_db_test

# Verify data integrity
psql -U khaleelal-mulla -d erp_db_test -c "\dt"
```

### Documentation Update
Review and update:
- API documentation
- User guides
- Deployment procedures
- Runbooks

## Emergency Procedures

### System Downtime
1. Check service status:
```bash
systemctl status tsh-erp  # or your service name
```

2. Check logs for errors:
```bash
tail -100 logs/app.log
```

3. Restart services:
```bash
systemctl restart tsh-erp
```

### Database Connection Issues
1. Check PostgreSQL status:
```bash
pg_isready
systemctl status postgresql
```

2. Check connection pool:
```bash
psql -U khaleelal-mulla -d erp_db -c "
SELECT count(*), state 
FROM pg_stat_activity 
GROUP BY state;
"
```

3. Kill idle connections if needed:
```bash
psql -U khaleelal-mulla -d erp_db -c "
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle' 
AND state_change < NOW() - INTERVAL '10 minutes';
"
```

### High CPU/Memory Usage
1. Identify resource-heavy queries:
```bash
psql -U khaleelal-mulla -d erp_db -c "
SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
FROM pg_stat_activity 
WHERE state = 'active' 
ORDER BY duration DESC;
"
```

2. Check system resources:
```bash
top
htop
```

3. Restart application if necessary

### Data Corruption
1. Stop application
2. Restore from latest backup
3. Run integrity checks
4. Restart application
5. Verify data

## Monitoring Alerts

### Set Up Alerts For:
- Disk space < 20%
- Memory usage > 80%
- Database connection pool exhausted
- API response time > 3 seconds
- Error rate > 5%
- Backup failures
- SSL certificate expiration (30 days)

## Performance Optimization

### Database Indexing
Review and create indexes:
```bash
psql -U khaleelal-mulla -d erp_db -c "
SELECT schemaname, tablename, indexname 
FROM pg_indexes 
WHERE schemaname = 'public' 
ORDER BY tablename;
"
```

### Query Optimization
Analyze slow queries:
```bash
psql -U khaleelal-mulla -d erp_db -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
"
```

### Cache Management
Clear application cache if needed:
```bash
# Redis (if using)
redis-cli FLUSHALL

# Application restart
systemctl restart tsh-erp
```

## Contact Information

**Technical Support:**
- Email: support@yourdomain.com
- Phone: +XXX-XXX-XXXX

**On-Call Engineer:**
- Phone: +XXX-XXX-XXXX

**Emergency Escalation:**
- Technical Lead: [contact]
- DevOps Lead: [contact]

---

**Last Updated**: September 30, 2025  
**Version**: 1.0.0
