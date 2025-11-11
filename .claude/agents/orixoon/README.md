# Orixoon Pre-Deployment Testing Agent with Auto-Healing

**Version:** 2.0.0
**Status:** Production Ready (Core Phases + Auto-Healing Implemented)

Orixoon is a comprehensive pre-deployment testing agent for the TSH ERP Ecosystem that ensures zero-downtime deployments by validating all critical systems before allowing production releases. **Now with intelligent auto-healing capabilities** to automatically fix common service issues.

---

## 🎯 Mission

Block broken deployments before they reach production by running thorough validation across all system layers:
- ✅ Environment & Infrastructure
- ✅ Service Health & Connectivity
- ✅ Database Integrity
- ✅ API Contracts (especially Flutter consumer app)
- ✅ Zoho Integration
- ✅ Performance Baselines
- ✅ End-to-End Workflows

---

## 📋 Test Phases

### Implemented Phases (Ready for Use)

| Phase | Name | Status | Critical | Duration |
|-------|------|--------|----------|----------|
| 1 | Pre-Flight Checks | ✅ Complete | Yes | 2-3 min |
| 2 | Service Health | ✅ Complete | Yes | 3-5 min |
| 3 | Database Validation | ✅ Complete | Yes | 3-5 min |
| 6 | Flutter API Tests | ✅ Complete | Yes | 4-6 min |

### Placeholder Phases (To Be Expanded)

| Phase | Name | Status | Critical | Duration |
|-------|------|--------|----------|----------|
| 4 | BFF Endpoint Validation | ⏳ Placeholder | No | 10-12 min |
| 5 | Zoho Integration Test | ⏳ Placeholder | No | 3-5 min |
| 7 | Visual Price Verification | ⏳ Placeholder | No | 5-7 min |
| 8 | E2E Workflows | ⏳ Placeholder | No | 5-8 min |
| 9 | Performance Baseline | ⏳ Placeholder | No | 3-5 min |
| 10 | Post-Deployment Verification | ⏳ Placeholder | No | 2-3 min |

---

## 🚀 Quick Start

### Manual Execution

```bash
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem/.claude/agents/orixoon
bash tools/orixoon_orchestrator.sh
```

### Integrated with Deployment

Orixoon automatically runs during production deployment via `scripts/deploy_production.sh`.

---

## 📊 Test Phase Details

### Phase 1: Pre-Flight Checks ⚠️ CRITICAL

**Purpose:** Validate environment readiness

**Checks:**
- ✓ Required environment variables present
- ✓ Database connectivity (PostgreSQL)
- ✓ Redis connectivity
- ✓ Zoho API credentials configured
- ✓ Disk space available (>5GB)
- ✓ Memory available (>20%)
- ✓ Docker daemon running
- ✓ Required ports available/in use
- ✓ Backup directory writable

**Failure Impact:** Deployment BLOCKED

---

### Phase 2: Service Health ⚠️ CRITICAL

**Purpose:** Verify all services are running and healthy

**Checks:**
- ✓ Docker containers running (app, postgres, redis, neurolink)
- ✓ Main API health (`http://localhost:8000/health`)
- ✓ Public API health (`https://erp.tsh.sale/health`)
- ✓ Neurolink health (`http://localhost:8002/health`)
- ✓ TDS Dashboard (`http://localhost:3000`)
- ✓ PostgreSQL responding (`pg_isready`)
- ✓ Redis responding (`redis-cli ping`)
- ✓ Background workers active (Uvicorn, TDS scheduler)
- ✓ Authentication endpoints accessible
- ✓ No critical errors in recent logs (last 5 min)

**Failure Impact:** Deployment BLOCKED

---

### Phase 3: Database Validation ⚠️ CRITICAL

**Purpose:** Ensure database integrity and migrations are current

**Checks:**
- ✓ Alembic migrations up to date
- ✓ All critical tables exist (users, products, orders, etc.)
- ✓ Critical data counts reasonable (users > 0, admin users > 0)
- ✓ Connection pool healthy (<90% utilization)
- ✓ No table locks or blocking queries

**Failure Impact:** Deployment BLOCKED

---

### Phase 6: Flutter API Tests ⚠️ CRITICAL

**Purpose:** Test API contracts that Flutter consumer app depends on

**Endpoints Tested:**
- ✓ Price List API (`/api/bff/mobile/tds/pricelists`) - CRITICAL
- ✓ Products List API (`/api/bff/mobile/tds/products`) - CRITICAL
- ✓ Categories API (`/api/bff/mobile/tds/categories`)
- ✓ Cart API (`/api/bff/mobile/tds/cart`) - CRITICAL

**Validation:**
- Response status codes (200, 401 expected)
- Response format matches Flutter Dart models
- Required fields present
- Consumer price list exists
- Response times acceptable (<10s)

**Failure Impact:** Deployment BLOCKED

---

## 🔧 Configuration

Edit `config.json` to customize behavior:

```json
{
  "server": {
    "host": "167.71.39.50",
    "base_url": "http://localhost:8000",
    "public_url": "https://erp.tsh.sale"
  },
  "thresholds": {
    "api_response_time_target_ms": 3000,
    "disk_space_minimum_gb": 5,
    "error_log_threshold": 50
  },
  "deployment_integration": {
    "block_on_critical_failure": true,
    "allow_with_warnings": true
  }
}
```

---

## 📈 Exit Codes

- **0**: All tests passed (deployment allowed)
- **1**: Critical failure (deployment blocked)
- **2**: Warnings only (deployment allowed with warnings)

---

## 🛠️ Expanding Test Phases

Placeholder phases can be expanded by editing the corresponding Python scripts:

### Example: Expanding Phase 4 (BFF Validator)

```bash
vim tools/04_bff_validator.py
```

Add logic to test all 198 BFF endpoints across 11 mobile apps.

### Example: Expanding Phase 7 (Visual Price Verification)

Integrate with Chrome DevTools MCP:

```python
# Use mcp__chrome-devtools tools
from claude_code import mcp_chrome_devtools

# Navigate to consumer.tsh.sale
# Take snapshots
# Verify prices match API data
```

---

## 🧪 Testing Orixoon Locally

Test individual phases:

```bash
# Test pre-flight checks
python3 tools/01_pre_flight_check.py

# Test service health
python3 tools/02_service_health.py

# Test database validation
python3 tools/03_database_validator.py

# Test Flutter APIs
python3 tools/06_flutter_api_tester.py
```

---

## 📁 Directory Structure

```
.claude/agents/orixoon/
├── agent.md                          # Agent instructions
├── config.json                       # Configuration
├── README.md                         # This file
├── tools/
│   ├── 01_pre_flight_check.py       # ✅ Complete
│   ├── 02_service_health.py         # ✅ Complete
│   ├── 03_database_validator.py     # ✅ Complete
│   ├── 04_bff_validator.py          # ⏳ Placeholder
│   ├── 05_zoho_integration_test.py  # ⏳ Placeholder
│   ├── 06_flutter_api_tester.py     # ✅ Complete
│   ├── 07_visual_price_verify.py    # ⏳ Placeholder (needs MCP)
│   ├── 08_e2e_workflows.py          # ⏳ Placeholder
│   ├── 09_performance_baseline.py   # ⏳ Placeholder
│   ├── 10_post_deploy_verify.py     # ⏳ Placeholder
│   └── orixoon_orchestrator.sh      # ✅ Complete
└── reports/                          # Test reports (timestamped)
    └── 20250110_143000/
        ├── 01_pre_flight_check.py.json
        ├── 02_service_health.py.json
        ├── 03_database_validator.py.json
        └── ...
```

---

## 🔗 Integration with Deployment Pipeline

### Method 1: Manual Integration (Recommended)

Add to `scripts/deploy_production.sh` before service restart:

```bash
# Run Orixoon pre-deployment tests
echo "Running pre-deployment tests (Orixoon)..."
bash "$PROJECT_DIR/.claude/agents/orixoon/tools/orixoon_orchestrator.sh"

if [ $? -ne 0 ]; then
    echo "❌ Pre-deployment tests failed. Deployment aborted."
    exit 1
fi

echo "✅ Pre-deployment tests passed"
```

### Method 2: GitHub Actions

Add to `.github/workflows/ci-deploy.yml`:

```yaml
- name: Run Orixoon Pre-Deployment Tests
  run: |
    cd .claude/agents/orixoon
    bash tools/orixoon_orchestrator.sh
```

---

## 📊 Report Format

Each phase generates a JSON report:

```json
{
  "phase": "01_pre_flight_check",
  "status": "passed",
  "timestamp": "2025-01-10T14:30:00Z",
  "duration": 2.3,
  "summary": {
    "total_checks": 9,
    "passed": 9,
    "failed": 0,
    "warnings": 0,
    "critical_failures": 0
  },
  "checks": [
    {
      "name": "database_connectivity",
      "status": "passed",
      "message": "PostgreSQL connected: PostgreSQL 15.3...",
      "critical": true,
      "timestamp": "2025-01-10T14:30:01Z"
    }
  ]
}
```

---

## 🚨 Failure Handling

### Critical Failure (Blocks Deployment)

1. **Immediate Stop:** Deployment process halts
2. **Report Generation:** Detailed failure report saved
3. **Evidence Capture:** Logs, screenshots, error traces saved
4. **Team Notification:** (If configured) Slack/email alerts sent
5. **Remediation:** Review report and fix issues before retrying

### Warning (Allows Deployment)

1. **Log Warning:** Details logged to report
2. **Continue Deployment:** Process continues
3. **Include in Report:** Warnings included in final summary
4. **Monitor:** Watch closely post-deployment

---

## 🎯 Success Criteria

**Deployment ALLOWED if:**
- ✅ All critical checks pass
- ✅ Warnings only on non-critical systems
- ✅ Performance within acceptable range
- ✅ Zero critical failures

**Deployment BLOCKED if:**
- ❌ Any service health check fails
- ❌ Database or Redis unreachable
- ❌ Authentication broken
- ❌ Flutter consumer price API fails
- ❌ > 10 failed items in Zoho sync queue
- ❌ Background workers not running

---

## 🔮 Future Enhancements

### Priority 1 (Next Sprint)
- [ ] Complete BFF endpoint validator (all 198 endpoints)
- [ ] Complete Zoho integration tester (API + sync queue health)
- [ ] Integrate Chrome DevTools MCP for visual verification

### Priority 2
- [ ] Add E2E workflow tests (complete order, product management)
- [ ] Add performance baseline and load testing
- [ ] Add post-deployment verification

### Priority 3
- [ ] Slack/email notifications on failures
- [ ] HTML report generation with charts
- [ ] Auto-rollback on critical failures
- [ ] Integration with monitoring dashboards

---

## 🐛 Troubleshooting

### Issue: "Cannot connect to database"

**Solution:**
- Check PostgreSQL is running: `docker ps | grep postgres`
- Verify DATABASE_URL in `.env.production`
- Test connection: `psql $DATABASE_URL -c "SELECT 1"`

### Issue: "Redis not responding"

**Solution:**
- Check Redis container: `docker ps | grep redis`
- Test Redis: `redis-cli -h localhost -p 6379 ping`
- Restart Redis: `docker restart redis`

### Issue: "Flutter API tests failing"

**Solution:**
- Check main API is running: `curl http://localhost:8000/health`
- Verify BFF endpoints exist: `curl http://localhost:8000/api/bff/mobile/tds/products`
- Check logs: `docker logs app | tail -100`

---

## 📞 Support

- **Documentation:** `/Users/khaleelal-mulla/TSH_ERP_Ecosystem/.claude/agents/orixoon/agent.md`
- **Configuration:** `/Users/khaleelal-mulla/TSH_ERP_Ecosystem/.claude/agents/orixoon/config.json`
- **Reports:** `/Users/khaleelal-mulla/TSH_ERP_Ecosystem/.claude/agents/orixoon/reports/`

---

## 📝 Version History

- **v1.0.0** (2025-01-10): Initial release with 4 core phases implemented
  - ✅ Pre-Flight Checks
  - ✅ Service Health
  - ✅ Database Validation
  - ✅ Flutter API Tests
  - ⏳ 6 placeholder phases for future expansion

---

**Orixoon** - Your deployment guardian, ensuring quality releases every time. 🚀
