#!/bin/bash

echo "🔥 AGGRESSIVE PIF Transfer Session Fix"
echo "====================================="

PROJECT_DIR="/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard"
cd "$PROJECT_DIR"

echo "1. 🛑 Closing Xcode (if running)..."
killall Xcode 2>/dev/null || echo "Xcode was not running"
sleep 2

echo "2. 🧹 Deep cleaning Xcode derived data..."
rm -rf ~/Library/Developer/Xcode/DerivedData/*
rm -rf ~/Library/Caches/com.apple.dt.Xcode/*
rm -rf ~/Library/Developer/Xcode/iOS\ DeviceSupport/*

echo "3. 🗑️ Removing all project build artifacts..."
rm -rf build/
rm -rf .dart_tool/
rm -rf ios/build/
rm -rf ios/.symlinks/
rm -rf ios/Flutter/ephemeral/
rm -rf ios/Pods/
rm -f ios/Podfile.lock
rm -rf ios/Runner.xcworkspace/xcuserdata/

echo "4. 📦 Complete Flutter clean..."
flutter clean

echo "5. 🔄 Regenerating Flutter configuration..."
flutter pub get
flutter precache --ios

echo "6. 🍎 Reinstalling CocoaPods with cache clear..."
cd ios
pod cache clean --all
pod deintegrate 2>/dev/null || true
pod install --repo-update --clean-install

echo "7. 🔧 Fixing Xcode project settings..."
cd "$PROJECT_DIR"

# Fix deployment target
sed -i '' 's/IPHONEOS_DEPLOYMENT_TARGET = [^;]*/IPHONEOS_DEPLOYMENT_TARGET = 12.0/g' ios/Runner.xcodeproj/project.pbxproj

# Fix bundle identifier
sed -i '' 's/PRODUCT_BUNDLE_IDENTIFIER = [^;]*/PRODUCT_BUNDLE_IDENTIFIER = com.tsh.admin/g' ios/Runner.xcodeproj/project.pbxproj

# Fix team ID
sed -i '' 's/DEVELOPMENT_TEAM = [^;]*/DEVELOPMENT_TEAM = 3BJB4453J5/g' ios/Runner.xcodeproj/project.pbxproj

# Enable automatic code signing
sed -i '' 's/CODE_SIGN_STYLE = [^;]*/CODE_SIGN_STYLE = Automatic/g' ios/Runner.xcodeproj/project.pbxproj

# Fix code sign identity
sed -i '' 's/"CODE_SIGN_IDENTITY\[sdk=iphoneos\*\]" = [^;]*/"CODE_SIGN_IDENTITY[sdk=iphoneos*]" = "iPhone Developer"/g' ios/Runner.xcodeproj/project.pbxproj

echo "8. 🧪 Testing Flutter framework generation..."
flutter build ios --debug --no-codesign

echo ""
echo "✅ AGGRESSIVE FIX COMPLETE!"
echo ""
echo "🚀 Next steps:"
echo "1. Open Xcode: open ios/Runner.xcworkspace"
echo "2. In Xcode: Product → Clean Build Folder (⇧⌘K)"
echo "3. Try building in Xcode or with: flutter run --device-id 00008130-0004310C1ABA001C"

echo ""
echo "Would you like to open Xcode now? (y/n)"
read -r response

if [[ $response =~ ^[Yy]$ ]]; then
    echo "🔧 Opening Xcode..."
    open ios/Runner.xcworkspace
fi
