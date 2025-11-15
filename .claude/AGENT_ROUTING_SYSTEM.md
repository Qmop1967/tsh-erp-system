# Agent Routing System - Master Coordinator

**Last Updated:** 2025-01-15
**Purpose:** Automatic task routing to specialized engineering agents

---

## System Overview

The TSH ERP Ecosystem uses a **multi-agent architecture** where Claude Code acts as the **Master Coordinator**, automatically routing tasks to specialized agents based on task domain.

**Master Coordinator Role:**
- Receives tasks from user
- Analyzes task domain
- Routes to appropriate specialist agent
- Collects agent output
- Returns unified response to user

**User Experience:**
- User gives task in natural language
- System automatically selects correct agent
- Task executed by domain specialist
- Result returned seamlessly

---

## Available Agents

### 1. Architect Agent
**Location:** `.claude/agents/architect/agent.md`

**Domain:** System architecture, design patterns, technical strategy

**Trigger Keywords:**
```yaml
- "architecture"
- "design pattern"
- "schema design"
- "database design"
- "API design"
- "system design"
- "scalability"
- "architectural decision"
- "tech stack"
- "integration pattern"
```

**Example Tasks:**
- "Design the database schema for inventory tracking"
- "Review this API endpoint architecture"
- "What's the best pattern for handling product variants?"
- "Make an architectural decision about caching strategy"

---

### 2. TDS Core Agent
**Location:** `.claude/agents/tds_core/agent.md`

**Domain:** Zoho Books/Inventory sync, TDS Core operations

**Trigger Keywords:**
```yaml
- "Zoho"
- "sync"
- "TDS"
- "webhook"
- "Zoho Books"
- "Zoho Inventory"
- "price list sync"
- "product sync"
- "queue"
- "sync failed"
- "Zoho API"
```

**Example Tasks:**
- "Fix Zoho product sync issue"
- "Check TDS sync queue status"
- "Implement new Zoho webhook handler"
- "Why are prices not syncing from Zoho?"
- "Add support for credit notes sync"

---

### 3. BFF Agent
**Location:** `.claude/agents/bff/agent.md`

**Domain:** Backend-for-Frontend layer, mobile API endpoints

**Trigger Keywords:**
```yaml
- "BFF"
- "mobile endpoint"
- "mobile API"
- "DTO"
- "consumer app endpoint"
- "wholesale app API"
- "salesperson endpoint"
- "mobile-optimized"
- "/api/bff/mobile"
```

**Example Tasks:**
- "Create BFF endpoint for consumer product list"
- "Optimize mobile API response for wholesale app"
- "Implement DTOs for salesperson app"
- "Add pagination to partner app product endpoint"
- "Design mobile-friendly error responses"

---

### 4. Flutter Agent
**Location:** `.claude/agents/flutter/agent.md`

**Domain:** Flutter mobile apps, Dart code, mobile UI/UX

**Trigger Keywords:**
```yaml
- "Flutter"
- "Dart"
- "mobile app"
- "consumer app"
- "wholesale app"
- "salesperson app"
- "Arabic RTL"
- "mobile UI"
- "widget"
- "state management"
```

**Example Tasks:**
- "Add product detail screen to consumer app"
- "Implement Arabic RTL support in Flutter"
- "Fix cart screen in consumer app"
- "Create order history page for wholesale app"
- "Optimize Flutter image loading"

---

### 5. DevOps Agent
**Location:** `.claude/agents/devops/agent.md`

**Domain:** Deployment, CI/CD, Docker, infrastructure

**Trigger Keywords:**
```yaml
- "deploy"
- "deployment"
- "Docker"
- "CI/CD"
- "GitHub Actions"
- "Nginx"
- "SSL"
- "infrastructure"
- "server"
- "production"
- "staging"
```

**Example Tasks:**
- "Deploy to production"
- "Fix GitHub Actions workflow"
- "Configure Nginx for new domain"
- "Set up SSL certificate"
- "Create Docker Compose for new service"
- "Rollback last deployment"

---

### 6. Security Agent
**Location:** `.claude/agents/security/agent.md`

**Domain:** Authentication, authorization, data security

**Trigger Keywords:**
```yaml
- "authentication"
- "authorization"
- "JWT"
- "RBAC"
- "ABAC"
- "permissions"
- "security"
- "access control"
- "encryption"
- "audit log"
```

**Example Tasks:**
- "Implement JWT authentication for new endpoint"
- "Add role-based authorization"
- "Review security of payment endpoint"
- "Encrypt sensitive customer data"
- "Add audit logging for order deletion"

---

### 7. Docs Agent
**Location:** `.claude/agents/docs/agent.md`

**Domain:** Documentation management, knowledge capture

**Trigger Keywords:**
```yaml
- "documentation"
- "document this"
- "update docs"
- "create guide"
- "README"
- "wiki"
- "knowledge"
- ".claude/"
- "troubleshooting guide"
```

**Example Tasks:**
- "Update PROJECT_VISION.md with new product count"
- "Create troubleshooting guide for sync issues"
- "Document the new BFF pattern"
- "Add this decision to DECISIONS.md"
- "Reorganize .claude/ documentation"

---

### 8. Orixoon (Pre-Deployment Testing)
**Location:** `.claude/agents/orixoon/agent.md`

**Domain:** Pre-deployment testing, quality assurance

**Trigger Keywords:**
```yaml
- "test before deploy"
- "pre-deployment"
- "Orixoon"
- "run tests"
- "validate deployment"
- "health check"
```

**Example Tasks:**
- "Run pre-deployment tests"
- "Validate production readiness"
- "Check all health endpoints"

---

### 9. Zoho Sync Manager (Monitoring & Auto-Healing)
**Location:** `.claude/agents/zoho-sync-manager/agent.md`

**Domain:** Zoho sync monitoring, auto-healing

**Trigger Keywords:**
```yaml
- "sync health"
- "sync status"
- "heal sync"
- "queue stuck"
- "sync monitoring"
```

**Example Tasks:**
- "Check Zoho sync health"
- "Auto-heal failed sync items"
- "Generate sync status report"

---

## Routing Decision Matrix

```yaml
Task Analysis Steps:
  1. Extract keywords from task
  2. Match keywords to agent domains
  3. Calculate confidence score
  4. Select agent with highest confidence
  5. Load agent context
  6. Execute task
  7. Return result

Confidence Threshold: 70%

If multiple agents match:
  - Choose agent with highest confidence
  - If tie, choose in priority order:
    1. architect_agent (broad scope)
    2. Domain-specific agents
    3. docs_agent (fallback for documentation)

If no agent matches (< 70% confidence):
  - Handle task directly as senior engineer
  - Do NOT route to agent
```

---

## Routing Algorithm (Pseudo-code)

```python
def route_task(task: str) -> str:
    """
    Automatically route task to appropriate agent.

    Args:
        task: User's task description

    Returns:
        Agent identifier (e.g., "architect_agent")
    """

    # Extract keywords
    keywords = extract_keywords(task.lower())

    # Calculate confidence for each agent
    scores = {}

    for agent_name, agent_keywords in AGENT_KEYWORDS.items():
        match_count = len(set(keywords) & set(agent_keywords))
        confidence = (match_count / len(agent_keywords)) * 100
        scores[agent_name] = confidence

    # Find best match
    best_agent = max(scores, key=scores.get)
    best_score = scores[best_agent]

    if best_score >= 70:
        return best_agent
    else:
        return None  # Handle directly, don't route
```

---

## Agent Loading Protocol

When routing to an agent:

```python
1. Read agent definition file (.claude/agents/{agent}/agent.md)
2. Load agent context and responsibilities
3. Provide task to agent
4. Agent executes using its specialized knowledge
5. Agent returns result
6. Master coordinator formats response for user
```

---

## Example Routing Scenarios

### Scenario 1: Architecture Task
```
User: "Design a database schema for tracking product variants"

Analysis:
  Keywords: ["design", "database", "schema"]
  Match: architect_agent (95% confidence)

Routing:
  → architect_agent

Agent Action:
  - Reviews current database patterns
  - Designs variant schema
  - Ensures bilingual fields
  - Creates migration plan
  - Returns schema design

Result:
  Detailed schema with migration script
```

### Scenario 2: Zoho Sync Issue
```
User: "Prices aren't syncing from Zoho Inventory"

Analysis:
  Keywords: ["prices", "syncing", "Zoho Inventory"]
  Match: tds_core_agent (100% confidence)

Routing:
  → tds_core_agent

Agent Action:
  - Checks TDS sync queue
  - Verifies price list sync status
  - Checks Zoho API connectivity
  - Diagnoses root cause
  - Provides fix

Result:
  Diagnosis and fix steps
```

### Scenario 3: Mobile App Feature
```
User: "Add product filtering to consumer app"

Analysis:
  Keywords: ["consumer app", "product", "filtering"]
  Matches:
    - flutter_agent (85% - mobile app implementation)
    - bff_agent (70% - might need API endpoint)

Routing:
  → flutter_agent (higher confidence)

Agent Action:
  - Designs Flutter UI for filters
  - Implements filter chips
  - Adds filter state management
  - Integrates with BFF API
  - Returns implementation

Result:
  Flutter code with filtering UI
```

### Scenario 4: Deployment
```
User: "Deploy the latest changes to production"

Analysis:
  Keywords: ["deploy", "production"]
  Match: devops_agent (100% confidence)

Routing:
  → devops_agent

Agent Action:
  - Verifies all components ready
  - Runs pre-deployment checks
  - Executes blue-green deployment
  - Runs health checks
  - Monitors deployment

Result:
  Deployment complete with verification
```

### Scenario 5: Multi-Agent Collaboration
```
User: "Implement a new BFF endpoint for salesperson GPS tracking and deploy it"

Analysis:
  Keywords: ["BFF endpoint", "salesperson", "GPS", "deploy"]
  Matches:
    - bff_agent (90% - BFF endpoint implementation)
    - devops_agent (80% - deployment)

Routing:
  → bff_agent (primary)
  → devops_agent (secondary, after BFF done)

Agent Actions:
  1. bff_agent:
     - Creates GPS tracking endpoint
     - Implements DTO
     - Tests endpoint

  2. devops_agent:
     - Deploys new endpoint
     - Verifies health

Result:
  Feature implemented and deployed
```

---

## Agent Coordination

### Sequential Execution
When task requires multiple agents in sequence:

```yaml
Example: "Design and implement product variant schema"

Step 1: architect_agent
  - Design schema

Step 2: devops_agent
  - Create migration script
  - Deploy migration

Step 3: docs_agent
  - Document new schema
```

### Parallel Execution
When task has independent sub-tasks:

```yaml
Example: "Prepare for production deployment"

Parallel:
  - orixoon: Run pre-deployment tests
  - zoho-sync-manager: Verify sync health
  - devops_agent: Prepare deployment artifacts

Then:
  - devops_agent: Execute deployment
```

---

## User Communication

### Routing Transparency
```markdown
Master Coordinator Response Format:

🎯 Task Analysis:
  Routing to: [agent_name]
  Reason: [why this agent]

📋 [Agent Name] is working on your request...

[Agent output]

✅ Task Complete
```

### Example Response
```markdown
🎯 Task Analysis:
  Routing to: BFF Agent
  Reason: Mobile API endpoint implementation

📋 BFF Agent is working on your request...

[BFF Agent creates endpoint, provides code]

✅ Task Complete

The salesperson GPS tracking endpoint has been implemented at:
POST /api/bff/mobile/salesperson/location

Ready to deploy when you are.
```

---

## Fallback Behavior

If no agent matches:
```markdown
🤔 No specialized agent matches this task.

I'll handle this directly as a senior software engineer.

[Proceed with task using general capabilities]
```

---

## Success Metrics

```yaml
Routing Accuracy: > 95%
  - Correct agent selected
  - Task completed successfully

Agent Utilization:
  - All agents used regularly
  - No unused agents

User Satisfaction:
  - Seamless experience
  - No manual agent selection needed
  - Fast task completion
```

---

## Maintenance

### Monthly Review
- Analyze routing patterns
- Update keyword lists
- Adjust confidence thresholds
- Add new agents if needed

### Agent Updates
When agent changes:
- Update agent definition file
- Update routing keywords
- Test routing with sample tasks
- Update this documentation

---

**The routing system is now ACTIVE. All tasks will be automatically routed to the appropriate specialist agent.**

---

## Quick Reference

```yaml
Architecture & Design → architect_agent
Zoho Sync & TDS → tds_core_agent
Mobile APIs → bff_agent
Flutter Apps → flutter_agent
Deployment & CI/CD → devops_agent
Security & Auth → security_agent
Documentation → docs_agent
Pre-Deployment Tests → orixoon
Sync Monitoring → zoho-sync-manager
```

---

**END OF AGENT ROUTING SYSTEM**

*Automatic task routing for maximum efficiency*
