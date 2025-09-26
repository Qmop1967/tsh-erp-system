#!/bin/bash

echo "🔧 TSH Admin - Complete iOS Build Fix"
echo "===================================="

PROJECT_PATH="/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard"
cd "$PROJECT_PATH"

echo "📋 Issues Detected from Screenshot:"
echo "❌ Build Failed"
echo "❌ Signing Configuration Problems"
echo "⚠️  iOS Deployment Target Warnings"
echo "❌ Team/Certificate Issues"
echo ""

echo "🧹 Step 1: Complete Clean Build"
echo "Cleaning all build artifacts..."
flutter clean
rm -rf ios/Pods
rm -rf ios/.symlinks
rm -rf ios/Flutter/Flutter.framework
rm -rf ios/Flutter/Flutter.podspec
rm -rf build/
rm -f ios/Podfile.lock

echo ""
echo "📦 Step 2: Reinstall Dependencies"
flutter pub get

echo ""
echo "🎯 Step 3: Fix iOS Configuration"

# Update iOS deployment target in project settings
echo "Updating IPHONEOS_DEPLOYMENT_TARGET to 12.0..."
if grep -q "IPHONEOS_DEPLOYMENT_TARGET" ios/Runner.xcodeproj/project.pbxproj; then
    sed -i '' 's/IPHONEOS_DEPLOYMENT_TARGET = [^;]*/IPHONEOS_DEPLOYMENT_TARGET = 12.0/g' ios/Runner.xcodeproj/project.pbxproj
else
    echo "⚠️  IPHONEOS_DEPLOYMENT_TARGET not found in project file"
fi

# Fix provisioning profile settings
echo "Fixing provisioning profile settings..."
sed -i '' 's/PROVISIONING_PROFILE_SPECIFIER = "[^"]*"/PROVISIONING_PROFILE_SPECIFIER = ""/g' ios/Runner.xcodeproj/project.pbxproj
sed -i '' 's/CODE_SIGN_STYLE = Manual/CODE_SIGN_STYLE = Automatic/g' ios/Runner.xcodeproj/project.pbxproj

echo ""
echo "🔄 Step 4: Reinstall CocoaPods"
cd ios
pod deintegrate 2>/dev/null || echo "No previous pods to deintegrate"
pod install

if [ $? -ne 0 ]; then
    echo "❌ Pod install failed. Trying alternative approach..."
    rm -rf Pods Podfile.lock .symlinks
    flutter clean
    flutter pub get
    pod install --repo-update
fi

cd ..

echo ""
echo "✅ Step 5: Verification"
echo "Checking project configuration..."

# Check current bundle ID
BUNDLE_ID=$(grep -o 'PRODUCT_BUNDLE_IDENTIFIER = [^;]*' ios/Runner.xcodeproj/project.pbxproj | head -1 | cut -d'=' -f2 | tr -d ' ;')
echo "Bundle Identifier: $BUNDLE_ID"

# Check team ID
TEAM_ID=$(grep -o 'DEVELOPMENT_TEAM = [^;]*' ios/Runner.xcodeproj/project.pbxproj | head -1 | cut -d'=' -f2 | tr -d ' ;')
echo "Development Team: $TEAM_ID"

# Check deployment target
DEPLOYMENT_TARGET=$(grep -o 'IPHONEOS_DEPLOYMENT_TARGET = [^;]*' ios/Runner.xcodeproj/project.pbxproj | head -1 | cut -d'=' -f2 | tr -d ' ;')
echo "iOS Deployment Target: $DEPLOYMENT_TARGET"

echo ""
echo "🚀 Step 6: Ready for Xcode Build"
echo ""
echo "Now in Xcode:"
echo "1. 📱 Select your iPhone 15 Pro Max from device dropdown"
echo "2. 🔧 Go to Runner → Signing & Capabilities"
echo "3. ✅ Verify settings:"
echo "   • Bundle Identifier: com.tsh.admin"
echo "   • Team: Khaleel Ahmed (3BJB4453J5)"  
echo "   • Automatically manage signing: ✅ CHECKED"
echo "4. 🔨 Clean Build Folder (Cmd+Shift+K)"
echo "5. 🚀 Build and Run (Cmd+R)"
echo ""

echo "🔐 If Signing Still Fails:"
echo ""
echo "Option 1 - Add Apple Developer Account:"
echo "• Xcode → Settings → Accounts"
echo "• Add Apple ID: khaleel_ahm@yahoo.com"
echo "• Select Team: 3BJB4453J5"
echo ""
echo "Option 2 - Use Personal Team (Quick Test):"
echo "• In Signing settings, change team to 'Personal Team'"
echo "• Change bundle ID to: com.khaleel.tshadmin"
echo ""
echo "Option 3 - Manual Certificate Installation:"
echo "• Download certificates from Apple Developer Portal"
echo "• Install in Keychain Access"
echo "• Download provisioning profiles"
echo ""

echo "📱 Testing Device:"
echo "• iPhone 15 Pro Max"
echo "• UDID: 00008130-000431C1ABA001C" 
echo "• Must be registered in Apple Developer Portal"
echo ""

echo "🌐 Backend Connection:"
echo "• App connects to: http://192.168.0.237:8000"
echo "• Make sure backend is running!"
echo ""

echo "✅ Project is now cleaned and reconfigured!"
echo "Return to Xcode and try building again."
