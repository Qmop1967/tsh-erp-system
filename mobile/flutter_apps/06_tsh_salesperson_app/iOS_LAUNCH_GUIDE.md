# 📱 TSH Salesperson App - iOS Launch Guide

## ✅ Complete Solution for iOS Codesigning Issues

This guide provides a complete solution for all iOS codesigning and deployment issues.

---

## 🚀 Quick Start (3 Simple Steps)

### Step 1: Run the Fix Script
```bash
cd /Users/khaleelal-mulla/TSH_ERP_System_Local/tsh_salesperson_app
chmod +x fix_ios_complete.sh
./fix_ios_complete.sh
```

This will automatically fix:
- ✓ Bundle identifier (com.tsh.salesperson)
- ✓ Development team ID (3BJB4453J5)
- ✓ Xcode configuration files
- ✓ CocoaPods setup
- ✓ Clean and rebuild everything

### Step 2: Connect Your iPhone
- Connect iPhone via USB cable
- Unlock your iPhone
- Trust this computer (tap "Trust" when prompted)
- Enable Developer Mode:
  - iOS 16+: Settings > Privacy & Security > Developer Mode
  - Toggle ON and restart iPhone if needed

### Step 3: Launch the App
```bash
chmod +x launch_on_iphone.sh
./launch_on_iphone.sh
```

---

## 🔧 What Was Fixed?

### Issue 1: Wrong Bundle Identifier ❌
**Problem**: App was using `com.tsh.admin` (admin app's bundle ID)  
**Solution**: Changed to `com.tsh.salesperson` ✅

### Issue 2: Wrong Team ID ❌
**Problem**: Team ID was set to `38U844SAJ5` (incorrect)  
**Solution**: Updated to `3BJB4453J5` (your Apple Developer Team ID) ✅

### Issue 3: Duplicate xcconfig Includes ❌
**Problem**: Debug.xcconfig and Release.xcconfig had duplicate includes causing build errors  
**Solution**: Cleaned up to single conditional include per file ✅

### Issue 4: Broken Podfile Configuration ❌
**Problem**: Critical Flutter iOS build function was commented out  
**Solution**: Restored `flutter_additional_ios_build_settings` function ✅

### Issue 5: Stale Build Artifacts ❌
**Problem**: Old build files causing signing conflicts  
**Solution**: Complete clean of all build artifacts and cache ✅

---

## 📋 Manual Xcode Configuration (If Needed)

If you still encounter signing issues, configure manually in Xcode:

1. **Open Project in Xcode**
   ```bash
   open ios/Runner.xcworkspace
   ```

2. **Select Runner Target**
   - In the left sidebar, click on "Runner" (blue icon)
   - Ensure "Runner" target is selected in the center panel

3. **Configure Signing**
   - Go to "Signing & Capabilities" tab
   - ✓ Check "Automatically manage signing"
   - Select Team: **3BJB4453J5** or your team name
   - Verify Bundle Identifier: **com.tsh.salesperson**

4. **Build in Xcode** (to verify)
   - Product > Build (⌘B)
   - Should complete without errors

---

## 🎯 Build Modes

The launch script supports three build modes:

### 1. Debug Mode (Default)
- Hot reload enabled
- Debug symbols included
- Best for development
```bash
flutter run
```

### 2. Release Mode
- Optimized performance
- Smaller app size
- Production-ready
```bash
flutter run --release
```

### 3. Profile Mode
- Performance profiling enabled
- Good for testing performance
```bash
flutter run --profile
```

---

## 🔍 Troubleshooting

### Problem: "No devices found"
**Solutions**:
1. Check USB cable connection
2. Unlock iPhone and trust computer
3. Enable Developer Mode (Settings > Privacy & Security)
4. Restart iPhone and Mac
5. Try a different USB cable or port

### Problem: "Code signing failed"
**Solutions**:
1. Run `./fix_ios_complete.sh` again
2. Open Xcode and verify team selection
3. Ensure you're logged into Xcode with Apple ID
4. Check Apple Developer account is active

### Problem: "Provisioning profile doesn't match"
**Solutions**:
1. Delete derived data: `rm -rf ~/Library/Developer/Xcode/DerivedData/`
2. Re-run fix script: `./fix_ios_complete.sh`
3. In Xcode: Product > Clean Build Folder (⇧⌘K)
4. Rebuild: Product > Build (⌘B)

### Problem: "Pod installation failed"
**Solutions**:
```bash
cd ios
rm -rf Pods Podfile.lock
pod install --repo-update
cd ..
flutter clean
flutter pub get
```

### Problem: "App installs but crashes immediately"
**Solutions**:
1. Check Xcode console for crash logs
2. Try debug mode instead of release: `flutter run`
3. Verify Info.plist has correct permissions
4. Check Flutter doctor: `flutter doctor -v`

---

## 📱 Testing on Simulator (Alternative)

If you don't have a physical iPhone available:

```bash
# List available simulators
xcrun simctl list devices available

# Open Simulator
open -a Simulator

# Run app on simulator
flutter run
```

---

## ✅ Verification Checklist

After running the fix script, verify:

- [ ] `flutter doctor` shows no critical issues
- [ ] Bundle ID is `com.tsh.salesperson`
- [ ] Team ID is `3BJB4453J5`
- [ ] CocoaPods installed successfully
- [ ] iPhone is connected and trusted
- [ ] Developer Mode is enabled on iPhone
- [ ] Xcode shows no signing errors

---

## 🆘 Still Having Issues?

1. **Check Flutter Doctor**
   ```bash
   flutter doctor -v
   ```

2. **Check Xcode Logs**
   - Open: ios/Runner.xcworkspace in Xcode
   - Try to build (⌘B)
   - Check error messages in the build log

3. **Full Reset** (last resort)
   ```bash
   ./fix_ios_complete.sh
   rm -rf ~/Library/Developer/Xcode/DerivedData/
   flutter clean
   flutter pub get
   cd ios && pod install && cd ..
   ```

4. **Contact Information**
   - Include the specific error message
   - Include output from `flutter doctor -v`
   - Include Xcode version: `xcodebuild -version`

---

## 📚 Additional Resources

- [Flutter iOS Setup](https://docs.flutter.dev/get-started/install/macos#ios-setup)
- [Apple Code Signing Guide](https://developer.apple.com/support/code-signing/)
- [CocoaPods Troubleshooting](https://guides.cocoapods.org/using/troubleshooting)

---

## 📝 Notes

- **Bundle ID**: `com.tsh.salesperson` (specific to this app)
- **Team ID**: `3BJB4453J5` (your Apple Developer account)
- **Minimum iOS Version**: 13.0
- **Supported Devices**: iPhone only (can be extended to iPad)

---

**Last Updated**: September 30, 2025  
**App Version**: 1.0.0+1

