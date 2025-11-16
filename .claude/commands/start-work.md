# Start Work Session

Quick session initialization - Load current state and orient to today's work.

---

## What This Command Does

1. Load current project state from `.claude/state/`
2. Check git status and recent activity
3. Load last session backup (if exists)
4. Display orientation summary
5. Ready to work immediately

---

## Execution Steps

### Step 1: Acknowledge Start

Display:
```
🚀 Starting work session for TSH ERP Ecosystem...
```

### Step 2: Load State Files

Read these files in order:
1. `.claude/state/current-phase.json` - Current Zoho migration phase
2. `.claude/state/recent-decisions.json` - Recent architectural decisions
3. `.claude/state/project-stats.json` - Business metrics and server info

### Step 3: Load Last Session (if exists)

```bash
# Find most recent session backup
ls -t .claude/session_backups/SESSION_STATE_*.md 2>/dev/null | head -1
```

If found, read it to understand what was being worked on.

### Step 4: Check Git Status

```bash
# Current branch and status
git status
git branch --show-current

# Recent commits (last 5)
git log --oneline -5

# Uncommitted changes summary
git diff --stat
```

### Step 5: Check Server Health (Quick)

```bash
# Quick health checks (3 second timeout each - don't block if slow)
timeout 3 curl -s https://erp.tsh.sale/health 2>/dev/null || echo "⏭️  Production health check skipped (timeout)"
timeout 3 curl -s https://tds.tsh.sale/api/health 2>/dev/null || echo "⏭️  TDS health check skipped (timeout)"
```

### Step 6: Display Session Orientation

Report in this format:

```
✅ TSH ERP SESSION STARTED

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 PROJECT STATE:
   Phase: [from current-phase.json: phase_description]
   Can Write to Zoho: [from current-phase.json: can_write_to_zoho]
   Environment: [from current-phase.json: deployment_constraints.current_mode]

   Active Products: [from project-stats.json: business_metrics.active_products]
   Daily Orders: [from project-stats.json: wholesale + retail combined]
   Wholesale Clients: [from project-stats.json: business_metrics.wholesale_clients]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌿 GIT STATUS:
   Current Branch: [branch name]
   Status: [clean / N uncommitted file(s)]
   Last Commit: [hash] [message]

   Recent Commits:
   [Show last 3 commits]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 LAST SESSION:
[If session backup exists]
   Last Updated: [timestamp from backup]
   Was Working On: [from backup: Current Task]
   Status: [from backup: Status]
   Next Steps: [from backup: Next Session Actions - first 2 items]

   Uncommitted Work: [if any listed in backup]

[If no session backup exists]
   ℹ️  No previous session found - starting fresh

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 RECENT DECISIONS (Last 2):
[From recent-decisions.json, show last 2 decisions with dates]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ READY TO WORK

Core Context Loaded:
   ✅ CLAUDE.md auto-loaded (authorization framework, core facts)
   ✅ Project state understood (phase, servers, scale)
   ✅ Git status verified (branch, commits, changes)
   ✅ Authorization: RBAC + ABAC + RLS (3 layers required)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

What would you like to work on today?
```

---

## Important Implementation Notes

**Speed is Critical:**
- This command should complete in < 10 seconds
- Don't read heavy documentation files (already in CLAUDE.md)
- Focus on current state, not full context reload
- If git or server checks timeout, continue anyway
- Always end with asking what user wants to work on

**Error Handling:**
- If state files don't exist, show default values
- If no session backup, just note "starting fresh"
- If git commands fail, show "Git status unavailable"
- If health checks timeout, note "skipped" and continue

**What NOT to Load:**
- Don't load full documentation files (@docs/)
- Don't load code templates
- Don't load failsafe protocols
- These are available via @docs/ when needed

**Focus On:**
- Current project phase and constraints
- Git status (what's changed)
- Last session context (what was being worked on)
- Quick orientation for immediate productivity

---

## When to Use This Command

✅ **Use `/start-work` when:**
- Starting a new Claude Code session
- Returning after a break or time away
- Switching context to TSH ERP from another project
- After context compaction (continuing from previous Claude instance)
- When you need quick orientation without full context reload
- At the beginning of a new conversation

❌ **Don't use for:**
- Mid-session state checks (just ask "what's the git status?")
- When you just loaded full context (redundant with CLAUDE.md)
- Quick questions that don't need orientation
- When already oriented and actively working

---

## Success Criteria

This command succeeds when:
- ✅ User is oriented in < 10 seconds
- ✅ User knows exactly where they left off
- ✅ User doesn't need to re-explain context
- ✅ Git status is clear
- ✅ Next steps are obvious
- ✅ Ready to work immediately

---

**Related Commands:**
- `/end-work` - Save state and end session
- `/context-handoff` - Emergency handoff for context compaction
- `/reload-context` - Full context reload (heavier operation)
