# 🚀 Tronix - TSH ERP Ecosystem Deployment & Integration Guide

**Senior Software Engineer's Handbook for Production Deployment**

---

## 🎯 Instruction Prompt

> **You are now acting as a highly experienced senior software engineer with deep expertise in scalable system design, clean code practices, DevOps workflows, and modern backend and frontend development. Your primary responsibility is to analyze existing codebases, propose improvements, eliminate redundancy, and provide high-quality, production-ready code. You will follow best practices, write maintainable and modular code, ensure architectural consistency, and document your work clearly for other developers. You must always check if a function or service already exists before creating a new one to avoid duplication.**

This is the core principle that guides all work on the TSH ERP Ecosystem. Every decision, every line of code, every architectural choice must align with this senior engineering mindset.

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

### Zoho API Best Practices & Instructions

**CRITICAL RULES FOR ZOHO INTEGRATION**

#### Rule 1: Always Use Pagination/Batch Processing

**Why:** Reduce API call consumption and avoid rate limits

**Implementation:**
```python
# ✅ CORRECT: Use pagination
result = await zoho_client.paginated_fetch(
    api_type=ZohoAPI.BOOKS,
    endpoint="items",
    page_size=100  # Process in batches of 100
)

# ❌ WRONG: Fetch all at once without pagination
result = await zoho_client.get("items")  # May exceed rate limits
```

**Batch Size Guidelines:**
- **Small datasets** (< 500 items): batch_size = 200
- **Medium datasets** (500-2,000): batch_size = 100
- **Large datasets** (> 2,000): batch_size = 50

#### Rule 2: API Priority System (Books → Inventory)

**Priority Order:**
1. **FIRST:** Try Zoho Books API
2. **SECOND:** Only if data not found, try Zoho Inventory API

**Why:** Zoho Inventory has VERY LIMITED API calls compared to Books

**Rate Limits:**
- **Zoho Books:** 100 requests/minute ✅ (Higher limit)
- **Zoho Inventory:** 25-50 requests/minute ⚠️ (Very limited)

**Implementation Pattern:**

```python
async def sync_product_with_priority(item_id: str):
    """
    Sync product data using priority system

    Priority: Books → Inventory
    """
    # Step 1: Try Zoho Books first
    try:
        product_data = await zoho_client.get(
            api_type=ZohoAPI.BOOKS,
            endpoint=f"items/{item_id}"
        )

        if product_data:
            logger.info(f"✅ Found in Zoho Books: {item_id}")
            return product_data

    except Exception as e:
        logger.warning(f"⚠️ Not in Books, trying Inventory: {e}")

    # Step 2: Only if not found in Books, try Inventory
    try:
        product_data = await zoho_client.get(
            api_type=ZohoAPI.INVENTORY,
            endpoint=f"items/{item_id}"
        )

        if product_data:
            logger.info(f"✅ Found in Zoho Inventory: {item_id}")
            return product_data

    except Exception as e:
        logger.error(f"❌ Not found in either Books or Inventory: {e}")
        raise
```

#### Rule 3: Batch Operations Structure

**For Bulk Sync Operations:**

```python
async def bulk_sync_with_batching():
    """
    Proper batch sync implementation
    """
    batch_size = 100
    page = 1
    has_more = True

    while has_more:
        # Fetch batch from Zoho Books (priority)
        response = await zoho_client.get(
            api_type=ZohoAPI.BOOKS,
            endpoint="items",
            params={
                "page": page,
                "per_page": batch_size
            }
        )

        items = response.get('items', [])
        page_context = response.get('page_context', {})

        # Process batch
        for item in items:
            await process_item(item)

        # Check if more pages exist
        has_more = page_context.get('has_more_page', False)
        page += 1

        # Rate limit protection: Small delay between batches
        await asyncio.sleep(0.5)  # 500ms delay

        logger.info(f"📦 Processed batch {page-1}: {len(items)} items")
```

#### Rule 4: API Endpoint Priority Matrix

| Data Type | Primary Source (Try First) | Secondary Source (Fallback) | Notes |
|-----------|----------------------------|----------------------------|-------|
| **Products/Items** | Zoho Books | Zoho Inventory | Books has more complete data |
| **Stock Levels** | Zoho Inventory | N/A | Only available in Inventory |
| **Customers** | Zoho Books | N/A | Only in Books |
| **Invoices** | Zoho Books | N/A | Only in Books |
| **Bills** | Zoho Books | N/A | Only in Books |
| **Warehouses** | Zoho Inventory | N/A | Only in Inventory |
| **Price Lists** | Zoho Books | N/A | Only in Books |

#### Rule 5: Error Handling & Retry Logic

**When Books API Fails:**

```python
async def resilient_zoho_fetch(item_id: str, max_retries: int = 3):
    """
    Fetch with retry and fallback logic
    """
    # Try Books API first (with retry)
    for attempt in range(max_retries):
        try:
            return await zoho_client.get(
                api_type=ZohoAPI.BOOKS,
                endpoint=f"items/{item_id}"
            )
        except RateLimitError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"⚠️ Rate limit hit, waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                logger.error("❌ Books API exhausted, trying Inventory...")
                break
        except Exception as e:
            logger.error(f"❌ Books API error: {e}")
            break

    # Fallback to Inventory API (with retry)
    for attempt in range(max_retries):
        try:
            return await zoho_client.get(
                api_type=ZohoAPI.INVENTORY,
                endpoint=f"items/{item_id}"
            )
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.warning(f"⚠️ Inventory retry {attempt+1}, waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"❌ All attempts failed: {e}")
                raise
```

#### Rule 6: API Call Monitoring

**Track API Usage:**

```python
# Track API calls per endpoint
api_call_stats = {
    "books": {"calls": 0, "failures": 0},
    "inventory": {"calls": 0, "failures": 0}
}

async def tracked_api_call(api_type: ZohoAPI, endpoint: str):
    """Call with tracking"""
    api_name = "books" if api_type == ZohoAPI.BOOKS else "inventory"

    try:
        api_call_stats[api_name]["calls"] += 1
        result = await zoho_client.get(api_type=api_type, endpoint=endpoint)
        return result
    except Exception as e:
        api_call_stats[api_name]["failures"] += 1
        raise

# Log stats periodically
logger.info(f"📊 API Stats: {api_call_stats}")
```

#### Rule 7: Sync Strategy Summary

**DO's:**
- ✅ Always use pagination (batch_size: 50-200)
- ✅ Try Zoho Books first for products
- ✅ Use Inventory ONLY for stock levels or when Books fails
- ✅ Implement exponential backoff for retries
- ✅ Add small delays (500ms) between batches
- ✅ Monitor API call counts
- ✅ Log which API source was used for each record

**DON'Ts:**
- ❌ Never fetch all data without pagination
- ❌ Don't start with Inventory API for products
- ❌ Don't hammer APIs without rate limiting
- ❌ Don't retry immediately after rate limit error
- ❌ Don't ignore Books API if Inventory seems "easier"

#### Rule 8: Real-World Example (Items Sync)

```python
async def sync_items_with_best_practices():
    """
    Complete example following all best practices
    """
    logger.info("🚀 Starting Items Sync (Books Priority)")

    # Configuration
    batch_size = 100
    books_items = []
    inventory_items = []

    # Step 1: Fetch from Books (Primary)
    logger.info("📘 Step 1: Fetching from Zoho Books...")
    books_result = await zoho_client.paginated_fetch(
        api_type=ZohoAPI.BOOKS,
        endpoint="items",
        page_size=batch_size
    )
    books_items = books_result.get('items', [])
    logger.info(f"   Found {len(books_items)} items in Books")

    # Step 2: Process Books items
    processed_ids = set()
    for item in books_items:
        await process_and_save(item, source="books")
        processed_ids.add(item['item_id'])

    # Step 3: Check Inventory ONLY for missing items
    logger.info("📦 Step 2: Checking Inventory for missing items...")
    inventory_result = await zoho_client.paginated_fetch(
        api_type=ZohoAPI.INVENTORY,
        endpoint="items",
        page_size=50  # Smaller batch for limited API
    )
    inventory_items = inventory_result.get('items', [])

    # Only process items NOT found in Books
    new_items = [
        item for item in inventory_items
        if item['item_id'] not in processed_ids
    ]

    logger.info(f"   Found {len(new_items)} NEW items in Inventory")

    for item in new_items:
        await process_and_save(item, source="inventory")

    # Summary
    logger.info("=" * 70)
    logger.info("✅ Sync Complete")
    logger.info(f"   Books Items: {len(books_items)}")
    logger.info(f"   Inventory-Only Items: {len(new_items)}")
    logger.info(f"   Total Unique Items: {len(processed_ids) + len(new_items)}")
    logger.info("=" * 70)
```

---

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

---

## Senior Engineering Standards & Best Practices

### 1. Token Management & Authentication Strategy

**Philosophy**: Proactive token management prevents service disruptions

#### 1.1 Automatic Token Refresh System

**Implementation**: `app/tds/integrations/zoho/auth.py`

```python
class ZohoAuthManager:
    """
    Handles Zoho OAuth 2.0 with automatic token refresh

    Features:
    - Auto-refresh 5 minutes before expiration
    - Background refresh task
    - Thread-safe token access
    - Retry logic with exponential backoff
    """

    def __init__(
        self,
        credentials: ZohoCredentials,
        auto_refresh: bool = True,
        refresh_buffer_minutes: int = 5
    ):
        self.credentials = credentials
        self.auto_refresh = auto_refresh
        self.refresh_buffer = timedelta(minutes=refresh_buffer_minutes)
        self._access_token = None
        self._token_expires_at = None
        self._refresh_task = None
        self._lock = asyncio.Lock()

    async def start(self):
        """Start auto-refresh background task"""
        if self.auto_refresh:
            self._refresh_task = asyncio.create_task(
                self._auto_refresh_loop()
            )

    async def _auto_refresh_loop(self):
        """Background task to refresh token before expiration"""
        while True:
            try:
                # Check if token needs refresh
                if self._needs_refresh():
                    await self.refresh_access_token()

                # Check every minute
                await asyncio.sleep(60)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Auto-refresh error: {e}")
                await asyncio.sleep(300)  # Wait 5 min on error
```

**Token Refresh Rules:**

1. **Always refresh 5 minutes before expiration**
2. **Retry up to 3 times with exponential backoff**
3. **Log all refresh attempts and failures**
4. **Never expose tokens in logs**
5. **Use environment variables, never hardcode**

#### 1.2 Rate Limiting Strategy

**Implementation**: `app/tds/integrations/zoho/utils/rate_limiter.py`

```python
class RateLimiter:
    """
    Token bucket rate limiter for Zoho API

    Limits:
    - Books API: 100 requests/minute
    - Inventory API: 25 requests/minute
    """

    def __init__(self, requests_per_minute: int = 100):
        self.rate = requests_per_minute
        self.tokens = requests_per_minute
        self.last_refill = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self):
        """Wait for available token"""
        async with self.lock:
            # Refill tokens based on time elapsed
            now = time.time()
            elapsed = now - self.last_refill
            refill_amount = elapsed * (self.rate / 60.0)

            self.tokens = min(
                self.rate,
                self.tokens + refill_amount
            )
            self.last_refill = now

            # Wait if no tokens available
            if self.tokens < 1:
                wait_time = (1 - self.tokens) / (self.rate / 60.0)
                await asyncio.sleep(wait_time)
                self.tokens = 1

            self.tokens -= 1
```

**Rate Limit Best Practices:**

- ✅ Never exceed 90% of rate limit (safety buffer)
- ✅ Implement exponential backoff on 429 errors
- ✅ Track API usage per endpoint
- ✅ Prioritize critical operations
- ✅ Queue non-urgent requests

#### 1.3 Token Validation Schedule

**Daily**: Verify token validity
```bash
# Cron job: daily_token_check.sh
#!/bin/bash
# Run at 2 AM daily
0 2 * * * /scripts/daily_token_check.sh

# Script content:
curl -X POST https://erp.tsh.sale/api/zoho/test-credentials \
  | jq '.status'

# If failed, send alert and refresh
```

**Monitoring**: Token health dashboard
```sql
-- Track token refresh history
CREATE TABLE zoho_token_refresh_log (
    id SERIAL PRIMARY KEY,
    refresh_type VARCHAR(20), -- 'auto' or 'manual'
    success BOOLEAN,
    error_message TEXT,
    token_expires_at TIMESTAMP,
    refreshed_at TIMESTAMP DEFAULT NOW()
);

-- Query recent refresh activity
SELECT * FROM zoho_token_refresh_log
ORDER BY refreshed_at DESC
LIMIT 10;
```

---

### 2. Code Quality & Consolidation Standards

**Philosophy**: Clean, DRY (Don't Repeat Yourself), maintainable code

#### 2.1 Code Duplication Detection

**Before any new code**, check for existing implementations:

```bash
#!/bin/bash
# check_duplication.sh

# Search for similar function names
grep -r "def sync_products" app/
grep -r "class ProductProcessor" app/
grep -r "async def fetch_zoho" app/

# Find similar patterns
rg "async def.*zoho.*fetch" app/
rg "class.*Sync.*Service" app/
```

**Consolidation Checklist:**

- [ ] Check `app/tds/` for existing TDS implementations
- [ ] Search for similar function names
- [ ] Review `app/services/` for legacy code
- [ ] Check `app/routers/` for duplicate endpoints
- [ ] Verify no redundant database models

#### 2.2 File Organization Rules

**TDS Core Structure** (Primary - Use This):
```
app/tds/
├── core/
│   ├── sync_engine.py       # Main sync orchestrator
│   └── events.py            # Event definitions
├── integrations/
│   └── zoho/
│       ├── client.py        # Unified API client
│       ├── auth.py          # Token management
│       ├── sync.py          # Sync operations
│       ├── webhooks.py      # Webhook handling
│       ├── stock_sync.py    # Stock sync
│       └── processors/      # Data transformers
│           ├── products.py
│           ├── customers.py
│           └── invoices.py
└── models/
    ├── sync_run.py
    └── sync_queue.py
```

**Legacy Structure** (Deprecated - Remove/Migrate):
```
app/services/
├── zoho_service.py         # ❌ DEPRECATED → Use tds/integrations/zoho/
├── zoho_sync.py            # ❌ DEPRECATED → Use tds/integrations/zoho/sync.py
└── zoho_processor.py       # ❌ DEPRECATED → Use tds/processors/
```

**Migration Strategy:**

1. **Identify** duplicate functionality
2. **Consolidate** into TDS structure
3. **Update** all imports
4. **Test** thoroughly
5. **Delete** old files
6. **Document** changes

#### 2.3 Code Review Checklist

**Before every commit:**

```markdown
## Code Quality Checklist

### Architecture
- [ ] Code follows TDS architecture
- [ ] No duplicate functionality
- [ ] Functions are in correct modules
- [ ] Proper separation of concerns

### Documentation
- [ ] Docstrings for all functions
- [ ] Type hints for parameters
- [ ] Comments for complex logic
- [ ] README updated if needed

### Testing
- [ ] Unit tests written
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Edge cases covered

### Security
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] SQL injection prevented
- [ ] XSS protection in place

### Performance
- [ ] No N+1 queries
- [ ] Proper indexing used
- [ ] Batch operations where possible
- [ ] Async operations utilized

### Error Handling
- [ ] Try-except blocks present
- [ ] Errors logged properly
- [ ] User-friendly error messages
- [ ] Retry logic implemented
```

---

### 3. Project Health & Size Optimization

**Philosophy**: Keep codebase lean, remove technical debt

#### 3.1 Codebase Analysis Workflow

**After every task completion:**

```bash
#!/bin/bash
# analyze_project.sh

echo "📊 TSH ERP Project Health Analysis"
echo "===================================="

# 1. Count lines of code by type
echo -e "\n📝 Lines of Code:"
find app/ -name "*.py" | xargs wc -l | tail -1

# 2. Find large files (> 500 lines)
echo -e "\n📦 Large Files (>500 lines):"
find app/ -name "*.py" -exec wc -l {} + | awk '$1 > 500' | sort -rn

# 3. Find duplicate code
echo -e "\n🔍 Potential Duplicates:"
fdupes -r app/ -S

# 4. Find unused imports
echo -e "\n🗑️  Unused Imports:"
autoflake --check --recursive app/

# 5. Find dead code
echo -e "\n💀 Dead Code:"
vulture app/ --min-confidence 80

# 6. Count TODO/FIXME
echo -e "\n📌 TODOs and FIXMEs:"
grep -r "TODO\|FIXME" app/ | wc -l

# 7. Security vulnerabilities
echo -e "\n🔐 Security Check:"
bandit -r app/ -ll

# 8. Dependencies audit
echo -e "\n📦 Dependencies:"
pip list --outdated
```

**Run after every major feature**:
```bash
./scripts/analyze_project.sh > reports/health_$(date +%Y%m%d).txt
```

#### 3.2 Files to Remove/Archive

**Criteria for Removal:**

1. **Archived/Old Files**:
   ```bash
   # Check for archived directories
   find . -type d -name "*archive*" -o -name "*old*" -o -name "*backup*"

   # Move to archive directory (not tracked by git)
   mkdir -p .archive/$(date +%Y%m%d)
   mv app/services/old_zoho_* .archive/$(date +%Y%m%d)/
   ```

2. **Unused Scripts**:
   ```bash
   # Find scripts not executed in last 30 days
   find scripts/ -type f -name "*.py" -mtime +30

   # Verify with git log
   git log --since="30 days ago" --name-only -- scripts/
   ```

3. **Test Fixtures** (if not needed):
   ```bash
   # Large test data files
   find tests/ -name "*.json" -size +1M
   find tests/ -name "*.csv" -size +1M
   ```

4. **Temporary Files**:
   ```bash
   # Python cache
   find . -type d -name "__pycache__" -exec rm -rf {} +
   find . -name "*.pyc" -delete
   find . -name "*.pyo" -delete

   # OS files
   find . -name ".DS_Store" -delete
   find . -name "Thumbs.db" -delete
   ```

**Monthly Cleanup Schedule:**

```bash
#!/bin/bash
# monthly_cleanup.sh

# Run on 1st of every month
echo "🧹 Monthly Project Cleanup"

# 1. Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +

# 2. Remove old logs
find logs/ -name "*.log" -mtime +30 -delete

# 3. Clean Docker
docker system prune -a --volumes -f

# 4. Archive old migrations (if needed)
# ... archive logic ...

# 5. Update .gitignore for ignored patterns
```

#### 3.3 Project Size Targets

**Optimal Sizes:**

| Component | Target Size | Max Size | Action if Exceeded |
|-----------|------------|----------|-------------------|
| Single File | < 300 lines | 500 lines | Split into modules |
| Function | < 50 lines | 100 lines | Extract subfunctions |
| Class | < 300 lines | 500 lines | Split responsibilities |
| Module | < 10 files | 20 files | Create subpackages |
| Dependencies | < 50 packages | 75 packages | Remove unused |

**Monitoring Script:**

```python
# scripts/size_monitor.py
import os
from pathlib import Path

def analyze_file_sizes(root_dir="app/"):
    """Analyze and report file sizes"""
    large_files = []

    for path in Path(root_dir).rglob("*.py"):
        lines = len(path.read_text().splitlines())

        if lines > 500:
            large_files.append((str(path), lines))

    # Sort by size
    large_files.sort(key=lambda x: x[1], reverse=True)

    print("⚠️  Files exceeding 500 lines:")
    for file, lines in large_files:
        print(f"   {file}: {lines} lines")

    return large_files

if __name__ == "__main__":
    analyze_file_sizes()
```

---

### 4. Daily Data Investigation System

**Philosophy**: Trust but verify - daily data consistency checks

#### 4.1 Automated Daily Comparison

**Implementation**: `scripts/daily_data_investigation.py`

```python
#!/usr/bin/env python3
"""
Daily Data Investigation System
================================

Compares data counts between Zoho and TSH ERP
Alerts on discrepancies

Run daily at 3 AM via cron:
0 3 * * * /usr/bin/python3 /path/to/daily_data_investigation.py
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, Any

from app.tds.integrations.zoho import UnifiedZohoClient, ZohoAPI
from app.db.database import get_async_db

class DataInvestigator:
    """Daily data consistency checker"""

    async def investigate(self) -> Dict[str, Any]:
        """Run full investigation"""

        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy",
            "discrepancies": [],
            "entities": {}
        }

        # Check each entity type
        entities_to_check = [
            ("products", "items", "products"),
            ("customers", "contacts", "customers"),
            ("invoices", "invoices", "invoices"),
            ("orders", "salesorders", "sales_orders")
        ]

        for entity_name, zoho_endpoint, db_table in entities_to_check:
            result = await self._compare_entity(
                entity_name, zoho_endpoint, db_table
            )
            report["entities"][entity_name] = result

            if result["discrepancy"]:
                report["discrepancies"].append(result)
                report["status"] = "warning"

        # Save report
        await self._save_report(report)

        # Send alert if discrepancies found
        if report["discrepancies"]:
            await self._send_alert(report)

        return report

    async def _compare_entity(
        self,
        entity_name: str,
        zoho_endpoint: str,
        db_table: str
    ) -> Dict[str, Any]:
        """Compare counts for single entity type"""

        # Get Zoho count
        zoho_count = await self._get_zoho_count(zoho_endpoint)

        # Get database count
        db_count = await self._get_db_count(db_table)

        # Calculate discrepancy
        difference = abs(zoho_count - db_count)
        percentage = (difference / zoho_count * 100) if zoho_count > 0 else 0

        result = {
            "entity": entity_name,
            "zoho_count": zoho_count,
            "db_count": db_count,
            "difference": difference,
            "discrepancy_percentage": round(percentage, 2),
            "discrepancy": percentage > 1.0,  # Alert if > 1% difference
            "timestamp": datetime.utcnow().isoformat()
        }

        return result

    async def _get_zoho_count(self, endpoint: str) -> int:
        """Get entity count from Zoho"""
        # Initialize Zoho client
        zoho_client = await self._get_zoho_client()

        response = await zoho_client.get(
            api_type=ZohoAPI.BOOKS,
            endpoint=endpoint,
            params={"per_page": 1, "page": 1}
        )

        page_context = response.get('page_context', {})
        return page_context.get('total', 0)

    async def _get_db_count(self, table: str) -> int:
        """Get entity count from database"""
        from sqlalchemy import text

        async for db in get_async_db():
            try:
                query = text(f"SELECT COUNT(*) FROM {table}")
                result = await db.execute(query)
                count = result.scalar()
                return count
            finally:
                break

        return 0

    async def _save_report(self, report: Dict[str, Any]):
        """Save investigation report to database"""
        from sqlalchemy import text

        async for db in get_async_db():
            try:
                query = text("""
                    INSERT INTO data_investigation_reports
                    (report_date, status, report_data, created_at)
                    VALUES (CURRENT_DATE, :status, :report_data, NOW())
                """)

                await db.execute(query, {
                    "status": report["status"],
                    "report_data": json.dumps(report)
                })

                await db.commit()
            finally:
                break

    async def _send_alert(self, report: Dict[str, Any]):
        """Send alert if discrepancies found"""
        # Email alert
        subject = f"⚠️ TSH ERP Data Discrepancy Alert - {datetime.utcnow().date()}"

        body = f"""
        Data Investigation Report
        =========================

        Status: {report['status']}
        Timestamp: {report['timestamp']}

        Discrepancies Found:
        """

        for disc in report['discrepancies']:
            body += f"""

            Entity: {disc['entity']}
            - Zoho Count: {disc['zoho_count']}
            - Database Count: {disc['db_count']}
            - Difference: {disc['difference']} ({disc['discrepancy_percentage']}%)
            """

        # Send email (implement email sending logic)
        # await send_email(subject, body)

        # Log alert
        print(f"🚨 ALERT: {subject}")
        print(body)

# Run investigation
async def main():
    investigator = DataInvestigator()
    report = await investigator.investigate()

    print("=" * 70)
    print("📊 Daily Data Investigation Report")
    print("=" * 70)
    print(json.dumps(report, indent=2))
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
```

**Database Schema for Reports:**

```sql
-- Create investigation reports table
CREATE TABLE IF NOT EXISTS data_investigation_reports (
    id SERIAL PRIMARY KEY,
    report_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'healthy', 'warning', 'critical'
    report_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for date queries
CREATE INDEX idx_investigation_date ON data_investigation_reports(report_date DESC);

-- View recent investigations
CREATE VIEW recent_investigations AS
SELECT
    report_date,
    status,
    (report_data->>'timestamp')::TIMESTAMP as investigated_at,
    jsonb_array_length(report_data->'discrepancies') as discrepancy_count
FROM data_investigation_reports
ORDER BY report_date DESC
LIMIT 30;
```

#### 4.2 Cron Job Setup

```bash
# Add to VPS crontab
ssh root@167.71.39.50

# Edit crontab
crontab -e

# Add daily investigation at 3 AM
0 3 * * * cd /home/deploy/TSH_ERP_Ecosystem && /usr/bin/python3 scripts/daily_data_investigation.py >> /var/log/tsh_data_investigation.log 2>&1
```

#### 4.3 Investigation Dashboard

**Endpoint**: `GET /api/admin/data-investigation`

```python
@router.get("/data-investigation")
async def get_investigation_dashboard(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get recent investigation reports"""

    from sqlalchemy import text

    query = text("""
        SELECT
            report_date,
            status,
            report_data
        FROM data_investigation_reports
        WHERE report_date >= CURRENT_DATE - :days
        ORDER BY report_date DESC
    """)

    result = db.execute(query, {"days": days})
    reports = result.fetchall()

    return {
        "total_reports": len(reports),
        "healthy_count": sum(1 for r in reports if r[1] == 'healthy'),
        "warning_count": sum(1 for r in reports if r[1] == 'warning'),
        "reports": [
            {
                "date": str(r[0]),
                "status": r[1],
                "data": r[2]
            }
            for r in reports
        ]
    }
```

---

### 5. Consumer App Product Filtering

**Philosophy**: Only show products with available stock

#### 5.1 Consumer Price List Requirement

**CRITICAL REQUIREMENT**: The Flutter Consumer App MUST display products using the **Consumer Price List** only. **NO FALLBACK TO BASE PRICE IS ALLOWED**.

**Implementation Details**:

1. **Backend Endpoints**:
   - `GET /api/consumer/products` - Returns products with Consumer pricelist pricing ONLY
   - `GET /api/bff/mobile/consumer/products` - BFF endpoint with Consumer pricelist pricing ONLY
   
2. **Price List Selection**:
   - Products MUST use the pricelist with code **"consumer_iqd"**
   - Currency MUST be **"IQD"** (Iraqi Dinar)
   - **CRITICAL**: NO fallback to base price - products without Consumer prices are NOT displayed
   
3. **Query Implementation** (`app/routers/consumer_api.py:138-170` and `app/bff/mobile/router.py:1234-1264`):
   ```sql
   LEFT JOIN LATERAL (
       SELECT pp.price, pp.currency
       FROM product_prices pp
       JOIN price_lists pl ON pp.pricelist_id = pl.id
       WHERE pp.product_id = p.id
         AND pl.code = 'consumer_iqd'  -- Use code for exact match
         AND (pp.currency = 'IQD' OR pp.currency IS NULL)
         AND pp.price > 0
       ORDER BY pp.price DESC
       LIMIT 1
   ) consumer_price ON true
   WHERE ...
     AND consumer_price.price IS NOT NULL 
     AND consumer_price.price > 0  -- CRITICAL: Only show products with Consumer prices
   ```
   
   **Important Notes**:
   - Table name is `price_lists` (with underscore), NOT `pricelists`
   - Use `pl.code = 'consumer_iqd'` for exact match (more reliable than name matching)
   - WHERE clause MUST require Consumer price (no OR condition allowing base price)
   
4. **Response Format**:
   ```json
   {
     "price": 15000.00,
     "currency": "IQD"
   }
   ```

5. **Validation in CI/CD**:
   - GitHub Actions workflow (`deploy-staging.yml`) includes `validate-consumer-pricelist` step
   - Validation script (`scripts/validate_consumer_pricelist.py`) checks:
     - Consumer price list exists
     - All products with stock have Consumer prices
     - No products are missing Consumer prices
   - Deployment FAILS if any product lacks Consumer price list price
   - Price currency MUST be IQD

6. **Root Cause Fix (November 2025)**:
   - **Issue**: Queries used wrong table name (`pricelists` instead of `price_lists`)
   - **Issue**: Fallback logic allowed base prices when Consumer prices missing
   - **Fix**: Changed table name to `price_lists`, removed fallback, enforced Consumer price requirement
   - **Result**: Consumer app now ONLY shows products with Consumer price list prices

**Flutter App Requirements**:
- Display Consumer pricelist price for all products
- Format prices in IQD currency
- Show currency symbol (IQD) or formatted as "15,000 IQD"

#### 5.2 API Filtering Rules

**Already Implemented**: `app/routers/consumer_api.py:119`

```python
# WHERE clause filters for products with stock
where_conditions = [
    "p.is_active = true",           # Only active products
    "p.actual_available_stock > 0"  # Only products with stock
]
```

**Additional Filters (Optional):**

```python
# Add to where_conditions based on requirements
where_conditions.extend([
    "p.price > 0",                  # Only products with price
    "p.image_url IS NOT NULL",      # Only products with images (optional)
    "p.category IS NOT NULL"        # Only categorized products (optional)
])
```

#### 5.2 Stock Threshold Configuration

**Environment Variable**: `.env`
```bash
# Minimum stock to display
CONSUMER_MIN_STOCK=1

# Low stock warning threshold
CONSUMER_LOW_STOCK_THRESHOLD=10
```

**Implementation**:
```python
min_stock = int(os.getenv('CONSUMER_MIN_STOCK', 1))
where_conditions.append(f"p.actual_available_stock >= {min_stock}")
```

#### 5.3 Real-time Stock Updates

**Webhook Integration**: When stock changes in Zoho, update immediately

```python
@router.post("/webhooks/stock-update")
async def handle_stock_webhook(
    payload: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Handle real-time stock updates from Zoho"""

    item_id = payload.get('item_id')
    new_stock = payload.get('actual_available_stock')

    # Update database
    db.execute(
        "UPDATE products SET actual_available_stock = :stock "
        "WHERE zoho_item_id = :item_id",
        {"stock": new_stock, "item_id": item_id}
    )
    db.commit()

    # Clear cache
    await redis.delete(f"product:{item_id}")

    return {"status": "success"}
```

---

### 6. TDS Core Responsibilities

**Philosophy**: TDS = Single Source of Truth for all sync operations

#### 6.1 TDS Architecture Mandate

**ALL Zoho operations MUST go through TDS:**

```
❌ WRONG: Direct Zoho API calls from routers
app/routers/products.py → zoho_client.get("items")

✅ CORRECT: Through TDS
app/routers/products.py → TDS Sync Orchestrator → Zoho Client
```

#### 6.2 TDS Responsibilities

**TDS Core (`app/tds/`) is responsible for:**

1. **Authentication**:
   - Token management
   - Auto-refresh
   - Rate limiting

2. **API Communication**:
   - All Zoho API calls
   - Request/response handling
   - Error handling and retries

3. **Data Transformation**:
   - Zoho format → TSH format
   - Validation
   - Enrichment

4. **Synchronization**:
   - Webhooks processing
   - Bulk sync operations
   - Queue management

5. **Event Publishing**:
   - Sync events
   - Status updates
   - Error notifications

**Other modules MUST NOT:**
- ❌ Make direct Zoho API calls
- ❌ Handle OAuth tokens
- ❌ Transform Zoho data
- ❌ Manage sync queue

**Migration Plan for Legacy Code:**

```bash
# Find legacy direct Zoho calls
grep -r "zoho_client\|ZohoService" app/routers/ app/services/

# Move to TDS
# Example:
# OLD: app/services/product_service.py → zoho_client.get("items")
# NEW: app/services/product_service.py → tds.sync.sync_entity(EntityType.PRODUCTS)
```

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | Nov 7, 2025 | Senior Engineer | Initial Tronix guide created |
| 1.1.0 | Nov 7, 2025 | Senior Engineer | Added senior engineering standards |
|  |  |  | - Token management strategy |
|  |  |  | - Code consolidation guidelines |
|  |  |  | - Daily data investigation system |
|  |  |  | - Consumer app filtering |
|  |  |  | - TDS core responsibilities |

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
