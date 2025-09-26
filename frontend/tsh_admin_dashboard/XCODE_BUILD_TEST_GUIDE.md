🎯 TSH ADMIN APP - XCODE BUILD & TEST GUIDE
===========================================

📱 DEVICE STATUS: ✅ iPhone 15 Pro Max Connected Wirelessly
🔧 PROJECT STATUS: ✅ Clean Build Ready
📦 DEPENDENCIES: ✅ All Dependencies Installed
🍎 XCODE: ✅ Workspace Opening

🏗️ CURRENT CONFIGURATION:
=========================
✅ Bundle Identifier: com.tsh.admin
✅ Team ID: 3BJB4453J5 (Khaleel Ahmed)
✅ iOS Deployment Target: 12.0
✅ Swift Version: 5.0
✅ Device: iPhone 15 Pro Max (00008130-0004310C1ABA001C)

🚀 IN XCODE - FOLLOW THESE STEPS:
=================================

1. 🧹 CLEAN BUILD FIRST (ESSENTIAL):
   • Press: Cmd + Shift + K
   • This clears any cached build issues

2. 🎯 SELECT YOUR DEVICE:
   • Click device dropdown (next to play button)
   • Select: "home" or "iPhone 15 Pro Max"
   • Should show as connected (wireless)

3. ⚙️ VERIFY SIGNING SETTINGS:
   • Click "Runner" in project navigator (left panel)
   • Select "Runner" target
   • Go to "Signing & Capabilities" tab
   • Check:
     ☐ Bundle Identifier: com.tsh.admin
     ☐ Team: Khaleel Ahmed (3BJB4453J5)
     ☐ Automatically manage signing: ✅ CHECKED

4. 🔨 BUILD & RUN:
   • Click Play button (▶) or press Cmd+R
   • First build: 3-5 minutes
   • Watch build progress in status bar

🔐 IF SIGNING ISSUES:
====================

OPTION 1 - Add Apple Developer Account:
• Xcode → Settings → Accounts
• Click "+" → Add Apple ID
• Email: khaleel_ahm@yahoo.com
• Team: 3BJB4453J5

OPTION 2 - Use Personal Team (Quick Test):
• In Signing settings, select "Personal Team"
• This bypasses Apple Developer Account requirement

OPTION 3 - Temporary Bundle ID:
• Change Bundle ID to: com.khaleel.tshadmin
• This uses automatic provisioning

📱 ON YOUR IPHONE:
==================

AFTER SUCCESSFUL BUILD:
1. Look for "TSH Admin" app on home screen
2. If you see "Untrusted Developer":
   • Settings → General → VPN & Device Management
   • Find "Khaleel Ahmed" → Trust

TRUST DEVELOPER STEPS:
• Settings → General
• Scroll to "VPN & Device Management"
• Under "Developer App", tap "Khaleel Ahmed"
• Tap "Trust Khaleel Ahmed"
• Confirm "Trust"

🌐 BACKEND CONNECTION:
=====================
Your app will connect to: http://192.168.0.237:8000

MAKE SURE:
• Your backend server is running
• iPhone and backend are on same network
• Port 8000 is accessible

🧪 TESTING CHECKLIST:
=====================
☐ App launches without crashing
☐ Login screen appears
☐ Can connect to backend server
☐ Navigation works properly
☐ All modules load correctly

⚡ QUICK TROUBLESHOOTING:
========================

BUILD FAILS:
• Clean Build Folder (Cmd+Shift+K)
• Try different device/simulator
• Check signing settings

DEVICE NOT FOUND:
• Reconnect iPhone via USB
• Trust computer when prompted
• Enable WiFi debugging in Xcode

APP CRASHES ON LAUNCH:
• Check backend server is running
• Check network connectivity
• Review error logs in Xcode

SIGNING ERRORS:
• Use Personal Team for testing
• Or add proper Apple Developer Account

🎉 READY TO TEST!
=================

Your TSH Admin app is now ready for testing on your iPhone 15 Pro Max!

Build it in Xcode and let's see how it performs! 🚀📱
