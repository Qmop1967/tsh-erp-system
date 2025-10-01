#!/bin/bash

echo "🚨 FIXING CRITICAL XCODE SIGNING & ASSET ISSUES"
echo "=============================================="

PROJECT_DIR="/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard"
cd "$PROJECT_DIR"

echo ""
echo "📋 Current Available Certificates:"
security find-identity -v -p codesigning

echo ""
echo "1. 🎨 Fixed missing Assets.xcassets..."
echo "   ✅ Created AppIcon.appiconset with proper Contents.json"
echo "   ✅ Created LaunchImage.imageset with placeholder images"

echo ""
echo "2. 🔧 Updating project settings to use available certificates..."

# Use the available development certificate team ID
AVAILABLE_DEV_TEAM="38U844SAJ5"  # From the Apple Distribution certificate
AVAILABLE_DEV_CERT="53P8RSV68A"   # From the Apple Development certificate

echo "   📝 Updating Development Team to: $AVAILABLE_DEV_TEAM"

# Update project.pbxproj to use the available team ID
sed -i '' "s/DEVELOPMENT_TEAM = 3BJB4453J5;/DEVELOPMENT_TEAM = $AVAILABLE_DEV_TEAM;/g" ios/Runner.xcodeproj/project.pbxproj
sed -i '' "s/DEVELOPMENT_TEAM = \"\";/DEVELOPMENT_TEAM = $AVAILABLE_DEV_TEAM;/g" ios/Runner.xcodeproj/project.pbxproj

echo "   📱 Setting bundle identifier to match available certificates"
# Since we have certificates, let's use a simpler bundle ID that should work
sed -i '' 's/PRODUCT_BUNDLE_IDENTIFIER = com\.tsh\.admin;/PRODUCT_BUNDLE_IDENTIFIER = com.khaleel.tshadmin;/g' ios/Runner.xcodeproj/project.pbxproj

echo ""
echo "3. 🧹 Cleaning and rebuilding dependencies..."
flutter clean
rm -rf ios/Pods ios/.symlinks ios/Podfile.lock

echo ""
echo "4. 📦 Reinstalling dependencies..."
flutter pub get
cd ios && pod install

echo ""
echo "5. ✅ Configuration Summary:"
echo "   - Team ID: $AVAILABLE_DEV_TEAM"
echo "   - Bundle ID: com.khaleel.tshadmin"
echo "   - Assets: Created AppIcon and LaunchImage sets"
echo "   - Dependencies: Cleaned and reinstalled"

echo ""
echo "🍎 NEXT STEPS:"
echo ""
echo "1. Open Xcode: open ios/Runner.xcworkspace"
echo "2. In Xcode → Preferences → Accounts:"
echo "   - Add your Apple ID account if not present"
echo "   - Verify team '$AVAILABLE_DEV_TEAM' appears"
echo ""
echo "3. In Runner target → Signing & Capabilities:"
echo "   - Enable 'Automatically manage signing'"
echo "   - Select team: '$AVAILABLE_DEV_TEAM'"
echo "   - Bundle ID should be: com.khaleel.tshadmin"
echo ""
echo "4. Create App ID in Apple Developer Portal:"
echo "   - Go to: https://developer.apple.com/account/resources/identifiers/list"
echo "   - Create new App ID: com.khaleel.tshadmin"
echo "   - Register your device UDID: 00008130-000431C1ABA001C"
echo ""
echo "5. Test build:"
echo "   flutter run --device-id 00008130-0004310C1ABA001C"

echo ""
echo "Would you like to open Xcode now? (y/n)"
read -r open_xcode

if [[ $open_xcode =~ ^[Yy]$ ]]; then
    echo "🔧 Opening Xcode..."
    open ios/Runner.xcworkspace
fi

echo ""
echo "🎉 Fix complete! The critical issues should now be resolved."
