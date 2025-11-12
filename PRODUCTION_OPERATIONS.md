# TSH ERP System - Production Operations Guide

**Deployment Date:** November 7, 2025
**Status:** ✅ Production Ready
**URL:** https://erp.tsh.sale

---

## 🚀 Quick Reference

### System Access
- **Production Site**: https://erp.tsh.sale
- **API Documentation**: https://erp.tsh.sale/docs
- **Health Check**: https://erp.tsh.sale/health
- **VPS IP**: 167.71.39.50
- **SSH Access**: `ssh tsh-vps` (alias configured)

### Service Status Check
```bash
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose ps"
```

---

## 📋 Common Operations

### View Logs
```bash
# All services
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose logs -f --tail 100"

# Specific service
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose logs app -f --tail 50"
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose logs nginx -f --tail 50"
```

### Restart Services
```bash
# Restart all
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose restart"

# Restart specific service
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose restart app"
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose restart nginx"
```

### Stop/Start System
```bash
# Stop all services
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose down"

# Start all services
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose up -d"
```

---

## 🔄 Deployment Updates

### Deploy New Code
```bash
# 1. Build locally (optional - test first)
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem
python -c "import sys; sys.path.insert(0, '.'); import app.main"

# 2. Upload to VPS
rsync -avz --progress --exclude '.git' --exclude '.venv' \
  --exclude '__pycache__' --exclude 'node_modules' \
  /Users/khaleelal-mulla/TSH_ERP_Ecosystem/ tsh-vps:/opt/tsh_erp_docker/

# 3. Rebuild and restart
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose build app && docker compose restart app"

# 4. Verify
curl -s https://erp.tsh.sale/health
```

### Rollback to Previous Version
```bash
# Check available images
ssh tsh-vps "docker images | grep tsh_erp"

# Restore from backup
ssh tsh-vps "cd /opt && mv tsh_erp_docker tsh_erp_docker_new && mv tsh_erp_docker_backup tsh_erp_docker"
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose up -d"
```

---

## 🔒 SSL Certificate Management

### Certificate Info
- **Domain**: erp.tsh.sale
- **Certificate Path**: `/etc/letsencrypt/live/erp.tsh.sale-0001/`
- **Expires**: February 5, 2026
- **Auto-Renewal**: Configured (daily at 3 AM)

### Manual Certificate Renewal
```bash
ssh tsh-vps "
  cd /opt/tsh_erp_docker && \
  docker compose stop nginx && \
  certbot renew --force-renewal && \
  cp /etc/letsencrypt/live/erp.tsh.sale-0001/*.pem /opt/tsh_erp_docker/nginx/ssl/ && \
  docker compose start nginx
"
```

### Check Certificate Expiry
```bash
ssh tsh-vps "certbot certificates"
```

---

## 🗄️ Database Operations

### Connect to Database
```bash
ssh tsh-vps "docker compose -f /opt/tsh_erp_docker/docker-compose.yml exec postgres psql -U tsh_admin -d tsh_erp"
```

### Database Backup
```bash
# Create backup
ssh tsh-vps "
  mkdir -p /opt/tsh_erp_backups && \
  docker compose -f /opt/tsh_erp_docker/docker-compose.yml exec -T postgres \
    pg_dump -U tsh_admin tsh_erp > /opt/tsh_erp_backups/tsh_erp_$(date +%Y%m%d_%H%M%S).sql
"

# Download backup
scp tsh-vps:/opt/tsh_erp_backups/tsh_erp_*.sql ~/Backups/
```

### Database Restore
```bash
# Upload backup
scp ~/Backups/tsh_erp_20251107.sql tsh-vps:/tmp/

# Restore
ssh tsh-vps "
  docker compose -f /opt/tsh_erp_docker/docker-compose.yml exec -T postgres \
    psql -U tsh_admin -d tsh_erp < /tmp/tsh_erp_20251107.sql
"
```

---

## 📊 Monitoring & Health

### Health Check Endpoints
```bash
# API Health
curl -s https://erp.tsh.sale/health | python3 -m json.tool

# Service Health
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose ps"
```

### Resource Usage
```bash
# Container stats
ssh tsh-vps "docker stats --no-stream"

# Disk usage
ssh tsh-vps "df -h"

# Memory usage
ssh tsh-vps "free -h"
```

### Check Logs for Errors
```bash
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose logs app --tail 100 | grep -i error"
```

---

## 🔧 Troubleshooting

### App Won't Start
```bash
# Check logs
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose logs app --tail 100"

# Check for import errors
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose exec app python -c 'import app.main'"

# Rebuild image
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose build --no-cache app"
```

### Nginx Issues
```bash
# Check nginx logs
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose logs nginx --tail 50"

# Test nginx config
ssh tsh-vps "docker compose -f /opt/tsh_erp_docker/docker-compose.yml exec nginx nginx -t"

# Restart nginx
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose restart nginx"
```

### Database Connection Issues
```bash
# Check postgres logs
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose logs postgres --tail 50"

# Test connection
ssh tsh-vps "docker compose -f /opt/tsh_erp_docker/docker-compose.yml exec postgres pg_isready -U tsh_admin"
```

### Out of Disk Space
```bash
# Check disk usage
ssh tsh-vps "df -h"

# Clean Docker
ssh tsh-vps "docker system prune -af && docker volume prune -f"

# Clean old logs
ssh tsh-vps "cd /opt/tsh_erp_docker/logs && find . -name '*.log' -mtime +7 -delete"
```

---

## 🔐 Security

### Update System Packages
```bash
ssh tsh-vps "apt update && apt upgrade -y && apt autoremove -y"
```

### Check Firewall Status
```bash
ssh tsh-vps "ufw status"
```

### Review Access Logs
```bash
ssh tsh-vps "tail -100 /opt/tsh_erp_docker/logs/nginx/access.log"
```

---

## 📈 Performance Optimization

### Scale Uvicorn Workers
Edit `/opt/tsh_erp_docker/docker-compose.yml`:
```yaml
command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 8
```

### Add Database Connection Pooling
Already configured in `app/db/database.py`

### Enable Redis Caching
Redis is already running and available at `redis:6379`

---

## 🚨 Emergency Procedures

### Complete System Restart
```bash
ssh tsh-vps "cd /opt/tsh_erp_docker && docker compose down && docker compose up -d"
```

### Emergency Backup
```bash
# Quick backup of everything
ssh tsh-vps "
  cd /opt && \
  tar -czf tsh_erp_backup_$(date +%Y%m%d_%H%M%S).tar.gz tsh_erp_docker/ && \
  ls -lh tsh_erp_backup_*.tar.gz
"
```

### Disaster Recovery
```bash
# If VPS is completely down, redeploy:
1. Get new VPS with same IP or update DNS
2. Install Docker & Docker Compose
3. Restore from backup
4. Get new SSL certificate
5. Start services
```

---

## 📝 Important Files & Locations

### On VPS
- **Application**: `/opt/tsh_erp_docker/`
- **SSL Certificates**: `/etc/letsencrypt/live/erp.tsh.sale-0001/`
- **Docker Volumes**: `/opt/tsh_erp_docker/nginx/ssl/`
- **Logs**: `/opt/tsh_erp_docker/logs/`
- **Backups**: `/opt/tsh_erp_backups/`

### On Local Machine
- **Source Code**: `/Users/khaleelal-mulla/TSH_ERP_Ecosystem/`
- **Deployment Guides**: `DEPLOYMENT.md`, `PRODUCTION_OPERATIONS.md`
- **Docker Config**: `docker-compose.yml`, `Dockerfile`

---

## 🎯 Performance Benchmarks

### Expected Response Times
- Health check: < 100ms
- API endpoints: < 500ms
- Database queries: < 200ms

### Resource Limits
- App CPU: ~50% per worker
- App Memory: ~200MB per worker
- PostgreSQL: ~500MB
- Redis: ~100MB
- Nginx: ~50MB

---

## 📞 Support Contacts

- **System Administrator**: Khaleel Al-Mulla (kha93ahm@gmail.com)
- **VPS Provider**: DigitalOcean
- **Domain Registrar**: Namecheap (tsh.sale)

---

## ✅ Deployment Checklist

- [x] All services running
- [x] SSL certificate installed
- [x] Auto-renewal configured
- [x] Health checks passing
- [x] Database operational
- [x] Logs accessible
- [x] Backups configured
- [x] Monitoring setup
- [x] Documentation complete

---

**Last Updated:** November 7, 2025
**System Version:** 1.0.0
**Status:** Production Ready ✅
