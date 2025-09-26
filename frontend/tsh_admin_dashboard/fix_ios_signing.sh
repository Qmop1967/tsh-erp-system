#!/bin/bash

echo "🔧 TSH Admin - iOS Signing Issues Fix"
echo "====================================="

# Project paths
PROJECT_PATH="/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard"
cd "$PROJECT_PATH"

echo "📋 Detected Issues from Xcode:"
echo "❌ No Account for Team '3BJ844563' (Team ID mismatch)"
echo "❌ No profiles for 'com.tsh.admin' were found"
echo "⚠️  iOS deployment target version warnings"
echo ""

echo "🔍 Step 1: Checking Apple Developer Account Setup..."

# Check if user is signed into Xcode
echo "Checking Xcode account status..."
xcodebuild -showBuildSettings -project ios/Runner.xcodeproj -target Runner 2>/dev/null | grep -i team || echo "❌ Team configuration issue detected"

echo ""
echo "🔐 Step 2: Apple Developer Account Setup Required"
echo ""
echo "In Xcode, you need to:"
echo "1. Go to Xcode → Settings → Accounts"
echo "2. Click '+' and sign in with your Apple Developer Account:"
echo "   📧 Email: khaleel_ahm@yahoo.com (or your Apple ID)"
echo "   🆔 Team: Khaleel Ahmed (3BJB4453J5)"
echo ""
echo "3. After signing in, the team should appear as:"
echo "   'Khaleel Ahmed (Personal Team) - 3BJB4453J5'"
echo ""

echo "📱 Step 3: Download Provisioning Profiles"
echo ""
echo "You need to download provisioning profiles from Apple Developer Portal:"
echo "1. Go to: https://developer.apple.com/account/resources/profiles/list"
echo "2. Download these profiles:"
echo "   • TSH Admin Dev Profile (Development)"
echo "   • TSH Admin Distribution Profile (App Store)"
echo "3. Double-click each .mobileprovision file to install"
echo ""

echo "🎯 Step 4: Fix Bundle Identifier & Signing"
echo ""
echo "In Xcode:"
echo "1. Select 'Runner' project in navigator"
echo "2. Select 'Runner' target"
echo "3. Go to 'Signing & Capabilities' tab"
echo "4. Configure:"
echo "   ☐ Team: Khaleel Ahmed (3BJB4453J5)"
echo "   ☐ Bundle Identifier: com.tsh.admin"
echo "   ☐ Check 'Automatically manage signing'"
echo ""

echo "🔄 Step 5: Alternative - Quick Signing Fix"
echo ""
echo "If you want to test quickly with automatic signing:"
echo "1. Change Bundle ID temporarily to: com.khaleel.tshadmin"
echo "2. This will use automatic provisioning"
echo "3. Later, when you have proper profiles, change back to: com.tsh.admin"
echo ""

echo "📱 Step 6: Device Registration"
echo ""
echo "Make sure your iPhone is registered in Apple Developer Portal:"
echo "• Device: iPhone 15 Pro Max"
echo "• UDID: 00008130-000431C1ABA001C"
echo "• Status: Should be 'Enabled'"
echo ""

echo "⚠️  Step 7: iOS Deployment Target Fix"
echo ""
echo "The warnings about iOS deployment target can be fixed:"
flutter clean
echo "Updating iOS deployment target to 12.0..."

# Update iOS deployment target
if [ -f "ios/Flutter/AppFrameworkInfo.plist" ]; then
    sed -i '' 's/9\.0/12.0/g' ios/Flutter/AppFrameworkInfo.plist 2>/dev/null || echo "AppFrameworkInfo.plist not found"
fi

echo ""
echo "🚀 Step 8: Next Actions"
echo ""
echo "1. Complete Apple Developer Account setup in Xcode"
echo "2. Download and install provisioning profiles"
echo "3. Return to Xcode and try building again"
echo "4. If issues persist, try the temporary bundle ID approach"
echo ""
echo "💡 Need help? The signing issues are common and fixable!"
echo "   Most likely cause: Missing Apple Developer Account in Xcode"
echo ""

# Create a temporary fix script
echo "#!/bin/bash" > quick_bundle_fix.sh
echo 'echo "🔧 Applying temporary bundle ID for testing..."' >> quick_bundle_fix.sh
echo 'cd "/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard"' >> quick_bundle_fix.sh
echo 'sed -i "" "s/com\.tsh\.admin/com.khaleel.tshadmin/g" ios/Runner.xcodeproj/project.pbxproj' >> quick_bundle_fix.sh
echo 'echo "✅ Temporary bundle ID applied: com.khaleel.tshadmin"' >> quick_bundle_fix.sh
echo 'echo "Now try building in Xcode again"' >> quick_bundle_fix.sh
chmod +x quick_bundle_fix.sh

echo "📄 Created 'quick_bundle_fix.sh' for temporary testing if needed"
