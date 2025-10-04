# iPhone Setup & Troubleshooting Guide

## 🎯 Goal
Run the TSH Salesperson app on your physical iPhone device.

---

## ✅ What's Already Done
- ✅ iOS build errors fixed (permission_handler downgraded to v11.3.1)
- ✅ All permissions added to Info.plist
- ✅ CocoaPods installed successfully
- ✅ Custom app icon generated (TSH SALES logo)
- ✅ Flutter project cleaned and dependencies updated
- ✅ App ready to deploy

---

## 📱 Step-by-Step iPhone Setup

### Step 1: Enable Developer Mode on iPhone

1. **Connect iPhone to Mac via USB cable**
2. **Trust the Mac on iPhone** (popup will appear)
3. **Enable Developer Mode:**
   - Go to **Settings** > **Privacy & Security** > **Developer Mode**
   - Toggle **ON**
   - Restart iPhone when prompted

### Step 2: Verify iPhone Connection

```bash
# Check if iPhone is detected
flutter devices

# You should see something like:
# iPhone 15 Pro (mobile) • 00008030-XXXXXXXXXXXXX • ios • iOS 17.2.1
```

**If iPhone is NOT detected:**
- Make sure USB cable supports data transfer (not just charging)
- Try a different USB port or cable
- Unplug and replug the iPhone
- Restart both Mac and iPhone
- Check that iTunes/Finder recognizes the iPhone

### Step 3: Configure Code Signing in Xcode

```bash
cd /Users/khaleelal-mulla/TSH_ERP_System_Local/tsh_salesperson_app/ios
open Runner.xcworkspace
```

In Xcode:
1. **Select "Runner" project** in the left navigator
2. **Select "Runner" target** (under Targets)
3. **Go to "Signing & Capabilities" tab**
4. **Check "Automatically manage signing"**
5. **Select your Team:**
   - If you have an Apple Developer account: select your team
   - If you don't: add your Apple ID in Xcode > Settings > Accounts
6. **Bundle Identifier:**
   - Should be: `com.tsh.salesperson` or similar
   - Make it unique if there's a conflict
7. **Wait for provisioning profile to be created**
   - You'll see "Provisioning profile created/updated" message

### Step 4: Run the App

#### Option A: From Command Line (Recommended)
```bash
cd /Users/khaleelal-mulla/TSH_ERP_System_Local/tsh_salesperson_app

# List available devices
flutter devices

# Run in debug mode (faster, hot reload enabled)
flutter run -d <your-iphone-device-id>

# OR run in release mode (better performance)
flutter run --release -d <your-iphone-device-id>
```

#### Option B: From Xcode
1. Open `Runner.xcworkspace` in Xcode
2. Select your iPhone from device dropdown (top left, next to "Runner")
3. Click the **Run** button (▶️)
4. Wait for build and installation

### Step 5: Trust Developer Certificate

**First time running the app:**
1. The app will install but may not open automatically
2. Go to **Settings** > **General** > **VPN & Device Management**
3. Under "Developer App", find your Apple ID certificate
4. Tap on it
5. Tap **"Trust [Your Apple ID]"**
6. Confirm by tapping **Trust** again
7. Go back to home screen and open the TSH Salesperson app

---

## 🔧 Troubleshooting

### Issue 1: "iPhone is not available"
**Symptoms:** iPhone appears in `flutter devices` but with "unavailable" status

**Solutions:**
- Make sure iPhone is unlocked
- Trust the Mac on iPhone (Settings > General > Transfer or Reset iPhone > Reset Location & Privacy)
- Enable Developer Mode (Settings > Privacy & Security > Developer Mode)
- Restart iPhone and Mac

### Issue 2: "Code signing error"
**Symptoms:** Build fails with "No valid code signing certificates found"

**Solutions:**
- Open Xcode > Settings > Accounts
- Add your Apple ID if not already added
- Download certificates (click on account, then "Download Manual Profiles")
- In project settings, select your team under "Signing & Capabilities"
- Try "Automatically manage signing"

### Issue 3: "Failed to install app"
**Symptoms:** Build succeeds but installation fails

**Solutions:**
- Delete the app from iPhone if already installed
- Restart iPhone
- Free up storage on iPhone (need ~200MB free)
- Try a different USB cable/port
- Run: `flutter clean && flutter pub get && cd ios && pod install`

### Issue 4: "Could not find iPhone"
**Symptoms:** `flutter devices` shows no iPhone

**Solutions:**
```bash
# Check USB connection
system_profiler SPUSBDataType | grep iPhone

# Restart Flutter daemon
flutter devices -v

# Check Xcode can see iPhone
xcrun xctrace list devices

# Pair iPhone with Mac (for wireless debugging later)
xcrun devicectl list devices

# Reset location & privacy on iPhone
# Settings > General > Transfer or Reset iPhone > Reset Location & Privacy
```

### Issue 5: "Build failed with exit code 65"
**Symptoms:** Xcode build fails during compilation

**Solutions:**
```bash
# Clean everything
cd /Users/khaleelal-mulla/TSH_ERP_System_Local/tsh_salesperson_app
flutter clean
rm -rf ios/Pods ios/Podfile.lock ios/.symlinks ios/Flutter/Flutter.framework
cd ios && pod install --repo-update && cd ..

# Try building from Xcode for better error messages
open ios/Runner.xcworkspace
# Then click Product > Clean Build Folder (Shift + Cmd + K)
# Then click Product > Build (Cmd + B)
```

### Issue 6: "Permission denied" errors
**Symptoms:** Can't write to iOS directories

**Solutions:**
```bash
# Fix permissions
sudo chown -R $(whoami) ~/Library/Developer
sudo chown -R $(whoami) /Users/khaleelal-mulla/TSH_ERP_System_Local/tsh_salesperson_app/ios
```

---

## 🔍 Verification Commands

```bash
# Check Flutter installation
flutter doctor -v

# Check iOS toolchain
xcodebuild -version

# Check connected devices
flutter devices -v

# Check CocoaPods
pod --version
cd ios && pod outdated

# Check provisioning profiles
xcrun devicectl list devices

# Check code signing identities
security find-identity -v -p codesigning
```

---

## 📋 Pre-Flight Checklist

Before running `flutter run`:
- [ ] iPhone connected via USB
- [ ] iPhone is unlocked
- [ ] Developer Mode enabled on iPhone
- [ ] Mac is trusted on iPhone
- [ ] Xcode installed (latest version)
- [ ] Apple ID added to Xcode
- [ ] Code signing configured in Xcode
- [ ] `flutter doctor` shows no iOS errors
- [ ] `flutter devices` shows your iPhone
- [ ] CocoaPods installed (`pod --version`)
- [ ] All pods installed (`cd ios && pod install`)

---

## 🚀 Quick Commands

```bash
# One-line setup (run from app directory)
cd /Users/khaleelal-mulla/TSH_ERP_System_Local/tsh_salesperson_app && flutter clean && flutter pub get && cd ios && pod install && cd .. && flutter devices

# Run app (after setup)
flutter run

# Run in release mode for best performance
flutter run --release

# Run with verbose output for debugging
flutter run -v

# Hot reload (while app is running)
# Press 'r' in terminal

# Hot restart (while app is running)
# Press 'R' in terminal

# Quit app
# Press 'q' in terminal
```

---

## 🎨 About the App Icon

The TSH Salesperson app now has a custom icon:
- **Design:** Blue background with white circle containing "TSH SALES" text
- **Size:** 1024x1024 pixels
- **Location:** `assets/icons/app_icon.png`
- **Platforms:** iOS, Android, Web

The icon was generated using `flutter_launcher_icons` package and is automatically applied when you build the app.

---

## 📱 Expected Result

After successful installation and run:
1. **App icon** appears on iPhone home screen with TSH logo
2. **App launches** showing the TSH Salesperson splash screen
3. **Home page** loads with bottom navigation:
   - Dashboard (Main & Leaderboard tabs)
   - POS (Point of Sale with demo products)
   - Customers
   - Orders
   - Menu
4. **POS page** shows:
   - Client selection at top
   - Search bar
   - Category tabs (All, Electronics, Accessories, etc.)
   - Product grid with demo items
   - Add to cart functionality
   - Cart icon with badge
   - Cart bottom sheet

---

## 🆘 Still Having Issues?

### Option 1: Build from Xcode (Best for debugging)
```bash
cd /Users/khaleelal-mulla/TSH_ERP_System_Local/tsh_salesperson_app/ios
open Runner.xcworkspace
```
- Select your iPhone in device dropdown
- Click Run (▶️)
- Check error messages in Xcode console

### Option 2: Use Simulator (For quick testing)
```bash
# Open iOS simulator
open -a Simulator

# List available simulators
xcrun simctl list devices

# Run on simulator
flutter run -d "iPhone 15 Pro"
```

### Option 3: Wireless Debugging (After initial USB setup)
```bash
# Pair iPhone (iPhone and Mac must be on same WiFi)
xcrun devicectl list devices

# Run wirelessly
flutter run -d <wireless-device-id>
```

---

## 📚 Additional Resources

- [Flutter iOS Setup](https://docs.flutter.dev/get-started/install/macos#ios-setup)
- [Xcode Code Signing](https://developer.apple.com/support/code-signing/)
- [CocoaPods Troubleshooting](https://guides.cocoapods.org/using/troubleshooting)
- [Flutter DevTools](https://docs.flutter.dev/development/tools/devtools)

---

## ✅ Success Indicators

You'll know everything is working when:
- ✅ `flutter devices` shows your iPhone as available
- ✅ `flutter run` builds without errors
- ✅ App installs on iPhone
- ✅ TSH icon appears on home screen
- ✅ App opens and shows dashboard
- ✅ POS page loads with demo products
- ✅ Navigation works between all pages
- ✅ Add to cart functionality works

---

**Good luck! 🚀 The app is ready to go!**

If you encounter any issues not covered here, check the Xcode console output for specific error messages.
