#!/bin/bash

echo "🔑 TSH Admin Dashboard - Complete Certificate Reset & Fresh Code Signing"
echo "====================================================================="

cd "/Users/khaleelal-mulla/TSH_ERP_System_Local/mobile/flutter_apps/admin_dashboard"

echo "🧹 Step 1: Cleaning All Build Artifacts"
echo "======================================"

# Complete clean
flutter clean
rm -rf ios/build
rm -rf ios/.symlinks
rm -rf ios/Pods
rm -rf ios/Podfile.lock
rm -rf build/
rm -rf .dart_tool/

echo ""
echo "🗑️ Step 2: Removing All iOS Development Certificates"
echo "=================================================="

echo "Listing current certificates..."
security find-identity -v -p codesigning

echo ""
echo "Removing iOS development certificates..."

# Delete all iOS development certificates
security delete-identity -Z "Apple Development" 2>/dev/null || true

# Delete all iPhone Developer certificates
security delete-identity -Z "iPhone Developer" 2>/dev/null || true

# Clear all provisioning profiles
echo "Removing provisioning profiles..."
rm -rf ~/Library/MobileDevice/Provisioning\ Profiles/* 2>/dev/null || true

echo ""
echo "🔄 Step 3: Reset Xcode Derived Data"
echo "=================================="

# Clear Xcode derived data
rm -rf ~/Library/Developer/Xcode/DerivedData/*

# Clear Xcode archives
rm -rf ~/Library/Developer/Xcode/Archives/*

echo ""
echo "📦 Step 4: Fresh Flutter Setup"
echo "=============================="

# Get fresh dependencies
flutter pub get

# Install iOS dependencies
cd ios
pod install --clean-install
cd ..

echo ""
echo "🍎 Step 5: Reset Xcode Project Settings"
echo "====================================="

# Remove any cached signing settings
rm -rf ios/Runner.xcworkspace/xcuserdata/
rm -rf ios/Runner.xcodeproj/xcuserdata/

echo ""
echo "🚀 Step 6: Launch with Fresh Signing"
echo "=================================="

echo "📱 Checking for connected devices..."
flutter devices

echo ""
echo "🔍 Looking for connected iPhone..."

# Check if iPhone is connected
IPHONE_DEVICE=$(flutter devices | grep "ios" | grep -v "simulator" | head -1)

if [ -z "$IPHONE_DEVICE" ]; then
    echo "❌ No iPhone found. Please connect your iPhone and run this script again."
    exit 1
else
    echo "✅ Found iPhone: $IPHONE_DEVICE"
    
    # Extract device ID
    DEVICE_ID=$(echo "$IPHONE_DEVICE" | grep -o '[A-F0-9-]\{36\}\|[0-9A-F]\{8\}-[0-9A-F]\{16\}' | head -1)
    
    echo "📱 Device ID: $DEVICE_ID"
    echo ""
    echo "🔑 Now launching - Xcode will prompt for fresh signing..."
    echo "   👤 When prompted, select your Apple ID"
    echo "   📝 Bundle ID will be automatically managed"
    echo "   ✅ Xcode will create fresh certificates"
    echo ""
    
    if [ -n "$DEVICE_ID" ]; then
        flutter run -d "$DEVICE_ID" --debug
    else
        flutter run --debug
    fi
fi

echo ""
echo "📋 What This Script Did:"
echo "======================"
echo "✅ Deleted all old iOS development certificates"
echo "✅ Removed all provisioning profiles"
echo "✅ Cleared Xcode caches and derived data"
echo "✅ Fresh Flutter and iOS dependencies"
echo "✅ Reset Xcode project signing settings"
echo ""
echo "🔑 On first run, Xcode will:"
echo "   1. Prompt you to select your Apple ID team"
echo "   2. Create fresh development certificates"
echo "   3. Generate new provisioning profiles"
echo "   4. Sign and install the app on your iPhone"
