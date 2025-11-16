# Claude Code Configuration Scripts

**Automation utilities for TSH ERP Ecosystem Claude Code configuration**

---

## 📁 Available Scripts

### 1. `update-state.sh` - State File Updater

Automatically updates `.claude/state/current-phase.json` with latest system metrics.

#### **Features:**
- ✅ Updates timestamps
- ✅ Fetches database metrics (products, customers, DB size)
- ✅ Checks TDS Core health
- ✅ Checks production/staging health
- ✅ Creates automatic backups
- ✅ Adds entries to change log
- ✅ Dry-run mode for testing

#### **Usage:**

```bash
# Normal update
./claude/scripts/update-state.sh

# Dry run (preview changes without applying)
./claude/scripts/update-state.sh --dry-run

# Force update (skip confirmations)
./claude/scripts/update-state.sh --force

# Help
./claude/scripts/update-state.sh --help
```

#### **Requirements:**
- `psql` (for database metrics)
- `curl` (for health checks)
- Database credentials in `.env` file

#### **What it updates:**
- `last_updated` timestamp
- `integration_status.*.status` fields
- `deployment_status.environments.*.status` fields
- `scale_metrics.active_products` (from database)
- Verification timestamps in `phase_success_criteria`
- Adds automatic entry to `change_log`

#### **Example Output:**

```
ℹ Starting state update process...
✓ Created backup: .claude/state/backups/current-phase_20251114_143000.json
ℹ Gathering system metrics...
✓ Database connection successful
✓ Products: 2218
✓ Customers: 500
✓ Database Size: 127 MB
✓ TDS Core is operational
✓ Production is active
✓ Staging is active
ℹ Updating state file...
✓ State file updated: .claude/state/current-phase.json

ℹ Update Summary:
  📅 Timestamp: 2025-11-14T14:30:00Z
  🔄 TDS Core: operational
  🌐 Production: active
  🧪 Staging: active
  📦 Products: 2218
  👥 Customers: 500

✓ State update complete!
```

---

### 2. `validate-state.sh` - State File Validator

Validates `.claude/state/current-phase.json` structure and content.

#### **Features:**
- ✅ JSON syntax validation
- ✅ Required fields check
- ✅ Data type validation
- ✅ Data consistency checks
- ✅ Verbose mode for detailed info

#### **Usage:**

```bash
# Normal validation
./claude/scripts/validate-state.sh

# Verbose mode (show detailed info)
./claude/scripts/validate-state.sh --verbose

# Short verbose flag
./claude/scripts/validate-state.sh -v

# Help
./claude/scripts/validate-state.sh --help
```

#### **Validation Checks:**

1. **JSON Syntax** - Ensures file is valid JSON
2. **Required Fields** - Checks all mandatory fields exist
3. **Data Types** - Validates field types (boolean, number, array, etc.)
4. **Data Consistency** - Checks logical consistency between fields

#### **Example Output:**

```
ℹ Validating state file: .claude/state/current-phase.json

ℹ Checking JSON syntax...
✓ JSON syntax is valid
ℹ Checking required fields...
✓ All required fields present
ℹ Checking data types and values...
✓ All data types are correct
ℹ Checking data consistency...
✓ Data is consistent

ℹ Validation Summary:
  📋 Total Checks: 4
  ✓ Passed: 4

✓ State file validation PASSED!
```

#### **Exit Codes:**
- `0` - Validation passed
- `1` - Validation failed

---

### 3. `bump-version.sh` - Version Manager

Manages semantic versioning across Claude Code configuration files.

#### **Features:**
- ✅ Semantic versioning (major.minor.patch)
- ✅ Updates CLAUDE.md version header
- ✅ Updates version history
- ✅ Updates state file timestamps
- ✅ Updates MCP configuration
- ✅ Adds entries to all change logs

#### **Usage:**

```bash
# Patch version (bug fixes)
./claude/scripts/bump-version.sh patch "Fixed typo in documentation"

# Minor version (new features)
./claude/scripts/bump-version.sh minor "Added state analytics feature"

# Major version (breaking changes)
./claude/scripts/bump-version.sh major "Complete configuration restructure"
```

#### **Semantic Versioning:**

- **Major (X.0.0)** - Breaking changes, major restructures
- **Minor (x.Y.0)** - New features, backward compatible
- **Patch (x.y.Z)** - Bug fixes, minor improvements

#### **What it updates:**

1. **`.claude/CLAUDE.md`**:
   - Version header (`**Version:** X.Y.Z`)
   - Last updated date
   - Version history section

2. **`.claude/state/current-phase.json`**:
   - `last_updated` timestamp
   - Adds entry to `change_log`

3. **`.claude/.mcp.json`**:
   - `last_updated` date
   - Adds entry to `change_log` (if MCP-related)

#### **Example Output:**

```
ℹ Starting version bump: minor
Current version: 3.0.0
✓ New version: 3.1.0

ℹ Updating CLAUDE.md...
✓ Updated CLAUDE.md
ℹ Updating state file...
✓ Updated state file
ℹ Updating MCP configuration...
✓ Updated MCP configuration

ℹ Version Bump Summary:
  📌 Old Version: 3.0.0
  📌 New Version: 3.1.0
  📝 Change: Added state analytics feature
  📅 Date: 2025-11-14

  Files Updated:
    ✓ .claude/CLAUDE.md
    ✓ .claude/state/current-phase.json
    ✓ .claude/.mcp.json

✓ Version bump complete!
ℹ Don't forget to commit these changes:

  git add .claude/CLAUDE.md .claude/state/current-phase.json .claude/.mcp.json
  git commit -m "chore: bump version to 3.1.0"
```

---

### 4. `mcp-analytics.py` - MCP Usage Analytics

Tracks and analyzes MCP server usage patterns for optimization.

#### **Features:**
- ✅ Usage frequency tracking
- ✅ Token usage analysis
- ✅ Task type distribution
- ✅ Optimization recommendations
- ✅ Session logging
- ✅ Historical data (last 100 sessions)

#### **Usage:**

```bash
# Generate full report
python3 .claude/scripts/mcp-analytics.py --report

# Show optimization recommendations
python3 .claude/scripts/mcp-analytics.py --optimize

# Both report and recommendations (default)
python3 .claude/scripts/mcp-analytics.py

# Log a session
python3 .claude/scripts/mcp-analytics.py --log-session "playwright,chrome-devtools" "testing" 45000
```

#### **Log Session Format:**

```bash
--log-session "mcp1,mcp2,mcp3" "task_type" token_count

# Examples:
--log-session "zoho" "sync" 15000
--log-session "playwright,chrome-devtools" "e2e_test" 50000
--log-session "" "development" 8000  # No MCPs used
```

#### **Report Sections:**

1. **Overview**
   - Total sessions
   - Total token usage
   - Average tokens per session

2. **MCP Usage Frequency**
   - Which MCPs are used most
   - Usage percentage per MCP

3. **Task Type Distribution**
   - Common task types
   - Frequency distribution

4. **Token Usage by MCP**
   - Total tokens per MCP
   - Average per session

5. **Current Configuration**
   - Enabled/disabled status
   - Priority levels
   - Token costs

#### **Example Output:**

```
============================================================
MCP Usage Analytics Report
============================================================

📊 Overview:
  Total Sessions: 45
  Total Token Usage: 985,000
  Average Tokens per Session: 21,888

🔌 MCP Usage Frequency:
  zoho: 35 sessions (77.8%)
  playwright: 8 sessions (17.8%)
  chrome-devtools: 8 sessions (17.8%)

📋 Task Type Distribution:
  development: 30 sessions (66.7%)
  testing: 10 sessions (22.2%)
  debugging: 5 sessions (11.1%)

💰 Token Usage by MCP:
  zoho:
    Total: 280,000 tokens
    Average per session: 8,000 tokens
  playwright:
    Total: 400,000 tokens
    Average per session: 50,000 tokens
  chrome-devtools:
    Total: 305,000 tokens
    Average per session: 38,125 tokens

⚙️  Current MCP Configuration:
  playwright:
    Status: ✗ Disabled
    Priority: medium
    Token Cost: ~11,700 tokens
  chrome-devtools:
    Status: ✗ Disabled
    Priority: medium
    Token Cost: ~12,000+ tokens
  zoho:
    Status: ✓ Enabled
    Priority: high
    Token Cost: ~8,000 tokens

============================================================
Optimization Recommendations
============================================================

🔴 High Priority Recommendations:
  • ENABLE: playwright
    Reason: Used in 17.8% of sessions but currently disabled

  • ENABLE: chrome-devtools
    Reason: Used in 17.8% of sessions but currently disabled

💰 Token Budget Analysis:
  Average Usage: 21,888 / 200,000 (10.9%)

✓ Token usage is well within budget
```

#### **Data Storage:**

Usage data is stored in `.claude/state/mcp_usage_log.json`:

```json
{
  "created": "2025-11-14T14:30:00Z",
  "sessions": [
    {
      "timestamp": "2025-11-14T14:30:00Z",
      "mcps_used": ["zoho"],
      "task_type": "development",
      "token_usage": 15000
    }
  ],
  "total_sessions": 1,
  "total_token_usage": 15000
}
```

---

## 🔄 Recommended Workflows

### **Daily/Weekly Maintenance:**

```bash
# 1. Validate state file
./claude/scripts/validate-state.sh

# 2. Update state with latest metrics
./claude/scripts/update-state.sh

# 3. Check MCP usage patterns
python3 .claude/scripts/mcp-analytics.py
```

### **Before Committing Changes:**

```bash
# 1. Validate state
./claude/scripts/validate-state.sh

# 2. Bump version if needed
./claude/scripts/bump-version.sh patch "Description of changes"

# 3. Commit all changes
git add .claude/
git commit -m "chore: update configuration"
```

### **Monthly Optimization:**

```bash
# 1. Generate full analytics report
python3 .claude/scripts/mcp-analytics.py --report > mcp_report.txt

# 2. Review optimization recommendations
python3 .claude/scripts/mcp-analytics.py --optimize

# 3. Update MCP configuration based on insights
vim .claude/.mcp.json

# 4. Bump version
./claude/scripts/bump-version.sh minor "Optimized MCP configuration based on usage data"
```

---

## 🔧 Troubleshooting

### **Script Won't Execute:**

```bash
# Make sure scripts are executable
chmod +x .claude/scripts/*.sh
chmod +x .claude/scripts/*.py
```

### **Database Connection Failed:**

```bash
# Check .env file has database credentials
cat .env | grep DATABASE

# Test database connection manually
PGPASSWORD="$DATABASE_PASSWORD" psql -h localhost -U tsh_app_user -d tsh_erp_production -c "SELECT 1;"
```

### **Python Script Errors:**

```bash
# Ensure Python 3 is installed
python3 --version

# Scripts require standard library only (no external dependencies)
```

### **Validation Fails:**

```bash
# Check JSON syntax manually
python3 -m json.tool .claude/state/current-phase.json

# Run validation in verbose mode
./claude/scripts/validate-state.sh --verbose
```

---

## 📝 Script Integration with Git Hooks

### **Pre-commit Hook (Optional):**

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash

echo "Validating Claude Code configuration..."

# Validate state file
if ! ./.claude/scripts/validate-state.sh; then
  echo "❌ State validation failed!"
  exit 1
fi

echo "✓ Configuration validated"
exit 0
```

```bash
chmod +x .git/hooks/pre-commit
```

---

## 🔐 Security Notes

- Scripts only read/write to `.claude/` directory
- No external API calls (except health checks to your own servers)
- Database credentials loaded from `.env` (never hardcoded)
- Backups created before any modifications
- Dry-run mode available for testing

---

## 📊 File Structure

```
.claude/
├── scripts/
│   ├── README.md                    # This file
│   ├── update-state.sh              # State updater
│   ├── validate-state.sh            # State validator
│   ├── bump-version.sh              # Version manager
│   └── mcp-analytics.py             # MCP analytics
├── state/
│   ├── current-phase.json           # Main state file
│   ├── mcp_usage_log.json           # MCP usage data
│   └── backups/                     # Automatic backups
│       └── current-phase_*.json
├── CLAUDE.md                        # Main context file
└── .mcp.json                        # MCP configuration
```

---

## 🎯 Best Practices

1. **Run validation before committing** configuration changes
2. **Update state weekly** to keep metrics current
3. **Review MCP analytics monthly** for optimization opportunities
4. **Bump version** when making significant configuration changes
5. **Keep backups** of state file (automatic with update-state.sh)
6. **Use dry-run** mode when testing update-state.sh
7. **Document changes** in version bump commit messages

---

## 🆘 Support

If you encounter issues:

1. Check this README for troubleshooting
2. Validate state file: `./claude/scripts/validate-state.sh --verbose`
3. Check script permissions: `ls -la .claude/scripts/`
4. Review error messages carefully
5. Consult `.claude/ENHANCEMENT_CHANGELOG_NOV14.md` for implementation details

---

**Last Updated:** 2025-11-14
**Version:** 1.0.0
**Maintainer:** TSH ERP Team
