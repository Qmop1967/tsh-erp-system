- 🔄 Easy to extend with new integrations
- 📊 Centralized metrics and monitoring
- 🚀 Better performance (connection pooling, caching)
- 🛡️ Reduced attack surface

**For Future Developers:**
- 📚 Clear patterns to follow
- 🎓 Easy onboarding
- 🔍 Quick to find relevant code
- 💡 Understand system faster

---

**Remember:** Code consolidation and TDS centralization are NOT suggestions - they are MANDATORY architectural principles. Every piece of code that violates these principles creates technical debt that future engineers must pay.

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
