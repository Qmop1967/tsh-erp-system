# TSH ERP Deployment Strategy

## Current Status (November 7, 2025)

### Active Deployment: Docker 🐳
- **Container:** tsh_erp_app
- **Status:** ✅ Running and Healthy
- **Port:** 8000
- **Method:** Docker Compose

### Inactive Deployment: Systemd Direct
- **Service:** tsh-erp.service
- **Status:** ⚠️ Stopped and Disabled
- **Directory:** /home/deploy/TSH_ERP_Ecosystem/
- **Method:** Direct Python + Gunicorn

---

## Recommended Strategy: Docker-Only Deployment

### Why Docker-Only?

1. **✅ Currently Active:** Already serving production traffic
2. **✅ Isolation:** Clean environment separation
3. **✅ Reproducibility:** Same setup everywhere
4. **✅ Scalability:** Easy to scale and load balance
5. **✅ Industry Standard:** Modern best practice

---

## Migration Steps

### Step 1: Confirm Docker as Primary ✅ DONE

```bash
# Check Docker status
docker ps | grep tsh_erp_app
# Status: Running and healthy
```

### Step 2: Clean Up Direct Deployment

#### A. Stop and Disable Systemd Service
```bash
ssh root@167.71.39.50 "systemctl stop tsh-erp"
ssh root@167.71.39.50 "systemctl disable tsh-erp"
```
✅ **DONE**

#### B. Archive Systemd Service File
```bash
ssh root@167.71.39.50 "mv /etc/systemd/system/tsh-erp.service /etc/systemd/system/tsh-erp.service.backup"
ssh root@167.71.39.50 "systemctl daemon-reload"
```

#### C. Keep Direct Code for Development
```bash
# Keep /home/deploy/TSH_ERP_Ecosystem/ for:
# - Git operations
# - Development testing
# - Docker builds
# DO NOT delete this directory!
```

### Step 3: Fix Docker Image Build

#### Issue: Dependency Conflicts
Current problem: `backports.asyncio.runner` and `uvicorn` version conflicts

#### Solution: Update requirements.txt
```bash
# Already fixed:
# - Removed backports.asyncio.runner (not needed for Python 3.11+)

# Need to fix:
# - Resolve uvicorn version conflict
```

#### Proper Docker Build Command
```bash
cd /home/deploy/TSH_ERP_Ecosystem
docker build -t tsh_erp_docker-app:latest .
docker tag tsh_erp_docker-app:latest tsh_erp_docker-app:$(date +%Y%m%d)
```

### Step 4: Deployment Workflow

#### Standard Deployment Process
```bash
# 1. Pull latest code
cd /home/deploy/TSH_ERP_Ecosystem
git pull origin main

# 2. Rebuild Docker image
docker build -t tsh_erp_docker-app:latest .

# 3. Stop old container
docker stop tsh_erp_app

# 4. Remove old container
docker rm tsh_erp_app

# 5. Start new container
docker run -d \
  --name tsh_erp_app \
  --network tsh_network \
  -p 8000:8000 \
  --env-file .env \
  --restart unless-stopped \
  tsh_erp_docker-app:latest

# 6. Verify
docker ps | grep tsh_erp_app
curl https://erp.tsh.sale/health
```

#### Quick Deployment (Hot Patch - Temporary)
```bash
# For urgent fixes only!
# Copy changed files directly to container

docker cp app/services/zoho_processor.py tsh_erp_app:/app/app/services/
docker cp app/services/zoho_queue.py tsh_erp_app:/app/app/services/
docker restart tsh_erp_app
```

---

## Docker Compose Setup (Recommended)

### Current docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    build: .
    container_name: tsh_erp_app
    ports:
      - "8000:8000"
    env_file:
      - .env
    networks:
      - tsh_network
    restart: unless-stopped
    depends_on:
      - postgres
      - redis

  nginx:
    image: nginx:alpine
    container_name: tsh_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - /etc/letsencrypt:/etc/letsencrypt
    networks:
      - tsh_network
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    container_name: tsh_postgres
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - tsh_network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: tsh_redis
    networks:
      - tsh_network
    restart: unless-stopped

networks:
  tsh_network:
    driver: bridge

volumes:
  postgres_data:
```

### Deployment with Docker Compose
```bash
# Deploy/Update
cd /home/deploy/TSH_ERP_Ecosystem
git pull origin main
docker-compose build app
docker-compose up -d app

# View logs
docker-compose logs -f app

# Restart specific service
docker-compose restart app

# Stop all
docker-compose down

# Full rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## Alternative Strategy: Direct Deployment Only

### If You Prefer Direct Deployment

#### Advantages
- Simpler deployment (git pull + systemctl restart)
- Direct file access
- Easier debugging

#### Migration Steps

1. **Stop Docker Containers**
```bash
docker stop tsh_erp_app tsh_nginx tsh_postgres tsh_redis
docker rm tsh_erp_app tsh_nginx tsh_postgres tsh_redis
```

2. **Update Nginx Configuration**
```bash
# Point to 127.0.0.1:8000 instead of Docker container
# /etc/nginx/sites-available/tsh-erp
```

3. **Fix Python Environment**
```bash
cd /home/deploy/TSH_ERP_Ecosystem
source venv/bin/activate
pip install -r requirements.txt
```

4. **Enable Systemd Service**
```bash
systemctl enable tsh-erp
systemctl start tsh-erp
systemctl status tsh-erp
```

5. **Deployment Workflow**
```bash
# Standard deployment
cd /home/deploy/TSH_ERP_Ecosystem
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
systemctl restart tsh-erp
systemctl status tsh-erp
```

---

## Hybrid Approach

### Use Docker for Production, Direct for Development

#### Production (Docker)
- Port 8000 (external)
- Always running
- Stable releases only

#### Development (Direct)
- Port 8001 (internal only)
- For testing before Docker deployment
- Quick iterations

#### Systemd Service for Development
```ini
[Service]
ExecStart=/home/deploy/TSH_ERP_Ecosystem/venv/bin/gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 127.0.0.1:8001
```

---

## Monitoring & Health Checks

### Docker Health Check
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Service Monitoring
```bash
# Check Docker container
docker ps | grep tsh_erp_app
docker logs tsh_erp_app --tail 50

# Check health endpoint
curl https://erp.tsh.sale/health

# Check Nginx
curl -I https://erp.tsh.sale

# Check database connection
docker exec tsh_postgres psql -U postgres -c "SELECT 1"
```

---

## Rollback Strategy

### Docker Rollback
```bash
# Keep tagged images
docker images | grep tsh_erp_docker-app

# Rollback to previous version
docker stop tsh_erp_app
docker rm tsh_erp_app
docker run -d --name tsh_erp_app tsh_erp_docker-app:20251106
```

### Direct Deployment Rollback
```bash
cd /home/deploy/TSH_ERP_Ecosystem
git log --oneline -5
git checkout <previous-commit>
systemctl restart tsh-erp
```

---

## CI/CD Integration (Future)

### GitHub Actions Workflow
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Docker image
        run: docker build -t tsh_erp:${{ github.sha }} .

      - name: Deploy to VPS
        run: |
          ssh root@167.71.39.50 "cd /home/deploy/TSH_ERP_Ecosystem && \
            git pull && \
            docker-compose build app && \
            docker-compose up -d app"
```

---

## Recommendation Summary

### ✅ RECOMMENDED: Docker-Only

**Reasons:**
1. Already running production
2. Modern and scalable
3. Easy rollback
4. Industry standard

**Action Items:**
1. ✅ Keep Docker as primary
2. ✅ Disable systemd service (DONE)
3. ✅ Fix Docker image dependencies (DONE - Nov 7, 2025)
   - Removed uvicorn==0.24.0 (conflicted with uvicorn[standard]==0.27.0)
   - Consolidated alembic to v1.13.1
   - Cleaned up duplicate psycopg2-binary entries
4. ⏳ Document Docker deployment process
5. ⏳ Set up proper CI/CD

---

## Decision Required

**Senior, which deployment strategy do you prefer?**

A. **Docker-Only** (Recommended)
B. **Direct Deployment Only**
C. **Hybrid (Both, but one at a time)**

**I'll implement whichever you choose!**

---

**Date:** November 7, 2025
**Status:** Awaiting decision
**Current:** Docker active, Direct disabled
