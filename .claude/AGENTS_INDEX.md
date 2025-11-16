# TSH ERP Agents Index

**Last Updated:** 2025-01-15
**Purpose:** Quick reference to all specialized agents

---

## Specialized Engineering Agents (9 Total)

### 1. **Architect Agent**
- **File:** `.claude/agents/architect/agent.md`
- **Domain:** System architecture, design patterns, database schemas
- **Use When:** Designing systems, reviewing architecture, making technical decisions

### 2. **TDS Core Agent**
- **File:** `.claude/agents/tds_core/agent.md`
- **Domain:** Zoho Books/Inventory sync, TDS Core operations
- **Use When:** Zoho integration issues, sync problems, webhook handling

### 3. **BFF Agent**
- **File:** `.claude/agents/bff/agent.md`
- **Domain:** Backend-for-Frontend layer, mobile API endpoints
- **Use When:** Creating mobile-optimized APIs, implementing DTOs

### 4. **Flutter Agent**
- **File:** `.claude/agents/flutter/agent.md`
- **Domain:** Flutter mobile apps, Dart code, mobile UI/UX
- **Use When:** Building/fixing mobile apps, implementing Arabic RTL

### 5. **DevOps Agent**
- **File:** `.claude/agents/devops/agent.md`
- **Domain:** Deployment, CI/CD, Docker, infrastructure
- **Use When:** Deploying, fixing GitHub Actions, managing infrastructure

### 6. **Security Agent**
- **File:** `.claude/agents/security/agent.md`
- **Domain:** Authentication, authorization, data security
- **Use When:** Implementing auth, securing endpoints, adding permissions

### 7. **Docs Agent**
- **File:** `.claude/agents/docs/agent.md`
- **Domain:** Documentation management, knowledge capture
- **Use When:** Writing/updating documentation, organizing knowledge

### 8. **Orixoon** (Pre-Deployment Testing)
- **File:** `.claude/agents/orixoon/agent.md`
- **Domain:** Pre-deployment testing, quality assurance
- **Use When:** Validating deployments, running comprehensive tests

### 9. **Zoho Sync Manager** (Monitoring & Auto-Healing)
- **File:** `.claude/agents/zoho-sync-manager/agent.md`
- **Domain:** Zoho sync health monitoring, auto-healing
- **Use When:** Checking sync status, healing failed syncs

---

## How to Use Agents

### Automatic Routing (Recommended)
Simply describe your task naturally. The system will automatically route to the correct agent.

**Example:**
```
User: "Design a database schema for inventory tracking"
System: Routes to → architect_agent
```

### Manual Agent Selection (If Needed)
Read the agent's definition file directly and provide task context.

---

## Agent Routing Keywords

```yaml
Architecture:
  - architecture, design pattern, schema, API design, scalability

TDS Core:
  - Zoho, sync, TDS, webhook, price list, queue

BFF:
  - BFF, mobile endpoint, DTO, mobile API, /api/bff/mobile

Flutter:
  - Flutter, Dart, mobile app, consumer app, Arabic RTL, widget

DevOps:
  - deploy, Docker, CI/CD, GitHub Actions, Nginx, SSL, production

Security:
  - authentication, authorization, JWT, RBAC, permissions, encryption

Docs:
  - documentation, docs, README, guide, .claude/

Orixoon:
  - pre-deployment, test before deploy, validation

Zoho Sync Manager:
  - sync health, sync status, heal sync, queue stuck
```

---

## Quick Commands

```bash
# View agent definition
cat .claude/agents/{agent}/agent.md

# List all agents
ls -la .claude/agents/

# View routing system
cat .claude/AGENT_ROUTING_SYSTEM.md
```

---

## Agent Collaboration

Agents can collaborate on complex tasks:

**Example:** "Implement a new feature with full deployment"

1. **architect_agent** → Designs architecture
2. **bff_agent** → Implements API
3. **flutter_agent** → Builds mobile UI
4. **security_agent** → Adds authentication
5. **orixoon** → Runs tests
6. **devops_agent** → Deploys
7. **docs_agent** → Documents feature

---

**See AGENT_ROUTING_SYSTEM.md for complete details on automatic routing.**
