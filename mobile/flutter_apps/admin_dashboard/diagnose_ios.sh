#!/bin/bash

echo "📊 iOS Code Signing Diagnostic"
echo "============================="

cd "/Users/khaleelal-mulla/TSH_ERP_System_Local/mobile/flutter_apps/admin_dashboard"

echo ""
echo "🔍 Checking Flutter Environment..."
flutter doctor -v | head -15

echo ""
echo "🔍 Checking Available Devices..."
flutter devices

echo ""
echo "🔍 Checking Xcode Installation..."
xcrun --show-sdk-version
xcodebuild -version

echo ""
echo "🔍 Checking Code Signing Identities..."
security find-identity -v -p codesigning | grep "iPhone"

echo ""
echo "🔍 Checking Provisioning Profiles..."
ls -la ~/Library/MobileDevice/Provisioning\ Profiles/ 2>/dev/null | wc -l | xargs -I {} echo "Found {} provisioning profiles"

echo ""
echo "🔍 Checking Bundle Identifier in Project..."
grep -o 'PRODUCT_BUNDLE_IDENTIFIER = [^;]*' ios/Runner.xcodeproj/project.pbxproj | head -1

echo ""
echo "🔍 Checking Development Team..."
grep -o 'DEVELOPMENT_TEAM = [^;]*' ios/Runner.xcodeproj/project.pbxproj | head -1

echo ""
echo "🔍 Checking iOS Deployment Target..."
grep -o 'IPHONEOS_DEPLOYMENT_TARGET = [^;]*' ios/Runner.xcodeproj/project.pbxproj | head -1

echo ""
echo "🔍 Checking Code Signing Style..."
grep -o 'CODE_SIGN_STYLE = [^;]*' ios/Runner.xcodeproj/project.pbxproj | head -1

echo ""
echo "📋 Diagnostic Complete!"
echo ""
echo "🔧 Next Steps:"
echo "1. Run: ./complete_ios_fix.sh"
echo "2. Follow Xcode setup instructions"
echo "3. Run: ./launch_iphone.sh"
