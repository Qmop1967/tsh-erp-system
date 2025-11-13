# TSH ERP Ecosystem - Claude Code Instructions

**Last Updated:** 2025-11-13
**Purpose:** Global instructions for Claude Code across all sessions

---

## 🚨 CRITICAL: Read Project Documentation First

Before starting ANY work, you MUST read these files in this order:

### Phase 1: Orientation (5 minutes)
1. **KNOWLEDGE_PORTAL.md** - Navigation guide to all documentation
   ```
   /Users/khaleelal-mulla/TSH_ERP_Ecosystem/.claude/KNOWLEDGE_PORTAL.md
   ```

2. **AI_CONTEXT_RULES.md** - Meta-guide on HOW to read and interpret files
   ```
   /Users/khaleelal-mulla/TSH_ERP_Ecosystem/.claude/AI_CONTEXT_RULES.md
   ```

3. **PROJECT_VISION.md** - Business context, scale, constraints, critical rules
   ```
   /Users/khaleelal-mulla/TSH_ERP_Ecosystem/.claude/PROJECT_VISION.md
   ```

4. **QUICK_REFERENCE.md** - 60-second context refresh
   ```
   /Users/khaleelal-mulla/TSH_ERP_Ecosystem/.claude/QUICK_REFERENCE.md
   ```

### Phase 2: Deep Context (as needed)
After orientation, read these based on task type:
- **ARCHITECTURE_RULES.md** - Before writing any code
- **TASK_PATTERNS.md** - Before starting any task
- **CODE_TEMPLATES.md** - When implementing features
- **FAILSAFE_PROTOCOL.md** - When handling errors or emergencies

---

## 📍 Project Context

### What This Is
- **Production ERP System** for TSH company (Iraq)
- **Real business** with 500+ wholesale clients, 100+ partner salesmen
- **30 wholesale orders daily** + 30 retail transactions daily
- **Multi-million IQD** daily transaction volume
- **2,218+ active products** in inventory
- **8 Flutter mobile apps** + 3 web applications

### What This Is NOT
- ❌ A generic multi-tenant SaaS product
- ❌ An open-source demo or template
- ❌ A startup MVP or proof-of-concept
- ❌ A simple CRUD application

---

## 🔒 Non-Negotiable Rules

### Third-Party Services
- **NO TWILIO**: This project does NOT use the Twilio platform. Do not suggest, implement, or configure any Twilio-related features.

### Technology Stack (NEVER Change)
- **Backend**: Python 3.9+ with FastAPI (NO Django, NO Flask)
- **Database**: PostgreSQL 12+ (single source of truth)
- **Frontend Web**: React 18+ with TypeScript (ERP Admin)
- **Mobile**: Flutter 3.0+ (ALL 8 apps - NO hybrid WebView)
- **Hosting**: VPS (167.71.39.50) with Docker + Nginx

### Critical Operations
- **Zoho Integration**: Currently in parallel operation (phased migration)
- **TDS Core**: Controls ALL Zoho ↔ TSH ERP sync operations
- **Production Data**: Handle with extreme care - real business transactions

---

## 🎯 Session Start Routine

At the beginning of EVERY session:

1. **Announce**: "Reading TSH ERP project documentation..."
2. **Read**: The 4 files listed in Phase 1 above (in order)
3. **Confirm**: "Context loaded. TSH ERP Ecosystem ready. How can I help?"

Do NOT skip this routine. The comprehensive documentation contains:
- Business context you need to understand
- Technical constraints you must follow
- Patterns and templates to use
- Emergency procedures for production issues

---

## 📂 Project Location

**Working Directory**: `/Users/khaleelal-mulla/TSH_ERP_Ecosystem`

**Documentation Hub**: `/Users/khaleelal-mulla/TSH_ERP_Ecosystem/.claude/`
- 22 comprehensive markdown files (~490 KB)
- Custom agents (Orixoon, Zoho Sync Manager)
- Code templates, patterns, and protocols

---

## 💡 Quick Tips

- **Lost/Confused?** → Read QUICK_REFERENCE.md
- **Need code examples?** → Read CODE_TEMPLATES.md
- **Production issue?** → Read FAILSAFE_PROTOCOL.md
- **Starting a task?** → Read TASK_PATTERNS.md
- **Complex problem?** → Read REASONING_PATTERNS.md

---

## ✅ Verification

Before claiming you're ready to work, verify:
- [ ] Read KNOWLEDGE_PORTAL.md (navigation guide)
- [ ] Read AI_CONTEXT_RULES.md (meta-guide)
- [ ] Read PROJECT_VISION.md (business context)
- [ ] Read QUICK_REFERENCE.md (quick facts)
- [ ] Understand: This is a PRODUCTION system with real revenue
- [ ] Understand: 500+ clients depend on this system daily
- [ ] Understand: Tech stack is non-negotiable
- [ ] Understand: Currently in Zoho migration phase

---

**Remember**: Every decision you make affects a real business with real customers and real revenue. Read the documentation carefully, follow established patterns, and when in doubt - ask Khaleel.
