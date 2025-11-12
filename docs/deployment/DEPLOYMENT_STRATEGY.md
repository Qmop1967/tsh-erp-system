# TSH ERP Deployment Strategy

## Overview

This document defines the **official deployment strategy** for TSH ERP across different environments. We use a **hybrid approach**: Docker for development and testing, Systemd for production VPS.

---

## Deployment Matrix

| Environment | Method | Why | Documentation |
|------------|--------|-----|---------------|
| **Local Development** | Docker Compose | Fast setup, consistent environment, hot-reload | [Docker Development Guide](../docker/README.md) |
| **CI/CD Testing** | Docker | Isolated, reproducible test environment | [CI/CD Workflows](../../.github/workflows/) |
| **Staging/Demo** | Docker Compose | Easy spin-up/teardown, quick deployments | [Docker README](../docker/README.md) |
| **Production VPS** | Systemd | Lower overhead, direct control, proven stability | [Production Deployment](../../scripts/deploy_production.sh) |

---

## Rationale

### Why Docker for Development?

✅ **Benefits:**
- **Fast onboarding**: New developers up and running in minutes
- **Consistency**: "Works on my machine" → "Works everywhere"
- **Isolation**: No conflicts with host system
- **Hot reload**: Code changes reflect immediately
- **Complete stack**: PostgreSQL, Redis, App, Nginx all managed together

❌ **Drawbacks:**
- Slight performance overhead on macOS/Windows (Docker Desktop)
- Additional layer of complexity for simple changes

**Verdict**: Benefits far outweigh drawbacks for development

---

### Why Systemd for Production?

✅ **Benefits:**
- **Performance**: Direct execution, no containerization overhead
- **Simplicity**: Fewer moving parts in production
- **Proven**: Already working reliably on VPS
- **Resource efficiency**: Lower memory footprint
- **Direct access**: Easier debugging and log access
- **Native integration**: Works with existing VPS infrastructure

❌ **Drawbacks:**
- Manual dependency management
- Environment-specific configuration
- Less portable than containers

**Verdict**: For a single VPS deployment, systemd is simpler and more efficient

---

## Environment-Specific Guides

### 1. Local Development (Docker)

**Setup:**
```bash
# Clone repository
git clone <repo-url>
cd TSH_ERP_Ecosystem

# Create environment file
cp config/env.example .env.dev
# Edit .env.dev with your settings

# Start all services
docker compose --profile core --profile dev \
  -f docker-compose.yml \
  -f docker-compose.dev.yml \
  up -d

# View logs
docker compose logs -f app

# Run migrations
docker compose exec app alembic upgrade head

# Access application
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
# PgAdmin: http://localhost:5050
```

**Features:**
- Hot reload enabled (code changes auto-refresh)
- PostgreSQL + PgAdmin for database management
- Redis for caching
- Volume mounts for logs and uploads
- No need to install Python, PostgreSQL, or Redis locally

**Documentation**: [docs/docker/README.md](../docker/README.md)

---

### 2. CI/CD Testing (Docker)

**Purpose**: Automated testing on every push/PR

**Process:**
1. GitHub Actions triggers on push to `main` or `develop`
2. Docker containers built and started
3. Tests run inside containers
4. Results reported back to PR
5. Containers destroyed

**Configuration**: [.github/workflows/ci-deploy.yml](../../.github/workflows/ci-deploy.yml)

**Key Points:**
- Uses Docker for consistent test environment
- No dependency on external services
- Tests run in isolation
- Fast feedback loop

---

### 3. Staging/Demo (Docker - Optional)

**Use Case**: Temporary environments for demos or testing

**Setup:**
```bash
# On staging server
git clone <repo-url>
cd TSH_ERP_Ecosystem

# Configure environment
cp config/env.example .env.staging
vim .env.staging

# Start with production-like settings
APP_ENV_FILE=.env.staging \
docker compose --profile core --profile proxy up -d

# Setup SSL (if needed)
# See docs/docker/SSL_SETUP.md
```

**Benefits:**
- Quick deployment and teardown
- Isolated from production
- Can run multiple staging environments on same server
- Easy rollback

---

### 4. Production VPS (Systemd)

**Current Setup:**
- VPS: erp.tsh.sale
- OS: Ubuntu 22.04 LTS
- Service: tsh-erp.service (systemd)
- Database: PostgreSQL 15 (native installation)
- Cache: Redis 7 (native installation)
- Web Server: Nginx (native, not Docker)

**Deployment Process:**

```bash
# SSH into production server
ssh root@erp.tsh.sale

# Navigate to project
cd /home/deploy/TSH_ERP_Ecosystem

# Run deployment script
./scripts/deploy_production.sh

# Or use automated CI/CD
# (triggered on push to main branch)
```

**What the deployment script does:**
1. Creates database and code backups
2. Pulls latest code from git
3. Installs/updates Python dependencies
4. Runs database migrations
5. Restarts systemd service
6. Runs health checks
7. Rolls back automatically if deployment fails

**Systemd Service:**
- Service file: `/etc/systemd/system/tsh-erp.service`
- Runs as: `deploy` user (not root)
- Manages: uvicorn workers
- Logs: `journalctl -u tsh-erp -f`

**Why not Docker in production?**
- Already working reliably with systemd
- Lower resource overhead (important for VPS)
- Simpler debugging (direct access to processes)
- No need for container orchestration (single server)
- Native nginx integration already configured

**Documentation**: [scripts/deploy_production.sh](../../scripts/deploy_production.sh)

---

## Migration Path (Future Consideration)

If you decide to move production to Docker in the future:

### Pros of Docker in Production:
- Consistent with dev/staging
- Easier horizontal scaling
- Better isolation
- Simplified dependency management
- Container orchestration (Kubernetes) if you grow

### Prerequisites:
1. Docker Swarm or Kubernetes cluster
2. Container registry (Docker Hub, ghcr.io, or private)
3. Volume management strategy (NFS, cloud storage)
4. Load balancer configuration
5. Monitoring and logging solution (Prometheus, Grafana, ELK)

### Migration Steps (when ready):
1. Set up Docker registry
2. Build and push production images with CI/CD
3. Configure Docker Swarm or Kubernetes
4. Set up persistent volumes
5. Migrate database (backup → restore)
6. Update DNS/load balancer
7. Gradual traffic migration
8. Monitor and validate

**Current Recommendation**: **Not needed yet**. Your VPS with systemd works well for current scale.

---

## Decision Tree

```
Need to deploy TSH ERP?
│
├─ Local development?
│  └─ Use Docker Compose (dev profile)
│
├─ Running automated tests?
│  └─ Use Docker (CI/CD)
│
├─ Temporary demo/staging?
│  └─ Use Docker Compose (proxy profile)
│
└─ Production deployment?
   └─ Use Systemd (deploy_production.sh)
```

---

## Quick Reference Commands

### Docker (Development)

```bash
# Start development environment
docker compose -f docker-compose.yml -f docker-compose.dev.yml --profile dev up -d

# View logs
docker compose logs -f app

# Run migrations
docker compose exec app alembic upgrade head

# Access database
docker compose exec tsh_postgres psql -U tsh_admin -d tsh_erp

# Stop all services
docker compose down

# Rebuild after code changes
docker compose build app && docker compose up -d app
```

### Systemd (Production)

```bash
# Check service status
sudo systemctl status tsh-erp

# View logs
sudo journalctl -u tsh-erp -f

# Restart service
sudo systemctl restart tsh-erp

# Run full deployment
./scripts/deploy_production.sh

# Manual rollback
git reset --hard HEAD~1
sudo systemctl restart tsh-erp
```

---

## Environment Variables

Each environment uses different `.env` files:

| Environment | File | Location |
|------------|------|----------|
| Local Dev | `.env.dev` | Repository root (git-ignored) |
| Staging | `.env.staging` | Repository root (git-ignored) |
| Production | `.env.production` | Repository root (git-ignored) |

**Never commit `.env` files to git!**

Templates available:
- `config/env.example` - Base template
- `config/env.docker.dev.example` - Docker development overrides

---

## Monitoring and Logs

### Docker (Development/Staging)

```bash
# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f app
docker compose logs -f postgres
docker compose logs -f redis

# Check container health
docker compose ps

# Resource usage
docker stats
```

### Systemd (Production)

```bash
# View service logs
journalctl -u tsh-erp -f

# Last 100 lines
journalctl -u tsh-erp -n 100

# Today's logs
journalctl -u tsh-erp --since today

# Check service status
systemctl status tsh-erp

# Application logs
tail -f /var/log/tsh_erp/app.log
```

---

## Backup Strategy

### Docker Volumes (Development/Staging)

```bash
# Backup all volumes
./scripts/docker_backup.sh all

# Backup specific service
./scripts/docker_backup.sh postgres
./scripts/docker_backup.sh redis

# Restore from backup
./scripts/docker_restore.sh <timestamp> all
```

### Production (Systemd)

```bash
# Automated backups (part of deploy script)
# Located in: /home/deploy/backups/

# Manual database backup
./scripts/backup_database.sh

# Backup uploads
tar czf backups/uploads_$(date +%Y%m%d).tar.gz uploads/
```

**Backup retention**: 7 days for Docker, 30 days for production

---

## Troubleshooting

### Docker Issues

**Problem**: Container won't start
```bash
# Check logs
docker compose logs app

# Rebuild container
docker compose build --no-cache app
docker compose up -d app

# Check resources
docker system df
docker system prune  # Free up space
```

**Problem**: Database connection failed
```bash
# Check if postgres is healthy
docker compose ps

# Restart postgres
docker compose restart tsh_postgres

# Check connection from app
docker compose exec app psql postgresql://tsh_admin:changeme@tsh_postgres:5432/tsh_erp
```

### Systemd Issues

**Problem**: Service won't start
```bash
# Check service status
systemctl status tsh-erp

# View recent errors
journalctl -u tsh-erp -n 50

# Check if port is in use
sudo lsof -i :8000

# Restart service
sudo systemctl restart tsh-erp
```

**Problem**: High memory usage
```bash
# Check worker count
ps aux | grep uvicorn

# Reduce workers in .env
# UVICORN_WORKERS=2

# Restart service
sudo systemctl restart tsh-erp
```

---

## Summary

| Aspect | Docker (Dev/Staging) | Systemd (Production) |
|--------|---------------------|---------------------|
| **Setup Time** | Minutes | Hours (first time) |
| **Consistency** | Identical everywhere | Environment-specific |
| **Performance** | Slight overhead | Native performance |
| **Isolation** | Complete | Process-level |
| **Portability** | High | Low |
| **Debugging** | Container logs | Direct access |
| **Scaling** | Easy (orchestration) | Manual |
| **Best For** | Development, testing | Stable production |

**Official Position**: Use the right tool for the job. Docker excels at development and testing; systemd excels at simple VPS production deployments.

---

## Contact

Questions about deployment strategy?
- Review this document first
- Check environment-specific documentation
- Ask team lead for clarification

---

**Last Updated**: January 2025
**Maintained By**: DevOps Team
