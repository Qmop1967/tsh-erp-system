# 🤖 TSH Auto-Healing MCP Server

Model Context Protocol (MCP) server for TSH ERP System auto-healing and monitoring.

## 🎯 Purpose

This MCP server provides Claude Code with direct tools to:
- Monitor TSH ERP system health
- View system logs
- Execute healing actions
- Check Zoho sync status
- Trigger GitHub workflows
- Get auto-healing suggestions

## 📋 Features

### 6 Available Tools

1. **check_system_health** - Check health of system components
   - Components: all, staging, production, database, zoho, tds-worker

2. **get_healing_suggestions** - Get AI-generated healing suggestions from CI/CD

3. **execute_healing_action** - Execute specific healing actions
   - Actions: restart_staging, restart_production, restart_tds_worker, retry_failed_syncs, check_zoho_webhooks, clear_sync_queue
   - Supports dry-run mode for safety

4. **view_system_logs** - View recent logs from components
   - Components: staging, production, tds-worker, auto-healing
   - Configurable line count (10-500)

5. **check_zoho_sync_status** - Check Zoho synchronization status
   - Optional detailed mode with sync queue info

6. **run_github_workflow** - Trigger GitHub Actions workflows
   - Workflows: intelligent-staging, intelligent-production, test

## 🚀 Installation

### 1. Install MCP SDK

```bash
pip install mcp
```

### 2. Add to Claude Desktop Config

Edit: `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "tsh-auto-healing": {
      "command": "python3",
      "args": [
        "/Users/khaleelal-mulla/TSH_ERP_Ecosystem/.mcp/tsh-auto-healing/server.py"
      ],
      "env": {
        "TSH_PROJECT_ROOT": "/Users/khaleelal-mulla/TSH_ERP_Ecosystem",
        "TSH_VPS_HOST": "167.71.39.50",
        "TSH_VPS_USER": "root"
      }
    }
  }
}
```

### 3. Restart Claude Desktop

Close and reopen Claude Desktop application.

## 💡 Usage Examples

### Example 1: Check System Health

```
Check the health of all TSH ERP components
```

Claude will use `check_system_health` tool with component="all"

### Example 2: View Staging Logs

```
Show me the last 100 lines of staging logs
```

Claude will use `view_system_logs` tool with component="staging", lines=100

### Example 3: Check Zoho Sync

```
Check the Zoho synchronization status with details
```

Claude will use `check_zoho_sync_status` tool with detailed=true

### Example 4: Execute Healing (Dry Run)

```
Restart the TDS worker (dry run first)
```

Claude will use `execute_healing_action` with action="restart_tds_worker", dry_run=true

### Example 5: Get Healing Suggestions

```
What are the latest auto-healing suggestions?
```

Claude will use `get_healing_suggestions` tool

### Example 6: Trigger Workflow

```
Run the intelligent staging workflow
```

Claude will use `run_github_workflow` with workflow="intelligent-staging", branch="develop"

## ⚙️ Configuration

### Environment Variables

- `TSH_PROJECT_ROOT` - Path to TSH ERP project (default: /Users/khaleelal-mulla/TSH_ERP_Ecosystem)
- `TSH_VPS_HOST` - VPS hostname or IP (default: 167.71.39.50)
- `TSH_VPS_USER` - VPS SSH user (default: root)

### SSH Setup Required

The MCP server requires SSH access to VPS:

```bash
# Add SSH key to ssh-agent
ssh-add ~/.ssh/id_rsa

# Test connection
ssh root@167.71.39.50 "echo Connected"
```

## 🔒 Security

- All destructive actions default to `dry_run=true`
- Requires SSH key authentication (no password)
- Executes commands via SSH with timeout protection
- Only whitelisted healing actions allowed

## 🛠️ Troubleshooting

### MCP Server Not Showing

1. Check Claude Desktop config is valid JSON
2. Restart Claude Desktop completely
3. Check logs: `~/Library/Logs/Claude/mcp*.log`

### SSH Connection Failed

1. Verify SSH key is added: `ssh-add -l`
2. Test connection: `ssh root@167.71.39.50`
3. Check VPS firewall allows SSH

### Tool Execution Failed

1. Check VPS services are running
2. Verify database credentials
3. Check GitHub CLI is authenticated: `gh auth status`

## 📚 Related Documentation

- `INTELLIGENT_CICD_SYSTEM.md` - Full CI/CD documentation
- `VPS_SETUP_INSTRUCTIONS.md` - VPS configuration guide
- `CLAUDE_CODE_AGENT_VERIFICATION.md` - Agent verification report

## 🤖 Integration with Auto-Healing

This MCP server integrates with:

1. **GitHub Actions** - `.github/workflows/intelligent-staging.yml`
   - Generates auto-healing suggestions
   - Creates artifact reports

2. **Auto-Healing Script** - `scripts/claude_auto_healing.sh`
   - Executes on VPS
   - Reads MCP tool suggestions
   - Performs healing actions

3. **Claude Code** - `.claude/settings.local.json`
   - Permission rules
   - Staging-first workflow enforcement

## 📞 Support

For issues or questions:
1. Check logs: `view_system_logs` tool
2. Review workflow runs: `gh run list`
3. Check auto-healing report: `get_healing_suggestions` tool

---

**🤖 Generated with [Claude Code](https://claude.com/claude-code)**
**📅 Created:** November 3, 2025
