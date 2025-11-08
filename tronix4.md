
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

