# AI Session Recovery Protocol

**Purpose:** Guidelines for maintaining context continuity across session resets
**Last Updated:** 2025-11-14
**Load via:** @docs/reference/ai-guidelines/ai-session-recovery.md

---

## 🔄 Session Reset Detection

### Signs of Context Loss
```yaml
Detect context loss when:
  - Previous messages are not visible
  - Don't remember recent work discussed
  - Conversation history appears truncated
  - New session without seeing prior context
  - CLAUDE.md hasn't been auto-loaded (system issue)
```

### Automatic Detection Triggers
```yaml
Technical Indicators:
  - Message count resets to 0
  - No memory of last task
  - User mentions "new session"
  - User repeats information previously shared
```

---

## 📥 Rapid Context Recovery Procedure

### Step 1: Acknowledge Context Loss
```yaml
SAY:
"I notice this is a new session or context was reset.
Let me reload the project context..."

DON'T PANIC or ask user to repeat everything
```

### Step 2: Load Core Context (30 seconds)
```bash
# These load automatically or quickly:
1. CLAUDE.md (auto-loaded, 387 lines)
2. Check current state:
   - cat .claude/state/current-phase.json
   - cat .claude/state/recent-decisions.json

3. Git context:
   - git status
   - git branch
   - git log --oneline -10
```

### Step 3: Reconstruct Work Context
```yaml
Check Recent Activity:
  # Last 5 commits
  git log --oneline -5

  # Current branch
  git branch --show-current

  # Uncommitted changes
  git status

  # Recent file modifications
  ls -lt | head -10

What This Tells You:
  - What was being worked on
  - Current feature/fix in progress
  - Whether work is committed or pending
```

### Step 4: Brief Status Report
```yaml
REPORT TO USER:
"I've reloaded context from CLAUDE.md and state files.

Current state:
  - Project: TSH ERP Ecosystem (500+ clients, 2,218+ products)
  - Phase: Zoho Migration Phase 1 (read-only sync via TDS Core)
  - Tech: FastAPI + Flutter + PostgreSQL
  - Branch: [current branch]
  - Recent work: [summary from git log]
  - Uncommitted: [git status summary]

What were we working on?"

DON'T:
  - Ask for full project explanation (you have CLAUDE.md)
  - Ask about tech stack (already know)
  - Ask about scale (already know)
  - Repeat information from CLAUDE.md back to user
```

### Step 5: Resume Work
```yaml
User provides brief task context:
"We were debugging the Zoho sync issue"
"Continue implementing the commission calculator"
"Deploy the changes to staging"

YOU:
  - Load any additional @docs/ files needed
  - Check relevant code locations
  - Continue work smoothly
```

---

## 💾 State Management for Continuity

### Automated State Files
```yaml
.claude/state/current-phase.json:
  - Zoho migration phase
  - Deployment constraints
  - Phase success criteria

.claude/state/recent-decisions.json:
  - Last 10 major decisions
  - Rationale for each
  - Outcomes and learnings

.claude/state/project-stats.json:
  - Business metrics
  - Technical metrics
  - Server information
  - Integration status
```

### Using State for Recovery
```bash
# Quick phase check
cat .claude/state/current-phase.json | grep "phase"

# Recent decisions
cat .claude/state/recent-decisions.json | jq '.decisions[-3:]'

# Project stats
cat .claude/state/project-stats.json | jq '.business_metrics'
```

---

## 🎯 Memory Continuity Best Practices

### What I Remember (Within Session)
```yaml
During Active Session:
  ✓ All messages in current conversation
  ✓ Files I've read
  ✓ Code I've written
  ✓ Decisions made together
  ✓ User preferences expressed
```

### What I DON'T Remember (Between Sessions)
```yaml
After Session Reset:
  ✗ Previous conversations
  ✗ Yesterday's work (unless in git log)
  ✗ Decisions not documented
  ✗ Temporary preferences
```

### How to Preserve Context
```yaml
For User (to help me remember):
  - Commit code with clear messages
  - Update state/ files for major decisions
  - Document in code comments
  - Keep CLAUDE.md up to date

For Me (to help continuity):
  - Write clear git commit messages
  - Add comments explaining business logic
  - Update state/recent-decisions.json
  - Suggest doc updates for major changes
```

---

## 🔄 Session Handoff Protocol

### End of Session Checklist
```yaml
Before session ends (if applicable):
  □ All code committed with clear messages
  □ State files updated if major decisions made
  □ Documentation updated if architecture changed
  □ Current task status clear (completed/pending)
  □ Next steps documented (in code comments or git log)
```

### Beginning of Session Checklist
```yaml
At session start:
  □ CLAUDE.md loaded (automatic)
  □ Git status checked
  □ Recent commits reviewed
  □ State files reviewed (if needed)
  □ Ready to ask user "What are we working on?"
```

---

## 📋 Recovery from Specific Scenarios

### Scenario 1: Mid-Feature Development Reset
```yaml
Situation: Session reset while implementing feature

Recovery Steps:
1. Check git log → see feature branch and commits
2. Check uncommitted changes → git status
3. Read recent code additions → git diff
4. Report to user:
   "I see we're implementing [feature] on branch [name].
    Last commit: [message]
    Uncommitted changes: [summary]
    Should I continue or review?"
```

### Scenario 2: Mid-Debugging Reset
```yaml
Situation: Session reset while debugging issue

Recovery Steps:
1. Check recent git log for "fix" commits
2. Check for error logs or screenshots
3. Ask user:
   "We were debugging an issue. Can you briefly describe:
    - What's the symptom?
    - What have we tried so far?"
4. Continue debugging with context
```

### Scenario 3: Mid-Deployment Reset
```yaml
Situation: Session reset during deployment

Recovery Steps:
1. Check GitHub Actions → gh run list --limit 3
2. Check server health → curl https://erp.tsh.sale/health
3. Report status:
   "Checking deployment status...
    Staging: [status]
    Production: [status]
    Recent workflow: [status]
    Should we continue deployment or verify current state?"
```

### Scenario 4: Complete Context Loss
```yaml
Situation: No git history, user says "new conversation"

Recovery Steps:
1. Load CLAUDE.md (automatic)
2. Load core files:
   - @docs/core/project-context.md
   - @docs/core/architecture.md
3. Say: "I've loaded TSH ERP context. What would you like to work on?"
4. DON'T ask user to explain entire project (you have docs)
```

---

## ⚡ Fast Recovery Shortcuts

### 5-Second Context Check
```bash
# One-liner for quick context
git log --oneline -3 && git status -s && cat .claude/state/current-phase.json | grep "phase"

# Output tells you:
# - Recent work (git log)
# - Current changes (git status)
# - Current phase (state file)
```

### 15-Second Full Recovery
```bash
# Complete context rebuild
echo "=== Git Context ===" && \
git branch --show-current && \
git log --oneline -5 && \
echo "\n=== Status ===" && \
git status -s && \
echo "\n=== Phase ===" && \
cat .claude/state/current-phase.json | jq '.zoho_migration_phase, .deployment_constraints'
```

---

## 🎯 Context Verification

### How to Know Recovery Was Successful
```yaml
✅ Successful Recovery:
  - I know current phase (Phase 1)
  - I know tech stack (FastAPI + Flutter + PostgreSQL)
  - I know scale (500+ clients, 2,218+ products)
  - I know what was being worked on (git log)
  - I know current environment (develop/main branch)
  - User doesn't need to repeat basic facts

❌ Incomplete Recovery:
  - I ask about tech stack (should already know)
  - I ask about project scale (should already know)
  - I don't check git history
  - I ask user to explain everything from scratch
```

---

## 💡 Proactive Context Preservation

### During Active Session
```yaml
When implementing something important:
  - Commit frequently with clear messages
  - Add code comments explaining "why"
  - Suggest updating state/recent-decisions.json
  - Document major architecture decisions

Example:
"I've implemented the commission calculator.
Should we update .claude/state/recent-decisions.json
to document why we chose percentage-based over fixed-rate?"
```

### When Major Decisions Made
```yaml
Suggest updating:
  - state/recent-decisions.json (decision log)
  - state/current-phase.json (if phase changes)
  - CLAUDE.md (if critical facts change)
  - core/ docs (if architecture changes)

Example:
"We've decided to use Redis for caching.
This is a significant architectural decision.
Should I update core/architecture.md to document this?"
```

---

## 📊 Recovery Success Metrics

```yaml
Fast Recovery (< 30 seconds):
  - Load CLAUDE.md
  - Check git status
  - Ask "What are we working on?"

Complete Recovery (< 2 minutes):
  - Load CLAUDE.md + state files
  - Check git log and status
  - Review recent code changes
  - Understand current task
  - Ready to continue work

Perfect Recovery:
  - User doesn't notice the reset
  - No need to repeat information
  - Work continues seamlessly
```

---

**Related Guidelines:**
- Core interpretation: @docs/reference/ai-guidelines/ai-context-core.md
- Security monitoring: @docs/reference/ai-guidelines/ai-monitoring.md
- Operation modes: @docs/reference/ai-guidelines/ai-operation-modes.md
