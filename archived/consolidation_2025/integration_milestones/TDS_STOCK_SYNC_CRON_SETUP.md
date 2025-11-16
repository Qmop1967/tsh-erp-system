# TDS Stock Sync - Cron Setup Guide

## Overview

This guide explains how to set up automated stock synchronization using cron jobs for the TDS Stock Sync system.

**Status**: ✅ Cron job configured and ready
**Schedule**: Every 4 hours (00:00, 04:00, 08:00, 12:00, 16:00, 20:00)

---

## Current Configuration

### Local Development Setup

**Cron Schedule**: Every 4 hours
**Script**: `/Users/khaleelal-mulla/TSH_ERP_Ecosystem/scripts/run_stock_sync.sh`
**Log File**: `/Users/khaleelal-mulla/TSH_ERP_Ecosystem/logs/tds_stock_sync_cron.log`

**Cron Entry**:
```bash
# TDS Stock Sync - Runs every 4 hours
# Syncs item stock from Zoho Books to local database
0 */4 * * * /Users/khaleelal-mulla/TSH_ERP_Ecosystem/scripts/run_stock_sync.sh >> /Users/khaleelal-mulla/TSH_ERP_Ecosystem/logs/tds_stock_sync_cron.log 2>&1
```

---

## Production Server Setup

### Method 1: API-Based Sync (Recommended)

This method calls the backend API endpoint, which is more reliable and doesn't require direct database access.

**Prerequisites**:
- Backend must be running (uvicorn/gunicorn)
- Backend accessible on localhost or configured URL

**Script**: `scripts/run_stock_sync.sh`

```bash
#!/bin/bash
# Production Stock Sync via API

cd /opt/tsh_erp || exit 1

# Load environment
export $(cat .env | grep -v '^#' | xargs)

# Backend URL (adjust as needed)
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"

# Trigger sync via API
curl -X POST "${BACKEND_URL}/api/bff/tds/sync/stock?batch_size=200&active_only=true" \
  -H "Content-Type: application/json"
```

**Production Cron Entry**:
```bash
# Add to /etc/cron.d/tds-stock-sync or user crontab
0 */4 * * * /opt/tsh_erp/scripts/run_stock_sync.sh >> /var/log/tds/stock_sync.log 2>&1
```

### Method 2: Direct Python Script

For environments where you want to run the sync independently of the backend.

**Prerequisites**:
- Python 3.9+
- Virtual environment activated
- Database credentials configured

**Production Cron Entry**:
```bash
# Add to crontab
0 */4 * * * cd /opt/tsh_erp && source .venv/bin/activate && python scripts/tds_sync_stock.py --batch-size 200 >> /var/log/tds/stock_sync.log 2>&1
```

---

## Installation Instructions

### For Production Server (VPS)

1. **SSH into your server**:
```bash
ssh tsh@erp.tsh.sale
```

2. **Create log directory**:
```bash
sudo mkdir -p /var/log/tds
sudo chown tsh:tsh /var/log/tds
```

3. **Copy sync script**:
```bash
# Make sure script is executable
chmod +x /opt/tsh_erp/scripts/run_stock_sync.sh
```

4. **Test the script manually**:
```bash
/opt/tsh_erp/scripts/run_stock_sync.sh
```

5. **Add to crontab**:
```bash
crontab -e

# Add this line:
0 */4 * * * /opt/tsh_erp/scripts/run_stock_sync.sh >> /var/log/tds/stock_sync.log 2>&1
```

6. **Verify cron job**:
```bash
crontab -l
```

### For Local Development

Already configured! The cron job is set up at:
```
0 */4 * * * /Users/khaleelal-mulla/TSH_ERP_Ecosystem/scripts/run_stock_sync.sh
```

---

## Cron Schedule Options

### Every 4 Hours (Current Setup)
```bash
0 */4 * * * /path/to/run_stock_sync.sh
```
Runs at: 00:00, 04:00, 08:00, 12:00, 16:00, 20:00

### Every 6 Hours
```bash
0 */6 * * * /path/to/run_stock_sync.sh
```
Runs at: 00:00, 06:00, 12:00, 18:00

### Twice Daily
```bash
0 2,14 * * * /path/to/run_stock_sync.sh
```
Runs at: 02:00 AM and 02:00 PM

### Daily at 2 AM
```bash
0 2 * * * /path/to/run_stock_sync.sh
```
Runs once daily at 02:00 AM

### Business Hours Only
```bash
0 9-18/3 * * 1-5 /path/to/run_stock_sync.sh
```
Runs every 3 hours from 9 AM to 6 PM, Monday to Friday

---

## Managing Cron Jobs

### View Current Cron Jobs
```bash
crontab -l
```

### Edit Cron Jobs
```bash
crontab -e
```

### Remove All Cron Jobs
```bash
crontab -r
```

### Remove Specific Cron Job
```bash
crontab -l | grep -v "stock_sync" | crontab -
```

### View Cron Logs
```bash
# Local
tail -f logs/tds_stock_sync_cron.log

# Production
tail -f /var/log/tds/stock_sync.log

# System cron log (macOS)
tail -f /var/log/system.log | grep cron

# System cron log (Linux)
tail -f /var/log/syslog | grep CRON
```

---

## Monitoring & Verification

### Check Last Sync Time
```bash
# Via API
curl "https://erp.tsh.sale/api/bff/tds/sync/stock/stats"

# Via database
psql -d tsh_erp -c "SELECT MAX(last_synced) FROM products;"
```

### View Sync History
```bash
# Via API
curl "https://erp.tsh.sale/api/bff/tds/runs?entity_type=product&limit=10"

# View logs
tail -50 logs/tds_stock_sync_cron.log
```

### Check Cron Execution
```bash
# Check if cron is running
ps aux | grep cron

# Check last cron execution (macOS)
log show --predicate 'process == "cron"' --last 1h

# Check last cron execution (Linux)
grep CRON /var/log/syslog | tail -20
```

---

## Troubleshooting

### Cron Job Not Running

**Check if cron service is running**:
```bash
# macOS
sudo launchctl list | grep cron

# Linux
sudo systemctl status cron
```

**Check cron permissions** (macOS):
```bash
# macOS may require Full Disk Access for cron
System Preferences > Security & Privacy > Privacy > Full Disk Access
# Add /usr/sbin/cron
```

**Verify script is executable**:
```bash
ls -la scripts/run_stock_sync.sh
# Should show: -rwxr-xr-x
```

### Backend Not Running

If using API-based sync, ensure backend is running:
```bash
# Check if backend is running
curl http://localhost:8000/api/bff/tds/health

# Start backend if not running
cd /opt/tsh_erp
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
```

### Script Fails

**Check the logs**:
```bash
tail -100 logs/tds_stock_sync_cron.log
```

**Run script manually for debugging**:
```bash
# Run with output
bash -x scripts/run_stock_sync.sh

# Check for errors
scripts/run_stock_sync.sh 2>&1 | tee /tmp/sync_debug.log
```

### Environment Variables Not Loaded

Ensure `.env` file exists and is readable:
```bash
ls -la .env
cat .env | grep -v "PASSWORD\|SECRET"
```

Add to script if needed:
```bash
export POSTGRES_HOST=your_host
export POSTGRES_DB=your_db
# etc.
```

---

## Best Practices

### 1. Log Rotation

Prevent log files from growing too large:

**Create logrotate config** (`/etc/logrotate.d/tds-sync`):
```
/var/log/tds/stock_sync.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    missingok
    create 0644 tsh tsh
}
```

### 2. Email Notifications

Get notified on sync failures:

```bash
# Add MAILTO to crontab
MAILTO=your-email@tsh.sale

0 */4 * * * /path/to/run_stock_sync.sh >> /var/log/tds/stock_sync.log 2>&1
```

### 3. Health Checks

Add a health check after sync:

```bash
#!/bin/bash
/opt/tsh_erp/scripts/run_stock_sync.sh

# Check if sync was successful
if [ $? -eq 0 ]; then
    echo "Sync successful"
else
    echo "Sync failed!" | mail -s "TDS Sync Failed" admin@tsh.sale
fi
```

### 4. Stagger Sync Times

If running multiple sync jobs, stagger them:
```bash
# Stock sync every 4 hours at :00
0 */4 * * * /path/to/run_stock_sync.sh

# Customer sync every 4 hours at :15
15 */4 * * * /path/to/run_customer_sync.sh

# Order sync every 4 hours at :30
30 */4 * * * /path/to/run_order_sync.sh
```

---

## Production Deployment Checklist

- [ ] Backend is running on production server
- [ ] Log directory created (`/var/log/tds/`)
- [ ] Sync script is executable
- [ ] Script tested manually
- [ ] Cron job added to crontab
- [ ] Cron job verified (`crontab -l`)
- [ ] First automatic run completed successfully
- [ ] Log rotation configured
- [ ] Monitoring alerts set up
- [ ] Documentation updated with production URLs

---

## Advanced: Systemd Timer (Alternative to Cron)

For production Linux servers, systemd timers are more modern and reliable.

### Create Service File

`/etc/systemd/system/tds-stock-sync.service`:
```ini
[Unit]
Description=TDS Stock Sync Service
After=network.target postgresql.service

[Service]
Type=oneshot
User=tsh
Group=tsh
WorkingDirectory=/opt/tsh_erp
Environment="PATH=/opt/tsh_erp/.venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/opt/tsh_erp/scripts/run_stock_sync.sh
StandardOutput=append:/var/log/tds/stock_sync.log
StandardError=append:/var/log/tds/stock_sync.log

[Install]
WantedBy=multi-user.target
```

### Create Timer File

`/etc/systemd/system/tds-stock-sync.timer`:
```ini
[Unit]
Description=TDS Stock Sync Timer
Requires=tds-stock-sync.service

[Timer]
OnCalendar=*-*-* 0/4:00:00
Persistent=true
AccuracySec=1m

[Install]
WantedBy=timers.target
```

### Enable and Start

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable timer
sudo systemctl enable tds-stock-sync.timer

# Start timer
sudo systemctl start tds-stock-sync.timer

# Check status
sudo systemctl status tds-stock-sync.timer

# View next run time
sudo systemctl list-timers tds-stock-sync.timer

# Manually trigger
sudo systemctl start tds-stock-sync.service
```

---

## Summary

### Current Setup (Local)
- ✅ Cron job configured
- ✅ Runs every 4 hours
- ✅ Uses API-based sync script
- ✅ Logs to `logs/tds_stock_sync_cron.log`

### Production Deployment
- Use API-based sync via `run_stock_sync.sh`
- Set up on production server at `/opt/tsh_erp`
- Configure logs to `/var/log/tds/`
- Consider systemd timer for better management

### Next Steps
1. Test cron job by waiting for next scheduled run
2. Deploy to production server
3. Set up monitoring and alerts
4. Configure log rotation

---

**Status**: ✅ Ready for Production
**Last Updated**: November 6, 2025
**Schedule**: Every 4 hours (0 */4 * * *)
