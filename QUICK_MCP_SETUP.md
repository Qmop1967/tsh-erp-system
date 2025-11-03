# 🚀 Quick MCP Setup - Add TSH Auto-Healing Agent

**Current Issue:** TSH Auto-Healing MCP server not showing in Claude Desktop

**Reason:** Python 3.11+ required (you have 3.9.6)

---

## Step 1: Install Python 3.11

```bash
# Install Python 3.11
brew install python@3.11

# Verify installation
python3.11 --version
# Should show: Python 3.11.x
```

## Step 2: Install MCP SDK

```bash
# Install MCP package
python3.11 -m pip install mcp

# Verify installation
python3.11 -c "import mcp; print('✅ MCP installed successfully!')"
```

## Step 3: Update Claude Desktop Config

**File to edit:** `~/.config/claude/claude_desktop_config.json`

**Current content:**
```json
{
  "mcpServers": {
    "supabase": { ... },
    "playwright": { ... },
    "zoho-books": { ... }
  }
}
```

**Add this section** (after zoho-books, before the closing `}`):

```json
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
```

**Complete file should look like:**
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

## Step 4: Verify JSON Syntax

```bash
# Validate JSON syntax
cat ~/.config/claude/claude_desktop_config.json | python3 -m json.tool
```

If you see formatted JSON output, it's valid! ✅

## Step 5: Setup SSH Access

```bash
# Add SSH key to agent
ssh-add ~/.ssh/id_rsa

# Test VPS connection
ssh root@167.71.39.50 "echo '✅ Connected!'"
```

## Step 6: Restart Claude Desktop

1. **Quit** Claude Desktop completely (⌘Q)
2. **Wait** 5 seconds
3. **Reopen** Claude Desktop
4. The MCP server will load automatically

## Step 7: Test It!

In Claude Desktop, ask:

```
Check the health of TSH ERP staging
```

You should see **real data** from your VPS! 🎉

---

## 🔧 Troubleshooting

### Issue: "Python 3.11 not found"

```bash
# Add to PATH
echo 'export PATH="/opt/homebrew/opt/python@3.11/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Verify
which python3.11
```

### Issue: "MCP module not found"

```bash
# Reinstall MCP
python3.11 -m pip install --upgrade mcp

# Check installation
python3.11 -m pip list | grep mcp
```

### Issue: "Server not loading in Claude"

1. Check Claude Desktop logs:
   ```bash
   tail -f ~/Library/Logs/Claude/mcp*.log
   ```

2. Verify config syntax:
   ```bash
   cat ~/.config/claude/claude_desktop_config.json | python3 -m json.tool
   ```

3. Check server script is executable:
   ```bash
   ls -la /Users/khaleelal-mulla/TSH_ERP_Ecosystem/.mcp/tsh-auto-healing/server.py
   ```

### Issue: "SSH connection failed"

```bash
# Check SSH key
ssh-add -l

# If empty, add key
ssh-add ~/.ssh/id_rsa

# Test connection
ssh -v root@167.71.39.50
```

---

## ✅ Success Indicators

You'll know it's working when:

1. ✅ Claude recognizes commands like "check system health"
2. ✅ You see **real VPS data** (not simulated)
3. ✅ Service statuses show actual systemd output
4. ✅ Logs show real timestamps from VPS
5. ✅ You can execute healing actions (with dry-run)

---

## 📚 What You'll Be Able to Do

Once the MCP server is active, you can ask Claude:

### System Monitoring
- "Check the health of all TSH ERP components"
- "Is staging running properly?"
- "What's the status of the production environment?"

### Log Analysis
- "Show me the last 100 lines of staging logs"
- "What errors are in the production logs?"
- "View TDS worker logs"

### Zoho Sync
- "Check Zoho synchronization status"
- "How many Zoho sync items are pending?"
- "Show me failed sync items"

### Healing Actions
- "Restart the staging service" (will ask for confirmation)
- "Retry failed Zoho syncs"
- "Clear old completed syncs"

### CI/CD
- "Trigger the intelligent staging workflow"
- "What are the latest auto-healing suggestions?"
- "Run the tests"

---

## 🎯 Quick Commands

Copy and paste these into your terminal:

```bash
# Complete setup in one go
brew install python@3.11 && \
python3.11 -m pip install mcp && \
ssh-add ~/.ssh/id_rsa && \
echo "✅ Setup complete! Now edit Claude Desktop config and restart."
```

Then:
1. Edit: `~/.config/claude/claude_desktop_config.json`
2. Add the `tsh-auto-healing` section
3. Save and restart Claude Desktop

---

**Need the config template?**

```bash
# View the template
cat /Users/khaleelal-mulla/TSH_ERP_Ecosystem/.mcp/tsh-auto-healing/claude_desktop_config_addition.json
```

---

🤖 Generated with Claude Code | 📅 November 3, 2025
