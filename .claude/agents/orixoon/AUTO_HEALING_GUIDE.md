# Orixoon Auto-Healing Guide

## 🔧 What is Auto-Healing?

Orixoon Auto-Healing is an intelligent system that automatically detects and fixes common service issues during pre-deployment testing. Instead of just reporting failures, Orixoon can now **automatically repair** problems and re-test to ensure deployment success.

---

## 🚀 Quick Start

### Enable Auto-Healing

```bash
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem/.claude/agents/orixoon

# Run with auto-healing enabled
bash tools/orixoon_orchestrator.sh --auto-heal
```

### Dry Run Mode (Recommended First)

```bash
# See what would be healed without making changes
bash tools/orixoon_orchestrator.sh --auto-heal --dry-run
```

---

## 🩹 What Can Be Auto-Healed?

### Container Issues

| Issue | Healing Action | Risk Level |
|-------|----------------|------------|
| Container not running | Start container | Low |
| Container unhealthy | Restart container | Low |
| Container stuck | Force restart | Medium |

**Example:**
```
❌ Docker container 'redis' not running
🔧 HEALING: Starting redis container...
✅ HEALED: Container started successfully
✓ Re-test: Redis now responding
```

### Database Issues

| Issue | Healing Action | Risk Level |
|-------|----------------|------------|
| Connection pool exhausted | Kill idle connections (>5min) | Low |
| Table locks detected | Clear blocking queries | Medium |
| Stuck transactions | Terminate idle transactions | Medium |

**Example:**
```
❌ Database connection pool 90% full
🔧 HEALING: Terminating 15 idle connections...
✅ HEALED: Connection pool now at 45%
✓ Re-test: Database healthy
```

### Redis Issues

| Issue | Healing Action | Risk Level |
|-------|----------------|------------|
| Redis not responding | Restart Redis container | Low |
| Memory full | Flush keys expiring soon | Low |
| High memory usage | Clear expired keys | Low |

**Example:**
```
❌ Redis not responding to PING
🔧 HEALING: Restarting redis container...
✅ HEALED: Redis restarted, responding normally
✓ Re-test: Redis healthy
```

### Background Worker Issues

| Issue | Healing Action | Risk Level |
|-------|----------------|------------|
| Uvicorn workers down | Restart main service | Medium |
| TDS scheduler stopped | Restart TDS service | Low |
| Worker not processing | Restart worker | Low |

**Example:**
```
❌ TDS auto-sync scheduler not running
🔧 HEALING: Restarting tds-scheduler service...
✅ HEALED: Scheduler restarted successfully
✓ Re-test: TDS scheduler active
```

### Zoho Integration Issues

| Issue | Healing Action | Risk Level |
|-------|----------------|------------|
| Sync queue stuck | Requeue failed items | Low |
| Too many pending items | Clear dead letter queue | Medium |
| Sync delay >1 hour | Reset processing status | Medium |

**Example:**
```
❌ Zoho sync queue has 75 stuck items
🔧 HEALING: Resetting 50 items, moving 25 to DLQ...
✅ HEALED: Queue cleared, sync resumed
✓ Re-test: Sync queue healthy (<10 items)
```

### Application Errors

| Issue | Healing Action | Risk Level |
|-------|----------------|------------|
| High error rate (>50 errors/5min) | Restart application | High |
| Memory leak detected | Restart application | High |
| Crash loop detected | Clear state and restart | High |

**Example:**
```
❌ High error rate: 75 errors in last 5 minutes
🔧 HEALING: Restarting main application...
⚠️  Confirmation required (High risk action)
✅ HEALED: Application restarted, error rate cleared
✓ Re-test: No errors in last 5 minutes
```

---

## ⚙️ Configuration

Edit `healing_config.json` to customize healing behavior:

```json
{
  "auto_healing": {
    "enabled": true,
    "dry_run": false,
    "max_healing_attempts": 3,
    "retry_delay_seconds": 10
  },

  "healing_actions": {
    "container_not_running": {
      "enabled": true,
      "action": "restart_container",
      "max_retries": 2,
      "timeout_seconds": 30,
      "requires_confirmation": false
    },

    "high_error_rate": {
      "enabled": true,
      "action": "restart_application",
      "max_retries": 1,
      "error_threshold": 50,
      "timeout_seconds": 60,
      "requires_confirmation": true  // ⚠️ High risk
    }
  },

  "safety_limits": {
    "max_container_restarts_per_session": 5,
    "max_database_operations_per_session": 3,
    "prevent_cascade_restarts": true
  }
}
```

---

## 🛡️ Safety Features

### 1. Dry Run Mode
Test healing actions without making changes:
```bash
bash tools/orixoon_orchestrator.sh --auto-heal --dry-run
```

### 2. Safety Limits
- Maximum 5 container restarts per session
- Maximum 3 database operations per session
- Cooldown period between actions (60 seconds)
- Prevents cascade restarts

### 3. Risk-Based Confirmation
High-risk actions require manual confirmation:
- Application restarts
- Force-killing processes
- Clearing all cache
- Emergency cleanup

### 4. Blacklist Protection
Never touches:
- PostgreSQL master process
- Init processes
- Protected tables (users, roles, permissions)

### 5. Healing Logs
All actions logged with:
- Timestamp
- Issue detected
- Action taken
- Success/failure status
- Details and output

---

## 📊 Healing Workflow

```
1. TEST PHASE RUNS
   ↓
2. ISSUE DETECTED
   ↓
3. Check if healable? ----NO----> Report failure, block deployment
   ↓ YES
4. Check healing config enabled?
   ↓ YES
5. Check safety limits OK?
   ↓ YES
6. Check requires confirmation?
   ↓ NO (or YES + user confirms)
7. EXECUTE HEALING ACTION
   ↓
8. Wait for stabilization (5-10s)
   ↓
9. RE-RUN TEST PHASE
   ↓
10. Issue fixed? ----YES----> Continue deployment
    ↓ NO
11. Retry (up to max_retries)
    ↓
12. Still failed? ----YES----> Report failure, block deployment
```

---

## 📈 Success Metrics

Orixoon tracks healing effectiveness:

```json
{
  "auto_healing": {
    "summary": {
      "total_actions": 5,
      "successful": 4,
      "failed": 1,
      "success_rate": "80.0%"
    },
    "actions": [
      {
        "timestamp": "2025-01-10T14:30:15Z",
        "issue": "Container redis not running",
        "action": "Restarted container",
        "success": true,
        "details": "Container now healthy"
      }
    ]
  }
}
```

---

## 🚨 When Auto-Healing Fails

If healing fails, Orixoon:

1. **Logs the failure** with detailed error message
2. **Blocks deployment** (safety first!)
3. **Generates detailed report** in `reports/` directory
4. **Recommends manual intervention**

Example failure report:
```
❌ HEALING FAILED: Container 'app' unhealthy
   Attempted: Restart container (3 times)
   Error: Container keeps crashing immediately after start
   Recommendation: Check application logs for crash cause
   Deployment: BLOCKED for safety
```

---

## 🔍 Testing Auto-Healing

### Test Individual Healing Actions

```bash
# Test container healing
python3 tools/auto_healing_engine.py --dry-run

# Test with specific issue JSON
python3 tools/auto_healing_engine.py --issue-file test_issues.json
```

### Test Full Workflow

```bash
# 1. Stop a container to simulate failure
docker stop redis

# 2. Run Orixoon with auto-healing
bash tools/orixoon_orchestrator.sh --auto-heal

# Expected output:
# ❌ Redis not responding
# 🔧 HEALING: Restarting redis container...
# ✅ HEALED: Container restarted successfully
# 🔄 Re-running health checks...
# ✓ Redis health: PASSED
```

---

## 📋 Deployment Integration

### Method 1: Manual Approval

Edit `scripts/deploy_production.sh`:

```bash
# Run Orixoon with auto-healing
bash "$PROJECT_DIR/.claude/agents/orixoon/tools/orixoon_orchestrator.sh" --auto-heal

if [ $? -ne 0 ]; then
    echo "❌ Pre-deployment tests failed. Deployment aborted."
    exit 1
fi
```

### Method 2: Dry Run First, Then Live

```bash
# First run dry run to see what would be healed
bash orixoon_orchestrator.sh --auto-heal --dry-run

# Review healing actions, then run live
bash orixoon_orchestrator.sh --auto-heal
```

---

## ⚠️ Important Warnings

### DO NOT use auto-healing if:

1. **Production database is in critical state** - Manual intervention required
2. **Multiple services failing simultaneously** - May indicate systemic issue
3. **Disk space critically low (<1GB)** - Fix manually first
4. **Never tested healing actions before** - Use --dry-run first!

### USE auto-healing for:

1. **Pre-deployment testing** ✅
2. **Staging environment deployments** ✅
3. **Development environment** ✅
4. **Routine maintenance windows** ✅
5. **Automated CI/CD pipelines** ✅ (with notifications)

---

## 📞 Troubleshooting

### Issue: "Auto-healing not working"

**Check:**
1. Is `--auto-heal` flag enabled?
2. Is `healing_config.json` enabled field set to true?
3. Are safety limits not exceeded?
4. Check healing logs in reports/

### Issue: "Healing succeeds but test still fails"

**Possible causes:**
1. Issue requires more time to stabilize (increase wait time)
2. Root cause not addressed by healing action
3. Multiple issues need healing
4. Service needs manual intervention

### Issue: "Too many healing attempts"

**Solution:**
Adjust in `healing_config.json`:
```json
{
  "safety_limits": {
    "max_container_restarts_per_session": 10,  // Increase if needed
    "max_database_operations_per_session": 5   // Increase if needed
  }
}
```

---

## 📊 Monitoring & Alerts

### Healing Logs

Located at: `reports/TIMESTAMP/healing_actions.log`

Example:
```
2025-01-10 14:30:15 | INFO | Detected issue: container_not_running
2025-01-10 14:30:15 | INFO | Starting healing action: restart_container
2025-01-10 14:30:20 | SUCCESS | Container redis started successfully
2025-01-10 14:30:25 | INFO | Re-testing service health...
2025-01-10 14:30:30 | SUCCESS | Service health check passed
```

### Notifications (Coming Soon)

Configure in `healing_config.json`:
```json
{
  "notifications": {
    "notify_on_healing_attempt": true,
    "notify_on_healing_success": true,
    "notify_on_healing_failure": true,
    "notification_channels": ["slack", "email"]
  }
}
```

---

## 🎯 Best Practices

1. **Always test with --dry-run first** in new environments
2. **Review healing logs** after each deployment
3. **Monitor healing success rate** (aim for >80%)
4. **Update healing config** based on your environment
5. **Document custom healing actions** you add
6. **Set up notifications** for healing failures
7. **Review failed healings** to improve healing logic

---

## 🔮 Future Enhancements

- [ ] Machine learning to predict failures before they occur
- [ ] Automatic rollback if healing fails repeatedly
- [ ] Integration with monitoring dashboards (Grafana, Datadog)
- [ ] Slack/Email notifications for healing actions
- [ ] Healing action analytics and trends
- [ ] Custom healing action plugins
- [ ] Multi-server coordinated healing

---

## 📝 Version History

- **v2.0.0** (2025-01-10): Auto-healing engine added
  - 9 healing action types
  - Safety limits and dry-run mode
  - Integration with service health checker
  - Configurable via healing_config.json

- **v1.0.0** (2025-01-10): Initial release
  - 4 core test phases
  - Basic health checking
  - No auto-healing

---

**Orixoon Auto-Healing** - Not just testing, but self-healing! 🔧✨
