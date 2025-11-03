# 🚀 TSH Auto-Healing MCP Server - Setup Instructions

## ⚠️ Prerequisites

The MCP SDK requires **Python 3.10 or higher**. Your system currently has Python 3.9.6.

### Step 1: Install Python 3.11

```bash
# Install Python 3.11 via Homebrew
brew install python@3.11

# Verify installation
python3.11 --version
# Should show: Python 3.11.x
```

### Step 2: Install MCP SDK

```bash
# Install MCP for Python 3.11
python3.11 -m pip install mcp

# Verify installation
python3.11 -c "import mcp; print('MCP installed successfully')"
```

### Step 3: Update Claude Desktop Config

Edit: `~/.config/claude/claude_desktop_config.json`

Add the `tsh-auto-healing` server to the `mcpServers` section:

```json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://postgres.trjjglxhteqnzmyakxhe:Zcbbm.97531tsh@aws-1-eu-north-1.pooler.supabase.com:6543/postgres"
      ]
    },
    "playwright": {
      "command": "npx",
      "args": [
        "-y",
        "@playwright/mcp"
      ]
    },
    "zoho-books": {
      "command": "python3",
      "args": [
        "/Users/khaleelal-mulla/TSH Projects/tsh-online-store/.mcp/zoho-books/server.py"
      ],
      "env": {
        "ZOHO_CLIENT_ID": "1000.RYRPK7578ZRKN6K4HKNF4LKL2CC9IQ",
        "ZOHO_CLIENT_SECRET": "a39a5dcdc057a8490cb7960d1400f62ce14edd6455",
        "ZOHO_REFRESH_TOKEN": "1000.2e358f3c53d3e22ac2d134c5c93d9c5b.118c5e88cd0a4ed2a1143056f2d09e68",
        "ZOHO_ORGANIZATION_ID": "748369814",
        "ZOHO_REGION": "US",
        "ZOHO_API_DOMAIN": "https://www.zohoapis.com"
      }
    },
    "tsh-auto-healing": {
      "command": "python3.11",
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

### Step 4: Setup SSH Access to VPS

```bash
# Add your SSH key to ssh-agent
ssh-add ~/.ssh/id_rsa

# Test connection to VPS
ssh root@167.71.39.50 "echo 'Connected successfully'"
```

### Step 5: Restart Claude Desktop

1. Quit Claude Desktop completely (⌘Q)
2. Reopen Claude Desktop
3. The MCP server should now be available

### Step 6: Verify Installation

In Claude Desktop, try:

```
Check the health of the TSH ERP staging environment
```

Claude should use the `check_system_health` tool from the tsh-auto-healing MCP server.

## 🔧 Troubleshooting

### Issue 1: Python 3.11 not found

```bash
# Check if installed
which python3.11

# If not found, install via Homebrew
brew install python@3.11

# Add to PATH if needed
echo 'export PATH="/opt/homebrew/opt/python@3.11/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Issue 2: MCP module not found

```bash
# Reinstall MCP
python3.11 -m pip install --upgrade mcp

# Check installation
python3.11 -c "import mcp; print(mcp.__version__)"
```

### Issue 3: MCP server not showing in Claude

1. Check config file is valid JSON:
   ```bash
   cat ~/.config/claude/claude_desktop_config.json | python3 -m json.tool
   ```

2. Check Claude Desktop logs:
   ```bash
   tail -f ~/Library/Logs/Claude/mcp*.log
   ```

3. Restart Claude Desktop completely

### Issue 4: SSH connection failed

```bash
# Check SSH key is loaded
ssh-add -l

# If not, add it
ssh-add ~/.ssh/id_rsa

# Test VPS connection
ssh -v root@167.71.39.50 "echo test"
```

## 📚 Available Tools After Setup

Once configured, Claude will have access to:

1. ✅ **check_system_health** - Monitor system components
2. ✅ **get_healing_suggestions** - Get AI healing suggestions
3. ✅ **execute_healing_action** - Execute healing actions (with dry-run)
4. ✅ **view_system_logs** - View system logs
5. ✅ **check_zoho_sync_status** - Check Zoho sync status
6. ✅ **run_github_workflow** - Trigger CI/CD workflows

## 🎯 Quick Test Commands

After setup, test with these prompts in Claude Desktop:

```
1. "Check the health of all TSH ERP components"
2. "Show me the last 50 lines of staging logs"
3. "Check Zoho synchronization status with details"
4. "What are the latest auto-healing suggestions?"
5. "Restart the TDS worker (dry run first)"
6. "Trigger the intelligent staging workflow"
```

## ✅ Success Indicators

You'll know it's working when:

- ✅ Claude responds with actual VPS data (not simulated)
- ✅ You see real systemd service statuses
- ✅ Logs show actual timestamps and entries
- ✅ GitHub workflow IDs are real and verifiable

## 📞 Next Steps After Setup

1. Review `README.md` for detailed usage examples
2. Check `CLAUDE_CODE_AGENT_VERIFICATION.md` for system status
3. Follow `VPS_SETUP_INSTRUCTIONS.md` to complete VPS setup
4. Enable auto-deployment in `intelligent-staging.yml` (line 725)

---

**🤖 Generated with [Claude Code](https://claude.com/claude-code)**
**📅 Created:** November 3, 2025
