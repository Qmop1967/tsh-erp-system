# Maintenance Scripts

This directory contains scripts for system maintenance and operational tasks.

## Available Scripts

### 💾 Backup Management
- **[backup.sh](backup.sh)** - System backup script
  - Database backup with compression
  - File system backup
  - Automated backup rotation
  - Backup integrity verification

## Usage

### Backup Operations
```bash
# Create full system backup
./scripts/maintenance/backup.sh

# Create database-only backup
./scripts/maintenance/backup.sh --database-only

# Create incremental backup
./scripts/maintenance/backup.sh --incremental
```

### Backup Strategy
- **Daily**: Automated incremental backups
- **Weekly**: Full system backups
- **Monthly**: Archived backups with long-term retention
- **Pre-deployment**: Manual backup before updates

## Backup Configuration

### Database Backup
```bash
# PostgreSQL backup with compression
pg_dump -h localhost -U username -d tsh_erp_prod | gzip > backup_$(date +%Y%m%d).sql.gz

# Backup with custom format for faster restoration
pg_dump -h localhost -U username -d tsh_erp_prod -Fc > backup_$(date +%Y%m%d).dump
```

### File System Backup
```bash
# Application files backup
tar -czf app_backup_$(date +%Y%m%d).tar.gz app/ config/ scripts/

# User uploads backup
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/

# Configuration files backup
tar -czf config_backup_$(date +%Y%m%d).tar.gz config/ .env
```

## Maintenance Tasks

### Regular Maintenance
- **Database Optimization**: Index rebuilding and statistics updates
- **Log Rotation**: Automated log cleanup and archiving
- **Disk Cleanup**: Temporary file cleanup and disk space optimization
- **Security Updates**: System and dependency updates

### Performance Maintenance
- **Database Vacuum**: PostgreSQL maintenance and optimization
- **Cache Cleanup**: Redis cache optimization
- **File Cleanup**: Temporary and obsolete file removal
- **Index Optimization**: Database index maintenance

### Security Maintenance
- **Certificate Renewal**: SSL certificate updates
- **Password Rotation**: System password updates
- **Access Review**: User access audit and cleanup
- **Vulnerability Scanning**: Security vulnerability assessment

## Monitoring & Alerts

### System Monitoring
- **Disk Space**: Alert when disk usage > 80%
- **Memory Usage**: Alert when memory usage > 85%
- **Database Size**: Monitor database growth
- **Backup Status**: Alert on backup failures

### Performance Monitoring
- **Response Time**: API response time monitoring
- **Database Performance**: Slow query detection
- **Error Rates**: Application error monitoring
- **Resource Usage**: CPU and memory monitoring

## Backup Verification

### Integrity Checks
```bash
# Verify backup integrity
gzip -t backup_$(date +%Y%m%d).sql.gz

# Test database restore
pg_restore -h localhost -U username -d test_db backup_$(date +%Y%m%d).dump
```

### Restoration Testing
- **Monthly**: Full backup restoration testing
- **Quarterly**: Disaster recovery simulation
- **Annual**: Complete system restoration testing
- **Documentation**: Restoration procedure documentation

## Automation

### Cron Jobs
```bash
# Daily backup at 2 AM
0 2 * * * /path/to/scripts/maintenance/backup.sh

# Weekly full backup on Sunday at 1 AM
0 1 * * 0 /path/to/scripts/maintenance/backup.sh --full

# Monthly cleanup on 1st of month at 3 AM
0 3 1 * * /path/to/scripts/maintenance/cleanup.sh
```

### Monitoring Integration
- **Nagios**: System monitoring integration
- **Zabbix**: Infrastructure monitoring
- **Grafana**: Performance dashboards
- **Slack**: Alert notifications

## Troubleshooting

### Common Issues
- **Backup Failures**: Check disk space and permissions
- **Slow Backups**: Optimize database and compression settings
- **Restoration Issues**: Verify backup integrity and target environment
- **Space Issues**: Implement backup rotation and cleanup

### Emergency Procedures
- **Backup Corruption**: Use previous backup versions
- **Disk Full**: Emergency cleanup procedures
- **Database Issues**: Emergency restore procedures
- **System Failure**: Disaster recovery procedures

## Best Practices

### Backup Best Practices
- **3-2-1 Rule**: 3 copies, 2 different media, 1 offsite
- **Encryption**: Encrypt sensitive backups
- **Compression**: Use appropriate compression algorithms
- **Verification**: Always verify backup integrity

### Security Practices
- **Access Control**: Restrict backup file access
- **Encryption**: Encrypt backups in transit and at rest
- **Audit Trail**: Log all backup operations
- **Retention**: Implement proper backup retention policies

### Performance Optimization
- **Timing**: Schedule backups during low-usage periods
- **Incremental**: Use incremental backups for large datasets
- **Compression**: Balance compression ratio vs. speed
- **Parallelization**: Use parallel backup processes when possible 