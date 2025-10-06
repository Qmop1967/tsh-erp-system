# 🎯 Chrome Extension Installation - Step by Step

## 📍 Where You Should Be Right Now

Chrome should have opened the **Extensions page** at: `chrome://extensions/`

---

## 🚀 Step-by-Step Visual Guide

### ✅ Step 1: Enable Developer Mode
1. Look in the **top-right corner** of the Extensions page
2. Find the toggle switch labeled **"Developer mode"**
3. **Click to turn it ON** (it should show blue/colored when enabled)

```
[Developer mode]  ← Click this toggle
     OFF    ON
```

### ✅ Step 2: Load the Extension
1. With Developer mode enabled, you'll see new buttons appear
2. Click the **"Load unpacked"** button (usually on the top left)
3. A file selection dialog will open

### ✅ Step 3: Select the Extension Folder
1. In the file dialog, navigate to: `/Users/khaleelal-mulla/Downloads/chrome-extension`
2. **Select the entire `chrome-extension` folder**
3. Click **"Select"**

### ✅ Step 4: Verify Installation
You should now see **"BrowserToolsMCP"** in your extensions list with:
- ✅ Extension name: BrowserToolsMCP
- ✅ Version: 1.2.0
- ✅ Status: Enabled (blue toggle switch)

---

## 🔗 Connect to Your TSH ERP System

### ✅ Step 5: Open Your Project
1. Open a new tab and go to: `http://localhost:5173`
2. Your TSH ERP System should be running

### ✅ Step 6: Open DevTools
1. On your TSH ERP System page, press **F12** (or right-click → **Inspect**)
2. Chrome DevTools will open

### ✅ Step 7: Find BrowserTools Panel
1. In DevTools, look for a new tab labeled **"BrowserToolsMCP"**
2. **Click on this tab**

### ✅ Step 8: Verify Connection
The BrowserToolsMCP panel should show:
- ✅ Connected to server on port 3025
- ✅ Ready to capture browser data

---

## 🎉 Success! Ready for Automated Testing

Once connected, you can:

### 📸 Take Screenshots
```bash
I'll be able to take screenshots of your UI automatically
```

### 📊 Monitor Console Logs
```bash
I can monitor JavaScript console errors and messages
```

### 🌐 Track Network Activity
```bash
I can watch API calls and network requests
```

### ♿ Run Accessibility Audits
```bash
I can check for WCAG compliance issues
```

### 🚀 Performance Testing
```bash
I can analyze page performance and suggest optimizations
```

---

## 🚨 If You See Any Issues

### Extension Not Loading:
- Make sure "Developer mode" is enabled
- Ensure you selected the entire `chrome-extension` folder
- Check for any error messages in the Extensions page

### Can't Find BrowserToolsMCP Tab:
- Refresh the page (F5)
- Close and reopen DevTools
- Make sure the extension is enabled (toggle switch is on)

### Connection Issues:
- Verify the browser-tools-server is running (should see in terminal)
- Check that both servers are running in your terminal tabs

---

## 📞 Need Help?

If you get stuck at any step, let me know what you see on screen and I'll help you troubleshoot!

**Quick Reference:**
- Extension path: `/Users/khaleelal-mulla/Downloads/chrome-extension`
- Your project: `http://localhost:5173`
- Extensions page: `chrome://extensions/`
