#!/bin/bash

echo "🍎 TSH Admin Dashboard - Complete Xcode Launch & iPhone Deploy Guide"
echo "===================================================================="
echo ""

# Set project path
PROJECT_PATH="/Users/khaleelal-mulla/TSH_ERP_System_Local/mobile/flutter_apps/admin_dashboard"
WORKSPACE_PATH="$PROJECT_PATH/ios/Runner.xcworkspace"

echo "📍 Project Path: $PROJECT_PATH"
echo ""

# Navigate to project directory
cd "$PROJECT_PATH"

# Step 1: Environment Check
echo "🔍 Step 1: Checking Development Environment"
echo "=========================================="

# Check Flutter installation
if command -v flutter &> /dev/null; then
    echo "✅ Flutter is installed"
    flutter --version | head -1
else
    echo "❌ Flutter not found. Please install Flutter first."
    exit 1
fi

# Check Xcode installation
if command -v xcodebuild &> /dev/null; then
    echo "✅ Xcode is installed"
    xcodebuild -version | head -1
else
    echo "❌ Xcode not found. Please install Xcode from App Store."
    exit 1
fi

echo ""

# Step 2: Flutter Setup
echo "📦 Step 2: Setting up Flutter Dependencies"
echo "========================================="

echo "Getting Flutter dependencies..."
flutter pub get

echo "Running Flutter doctor to check setup..."
flutter doctor

echo ""

# Step 3: iOS Setup
echo "🔧 Step 3: iOS Project Setup"
echo "============================"

echo "Cleaning previous builds..."
flutter clean

echo "Getting iOS dependencies (CocoaPods)..."
cd ios
pod install
cd ..

echo ""

# Step 4: Device Detection
echo "📱 Step 4: Detecting Connected Devices"
echo "====================================="

echo "Available devices:"
flutter devices

echo ""
echo "Looking for connected iPhone..."

# Check for physical iOS device
IPHONE_DEVICE=$(flutter devices | grep "ios" | grep -v "simulator" | head -1)

if [ -z "$IPHONE_DEVICE" ]; then
    echo "❌ No physical iPhone detected."
    echo ""
    echo "📋 To connect your iPhone:"
    echo "   1. Connect iPhone with USB cable"
    echo "   2. Unlock iPhone and tap 'Trust This Computer'"
    echo "   3. Enable Developer Mode:"
    echo "      Settings → Privacy & Security → Developer Mode → ON"
    echo "   4. For wireless debugging (optional):"
    echo "      Xcode → Window → Devices and Simulators"
    echo "      Select your device → Check 'Connect via network'"
    echo ""
    
    echo "🔄 Would you like to:"
    echo "   1) Continue with iOS Simulator"
    echo "   2) Open Xcode to set up device"
    echo "   3) Exit and connect iPhone manually"
    echo ""
    read -p "Choose option (1/2/3): " option
    
    case $option in
        1)
            echo "📱 Launching on iOS Simulator..."
            flutter run -d ios-simulator
            ;;
        2)
            echo "🍎 Opening Xcode..."
            open "$WORKSPACE_PATH"
            echo ""
            echo "📋 In Xcode:"
            echo "   1. Select your Team in Signing & Capabilities"
            echo "   2. Connect your iPhone"
            echo "   3. Select your iPhone as target device"
            echo "   4. Click the Play button to build and run"
            ;;
        3)
            echo "🛑 Exiting. Please connect your iPhone and run this script again."
            exit 0
            ;;
        *)
            echo "❌ Invalid option. Exiting."
            exit 1
            ;;
    esac
else
    echo "✅ iPhone detected: $IPHONE_DEVICE"
    DEVICE_ID=$(echo "$IPHONE_DEVICE" | grep -o '[A-F0-9-]\{36\}\|[A-F0-9]\{8\}-[A-F0-9]\{16\}' | head -1)
    echo "📱 Device ID: $DEVICE_ID"
fi

echo ""

# Step 5: Launch Options
echo "🚀 Step 5: Launch Options"
echo "========================"

if [ -n "$IPHONE_DEVICE" ]; then
    echo "Choose how to launch:"
    echo "   1) Flutter run (command line)"
    echo "   2) Open in Xcode for full IDE experience"
    echo "   3) Both (Flutter run + open Xcode)"
    echo ""
    read -p "Choose option (1/2/3): " launch_option
    
    case $launch_option in
        1)
            echo "🚀 Launching with Flutter..."
            if [ -n "$DEVICE_ID" ]; then
                flutter run -d "$DEVICE_ID" --debug
            else
                flutter run --debug
            fi
            ;;
        2)
            echo "🍎 Opening in Xcode..."
            open "$WORKSPACE_PATH"
            echo ""
            echo "📋 Next steps in Xcode:"
            echo "   1. Wait for project to load"
            echo "   2. Select your iPhone from device list (top of Xcode)"
            echo "   3. Click the Play button (▶) to build and run"
            echo "   4. First time may ask for signing - select your Apple ID"
            ;;
        3)
            echo "🚀 Starting Flutter in background..."
            if [ -n "$DEVICE_ID" ]; then
                flutter run -d "$DEVICE_ID" --debug &
            else
                flutter run --debug &
            fi
            
            sleep 2
            echo "🍎 Opening Xcode..."
            open "$WORKSPACE_PATH"
            echo ""
            echo "✅ Both Flutter and Xcode are now running!"
            ;;
        *)
            echo "❌ Invalid option"
            exit 1
            ;;
    esac
fi

echo ""
echo "📋 Troubleshooting Tips:"
echo "======================"
echo ""
echo "If you encounter issues:"
echo ""
echo "🔑 Code Signing Issues:"
echo "   • In Xcode → Runner → Signing & Capabilities"
echo "   • Select your Apple Developer Team"
echo "   • Change Bundle Identifier if needed (com.yourname.tshadmin)"
echo ""
echo "📱 Device Trust Issues:"
echo "   • Disconnect and reconnect iPhone"
echo "   • Check 'Settings → General → Device Management' on iPhone"
echo "   • Trust the developer certificate"
echo ""
echo "🔧 Build Issues:"
echo "   • Run: flutter clean"
echo "   • Run: cd ios && pod install && cd .."
echo "   • Run: flutter pub get"
echo ""
echo "🌐 Network Issues:"
echo "   • Check if app tries to connect to localhost"
echo "   • Use your Mac's IP address instead of localhost"
echo "   • Example: http://192.168.1.100:8000 instead of http://localhost:8000"
echo ""
echo "🎯 Target Device:"
echo "   • Make sure iPhone is selected in Xcode (not simulator)"
echo "   • Device should appear in Xcode → Window → Devices and Simulators"
echo ""
echo "✅ Success indicators:"
echo "   • App appears on iPhone home screen"
echo "   • No crash on launch"
echo "   • Can navigate through the admin dashboard"
echo ""
echo "🔄 For quick rebuilds:"
echo "   • Use 'r' in Flutter terminal for hot reload"
echo "   • Use 'R' for hot restart"
echo "   • Use 'q' to quit Flutter session"
