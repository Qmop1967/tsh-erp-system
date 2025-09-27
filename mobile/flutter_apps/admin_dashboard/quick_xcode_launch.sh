#!/bin/bash

echo "🍎 Quick Xcode Launch for TSH Admin Dashboard"
echo "============================================"

PROJECT_PATH="/Users/khaleelal-mulla/TSH_ERP_System_Local/mobile/flutter_apps/admin_dashboard"
WORKSPACE_PATH="$PROJECT_PATH/ios/Runner.xcworkspace"

cd "$PROJECT_PATH"

echo "📦 Getting Flutter dependencies..."
flutter pub get

echo "🔧 Installing iOS dependencies..."
cd ios && pod install && cd ..

echo "🍎 Opening Xcode..."
open "$WORKSPACE_PATH"

echo ""
echo "✅ Xcode is opening with your TSH Admin Dashboard!"
echo ""
echo "📋 Next steps in Xcode:"
echo "   1. Wait for project to load completely"
echo "   2. Connect your iPhone via USB"
echo "   3. Select your iPhone from the device dropdown (top-left)"
echo "   4. Click the Play button (▶) to build and run on your iPhone"
echo ""
echo "🔑 If prompted for signing:"
echo "   1. Go to Runner → Signing & Capabilities"
echo "   2. Select your Apple Developer Team"
echo "   3. The app will be signed automatically"
echo ""
echo "📱 Your iPhone will show the TSH Admin Dashboard once built!"
