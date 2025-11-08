# TSH ERP System - Quick Reference Card

**Production URL:** https://erp.tsh.sale
**VPS IP:** 167.71.39.50
**SSH Alias:** `ssh tsh-vps`

---

## 🚀 Quick Commands

### Service Management
```bash
# SSH to VPS
ssh tsh-vps

# Check all services
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose ps"

# View logs (all services)
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose logs -f --tail 100"

# View logs (specific service)
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose logs app -f"

# Restart all services
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose restart"

# Restart specific service
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose restart app"

# Stop all services
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose down"

# Start all services
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose up -d"
```

### Health Checks
```bash
# API Health Check
curl -s https://erp.tsh.sale/health | python3 -m json.tool

# Check Docker Stats
ssh tsh-vps "docker stats --no-stream"

# Check Disk Space
ssh tsh-vps "df -h /"

# Check Memory
ssh tsh-vps "free -h"
```

### Deployment Updates
```bash
# 1. Upload new code
rsync -avz --progress --exclude '.git' --exclude '.venv' \
  --exclude '__pycache__' --exclude 'node_modules' \
  /Users/khaleelal-mulla/TSH_ERP_Ecosystem/ tsh-vps:/opt/tsh_erp_docker/

# 2. Rebuild and restart app
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose build app && docker compose restart app"

# 3. Verify deployment
curl -s https://erp.tsh.sale/health
```

### SSL Certificate
```bash
# Check certificate status
ssh tsh-vps "certbot certificates | grep -A5 'erp.tsh.sale-0001'"

# Manual renewal (if needed)
ssh tsh-vps "certbot renew --force-renewal"

# View auto-renewal cron
ssh tsh-vps "crontab -l | grep certbot"
```

### Database Operations
```bash
# Connect to PostgreSQL
ssh tsh-vps "docker compose -f /opt/tsh_erp_docker/docker-compose.yml exec postgres psql -U tsh_admin -d tsh_erp"

# Create backup
ssh tsh-vps "mkdir -p /opt/tsh_erp_backups && docker compose -f /opt/tsh_erp_docker/docker-compose.yml exec -T postgres pg_dump -U tsh_admin tsh_erp > /opt/tsh_erp_backups/backup_$(date +%Y%m%d_%H%M%S).sql"

# Download backup
scp tsh-vps:/opt/tsh_erp_backups/backup_*.sql ~/Backups/
```

### Troubleshooting
```bash
# Check for errors in logs
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose logs app --tail 100 | grep -i error"

# Check nginx logs
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose logs nginx --tail 50"

# Test nginx config
ssh tsh-vps "docker compose -f /opt/tsh_erp_docker/docker-compose.yml exec nginx nginx -t"

# Check PostgreSQL connection
ssh tsh-vps "docker compose -f /opt/tsh_erp_docker/docker-compose.yml exec postgres pg_isready -U tsh_admin"

# Rebuild app (no cache)
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose build --no-cache app"

# Clean Docker system
ssh tsh-vps "docker system prune -af && docker volume prune -f"
```

---

## 🌐 Production Endpoints

| Endpoint | URL | Status |
|----------|-----|--------|
| Health Check | https://erp.tsh.sale/health | ✅ 200 |
| API Docs | https://erp.tsh.sale/docs | ✅ 200 |
| ReDoc | https://erp.tsh.sale/redoc | ✅ 200 |
| OpenAPI Schema | https://erp.tsh.sale/openapi.json | ✅ 200 |

---

## 📊 System Status

### Current Services
- **FastAPI App:** HEALTHY (4 Uvicorn workers)
- **PostgreSQL 15:** HEALTHY
- **Redis 7:** HEALTHY
- **Nginx:** RUNNING (HTTPS enabled)

### SSL Certificate
- **Provider:** Let's Encrypt
- **Domain:** erp.tsh.sale
- **Expires:** February 5, 2026 (89 days)
- **Auto-Renewal:** Daily at 3 AM

### Resources
- **Disk Usage:** 58GB / 78GB (75%)
- **Free Space:** 21GB
- **VPS Location:** DigitalOcean

---

## 🚨 Emergency Procedures

### Complete System Restart
```bash
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose down && docker compose up -d"
```

### Emergency Backup
```bash
ssh tsh-vps "cd /opt && tar -czf tsh_erp_emergency_$(date +%Y%m%d_%H%M%S).tar.gz tsh_erp_docker/"
```

### View Recent Errors
```bash
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose logs --tail 200 | grep -i -E '(error|exception|failed)'"
```

---

## 📚 Documentation Files

- **PRODUCTION_OPERATIONS.md** - Comprehensive operations guide
- **DEPLOYMENT_COMPLETE.md** - Deployment completion report
- **DEPLOYMENT.md** - Deployment procedures
- **THIS FILE** - Quick reference card

---

## 📞 Support

- **Administrator:** Khaleel Al-Mulla
- **Email:** kha93ahm@gmail.com
- **VPS Provider:** DigitalOcean
- **Domain:** Namecheap (tsh.sale)

---

**Last Updated:** November 7, 2025
**System Version:** 1.0.0
**Status:** Production Ready ✅
