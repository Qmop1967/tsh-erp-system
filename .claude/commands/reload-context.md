# Reload Context Command

Force a complete context reload from `.claude/` files. Use this when:
- Context appears stale or outdated
- After updating `.claude/` documentation files
- Mid-session if Claude seems confused
- To refresh understanding of project state

---

## Task

Perform a complete context reload following these steps:

### 1. Acknowledge Reload Request
```
"🔄 Reloading TSH ERP context from .claude/ files..."
```

### 2. Load Core Context Files (Priority 1)
Read these files in order:
- `.claude/AI_CONTEXT_RULES.md` - How to interpret context
- `.claude/PROJECT_VISION.md` - Business context and vision
- `.claude/QUICK_REFERENCE.md` - Quick facts and rules
- `.claude/ARCHITECTURE_RULES.md` - Technical constraints

### 3. Verify Current State
Check git status and recent commits:
```bash
git status
git branch
git log --oneline -5
```

### 4. Confirm Reload Complete
Report:
```
✅ Context reloaded successfully

Current state:
- Project: TSH ERP Ecosystem
- Phase: [current Zoho migration phase from PROJECT_VISION.md]
- Tech Stack: FastAPI + Flutter + PostgreSQL
- Environment: [Development/Production from PROJECT_VISION.md]
- Recent commits: [summary from git log]
- Branch: [current branch]
- Status: [clean/uncommitted changes]

Ready to continue. What would you like to work on?
```

### 5. Load Additional Files As Needed
Based on the task, load:
- `TASK_PATTERNS.md` - For workflow guidance
- `CODE_TEMPLATES.md` - For implementation patterns
- `FAILSAFE_PROTOCOL.md` - For error recovery
- `REASONING_PATTERNS.md` - For complex problem-solving
- `PERFORMANCE_OPTIMIZATION.md` - For optimization tasks

### Important Notes
- Always read core files (Priority 1) completely
- Verify git state for current work context
- Report clearly what was loaded
- Be ready to continue immediately after reload
- Don't ask Khaleel to repeat information from `.claude/` files
