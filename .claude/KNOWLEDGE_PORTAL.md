# Knowledge Portal - TSH ERP Documentation Hub

**Purpose:** Central navigation index for all `.claude/` knowledge files. Start here for orientation.

**Last Updated:** 2025-11-12

---

## 🎯 How to Use This Portal

**For Claude Code (AI):**
- Read this at session start for quick navigation
- Use file loading order (Priority 1 → 5)
- Jump to specific topics as needed during work

**For Human Developers:**
- Start with "Onboarding Path" section
- Use as reference during development
- Bookmark specific files for quick access

---

## 📊 File Loading Priority (For AI Session Start)

### Priority 0: SESSION START - Read Immediately
```yaml
0. CLAUDE.md (~130 lines)
   Purpose: Session start instructions and global rules
   When: At the very start of EVERY new session
   Key Content:
     - Session start routine
     - File reading order
     - Non-negotiable rules (NO TWILIO, tech stack)
     - Project location and structure
     - Verification checklist

   Note: This file directs to read the Priority 1 files below
```

### Priority 1: CRITICAL - Read First
```yaml
1. AI_CONTEXT_RULES.md (~1,540 lines)
   Purpose: Meta-guide - HOW to read and interpret all other files
   When: FIRST file to read in every session (after CLAUDE.md)
   Key Content:
     - File loading order hierarchy
     - Conflict resolution rules
     - Memory continuity strategy
     - Smart Alert Conditions (proactive issue detection)
     - AI Access Levels & Operation Modes

2. PROJECT_VISION.md (~500 lines)
   Purpose: SUPREME AUTHORITY on business context
   When: After AI_CONTEXT_RULES.md
   Key Content:
     - Business purpose & scale (500+ clients, 2,218+ products)
     - Zoho migration 4-phase strategy (currently Phase 1)
     - Tech stack constraints (FastAPI + Flutter + PostgreSQL)
     - Critical rules (NEVER/ALWAYS)
     - User roles and workflows
```

### Priority 2: HIGH - Read for Orientation
```yaml
3. QUICK_REFERENCE.md (~300 lines)
   Purpose: 60-second context refresh
   When: After PROJECT_VISION.md or when confused
   Key Content:
     - 30-second project overview
     - NEVER/ALWAYS rules
     - Decision trees (visual)
     - 10 most common commands
     - Quick context refresh guide

4. SESSION_START.md (~800 lines)
   Purpose: Session start checklist & onboarding
   When: Beginning of every session
   Key Content:
     - AI System Health Check (100+ checkpoints)
     - Session start routine
     - Common task patterns
     - Post-maintenance validation
     - Human onboarding guide

5. ARCHITECTURE_RULES.md (~600 lines)
   Purpose: Technical constraints and patterns
   When: Before implementing any code
   Key Content:
     - Database schema patterns
     - API endpoint conventions
     - Security patterns (auth, RBAC)
     - Arabic RTL implementation
     - AI interaction rules
```

### Priority 3: MEDIUM - Read When Relevant
```yaml
6. WORKING_TOGETHER.md (~400 lines)
   Purpose: Collaboration model (Khaleel + Claude Code)
   When: When unclear about decision-making
   Key Content:
     - Who decides what
     - When to ask vs. when to decide
     - Communication patterns
     - Feature/bug workflows

7. TASK_PATTERNS.md (~1,100 lines)
   Purpose: Step-by-step workflows for task types
   When: Starting any task
   Key Content:
     - Feature implementation workflow (7 steps)
     - Bug fix workflow (6 steps)
     - Pre-action checklists (60+ points)
     - Deployment workflow
     - Testing patterns

8. REASONING_PATTERNS.md (~1,200 lines)
   Purpose: HOW to think through problems
   When: Complex problems, trade-offs, debugging
   Key Content:
     - Root-cause analysis (5 Whys method)
     - Trade-off decision framework
     - Performance analysis
     - Strategic business-tech alignment
     - Change impact analysis
```

### Priority 4: SPECIALIZED - Read As Needed
```yaml
9. CODE_TEMPLATES.md (~2,500 lines)
   Purpose: Reusable code patterns with reasoning
   When: Implementing features
   Key Content:
     - Authentication & authorization templates
     - CRUD operations (with Arabic + pagination)
     - Zoho sync operations (via TDS Core)
     - Bilingual field patterns
     - Error response templates
     - Database query optimization

10. PERFORMANCE_OPTIMIZATION.md (~1,000 lines)
    Purpose: Performance strategies for TSH scale
    When: Optimizing slow operations
    Key Content:
      - Database optimization (indexes, queries)
      - API optimization (caching, compression)
      - Mobile app optimization
      - Performance thresholds & monitoring
      - Quick wins (high ROI optimizations)

11. FAILSAFE_PROTOCOL.md (~900 lines)
    Purpose: System failure recovery procedures
    When: Production issues, errors, emergencies
    Key Content:
      - 5 critical failure scenarios & recovery
      - Safe-mode operations
      - Backup & restore procedures
      - Emergency contacts
      - Common error patterns & solutions

12. SESSION_CHECKLIST.md (~1,160 lines)
    Purpose: Practical session metrics & validation
    When: Throughout session (start, during, end)
    Key Content:
      - Session start checklist
      - Code search protocol
      - Testing protocol
      - Output validation (8 quality gates)
      - Deployment checklist
```

### Priority 5: SESSION CONTINUITY - Memory & Context
```yaml
13. SESSION_STATE.md (~200 lines)
    Purpose: Track current work across sessions
    When: Session start/end, context recovery
    Key Content:
      - Current task and progress
      - Recent context (last session)
      - Active branches and git status
      - Pending questions
      - Session continuity instructions

14. DECISIONS.md (~800 lines)
    Purpose: Record important decisions with reasoning
    When: Making architectural/business decisions
    Key Content:
      - Architecture decisions (deploy all, TDS Core, working directory)
      - Zoho migration decisions
      - Technology stack decisions (non-negotiable)
      - Development process decisions
      - Business logic decisions

15. COMMON_ISSUES.md (~1,000 lines)
    Purpose: Recurring problems with proven solutions
    When: Debugging, troubleshooting, problem-solving
    Key Content:
      - Critical issues (production impact)
      - High/Medium/Low impact issues
      - Root cause analysis
      - Step-by-step solutions
      - Prevention strategies
      - Issue statistics
```

### Priority 6: ADMINISTRATIVE - Reference Only
```yaml
16. CHANGELOG_AI.md (~300 lines)
    Purpose: Track .claude/ system changes
    When: After major updates, phase transitions
    Key Content:
      - Historical changes to documentation
      - Context evolution over time
      - Update instructions

17. KNOWLEDGE_LINKS.md (~200 lines)
    Purpose: Operational resources (URLs, credentials)
    When: Need access to systems
    Key Content:
      - GitHub repository
      - VPS server details
      - Database credentials
      - Zoho organization info
      - Domain management

18. KNOWLEDGE_PORTAL.md (This file)
    Purpose: Navigation index
    When: Session start or when lost
    Key Content:
      - File loading priority
      - Topic-based navigation
      - Onboarding paths
```

---

## 🗂️ Topic-Based Navigation

### 🚀 Session Start & Orientation
```yaml
Start a new session:
  → CLAUDE.md (session start instructions, global rules)

Get oriented quickly:
  → QUICK_REFERENCE.md (60-second context refresh)

Navigate documentation:
  → KNOWLEDGE_PORTAL.md (this file - navigation index)

Resume previous work:
  → SESSION_STATE.md (current task, recent context)
  → scripts/session_handoff.sh (save/load session state)
```

### 🧠 Memory & Context (NEW)
```yaml
Track current work:
  → SESSION_STATE.md (what I'm working on now)

Remember decisions:
  → DECISIONS.md (why we made certain choices)

Solve recurring problems:
  → COMMON_ISSUES.md (known issues with solutions)

Session recovery:
  → scripts/session_handoff.sh (automated save/load)
```

### 🧠 Thinking & Learning
```yaml
How to think systematically:
  → REASONING_PATTERNS.md (root-cause, trade-offs, performance)

How to interpret documentation:
  → AI_CONTEXT_RULES.md (meta-guide, conflict resolution)

What's changed recently:
  → CHANGELOG_AI.md (historical tracking)
```

### ⚙️ Engineering & Code
```yaml
Copy-paste code patterns:
  → CODE_TEMPLATES.md (auth, CRUD, Zoho sync, pagination)

Optimize performance:
  → PERFORMANCE_OPTIMIZATION.md (database, API, mobile)

Step-by-step task workflows:
  → TASK_PATTERNS.md (feature, bug fix, deployment)
```

### 🔒 Security & Recovery
```yaml
Handle system failures:
  → FAILSAFE_PROTOCOL.md (PostgreSQL, GitHub Actions, Zoho sync, errors)

Detect security issues:
  → AI_CONTEXT_RULES.md (Smart Alert Conditions section)

Secure code patterns:
  → CODE_TEMPLATES.md (authentication, authorization, validation)
```

### 🧾 Operations & Process
```yaml
Session start routine:
  → SESSION_START.md (health check, validation, onboarding)

Task execution checklist:
  → SESSION_CHECKLIST.md (code search, testing, output validation)

Quick context refresh:
  → QUICK_REFERENCE.md (60-second overview, decision trees)

Deployment process:
  → TASK_PATTERNS.md (Deployment section)
  → SESSION_CHECKLIST.md (Deployment checklist)
```

### 📖 Business & Architecture
```yaml
Business context & strategy:
  → PROJECT_VISION.md (scale, Zoho migration, constraints)

Technical rules & patterns:
  → ARCHITECTURE_RULES.md (database, API, security, Arabic)

Collaboration model:
  → WORKING_TOGETHER.md (who decides what, when to ask)

System access & resources:
  → KNOWLEDGE_LINKS.md (GitHub, VPS, Zoho, domains)
```

---

## 🎓 Onboarding Paths

### For AI (Claude Code) - New Session

**5-Minute Orientation:**
```yaml
1. Read AI_CONTEXT_RULES.md (2 min)
   → Understand how to interpret files

2. Read QUICK_REFERENCE.md (1 min)
   → Get 30-second project overview

3. Read PROJECT_VISION.md key sections (2 min)
   → Scale, Zoho phase, tech stack, critical rules

Status: READY FOR BASIC TASKS
```

**15-Minute Deep Dive:**
```yaml
4. Read SESSION_START.md (5 min)
   → Complete health check checklist

5. Read ARCHITECTURE_RULES.md (5 min)
   → Technical constraints, patterns

6. Read WORKING_TOGETHER.md (3 min)
   → Collaboration model

7. Skim TASK_PATTERNS.md (2 min)
   → Familiarize with workflows

Status: READY FOR COMPLEX TASKS
```

---

### For Human Developers - First Day

**Day 1: Context Immersion (3-4 hours)**
```yaml
Morning:
□ Read PROJECT_VISION.md (1 hour)
  → Business context, scale, Zoho migration

□ Read ARCHITECTURE_RULES.md (1 hour)
  → Tech stack, patterns, security

□ Read WORKING_TOGETHER.md (30 min)
  → Collaboration with Khaleel

□ Read QUICK_REFERENCE.md (15 min)
  → Quick facts, commands

Lunch Break

Afternoon:
□ Read SESSION_START.md (30 min)
  → Checklist, common patterns

□ Setup local environment (1 hour)
  → Follow instructions in SESSION_START.md

□ Explore codebase (30 min)
  → Browse /app/, /mobile/, /scripts/

Status: CONTEXT LOADED
```

**Day 2-3: Hands-On Learning**
```yaml
□ Fix a minor bug (Khaleel assigns)
  → Follow TASK_PATTERNS.md (Bug Fix workflow)
  → Reference CODE_TEMPLATES.md as needed

□ Add a small feature (Khaleel assigns)
  → Follow TASK_PATTERNS.md (Feature workflow)
  → Use CODE_TEMPLATES.md for patterns

□ Deploy to staging
  → Follow SESSION_CHECKLIST.md (Deployment)

Status: PRODUCTIVE DEVELOPER
```

---

### For Emergency Situations

**Production Down (2 Minutes)**
```yaml
1. QUICK_REFERENCE.md → Emergency Contacts section
2. FAILSAFE_PROTOCOL.md → Scenario matching issue
3. Execute recovery steps
4. Alert Khaleel
```

**Zoho Sync Failed (5 Minutes)**
```yaml
1. FAILSAFE_PROTOCOL.md → Scenario 3 (TDS Core sync)
2. Follow diagnostic steps
3. Apply fix
4. Monitor recovery
```

**Unknown Error (10 Minutes)**
```yaml
1. REASONING_PATTERNS.md → Root-Cause Analysis
2. FAILSAFE_PROTOCOL.md → Error Pattern Knowledge Base
3. CODE_TEMPLATES.md → Error Response patterns
4. Debug systematically
```

---

## 📋 File Size Reference (For Context Budget)

```yaml
Small Files (< 500 lines) - Quick reads:
  QUICK_REFERENCE.md         ~300 lines   (2 min read)
  CHANGELOG_AI.md            ~300 lines   (2 min read)
  KNOWLEDGE_LINKS.md         ~200 lines   (1 min read)
  KNOWLEDGE_PORTAL.md        ~400 lines   (3 min read)

Medium Files (500-1,000 lines) - Focused reading:
  PROJECT_VISION.md          ~500 lines   (10 min read)
  ARCHITECTURE_RULES.md      ~600 lines   (12 min read)
  WORKING_TOGETHER.md        ~400 lines   (8 min read)
  SESSION_START.md           ~800 lines   (15 min read)
  FAILSAFE_PROTOCOL.md       ~900 lines   (18 min read)
  PERFORMANCE_OPTIMIZATION   ~1,000 lines (20 min read)

Large Files (1,000+ lines) - Reference material:
  TASK_PATTERNS.md           ~1,100 lines (browse as needed)
  REASONING_PATTERNS.md      ~1,200 lines (browse as needed)
  SESSION_CHECKLIST.md       ~1,160 lines (checklist format)
  AI_CONTEXT_RULES.md        ~1,540 lines (browse as needed)
  CODE_TEMPLATES.md          ~2,500 lines (copy-paste reference)

Total: ~11,800 lines (~600 KB)
```

---

## 🔍 Quick Find

**"I need to..."**

```yaml
...understand the business:
  → PROJECT_VISION.md

...know what tech to use:
  → ARCHITECTURE_RULES.md

...see code examples:
  → CODE_TEMPLATES.md

...optimize performance:
  → PERFORMANCE_OPTIMIZATION.md

...handle an error:
  → FAILSAFE_PROTOCOL.md

...start a task:
  → TASK_PATTERNS.md

...think through a problem:
  → REASONING_PATTERNS.md

...check my output quality:
  → SESSION_CHECKLIST.md (Output Validation section)

...get oriented quickly:
  → QUICK_REFERENCE.md

...recover from confusion:
  → This file (KNOWLEDGE_PORTAL.md)

...resume previous work:
  → SESSION_STATE.md
  → scripts/session_handoff.sh

...understand past decisions:
  → DECISIONS.md

...solve a recurring problem:
  → COMMON_ISSUES.md
```

---

## 🆕 Recently Added/Updated Files

```yaml
[2025-11-13] Session Continuity & Memory Enhancement:
  ✅ SESSION_STATE.md (NEW - track current work across sessions)
  ✅ DECISIONS.md (NEW - record important decisions with reasoning)
  ✅ COMMON_ISSUES.md (NEW - recurring problems with solutions)
  ✅ scripts/session_handoff.sh (NEW - save/load session state)
  ✅ KNOWLEDGE_PORTAL.md (UPDATED - added Priority 5 Session Continuity)

[2025-11-13] Session Start Enhancement:
  ✅ CLAUDE.md (MOVED - from home directory to .claude/)
  ✅ QUICK_START.txt (NEW - ultra-fast reference card)
  ✅ ENHANCEMENTS_2025-11-13.md (NEW - enhancement documentation)
  ✅ .claude/verify_context.sh (NEW - automated verification script)
  ✅ .claude/search_docs.sh (NEW - fast documentation search)
  ✅ scripts/session_context.sh (NEW - session recovery helper)
  ✅ AI_CONTEXT_RULES.md (UPDATED - Working Directory Protocol)
  ✅ KNOWLEDGE_PORTAL.md (UPDATED - added CLAUDE.md as Priority 0)

[2025-11-12] Phase IV Implementation:
  ✅ CODE_TEMPLATES.md (NEW - 2,500 lines)
  ✅ PERFORMANCE_OPTIMIZATION.md (NEW - 1,000 lines)
  ✅ QUICK_REFERENCE.md (NEW - 300 lines)
  ✅ KNOWLEDGE_PORTAL.md (NEW - this file)
  ✅ FAILSAFE_PROTOCOL.md (ENHANCED - added error patterns)

[2025-11-12] Phase III Implementation:
  ✅ REASONING_PATTERNS.md (NEW - 1,200 lines)
  ✅ FAILSAFE_PROTOCOL.md (NEW - 800 lines)
  ✅ AI_CONTEXT_RULES.md (ENHANCED - alerts + modes)
  ✅ TASK_PATTERNS.md (ENHANCED - pre-action checklists)
  ✅ SESSION_CHECKLIST.md (ENHANCED - output validation)

[2025-11-12] Phase II Implementation:
  ✅ TASK_PATTERNS.md (NEW - 900 lines)
  ✅ CHANGELOG_AI.md (NEW - 300 lines)
  ✅ SESSION_CHECKLIST.md (NEW - 900 lines)

[2025-11-12] Initial .claude/ System:
  ✅ AI_CONTEXT_RULES.md (700 lines)
  ✅ PROJECT_VISION.md (500 lines)
  ✅ WORKING_TOGETHER.md (400 lines)
  ✅ SESSION_START.md (440 lines)
  ✅ ARCHITECTURE_RULES.md (600 lines)
  ✅ KNOWLEDGE_LINKS.md (200 lines)
```

---

## ✅ Documentation Health Check

**Before starting work, verify:**

```yaml
□ All 27 markdown files + 1 TXT file present in .claude/ directory
□ CLAUDE.md read (session start instructions)
□ AI_CONTEXT_RULES.md read (loading order understood)
□ PROJECT_VISION.md internalized (business context clear)
□ QUICK_REFERENCE.md read (quick facts)
□ SESSION_STATE.md available (session continuity)
□ DECISIONS.md available (decision reference)
□ COMMON_ISSUES.md available (problem solving)
□ Current phase confirmed (Zoho Migration Phase 1)
□ Current environment known (Development, deploy anytime)
□ "Last Updated" dates reviewed (context is current)
□ No knowledge gaps or confusion

Status: READY TO WORK
```

---

## 🎯 Next Steps

**After reading this portal:**

```yaml
If New AI Session:
  1. Read CLAUDE.md (session start instructions)
  2. Read AI_CONTEXT_RULES.md (meta-guide)
  3. Read PROJECT_VISION.md (business context)
  4. Read QUICK_REFERENCE.md (quick facts)
  5. Confirm with: "Context loaded. TSH ERP Ecosystem ready. How can I help?"

If New Human Developer:
  1. Follow Day 1 onboarding path (above)
  2. Setup local environment
  3. Ask Khaleel for first task

If Lost/Confused:
  1. Re-read QUICK_REFERENCE.md
  2. Check relevant topic section (above)
  3. Ask Khaleel for clarification

If Emergency:
  1. Jump to FAILSAFE_PROTOCOL.md
  2. Follow recovery procedures
  3. Alert Khaleel
```

---

**END OF KNOWLEDGE_PORTAL.MD**

*Your navigation hub. Bookmark this file for quick access to all TSH ERP documentation.*
