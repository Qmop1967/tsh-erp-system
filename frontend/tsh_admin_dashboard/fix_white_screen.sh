#!/bin/bash

# Flutter iOS White Screen Fix Script
# Addresses common causes of white screen on iOS devices

echo "🔧 Diagnosing Flutter iOS White Screen Issue..."
echo ""

APP_DIR="/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard"
cd "$APP_DIR"

echo "❓ Common causes of white screen on iOS:"
echo "   1. Flutter engine not properly embedded"
echo "   2. Missing Flutter.framework"
echo "   3. App.framework issues"
echo "   4. Main.dart not found"
echo "   5. iOS deployment target mismatch"
echo "   6. Code signing issues preventing proper execution"
echo ""

echo "🔍 Checking current setup..."
echo ""

# Check if Flutter frameworks exist
echo "📱 Checking Flutter frameworks:"
if [ -d "ios/Flutter/Flutter.framework" ]; then
    echo "   ✅ Flutter.framework exists"
else
    echo "   ❌ Flutter.framework MISSING"
fi

if [ -d "ios/Flutter/App.framework" ]; then
    echo "   ✅ App.framework exists"
else
    echo "   ❌ App.framework MISSING"
fi

echo ""
echo "📋 Checking main.dart:"
if [ -f "lib/main.dart" ]; then
    echo "   ✅ lib/main.dart exists"
    echo "   First few lines:"
    head -5 lib/main.dart | sed 's/^/      /'
else
    echo "   ❌ lib/main.dart MISSING"
fi

echo ""
echo "🔧 COMPREHENSIVE FIX PROCEDURE:"
echo ""
echo "Step 1: Complete Clean & Rebuild"
echo "Step 2: Fix Flutter Framework Integration"
echo "Step 3: Verify iOS Configuration"
echo "Step 4: Test with Debug Console"
echo ""

read -p "Apply comprehensive fix? (Y/n): " apply_fix
if [[ $apply_fix =~ ^[Nn]$ ]]; then
    echo "Skipping fix. Check Xcode console for error details."
    exit 0
fi

echo ""
echo "🧹 Step 1: Complete Clean & Rebuild..."

# Deep clean everything
flutter clean
rm -rf .dart_tool/
rm -rf build/
rm -rf ios/Pods/
rm -rf ios/Podfile.lock
rm -rf ios/Flutter/Flutter.framework
rm -rf ios/Flutter/App.framework
rm -rf ios/.symlinks/

echo "✅ Cleaned all build artifacts"

echo ""
echo "📦 Step 2: Rebuilding Dependencies..."

# Get fresh dependencies
flutter pub get

# Rebuild iOS
cd ios
pod install --repo-update
cd ..

echo "✅ Dependencies rebuilt"

echo ""
echo "🛠️ Step 3: Rebuilding Flutter for iOS..."

# Build Flutter app specifically for iOS
flutter build ios --debug --no-codesign

echo "✅ Flutter iOS build complete"

echo ""
echo "📱 Step 4: Checking Framework Integration..."

# Check if frameworks were created
if [ -d "ios/Flutter/Flutter.framework" ]; then
    echo "✅ Flutter.framework created successfully"
else
    echo "❌ Flutter.framework still missing - this is the issue!"
    echo ""
    echo "🔧 MANUAL FIX REQUIRED:"
    echo "   Run: flutter precache --ios"
    echo "   Then: flutter build ios --debug"
    exit 1
fi

if [ -d "ios/Flutter/App.framework" ]; then
    echo "✅ App.framework created successfully"
else
    echo "❌ App.framework missing - regenerating..."
    flutter build ios --debug --no-codesign
fi

echo ""
echo "✅ COMPREHENSIVE FIX COMPLETE!"
echo ""
echo "📱 NEXT STEPS:"
echo ""
echo "1. Open Xcode: open ios/Runner.xcworkspace"
echo "2. Clean Build Folder (⌘⇧K)"
echo "3. In Xcode Product menu → Scheme → Edit Scheme"
echo "4. Under 'Run' → 'Arguments' tab"
echo "5. Add Environment Variable:"
echo "   Name: FLUTTER_ENGINE_LOGGING_LEVEL"
echo "   Value: debug"
echo "6. Build and Run (⌘R)"
echo ""
echo "🔍 DEBUGGING:"
echo "   - Watch Xcode Console for detailed error messages"
echo "   - Look for Flutter engine initialization errors"
echo "   - Check for any red error messages"
echo ""
echo "💡 If still white screen:"
echo "   - The console will show the exact error"
echo "   - Share the console output for further diagnosis"
