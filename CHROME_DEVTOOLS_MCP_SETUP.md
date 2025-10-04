# Chrome DevTools MCP Setup Guide for VS Code

## Overview
The Chrome DevTools MCP (Model Context Protocol) allows GitHub Copilot in VS Code to interact with Chrome browser tabs, enabling you to debug, inspect, and test web applications directly from your AI chat.

## Installation Methods

### Method 1: Using npx (Recommended - No Global Install Needed)

This method doesn't require global installation and works better with network issues.

#### Step 1: Configure VS Code Settings

1. Open VS Code Command Palette: `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
2. Type: `Preferences: Open User Settings (JSON)`
3. Add the following MCP configuration:

```json
{
  "github.copilot.chat.mcp": {
    "servers": {
      "puppeteer": {
        "command": "npx",
        "args": [
          "-y",
          "@modelcontextprotocol/server-puppeteer"
        ],
        "env": {
          "PUPPETEER_SKIP_DOWNLOAD": "false"
        }
      }
    }
  }
}
```

### Method 2: Manual Installation with Local Chrome

If you want to use your existing Chrome installation:

#### Step 1: Install Chrome DevTools Protocol Package

```bash
npm install -g chrome-remote-interface
```

#### Step 2: Create MCP Server Script

Create a file at `~/.config/mcp/chrome-devtools-server.js`:

```javascript
#!/usr/bin/env node

const CDP = require('chrome-remote-interface');

async function main() {
  try {
    const client = await CDP();
    const { Network, Page, Runtime, DOM } = client;
    
    // Enable necessary domains
    await Network.enable();
    await Page.enable();
    await DOM.enable();
    await Runtime.enable();
    
    console.log('Chrome DevTools MCP Server started');
    
    // Keep the server running
    await new Promise(() => {});
  } catch (err) {
    console.error('Error:', err);
    process.exit(1);
  }
}

main();
```

### Method 3: Using Playwright (More Reliable Alternative)

Playwright is more stable and well-maintained than Puppeteer for MCP.

#### Step 1: Install Playwright

```bash
npm install -g @playwright/test
npx playwright install chromium
```

#### Step 2: Configure VS Code

Add to your VS Code `settings.json`:

```json
{
  "github.copilot.chat.mcp": {
    "servers": {
      "playwright": {
        "command": "npx",
        "args": [
          "-y",
          "playwright",
          "run-server"
        ]
      }
    }
  }
}
```

## Alternative: Use Browser Extension Instead

If MCP servers are having issues, you can use browser extensions:

### Chrome DevTools Extension for VS Code

1. **Install Extension**: Search for "Browser Preview" in VS Code extensions
2. **Usage**: Opens Chrome preview directly in VS Code
3. **Benefit**: No MCP configuration needed

## Recommended Setup for Your TSH ERP System

Since you're already testing at `http://localhost:5173`, here's the best approach:

### Option A: Simple Browser Preview (Built-in VS Code)

Already working! You've been using this:
```
Simple Browser at http://localhost:5173
```

**Advantages**:
- ✅ Already working
- ✅ No configuration needed  
- ✅ Built into VS Code

### Option B: Live Server + External Chrome

1. Keep your dev server running
2. Open Chrome manually
3. Use Chrome DevTools directly (F12)
4. More reliable than MCP for now

## Troubleshooting

### Issue: Puppeteer Download Fails
**Solution**: Use npx method or Playwright instead

### Issue: Network Timeout
**Solution**: Skip Chrome download:
```bash
PUPPETEER_SKIP_DOWNLOAD=true npm install -g @modelcontextprotocol/server-puppeteer
```

Then configure Chrome path manually in settings.

### Issue: MCP Not Working
**Solution**: 
1. Restart VS Code
2. Check GitHub Copilot is enabled
3. Try the Simple Browser instead

## Testing Your Current Setup

You already have a working browser preview! Test it:

1. Open Command Palette: `Cmd+Shift+P`
2. Type: "Simple Browser: Show"
3. Enter: `http://localhost:5173`
4. Your TSH ERP app loads with the hover dropdown working!

## Best Practice for Your Workflow

For testing the sidebar hover dropdowns:

```
1. Terminal 1: npm run dev (frontend)
2. Terminal 2: Backend server
3. VS Code: Simple Browser preview
4. External Chrome: Full DevTools access
```

This gives you the best of both worlds!

## Summary

**Current Status**: ✅ You already have browser preview working in VS Code!

**Recommended**: Continue using Simple Browser for now, it's working perfectly for testing your hover dropdowns.

**Future**: Once MCP servers are more stable, you can revisit this setup.

---

**Your TSH ERP System is already set up perfectly for development! 🚀**
