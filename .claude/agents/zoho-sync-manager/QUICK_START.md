# 🚀 Zoho Sync Manager - Quick Start Guide

## 5-Minute Setup

### Step 1: Verify Agent Files
```bash
cd TSH_ERP_Ecosystem
ls -la .claude/agents/zoho-sync-manager/
```

You should see:
- ✅ `agent.md` - Agent instructions
- ✅ `config.json` - Configuration
- ✅ `README.md` - Full documentation
- ✅ `tools/` - Monitoring scripts

### Step 2: Make Scripts Executable
```bash
chmod +x .claude/agents/zoho-sync-manager/tools/*.sh
```

### Step 3: Test Scripts Manually (Optional)
```bash
# Test health check
.claude/agents/zoho-sync-manager/tools/sync_health_check.sh

# Test auto-heal
.claude/agents/zoho-sync-manager/tools/auto_heal.sh
```

### Step 4: Activate Agent in Claude Code

Simply ask Claude Code:

```
Please use the Zoho Sync Manager agent to check our sync health
```

OR

```
activate zoho sync manager
```

---

## Common Commands

### Daily Health Check
```
Check Zoho sync health
```

### Investigate Issues
```
We have sync delays - please investigate and fix
```

### Emergency Response
```
URGENT: Zoho sync is down!
```

### Performance Analysis
```
Analyze Zoho sync performance and suggest optimizations
```

---

## What You'll Get

### Health Report Example:
```
✅ Service running
✅ Pending: 12 items
⚠️  Failed: 8 items → Auto-healed ✅
✅ Sync delay: < 5 min
✅ Workers active
```

### Auto-Healing Actions:
- Re-queued failed items
- Cleared stuck locks
- Restarted workers if needed
- Cleaned old data

---

## Quick Troubleshooting

### "Permission denied"
```bash
chmod +x .claude/agents/zoho-sync-manager/tools/*.sh
```

### "SSH connection failed"
```bash
ssh root@167.71.39.50 "echo 'test'"
```

### "Database query failed"
```bash
ssh root@167.71.39.50 "sudo -u postgres psql tsh_erp -c 'SELECT 1;'"
```

---

## Next Steps

1. ✅ Run your first health check
2. ✅ Review the full [README.md](README.md)
3. ✅ Schedule automated checks (optional)
4. ✅ Customize thresholds in `config.json` (optional)

---

**You're all set! 🎉**

The Zoho Sync Manager is now ready to help you maintain a healthy Zoho integration.
