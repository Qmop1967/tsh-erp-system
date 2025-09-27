#!/bin/bash

echo "🔐 TSH Admin Dashboard - Complete iOS Setup"
echo "=========================================="

# Navigate to the project directory
cd "/Users/khaleelal-mulla/TSH_ERP_System_Local/mobile/flutter_apps/admin_dashboard"

echo "📱 Checking Flutter doctor..."
flutter doctor --verbose | head -20

echo ""
echo "🔧 Setting up iOS signing configuration..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
flutter clean
rm -rf ios/Pods
rm -rf ios/.symlinks
rm -f ios/Podfile.lock

# Get dependencies
echo "📦 Getting Flutter dependencies..."
flutter pub get

# Update CocoaPods
echo "🍫 Updating CocoaPods..."
cd ios
pod install --repo-update
cd ..

# Open Xcode for manual configuration
echo "📱 Opening Xcode project..."
open ios/Runner.xcworkspace

echo ""
echo "✅ Project cleaned and dependencies updated!"
echo ""
echo "🔥 CRITICAL: Complete these steps in Xcode (now open):"
echo "   1. Select 'Runner' project in left navigator"
echo "   2. Select 'Runner' target"
echo "   3. Go to 'Signing & Capabilities' tab"
echo "   4. ✅ Check 'Automatically manage signing'"
echo "   5. Select your Apple Developer Team"
echo "   6. Change Bundle Identifier to: com.tsh.erp.admin"
echo "   7. Make sure Deployment Target is iOS 12.0+"
echo ""
echo "📋 Press Enter after completing Xcode setup..."
read -r

echo ""
echo "🚀 Testing iPhone connection..."
flutter devices

echo ""
echo "✅ Setup complete! Running launch script..."
./launch_iphone.sh
