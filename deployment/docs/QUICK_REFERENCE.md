# TSH ERP CI/CD - Quick Reference

## 🚀 Quick Commands

### Deployment
```bash
# Deploy from main branch
bash /opt/tsh_erp/bin/deploy.sh main

# Deploy from specific branch
bash /opt/tsh_erp/bin/deploy.sh develop
```

### Rollback
```bash
# Instant rollback to previous version
bash /opt/tsh_erp/bin/rollback.sh
```

### Health Checks
```bash
# Check service health
curl http://localhost:8001/ready  # Blue
curl http://localhost:8002/ready  # Green

# Detailed health
curl http://localhost:8001/health
```

### Service Management
```bash
# Status
systemctl status tsh_erp-blue
systemctl status tsh_erp-green

# Restart
sudo systemctl restart tsh_erp-blue
sudo systemctl restart tsh_erp-green

# Logs
journalctl -u tsh_erp-blue -f
journalctl -u tsh_erp-green -f
```

### Nginx
```bash
# Check active upstream
readlink -f /etc/nginx/upstreams/tsh_erp_active.conf

# Test configuration
sudo nginx -t

# Reload
sudo systemctl reload nginx

# Manually switch
bash /opt/tsh_erp/bin/switch_upstream.sh blue
```

### Database
```bash
# Manual backup
pg_dump --file=/opt/backups/manual_$(date +%F).dump --format=custom "$DATABASE_URL"

# List backups
ls -lh /opt/backups/

# Restore
pg_restore --dbname=tsh_erp_production /opt/backups/backup.dump
```

### Logs
```bash
# Deployment logs
tail -f /opt/tsh_erp/shared/logs/api/deploy_*.log

# Application logs (last 100 lines)
journalctl -u tsh_erp-blue -n 100

# Nginx access logs
tail -f /var/log/nginx/tsh_erp_access.log

# Nginx error logs
tail -f /var/log/nginx/tsh_erp_error.log
```

## 📊 Status Indicators

### Active Color
```bash
readlink /etc/nginx/upstreams/tsh_erp_active.conf
# Output: /etc/nginx/upstreams/tsh_erp_blue.conf  → Blue is active
# Output: /etc/nginx/upstreams/tsh_erp_green.conf → Green is active
```

### Service Status
```bash
systemctl is-active tsh_erp-blue   # active/inactive
systemctl is-active tsh_erp-green  # active/inactive
```

### Port Check
```bash
lsof -i :8001  # Blue
lsof -i :8002  # Green
```

## 🔥 Emergency Commands

### Stop Everything
```bash
sudo systemctl stop tsh_erp-blue tsh_erp-green
```

### Start Fresh
```bash
# Stop both
sudo systemctl stop tsh_erp-blue tsh_erp-green

# Start blue
sudo systemctl start tsh_erp-blue

# Wait and check health
sleep 5 && curl http://localhost:8001/ready

# Switch to blue
bash /opt/tsh_erp/bin/switch_upstream.sh blue
```

### Kill Stuck Process
```bash
# Find PID
lsof -t -i :8001

# Kill
kill -9 $(lsof -t -i :8001)
```

## 📍 File Locations

### Configuration
- Nginx config: `/etc/nginx/sites-available/tsh_erp.conf`
- Upstreams: `/etc/nginx/upstreams/`
- Systemd services: `/etc/systemd/system/tsh_erp-*.service`
- Environment: `/opt/tsh_erp/shared/env/prod.env`

### Code
- Blue release: `/opt/tsh_erp/releases/blue`
- Green release: `/opt/tsh_erp/releases/green`
- Blue venv: `/opt/tsh_erp/venvs/blue`
- Green venv: `/opt/tsh_erp/venvs/green`

### Logs & Backups
- Deploy logs: `/opt/tsh_erp/shared/logs/api/`
- DB backups: `/opt/backups/`
- Nginx logs: `/var/log/nginx/`

### Scripts
- Deploy: `/opt/tsh_erp/bin/deploy.sh`
- Rollback: `/opt/tsh_erp/bin/rollback.sh`
- Health check: `/opt/tsh_erp/bin/healthcheck.sh`
- Switch: `/opt/tsh_erp/bin/switch_upstream.sh`

## 🎯 Common Scenarios

### Scenario 1: Deployment Stuck
```bash
# Check what's running
ps aux | grep uvicorn

# Check logs
tail -50 /opt/tsh_erp/shared/logs/api/deploy_*.log

# If needed, kill and restart
pkill -f uvicorn
bash /opt/tsh_erp/bin/deploy.sh main
```

### Scenario 2: Website Down
```bash
# Check Nginx
sudo systemctl status nginx

# Check active service
systemctl status tsh_erp-blue tsh_erp-green

# Check logs
journalctl -u nginx -n 50
journalctl -u tsh_erp-blue -n 50
```

### Scenario 3: Database Connection Error
```bash
# Test database connection
psql "$DATABASE_URL" -c "SELECT 1"

# Check environment
cat /opt/tsh_erp/shared/env/prod.env | grep DATABASE_URL

# Restart service
sudo systemctl restart tsh_erp-blue
```

### Scenario 4: Deployment Failed, Need Rollback
```bash
# Immediate rollback
bash /opt/tsh_erp/bin/rollback.sh

# Verify
curl http://your-domain.com/health
```

## 📱 Monitoring

### Quick Health Check Script
```bash
#!/bin/bash
echo "=== TSH ERP Health Check ==="
echo "Active: $(readlink /etc/nginx/upstreams/tsh_erp_active.conf)"
echo "Blue: $(systemctl is-active tsh_erp-blue)"
echo "Green: $(systemctl is-active tsh_erp-green)"
echo "Nginx: $(systemctl is-active nginx)"
curl -s http://localhost/health | python3 -m json.tool
```

### Watch Logs Live
```bash
# All services
sudo journalctl -f -u tsh_erp-blue -u tsh_erp-green -u nginx

# Deployment only
tail -f /opt/tsh_erp/shared/logs/api/deploy_*.log
```

## 🔐 Security

### Update SSH Keys
```bash
# Add new key
cat ~/.ssh/new_key.pub >> ~/.ssh/authorized_keys

# Remove old key
sed -i '/old_key_content/d' ~/.ssh/authorized_keys
```

### Check Open Ports
```bash
sudo netstat -tlnp
# Should see: 22 (SSH), 80 (HTTP), 443 (HTTPS), 8001 (Blue), 8002 (Green)
```

### Firewall Status
```bash
sudo ufw status
```

---

**Pro Tip**: Bookmark this page for quick access during operations! 🚀
