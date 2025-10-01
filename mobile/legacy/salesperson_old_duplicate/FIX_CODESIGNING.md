# 🔐 Fix Code Signing Issue - TSH Salesperson App

## The Issue
**"The executable is not codesigned"** - This means Xcode needs your Apple Developer account to sign the app for installation on your iPhone.

## Quick Fix Steps

### 1. In Xcode (Now Open):

1. **Select "Runner"** in the left sidebar (the top blue icon)
2. Click on **"Signing & Capabilities"** tab (top section)
3. Under **"Team"** dropdown:
   - If you see **"Khaleel Ahmed (3BJB4453J5)"** → Select it
   - If you see **"Add Account..."** → Click it and sign in with your Apple ID
   
4. Make sure these are checked:
   - ✅ **"Automatically manage signing"**
   - ✅ Team: **Khaleel Ahmed (3BJB4453J5)** or your Apple ID
   
5. **Bundle Identifier**: Should be something like `com.tsh.salesperson`
   - If it shows an error, change it to: `com.tsh.salesperson.app` or `com.yourdomain.salesperson`

6. **Click the Play button (▶️)** in Xcode (top left) with your iPhone selected

### 2. On Your iPhone:

First time running the app, you'll see:
- **"Untrusted Developer"** message

To fix:
1. Go to **Settings** on your iPhone
2. Tap **General** → **VPN & Device Management**
3. Under **"Developer App"**, tap on **your Apple ID/name**
4. Tap **"Trust [Your Name]"**
5. Tap **"Trust"** again to confirm

### 3. Launch Again:

Once trusted, the app will launch automatically!

---

## Alternative: Use Personal Apple ID (Free)

Don't have a paid Apple Developer account? No problem!

1. In Xcode → **Preferences** → **Accounts**
2. Click **"+"** → **"Add Apple ID"**
3. Sign in with your personal Apple ID (free)
4. Go back to **Signing & Capabilities**
5. Select your personal Apple ID as the Team
6. Change Bundle ID to something unique: `com.yourname.salesperson`

---

## What I've Done:

✅ Opened the project in Xcode
✅ The workspace is loaded and ready

## Next Steps:

**In Xcode that just opened:**
1. Configure signing (steps above)
2. Click Run (▶️) button
3. Trust developer on iPhone
4. App will launch!

---

**The app is ready to run once you configure the signing in Xcode!** 🚀
