# Chrome DevTools MCP - Quick Reference

## 🚀 Quick Start

```bash
# 1. Start Chrome with debugging
./scripts/start-chrome-devtools.sh

# 2. Start MCP server (in another terminal)
npx chrome-devtools-mcp

# 3. Your app is ready at:
http://localhost:5173
```

## 📝 Common Commands

### Start Chrome with Debugging
```bash
./scripts/start-chrome-devtools.sh
```

### Check if Chrome Debugging is Active
```bash
curl http://localhost:9222/json/version
```

### Start MCP Server
```bash
npx chrome-devtools-mcp
```

### Kill Chrome Process
```bash
pkill -9 "Google Chrome"
```

## 🎯 Use Cases for Settings Button Testing

### 1. Verify Settings Button in Header
```javascript
// Open DevTools Console and run:
document.querySelector('header button > svg.lucide-settings')
```

### 2. Confirm No Settings in Sidebar
```javascript
// Should return null:
document.querySelector('.sidebar a[href="/settings"]')
```

### 3. Check Button Click
```javascript
// Click settings button programmatically:
document.querySelector('header a[href="/settings"]').click()
```

### 4. Monitor Network Requests
Open Network tab and check API calls when navigating to settings.

## 🔧 Configuration Files

- **MCP Config**: `.mcp/chrome-devtools-config.json`
- **Start Script**: `scripts/start-chrome-devtools.sh`
- **Documentation**: `CHROME_DEVTOOLS_MCP_INSTALLATION_COMPLETE.md`

## 🌐 Useful URLs

- **DevTools Protocol**: http://localhost:9222/json
- **Version Info**: http://localhost:9222/json/version
- **Active Tabs**: http://localhost:9222/json/list
- **Your App**: http://localhost:5173

## ⚡ Package Info

- **Package**: `chrome-devtools-mcp`
- **Version**: `0.6.0`
- **Location**: `/opt/homebrew/bin/chrome-devtools-mcp`
- **Status**: ✅ Installed globally + project devDependency

## 💡 Tips

1. **Always start Chrome with debugging before using MCP**
2. **Use a separate Chrome profile for debugging**
3. **Close other Chrome instances to avoid conflicts**
4. **Check port 9222 availability before starting**

## 🐛 Troubleshooting

**Chrome won't start with debugging:**
```bash
# Kill all Chrome processes
pkill -9 "Google Chrome"

# Try again
./scripts/start-chrome-devtools.sh
```

**Port 9222 already in use:**
```bash
# Check what's using the port
lsof -i :9222

# Kill the process
kill -9 <PID>
```

**MCP not connecting:**
```bash
# Verify Chrome is running with debugging
curl http://localhost:9222/json/version

# Should return JSON with browser version
```

---

**Installation Complete**: ✅  
**Version**: chrome-devtools-mcp@0.6.0  
**Ready to Use**: Yes 🎉
