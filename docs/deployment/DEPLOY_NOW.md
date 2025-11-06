# Deploy Phase 1 Now - Quick Guide

**Status:** Ready to Deploy
**Time Required:** 10-15 minutes
**Risk:** Low (automatic backups, rollback available)

---

## Option 1: Automated Deployment (Recommended)

### From Your Local Machine:

```bash
# 1. Navigate to project directory
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem

# 2. Push to remote repository (if not already done)
git push origin main

# 3. Deploy to VPS (automated script)
ssh root@erp.tsh.sale 'bash -s' < deployment/deploy_phase1.sh
```

**That's it!** The script will:
- ✅ Create automatic backup
- ✅ Pull latest code
- ✅ Install and configure Redis
- ✅ Update environment variables
- ✅ Apply database indexes
- ✅ Restart application
- ✅ Validate deployment

**Time:** ~10 minutes

---

## Option 2: Manual Deployment

If you prefer manual control:

### Step 1: SSH to VPS

```bash
ssh root@erp.tsh.sale
```

### Step 2: Navigate to App Directory

```bash
cd /opt/tsh_erp
```

### Step 3: Pull Latest Code

```bash
git pull origin main
```

### Step 4: Install Redis

```bash
# Install
sudo apt update
sudo apt install -y redis-server

# Start and enable
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify
redis-cli ping  # Should return "PONG"
```

### Step 5: Update Environment

```bash
nano .env.production

# Add these lines at the end:
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Save and exit (Ctrl+X, Y, Enter)
```

### Step 6: Apply Database Indexes

```bash
sudo -u postgres psql -d tsh_erp -f database/performance_indexes.sql
```

### Step 7: Restart Application

```bash
sudo systemctl restart tsh_erp
```

### Step 8: Verify

```bash
# Check status
sudo systemctl status tsh_erp

# Check health
curl http://localhost:8000/health

# Check logs
journalctl -u tsh_erp -n 50
```

**Time:** ~15 minutes

---

## Verification Checklist

After deployment, verify:

### 1. Application Running ✓
```bash
sudo systemctl status tsh_erp
```
Expected: `Active: active (running)`

### 2. Redis Running ✓
```bash
redis-cli ping
```
Expected: `PONG`

### 3. Health Endpoint ✓
```bash
curl https://erp.tsh.sale/health
```
Expected: JSON response with status "healthy"

### 4. API Responding ✓
```bash
curl https://erp.tsh.sale/api/products?limit=5
```
Expected: JSON response with products

### 5. No Errors in Logs ✓
```bash
journalctl -u tsh_erp --since "5 minutes ago" | grep -i error
```
Expected: No critical errors

---

## Monitoring Performance

### Redis Statistics

```bash
# Connection info
redis-cli info stats

# Memory usage
redis-cli info memory

# Real-time monitoring
redis-cli --stat
```

### Application Logs

```bash
# Follow logs in real-time
journalctl -u tsh_erp -f

# Last 100 lines
journalctl -u tsh_erp -n 100

# Errors only
journalctl -u tsh_erp -p err
```

### API Performance

```bash
# Response time test
time curl https://erp.tsh.sale/api/products?limit=100

# Load test (requires apache-bench)
ab -n 100 -c 10 https://erp.tsh.sale/api/products
```

---

## Expected Results

### Before Phase 1:
- API Response: ~150ms
- Database Queries: 200-300ms
- No caching

### After Phase 1:
- API Response: **~105ms** (-30%)
- Cached Responses: **~45ms** (-70%)
- Database Queries: **150-200ms** (-25%)
- Cache Hit Rate: **80%+**

---

## Rollback (If Needed)

If anything goes wrong:

### 1. Quick Rollback

```bash
# On VPS
cd /opt/tsh_erp

# Revert to previous commit
git reset --hard HEAD~1

# Restart application
sudo systemctl restart tsh_erp
```

### 2. Restore Database (If Needed)

```bash
# Find latest backup
ls -lh /opt/backups/tsh_erp/

# Restore (replace TIMESTAMP with actual value)
gunzip < /opt/backups/tsh_erp/backup_TIMESTAMP.sql.gz | sudo -u postgres psql -d tsh_erp
```

### 3. Disable Redis

```bash
# Edit .env.production
nano .env.production

# Change this line:
REDIS_ENABLED=false

# Restart
sudo systemctl restart tsh_erp
```

**Note:** Redis cache has memory fallback, so disabling it won't break the app!

---

## Troubleshooting

### Issue: Redis Not Starting

**Check status:**
```bash
sudo systemctl status redis-server
```

**Check logs:**
```bash
sudo journalctl -u redis-server -n 50
```

**Restart:**
```bash
sudo systemctl restart redis-server
```

### Issue: Application Not Starting

**Check logs:**
```bash
journalctl -u tsh_erp -n 100
```

**Common causes:**
- Database connection issue
- Port already in use
- Configuration error

**Quick fix:**
```bash
# Check if port is in use
sudo lsof -i :8000

# Kill old process if needed
sudo pkill -f "python.*main.py"

# Restart
sudo systemctl restart tsh_erp
```

### Issue: High Memory Usage

**Check memory:**
```bash
free -h
htop  # or top
```

**Redis memory:**
```bash
redis-cli info memory
```

**Reduce Redis memory limit:**
```bash
redis-cli CONFIG SET maxmemory 128mb
```

---

## Post-Deployment Tasks

### Immediate (Next Hour):

1. **Monitor Logs**
   ```bash
   journalctl -u tsh_erp -f
   ```
   Watch for any errors or warnings

2. **Test Critical Endpoints**
   - Health: `/health`
   - Products: `/api/products`
   - Orders: `/api/orders`
   - Authentication: `/api/auth/login`

3. **Check Redis Stats**
   ```bash
   redis-cli info stats
   ```
   Monitor cache hit rate

### Today:

4. **Update Flutter Apps**
   - Follow guide: `mobile/FLUTTER_CONFIG_UPDATE_GUIDE.md`
   - Update all 11 apps to use unified backend
   - Test each app thoroughly

5. **Monitor Performance**
   - API response times
   - Cache hit rate (target: 80%+)
   - Error rates
   - User feedback

### This Week:

6. **Document Any Issues**
   - Note any errors or unexpected behavior
   - Document solutions

7. **Performance Baseline**
   - Record API response times
   - Cache statistics
   - Database query times
   - Use for Phase 2 comparison

---

## Next Steps (Phase 2)

After Phase 1 is deployed and validated:

### Week 2-3: Mobile BFF Expansion
- Implement BFF for Salesperson app
- Extend to Admin app
- Continue with remaining 8 apps
- **Impact:** 72% reduction in API calls

### Week 3-4: Background Jobs
- Install Celery and RabbitMQ
- Move email sending to background
- Move Zoho sync to background
- **Impact:** 30% faster API responses

### Refer to:
- `MOBILE_BFF_ENHANCEMENT_PLAN.md`
- `PERFORMANCE_OPTIMIZATION_GUIDE.md`
- `NEXT_STEPS_ROADMAP.md`

---

## Support

### Documentation:
- Full deployment guide: `PHASE_1_IMPLEMENTATION_COMPLETE.md`
- Implementation status: `IMPLEMENTATION_STATUS.md`
- Architecture details: `MONOLITHIC_TRANSFORMATION_COMPLETE.md`

### Health Checks:
- Backend: `https://erp.tsh.sale/health`
- API Docs: `https://erp.tsh.sale/docs`
- Redis: `redis-cli ping`

### Logs:
- Application: `journalctl -u tsh_erp -f`
- Redis: `journalctl -u redis-server -f`
- Nginx: `tail -f /var/log/nginx/error.log`

---

## Quick Command Reference

```bash
# Application
systemctl status tsh_erp       # Check status
systemctl restart tsh_erp      # Restart
journalctl -u tsh_erp -f       # Follow logs

# Redis
redis-cli ping                 # Test connection
redis-cli info stats           # Statistics
redis-cli monitor              # Monitor commands

# Database
sudo -u postgres psql -d tsh_erp -c "SELECT version();"

# Health Checks
curl https://erp.tsh.sale/health
curl https://erp.tsh.sale/api/products?limit=5

# Performance Test
time curl https://erp.tsh.sale/api/products?limit=100
```

---

## Deployment Checklist

- [ ] Code pushed to git
- [ ] Backup created automatically
- [ ] Latest code pulled
- [ ] Redis installed and running
- [ ] Environment variables updated
- [ ] Database indexes applied
- [ ] Application restarted
- [ ] Health endpoint responding
- [ ] API endpoints working
- [ ] No errors in logs
- [ ] Redis responding to PING
- [ ] Performance baseline recorded

---

**Status:** Ready to Deploy
**Risk Level:** Low
**Expected Duration:** 10-15 minutes
**Expected Impact:** 30-70% performance improvement

**Deploy now with:**
```bash
ssh root@erp.tsh.sale 'bash -s' < deployment/deploy_phase1.sh
```

---

**Created:** November 5, 2025
**Version:** 1.0
**Last Updated:** November 5, 2025

**Made with ❤️ for TSH Business Operations**
