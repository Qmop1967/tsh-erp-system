#!/bin/bash

echo "🍎 TSH Admin App - Xcode Launch & Deploy Script"
echo "=============================================="
echo "📱 Updated Configuration:"
echo "   • Bundle ID: com.tsh.admin"
echo "   • Team ID: 3BJB4453J5 (Khaleel Ahmed)"
echo "   • Target Device: iPhone 15 Pro Max"
echo "   • UDID: 00008130-000431C1ABA001C"
echo ""

# Project paths
PROJECT_PATH="/Users/khaleelal-mulla/TSH_ERP_System_Local/mobile/flutter_apps/admin_dashboard"
WORKSPACE_PATH="$PROJECT_PATH/ios/Runner.xcworkspace"
PROJECT_FILE="$PROJECT_PATH/ios/Runner.xcodeproj"

cd "$PROJECT_PATH"

echo "🔧 Pre-flight checks..."

# Check if Xcode is installed
if ! command -v xcodebuild &> /dev/null; then
    echo "❌ Xcode is not installed or not in PATH"
    exit 1
fi

# Check if Flutter is ready
echo "📦 Checking Flutter dependencies..."
flutter doctor --version
flutter pub get

echo ""
echo "🔍 Checking connected devices..."
flutter devices

echo ""
echo "📱 Checking for your iPhone 15 Pro Max..."
DEVICE_CONNECTED=$(flutter devices | grep "00008130-000431C1ABA001C" || echo "")

if [[ -z "$DEVICE_CONNECTED" ]]; then
    echo "⚠️  iPhone 15 Pro Max not detected via Flutter"
    echo "   • Make sure your iPhone is connected (USB or WiFi)"
    echo "   • Trust this computer if prompted"
    echo "   • Enable Developer Mode: Settings → Privacy & Security → Developer Mode"
    echo ""
    echo "💡 Don't worry, we'll open Xcode anyway - you can select the device there."
else
    echo "✅ iPhone 15 Pro Max detected!"
fi

echo ""
echo "🚀 Opening Xcode workspace..."

# Open Xcode with the workspace
open "$WORKSPACE_PATH"

echo ""
echo "📋 In Xcode, follow these steps:"
echo ""
echo "1. 🎯 Select Target Device:"
echo "   • Click the device dropdown next to the play button"
echo "   • Choose your 'iPhone 15 Pro Max' from the list"
echo "   • If not visible, go to Window → Devices and Simulators"
echo ""
echo "2. ⚙️  Verify Signing (if needed):"
echo "   • Select 'Runner' in the project navigator"
echo "   • Go to 'Signing & Capabilities' tab"
echo "   • Ensure 'Automatically manage signing' is checked"
echo "   • Team should show: Khaleel Ahmed (3BJB4453J5)"
echo "   • Bundle Identifier: com.tsh.admin"
echo ""
echo "3. 🔨 Build & Deploy:"
echo "   • Click the Play button (▶) or press Cmd+R"
echo "   • Xcode will build and install on your iPhone"
echo "   • First run may take a few minutes"
echo ""
echo "4. 📱 On Your iPhone:"
echo "   • If you see 'Untrusted Developer' message:"
echo "     Settings → General → VPN & Device Management"
echo "     → Trust 'Khaleel Ahmed'"
echo "   • Look for 'TSH Admin' app on home screen"
echo ""
echo "🌐 Backend Connection:"
echo "   The app is configured to connect to: http://192.168.0.237:8000"
echo "   Make sure your backend server is running!"
echo ""
echo "🔍 Troubleshooting:"
echo "   • If build fails: Clean build folder (Cmd+Shift+K)"
echo "   • If signing issues: Check Apple Developer Account certificates"
echo "   • If device not found: Check cable/WiFi connection"
echo ""
echo "✅ Xcode is now open - Happy coding! 🚀"

# Also create a simple Flutter run option
echo ""
echo "🔄 Alternative: Want to try Flutter run instead?"
echo "   Run: flutter run -d 00008130-000431C1ABA001C"
echo ""

# Keep terminal open for reference
echo "💡 Keep this terminal open for reference while using Xcode"
