🍎 TSH Admin App - Xcode Setup Checklist
=========================================

📱 Current Configuration Status:
✅ Bundle Identifier: com.tsh.admin (matches Apple Developer Account)
⚠️  Team ID: Needs to be verified/updated to 3BJB4453J5
✅ Xcode workspace is now open

🔧 In Xcode - VERIFY THESE SETTINGS:

1. 🎯 SELECT RUNNER TARGET:
   • In project navigator (left panel), click "Runner"
   • Click on "Runner" target (under TARGETS)

2. ⚙️  SIGNING & CAPABILITIES TAB:
   • Bundle Identifier: com.tsh.admin ✅
   • Team: Should show "Khaleel Ahmed (3BJB4453J5)"
   • If not showing correct team:
     - Click team dropdown
     - Select your Apple Developer Account team
   • ✅ Check "Automatically manage signing"

3. 📱 DEVICE SELECTION:
   • Click device dropdown next to play button
   • Select your iPhone 15 Pro Max
   • Device should show as connected (wired or WiFi)

4. 🚀 BUILD & RUN:
   • Click Play button (▶) or Cmd+R
   • First build may take several minutes
   • Watch for any signing errors in build output

🔍 If You See Signing Errors:

Option A - Add Apple Developer Account:
• Xcode → Settings → Accounts
• Add your Apple ID: khaleel_ahm@yahoo.com
• Download Manual Profiles if needed

Option B - Use Personal Team (Quick Test):
• In Signing settings, select "Personal Team"
• This will work for testing but not App Store

📱 On Your iPhone:
• After successful build, look for "TSH Admin" app
• If "Untrusted Developer" appears:
  Settings → General → VPN & Device Management
  → Trust "Khaleel Ahmed"

🌐 Backend Connection:
Your app will connect to: http://192.168.0.237:8000
(Make sure your backend server is running!)

💡 Quick Commands (if needed):
• Clean Build: Cmd+Shift+K
• Build: Cmd+B  
• Run: Cmd+R

🚀 Ready to launch! Try building in Xcode now.
