# 🚀 Chrome DevTools MCP - Quick Start Guide

## ✅ Installation Complete!

**Status**: Chrome DevTools MCP Server is installed and configured!

---

## ⚡ Quick Start (3 Steps)

### Step 1: Restart VS Code
```bash
# VERY IMPORTANT: Close VS Code completely and reopen it!
```

### Step 2: Test Installation
Open Claude in VS Code and say:
```
"Open Chrome and navigate to http://localhost:5173"
```

### Step 3: Test Your Hover Dropdowns!
```
"Test the hover dropdown feature:
1. Open localhost:5173
2. Collapse the sidebar
3. Hover over User Management icon
4. Take a screenshot of the dropdown"
```

---

## 🎯 Common Commands for Your TSH ERP System

### Test UI Features
```
"Open my app and test if the sidebar collapse/expand works"
"Check if all navigation menu items are clickable"
"Verify the hover dropdowns appear correctly"
"Test the login form with test credentials"
```

### Take Screenshots
```
"Take a screenshot of the dashboard"
"Capture the sidebar in both collapsed and expanded states"
"Screenshot the hover dropdown in action"
```

### Debug Issues
```
"Check for JavaScript errors in the console"
"Monitor network requests when loading the page"
"Verify the API endpoints are being called correctly"
```

### Visual Testing
```
"Compare the current UI with the design"
"Check if the theme switching works"
"Test responsive design at different screen sizes"
```

---

## 🔧 Configuration Details

**Installed**: `@modelcontextprotocol/server-puppeteer@2025.5.12`

**Config Location**: 
```
~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings.json
```

**Current Config**:
```json
{
  "mcpServers": {
    "puppeteer": {
      "command": "mcp-server-puppeteer",
      "args": []
    }
  }
}
```

---

## 🎬 Example: Test Your Hover Dropdowns

**You**: 
```
Please test my sidebar hover dropdown feature:
1. Open http://localhost:5173
2. Wait for the page to load
3. Collapse the sidebar using the bottom button
4. Hover over the "Inventory" icon
5. Take a screenshot showing the dropdown
6. Verify the dropdown appears outside the sidebar and overlays the main content
```

**Claude will**:
- Launch Chrome
- Navigate to your app
- Perform each step
- Capture screenshots
- Analyze the results
- Report findings

---

## ⚠️ Important Notes

### Must Restart VS Code!
The MCP server only activates after restarting VS Code. Don't skip this!

### Development Server Must Be Running
Make sure your app is running on `http://localhost:5173` before testing.

### Chrome Will Open Automatically
When you use MCP commands, Chrome/Chromium will launch automatically.

---

## 🐛 Troubleshooting

### "MCP server not responding"
→ Did you restart VS Code? This is the #1 issue!

### "Cannot connect to localhost"
→ Make sure your dev server is running:
```bash
cd frontend && npm run dev
```

### "Command not found"
→ Verify installation:
```bash
npm list -g @modelcontextprotocol/server-puppeteer
```

---

## 💡 Pro Tips

1. **Use natural language** - Claude understands what you want to test
2. **Be specific** - Mention exact elements, buttons, or features
3. **Request screenshots** - Visual proof is very helpful
4. **Combine actions** - Test multiple features in one command
5. **Debug together** - Let Claude inspect HTML/CSS/console logs

---

## 🎉 You're Ready!

**Next Action**: 
1. **Restart VS Code NOW** (close and reopen)
2. Try the test command above
3. Start testing your hover dropdowns automatically!

---

**Status**: ✅ INSTALLED  
**Action Required**: RESTART VS CODE

**After restart, you can control Chrome through Claude! 🎯**
