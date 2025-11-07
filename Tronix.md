# 🚀 Tronix - TSH ERP Ecosystem Deployment & Integration Guide

**Senior Software Engineer's Handbook for Production Deployment**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture Philosophy](#architecture-philosophy)
3. [Deployment Strategy](#deployment-strategy)
4. [Zoho Integration Strategy](#zoho-integration-strategy)
5. [Development Workflow](#development-workflow)
6. [Troubleshooting Guide](#troubleshooting-guide)
7. [Maintenance & Monitoring](#maintenance--monitoring)
8. [Team Transition Plan](#team-transition-plan)

---

## Overview

### Project Context

**TSH ERP Ecosystem** is a comprehensive ERP system built with:
- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (Primary), Supabase (Cloud)
- **Cache**: Redis
- **Web Server**: Nginx (Reverse Proxy)
- **Deployment**: Docker Compose
- **Integration**: Zoho Books & Inventory (Bi-directional Sync)

### Deployment Environment

- **VPS**: DigitalOcean Droplet (167.71.39.50)
- **Domain**: erp.tsh.sale
- **SSL**: Let's Encrypt (Auto-renewal via Certbot)
- **OS**: Ubuntu 22.04 LTS
- **Docker**: Docker Compose v3.8

---

## Architecture Philosophy

### Senior Engineer Mindset

As a senior software engineer, always follow these principles:

1. **🔒 Security First**: Never commit secrets, always use environment variables
2. **📝 Document Everything**: Code changes, deployment steps, architectural decisions
3. **🧪 Test Before Deploy**: Local testing → Staging → Production
4. **🔄 Rollback Ready**: Always tag Docker images with versions for easy rollback
5. **📊 Monitor Continuously**: Logs, metrics, health checks
6. **🎯 Incremental Changes**: Small, frequent deployments over large, risky ones
7. **🤝 Team Communication**: Keep team informed of changes and issues

### Deployment Philosophy: Docker-Only

**Why Docker-Only?**

✅ **Consistency**: Same environment everywhere (dev, staging, prod)
✅ **Isolation**: No dependency conflicts with host system
✅ **Scalability**: Easy horizontal scaling with orchestration
✅ **Rollback**: Simple version management with tagged images
✅ **Industry Standard**: Modern best practice for microservices

**Decision Made**: Docker-Only deployment (November 7, 2025)
- ✅ Direct systemd deployment disabled
- ✅ All production traffic through Docker containers
- ✅ Clean separation of concerns

---

## Deployment Strategy

### Production Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Internet (Port 443/80)                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Nginx (Docker)  │
                  │  SSL Termination │
                  │  Reverse Proxy   │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   TSH ERP App    │
                  │  (FastAPI:8000)  │
                  │   Docker Container│
                  └────┬──────┬──────┘
                       │      │
         ┌─────────────┘      └──────────────┐
         ▼                                    ▼
┌──────────────────┐                ┌─────────────────┐
│  PostgreSQL      │                │  Redis Cache    │
│  (Docker)        │                │  (Docker)       │
│  Port: 5432      │                │  Port: 6379     │
└──────────────────┘                └─────────────────┘
         │
         └──────────────────┐
                            ▼
                   ┌─────────────────┐
                   │  Supabase Cloud  │
                   │  (Backup/Sync)   │
                   └─────────────────┘
```

### Docker Compose Stack

**File**: `docker-compose.yml`

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
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

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
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: tsh_redis
    networks:
      - tsh_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

networks:
  tsh_network:
    driver: bridge

volumes:
  postgres_data:
```

---

## Zoho Integration Strategy

### Integration Philosophy

**Hybrid Approach: Dual System Operation**

During the transition period, the team will use **BOTH** systems simultaneously:

- **Zoho Books/Inventory**: Primary system (legacy, trusted)
- **TSH ERP Ecosystem**: New system (being validated)

**Data Flow**: Bi-directional synchronization ensures both systems stay in sync.

### Synchronization Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      Zoho Books/Inventory                     │
│  (Products, Customers, Invoices, Bills, Inventory, Prices)   │
└────────────┬─────────────────────────────────┬───────────────┘
             │                                 │
             │ Webhooks (Real-time)            │ Bulk Sync (Scheduled)
             ▼                                 ▼
    ┌─────────────────┐              ┌─────────────────┐
    │  TDS Inbox      │              │  TDS Bulk Sync  │
    │  (Webhooks)     │              │  (Polling/API)  │
    └────────┬────────┘              └────────┬────────┘
             │                                │
             └────────────┬───────────────────┘
                          ▼
                 ┌──────────────────┐
                 │  TDS Sync Queue  │
                 │  (Processing)    │
                 └────────┬─────────┘
                          │
                          ▼
           ┌──────────────────────────┐
           │  Entity Handlers         │
           │  (Products, Customers,   │
           │   Invoices, etc.)        │
           └────────┬─────────────────┘
                    │
                    ▼
        ┌────────────────────────┐
        │  TSH ERP Database      │
        │  (PostgreSQL/Supabase) │
        └────────────────────────┘
```

### Synchronization Components

#### 1. **Webhooks (Real-time Sync)**

Zoho sends webhooks whenever data changes:

**Webhook Endpoints** (`app/routers/zoho_webhooks.py`):
- `POST /api/zoho/webhooks/products`
- `POST /api/zoho/webhooks/customers`
- `POST /api/zoho/webhooks/invoices`
- `POST /api/zoho/webhooks/bills`
- `POST /api/zoho/webhooks/credit-notes`
- `POST /api/zoho/webhooks/stock`
- `POST /api/zoho/webhooks/prices`

**Webhook Processing Flow**:
1. Webhook received → Signature verification
2. Store in `tds_inbox_events` table (raw data)
3. Queue in `tds_sync_queue` table (for processing)
4. Background worker processes queue
5. EntityHandler syncs to local database
6. Update queue status (completed/failed)

#### 2. **Bulk Sync (Scheduled/Manual)**

For initial data load or recovery:

**Bulk Sync Endpoint**: `POST /api/zoho/bulk-sync`

**Supports**:
- Full entity sync (all products, customers, etc.)
- Incremental sync (since last sync timestamp)
- Selective sync (specific entity types)
- Pagination (large datasets)

#### 3. **TDS (TSH Data Sync) Architecture**

**Key Components**:

```
app/tds/
├── core/
│   ├── events.py          # Event definitions
│   ├── sync_engine.py     # Core sync logic
│   └── entity_handlers/   # Entity-specific handlers
│       ├── product_handler.py
│       ├── customer_handler.py
│       ├── invoice_handler.py
│       └── ...
├── integrations/
│   └── zoho/
│       ├── client.py      # Unified Zoho API client
│       ├── auth.py        # OAuth 2.0 authentication
│       ├── sync.py        # Sync orchestrator
│       └── webhooks.py    # Webhook manager
└── models/
    ├── sync_run.py        # Sync run tracking
    ├── inbox_event.py     # Webhook inbox
    └── sync_queue.py      # Processing queue
```

**Database Tables**:

```sql
-- Webhook Inbox (Raw Events)
tds_inbox_events (
    id, event_id, source_type, entity_type, entity_id,
    event_type, raw_payload, received_at, processed_at, status
)

-- Processing Queue
tds_sync_queue (
    id, inbox_event_id, entity_type, entity_id, zoho_entity_id,
    priority, status, retry_count, error_message,
    queued_at, processing_started_at, processing_completed_at
)

-- Sync Runs (Bulk Operations)
tds_sync_runs (
    id, run_type, entity_type, source_type, status,
    total_items, processed_items, failed_items,
    started_at, completed_at, error_log
)
```

### Authentication & Security

**Zoho OAuth 2.0 Flow**:

1. **Initial Setup** (One-time):
   ```bash
   # Configure credentials
   export ZOHO_CLIENT_ID="your_client_id"
   export ZOHO_CLIENT_SECRET="your_client_secret"
   export ZOHO_REFRESH_TOKEN="your_refresh_token"
   export ZOHO_ORGANIZATION_ID="your_org_id"
   ```

2. **Auto-refresh** (Handled by `ZohoAuthManager`):
   - Access token expires every 1 hour
   - Automatic refresh using refresh_token
   - Token stored in memory (not persisted)
   - Concurrent request handling with locks

3. **Rate Limiting**:
   - Zoho API: 100 requests/minute
   - Built-in rate limiter with exponential backoff
   - Queue-based processing prevents rate limit violations

### Monitoring Sync Health

**Health Check Endpoints**:

```bash
# Overall system health
GET /health

# Sync queue statistics
GET /api/zoho/sync/stats
Response: {
  "queue": {
    "pending": 45,
    "processing": 3,
    "completed": 1234,
    "failed": 12,
    "dead_letter": 2
  },
  "by_entity": {
    "products": {"pending": 20, "failed": 5},
    "customers": {"pending": 15, "failed": 3},
    "invoices": {"pending": 10, "failed": 4}
  },
  "sync_delay_avg_seconds": 12.5
}

# Recent sync runs
GET /api/zoho/sync/runs?limit=10

# Webhook inbox status
GET /api/zoho/webhooks/inbox/stats
```

**SQL Queries for Health Monitoring**:

```sql
-- Check queue status
SELECT status, COUNT(*)
FROM tds_sync_queue
GROUP BY status;

-- Check sync delays
SELECT entity_type,
       AVG(EXTRACT(EPOCH FROM (processing_completed_at - queued_at))) as avg_delay_seconds
FROM tds_sync_queue
WHERE status = 'completed'
  AND processing_completed_at IS NOT NULL
GROUP BY entity_type;

-- Check recent failures
SELECT entity_type, error_message, COUNT(*) as count
FROM tds_sync_queue
WHERE status = 'failed'
  AND queued_at > NOW() - INTERVAL '24 hours'
GROUP BY entity_type, error_message
ORDER BY count DESC;

-- Check webhook delivery success rate
SELECT
  COUNT(*) as total_webhooks,
  SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful,
  SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
  ROUND(100.0 * SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate_percent
FROM tds_inbox_events
WHERE received_at > NOW() - INTERVAL '24 hours';
```

---

## Development Workflow

### Senior Engineer's Deployment Checklist

#### **Phase 1: Local Development**

```bash
# 1. Pull latest code
cd /path/to/TSH_ERP_Ecosystem
git pull origin main

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Make changes
# ... code changes ...

# 4. Test locally
python -m pytest tests/
python -m pytest tests/integration/

# 5. Run linter
black app/
flake8 app/

# 6. Test Docker build locally
docker build -t tsh_erp_test:local .

# 7. Run locally with Docker Compose
docker-compose up -d
docker logs -f tsh_erp_app

# 8. Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/zoho/sync/stats

# 9. Commit changes
git add .
git commit -m "feat: your feature description

Detailed explanation of changes...

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 10. Push to remote
git push origin feature/your-feature-name

# 11. Create Pull Request
gh pr create --title "feat: your feature" --body "..."
```

#### **Phase 2: Production Deployment**

**Standard Deployment Process**:

```bash
#!/bin/bash
# deploy.sh - Production Deployment Script

set -e  # Exit on error

# Configuration
VPS_HOST="root@167.71.39.50"
DEPLOY_DIR="/home/deploy/TSH_ERP_Ecosystem"
DOCKER_IMAGE="tsh_erp_docker-app"
DATE_TAG=$(date +%Y%m%d-%H%M%S)

echo "🚀 Starting deployment to production..."

# Step 1: Merge to main (after PR approval)
echo "📝 Step 1: Ensure code is merged to main"
git checkout main
git pull origin main

# Step 2: Connect to VPS and pull latest code
echo "📥 Step 2: Pulling latest code on VPS"
ssh $VPS_HOST "cd $DEPLOY_DIR && git pull origin main"

# Step 3: Backup current Docker image
echo "💾 Step 3: Backing up current image"
ssh $VPS_HOST "docker tag $DOCKER_IMAGE:latest $DOCKER_IMAGE:backup-$(date +%Y%m%d)"

# Step 4: Build new Docker image
echo "🔨 Step 4: Building new Docker image"
ssh $VPS_HOST "cd $DEPLOY_DIR && docker build -t $DOCKER_IMAGE:latest -t $DOCKER_IMAGE:$DATE_TAG ."

# Step 5: Stop old container
echo "🛑 Step 5: Stopping old container"
ssh $VPS_HOST "docker stop tsh_erp_app || true"
ssh $VPS_HOST "docker rm tsh_erp_app || true"

# Step 6: Start new container
echo "▶️  Step 6: Starting new container"
ssh $VPS_HOST "docker run -d \
  --name tsh_erp_app \
  --network tsh_erp_docker_tsh_network \
  -p 8000:8000 \
  --env-file $DEPLOY_DIR/.env \
  --restart unless-stopped \
  $DOCKER_IMAGE:latest"

# Step 7: Wait for health check
echo "🏥 Step 7: Waiting for health check..."
sleep 15

# Step 8: Verify deployment
echo "✅ Step 8: Verifying deployment"
HEALTH_CHECK=$(curl -s https://erp.tsh.sale/health)
if echo "$HEALTH_CHECK" | grep -q '"status":"healthy"'; then
  echo "✅ Deployment successful!"
  echo "🎉 Version $DATE_TAG is now live!"
else
  echo "❌ Health check failed!"
  echo "🔄 Rolling back to previous version..."
  ssh $VPS_HOST "docker stop tsh_erp_app && docker rm tsh_erp_app"
  ssh $VPS_HOST "docker run -d --name tsh_erp_app --network tsh_erp_docker_tsh_network -p 8000:8000 --env-file $DEPLOY_DIR/.env --restart unless-stopped $DOCKER_IMAGE:backup-$(date +%Y%m%d)"
  exit 1
fi

# Step 9: Clean up old images (keep last 5 versions)
echo "🧹 Step 9: Cleaning up old images"
ssh $VPS_HOST "docker images | grep $DOCKER_IMAGE | tail -n +6 | awk '{print \$3}' | xargs -r docker rmi"

# Step 10: Check logs
echo "📋 Step 10: Recent logs"
ssh $VPS_HOST "docker logs tsh_erp_app --tail 20"

echo "✨ Deployment complete!"
```

**Make script executable**:
```bash
chmod +x deploy.sh
```

**Usage**:
```bash
./deploy.sh
```

#### **Phase 3: Rollback Procedure**

If deployment fails or issues are discovered:

```bash
#!/bin/bash
# rollback.sh - Emergency Rollback Script

VPS_HOST="root@167.71.39.50"
DOCKER_IMAGE="tsh_erp_docker-app"

echo "🔄 Starting rollback procedure..."

# Step 1: List available versions
echo "📋 Available versions:"
ssh $VPS_HOST "docker images | grep $DOCKER_IMAGE"

# Step 2: Prompt for version to rollback to
read -p "Enter version tag to rollback to (e.g., 20251107-143022): " ROLLBACK_VERSION

# Step 3: Stop current container
echo "🛑 Stopping current container"
ssh $VPS_HOST "docker stop tsh_erp_app"
ssh $VPS_HOST "docker rm tsh_erp_app"

# Step 4: Start container with old version
echo "▶️  Starting container with version $ROLLBACK_VERSION"
ssh $VPS_HOST "docker run -d \
  --name tsh_erp_app \
  --network tsh_erp_docker_tsh_network \
  -p 8000:8000 \
  --env-file /home/deploy/TSH_ERP_Ecosystem/.env \
  --restart unless-stopped \
  $DOCKER_IMAGE:$ROLLBACK_VERSION"

# Step 5: Verify health
sleep 10
echo "🏥 Verifying health"
curl -s https://erp.tsh.sale/health | jq .

echo "✅ Rollback complete!"
```

#### **Hot-Patch Procedure (Emergency Only)**

For urgent fixes that can't wait for full rebuild:

```bash
# Copy changed files directly to running container
docker cp app/services/zoho_processor.py tsh_erp_app:/app/app/services/
docker cp app/services/zoho_queue.py tsh_erp_app:/app/app/services/

# Restart container
docker restart tsh_erp_app

# Verify
docker logs tsh_erp_app --tail 50

# IMPORTANT: Follow up with proper rebuild ASAP
```

**⚠️ Warning**: Hot-patching should only be used for emergencies. Always follow up with a proper rebuild and deployment.

---

## Troubleshooting Guide

### Common Issues & Solutions

#### **Issue 1: Container Won't Start**

**Symptoms**:
- `docker ps` shows container as "Restarting" or "Exited"
- 502 Bad Gateway on website

**Diagnosis**:
```bash
# Check container status
docker ps -a | grep tsh_erp_app

# Check logs
docker logs tsh_erp_app --tail 100

# Common errors to look for:
# - ImportError / ModuleNotFoundError
# - Database connection errors
# - Missing environment variables
```

**Solutions**:

1. **Import Errors**:
   ```bash
   # Check if all Python files are synced
   ssh root@167.71.39.50 "cd /home/deploy/TSH_ERP_Ecosystem && git status"

   # Rebuild image
   ssh root@167.71.39.50 "cd /home/deploy/TSH_ERP_Ecosystem && docker build -t tsh_erp_docker-app:latest ."
   ```

2. **Database Connection Errors**:
   ```bash
   # Check if PostgreSQL is running
   docker ps | grep postgres

   # Test database connection
   docker exec tsh_postgres psql -U postgres -c "SELECT 1"

   # Check .env file has correct credentials
   ssh root@167.71.39.50 "grep DB_ /home/deploy/TSH_ERP_Ecosystem/.env"
   ```

3. **Missing Environment Variables**:
   ```bash
   # Verify .env file exists and is complete
   ssh root@167.71.39.50 "cat /home/deploy/TSH_ERP_Ecosystem/.env | grep -E 'ZOHO|DB_|REDIS'"
   ```

#### **Issue 2: Disk Space Full**

**Symptoms**:
- Docker build fails with "no space left on device"
- Container crashes unexpectedly

**Diagnosis**:
```bash
# Check disk usage
ssh root@167.71.39.50 "df -h"

# Check Docker disk usage
ssh root@167.71.39.50 "docker system df"
```

**Solution**:
```bash
# Clean up Docker system (removes unused images, containers, volumes)
ssh root@167.71.39.50 "docker system prune -a --volumes -f"

# Remove old logs
ssh root@167.71.39.50 "find /var/log -name '*.log' -mtime +30 -delete"

# Clean up archived files (if applicable)
ssh root@167.71.39.50 "du -sh /home/deploy/TSH_ERP_Ecosystem/archived/*"
ssh root@167.71.39.50 "rm -rf /home/deploy/TSH_ERP_Ecosystem/archived/old_backup"
```

#### **Issue 3: Zoho Sync Not Working**

**Symptoms**:
- Queue items stuck in "pending" status
- Webhooks not being processed
- Data not syncing between Zoho and TSH ERP

**Diagnosis**:
```bash
# Check queue status
curl -s https://erp.tsh.sale/api/zoho/sync/stats | jq .

# Check database directly
ssh root@167.71.39.50 "PGPASSWORD='password' psql -U postgres -d tsh_erp -c 'SELECT status, COUNT(*) FROM tds_sync_queue GROUP BY status;'"

# Check background worker logs
docker logs tsh_erp_app | grep -i "worker\|sync\|zoho"
```

**Solutions**:

1. **Worker Not Running**:
   ```bash
   # Check if worker is started in main.py
   # Restart container to restart worker
   docker restart tsh_erp_app
   ```

2. **Zoho Authentication Issues**:
   ```bash
   # Test Zoho credentials
   curl -X POST https://erp.tsh.sale/api/zoho/test-credentials

   # Refresh tokens manually if needed
   # Update .env with new tokens
   docker restart tsh_erp_app
   ```

3. **Queue Backlog**:
   ```bash
   # Manually trigger bulk sync to clear backlog
   curl -X POST https://erp.tsh.sale/api/zoho/bulk-sync \
     -H "Content-Type: application/json" \
     -d '{"entity_type": "products", "mode": "incremental"}'
   ```

#### **Issue 4: SSL Certificate Expired**

**Symptoms**:
- Browser shows "Connection not secure"
- API calls fail with SSL errors

**Solution**:
```bash
# Renew Let's Encrypt certificate
ssh root@167.71.39.50 "certbot renew --nginx"

# Restart Nginx
docker restart tsh_nginx
```

#### **Issue 5: High CPU/Memory Usage**

**Diagnosis**:
```bash
# Check resource usage
docker stats

# Check which container is using resources
docker stats --no-stream | sort -k 3 -hr
```

**Solutions**:
```bash
# Restart problematic container
docker restart <container_name>

# Check for memory leaks in logs
docker logs tsh_erp_app | grep -i "memory\|out of memory"

# Scale down workers if needed (modify gunicorn workers in Dockerfile)
```

---

## Maintenance & Monitoring

### Daily Health Checks

**Morning Checklist** (5 minutes):

```bash
#!/bin/bash
# daily_health_check.sh

echo "📊 TSH ERP Daily Health Check"
echo "================================"

# 1. Container Status
echo "🐳 Docker Containers:"
ssh root@167.71.39.50 "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

# 2. Health Endpoint
echo -e "\n🏥 Application Health:"
curl -s https://erp.tsh.sale/health | jq .

# 3. Sync Queue Status
echo -e "\n📦 Sync Queue Status:"
curl -s https://erp.tsh.sale/api/zoho/sync/stats | jq .queue

# 4. Disk Space
echo -e "\n💾 Disk Space:"
ssh root@167.71.39.50 "df -h | grep '/dev/vda1'"

# 5. Recent Errors
echo -e "\n❌ Recent Errors (last 1 hour):"
ssh root@167.71.39.50 "docker logs tsh_erp_app --since 1h 2>&1 | grep -i error | tail -5"

# 6. SSL Certificate Expiry
echo -e "\n🔐 SSL Certificate:"
echo | openssl s_client -servername erp.tsh.sale -connect erp.tsh.sale:443 2>/dev/null | openssl x509 -noout -dates

echo -e "\n✅ Health check complete!"
```

### Weekly Maintenance Tasks

**Every Sunday** (30 minutes):

```bash
#!/bin/bash
# weekly_maintenance.sh

echo "🔧 TSH ERP Weekly Maintenance"
echo "================================"

# 1. Backup Database
echo "💾 Step 1: Backing up database..."
ssh root@167.71.39.50 "docker exec tsh_postgres pg_dump -U postgres tsh_erp > /backups/tsh_erp_$(date +%Y%m%d).sql"

# 2. Clean up old queue items (older than 30 days)
echo "🧹 Step 2: Cleaning up old queue items..."
ssh root@167.71.39.50 "PGPASSWORD='password' psql -U postgres -d tsh_erp -c \"DELETE FROM tds_sync_queue WHERE status IN ('completed', 'dead_letter') AND queued_at < NOW() - INTERVAL '30 days';\""

# 3. Clean up old Docker images (keep last 10)
echo "🗑️  Step 3: Cleaning up old Docker images..."
ssh root@167.71.39.50 "docker images | grep tsh_erp_docker-app | tail -n +11 | awk '{print \$3}' | xargs -r docker rmi"

# 4. Update system packages
echo "📦 Step 4: Updating system packages..."
ssh root@167.71.39.50 "apt update && apt upgrade -y"

# 5. Restart containers (for fresh start)
echo "🔄 Step 5: Restarting containers..."
ssh root@167.71.39.50 "docker-compose -f /home/deploy/TSH_ERP_Ecosystem/docker-compose.yml restart"

# 6. Generate weekly report
echo "📊 Step 6: Generating weekly report..."
# ... report generation logic ...

echo "✅ Weekly maintenance complete!"
```

### Monitoring Setup (Optional - Recommended)

**Prometheus + Grafana Stack**:

```yaml
# monitoring/docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - tsh_network

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=your_secure_password
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - tsh_network

volumes:
  prometheus_data:
  grafana_data:
```

**Key Metrics to Monitor**:
- API response time (p50, p95, p99)
- Sync queue depth
- Webhook delivery success rate
- Database connection pool usage
- Docker container health
- Disk space usage
- CPU/Memory usage

---

## Team Transition Plan

### Phase 1: Parallel Operation (Current Phase)

**Duration**: 2-4 weeks

**Goal**: Validate TSH ERP functionality while maintaining Zoho as primary

**Team Behavior**:
- ✅ Continue using Zoho Books/Inventory as primary system
- ✅ TSH ERP syncs data automatically in background
- ✅ Team can view/verify data in TSH ERP (read-only validation)
- ❌ Do NOT make changes directly in TSH ERP yet

**Validation Checklist**:

```
□ All products sync correctly (images, descriptions, prices)
□ All customers sync correctly (contact details, addresses)
□ All invoices sync correctly (line items, totals, taxes)
□ All bills sync correctly
□ Inventory levels sync accurately
□ Price lists sync correctly
□ No sync delays (< 30 seconds average)
□ No data loss or corruption
□ All webhooks processed successfully (> 99% success rate)
```

### Phase 2: Gradual Migration (After Validation)

**Duration**: 2-4 weeks

**Goal**: Start using TSH ERP for specific workflows while maintaining Zoho sync

**Team Behavior**:
- ✅ Use TSH ERP for new workflows (e.g., POS, consumer app)
- ✅ Continue using Zoho for accounting/reporting
- ✅ Bi-directional sync ensures both systems stay updated
- ⚠️ Monitor data consistency daily

**Recommended Order**:
1. **Week 1**: POS transactions (TSH ERP) → Sync to Zoho
2. **Week 2**: Consumer orders (TSH ERP) → Sync to Zoho
3. **Week 3**: Inventory management (TSH ERP) → Sync to Zoho
4. **Week 4**: Customer management (TSH ERP) → Sync to Zoho

### Phase 3: Full Migration (Final Phase)

**Duration**: 2-4 weeks

**Goal**: TSH ERP becomes primary system, Zoho for backup/reporting only

**Team Behavior**:
- ✅ Use TSH ERP for ALL operations
- ✅ Zoho receives updates (one-way sync for reporting)
- ✅ Export reports from TSH ERP
- ❌ Avoid making changes in Zoho (read-only)

**Migration Completion Criteria**:

```
□ All team members trained on TSH ERP
□ All workflows tested and validated
□ Reporting dashboards created in TSH ERP
□ Backup procedures established
□ 100% data consistency verified
□ Performance meets requirements (< 200ms average response time)
□ No critical bugs in production
□ Team comfortable with new system
```

### Training & Support

**Team Training Schedule**:

**Week 1**: System Overview
- Architecture and design philosophy
- Key features and differences from Zoho
- Navigation and basic operations

**Week 2**: Daily Operations
- Creating invoices and bills
- Managing customers and products
- Processing orders and payments
- Inventory management

**Week 3**: Advanced Features
- Reports and analytics
- Bulk operations
- Custom workflows
- Troubleshooting

**Week 4**: Admin & Support
- User management
- Permissions and roles
- System monitoring
- Backup and recovery

**Support Channels**:
- 📧 Email: support@tsh.sale
- 💬 Slack: #tsh-erp-support
- 📱 Phone: +XXX-XXXX-XXXX (emergency only)
- 📖 Documentation: https://docs.tsh.sale

---

## Emergency Contacts

**Senior Engineer (You)**:
- Role: System Architecture & Deployment
- Contact: [Your Contact Info]
- Availability: 24/7 for critical issues

**Team Lead**:
- Role: Product & Business Logic
- Contact: [Team Lead Contact]

**DevOps Engineer** (if applicable):
- Role: Infrastructure & Monitoring
- Contact: [DevOps Contact]

**Zoho Support**:
- Support: https://help.zoho.com
- API Issues: api-support@zoho.com

---

## Appendix

### Essential Commands Cheat Sheet

```bash
# SSH to VPS
ssh root@167.71.39.50

# Check all containers
docker ps -a

# View logs (live)
docker logs -f tsh_erp_app

# View logs (last 100 lines)
docker logs tsh_erp_app --tail 100

# Restart container
docker restart tsh_erp_app

# Rebuild image
cd /home/deploy/TSH_ERP_Ecosystem && docker build -t tsh_erp_docker-app:latest .

# Check disk space
df -h

# Check Docker disk usage
docker system df

# Clean up Docker
docker system prune -a --volumes -f

# Database access
docker exec -it tsh_postgres psql -U postgres -d tsh_erp

# Redis access
docker exec -it tsh_redis redis-cli

# Health check
curl https://erp.tsh.sale/health

# Sync stats
curl https://erp.tsh.sale/api/zoho/sync/stats
```

### Environment Variables Reference

**Required Variables** (`.env` file):

```bash
# Application
APP_ENV=production
APP_DEBUG=False
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=erp.tsh.sale,localhost

# Database (Supabase)
DATABASE_URL=postgresql://user:pass@host:5432/dbname
DB_HOST=aws-1-eu-north-1.pooler.supabase.com
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_db_password

# Redis
REDIS_URL=redis://tsh_redis:6379/0

# Zoho Integration
ZOHO_CLIENT_ID=your_zoho_client_id
ZOHO_CLIENT_SECRET=your_zoho_client_secret
ZOHO_REFRESH_TOKEN=your_zoho_refresh_token
ZOHO_ORGANIZATION_ID=your_zoho_org_id

# Security
JWT_SECRET_KEY=your_jwt_secret
ENCRYPTION_KEY=your_encryption_key

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_email_password
```

### Database Schema Updates

When schema changes are needed:

```bash
# 1. Create migration
alembic revision -m "description of change"

# 2. Edit migration file
# Edit: alembic/versions/xxxxx_description_of_change.py

# 3. Test locally
alembic upgrade head

# 4. Deploy to production
ssh root@167.71.39.50 "cd /home/deploy/TSH_ERP_Ecosystem && docker exec tsh_erp_app alembic upgrade head"

# 5. Verify migration
ssh root@167.71.39.50 "docker exec tsh_postgres psql -U postgres -d tsh_erp -c '\dt'"
```

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | Nov 7, 2025 | Senior Engineer | Initial Tronix guide created |
| - | - | - | - |

---

## Notes

**This guide is a living document**. Update it whenever:
- Architecture changes
- New features are added
- Deployment process changes
- New issues and solutions are discovered
- Team feedback suggests improvements

**Remember**: As a senior engineer, your responsibility is not just to build and deploy, but to **document, mentor, and ensure the system can be maintained by others**.

---

**🚀 Stay sharp. Deploy smart. Build for the future.**

*End of Tronix Guide*
