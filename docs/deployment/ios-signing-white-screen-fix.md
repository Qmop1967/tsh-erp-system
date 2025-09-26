# iOS Signing & White Screen Fix Guide

## Current Status
The Team ID has been successfully updated to `3BJB4453J5`, but Xcode needs to be configured with your Apple Developer account.

## Step 1: Configure Apple Developer Account in Xcode

1. **Open Xcode** (should already be open via the Runner.xcworkspace)

2. **Add your Apple Developer Account:**
   - Go to `Xcode > Settings/Preferences` (or press `Cmd + ,`)
   - Click on the `Accounts` tab
   - Click the `+` button and select `Apple ID`
   - Sign in with your Apple Developer account: `khaleel_ahm@yahoo.com`
   - After signing in, you should see your Team ID `3BJB4453J5` listed

## Step 2: Configure Code Signing

1. **In the open Xcode project:**
   - Select the `Runner` project in the navigator (top-level blue icon)
   - Select the `Runner` target under the project
   - Go to the `Signing & Capabilities` tab

2. **Configure Signing:**
   - Check `Automatically manage signing`
   - Select your team from the dropdown: `Khaleel Ahmed (3BJB4453J5)`
   - Verify the Bundle Identifier is: `com.tsh.admin`
   - Ensure the provisioning profile shows as valid

3. **For the RunnerTests target (if present):**
   - Select the `RunnerTests` target
   - Configure the same signing settings

## Step 3: Download and Install Provisioning Profiles

1. **Go to Apple Developer Portal:**
   - Visit: https://developer.apple.com/account/resources/profiles/list
   - Download the development profile: `TSH Admin Dev Profile`
   - Double-click the downloaded `.mobileprovision` file to install it

## Step 4: Build and Test

### Option A: Build via Xcode (Recommended for troubleshooting)
1. In Xcode: `Product > Build` (or press `Cmd + B`)
2. If successful: `Product > Run` (or press `Cmd + R`)

### Option B: Build via Flutter Command
```bash
cd "/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard"
flutter run -d 00008130-0004310C1ABA001C --debug
```

## Step 5: Resolving White Screen Issues

If the app builds successfully but shows a white screen, try these solutions:

### Solution 1: Check Debug Console
1. In Xcode, open the debug console (`View > Debug Area > Activate Console`)
2. Look for any error messages or crashes
3. Common issues:
   - Flutter engine not initializing
   - Missing frameworks
   - Plugin initialization errors

### Solution 2: Verify Framework Installation
```bash
cd "/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard"
ls -la ios/Flutter/
# Should contain Flutter.framework and App.framework after successful build
```

### Solution 3: Test with Minimal App
If still getting white screen, test with a minimal Flutter app:

1. **Create a simple test app:**
```dart
// Create: lib/main_simple.dart
import 'package:flutter/material.dart';

void main() {
  runApp(SimpleTestApp());
}

class SimpleTestApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Simple Test',
      home: Scaffold(
        appBar: AppBar(title: Text('Simple Test')),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text('Hello Flutter!', style: TextStyle(fontSize: 24)),
              SizedBox(height: 20),
              ElevatedButton(
                onPressed: () {
                  print('Button pressed!');
                },
                child: Text('Test Button'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
```

2. **Run the simple test:**
```bash
flutter run -d 00008130-0004310C1ABA001C lib/main_simple.dart
```

### Solution 4: Check App Delegate
Verify the iOS App Delegate is properly configured:
- File: `ios/Runner/AppDelegate.swift`
- Should contain proper Flutter initialization code

### Solution 5: Plugin Issues
If plugins are causing issues:
```bash
# Clean and reinstall all plugins
flutter clean
flutter pub get
cd ios && pod deintegrate && pod install
```

## Common Error Solutions

### Error: "No Account for Team"
- Add your Apple ID in Xcode Preferences > Accounts
- Download certificates from Apple Developer Portal

### Error: "No profiles found"
- Download provisioning profiles from Apple Developer Portal
- Install by double-clicking the .mobileprovision files

### White Screen on Device
- Check Xcode console for errors
- Verify frameworks are generated in `ios/Flutter/`
- Test with minimal app to isolate the issue

## Production Build Commands

Once development build works:

```bash
# For App Store distribution
flutter build ios --release
```

Then archive in Xcode for App Store submission.

## Next Steps

1. Follow Step 1-2 to configure Xcode signing
2. Build the app using Xcode first
3. If successful, try Flutter run command
4. If white screen persists, test with the minimal app
5. Check debug console for specific error messages

The key issue was the Team ID mismatch - this has been fixed. The remaining issues are likely signing configuration and potentially plugin initialization problems.
