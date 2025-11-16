# Docker Deployment Guide - TSH ERP

**Priority:** CRITICAL - Read before any deployment
**Purpose:** Leverage Docker's portability for easy, consistent deployments
**Last Updated:** November 13, 2025

---

## 🎯 Docker Philosophy

**Docker's Promise:** "Build once, run anywhere"

```
Local Development → Docker Build → Push to Registry → Pull on Server → Deploy
                    (Same Image)                      (Same Image)     (Same Environment)
```

**Key Principle:** If it works in Docker locally, it works on ANY server with Docker installed.

---

## 🚨 CRITICAL: Why Docker for Deployment?

### ❌ OLD WAY (Manual):
```bash
# Deploy to staging
ssh staging
git pull
pip install -r requirements.txt  # May fail due to dependencies
systemctl restart app              # May have environment issues
# Cross fingers and hope it works 🤞
```

**Problems:**
- Different Python versions
- Different system libraries
- Different environment variables
- "Works on my machine" syndrome
- Hard to debug issues
- Difficult to rollback

### ✅ NEW WAY (Docker):
```bash
# Deploy to staging
docker-compose up -d --build
# Done! Everything works consistently 🎉
```

**Benefits:**
- ✅ Same environment everywhere (local = staging = production)
- ✅ One command deployment
- ✅ Easy rollback (just run old image)
- ✅ Isolated services (backend, database, redis all separate)
- ✅ Reproducible builds
- ✅ No dependency hell

---

## 📦 TSH ERP Docker Architecture

### Multi-Service Stack

```yaml
services:
  tsh_postgres:     # Database
  redis:            # Cache
  tsh_erp_app:      # Backend API (FastAPI)
  tsh_neurolink:    # NeuroLink service
```

### Environment-Specific Configs

```
.env.production   → Production server (167.71.39.50)
.env.staging      → Staging server (167.71.58.65)
```

---

## 🚀 Deployment Workflow

### Step 1: Build Locally (Test)
```bash
# Test the Docker build works
docker-compose build

# Test everything runs
docker-compose up -d

# Verify
curl http://localhost:8000/health

# If works locally → will work on server!
```

### Step 2: Deploy to Staging (167.71.58.65)

```bash
# SSH to staging
ssh khaleel@167.71.58.65

# Navigate to project
cd /opt/tsh-erp-staging

# Pull latest code
git pull origin develop

# Deploy with Docker (ONE COMMAND!)
docker-compose --profile core up -d --build

# Verify
curl http://localhost:8000/health
```

**What Docker does automatically:**
- ✅ Reads `.env.staging` for configuration
- ✅ Builds all containers with correct dependencies
- ✅ Starts PostgreSQL, Redis, Backend, NeuroLink
- ✅ Sets up networking between services
- ✅ Runs health checks
- ✅ Restarts on failure

### Step 3: Deploy to Production (167.71.39.50)

```bash
# SSH to production
ssh root@167.71.39.50

# Navigate to project
cd /opt/tsh-erp

# Pull latest code (from main branch)
git pull origin main

# Deploy with Docker (SAME COMMAND!)
docker-compose --profile core up -d --build

# Verify
curl http://localhost:8000/health
```

---

## 🔧 Essential Docker Commands

### Deployment Commands

```bash
# Start all services (with core profile for PostgreSQL)
docker-compose --profile core up -d

# Rebuild and restart (after code changes)
docker-compose --profile core up -d --build

# Restart specific service
docker-compose restart tsh_erp_app

# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ DANGEROUS - deletes data!)
docker-compose down -v
```

### Monitoring Commands

```bash
# View all running containers
docker ps

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f tsh_erp_app
docker logs tsh_erp_app --tail 100

# Check resource usage
docker stats

# Inspect container
docker inspect tsh_erp_app
```

### Debugging Commands

```bash
# Enter container shell
docker exec -it tsh_erp_app bash

# Run command in container
docker exec tsh_erp_app python -c "print('Hello')"

# Check container health
docker inspect --format='{{.State.Health.Status}}' tsh_erp_app

# View container environment variables
docker exec tsh_erp_app env
```

### Cleanup Commands

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove everything unused (⚠️ BE CAREFUL!)
docker system prune -a
```

---

## 📋 Complete Staging Setup from Scratch

### Prerequisites
```bash
# 1. Server has Docker and docker-compose installed
docker --version
docker-compose --version

# 2. User has Docker permissions
sudo usermod -aG docker khaleel
# Logout and login again
```

### One-Time Setup

```bash
# 1. SSH to staging
ssh khaleel@167.71.58.65

# 2. Clone repository (if not exists)
sudo mkdir -p /opt/tsh-erp-staging
sudo chown khaleel:khaleel /opt/tsh-erp-staging
cd /opt
git clone https://github.com/Qmop1967/tsh-erp-system.git tsh-erp-staging
cd tsh-erp-staging

# 3. Checkout develop branch
git checkout develop

# 4. Create .env.staging file
cp .env.staging.template .env.staging

# 5. Edit .env.staging with correct values
nano .env.staging

# 6. Deploy entire stack with ONE command!
docker-compose --profile core up -d --build

# 7. Wait for health checks (30 seconds)
sleep 30

# 8. Verify all services are healthy
docker ps
curl http://localhost:8000/health
curl http://localhost:8002/health  # NeuroLink

# 9. Check logs for errors
docker-compose logs --tail 50

# Done! 🎉
```

---

## 🔄 Regular Deployment (After Setup)

```bash
# 1. SSH to staging
ssh khaleel@167.71.58.65

# 2. Navigate to project
cd /opt/tsh-erp-staging

# 3. Pull latest code
git pull origin develop

# 4. Deploy (ONE COMMAND!)
docker-compose --profile core up -d --build

# 5. Verify (30 seconds)
sleep 30 && curl http://localhost:8000/health

# Done! That's it! 🚀
```

**Time:** ~2 minutes total

---

## 🏗️ Docker-Compose Profiles

### What are Profiles?

Profiles let you start different sets of services:

```yaml
services:
  tsh_postgres:
    profiles: [core]      # Only starts with --profile core

  tsh_erp_app:
    profiles: []          # Always starts (no profile needed)
```

### Available Profiles

```bash
# Start only app services (no database)
docker-compose up -d

# Start everything including database
docker-compose --profile core up -d

# Start development services
docker-compose --profile dev up -d
```

---

## 🐛 Troubleshooting Docker Deployments

### Issue: Container keeps restarting

```bash
# Check logs
docker logs tsh_erp_app --tail 100

# Common causes:
# 1. Database not ready → Wait 30 seconds for PostgreSQL health check
# 2. Missing environment variables → Check .env file
# 3. Port already in use → Check: netstat -tulpn | grep 8000
# 4. Insufficient resources → Check: docker stats
```

### Issue: Can't connect to database

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check PostgreSQL logs
docker logs tsh_postgres --tail 50

# Test database connection
docker exec tsh_erp_app psql -h tsh_postgres -U tsh_admin -d tsh_erp -c "SELECT 1"

# Verify network
docker network ls
docker network inspect tsh-erp-staging_tsh_network
```

### Issue: Port conflicts

```bash
# Check what's using port 8000
netstat -tulpn | grep 8000

# Stop conflicting service
docker stop $(docker ps -q --filter "publish=8000")

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Map to different external port
```

### Issue: Out of disk space

```bash
# Check disk usage
df -h

# Clean up Docker
docker system prune -a --volumes

# Check Docker disk usage
docker system df
```

---

## 📊 Health Check Verification

### Backend Health Check

```bash
# Local
curl http://localhost:8000/health

# Staging
curl http://staging.erp.tsh.sale/health
ssh khaleel@167.71.58.65 "curl http://localhost:8000/health"

# Production
curl http://erp.tsh.sale/health
ssh root@167.71.39.50 "curl http://localhost:8000/health"
```

### Expected Response

```json
{
  "status": "healthy",
  "timestamp": "2025-11-13T12:00:00",
  "services": {
    "database": "connected",
    "redis": "connected",
    "tds_core": "operational"
  }
}
```

### Docker Health Status

```bash
# Check all containers health
docker ps --format "table {{.Names}}\t{{.Status}}"

# Should show:
# tsh_erp_app        Up 5 minutes (healthy)
# tsh_postgres       Up 5 minutes (healthy)
# redis              Up 5 minutes (healthy)
```

---

## 🔐 Environment Variables Management

### File Structure

```
.env.staging          # Staging secrets (git ignored)
.env.production       # Production secrets (git ignored)
.env.template         # Template for reference (committed)
```

### Required Variables

```bash
# Database
POSTGRES_DB=tsh_erp_staging
POSTGRES_USER=tsh_admin
POSTGRES_PASSWORD=<staging-password>
DATABASE_URL=postgresql://tsh_admin:<password>@tsh_postgres:5432/tsh_erp_staging

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_ENABLED=true

# Application
ENVIRONMENT=staging
DEBUG=false
SECRET_KEY=<generate-random-secret>
JWT_SECRET_KEY=<generate-random-secret>

# Zoho
ZOHO_CLIENT_ID=<from-zoho>
ZOHO_CLIENT_SECRET=<from-zoho>
ZOHO_REFRESH_TOKEN=<from-zoho>
ZOHO_ORGANIZATION_ID=748369814
```

### Generate Secrets

```bash
# Generate random secrets
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or use openssl
openssl rand -hex 32
```

---

## 📈 Performance Best Practices

### 1. Multi-Stage Builds

```dockerfile
# Build stage (larger, has build tools)
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Runtime stage (smaller, production-ready)
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
CMD ["uvicorn", "app.main:app"]
```

### 2. Layer Caching

```dockerfile
# ✅ GOOD: Dependencies first (cached)
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# ❌ BAD: Code first (no caching)
COPY . .
RUN pip install -r requirements.txt
```

### 3. Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

### 4. Resource Limits

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 256M
```

---

## 🚀 CI/CD Integration with Docker

### GitHub Actions Workflow

```yaml
name: Deploy to Staging

on:
  push:
    branches: [develop]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Deploy to Staging
        uses: appleboy/ssh-action@master
        with:
          host: 167.71.58.65
          username: khaleel
          key: ${{ secrets.STAGING_SSH_KEY }}
          script: |
            cd /opt/tsh-erp-staging
            git pull origin develop
            docker-compose --profile core up -d --build
            sleep 30
            curl -f http://localhost:8000/health || exit 1
```

---

## 📝 Deployment Checklist

### Before Deployment

- [ ] Code tested locally with Docker
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] `.env.staging` file exists on server
- [ ] Backup database (production only)
- [ ] Notify team of deployment

### During Deployment

- [ ] SSH to correct server (staging: 167.71.58.65, production: 167.71.39.50)
- [ ] Navigate to correct directory
- [ ] Pull latest code from correct branch (develop/main)
- [ ] Run `docker-compose --profile core up -d --build`
- [ ] Wait for health checks (30 seconds)
- [ ] Verify all containers healthy: `docker ps`

### After Deployment

- [ ] Check health endpoint: `curl http://localhost:8000/health`
- [ ] Check logs: `docker-compose logs --tail 50`
- [ ] Test key functionality
- [ ] Monitor for errors (first 15 minutes)
- [ ] Update deployment log

---

## 🎓 Key Takeaways

### For AI (Claude Code)

**ALWAYS use Docker for deployment:**
```bash
# ✅ CORRECT: Docker-based deployment
docker-compose --profile core up -d --build

# ❌ WRONG: Manual deployment
ssh server
git pull
pip install
systemctl restart
```

**ONE command should:**
- Pull latest code
- Build containers
- Start all services
- Run health checks
- Be ready to serve traffic

### For Developers

**Docker = Consistency:**
- Local development matches staging matches production
- No more "works on my machine"
- Easy rollback (just run old container)
- Fast deployments (1-2 minutes)

**Best Practice:**
```bash
# Development
docker-compose up -d

# Staging
ssh khaleel@167.71.58.65
cd /opt/tsh-erp-staging && docker-compose --profile core up -d --build

# Production
ssh root@167.71.39.50
cd /opt/tsh-erp && docker-compose --profile core up -d --build
```

---

## 🔗 Related Documentation

- **Docker Official Docs:** https://docs.docker.com/
- **docker-compose Reference:** https://docs.docker.com/compose/
- **Best Practices:** https://docs.docker.com/develop/dev-best-practices/
- **SERVER_INFRASTRUCTURE.md** - Server IPs and credentials
- **DEPLOYMENT_RULES.md** - Deployment safety rules
- **STAGING_TO_PRODUCTION_WORKFLOW.md** - Deployment workflow

---

**Created:** November 13, 2025
**Inspired by:** User feedback on Docker deployment simplicity
**Priority:** CRITICAL - Use Docker for ALL deployments

**Remember:** If it doesn't work with Docker, fix Docker - don't work around it! 🐳
