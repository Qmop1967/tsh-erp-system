# AI Context Core Guidelines

**Purpose:** Essential rules for interpreting TSH ERP documentation
**Last Updated:** 2025-11-14
**Load via:** @docs/reference/ai-guidelines/ai-context-core.md

---

## 📚 Documentation Hierarchy (Priority Order)

When conflicts arise between documentation files, follow this priority:

### Level 1: CLAUDE.md (Auto-Loaded)
- **Purpose:** Essential facts and rules (auto-loaded every session)
- **Authority:** Primary reference for daily operations
- **Content:** Core facts, critical rules, common commands
- **When to Use:** Every session (automatic)

### Level 2: PROJECT_VISION.md → core/project-context.md
- **Purpose:** Business context and strategic direction
- **Authority:** SUPREME on business requirements
- **Content:** Scale, migration phases, business model
- **When to Use:** When clarifying business logic or requirements

### Level 3: ARCHITECTURE_RULES.md → core/architecture.md
- **Purpose:** Technical constraints and patterns
- **Authority:** SUPREME on technical implementation
- **Content:** Tech stack, security patterns, coding conventions
- **When to Use:** When implementing features or writing code

### Level 4: TASK_PATTERNS.md → core/workflows.md
- **Purpose:** Step-by-step operational workflows
- **Authority:** Process guidance
- **Content:** Feature implementation, bug fixes, deployments
- **When to Use:** When executing specific task types

### Level 5: Specialized Documentation (reference/)
- **Purpose:** Detailed guidance on specific topics
- **Authority:** Subject-specific
- **Content:** Code templates, failsafe protocols, detailed patterns
- **When to Use:** Load on-demand with @docs/ when needed

---

## 🧠 Context Interpretation Rules

### Rule 1: Never Summarize Back to User
```yaml
❌ DON'T SAY:
"I've read PROJECT_VISION.md which says you have 500+ clients..."

✅ DO SAY:
"This feature needs to handle 500+ wholesale clients efficiently..."

Principle: Internalize context, don't repeat it back
```

### Rule 2: Infer Actionable Rules
```yaml
DON'T just store information passively
DO derive operational rules from context

Example:
Context: "Data comes from BOTH Zoho Books AND Zoho Inventory"

Inferred Rules:
  - When syncing products → check Zoho Inventory API
  - When syncing invoices → check Zoho Books API
  - TDS Core must handle BOTH APIs
  - Never assume all data is in one place
```

### Rule 3: Connect Related Context
```yaml
DON'T treat each file as isolated
DO connect business + technical context

Example:
PROJECT_VISION: "500+ wholesale clients, 30 orders/day"
ARCHITECTURE_RULES: "Use pagination, max 100 items per page"

Connected Understanding:
  → Large datasets require pagination
  → Database indexes are critical
  → Performance matters (not just nice-to-have)
```

### Rule 4: Maintain Temporal Awareness
```yaml
Remember:
  - Current phase: Zoho Migration Phase 1
  - Environment: Development (deploy anytime)
  - Scale: 500+ clients, 2,218+ products
  - Date: 2025-11-14

Check "Last Updated" dates to know if information is current
```

---

## ⚖️ Conflict Resolution Protocol

When documentation appears to conflict:

### Step 1: Check Priority Hierarchy
```
CLAUDE.md conflicts with other file?
  → CLAUDE.md wins (it's the synthesized truth)

core/project-context.md conflicts with core/architecture.md?
  → For business logic: project-context.md wins
  → For technical implementation: architecture.md wins

Current state conflicts with archived docs?
  → Current state wins (archived is historical)
```

### Step 2: Context Matters
```yaml
Example Conflict:
- PROJECT_VISION.md: "Deploy anytime during development"
- DEPLOYMENT_GUIDE.md: "Avoid business hours"

Resolution:
1. Check current phase → Development phase
2. PROJECT_VISION takes precedence for current state
3. DEPLOYMENT_GUIDE applies to future production phase
4. Current context: Deploy anytime ✅
```

### Step 3: Ask User if Unclear
```yaml
When to Ask:
  - Genuine ambiguity (both interpretations valid)
  - Missing information
  - Business logic decision needed
  - Multiple technical approaches possible

How to Ask:
  ✅ "I see PROJECT_VISION says X but ARCHITECTURE says Y.
      For [specific case], should I follow [approach A] or [approach B]?"

  ❌ "The documentation is confusing, what should I do?"
```

---

## 🎯 Core Behavioral Rules (IMMUTABLE)

### Absolute Never Do
```yaml
❌ NEVER suggest changing tech stack (FastAPI/Flutter/PostgreSQL fixed)
❌ NEVER bypass TDS Core for Zoho operations
❌ NEVER deploy partial components (ALL together)
❌ NEVER forget Arabic support (name_ar, description_ar mandatory)
❌ NEVER skip authorization (RBAC + ABAC + RLS all 3 layers)
❌ NEVER write to Zoho in Phase 1 (read-only restriction)
❌ NEVER hardcode credentials (use environment variables)
❌ NEVER use Twilio or Firebase (TSH NeuroLink handles all communications)
```

### Always Do
```yaml
✅ ALWAYS search existing code before creating new
✅ ALWAYS include all 3 authorization layers
✅ ALWAYS include Arabic fields on user-facing data
✅ ALWAYS paginate results > 100 records
✅ ALWAYS use parameterized queries (prevent SQL injection)
✅ ALWAYS route Zoho operations through TDS Core
✅ ALWAYS test on staging before production
✅ ALWAYS deploy ALL components together
```

---

## 🔄 Context Refresh Triggers

### Automatic Refresh Events

**Trigger 1: User Explicitly Says**
```yaml
Statements that trigger full re-read:
  - "We've moved to Phase 2"
  - "We're now in production"
  - "The architecture has changed"
  - "Re-read the vision"
  - "Reload context"
```

**Trigger 2: Session Reset Detected**
```yaml
Signs of context loss:
  - Previous messages not visible
  - Don't remember recent work
  - Conversation history truncated
  - New session without context

Action:
1. Acknowledge: "I notice this is a new session"
2. Reload: Read CLAUDE.md + recent state/
3. Check git: Recent commits, current branch
4. Ask: "What were we working on?"
```

**Trigger 3: Repeated Corrections**
```yaml
If user corrects same thing 2+ times:
  - Indicates outdated context
  - Need to re-read relevant files
  - Update mental model
  - Don't repeat same mistake
```

---

## 📋 Quick Decision Framework

### Should I Create New Code or Enhance Existing?
```
1. Search existing code (grep, find, Task tool)
2. Found similar?
   YES → Enhance existing ✅
   NO → Create new following patterns ✅
   UNSURE → Use Task tool with Explore agent
```

### Should I Ask User?
```
1. Is this business logic?
   YES → Ask user ✅
   NO → Continue to step 2

2. Is there ONE clear technical solution?
   YES → Implement ✅
   NO (multiple options) → Ask user ✅
```

### Should I Optimize This?
```
1. Is it slow? (>2 seconds)
   NO → Don't optimize (premature) ❌
   YES → Continue to step 2

2. Does it affect many users?
   NO → Low priority (defer) ⏸️
   YES → Optimize now ✅

3. How to optimize:
   Measure → Identify bottleneck → Fix → Verify
```

---

## 💡 Context Loading Strategy

### Session Start (Automatic)
```yaml
1. CLAUDE.md auto-loads (387 lines)
2. Contains links to other files via @docs/
3. Ready to work in 2-5 seconds
4. Load additional files only when needed
```

### When to Load Additional Files
```yaml
Business Logic Question:
  → Load @docs/core/project-context.md

Technical Implementation:
  → Load @docs/core/architecture.md

Workflow Steps:
  → Load @docs/core/workflows.md

Code Examples:
  → Load @docs/reference/code-templates/*

Security Check:
  → Load @docs/reference/ai-guidelines/ai-monitoring.md

Emergency:
  → Load @docs/FAILSAFE_PROTOCOL.md
```

---

## 🎯 Success Indicators

**I'm working effectively when:**
```yaml
✅ User doesn't repeat context
✅ I search before creating new code
✅ I never forget Arabic fields
✅ I never forget 3 authorization layers
✅ I deploy all components together
✅ I test on staging first
✅ Features work correctly first time
✅ User feels productive
```

**Red flags (need improvement):**
```yaml
❌ User repeats same context
❌ I create duplicate functionality
❌ I forget Arabic or authorization
❌ I deploy partial components
❌ I skip staging testing
❌ Same bugs repeat
```

---

## 📊 Context Health Checklist

**Before starting ANY work:**
```yaml
□ CLAUDE.md content internalized
□ Current phase understood (Phase 1: read-only)
□ Current environment known (Development)
□ Current git branch verified
□ Tech stack constraints clear
□ Authorization framework clear (RBAC + ABAC + RLS)
□ Arabic support requirements clear
□ Scale awareness active (500+ clients, 2,218+ products)
```

---

**For More Details:**
- Session recovery: @docs/reference/ai-guidelines/ai-session-recovery.md
- Security monitoring: @docs/reference/ai-guidelines/ai-monitoring.md
- Operation modes: @docs/reference/ai-guidelines/ai-operation-modes.md
- Learning & adaptation: @docs/reference/ai-guidelines/ai-learning.md
