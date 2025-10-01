#!/bin/bash

# iOS Plugin Fix Script for TSH Admin Dashboard
# This script fixes the "Module 'connectivity_plus' not found" error

set -e  # Exit on any error

APP_DIR="/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard"
CORE_DIR="/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_core_package"

echo "🔧 Starting iOS Plugin Fix for TSH Admin Dashboard..."

cd "$APP_DIR"

echo "📍 Current directory: $(pwd)"

# Step 1: Clean Flutter
echo "🧹 Cleaning Flutter cache and build artifacts..."
flutter clean
rm -rf .dart_tool/
rm -rf build/

# Step 2: Clean iOS specific files
echo "🍎 Cleaning iOS artifacts..."
cd ios
rm -rf Podfile.lock
rm -rf Pods/
rm -rf .symlinks/
rm -rf Flutter/App.framework
rm -rf Flutter/Flutter.framework
rm -rf Runner.xcworkspace
cd ..

# Step 3: Clean core package
echo "📦 Cleaning core package..."
cd "$CORE_DIR"
flutter clean
rm -rf .dart_tool/
cd "$APP_DIR"

# Step 4: Get dependencies for core package first
echo "📥 Getting core package dependencies..."
cd "$CORE_DIR"
flutter pub get
cd "$APP_DIR"

# Step 5: Get dependencies for main app
echo "📥 Getting main app dependencies..."
flutter pub get

# Step 6: Install CocoaPods
echo "🍎 Installing CocoaPods..."
cd ios

# Check if CocoaPods is installed
if ! command -v pod &> /dev/null; then
    echo "❗ CocoaPods not found. Installing..."
    sudo gem install cocoapods
fi

# Update CocoaPods repo
echo "🔄 Updating CocoaPods repository..."
pod repo update

# Install pods with verbose output
echo "📥 Installing iOS pods..."
pod install --verbose

cd ..

# Step 7: Check if the connectivity_plus module exists in Pods
echo "🔍 Checking if connectivity_plus pod was installed..."
if [ -d "ios/Pods/connectivity_plus" ]; then
    echo "✅ connectivity_plus pod found"
else
    echo "❌ connectivity_plus pod NOT found"
    
    # Try to manually add connectivity_plus to pubspec.yaml
    echo "🔧 Adding connectivity_plus directly to pubspec.yaml..."
    
    # Check if connectivity_plus is already in pubspec.yaml
    if ! grep -q "connectivity_plus:" pubspec.yaml; then
        sed -i '' '/tsh_core_package:/a\
  \
  # Network connectivity\
  connectivity_plus: ^5.0.1' pubspec.yaml
        
        echo "✅ Added connectivity_plus to pubspec.yaml"
        
        # Re-run pub get and pod install
        echo "📥 Re-running pub get..."
        flutter pub get
        
        echo "📥 Re-running pod install..."
        cd ios
        pod install --verbose
        cd ..
    fi
fi

# Step 8: Generate iOS plugin registrations
echo "🔧 Regenerating iOS plugin registrations..."
flutter packages get
flutter packages pub run build_runner build --delete-conflicting-outputs || true

# Step 9: Check the GeneratedPluginRegistrant file
echo "🔍 Checking GeneratedPluginRegistrant.m..."
if [ -f "ios/Runner/GeneratedPluginRegistrant.m" ]; then
    echo "✅ GeneratedPluginRegistrant.m exists"
    if grep -q "ConnectivityPlusPlugin" ios/Runner/GeneratedPluginRegistrant.m; then
        echo "✅ ConnectivityPlusPlugin found in GeneratedPluginRegistrant.m"
    else
        echo "❌ ConnectivityPlusPlugin NOT found in GeneratedPluginRegistrant.m"
    fi
else
    echo "❌ GeneratedPluginRegistrant.m NOT found"
fi

# Step 10: Build for iOS to verify everything works
echo "🔨 Building for iOS to verify fix..."
flutter build ios --no-codesign --debug

# Step 11: Final verification
echo "✅ iOS Plugin Fix Complete!"
echo ""
echo "📋 Summary:"
echo "- Flutter cache cleaned"
echo "- iOS artifacts cleaned" 
echo "- Dependencies re-fetched"
echo "- CocoaPods reinstalled"
echo "- iOS build completed"
echo ""
echo "🚀 You can now open the project in Xcode:"
echo "open ios/Runner.xcworkspace"
echo ""
echo "🎯 The connectivity_plus module should now be available in Xcode."
