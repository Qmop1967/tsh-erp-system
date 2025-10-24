# TSH ERP System - Backup & Restore

Automated backup system for protecting your TSH ERP System data.

## 📁 Backup Structure

```
backups/
├── database/           # PostgreSQL database backups
├── images/            # Product images backups
├── env/               # Environment files backups (.env)
├── full/              # Complete system backups + logs
├── backup_database.sh # Database backup script
├── backup_images.sh   # Images backup script
├── backup_env.sh      # Environment files backup script
├── full_backup.sh     # Run all backups
└── restore.sh         # Restore from backups
```

## 🚀 Quick Start

### Run Full Backup
```bash
cd /Users/khaleelal-mulla/TSH_ERP_System_Local/backups
./full_backup.sh
```

### Restore from Latest Backup
```bash
cd /Users/khaleelal-mulla/TSH_ERP_System_Local/backups
./restore.sh
# Select option 1
```

## 📋 Individual Backup Scripts

### Database Backup
```bash
./backup_database.sh
```
- Backs up PostgreSQL database `tsh_erp`
- Creates compressed SQL dump
- Keeps last 30 days of backups
- Output: `database/tsh_erp_YYYYMMDD_HHMMSS.sql.gz`

### Product Images Backup
```bash
./backup_images.sh
```
- Backs up all product images from `static/images/products/`
- Creates compressed tar archive
- Keeps last 30 days of backups
- Output: `images/product_images_YYYYMMDD_HHMMSS.tar.gz`

### Environment Files Backup
```bash
./backup_env.sh
```
- Backs up all `.env` files in project
- Creates compressed tar archive
- Keeps last 90 days of backups (critical files)
- Output: `env/env_files_YYYYMMDD_HHMMSS.tar.gz`

## 🔄 Restore Options

The `restore.sh` script provides multiple restore options:

1. **Restore from latest backups** - Restores database, images, and env files from most recent backups
2. **Restore from specific full backup** - Choose a specific full backup archive
3. **Restore database only** - Restore just the database
4. **Restore images only** - Restore just product images
5. **Restore environment files only** - Restore just .env files

### Example: Restore Everything from Latest
```bash
./restore.sh
# Enter: 1
```

### Example: Restore Specific Component
```bash
./restore.sh
# Enter: 3 (for database only)
# Press Enter to use latest, or specify path
```

## ⏰ Automated Scheduled Backups

### Setup Daily Backups (macOS/Linux)

1. Open crontab editor:
```bash
crontab -e
```

2. Add daily backup at 2 AM:
```cron
0 2 * * * /Users/khaleelal-mulla/TSH_ERP_System_Local/backups/full_backup.sh >> /Users/khaleelal-mulla/TSH_ERP_System_Local/backups/full/cron.log 2>&1
```

3. Add weekly full backup on Sundays at 3 AM:
```cron
0 3 * * 0 /Users/khaleelal-mulla/TSH_ERP_System_Local/backups/full_backup.sh >> /Users/khaleelal-mulla/TSH_ERP_System_Local/backups/full/cron.log 2>&1
```

## 🛡️ Backup Strategy (3-2-1 Rule)

✅ **3 Copies**: Original data + local backup + GitHub
✅ **2 Media Types**: Local disk + cloud (GitHub)
✅ **1 Offsite**: GitHub remote repository

### What's Protected

| Component | Local Backup | GitHub | Notes |
|-----------|--------------|--------|-------|
| Source Code | ✅ | ✅ | Fully protected |
| Database | ✅ | ❌ | Use backup scripts |
| Product Images | ✅ | ❌ | Use backup scripts |
| .env Files | ✅ | ❌ | NEVER commit to GitHub |

### Recommended Backup Schedule

- **Daily**: Database backup (critical data changes daily)
- **Weekly**: Full backup (database + images + env)
- **After major changes**: Manual full backup
- **Before deployment**: Manual full backup
- **After code changes**: Git push to GitHub

## 📊 Monitoring Backups

### Check Latest Backups
```bash
ls -lh database/latest.sql.gz
ls -lh images/latest.tar.gz
ls -lh env/latest.tar.gz
ls -lh full/latest.tar.gz
```

### View Backup Logs
```bash
# View latest full backup log
ls -t full/backup_*.log | head -1 | xargs cat
```

### Check Backup Sizes
```bash
du -sh database/
du -sh images/
du -sh env/
du -sh full/
```

## ⚠️ Important Notes

1. **Database Credentials**: Ensure PostgreSQL user has proper permissions
2. **Disk Space**: Monitor available disk space for backups
3. **Security**: Keep `.env` backups secure - they contain sensitive data
4. **Testing**: Regularly test restore process in development environment
5. **Offsite**: Consider additional offsite backups (external drive, cloud storage)

## 🔧 Configuration

Edit the scripts to customize:
- Database name and user (default: `tsh_erp`, `postgres`)
- Backup retention periods (default: 30 days for DB/images, 90 days for env)
- Backup locations

## 🆘 Disaster Recovery

### Complete System Restore

1. Install fresh system with PostgreSQL and project dependencies
2. Clone project from GitHub
3. Restore from latest full backup:
```bash
cd backups
./restore.sh
# Select option 1
```
4. Verify all services start correctly
5. Test critical functionality

### Partial Data Loss

If only specific data is lost:
- **Database corruption**: Use `restore.sh` option 3
- **Images deleted**: Use `restore.sh` option 4
- **Config lost**: Use `restore.sh` option 5

## 📞 Support

For issues with backup system:
- Check backup logs in `full/` directory
- Verify disk space: `df -h`
- Verify PostgreSQL access: `psql -U postgres -d tsh_erp -c "SELECT 1;"`
- Check file permissions: `ls -la backups/*.sh`
