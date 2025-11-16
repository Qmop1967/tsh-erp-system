# AI Operation Modes & Access Levels

**Purpose:** Defines what operations are allowed in each operational mode
**Last Updated:** 2025-11-14
**Load via:** @docs/reference/ai-guidelines/ai-operation-modes.md

---

## 🎯 Operation Mode Framework

Claude Code operates in different modes with different permission levels.

---

## 🔍 Mode 1: Read-Only Analysis

**When to Use:**
- Initial code review
- Bug investigation (diagnosis only, no fixes)
- Understanding codebase
- Security audit (report only)
- Performance analysis (recommendations only)

### Allowed Operations
```yaml
✅ CAN DO:
  - Read any file
  - Search codebase (grep, find, Task tool)
  - Analyze code for issues
  - Provide recommendations
  - Answer questions
  - Review documentation
  - Explain code behavior
  - Identify bugs or vulnerabilities
  - Create analysis reports
```

### Forbidden Operations
```yaml
❌ CANNOT DO:
  - Write or modify files
  - Execute commands (except read-only: ls, cat, grep)
  - Create branches or commits
  - Deploy anything
  - Modify database
  - Access production systems
  - Run tests (they might modify state)
```

### Example Interaction
```
User: "Review this code for security issues"
Mode: Read-Only Analysis ✅

Actions:
1. Read code files
2. Search for vulnerability patterns
3. Report findings with recommendations
4. DO NOT fix issues (just report)
```

---

## 🛠️ Mode 2: Development Mode (DEFAULT)

**This is the DEFAULT mode for most work.**

**When to Use:**
- Feature implementation
- Bug fixes
- Refactoring
- Testing
- Staging deployments
- Normal development work

### Allowed Operations
```yaml
✅ CAN DO:
  - All Read-Only operations
  - Write/modify code files
  - Create test files
  - Run local tests
  - Create git branches
  - Commit changes (to develop branch)
  - Deploy to staging (develop branch)
  - Run database migrations (staging only)
  - Execute build/test commands
  - Install dependencies
```

### Forbidden Operations
```yaml
❌ CANNOT DO:
  - Push to main branch directly
  - Deploy to production directly
  - Modify production database
  - Delete data permanently
  - Change critical infrastructure
  - Skip staging verification
```

### Example Interaction
```
User: "Add pagination to the products endpoint"
Mode: Development ✅

Actions:
1. Read existing code
2. Modify endpoint to add pagination
3. Add tests
4. Commit to develop branch
5. Deploy to staging
6. Verify on staging
7. Report completion
```

---

## ⚡ Mode 3: Critical Operations Mode

**Requires explicit approval before ANY operation.**

**When to Use:**
- Production deployments
- Emergency hotfixes
- Database migrations (production)
- Configuration changes (production)

### Allowed Operations
```yaml
✅ CAN DO (with approval):
  - All Development Mode operations
  - Push to main branch
  - Deploy to production
  - Run production database migrations
  - Modify production configuration
  - Rollback deployments
```

### REQUIRES EXPLICIT APPROVAL
```yaml
Before EVERY Critical Operation:

1. Summarize what will be done
2. State the risk level (LOW/MEDIUM/HIGH)
3. Confirm staging tested successfully
4. Confirm rollback plan exists
5. Wait for user's explicit "go ahead"

Example Request:
"I'm ready to deploy to production:
- Changes: [Feature A, Bug fix B]
- Risk: LOW (no schema changes, tested on staging)
- Staging: Tested successfully for 2 hours, no errors
- Rollback: git revert available, takes < 5 minutes
- Affects: All users

May I proceed with production deployment?"
```

### Forbidden Operations
```yaml
❌ CANNOT DO (even with approval):
  - Delete production data (requires backup first)
  - Direct database edits (use migrations)
  - Bypass deployment pipeline
  - Skip staging verification
  - Force push to main
```

### Example Interaction
```
User: "Deploy to production"
Mode: Critical Operations ⚠️

Actions:
1. Verify all checks pass
2. Summarize changes and risks
3. REQUEST APPROVAL
4. Wait for explicit "yes"
5. Execute deployment
6. Monitor closely
7. Report status
```

---

## 🚨 Mode 4: Emergency Mode

**Activated only during production emergencies.**

### When to Activate
```yaml
Activate Emergency Mode when:
  - Production is completely down
  - Data corruption detected
  - Security breach suspected
  - Critical sync failure (> 4 hours)
  - Revenue-impacting outage
```

### Special Rules
```yaml
In Emergency Mode:

✅ ALLOWED (to restore service):
  - Skip normal approval for time-sensitive fixes
  - Alert user immediately
  - Follow @docs/FAILSAFE_PROTOCOL.md
  - Document all actions taken
  - Prioritize stability over perfection
  - Rollback without asking (if needed)
  - Restart services without asking
  - Apply quick fixes without full testing
  - Disable failing features temporarily

❌ STILL FORBIDDEN:
  - Delete data without backup
  - Make irreversible changes
  - Guess at solutions (diagnose first)
  - Skip all testing (test minimally)
```

### Exit Emergency Mode
```yaml
Return to normal when:
  - Production restored and stable
  - Root cause identified
  - Proper fix planned for later
  - User informed of all actions taken
  - Post-mortem scheduled
```

### Example Interaction
```
System: Production is down!
Mode: 🚨 EMERGENCY MODE ACTIVATED

Actions:
1. Immediately check health endpoints
2. Check GitHub Actions for failed deployments
3. Check server logs
4. Identify issue
5. Apply quickest fix (even if not perfect)
6. Restore service
7. Monitor stability
8. Document everything
9. Plan proper fix later
10. Report to user
```

---

## 🎛️ Mode Selection Matrix

```yaml
Task Type → Recommended Mode
─────────────────────────────────────────
Code review → Read-Only
Bug investigation (diagnosis) → Read-Only
Bug investigation (fix) → Development
Feature implementation → Development
Refactoring → Development
Testing → Development
Deploy to staging → Development
Deploy to production → Critical Operations
Emergency fix → Emergency
Database migration (staging) → Development
Database migration (production) → Critical Operations
Security audit → Read-Only
Performance analysis → Read-Only
Configuration change (staging) → Development
Configuration change (production) → Critical Operations
```

---

## ✅ Mode Verification Checklist

Before performing ANY operation, verify:

### Mode Check
```yaml
□ What mode am I in?
□ Is this operation allowed in current mode?
□ Do I need to switch modes?
□ Do I need user approval?
```

### Risk Assessment
```yaml
□ What's the risk level? (LOW/MEDIUM/HIGH/CRITICAL)
□ Is this reversible?
□ What's the rollback plan?
□ Have I tested this?
□ What's the impact if it fails?
```

### Context Verification
```yaml
□ Am I on the right branch? (develop for dev, main for prod)
□ Am I in the right environment? (staging/production)
□ Do I have the right permissions?
□ Is this the right time? (production deploy during business hours?)
```

### Safety Checks
```yaml
□ Have I read relevant documentation?
□ Have I followed appropriate workflow?
□ Have I checked for security issues?
□ Have I verified at scale?
□ Is backup available (if needed)?
```

---

## 🚦 Mode Transition Protocol

### Switching Modes
```yaml
When switching modes, explicitly state:

"Switching to [Mode Name] mode for [reason]..."

Examples:
"Switching to Read-Only Analysis mode to investigate bug..."
"Switching to Critical Operations mode for production deployment..."
"EMERGENCY MODE ACTIVATED: Production is down, following failsafe protocol."
```

### Current Mode Indicators
```yaml
At start of each session:
DEFAULT: Development Mode 🛠️

Explicitly state when switching:
- "Now in Critical Operations mode ⚡"
- "Entering Emergency Mode 🚨"
- "Switching to Read-Only Analysis 🔍"
```

---

## 🎯 Mode-Specific Examples

### Development Mode (Most Common)
```
User: "Add a new field to the Product model"

Mode: Development 🛠️ (DEFAULT)

Actions:
1. Read current Product model
2. Add new field (e.g., manufacturer)
3. Add Arabic field (manufacturer_ar)
4. Create migration
5. Update Pydantic schema
6. Update affected endpoints
7. Run tests
8. Commit to develop
9. Deploy to staging
10. Verify on staging ✅
```

### Critical Operations Mode
```
User: "Deploy to production now"

Mode: Critical Operations ⚡ (APPROVAL REQUIRED)

Actions:
1. Verify staging success
2. Request approval:
   "Ready to deploy to production:
    - Changes: [list]
    - Risk: [level]
    - Staging: [status]
    - Rollback: [plan]
    May I proceed? (YES/NO)"
3. Wait for explicit YES
4. Execute deployment
5. Monitor closely
6. Report status ✅
```

### Emergency Mode
```
Alert: "Production API is returning 500 errors!"

Mode: 🚨 EMERGENCY ACTIVATED

Actions:
1. Check server health immediately
2. Check recent deployments
3. Check logs for errors
4. Identify root cause (database connection)
5. Apply quick fix (restart database connection pool)
6. Verify service restored
7. Monitor for stability
8. Document actions
9. Plan proper fix
10. Report to user ✅
```

---

## 📊 Mode Usage Statistics

```yaml
Expected Distribution:
  Development Mode: ~85% of time
  Read-Only Analysis: ~10% of time
  Critical Operations: ~4% of time
  Emergency Mode: ~1% of time (hopefully less!)

If you're in Emergency Mode frequently:
  → Something is wrong with deployment process
  → Need better testing/staging verification
  → Need architectural improvements
```

---

## 💡 Mode Best Practices

### Always Prefer Lower Modes
```yaml
Can the task be done in Read-Only?
  → Use Read-Only (safest)

Can it be done in Development?
  → Use Development (normal)

Only if absolutely necessary:
  → Use Critical Operations (careful)

Only in true emergencies:
  → Use Emergency Mode (rare)
```

### Clear Communication
```yaml
✅ GOOD:
"I'm in Development mode, deploying to staging..."
"Switching to Critical Operations mode for production deployment..."
"EMERGENCY MODE: Production is down, applying immediate fix..."

❌ BAD:
"Deploying..." (which environment? what mode?)
"Making changes..." (what kind? what mode?)
```

### Document Mode-Specific Actions
```yaml
In Critical Operations or Emergency:
  - Document every action taken
  - Timestamp each step
  - Record what was changed
  - Note rollback steps available
  - Report to user at end
```

---

**Related Guidelines:**
- Core interpretation: @docs/reference/ai-guidelines/ai-context-core.md
- Session recovery: @docs/reference/ai-guidelines/ai-session-recovery.md
- Security monitoring: @docs/reference/ai-guidelines/ai-monitoring.md
- Failsafe protocols: @docs/FAILSAFE_PROTOCOL.md
