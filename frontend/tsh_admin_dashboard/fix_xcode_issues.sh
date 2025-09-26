#!/bin/bash

echo "🔧 Fixing Xcode Project Settings and Dependencies"
echo "================================================"

PROJECT_DIR="/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard"
cd "$PROJECT_DIR"

echo "1. 🧹 Cleaning previous builds and dependencies..."
flutter clean
rm -rf ios/Pods
rm -rf ios/.symlinks  
rm -f ios/Podfile.lock
rm -rf build/
rm -rf .dart_tool/

echo "2. 📦 Getting Flutter dependencies..."
flutter pub get

echo "3. 🍎 Reinstalling CocoaPods..."
cd ios
pod deintegrate 2>/dev/null || true
pod install --repo-update

echo "4. 🔧 Updating Xcode project settings..."
cd "$PROJECT_DIR"

# Update iOS deployment target in project.pbxproj
sed -i '' 's/IPHONEOS_DEPLOYMENT_TARGET = [0-9.]*;/IPHONEOS_DEPLOYMENT_TARGET = 12.0;/g' ios/Runner.xcodeproj/project.pbxproj

# Ensure correct bundle identifier
sed -i '' 's/PRODUCT_BUNDLE_IDENTIFIER = .*/PRODUCT_BUNDLE_IDENTIFIER = com.tsh.admin;/g' ios/Runner.xcodeproj/project.pbxproj

# Set correct team ID
sed -i '' 's/DEVELOPMENT_TEAM = .*/DEVELOPMENT_TEAM = 3BJB4453J5;/g' ios/Runner.xcodeproj/project.pbxproj

# Enable automatic code signing
sed -i '' 's/CODE_SIGN_STYLE = .*/CODE_SIGN_STYLE = Automatic;/g' ios/Runner.xcodeproj/project.pbxproj

echo "5. ✅ Project configuration updated!"

echo ""
echo "📱 Updated Settings:"
echo "   - iOS Deployment Target: 12.0"
echo "   - Bundle Identifier: com.tsh.admin"
echo "   - Development Team: 3BJB4453J5"
echo "   - Code Sign Style: Automatic"

echo ""
echo "🚀 Next Steps:"
echo "1. Close and reopen Xcode"
echo "2. Clean Build Folder (Product → Clean Build Folder)"
echo "3. Try building: flutter build ios --device-id 00008130-0004310C1ABA001C"

echo ""
echo "Would you like to open Xcode now? (y/n)"
read -r open_xcode_response

if [[ $open_xcode_response =~ ^[Yy]$ ]]; then
    echo "🔧 Opening Xcode..."
    open ios/Runner.xcworkspace
fi
