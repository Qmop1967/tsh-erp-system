# TDS Auto-Sync Guide
**Automatic Comparison & Synchronization between Zoho and TSH ERP**

---

## 📋 Overview

The TDS Auto-Sync system automatically compares Zoho Books data with TSH ERP data and syncs any differences. This ensures your local database stays perfectly synchronized with Zoho.

### What Gets Compared & Synced

| Entity | Description | Auto-Sync |
|--------|-------------|-----------|
| **Items** | Products/inventory items | ✅ Yes |
| **Stock** | Inventory levels | ✅ Yes |
| **Images** | Product images | ✅ Yes |
| **Price Lists** | Consumer/wholesale pricing | ✅ Yes |
| **Customers** | Client records | ✅ Yes |
| **Vendors** | Supplier records | ✅ Yes |

---

## 🚀 Quick Start

### Option 1: Run Comparison Only (No Sync)

```bash
# Simple comparison report
python tds_compare_and_sync.py

# Compare specific entities only
python tds_compare_and_sync.py --entities items stock images price_lists
```

**Output:**
```
📊 QUICK SUMMARY
Health Score: 98.5/100 (EXCELLENT)
Overall Match: 98.7%

Comparisons:
  ✅ items           Zoho:  1,250 | Local:  1,240 | Diff:    +10 | Match:  99.2%
  ✅ stock           Zoho:  1,180 | Local:  1,175 | Diff:     +5 | Match:  99.6%
  ⚠️  images         Zoho:    850 | Local:    780 | Diff:    +70 | Match:  91.8%
  ✅ price_lists     Zoho:      2 | Local:      2 | Diff:     +0 | Match: 100.0%
```

### Option 2: Run Comparison + Auto-Sync

```bash
# Compare and automatically sync differences
python tds_compare_and_sync.py --sync

# Dry run (see what would be synced without actually syncing)
python tds_compare_and_sync.py --sync --dry-run
```

**Output:**
```
🔄 AUTO-SYNC MODE - Syncing differences

📦 ITEMS: INCREMENTAL_SYNC
   Difference: +10 items
   Priority: 8/10
   ✅ Synced: 10 | Failed: 0 | Skipped: 0

📦 IMAGES: DOWNLOAD_MISSING
   Difference: +70 images
   Priority: 6/10
   ✅ Synced: 70 | Failed: 0 | Skipped: 0

✅ Auto-sync complete!
```

---

## ⏰ Automated Scheduling (Every 6 Hours)

### Method 1: Run Scheduler Script (Recommended)

The scheduler script runs continuously and executes comparison + auto-sync every 6 hours.

```bash
# Run scheduler (keeps running, syncs every 6 hours)
python tds_auto_sync_scheduler.py

# Custom interval (e.g., every 12 hours)
python tds_auto_sync_scheduler.py --interval 12

# Dry run mode (test without actual syncing)
python tds_auto_sync_scheduler.py --dry-run
```

**Output:**
```
🚀 TDS AUTO-SYNC SCHEDULER STARTING
   Interval: Every 6 hours
   Mode: LIVE SYNC
   Started: 2025-01-09 14:30:00

✅ Scheduler started successfully
   Next scheduled run: 6 hours from now
   Press Ctrl+C to stop
```

**To run as background service:**
```bash
# Using nohup (Linux/Mac)
nohup python tds_auto_sync_scheduler.py > logs/scheduler.log 2>&1 &

# Using screen (Linux/Mac)
screen -dmS tds_scheduler python tds_auto_sync_scheduler.py

# Check if running
ps aux | grep tds_auto_sync_scheduler
```

### Method 2: Cron Job (Alternative)

If you prefer cron, run the script once every 6 hours:

```bash
# Edit crontab
crontab -e

# Add this line (runs every 6 hours: 00:00, 06:00, 12:00, 18:00)
0 */6 * * * cd /path/to/TSH_ERP_Ecosystem && python tds_auto_sync_scheduler.py --once >> logs/cron_tds_sync.log 2>&1
```

**Alternative cron schedules:**
```bash
# Every 12 hours (00:00, 12:00)
0 */12 * * * cd /path/to/TSH_ERP_Ecosystem && python tds_auto_sync_scheduler.py --once

# Every 4 hours
0 */4 * * * cd /path/to/TSH_ERP_Ecosystem && python tds_auto_sync_scheduler.py --once

# Specific times (2 AM, 8 AM, 2 PM, 8 PM)
0 2,8,14,20 * * * cd /path/to/TSH_ERP_Ecosystem && python tds_auto_sync_scheduler.py --once
```

---

## 📊 Understanding the Reports

### Health Score

| Score | Status | Meaning | Action |
|-------|--------|---------|--------|
| 95-100 | EXCELLENT | Perfect sync | None needed |
| 90-94 | GOOD | Minor differences | Monitor |
| 80-89 | WARNING | Sync recommended | Run --sync |
| <80 | CRITICAL | Immediate action required | Run --sync ASAP |

### Match Percentage

- **100%**: Perfect match between Zoho and local
- **95-99%**: Minor differences (normal)
- **90-94%**: Moderate differences (sync recommended)
- **<90%**: Significant differences (sync required)

### Sync Recommendations

The system automatically determines what needs to be synced:

| Recommendation | Meaning |
|----------------|---------|
| `NO_SYNC_NEEDED` | Data is in sync |
| `INCREMENTAL_SYNC` | Sync only changed items |
| `FULL_SYNC` | Complete resync needed |
| `DOWNLOAD_MISSING` | Download missing items (e.g., images) |
| `RECONCILIATION` | Complex differences requiring manual review |

---

## 🔧 Advanced Usage

### Compare Specific Entities Only

```bash
# Compare only items and stock
python tds_compare_and_sync.py --entities items stock

# Compare only images
python tds_compare_and_sync.py --entities images --sync
```

### Monitoring and Logs

All operations are logged to:
- **Console**: Real-time output
- **File**: `logs/tds_auto_sync.log`
- **Summary**: `logs/tds_auto_sync_summary.txt`

```bash
# Watch logs in real-time
tail -f logs/tds_auto_sync.log

# View summary of recent runs
cat logs/tds_auto_sync_summary.txt
```

### Using the Original Statistics Script

The original script is still available for advanced use:

```bash
# Full comparison with detailed output
python run_tds_statistics.py

# Auto-sync with detailed output
python run_tds_statistics.py --auto-sync

# Save report to JSON
python run_tds_statistics.py --output report.json

# Specific entities + auto-sync + dry-run
python run_tds_statistics.py --entities items images --auto-sync --dry-run
```

---

## 🔒 Safety Features

### 1. Dry Run Mode
Test without making changes:
```bash
python tds_compare_and_sync.py --sync --dry-run
```

### 2. Incremental Sync
Only syncs changes, not entire database (fast & safe)

### 3. Auto-Healing
If sync fails, it will retry automatically (built into TDS)

### 4. Circuit Breaker
Protects against API failures (automatic fallback)

### 5. Logging & Auditing
All operations are logged with timestamps and correlation IDs

---

## 🚨 Troubleshooting

### Issue: "No differences found but data looks wrong"

**Solution:**
```bash
# Force a full comparison
python run_tds_statistics.py --auto-sync
```

### Issue: "Sync keeps failing"

**Possible causes:**
1. Zoho API token expired → Check `.env` file
2. Network issues → Check internet connection
3. Database connection issues → Check PostgreSQL

**Solution:**
```bash
# Check TDS health
python run_tds_zoho_sync.py --test-connection

# View detailed logs
tail -100 logs/tds_auto_sync.log
```

### Issue: "Scheduler stopped running"

**Check if process is running:**
```bash
ps aux | grep tds_auto_sync_scheduler
```

**Restart scheduler:**
```bash
# Kill old process
pkill -f tds_auto_sync_scheduler

# Start new process
nohup python tds_auto_sync_scheduler.py > logs/scheduler.log 2>&1 &
```

### Issue: "Too many differences detected"

This usually indicates:
- First time running (normal)
- Long period without sync (normal)
- Data integrity issue (investigate)

**Solution:**
```bash
# Run dry-run first to see what would be synced
python tds_compare_and_sync.py --sync --dry-run

# If looks good, run actual sync
python tds_compare_and_sync.py --sync
```

---

## 📈 Performance

| Operation | Time | Frequency |
|-----------|------|-----------|
| Quick comparison | 20-30 sec | Every 6 hours |
| Items sync (100 items) | ~30 sec | As needed |
| Stock sync (1000 items) | ~2 min | As needed |
| Image download (50 images) | ~5 min | As needed |
| Full sync (10K items) | ~5 min | Rare |

---

## 🎯 Best Practices

### 1. Start with Dry Run
Always test with `--dry-run` first:
```bash
python tds_compare_and_sync.py --sync --dry-run
```

### 2. Monitor First Few Runs
Watch the logs for the first 2-3 scheduled runs to ensure everything works:
```bash
tail -f logs/tds_auto_sync.log
```

### 3. Check Summary Regularly
Review the summary file weekly:
```bash
cat logs/tds_auto_sync_summary.txt
```

### 4. Set Up Alerts
Configure email/Slack alerts for critical issues (see alert configuration in code)

### 5. Regular Health Checks
Run manual comparison weekly:
```bash
python tds_compare_and_sync.py
```

---

## 📞 Support

### Quick Reference

| Task | Command |
|------|---------|
| Compare only | `python tds_compare_and_sync.py` |
| Compare + sync | `python tds_compare_and_sync.py --sync` |
| Dry run | `python tds_compare_and_sync.py --sync --dry-run` |
| Start scheduler | `python tds_auto_sync_scheduler.py` |
| Run once (cron) | `python tds_auto_sync_scheduler.py --once` |
| View logs | `tail -f logs/tds_auto_sync.log` |
| View summary | `cat logs/tds_auto_sync_summary.txt` |

### Need Help?

- **Logs**: Check `logs/tds_auto_sync.log`
- **Summary**: Check `logs/tds_auto_sync_summary.txt`
- **Full docs**: See `TDS_MASTER_ARCHITECTURE.md`

---

**Last Updated:** January 9, 2025
**Version:** 1.0.0
**Status:** Production Ready ✅
