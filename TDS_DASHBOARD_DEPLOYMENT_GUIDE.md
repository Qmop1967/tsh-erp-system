# TDS Admin Dashboard - Deployment Guide

**Target Server**: VPS at 167.71.39.50
**Date**: 2025-11-09
**Status**: Ready for Deployment

---

## Pre-Deployment Checklist

### ✅ Completed Requirements

1. **Frontend Dashboard** - Next.js 15 application built and tested
2. **Backend Socket.IO** - Real-time server module implemented
3. **Docker Configuration** - Multi-stage Dockerfile and docker-compose service
4. **Flutter Consumer App** - Verified to display consumer price list
5. **All Pages Built**:
   - Executive Dashboard (Overview)
   - Sync Management
   - Statistics & Comparison
   - Alerts & Notifications
   - Settings
6. **Git Commits** - All changes committed locally

### ⚠️ Pre-Deployment Steps

Before deployment, ensure:

1. **Backend API is Running** on VPS (port 8000)
2. **PostgreSQL Database** is accessible
3. **Redis Cache** is running
4. **Environment Variables** are configured

---

## Deployment Methods

### Method 1: Automated Deployment Script (Recommended)

```bash
# From your local machine, sync code to VPS
rsync -avz --exclude 'node_modules' \
  /Users/khaleelal-mulla/TSH_ERP_Ecosystem/apps/tds_admin_dashboard/ \
  root@167.71.39.50:/root/TSH_ERP_Ecosystem/apps/tds_admin_dashboard/

# SSH into VPS
ssh root@167.71.39.50

# Navigate to project root
cd /root/TSH_ERP_Ecosystem

# Run deployment script
cd apps/tds_admin_dashboard
chmod +x deploy.sh
./deploy.sh
```

### Method 2: Manual Docker Deployment

```bash
# SSH into VPS
ssh root@167.71.39.50

# Navigate to project root
cd /root/TSH_ERP_Ecosystem

# Pull latest code (if using git)
git pull origin develop

# Build the dashboard
docker-compose build tds_admin_dashboard

# Start the service
docker-compose --profile dashboard up -d tds_admin_dashboard

# View logs
docker-compose logs -f tds_admin_dashboard
```

### Method 3: Local Build + Deploy

```bash
# Build locally (faster on powerful machines)
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem/apps/tds_admin_dashboard
docker build -t tds-admin-dashboard:latest .

# Save image
docker save tds-admin-dashboard:latest | gzip > tds-dashboard.tar.gz

# Copy to VPS
scp tds-dashboard.tar.gz root@167.71.39.50:/tmp/

# SSH and load
ssh root@167.71.39.50
docker load < /tmp/tds-dashboard.tar.gz
cd /root/TSH_ERP_Ecosystem
docker-compose --profile dashboard up -d tds_admin_dashboard
```

---

## Environment Configuration

### Production Environment Variables

Create or update `.env.production` on VPS:

```env
# TDS Admin Dashboard
NEXT_PUBLIC_API_URL=https://erp.tsh.sale
NEXT_PUBLIC_SOCKET_URL=wss://erp.tsh.sale
TDS_DASHBOARD_PORT=3000

# Backend API
APP_PORT=8000
DATABASE_URL=postgresql://tsh_admin:changeme@tsh_postgres:5432/tsh_erp
REDIS_URL=redis://tsh_redis:6379/0

# Docker
VERSION=latest
ENVIRONMENT=production
```

---

## Nginx Reverse Proxy Configuration

Update Nginx configuration to proxy the dashboard:

```nginx
# /etc/nginx/sites-available/tsh-erp

upstream tds_dashboard {
    server localhost:3000;
}

upstream tsh_backend {
    server localhost:8000;
}

server {
    listen 80;
    listen 443 ssl http2;
    server_name erp.tsh.sale;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/erp.tsh.sale.crt;
    ssl_certificate_key /etc/nginx/ssl/erp.tsh.sale.key;

    # TDS Admin Dashboard
    location /tds-admin {
        proxy_pass http://tds_dashboard;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api {
        proxy_pass http://tsh_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Socket.IO WebSocket
    location /socket.io {
        proxy_pass http://tsh_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # Health check
    location /health {
        proxy_pass http://tsh_backend;
    }
}
```

Apply Nginx configuration:

```bash
# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

---

## Post-Deployment Verification

### 1. Check Container Status

```bash
docker-compose ps tds_admin_dashboard
```

Expected output:
```
NAME                  STATUS         PORTS
tds_admin_dashboard   Up (healthy)   0.0.0.0:3000->3000/tcp
```

### 2. Check Health

```bash
# Direct container health check
curl http://localhost:3000

# Through Nginx (if configured)
curl https://erp.tsh.sale/tds-admin
```

### 3. Check Logs

```bash
# View real-time logs
docker-compose logs -f tds_admin_dashboard

# Last 100 lines
docker-compose logs --tail=100 tds_admin_dashboard
```

### 4. Test Socket.IO Connection

```bash
# Check Socket.IO endpoint
curl -i http://localhost:8000/socket.io/?EIO=4&transport=polling
```

Expected: HTTP 200 with Socket.IO handshake data

### 5. Test API Endpoints

```bash
# Test dashboard API
curl http://localhost:8000/api/bff/tds/dashboard/complete

# Test health
curl http://localhost:8000/api/bff/tds/health/complete
```

### 6. Browser Testing

1. Open: `https://erp.tsh.sale/tds-admin` (or `http://167.71.39.50:3000`)
2. Verify:
   - Dashboard loads without errors
   - KPI cards show data
   - Navigation works
   - Socket.IO connects (check browser console)
   - Real-time updates work

---

## Troubleshooting

### Dashboard Container Won't Start

```bash
# Check logs
docker-compose logs tds_admin_dashboard

# Common issues:
# 1. Port 3000 already in use
sudo lsof -i:3000
sudo kill -9 <PID>

# 2. Missing environment variables
docker-compose config | grep -A 10 tds_admin_dashboard

# 3. Build errors
docker-compose build --no-cache tds_admin_dashboard
```

### Socket.IO Not Connecting

```bash
# Check if Socket.IO server is running in backend
docker-compose logs app | grep -i socket

# Check CORS configuration
# Ensure NEXT_PUBLIC_SOCKET_URL is correct

# Test WebSocket connection
wscat -c ws://localhost:8000/socket.io/?EIO=4&transport=websocket
```

### API Calls Failing

```bash
# Check API URL
echo $NEXT_PUBLIC_API_URL

# Test backend is accessible
curl http://localhost:8000/health

# Check CORS headers
curl -I http://localhost:8000/api/bff/tds/dashboard/complete
```

### Build Failures

```bash
# Clear Docker cache
docker system prune -a

# Rebuild with no cache
docker-compose build --no-cache tds_admin_dashboard

# Check disk space
df -h
```

---

## Monitoring & Maintenance

### Check Resource Usage

```bash
# Container stats
docker stats tds_admin_dashboard

# Disk usage
docker system df

# Logs size
du -sh /var/lib/docker/containers/*
```

### Automatic Restarts

The dashboard is configured with `restart: always` in docker-compose.yml, so it will:
- Auto-restart on failure
- Start on system boot
- Recover from crashes

### Backup & Rollback

```bash
# Tag current version before update
docker tag tds-admin-dashboard:latest tds-admin-dashboard:backup-$(date +%Y%m%d)

# Rollback if needed
docker-compose down tds_admin_dashboard
docker tag tds-admin-dashboard:backup-20251109 tds-admin-dashboard:latest
docker-compose up -d tds_admin_dashboard
```

---

## Update Procedure

### Minor Updates (Code Changes)

```bash
# 1. Pull latest code
git pull origin develop

# 2. Rebuild
docker-compose build tds_admin_dashboard

# 3. Restart
docker-compose up -d tds_admin_dashboard

# 4. Verify
docker-compose logs -f tds_admin_dashboard
```

### Major Updates (Dependencies)

```bash
# 1. Stop current version
docker-compose stop tds_admin_dashboard

# 2. Backup current image
docker tag tds-admin-dashboard:latest tds-admin-dashboard:pre-update

# 3. Pull and rebuild
git pull origin develop
docker-compose build --no-cache tds_admin_dashboard

# 4. Start and test
docker-compose up -d tds_admin_dashboard
docker-compose logs -f tds_admin_dashboard
```

---

## Security Considerations

### 1. Enable HTTPS

Ensure SSL/TLS is configured in Nginx:
- Use Let's Encrypt certificates
- Redirect HTTP to HTTPS
- Enable HSTS headers

### 2. JWT Authentication

The dashboard requires JWT tokens for:
- API requests
- Socket.IO connections

Ensure tokens are:
- Securely generated
- Properly validated
- Refreshed before expiry

### 3. CORS Configuration

Update CORS to allow only your domains:

```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://erp.tsh.sale",
        "https://www.erp.tsh.sale",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. Rate Limiting

Nginx rate limiting is already configured. Monitor for abuse:

```bash
# Check Nginx error logs for rate limit hits
sudo tail -f /var/log/nginx/error.log | grep limiting
```

---

## Performance Optimization

### 1. Enable Gzip Compression

```nginx
# In nginx.conf
gzip on;
gzip_vary on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
gzip_comp_level 6;
```

### 2. Cache Static Assets

```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 3. Enable HTTP/2

Already configured in the Nginx template above with `http2` directive.

---

## Success Criteria

Dashboard deployment is successful when:

✅ Container status is "healthy"
✅ Dashboard accessible at https://erp.tsh.sale/tds-admin
✅ All pages load without errors
✅ KPI cards display real data
✅ Socket.IO connects successfully
✅ Real-time updates work
✅ Navigation functions properly
✅ No errors in browser console
✅ API calls return data
✅ Performance is acceptable (< 2s load time)

---

## Support & Documentation

- **Dashboard README**: `/apps/tds_admin_dashboard/README.md`
- **Implementation Summary**: `/TDS_DASHBOARD_IMPLEMENTATION_SUMMARY.md`
- **API Documentation**: Check BFF router at `/app/bff/routers/tds.py`
- **Socket.IO Server**: `/app/tds/websocket/`

---

**Generated with Claude Code** | TSH ERP Ecosystem v3.0.0
