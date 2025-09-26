#!/bin/bash

echo "🔧 TSH Admin - Final Build Preparation"
echo "====================================="

cd "/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard"

echo "🛠️  Step 1: Fix Swift Version Conflict"
# Set all Swift versions to 5.0 in project file
sed -i '' 's/SWIFT_VERSION = "";/SWIFT_VERSION = 5.0;/g' ios/Runner.xcodeproj/project.pbxproj
sed -i '' 's/SWIFT_VERSION = ;/SWIFT_VERSION = 5.0;/g' ios/Runner.xcodeproj/project.pbxproj

echo "✅ Swift version fixed to 5.0 for all targets"

echo ""
echo "📱 Step 2: Update Team ID to Match Your Certificates"
# Update team ID to match your certificates (3BJB4453J5)
sed -i '' 's/DEVELOPMENT_TEAM = 38U844SAJ5;/DEVELOPMENT_TEAM = 3BJB4453J5;/g' ios/Runner.xcodeproj/project.pbxproj

echo "✅ Team ID updated to 3BJB4453J5 (from your certificates)"

echo ""
echo "🔄 Step 3: Final CocoaPods Installation"
cd ios
rm -rf Pods Podfile.lock .symlinks

# Try pod install with specific version
pod install --verbose

if [ $? -ne 0 ]; then
    echo "⚠️  Standard pod install failed, trying with repo update..."
    pod install --repo-update
fi

cd ..

echo ""
echo "🚀 Step 4: Ready for Xcode!"
echo ""
echo "✅ Configuration Summary:"
echo "   • Bundle ID: com.tsh.admin"
echo "   • Team ID: 3BJB4453J5 (matches your certificates)"
echo "   • Swift Version: 5.0 (unified)"
echo "   • iOS Target: 12.0"
echo "   • Signing: Automatic"
echo ""

echo "📱 Now in Xcode:"
echo "1. 🧹 Clean Build Folder (Cmd+Shift+K)"
echo "2. 🎯 Select iPhone 15 Pro Max from device dropdown"
echo "3. 🔐 Check Signing & Capabilities:"
echo "     • Team: Khaleel Ahmed (3BJB4453J5)"
echo "     • Bundle ID: com.tsh.admin" 
echo "     • Auto-manage signing: ✅ ON"
echo "4. 🚀 Build and Run (Cmd+R)"
echo ""

echo "💡 If Team Not Found:"
echo "   • Xcode → Settings → Accounts"
echo "   • Add Apple ID: khaleel_ahm@yahoo.com"
echo "   • Or use Personal Team for quick testing"
echo ""

echo "🎉 Ready to build! Good luck! 🚀"
