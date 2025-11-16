# End Work Session

Save current session state and prepare handoff for next Claude instance.

---

## What This Command Does

1. Capture current work state
2. Check for uncommitted changes
3. Create session backup with timestamp
4. Update state files if needed
5. Prepare comprehensive handoff summary

---

## Execution Steps

### Step 1: Acknowledge End Session

Display:
```
💾 Saving session state and preparing handoff...
```

### Step 2: Gather Current State

```bash
# Git status
git status --porcelain
git branch --show-current
git log --oneline -5

# List uncommitted files
git status --short

# Check staged changes
git diff --cached --name-only

# Check unstaged changes
git diff --name-only

# Get last 10 commits for session summary
git log --oneline -10 --format="%h %s (%ar)"
```

### Step 3: Capture Work Summary

Ask user:
```
To create a comprehensive handoff, please provide:

1️⃣  What did you accomplish this session?
    (e.g., "Implemented customer filtering API", "Fixed Zoho sync bug")

2️⃣  What's currently in progress (not finished)?
    (e.g., "Customer API - backend done, frontend pending")

3️⃣  What should be done next?
    (e.g., "Test on staging", "Deploy to production", "Add unit tests")

4️⃣  Any blockers or issues?
    (e.g., "Waiting for Zoho API key", "Need clarification on X", or "None")

💡 You can say "auto-summary" and I'll infer from git commits and status.
```

If user says "auto-summary", infer from git log and uncommitted files.

### Step 4: Create Session Backup

Generate filename:
```bash
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE=".claude/session_backups/SESSION_STATE_${TIMESTAMP}.md"
```

Write session backup with this format:

```markdown
# TSH ERP - Session State

**Purpose:** Track current work across Claude Code sessions for seamless continuity.

**Last Updated:** [ISO 8601 timestamp - e.g., 2025-11-14T14:30:22+03:00]
**Session ID:** session-[YYYYMMDD-HHMM]

---

## 🎯 Current Task

**Working On:** [User's description or auto-inferred from commits]

**Status:** [In Progress / Completed / Blocked]

**Progress:** [Percentage or description]

**Next Step:** [What to do immediately next]

**Files Modified:**
```
[Output of git status --short]
```

**Blockers:** [User-provided or "None"]

**Dependencies:** [User-provided or "None"]

---

## 📝 Session Accomplishments

[User-provided summary or auto-generated from commits]

**Commits This Session:**
```
[git log --oneline -10 with relative timestamps]
```

**Key Changes:**
[Bullet list from user or inferred from git diff --stat]

---

## 🌿 Git State

**Current Branch:** [branch]

**Status:** [clean / N uncommitted file(s)]

**Staged Changes:** [N files or "None"]

**Unstaged Changes:** [N files or "None"]

**Last Commit:** [hash] [message] ([time ago])

**Recent Commits:**
```
[git log --oneline -5]
```

**Uncommitted Files:**
[If any, list them with M/A/D/? status]

**Branch Strategy Reminder:**
- Push to `develop` → Auto-deploy to staging (167.71.58.65)
- Push to `main` → Auto-deploy to production (167.71.39.50)

---

## 📌 Next Session Actions

**Immediate Next Steps:**
1. [User-provided or inferred - most urgent]
2. [Second priority]
3. [Third priority]

**Before Starting Next Session:**
- [ ] Run `/start-work` to load this state
- [ ] Review uncommitted changes (if any)
- [ ] Check recent commits for context
- [ ] Verify current branch

**Context to Load:**
- `.claude/CLAUDE.md` (auto-loaded every session)
- This session state file (loaded by `/start-work`)
- [Any specific @docs/ files if mentioned]

---

## 🚨 Important Reminders

**From This Session:**
[Any critical notes, warnings, or decisions made during this session]

**Uncommitted Work:**
[If git status shows changes]
⚠️  There are [N] uncommitted file(s):
[List files with status]

**Action Required:**
- Review changes before committing
- Verify all changes are intentional
- Test changes before pushing
- Write meaningful commit message

[If git status is clean]
✅ No uncommitted changes - all work committed

**Deployment Status:**
[If on develop or main branch]
- Current branch: [branch]
- Ahead of remote: [N commits or "No"]
- Needs push: [Yes/No]

---

## 📊 Session Metrics

**Branch:** [current branch]

**Commits Made:** [count from git log]

**Files Changed:** [count from git diff --stat]

**Session Duration:** [If trackable - otherwise omit]

---

## 🔄 Context for Next Session

**Quick Summary:**
When you start the next session, you were [brief description of current task/status].

**Current Phase:** [from .claude/state/current-phase.json]

**Authorization Reminder:** All endpoints need RBAC + ABAC + RLS (3 layers)

**Tech Stack:** FastAPI + PostgreSQL + Flutter (don't suggest changes)

**Servers:**
- Staging: 167.71.58.65 (develop branch)
- Production: 167.71.39.50 (main branch)

---

**END OF SESSION STATE**

*This file is automatically created by `/end-work` command.*
*To resume: Run `/start-work` at the beginning of next session.*
```

### Step 5: Update State Files (if needed)

Ask user:
```
Do any of these state files need updating?

- **Current Phase** (.claude/state/current-phase.json)
  - Did Zoho migration phase change?
  - Did deployment mode change?

- **Recent Decisions** (.claude/state/recent-decisions.json)
  - Was a major architectural decision made?
  - Should we document this decision?

- **Project Stats** (.claude/state/project-stats.json)
  - Did business metrics change significantly?
  - New major milestone reached?

If yes, please specify what to update. If no, I'll skip updates.
```

Only update if user explicitly requests changes.

### Step 6: Check Deployment Status

```bash
# If on develop or main branch, check if pushed
BRANCH=$(git branch --show-current)
if [[ "$BRANCH" == "develop" || "$BRANCH" == "main" ]]; then
    git status --porcelain --branch | grep ahead
    # Note if ahead of remote
fi
```

### Step 7: Final Handoff Summary

Display:
```
✅ SESSION STATE SAVED

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 BACKUP CREATED:
   .claude/session_backups/SESSION_STATE_[timestamp].md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 SESSION SUMMARY:

   Accomplishments:
   [Bullet list of what was done]

   In Progress:
   [What's not finished]

   Next Steps:
   1. [First action]
   2. [Second action]
   3. [Third action]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌿 GIT STATUS:
   Branch: [branch name]
   Uncommitted: [N file(s) or "clean"]
   Staged: [N file(s) or "none"]
   Last Commit: [hash] [message]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  HANDOFF CHECKLIST:
   [✓/✗] All work committed
   [✓/✗] Pushed to remote
   [✓/✗] No pending deployments
   [✓/✗] No blockers documented
   [✓/✗] Next steps clear

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 NEXT SESSION:

   To resume this work, run: /start-work

   The next Claude instance will automatically load:
   ✅ This session backup
   ✅ Current git state
   ✅ Project state files
   ✅ Recent decisions

   And continue from: [Next Step]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 READY FOR HANDOFF

Thank you for the session! The next instance will be well-prepared.
```

---

## Important Implementation Notes

**Capture Everything:**
- Even if minimal work done, create backup
- Uncommitted changes are critical to document
- Make next steps explicit (don't assume next Claude knows)
- Include enough context for seamless continuation

**User Input vs Auto-Summary:**
- Prefer user input (more accurate)
- If user says "auto-summary", infer from git
- Auto-summary should look at:
  - Commit messages (last 10)
  - Files changed (git diff --stat)
  - Uncommitted files
  - Branch name

**State File Updates:**
- Only update if user explicitly confirms
- Don't auto-update (requires user validation)
- Ask specific questions about what changed
- Document updates in recent-decisions.json

**Handoff Document Quality:**
- Make it self-contained
- Next Claude shouldn't ask "what were we doing?"
- Include enough context to continue
- But don't duplicate CLAUDE.md content

---

## When to Use This Command

✅ **Use `/end-work` when:**
- Ending a Claude Code session for the day
- Taking a long break from the project
- Switching to different project/task
- After significant milestone (good checkpoint)
- Before expected context compaction (long session)
- Want to create clean handoff point

❌ **Don't use for:**
- Quick breaks (< 15 minutes) - context still available
- Mid-task when coming right back
- Multiple times in same session (once at end is enough)

---

## Success Criteria

This command succeeds when:
- ✅ Complete session state captured
- ✅ Git status documented clearly
- ✅ Next steps are explicit
- ✅ Uncommitted work noted
- ✅ Next session can continue seamlessly
- ✅ User feels confident work won't be lost

---

## Special Cases

**If No Work Done:**
Still create backup with:
- Session started and ended with no changes
- Git status (even if clean)
- Note "No work done this session"

**If Major Uncommitted Work:**
Warn user:
```
⚠️  Warning: You have [N] uncommitted files.

Consider:
1. Committing changes if work is complete
2. Stashing if work is incomplete
3. At minimum, this is documented in session backup

Proceed with /end-work anyway? (Yes/No)
```

**If On main Branch with Changes:**
Warn user:
```
🚨 You're on 'main' branch with uncommitted changes.

This is unusual - main should only receive PR merges.

Consider:
1. Switching to develop or feature branch
2. Committing and pushing if this is intentional hotfix

Proceed anyway? (Yes/No)
```

---

**Related Commands:**
- `/start-work` - Quick session initialization
- `/context-handoff` - Emergency handoff for context compaction (more comprehensive)
- `/reload-context` - Full context reload
