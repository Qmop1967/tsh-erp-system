# TSH Admin Dashboard - iPhone Deployment Guide

## ✅ What We Just Did
1. ✅ Fixed the core package dependency issue  
2. ✅ Cleaned and updated Flutter dependencies
3. ✅ Installed iOS CocoaPods dependencies
4. ✅ Opened Xcode with your admin dashboard project

## 📱 Next Steps in Xcode

### 1. Wait for Project to Load
- Xcode is currently opening your project
- Wait for indexing and loading to complete (may take 1-2 minutes)

### 2. Connect Your iPhone
- Connect your iPhone to your Mac using a USB cable
- Unlock your iPhone
- If prompted "Trust This Computer?" → Tap **Trust**

### 3. Select Your iPhone as Target
- In Xcode, at the top-left, you'll see a device selector
- Click it and select your iPhone from the list
- If your iPhone doesn't appear, go to Window → Devices and Simulators

### 4. Configure Code Signing (If Needed)
- In Xcode Navigator (left panel), click on **Runner** (blue icon at top)
- Select **Runner** under TARGETS
- Go to **Signing & Capabilities** tab
- Under **Team**, select your Apple Developer account
- If you don't have one, you can use a free Apple ID for development

### 5. Build and Run
- Click the **Play button (▶)** in the top-left of Xcode
- This will build the app and install it on your iPhone
- First build may take several minutes

## 🔧 If You Encounter Issues

### Code Signing Issues
```
Error: "No signing certificate found"
```
**Solution:**
1. Go to Xcode → Preferences → Accounts
2. Add your Apple ID if not already added
3. In Signing & Capabilities, select your team
4. Change Bundle Identifier if needed (e.g., com.yourname.tshadmin)

### Device Not Found
```
"iPhone is not available"
```
**Solution:**
1. Disconnect and reconnect iPhone
2. Check iPhone: Settings → General → Device Management
3. Enable Developer Mode: Settings → Privacy & Security → Developer Mode

### Network/API Issues
- The admin dashboard may try to connect to your backend
- Make sure your backend server is running
- Update API endpoints from localhost to your Mac's IP address if needed

## 🚀 Alternative: Flutter Command Line

If Xcode gives you trouble, you can also deploy directly using Flutter:

```bash
# Go to project directory
cd "/Users/khaleelal-mulla/TSH_ERP_System_Local/mobile/flutter_apps/admin_dashboard"

# List available devices
flutter devices

# Run on your iPhone (replace DEVICE_ID with your iPhone's ID)
flutter run -d [DEVICE_ID]

# Or just run (Flutter will ask which device to use)
flutter run
```

## 📋 Success Indicators

✅ **App builds successfully** - No red errors in Xcode  
✅ **App installs on iPhone** - You'll see "TSH Admin" icon on home screen  
✅ **App launches** - Opens without crashing  
✅ **UI displays** - Admin dashboard interface appears  

## 🔄 Hot Reload During Development

Once the app is running:
- Make changes to Dart code
- Press `r` in terminal for hot reload (fast)
- Press `R` in terminal for hot restart (slower but more complete)
- Changes will appear instantly on your iPhone

## 📞 Need Help?

If you encounter any specific errors, note down the exact error message and we can troubleshoot further!
