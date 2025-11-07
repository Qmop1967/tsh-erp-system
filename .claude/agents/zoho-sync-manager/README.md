# 🤖 Zoho Sync Manager Agent

**Your AI Software Engineer for Zoho Integration Management**

Version: 1.0.0
Created: November 4, 2025
Status: Production Ready ✅

---

## 🎯 What Is This Agent?

The **Zoho Sync Manager** is a specialized Claude Code agent that acts as your dedicated software engineer for managing the Zoho Books/Inventory integration with your TSH ERP system. It continuously monitors, diagnoses, and auto-heals sync issues, ensuring 99.9% reliability.

### Key Capabilities:
- ✅ **24/7 Monitoring** - Tracks queue status, sync delays, and system health
- ✅ **Auto-Healing** - Automatically fixes common issues without human intervention
- ✅ **Intelligent Diagnosis** - Analyzes error patterns and root causes
- ✅ **Proactive Alerts** - Warns you before small issues become big problems
- ✅ **Performance Optimization** - Suggests improvements based on data
- ✅ **Detailed Reporting** - Provides comprehensive health reports

---

## 🚀 Quick Start

### Option 1: Using Claude Code CLI

```bash
# Navigate to your project
cd TSH_ERP_Ecosystem

# Activate the agent (in Claude Code)
# Simply say: "activate zoho sync manager" or "check zoho sync health"
```

### Option 2: Manual Invocation

In Claude Code, use this prompt:

```
Please use the Zoho Sync Manager agent to check the current health
of our Zoho sync system and perform any necessary auto-healing.
```

---

## 📊 What The Agent Does

### 1. Health Monitoring

The agent checks:
- ✅ Service status (is tsh-erp running?)
- ✅ Queue status (pending, processing, completed, failed items)
- ✅ Sync delays (how old is the last successful sync?)
- ✅ Worker status (are background workers active?)
- ✅ Error patterns (what's failing and why?)
- ✅ System resources (memory, disk, CPU)

### 2. Auto-Healing Actions

The agent automatically:
- ✅ Re-queues failed items (if retry count < 5)
- ✅ Clears stuck locks (> 30 minutes old)
- ✅ Restarts service if workers are stuck
- ✅ Moves permanently failed items to dead letter queue
- ✅ Cleans old completed items (> 30 days)

### 3. Intelligent Reporting

The agent generates:
- ✅ Real-time health status
- ✅ Error pattern analysis
- ✅ Performance metrics
- ✅ Actionable recommendations
- ✅ Trend analysis

---

## 📋 Available Tools

### Monitoring Scripts

#### 1. Health Check Script
```bash
# Run comprehensive health check
bash .claude/agents/zoho-sync-manager/tools/sync_health_check.sh
```

**What it checks:**
- Service status
- Queue statistics (pending, failed, completed)
- Sync delays per entity type
- Worker activity
- Error patterns (top 5)
- Stuck locks
- System resources

**Output:** Detailed report with color-coded status indicators

#### 2. Auto-Heal Script
```bash
# Run auto-healing procedures
bash .claude/agents/zoho-sync-manager/tools/auto_heal.sh
```

**What it does:**
- Re-queues failed items (< 5 retries)
- Clears stuck locks (> 30 min)
- Moves permanently failed items to dead letter queue
- Checks worker status and restarts if needed
- Cleans old completed items (> 30 days)
- Monitors database connections

**Output:** Summary of actions taken

---

## 🔍 Common Use Cases

### Use Case 1: Daily Health Check

**Prompt:**
```
Check the Zoho sync health status and report any issues.
```

**What happens:**
1. Agent runs health check script
2. Reviews all metrics
3. Generates report with status
4. Performs auto-healing if needed
5. Provides recommendations

---

### Use Case 2: Investigating Sync Delays

**Prompt:**
```
I notice our Zoho data is not up to date. Can you investigate
what's causing the sync delay?
```

**What happens:**
1. Agent checks last sync timestamps
2. Analyzes queue backlog
3. Reviews worker logs
4. Identifies bottleneck (e.g., stuck lock, failed items, worker crash)
5. Applies appropriate fix
6. Monitors for 10 minutes
7. Reports results

---

### Use Case 3: Handling Mass Failures

**Prompt:**
```
We have many failed sync items. Please diagnose and fix them.
```

**What happens:**
1. Agent queries failed items
2. Groups by error message
3. Identifies patterns (e.g., "API timeout", "Invalid data")
4. Re-queues retriable failures
5. Moves permanent failures to dead letter queue
6. Suggests code fixes if pattern detected
7. Creates GitHub issue with details

---

### Use Case 4: Performance Optimization

**Prompt:**
```
Analyze our Zoho sync performance and suggest optimizations.
```

**What happens:**
1. Agent calculates processing rate (items/hour)
2. Measures average processing time per item
3. Identifies slow entity types
4. Checks for queue bottlenecks
5. Reviews worker configuration
6. Suggests:
   - Increase batch size
   - Add more workers
   - Optimize slow queries
   - Adjust retry logic

---

### Use Case 5: Emergency Response

**Prompt:**
```
URGENT: Zoho sync has stopped working completely!
```

**What happens:**
1. Agent immediately checks service status
2. Checks if workers are running
3. Reviews recent error logs
4. Restarts service if crashed
5. Re-queues all pending items
6. Monitors recovery for 15 minutes
7. Creates incident report

---

## 🎓 Understanding The Output

### Health Check Report Example:

```
🔍 Zoho Sync Health Check - 2025-11-04 18:30:00
==========================================

📊 Service Status Check
---
✅ TSH ERP service is running

📋 Queue Status Check
---
✅ Pending: 12 items
✅ Processing: 2 items
✅ Completed: 5,234 items
⚠️  Failed: 8 items
  🔧 Auto-heal: Re-queuing failed items...
  ✅ Failed items re-queued

⏰ Sync Delay Check
---
✅ product: 5 min ago
✅ customer: 8 min ago
⚠️  invoice: 45 min ago (warning threshold: 30min)
✅ bill: 12 min ago

👷 Worker Status Check
---
✅ Workers active (found 4 startup messages)

🔍 Error Pattern Analysis
---
  ❌ [5] API timeout after 30 seconds
  ❌ [2] Invalid customer_id format
  ❌ [1] Database connection lost

🔒 Locked Items Check
---
✅ No stuck locks detected

💻 System Resources
---
  Memory: 1.8Gi / 3.8Gi (47% used)
  Disk: 20G / 78G (26% used)

==========================================
📊 Health Check Complete
Report saved to: /tmp/zoho_sync_health_20251104_183000.txt
==========================================
```

### Status Indicators:
- ✅ **Green** - All good
- ⚠️ **Yellow** - Warning, attention needed
- 🔴 **Red** - Critical, immediate action required
- 🔧 **Wrench** - Auto-heal action taken
- ℹ️ **Info** - Informational message

---

## ⚙️ Configuration

### Thresholds (config.json)

You can customize alert thresholds:

```json
{
  "thresholds": {
    "queue": {
      "pending_warning": 50,      // Warn if > 50 pending
      "pending_critical": 200,    // Critical if > 200 pending
      "failed_warning": 5,        // Warn if > 5 failed
      "failed_critical": 10       // Critical if > 10 failed
    },
    "sync_delay": {
      "warning_minutes": 30,      // Warn if sync > 30 min old
      "critical_minutes": 120     // Critical if sync > 2 hours old
    },
    "worker_inactivity_minutes": 15,  // Alert if no activity for 15 min
    "stuck_lock_minutes": 30,         // Clear locks stuck > 30 min
    "max_retry_attempts": 5           // Move to DLQ after 5 failures
  }
}
```

---

## 🔐 Security & Permissions

### What the Agent Can Do:
- ✅ Read database tables (via sudo -u postgres)
- ✅ Update queue status (re-queue, clear locks)
- ✅ Restart tsh-erp service (via systemctl)
- ✅ Read system logs (via journalctl)
- ✅ SSH to production server (as root)

### What the Agent CANNOT Do:
- ❌ Delete production data (requires confirmation)
- ❌ Modify core application code (read-only)
- ❌ Make Zoho API calls (cost considerations)
- ❌ Change database schema (locked)
- ❌ Stop services during business hours (policy)

### Safety Features:
- 🔒 All destructive actions require confirmation
- 🔒 Automatic backups before major changes
- 🔒 Rollback capability
- 🔒 Audit logging of all actions

---

## 📅 Recommended Schedule

### Daily (Automatic):
- Health check every 15 minutes (via cron)
- Auto-healing every hour
- Performance report once per day

### Weekly (Manual):
- Full data consistency check
- Review dead letter queue items
- Performance optimization review

### Monthly (Manual):
- Clean old logs and completed items
- Review and update thresholds
- Optimize queries and indexes

---

## 🆘 Troubleshooting

### Problem: Agent Not Finding Scripts

**Solution:**
```bash
# Make scripts executable
chmod +x .claude/agents/zoho-sync-manager/tools/*.sh
```

### Problem: SSH Connection Fails

**Solution:**
```bash
# Test SSH connection
ssh root@167.71.39.50 "echo 'Connected'"

# Check SSH keys
ls -la ~/.ssh/
```

### Problem: Database Queries Fail

**Solution:**
```bash
# Test database connection
ssh root@167.71.39.50 "sudo -u postgres psql tsh_erp -c 'SELECT 1;'"
```

### Problem: False Alarms

**Solution:**
- Adjust thresholds in `config.json`
- Review and update alert logic
- Consider your normal traffic patterns

---

## 📞 Getting Help

### Ask the Agent:
```
Can you explain what this error means? [paste error]
```

```
What should I do if the queue is stuck?
```

```
How can I improve sync performance?
```

### Read the Logs:
```bash
# Service logs
ssh root@167.71.39.50 "journalctl -u tsh-erp -n 100"

# Health check reports
ls -lt /tmp/zoho_sync_health_*.txt | head -5
```

---

## 🎉 Success Metrics

Your Zoho sync is healthy when:
- ✅ Queue backlog < 20 items
- ✅ Failed items < 1% of total
- ✅ Sync delay < 5 minutes
- ✅ Workers always running
- ✅ Zero data loss
- ✅ 99.9% uptime

---

## 🔄 Updates & Maintenance

### Updating the Agent:

```bash
# Pull latest agent code
cd TSH_ERP_Ecosystem
git pull origin main

# Review changes
git log --oneline .claude/agents/zoho-sync-manager/
```

### Adding New Features:

1. Edit `agent.md` to add new capabilities
2. Create new scripts in `tools/` directory
3. Update `config.json` with new settings
4. Test thoroughly in staging
5. Deploy to production

---

## 📚 Additional Resources

- **Agent Prompt:** `.claude/agents/zoho-sync-manager/agent.md`
- **Configuration:** `.claude/agents/zoho-sync-manager/config.json`
- **Tools Directory:** `.claude/agents/zoho-sync-manager/tools/`
- **TSH ERP Docs:** `docs/ZOHO_INTEGRATION_*.md`
- **Production Server:** `ssh root@167.71.39.50`

---

## 🤝 Contributing

To improve this agent:

1. Test your changes in development
2. Document new features in this README
3. Update the agent prompt if needed
4. Share improvements via pull request

---

**Created with 🤖 Claude Code**
**Version:** 1.0.0
**Last Updated:** November 4, 2025
**Status:** ✅ Production Ready
