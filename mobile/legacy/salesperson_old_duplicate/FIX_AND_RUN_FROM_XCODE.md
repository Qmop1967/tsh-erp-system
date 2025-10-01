# 🔧 Fix Code Signing and Run from Xcode

## The Problem
The app isn't signing properly through command line. We need to use Xcode's GUI for automatic signing.

---

## ✅ **SIMPLE SOLUTION - Follow These Steps:**

### 1️⃣ Open Xcode Properly
The workspace should already be open. If not, double-click:
```
mobile/flutter_apps/salesperson/ios/Runner.xcworkspace
```

### 2️⃣ Select "Runner" Project
- **Left sidebar** → Click **"Runner"** (the blue icon at top)
- This opens the project settings

### 3️⃣ Select "Runner" Target
- In the middle panel, under **TARGETS**
- Click **"Runner"** (not the PROJECT, the TARGET)

### 4️⃣ Go to "Signing & Capabilities" Tab
- Click the tab at the top: **"Signing & Capabilities"**

### 5️⃣ Enable Automatic Signing
Make sure these are set:
- ✅ **"Automatically manage signing"** checkbox is **CHECKED**
- **Team:** Should show **"Khaleel Ahmed (38U844SAJ5)"**
- **Bundle Identifier:** `com.tsh.admin`
- **Signing Certificate:** Should show **"Apple Development"**

### 6️⃣ Fix Any Errors
If you see **RED errors** about signing:
- Click the **"Team"** dropdown
- Select **"Khaleel Ahmed (38U844SAJ5)"** again
- Click **"Try Again"** button if it appears

### 7️⃣ Select Your iPhone
- **Top toolbar** → Device dropdown (next to "Runner" scheme)
- Select **"home"** (your iPhone)
- Make sure it shows **"home"** not "Any iOS Device"

### 8️⃣ Clean Build Folder
- Menu: **Product** → **Clean Build Folder**
- Or press: **Shift + Cmd + K**
- Wait for it to finish

### 9️⃣ Click RUN!
- Click the **▶️ Play button** (top left)
- Or press: **Cmd + R**

---

## 📱 Watch the Progress

You'll see in Xcode:
1. ⏳ **"Building..."** (30-60 seconds)
2. ✅ **"Build Succeeded"**
3. 📲 **"Installing..."**
4. 🚀 **App launches on your iPhone!**

---

## 🔐 On Your iPhone (First Launch)

If you see **"Untrusted Developer"** on your iPhone:

### Trust the Certificate:
1. **iPhone Settings** → **General** → **VPN & Device Management**
2. Under **"DEVELOPER APP"**, tap: **"Khaleel Ahmed"**
3. Tap: **"Trust 'Khaleel Ahmed'"**
4. Tap: **"Trust"** again to confirm
5. Go back to home screen
6. **Tap the TSH Salesperson App icon**

---

## ❓ Common Issues

### Issue: "No code signing identities found"
**Fix:**
1. Xcode → **Settings** (Cmd + ,)
2. **Accounts** tab
3. Click your Apple ID
4. Click **"Manage Certificates..."**
5. Click **"+"** → **"Apple Development"**
6. Close and try again

### Issue: Device shows "Unavailable"
**Fix:**
1. Unplug and replug iPhone
2. Unlock iPhone
3. Trust computer if asked
4. Xcode → **Window** → **Devices and Simulators**
5. Wait for device to show "Ready"

### Issue: Build succeeds but app doesn't launch
**Fix:**
1. Manually tap the app icon on iPhone
2. Or: Product → Run Without Building (Cmd + Ctrl + R)

---

## 🎯 Expected Result

Once the app launches, you'll see:
- ✅ **TSH Salesperson App** interface
- ✅ **Dashboard** with metrics
- ✅ **Navigation menu**
- ✅ **Arabic/English** language support
- ✅ **Login screen** or **Home screen**

---

**Just open Xcode, check the Signing & Capabilities, and click Run!** 🚀

