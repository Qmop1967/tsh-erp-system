# AI Guidelines for Claude Code

**Purpose:** Meta-instructions for how Claude Code should interpret and use TSH ERP documentation
**Last Updated:** 2025-11-14
**Original:** AI_CONTEXT_RULES.md (1,701 lines) - Split into modular components

---

## Module Structure

The original AI_CONTEXT_RULES.md has been split into focused modules:

### Core Guidelines (Load First)
- **ai-context-core.md** - File hierarchy, interpretation rules, conflict resolution
  - How to read and prioritize documentation
  - Conflict resolution between files
  - Core behavioral rules

### Operational Guidelines (Load When Needed)
- **ai-session-recovery.md** - Session continuity and context recovery
  - Memory continuity strategy
  - Session recovery protocol
  - Context refresh procedures

- **ai-monitoring.md** - Proactive monitoring and alerting
  - Security vulnerability detection
  - Performance issue detection
  - Smart alert conditions

- **ai-operation-modes.md** - Access levels and operational boundaries
  - Read-only vs Development vs Critical operations
  - What operations are allowed in each mode
  - Error handling protocols

- **ai-learning.md** - Learning, adaptation, and success metrics
  - How to learn from mistakes
  - Operational excellence patterns
  - Success indicators

---

## When to Load Each Module

```yaml
Session Start:
  - CLAUDE.md (auto-loaded)
  - ai-context-core.md (if confusion about documentation hierarchy)

When Context is Lost:
  - ai-session-recovery.md

When Writing Code:
  - ai-monitoring.md (for security/performance checks)

Before Critical Operations:
  - ai-operation-modes.md

When Evaluating Performance:
  - ai-learning.md
```

---

## Usage Pattern

```markdown
# In conversation:
"I need guidance on how to interpret conflicting documentation"
→ Load @docs/reference/ai-guidelines/ai-context-core.md

"Session was reset, need to recover context"
→ Load @docs/reference/ai-guidelines/ai-session-recovery.md

"Need to check for security issues in code"
→ Load @docs/reference/ai-guidelines/ai-monitoring.md
```

---

## Benefits of Splitting

1. **Focused Loading** - Load only relevant guidance
2. **Faster Sessions** - No need to load all 1,701 lines at once
3. **Better Organization** - Clear separation of concerns
4. **Easier Maintenance** - Update specific modules without affecting others
5. **Selective Context** - Choose what's needed for current task

---

## Original File

The original AI_CONTEXT_RULES.md (1,701 lines) is preserved in `.claude.backup/` for reference.
