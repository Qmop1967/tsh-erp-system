# BrowserTools Chrome Extension Installation Guide

## 🚀 Quick Installation Steps

### Step 1: Open Chrome Extension Management
1. Open Chrome browser
2. Navigate to: `chrome://extensions/`
3. Enable "Developer mode" (toggle switch in top right corner)

### Step 2: Load the Extension
1. Click on "Load unpacked" button
2. Navigate to: `/Users/khaleelal-mulla/Downloads/chrome-extension`
3. Select the folder and click "Select"

### Step 3: Verify Installation
1. You should see "BrowserToolsMCP" in your extensions list
2. The extension should be enabled

### Step 4: Connect to Browser Tools Server
1. Open your TSH ERP System (http://localhost:5173)
2. Open Chrome DevTools (F12 or right-click → Inspect)
3. Click on the "BrowserToolsMCP" tab in DevTools
4. The extension should automatically connect to the running server on port 3025

## 🔧 Server Status Check

Both servers should be running:
- ✅ MCP Server: Configured in IDE
- ✅ Browser Tools Server: Running on http://localhost:3025

## 🧪 Automated UI Testing

Once the extension is connected, you can use these commands:
- Take screenshots of your UI
- Monitor console logs
- Track network activity
- Run accessibility audits
- Perform SEO analysis
- Check performance metrics

## 📋 Current Files Ready

Extension location: `/Users/khaleelal-mulla/Downloads/chrome-extension/`
- manifest.json (extension configuration)
- background.js (background script)
- devtools.html & devtools.js (DevTools integration)
- panel.html & panel.js (extension panel)

## 🎯 Next Steps

1. Install the extension using the steps above
2. Open your TSH ERP System in Chrome
3. Open DevTools and navigate to BrowserToolsMCP tab
4. Start automated UI testing!
