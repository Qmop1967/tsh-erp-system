# TSH ERP System - Production Status

**Last Updated**: November 2, 2025, 23:37 UTC
**Status**: ✅ **FULLY OPERATIONAL**

---

## System Overview

The TSH ERP System is currently running in **production** with:
- ✅ Automated CI/CD deployment
- ✅ Blue/green deployment strategy
- ✅ SSL/TLS encryption (HTTPS)
- ✅ Zero-downtime deployments
- ✅ Health monitoring

---

## Production Infrastructure

### Server Details
- **Provider**: DigitalOcean
- **IP Address**: 167.71.39.50
- **Location**: Frankfurt (fra1)
- **Specs**: 2 vCPU, 4GB RAM
- **OS**: Ubuntu 22.04 LTS

### Services Running
| Service | Status | Port | Protocol |
|---------|--------|------|----------|
| TDS Core API (Green) | ✅ Running | 8002 | HTTP (internal) |
| TDS Core API (Blue) | Stopped | 8001 | HTTP (internal) |
| Nginx Reverse Proxy | ✅ Running | 80, 443 | HTTP/HTTPS |
| PostgreSQL Database | ✅ Running | 5432 | TCP (internal) |

---

## Domain Configuration

### DNS Records (All pointing to 167.71.39.50)
| Domain | Type | Target | Status |
|--------|------|--------|--------|
| tsh.sale | A | 167.71.39.50 | ✅ Active |
| www.tsh.sale | A | 167.71.39.50 | ✅ Active |
| erp.tsh.sale | A | 167.71.39.50 | ✅ Active |
| shop.tsh.sale | A | 167.71.39.50 | ✅ Active |
| consumer.tsh.sale | A | 167.71.39.50 | ✅ Active |

### SSL/TLS Certificates
**Certificate Details**:
- ✅ **Issuer**: Let's Encrypt (R13)
- ✅ **Valid From**: October 30, 2025
- ✅ **Valid Until**: January 28, 2026 (90 days)
- ✅ **Auto-Renewal**: Configured

**Domains Covered**:
- ✅ tsh.sale
- ✅ www.tsh.sale
- ✅ erp.tsh.sale
- ✅ shop.tsh.sale
- ⚠️ consumer.tsh.sale (not in current certificate)

**Action Required**: Add `consumer.tsh.sale` to SSL certificate renewal

---

## API Endpoints

### TDS Core API (Backend)
**Base URL**: https://erp.tsh.sale

**Available Endpoints**:
- ✅ `GET /health` - System health check
- ✅ `GET /api/v1/products` - Product management
- ✅ `POST /api/v1/auth/login` - Authentication
- ✅ `GET /api/v1/customers` - Customer management
- ✅ `GET /api/v1/orders` - Order management

**Current Status**:
```json
{
  "status": "healthy",
  "database": {
    "status": "healthy",
    "latency_ms": 3.3,
    "database": "tsh_erp",
    "pool": {
      "size": 20,
      "checked_in": 1,
      "checked_out": 0
    }
  },
  "uptime_seconds": 1254
}
```

### Consumer App (Frontend)
**URLs**:
- https://shop.tsh.sale
- https://consumer.tsh.sale

**Status**: ✅ Static site serving

### ERP Admin (Frontend)
**URL**: https://www.tsh.sale

**Status**: ✅ Static site serving

---

## Database Configuration

### PostgreSQL (Local)
- **Database Name**: tsh_erp
- **Host**: localhost
- **Port**: 5432 (internal only, not exposed)
- **Connection Pool**: 20 connections (max overflow: 10)
- **Status**: ✅ Healthy (3.3ms latency)

### Supabase (Legacy)
- **Status**: ⚠️ Deprecated
- **Migration**: ✅ Complete
- **Note**: All data migrated to local PostgreSQL

---

## CI/CD Pipeline

### GitHub Repository
- **Repository**: https://github.com/Qmop1967/tsh-erp-system
- **Visibility**: PUBLIC (unlimited Actions minutes)
- **Main Branch**: main
- **Workflow**: `.github/workflows/ci-deploy.yml`

### Automated Deployment
**Trigger**: Push to `main` branch

**Process**:
1. ✅ Run tests (frontend, backend, flutter, docker) ~2.5 min
2. ✅ SSH to production server
3. ✅ Execute deployment script (`/opt/tsh_erp/bin/deploy.sh`)
4. ✅ Blue/green deployment switch
5. ✅ Health check validation
6. ✅ Traffic switch via Nginx
7. ✅ Total deployment time: ~6 minutes

**Latest Deployment**:
- **Date**: November 2, 2025, 23:27 UTC
- **Status**: ✅ Success
- **Duration**: 6m27s
- **Instance**: Green (port 8002)

---

## Monitoring & Health

### Current Health Status
```bash
# Check API health
curl https://erp.tsh.sale/health

# Expected response:
{
  "status": "healthy",
  "database": {
    "status": "healthy",
    "latency_ms": 3.3
  },
  "queue": {
    "pending": 0,
    "processing": 0,
    "failed": 0
  }
}
```

### Service Status
```bash
# On production server
ssh root@167.71.39.50

# Check services
systemctl status tsh_erp-green  # Should be active (running)
systemctl status tsh_erp-blue   # May be inactive (stopped)
systemctl status nginx          # Should be active (running)
systemctl status postgresql     # Should be active (running)

# Check ports
ss -tlnp | grep -E ':(8001|8002|80|443)'
```

### Log Locations
```bash
# Application logs
journalctl -u tsh_erp-green -f
journalctl -u tsh_erp-blue -f

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# PostgreSQL logs
tail -f /var/log/postgresql/postgresql-14-main.log
```

---

## Deployment Architecture

### Blue/Green Deployment

```
┌─────────────────────────────────────────────┐
│           Nginx Reverse Proxy               │
│         (Port 80/443 - HTTPS)               │
│                                             │
│  Routes to: tsh_erp_active.conf             │
└──────────────┬──────────────────────────────┘
               │
               ├─ Symlink to either:
               │
               ├─ Green Instance (ACTIVE)
               │  └─ Port 8002
               │     └─ /opt/tsh_erp/venvs/green
               │
               └─ Blue Instance (INACTIVE)
                  └─ Port 8001
                     └─ /opt/tsh_erp/venvs/blue
```

**Current State**: Traffic routed to **Green** instance (port 8002)

### Deployment Flow
1. New code pushed to GitHub
2. GitHub Actions triggers
3. Tests run and pass
4. SSH to production server
5. Deployment script identifies idle instance (Blue)
6. Sync latest code to Blue
7. Install dependencies in Blue venv
8. Start Blue service
9. Run health checks on Blue (30 attempts, 10s each)
10. Switch Nginx to Blue
11. Reload Nginx
12. Stop Green service
13. Blue is now active, Green is idle

**Next deployment**: Will deploy to Green, then switch traffic

---

## Security

### SSL/TLS
- ✅ Let's Encrypt certificates
- ✅ Automatic renewal (acme.sh)
- ✅ TLS 1.2/1.3 enabled
- ✅ HTTP to HTTPS redirect

### Firewall (UFW)
- ✅ Port 22 (SSH) - Restricted to specific IPs
- ✅ Port 80 (HTTP) - Open (redirects to HTTPS)
- ✅ Port 443 (HTTPS) - Open
- ✅ Internal ports (8001, 8002, 5432) - Blocked externally

### Database
- ✅ PostgreSQL on localhost only
- ✅ No external access
- ✅ Connection pooling (20 connections)
- ✅ Password-protected

### API Authentication
- ✅ JWT tokens
- ✅ Role-based access control (RBAC)
- ✅ Password hashing (bcrypt)

---

## Performance

### Current Metrics
- **API Response Time**: < 100ms (avg)
- **Database Latency**: 3.3ms (current)
- **Uptime**: 21 minutes (latest deployment)
- **Memory Usage**: 311.6MB (green instance)
- **Worker Processes**: 5 (uvicorn)

### Optimization
- ✅ Nginx connection pooling (32 keepalive connections)
- ✅ Database connection pooling (20 connections)
- ✅ Static file caching
- ✅ Gzip compression enabled

---

## Backup & Recovery

### Database Backups
**Location**: `/opt/tsh_erp/backups/`

**Schedule**:
- ✅ Automated daily backups (via cron)
- ✅ Retention: 7 days
- ✅ Format: PostgreSQL dump (compressed)

**Manual Backup**:
```bash
ssh root@167.71.39.50
pg_dump -U postgres tsh_erp | gzip > /opt/tsh_erp/backups/manual_$(date +%Y%m%d_%H%M%S).sql.gz
```

### Rollback
If deployment fails or issues occur:

```bash
# SSH to server
ssh root@167.71.39.50

# Rollback to previous instance
cd /opt/tsh_erp
./bin/rollback.sh

# Or manually switch back
sudo ln -sfn /etc/nginx/upstreams/tsh_erp_blue.conf \
    /etc/nginx/upstreams/tsh_erp_active.conf
sudo systemctl reload nginx
sudo systemctl start tsh_erp-blue
```

---

## Known Issues

### Minor Issues
1. ⚠️ `consumer.tsh.sale` not included in SSL certificate
   - **Impact**: Low - domain works with HTTP but shows SSL warning
   - **Fix**: Re-issue certificate with all 5 domains
   - **Priority**: Medium

2. ⚠️ Nginx server name conflicts (warnings)
   - **Impact**: None - cosmetic only
   - **Warnings**: www.tsh.sale, shop.tsh.sale, consumer.tsh.sale
   - **Fix**: Consolidate nginx configurations
   - **Priority**: Low

### Resolved Issues
- ✅ Blue/green deployment script syntax errors (fixed)
- ✅ CI/CD workflow configuration (fixed)
- ✅ Database migration from Supabase (completed)
- ✅ SSL certificate for main domains (active)

---

## Next Steps

### Immediate (High Priority)
1. Add `consumer.tsh.sale` to SSL certificate
2. Test consumer app functionality
3. Set up monitoring alerts (optional)

### Short Term (Medium Priority)
1. Implement database backup verification
2. Add performance monitoring (APM)
3. Configure log rotation
4. Add deployment rollback workflow

### Long Term (Low Priority)
1. Implement staging environment
2. Add deployment notifications (Slack/Discord)
3. Set up metrics dashboard (Grafana)
4. Implement automated testing in CI/CD

---

## Emergency Contacts

### System Access
- **SSH**: `ssh root@167.71.39.50`
- **GitHub**: https://github.com/Qmop1967/tsh-erp-system
- **DigitalOcean**: Dashboard access required

### Quick Commands
```bash
# Check service status
systemctl status tsh_erp-green

# Restart service
systemctl restart tsh_erp-green

# Check logs
journalctl -u tsh_erp-green -n 100 --no-pager

# Check health
curl https://erp.tsh.sale/health

# Emergency stop all
systemctl stop tsh_erp-green tsh_erp-blue

# Emergency start
systemctl start tsh_erp-green
```

---

## Conclusion

The TSH ERP System is **fully operational** in production with:
- ✅ **100% uptime** since latest deployment
- ✅ **Automated deployments** with zero downtime
- ✅ **SSL encryption** for secure communication
- ✅ **Health monitoring** for system reliability
- ✅ **Blue/green deployment** for safe releases

**System is production-ready and serving traffic!** 🚀

---

*Last deployment: November 2, 2025, 23:27 UTC*
*Next certificate renewal: January 28, 2026*
*Document generated: November 2, 2025, 23:37 UTC*
