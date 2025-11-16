# Git Worktrees for Parallel Claude Code Sessions

**Version:** 1.0.0
**Created:** 2025-11-15
**Purpose:** Enable multiple Claude Code sessions to work in parallel using git worktrees

---

## 🎯 What Are Git Worktrees?

Git worktrees allow you to have **multiple working directories** for the same repository, each on a different branch. This enables:

- **Multiple Claude Code sessions** working on different features simultaneously
- **Parallel development** without branch switching conflicts
- **Independent testing** of different features at the same time
- **Faster context switching** between tasks

---

## 🚀 Quick Setup Guide

### Step 1: Check Current Worktrees

```bash
# See all existing worktrees
git worktree list

# Expected output:
# /Users/khaleelal-mulla/TSH_ERP_Ecosystem    f2c4788 [develop]
```

### Step 2: Create Worktrees for Parallel Sessions

```bash
# Navigate to your main project directory
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem

# Create worktrees for different agents/features
# Pattern: git worktree add <path> <branch-name>

# Example 1: Database Agent worktree
git worktree add ../TSH_ERP_Database database/schema-optimization

# Example 2: API Agent worktree
git worktree add ../TSH_ERP_API api/new-endpoints

# Example 3: Testing Agent worktree
git worktree add ../TSH_ERP_Testing testing/coverage-improvement

# Example 4: Performance Agent worktree
git worktree add ../TSH_ERP_Performance performance/query-optimization

# Example 5: Security Agent worktree
git worktree add ../TSH_ERP_Security security/vulnerability-scan
```

### Step 3: Verify Worktrees Created

```bash
git worktree list

# Expected output:
# /Users/khaleelal-mulla/TSH_ERP_Ecosystem                 f2c4788 [develop]
# /Users/khaleelal-mulla/TSH_ERP_Database                  abc1234 [database/schema-optimization]
# /Users/khaleelal-mulla/TSH_ERP_API                       def5678 [api/new-endpoints]
# /Users/khaleelal-mulla/TSH_ERP_Testing                   ghi9012 [testing/coverage-improvement]
# /Users/khaleelal-mulla/TSH_ERP_Performance               jkl3456 [performance/query-optimization]
# /Users/khaleelal-mulla/TSH_ERP_Security                  mno7890 [security/vulnerability-scan]
```

---

## 💻 Using Worktrees with Claude Code

### Open Multiple VS Code Windows

Each worktree gets its own VS Code window:

```bash
# Terminal 1: Database Agent
cd /Users/khaleelal-mulla/TSH_ERP_Database
code .

# Terminal 2: API Agent
cd /Users/khaleelal-mulla/TSH_ERP_API
code .

# Terminal 3: Testing Agent
cd /Users/khaleelal-mulla/TSH_ERP_Testing
code .

# Terminal 4: Performance Agent
cd /Users/khaleelal-mulla/TSH_ERP_Performance
code .

# Terminal 5: Security Agent
cd /Users/khaleelal-mulla/TSH_ERP_Security
code .
```

### Start Claude Code in Each Window

In each VS Code window:

1. Open integrated terminal (`` Ctrl+` `` or `` Cmd+` ``)
2. Start Claude Code: `claude`
3. Each session works independently on its own branch

---

## 📋 Recommended Worktree Structure

### Option 1: Agent-Based Worktrees

Create one worktree per agent type:

```bash
# Main repository (coordinator)
/Users/khaleelal-mulla/TSH_ERP_Ecosystem           [develop]

# Agent worktrees
/Users/khaleelal-mulla/TSH_ERP_Database           [database/*]
/Users/khaleelal-mulla/TSH_ERP_API                [api/*]
/Users/khaleelal-mulla/TSH_ERP_Testing            [testing/*]
/Users/khaleelal-mulla/TSH_ERP_Performance        [performance/*]
/Users/khaleelal-mulla/TSH_ERP_Security           [security/*]
/Users/khaleelal-mulla/TSH_ERP_BFF                [bff/*]
/Users/khaleelal-mulla/TSH_ERP_Flutter            [flutter/*]
/Users/khaleelal-mulla/TSH_ERP_TDS                [tds-core/*]
/Users/khaleelal-mulla/TSH_ERP_DevOps             [devops/*]
```

### Option 2: Feature-Based Worktrees

Create worktrees for specific features:

```bash
# Main repository
/Users/khaleelal-mulla/TSH_ERP_Ecosystem           [develop]

# Feature worktrees
/Users/khaleelal-mulla/TSH_ERP_OrderManagement    [feature/order-management]
/Users/khaleelal-mulla/TSH_ERP_InventorySync      [feature/inventory-sync]
/Users/khaleelal-mulla/TSH_ERP_MobileOptimization [feature/mobile-optimization]
/Users/khaleelal-mulla/TSH_ERP_ReportingDashboard [feature/reporting-dashboard]
```

### Option 3: Hybrid (Recommended for TSH ERP)

Combine both approaches:

```bash
# Main repository (coordination)
/Users/khaleelal-mulla/TSH_ERP_Ecosystem           [develop]

# Priority 1: Critical agents (always available)
/Users/khaleelal-mulla/TSH_ERP_Security           [security/*]
/Users/khaleelal-mulla/TSH_ERP_Testing            [testing/*]
/Users/khaleelal-mulla/TSH_ERP_Database           [database/*]

# Priority 2: Feature development (create as needed)
/Users/khaleelal-mulla/TSH_ERP_Feature1           [feature/product-catalog]
/Users/khaleelal-mulla/TSH_ERP_Feature2           [feature/order-processing]
```

---

## 🔧 Worktree Management Commands

### Create New Worktree

```bash
# Create from current branch
git worktree add ../TSH_ERP_NewFeature feature/new-feature

# Create from develop branch
git worktree add ../TSH_ERP_NewFeature -b feature/new-feature develop

# Create and checkout existing remote branch
git worktree add ../TSH_ERP_BugFix bugfix/critical-issue
```

### List All Worktrees

```bash
git worktree list

# Detailed output with commit info
git worktree list -v
```

### Remove Worktree (When Done)

```bash
# Step 1: Remove the directory
rm -rf /Users/khaleelal-mulla/TSH_ERP_Feature1

# Step 2: Prune worktree metadata
git worktree prune

# Or do both in one step:
git worktree remove /Users/khaleelal-mulla/TSH_ERP_Feature1
```

### Move Worktree

```bash
# Move worktree to new location
git worktree move /Users/khaleelal-mulla/TSH_ERP_Feature1 /Users/khaleelal-mulla/Projects/Feature1
```

### Lock Worktree (Prevent Deletion)

```bash
# Lock to prevent accidental deletion
git worktree lock /Users/khaleelal-mulla/TSH_ERP_Security

# Unlock
git worktree unlock /Users/khaleelal-mulla/TSH_ERP_Security
```

---

## 🎯 Parallel Session Workflows

### Workflow 1: Multi-Agent Coordinated Development

**Scenario:** Build a complete feature with 5 agents working in parallel

```bash
# User starts 5 Claude Code sessions simultaneously:

# Session 1: Database Agent
cd /Users/khaleelal-mulla/TSH_ERP_Database
git worktree add . -b database/product-catalog-schema develop
claude
# Task: Design database schema for product catalog

# Session 2: API Agent
cd /Users/khaleelal-mulla/TSH_ERP_API
git worktree add . -b api/product-catalog-endpoints develop
claude
# Task: Create FastAPI endpoints for product catalog

# Session 3: Security Agent
cd /Users/khaleelal-mulla/TSH_ERP_Security
git worktree add . -b security/product-catalog-auth develop
claude
# Task: Add RBAC/ABAC/RLS to product catalog

# Session 4: Testing Agent
cd /Users/khaleelal-mulla/TSH_ERP_Testing
git worktree add . -b testing/product-catalog-tests develop
claude
# Task: Write comprehensive tests for product catalog

# Session 5: Flutter Agent
cd /Users/khaleelal-mulla/TSH_ERP_Flutter
git worktree add . -b flutter/product-catalog-ui develop
claude
# Task: Build product catalog UI in consumer app

# Each agent works independently, commits to own branch, pushes to GitHub
# DevOps Agent coordinates final merge to develop
```

### Workflow 2: Hotfix While Feature Development Continues

```bash
# Feature development in progress
# Worktree: /Users/khaleelal-mulla/TSH_ERP_Feature [feature/new-dashboard]

# Critical bug discovered in production!
# Create hotfix worktree from main:
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem
git worktree add ../TSH_ERP_Hotfix -b hotfix/critical-security-fix main

# Start Claude in hotfix worktree
cd /Users/khaleelal-mulla/TSH_ERP_Hotfix
claude
# Fix the critical bug, test, deploy

# Meanwhile, feature development continues uninterrupted in other worktree
```

### Workflow 3: Testing Multiple Solutions

```bash
# Try 3 different approaches to solve a performance problem

# Approach 1: Caching
git worktree add ../TSH_ERP_Perf_Cache -b perf/redis-caching develop
cd /Users/khaleelal-mulla/TSH_ERP_Perf_Cache
claude
# Implement Redis caching solution

# Approach 2: Database indexing
git worktree add ../TSH_ERP_Perf_Index -b perf/database-indexes develop
cd /Users/khaleelal-mulla/TSH_ERP_Perf_Index
claude
# Add database indexes

# Approach 3: Query optimization
git worktree add ../TSH_ERP_Perf_Query -b perf/query-optimization develop
cd /Users/khaleelal-mulla/TSH_ERP_Perf_Query
claude
# Optimize queries

# Benchmark all 3 approaches, keep the best one
```

---

## ⚙️ Configuration & Best Practices

### 1. Shared Git Configuration

All worktrees share the same `.git` directory, so:

✅ **Shared:**
- Git configuration (.gitconfig)
- Branches
- Commits
- Tags
- Remotes
- Hooks

❌ **Not Shared:**
- Working directory files
- Uncommitted changes
- Current branch checkout
- Local modifications

### 2. Environment Variables

Each worktree should have its own `.env` file:

```bash
# In each worktree, copy from template:
cp .env.template .env

# Or create symbolic links to shared config:
ln -s /Users/khaleelal-mulla/TSH_ERP_Ecosystem/.env.shared .env
```

### 3. Node Modules & Dependencies

**Option A: Separate dependencies per worktree (safer)**
```bash
# Each worktree has own node_modules/
cd /Users/khaleelal-mulla/TSH_ERP_API
npm install
```

**Option B: Shared dependencies (faster, use carefully)**
```bash
# Symbolic link to main node_modules
cd /Users/khaleelal-mulla/TSH_ERP_API
ln -s /Users/khaleelal-mulla/TSH_ERP_Ecosystem/node_modules node_modules
```

### 4. Database Connections

Use different database names per worktree to avoid conflicts:

```bash
# Main worktree
DATABASE_URL=postgresql://user:pass@localhost/tsh_erp_dev

# Database Agent worktree
DATABASE_URL=postgresql://user:pass@localhost/tsh_erp_database_agent

# API Agent worktree
DATABASE_URL=postgresql://user:pass@localhost/tsh_erp_api_agent
```

### 5. Port Assignments

Assign different ports to avoid conflicts:

```bash
# Main worktree: Port 8000
PORT=8000

# Database Agent worktree: Port 8001
PORT=8001

# API Agent worktree: Port 8002
PORT=8002

# Testing Agent worktree: Port 8003
PORT=8003
```

---

## 🚨 Common Issues & Solutions

### Issue 1: Branch Already Checked Out

**Error:**
```
fatal: 'feature/new-feature' is already checked out at '/Users/khaleelal-mulla/TSH_ERP_Ecosystem'
```

**Solution:**
You cannot checkout the same branch in multiple worktrees. Create a new branch:

```bash
git worktree add ../TSH_ERP_NewWorktree -b feature/new-feature-v2 feature/new-feature
```

### Issue 2: Worktree Directory Not Empty

**Error:**
```
fatal: '/Users/khaleelal-mulla/TSH_ERP_NewWorktree' already exists
```

**Solution:**
```bash
# Remove directory first
rm -rf /Users/khaleelal-mulla/TSH_ERP_NewWorktree

# Then create worktree
git worktree add ../TSH_ERP_NewWorktree feature/new-feature
```

### Issue 3: Stale Worktree Metadata

**Error:**
```
fatal: '/Users/khaleelal-mulla/TSH_ERP_OldWorktree' is a missing but locked worktree
```

**Solution:**
```bash
# Unlock and remove stale worktree
git worktree unlock /Users/khaleelal-mulla/TSH_ERP_OldWorktree
git worktree remove /Users/khaleelal-mulla/TSH_ERP_OldWorktree --force

# Or prune all stale worktrees
git worktree prune
```

### Issue 4: Disk Space Concerns

Each worktree is a full working directory. For TSH ERP (~7GB mobile apps):

**Solution:**
```bash
# Exclude large directories from worktrees
# Add to .git/info/sparse-checkout

# Only check out specific directories
git worktree add ../TSH_ERP_API -b api/new-endpoints develop
cd ../TSH_ERP_API
git sparse-checkout init --cone
git sparse-checkout set app/routers app/schemas app/services
```

---

## 📊 Recommended Setup for TSH ERP

### Phase 1: Create Core Agent Worktrees

```bash
# Navigate to main repository
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem

# Create worktrees for critical agents
git worktree add ../TSH_ERP_Security -b security/ongoing develop
git worktree add ../TSH_ERP_Testing -b testing/ongoing develop
git worktree add ../TSH_ERP_Database -b database/ongoing develop
git worktree add ../TSH_ERP_Performance -b performance/ongoing develop

# Lock these worktrees (keep them permanent)
git worktree lock ../TSH_ERP_Security
git worktree lock ../TSH_ERP_Testing
git worktree lock ../TSH_ERP_Database
git worktree lock ../TSH_ERP_Performance
```

### Phase 2: Open Multiple Claude Sessions

```bash
# Terminal/Tab 1: Main Coordinator
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem
code .
# Claude session 1: Master Coordinator

# Terminal/Tab 2: Security Agent
cd /Users/khaleelal-mulla/TSH_ERP_Security
code .
# Claude session 2: Security specialist

# Terminal/Tab 3: Testing Agent
cd /Users/khaleelal-mulla/TSH_ERP_Testing
code .
# Claude session 3: Testing specialist

# Terminal/Tab 4: Database Agent
cd /Users/khaleelal-mulla/TSH_ERP_Database
code .
# Claude session 4: Database specialist

# Terminal/Tab 5: Performance Agent
cd /Users/khaleelal-mulla/TSH_ERP_Performance
code .
# Claude session 5: Performance specialist
```

### Phase 3: Coordinate Workflow

**Master Coordinator (Main Worktree):**
- Receives user requirements
- Routes tasks to specialist agents
- Reviews and merges completed work
- Coordinates deployment

**Specialist Agents (Dedicated Worktrees):**
- Receive specific tasks from coordinator
- Work independently on own branches
- Commit and push to GitHub
- Report completion to coordinator

---

## 🎯 Example: Parallel Feature Development

### Task: Build Complete Order Management System

**User Request:**
"Build a complete order management system with database, API, security, tests, and mobile UI - all in parallel"

**Execution:**

```bash
# Coordinator creates 5 worktrees
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem

git worktree add ../TSH_ERP_Orders_DB -b feature/orders-database develop
git worktree add ../TSH_ERP_Orders_API -b feature/orders-api develop
git worktree add ../TSH_ERP_Orders_Security -b feature/orders-security develop
git worktree add ../TSH_ERP_Orders_Testing -b feature/orders-testing develop
git worktree add ../TSH_ERP_Orders_Mobile -b feature/orders-mobile develop

# Start 5 Claude sessions in parallel:

# Session 1: Database Agent (Port 8001)
cd /Users/khaleelal-mulla/TSH_ERP_Orders_DB
# Task: Create orders, order_items, order_payments tables

# Session 2: API Agent (Port 8002)
cd /Users/khaleelal-mulla/TSH_ERP_Orders_API
# Task: Build /api/orders endpoints with Pydantic validation

# Session 3: Security Agent (Port 8003)
cd /Users/khaleelal-mulla/TSH_ERP_Orders_Security
# Task: Implement RBAC + ABAC + RLS for orders

# Session 4: Testing Agent (Port 8004)
cd /Users/khaleelal-mulla/TSH_ERP_Orders_Testing
# Task: Write unit + integration tests for orders

# Session 5: Flutter Agent (Port 8005)
cd /Users/khaleelal-mulla/TSH_ERP_Orders_Mobile
# Task: Build order management UI in mobile apps

# All 5 agents work simultaneously, commit to own branches
# When all complete, merge all 5 branches to develop in sequence:

cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem
git checkout develop
git merge feature/orders-database
git merge feature/orders-api
git merge feature/orders-security
git merge feature/orders-testing
git merge feature/orders-mobile
git push origin develop

# Clean up worktrees
git worktree remove ../TSH_ERP_Orders_DB
git worktree remove ../TSH_ERP_Orders_API
git worktree remove ../TSH_ERP_Orders_Security
git worktree remove ../TSH_ERP_Orders_Testing
git worktree remove ../TSH_ERP_Orders_Mobile
```

**Time Saved:**
- Sequential development: ~10 days
- Parallel with worktrees: ~2 days
- **80% time reduction!**

---

## 📋 Worktree Naming Convention

**Recommended Pattern:**
```
TSH_ERP_<Agent>_<Feature>

Examples:
TSH_ERP_Database_ProductCatalog
TSH_ERP_API_OrderManagement
TSH_ERP_Security_MFAImplementation
TSH_ERP_Testing_E2ECoverage
TSH_ERP_Flutter_ConsumerApp
```

**Branch Naming Convention:**
```
<type>/<agent>-<description>

Examples:
feature/database-product-catalog
feature/api-order-management
security/mfa-implementation
testing/e2e-coverage
flutter/consumer-app-optimization
```

---

## 🔍 Monitoring Multiple Sessions

### Using tmux for Session Management

```bash
# Install tmux (if not already installed)
brew install tmux

# Start tmux session
tmux new -s tsh-erp-parallel

# Split into 5 panes (Ctrl+b %)
# Navigate between panes (Ctrl+b arrow keys)

# Pane 1: Main Coordinator
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem && claude

# Pane 2: Database Agent
cd /Users/khaleelal-mulla/TSH_ERP_Database && claude

# Pane 3: API Agent
cd /Users/khaleelal-mulla/TSH_ERP_API && claude

# Pane 4: Security Agent
cd /Users/khaleelal-mulla/TSH_ERP_Security && claude

# Pane 5: Testing Agent
cd /Users/khaleelal-mulla/TSH_ERP_Testing && claude

# Detach from session: Ctrl+b d
# Reattach later: tmux attach -t tsh-erp-parallel
```

---

## ✅ Quick Start Checklist

Ready to enable parallel Claude Code sessions?

- [ ] Understand git worktrees concept
- [ ] Plan worktree structure (agent-based or feature-based)
- [ ] Create first worktree: `git worktree add ../TSH_ERP_Test -b test/feature develop`
- [ ] Open worktree in new VS Code window: `code ../TSH_ERP_Test`
- [ ] Start Claude in worktree: `claude`
- [ ] Configure environment (ports, database, env vars)
- [ ] Test workflow with 2-3 parallel sessions
- [ ] Scale up to 5+ parallel sessions
- [ ] Document your worktree setup
- [ ] Train team on parallel workflows

---

## 🚀 Automation Script

Create a helper script to quickly set up worktrees:

```bash
#!/bin/bash
# File: scripts/create-worktree.sh

AGENT=$1
FEATURE=$2
BASE_BRANCH=${3:-develop}

if [ -z "$AGENT" ] || [ -z "$FEATURE" ]; then
    echo "Usage: ./create-worktree.sh <agent> <feature> [base-branch]"
    echo "Example: ./create-worktree.sh database product-catalog develop"
    exit 1
fi

WORKTREE_PATH="../TSH_ERP_${AGENT^}_${FEATURE^}"
BRANCH_NAME="${AGENT}/${FEATURE}"

echo "Creating worktree:"
echo "  Path: $WORKTREE_PATH"
echo "  Branch: $BRANCH_NAME"
echo "  Base: $BASE_BRANCH"

git worktree add "$WORKTREE_PATH" -b "$BRANCH_NAME" "$BASE_BRANCH"

cd "$WORKTREE_PATH"
echo "✅ Worktree created successfully!"
echo "Next steps:"
echo "  1. cd $WORKTREE_PATH"
echo "  2. code ."
echo "  3. Start Claude Code session"
```

Usage:
```bash
chmod +x scripts/create-worktree.sh
./scripts/create-worktree.sh database product-catalog develop
./scripts/create-worktree.sh api order-management develop
./scripts/create-worktree.sh security mfa-implementation develop
```

---

**Last Updated:** 2025-11-15
**Version:** 1.0.0
**Status:** Ready to Use

**Next Step:** Try creating your first worktree and running parallel Claude Code sessions!
