# TSH ERP Backup System - Quick Start Guide

## ✅ Backup System Successfully Installed!

Your automated backup system is now ready to protect your TSH ERP data.

---

## 🚀 Quick Commands

### Run Full Backup (Recommended)
```bash
cd /Users/khaleelal-mulla/TSH_ERP_System_Local/backups
./full_backup.sh
```
**What it does**: Backs up database (24K), product images (384M), and environment files (4K)

### Restore Everything
```bash
cd /Users/khaleelal-mulla/TSH_ERP_System_Local/backups
./restore.sh
```
Then select option `1` to restore from latest backups.

---

## 📊 What's Being Backed Up

| Component | Size | Location | Count |
|-----------|------|----------|-------|
| **Database** | 24KB | `tsh_erp_db` | All tables |
| **Backend Images** | ~10MB | `app/static/images/products/` | 15 images |
| **Frontend Images** | ~380MB | `frontend/public/images/products/` | 825 images |
| **Environment Files** | 4KB | `.env` files | 3 files |

**Total Backup Size**: ~384MB per full backup

---

## ⏰ Recommended Backup Schedule

### Daily (Automatic)
Set up automated daily backups at 2 AM:
```bash
crontab -e
```
Add this line:
```
0 2 * * * /Users/khaleelal-mulla/TSH_ERP_System_Local/backups/full_backup.sh >> /Users/khaleelal-mulla/TSH_ERP_System_Local/backups/full/cron.log 2>&1
```

### Manual (Before Important Changes)
```bash
cd /Users/khaleelal-mulla/TSH_ERP_System_Local/backups
./full_backup.sh
```

---

## 📁 Backup Files Location

```
/Users/khaleelal-mulla/TSH_ERP_System_Local/backups/
├── database/
│   ├── latest.sql.gz              → Latest database backup
│   └── tsh_erp_YYYYMMDD_HHMMSS.sql.gz
├── images/
│   ├── latest.tar.gz              → Latest images backup
│   └── product_images_YYYYMMDD_HHMMSS.tar.gz
├── env/
│   ├── latest.tar.gz              → Latest .env files backup
│   └── env_files_YYYYMMDD_HHMMSS.tar.gz
└── full/
    ├── latest.tar.gz              → Latest complete backup
    ├── tsh_erp_full_YYYYMMDD_HHMMSS.tar.gz
    └── backup_YYYYMMDD_HHMMSS.log → Backup logs
```

---

## 🔄 Restore Scenarios

### Scenario 1: Complete System Failure
```bash
./restore.sh
# Select: 1 (Restore from latest backups)
```
Restores: Database + Images + Environment files

### Scenario 2: Database Corruption Only
```bash
./restore.sh
# Select: 3 (Restore database only)
# Press Enter for latest
```

### Scenario 3: Accidentally Deleted Images
```bash
./restore.sh
# Select: 4 (Restore images only)
# Press Enter for latest
```

### Scenario 4: Lost .env Configuration
```bash
./restore.sh
# Select: 5 (Restore environment files only)
# Press Enter for latest
```

---

## 🛡️ Protection Strategy

### Three-Layer Protection (3-2-1 Rule)

✅ **Layer 1**: Local backups (this system)
- Database backups (kept 30 days)
- Image backups (kept 30 days)
- Config backups (kept 90 days)

✅ **Layer 2**: GitHub repository
- Source code fully versioned
- Complete development history
- Branch: `clean-main`

✅ **Layer 3**: Offsite storage (recommended to add)
- External hard drive
- Cloud storage (Google Drive, Dropbox)
- Another computer/server

---

## ⚠️ Important Notes

1. **Backup Retention**:
   - Database: 30 days (automatic cleanup)
   - Images: 30 days (automatic cleanup)
   - Environment files: 90 days (automatic cleanup)
   - Full backups: Last 14 (automatic cleanup)

2. **Disk Space**: Monitor available space - each full backup is ~384MB

3. **Security**: Never commit `.env` backups to GitHub (they contain passwords!)

4. **Testing**: Test restore process monthly in development environment

---

## 📈 Monitoring Your Backups

### Check Latest Backup Status
```bash
ls -lh backups/database/latest.sql.gz
ls -lh backups/images/latest.tar.gz
ls -lh backups/env/latest.tar.gz
```

### View Last Backup Log
```bash
ls -t backups/full/backup_*.log | head -1 | xargs cat
```

### Check Disk Usage
```bash
du -sh backups/database/
du -sh backups/images/
du -sh backups/env/
du -sh backups/full/
```

---

## 🆘 Emergency Contacts

- **Backup System Issues**: Check `backups/full/backup_*.log` files
- **Restore Problems**: Verify PostgreSQL is running: `psql -l`
- **Disk Full**: Clean old backups manually or increase retention

---

## ✨ Success Indicators

After running `./full_backup.sh`, you should see:
```
✓ Database backup completed successfully!
  File: .../database/tsh_erp_YYYYMMDD_HHMMSS.sql.gz
  Size: 24K

✓ Product images backup completed successfully!
  File: .../images/product_images_YYYYMMDD_HHMMSS.tar.gz
  Size: 384M
  Images: 840

✓ Environment files backup completed successfully!
  File: .../env/env_files_YYYYMMDD_HHMMSS.tar.gz
  Size: 4.0K
  Files: 3

✓ FULL BACKUP COMPLETED SUCCESSFULLY!
```

---

**System Status**: ✅ **FULLY OPERATIONAL**

Last tested: October 6, 2025
Database: tsh_erp_db (24KB)
Images: 840 files (384MB)
Environment: 3 files (4KB)
