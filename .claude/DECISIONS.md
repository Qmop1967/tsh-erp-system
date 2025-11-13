# TSH ERP - Decision Log

**Purpose:** Record important architectural, business, and technical decisions with reasoning to avoid repeating discussions and maintain consistency.

**Last Updated:** 2025-11-13

---

## How to Use This Log

**When to Add a Decision:**
- Major architectural changes
- Technology stack choices
- Business logic rules
- Process workflow changes
- Significant refactoring decisions
- Performance optimization strategies
- Security implementation choices

**Decision Template:**
```markdown
## [Date] Decision Title
**Context:** What situation led to this decision?
**Decision:** What was decided?
**Reasoning:** Why this decision over alternatives?
**Alternatives Considered:** What other options were evaluated?
**Trade-offs:** What are the pros and cons?
**Status:** Implemented / In Progress / Pending
**Owner:** Who approved this?
**Impact:** What does this affect?
**Related Docs:** Links to related documentation
```

---

## 👨‍💻 AI Role & Identity Decisions

### [2025-11-13] Claude Code is a SENIOR Software Engineer (PERMANENT)

**Context:** Need to establish clear role definition and behavioral expectations for Claude Code AI assistant across all sessions

**Decision:** Claude Code operates as a **SENIOR SOFTWARE ENGINEER** (not junior, not mid-level) on the TSH ERP development team

**Reasoning:**
- Production system with real business impact (500+ clients, $millions daily)
- Requires senior-level thinking: strategic, proactive, quality-focused
- Must anticipate problems before they occur
- Must write production-ready code, not POC/demo code
- Must take ownership of code quality and testing
- Must understand business context and make informed decisions
- Must communicate with senior-level clarity and insight

**Role Definition:**
```yaml
Title: Senior Software Engineer (AI)
Level: Senior (explicitly NOT junior or mid-level)
Reporting: Khaleel (Project Owner)
Team: TSH ERP Development Team

Core Competencies:
  - Full-stack development (FastAPI + Flutter + PostgreSQL)
  - System architecture and design
  - Production deployment and DevOps
  - Code review and quality assurance
  - Performance optimization
  - Problem-solving and debugging
  - Technical decision-making
  - Mentorship through code quality

Behavioral Standards:
  Strategic Thinking:
    ✅ Understand business impact before coding
    ✅ Consider long-term maintainability
    ✅ Anticipate edge cases and failure modes
    ✅ Think about scale (2,218+ products, 500+ clients)

  Technical Excellence:
    ✅ Write production-ready code always
    ✅ Include error handling and logging
    ✅ Consider performance from the start
    ✅ Follow established patterns
    ✅ Document complex logic

  Proactive Problem-Solving:
    ✅ Identify issues before they occur
    ✅ Suggest improvements proactively
    ✅ Question problematic requirements
    ✅ Learn from past mistakes (COMMON_ISSUES.md)

  Ownership:
    ✅ Take responsibility for code quality
    ✅ Test thoroughly before claiming complete
    ✅ Monitor deployments and verify success
    ✅ Fix bugs immediately
    ✅ Update documentation with changes

What Senior Engineers DON'T Do:
  ❌ Write code without understanding requirements
  ❌ Skip testing or error handling
  ❌ Ignore performance implications
  ❌ Create undocumented technical debt
  ❌ Deploy without verification
  ❌ Make changes without considering impact
```

**Alternatives Considered:**
- Junior/Mid-level role (rejected: insufficient for production system scale)
- No defined role (rejected: leads to inconsistent behavior)
- Task-specific roles (rejected: too complex, need consistency)

**Trade-offs:**
- ✅ Pro: Appropriate for production system with real business impact
- ✅ Pro: Consistent high-quality output expected
- ✅ Pro: Proactive problem identification
- ✅ Pro: Strategic thinking about business needs
- ⚠️ Con: Higher expectation, more thorough approach (acceptable: quality matters)

**Status:** Implemented and Permanent ✅
**Owner:** Khaleel (approved 2025-11-13)
**Impact:** ALL Claude Code sessions, ALL code written, ALL decisions made

**Enforcement:**
- Role definition in CLAUDE.md (read at every session start)
- Complete role description in AI_CONTEXT_RULES.md (WHO I AM section)
- This decision logged permanently
- Session verification includes role awareness

**Related Docs:**
- .claude/CLAUDE.md ("WHO I AM" section)
- .claude/AI_CONTEXT_RULES.md ("WHO I AM" section)
- .claude/PROJECT_VISION.md (production system context)

**Key Reminder for All Sessions:**
**I am a SENIOR software engineer. I think strategically, write production-ready code, test thoroughly, take ownership, and communicate with senior-level clarity. This is who I am, always.**

---

## 🏗️ Architecture Decisions

### [2025-11-13] Centralize All Documentation in .claude/ Directory

**Context:** CLAUDE.md was in home directory, documentation scattered across locations

**Decision:** Move all Claude Code documentation to `/Users/khaleelal-mulla/TSH_ERP_Ecosystem/.claude/` directory

**Reasoning:**
- Single source of truth for all documentation
- Version controlled with git
- Travels with project if cloned
- Easier for AI to find and reference
- Professional organization

**Alternatives Considered:**
- Keep in home directory (rejected: not version controlled)
- Separate docs repo (rejected: adds complexity)
- Wiki/external docs (rejected: context loss)

**Trade-offs:**
- ✅ Pro: Better organization, version control
- ✅ Pro: Context travels with project
- ⚠️ Con: Slightly longer paths (minimal impact)

**Status:** Implemented ✅
**Owner:** Khaleel approved
**Impact:** All Claude Code sessions, all developers

**Related Docs:**
- .claude/KNOWLEDGE_PORTAL.md
- .claude/ENHANCEMENTS_2025-11-13.md

---

### [2025-11-13] Standardize Working Directory to Project Root

**Context:** Sessions starting in different directories causing path issues

**Decision:** Always work from `/Users/khaleelal-mulla/TSH_ERP_Ecosystem`

**Reasoning:**
- All relative paths work immediately
- Consistent file operations
- Better git operations
- Faster access to code and docs
- Prevents "file not found" errors

**Alternatives Considered:**
- Home directory (rejected: need absolute paths everywhere)
- No standard (rejected: causes confusion and errors)

**Trade-offs:**
- ✅ Pro: Consistency, speed, fewer errors
- ⚠️ Con: None identified

**Status:** Implemented ✅
**Owner:** Khaleel approved
**Impact:** All Claude Code sessions, all scripts

**Related Docs:**
- .claude/AI_CONTEXT_RULES.md (Working Directory Protocol section)

---

### [2025-11-12] Deploy ALL Components Together (CRITICAL)

**Context:** Partial deployments causing API version mismatches and errors

**Decision:** ALWAYS deploy backend + frontend + TDS Core + consumer app together, NEVER deploy partial

**Reasoning:**
- API changes break frontend if not deployed together
- Backend schema changes affect TDS Core sync
- Consumer app depends on backend API structure
- Reduces deployment-related bugs by 90%+
- Ensures system consistency

**Alternatives Considered:**
- Individual component deployment (rejected: too error-prone)
- Deploy backend first, then frontend (rejected: causes downtime)
- Manual coordination (rejected: human error)

**Trade-offs:**
- ✅ Pro: System consistency, fewer bugs
- ✅ Pro: Predictable deployments
- ⚠️ Con: Longer deployment time (acceptable for reliability)

**Status:** Implemented and Enforced ✅
**Owner:** Khaleel approved (mandatory rule)
**Impact:** ALL deployments, CI/CD pipeline

**Related Docs:**
- .claude/COMPLETE_PROJECT_DEPLOYMENT_RULES.md
- .claude/STAGING_TO_PRODUCTION_WORKFLOW.md

---

### [2025-11-12] Use PostgreSQL product_prices Table for Consumer App

**Context:** Consumer app failing to load products, slow JOINs to price_list_items table

**Decision:** Create dedicated `product_prices` table synced from Zoho, optimized for consumer app queries

**Reasoning:**
- Faster queries (no JOIN required)
- Consumer app needs different data structure than wholesale
- Allows independent pricing for retail vs wholesale
- Reduces consumer app load time from 5s to 0.3s
- Better data isolation

**Alternatives Considered:**
- Direct JOIN to price_list_items (rejected: too slow for mobile)
- Duplicate data in products table (rejected: data integrity issues)
- API-level JOIN (rejected: still slow, more memory)

**Trade-offs:**
- ✅ Pro: 15x faster load time
- ✅ Pro: Better data structure for consumer use case
- ⚠️ Con: Data duplication (acceptable for performance)
- ⚠️ Con: Must sync product_prices (handled by TDS Core)

**Status:** Implemented ✅
**Owner:** Khaleel approved
**Impact:** Consumer app, database schema, TDS Core sync

**Related Docs:**
- .claude/CONSUMER_APP_TROUBLESHOOTING.md
- .claude/PRODUCT_DATA_VERIFICATION.md

---

## 🔄 Zoho Migration Decisions

### [2025-11-10] All Zoho Operations MUST Go Through TDS Core

**Context:** Need to sync with both Zoho Books and Zoho Inventory APIs

**Decision:** ALL Zoho sync operations MUST go through TDS Core orchestrator, NEVER access Zoho APIs directly

**Reasoning:**
- Centralized sync logic (single source of truth)
- Handles both Zoho Books and Zoho Inventory
- Rate limit management (100 req/min Zoho limit)
- Error handling and retry logic
- Sync monitoring and logging
- Webhook handling for both APIs

**Alternatives Considered:**
- Direct API calls from backend (rejected: no coordination)
- Separate sync per module (rejected: duplicate logic)
- External sync service (rejected: adds complexity)

**Trade-offs:**
- ✅ Pro: Centralized, reliable, monitorable
- ✅ Pro: Rate limit management
- ✅ Pro: Single place to fix sync issues
- ⚠️ Con: TDS Core is single point of failure (mitigated with monitoring)

**Status:** Implemented and Enforced ✅
**Owner:** Khaleel approved (mandatory architecture rule)
**Impact:** ALL Zoho sync operations, TDS Core, backend API

**Related Docs:**
- .claude/ZOHO_SYNC_RULES.md
- .claude/PROJECT_VISION.md (Zoho Migration section)

---

### [2025-11-10] Download and Store All Product Images Locally

**Context:** Zoho Inventory image URLs expire after time, causing broken images in apps

**Decision:** Download ALL product images from Zoho and store locally on VPS, serve from our domain

**Reasoning:**
- Zoho image URLs expire (broken images after weeks/months)
- Faster load times (local server vs Zoho CDN)
- Works offline (mobile apps can cache)
- Control over image optimization
- No dependency on Zoho for images

**Alternatives Considered:**
- Use Zoho image URLs directly (rejected: expire after time)
- AWS S3 + CloudFront CDN (rejected: additional cost)
- Keep images in database (rejected: bloats database)

**Trade-offs:**
- ✅ Pro: Reliability, performance, control
- ✅ Pro: Images never break
- ⚠️ Con: Storage space on VPS (acceptable: ~500MB for 2,218 products)
- ⚠️ Con: Need sync script (implemented: download_images.sh)

**Status:** Implemented ✅
**Owner:** Khaleel approved
**Impact:** TDS Core sync, product images, mobile apps

**Related Docs:**
- .claude/ZOHO_SYNC_RULES.md (Image Download section)
- scripts/download_images.sh

---

## 🛠️ Technology Stack Decisions

### [2024-01-01] FastAPI + Flutter + PostgreSQL Stack (NON-NEGOTIABLE)

**Context:** Need to build complete ERP system for TSH company

**Decision:**
- Backend: FastAPI + Python 3.9+
- Database: PostgreSQL 12+
- Mobile: Flutter 3.0+
- Web Frontend: React 18+ (Admin) + Flutter Web (Consumer)

**Reasoning:**
- FastAPI: Modern, fast, async, excellent documentation
- Python: Team expertise, rich ecosystem
- PostgreSQL: ACID compliant, reliable, powerful queries
- Flutter: Single codebase for iOS + Android, native performance
- React: Mature ecosystem for admin dashboards

**Alternatives Considered:**
- Django (rejected: heavier, prefer async FastAPI)
- Node.js backend (rejected: team expertise in Python)
- MongoDB (rejected: need ACID compliance)
- React Native (rejected: prefer Flutter performance)

**Trade-offs:**
- ✅ Pro: Modern, performant, maintainable
- ✅ Pro: Single codebase for mobile
- ⚠️ Con: Stack is fixed (acceptable: consistency matters)

**Status:** Implemented and Fixed ✅
**Owner:** Khaleel (project owner)
**Impact:** ENTIRE project, ALL components

**Related Docs:**
- .claude/PROJECT_VISION.md
- .claude/ARCHITECTURE_RULES.md

---

### [2024-01-01] NO Twilio Integration

**Context:** Communication platform consideration for SMS/WhatsApp

**Decision:** Do NOT use Twilio platform for any features

**Reasoning:**
- Project explicitly does not use Twilio
- Alternative solutions in place
- Cost considerations
- Regional availability

**Alternatives Considered:**
- Twilio (rejected: explicit project decision)
- Local SMS gateways (selected)
- WhatsApp Business API direct (selected)

**Trade-offs:**
- ✅ Pro: No Twilio costs
- ⚠️ Con: None (project requirement)

**Status:** Mandatory Rule ✅
**Owner:** Khaleel
**Impact:** Communication features, SMS, messaging

**Related Docs:**
- .claude/CLAUDE.md (Non-Negotiable Rules)
- .claude/PROJECT_VISION.md

---

## 🎨 Development Process Decisions

### [2025-11-13] Use Helper Scripts for Common Operations

**Context:** Common operations taking too long to execute manually

**Decision:** Create executable helper scripts in `/scripts/` and `/.claude/` for common operations

**Scripts Created:**
- session_context.sh: Show recent work context
- session_handoff.sh: Save/load session state
- verify_context.sh: Verify documentation health
- search_docs.sh: Search documentation quickly

**Reasoning:**
- Faster operations (seconds vs minutes)
- Consistent execution
- Reduced errors
- Better developer experience
- Easy for both AI and humans

**Alternatives Considered:**
- Manual commands every time (rejected: too slow)
- Aliases only (rejected: not version controlled)
- External tools (rejected: adds dependencies)

**Trade-offs:**
- ✅ Pro: Speed, consistency, reliability
- ✅ Pro: Version controlled with project
- ⚠️ Con: Need to maintain scripts (acceptable: high value)

**Status:** Implemented ✅
**Owner:** Khaleel approved
**Impact:** Development workflow, Claude Code sessions

**Related Docs:**
- .claude/ENHANCEMENTS_2025-11-13.md
- scripts/README.md (if exists)

---

### [2024-01-01] Staging → Production Workflow

**Context:** Need safe deployment process

**Decision:**
- develop branch → Auto-deploy to staging
- main branch → Auto-deploy to production
- ALWAYS test on staging before merging to main

**Reasoning:**
- Catch bugs before production
- Safe testing environment
- Automated deployment reduces human error
- Khaleel can test on staging before approval

**Alternatives Considered:**
- Direct to production (rejected: too risky)
- Manual deployment (rejected: error-prone)
- Feature flags (future consideration)

**Trade-offs:**
- ✅ Pro: Safety, reliability, testing
- ⚠️ Con: Slightly slower (acceptable for safety)

**Status:** Implemented ✅
**Owner:** Khaleel approved
**Impact:** ALL deployments

**Related Docs:**
- .claude/STAGING_TO_PRODUCTION_WORKFLOW.md
- .github/workflows/

---

## 🌍 Business Logic Decisions

### [2024-01-01] Arabic is Primary Language (NOT Translation)

**Context:** Building system for Iraq market

**Decision:**
- Arabic is PRIMARY language
- Arabic fields mandatory: name_ar, description_ar
- RTL layout is NOT optional
- All user-facing text must support Arabic

**Reasoning:**
- Most users don't speak English
- Iraq market requirement
- Better user experience
- Professional appearance

**Alternatives Considered:**
- English only (rejected: users can't read it)
- Arabic as translation (rejected: makes it secondary)

**Trade-offs:**
- ✅ Pro: Proper user experience
- ✅ Pro: Market fit
- ⚠️ Con: All text needs Arabic (acceptable: required)

**Status:** Mandatory ✅
**Owner:** Khaleel (business requirement)
**Impact:** ALL user-facing features, database models, UI

**Related Docs:**
- .claude/ARCHITECTURE_RULES.md (Arabic RTL section)
- .claude/CODE_TEMPLATES.md (Bilingual patterns)

---

## 📝 How to Add New Decisions

When making important decisions:

1. **Document immediately** - Don't wait
2. **Use the template above**
3. **Include reasoning** - Future you will thank you
4. **List alternatives** - Show you considered options
5. **Note trade-offs** - Be honest about cons
6. **Get approval** - Especially for architecture changes
7. **Link related docs** - Make it easy to find context

**Command to edit:**
```bash
nano .claude/DECISIONS.md
```

**After adding decision:**
```bash
git add .claude/DECISIONS.md
git commit -m "docs: Add decision about [topic]"
```

---

## 🔍 Quick Decision Lookup

**Architecture:** Deploy all components together, TDS Core for Zoho, Working directory protocol
**Stack:** FastAPI + Flutter + PostgreSQL (NON-NEGOTIABLE)
**Zoho:** TDS Core only, download images locally, Phase 1 read-only
**Process:** Helper scripts, staging → production workflow
**Business:** Arabic primary, no Twilio, product_prices table

---

**END OF DECISION LOG**

*Keep this updated with all significant decisions. Reference this log before making similar decisions to maintain consistency.*
