#!/bin/bash

echo "📱 TSH Admin App - iPhone 15 Pro Max Wireless Deployment"
echo "========================================================"

# Project configuration
PROJECT_NAME="TSH Admin Dashboard"
APP_PATH="/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard"
BUNDLE_ID="com.tsh.admin.tshAdminDashboard"

cd "$APP_PATH"

# Function to check prerequisites
check_prerequisites() {
    echo "🔍 Checking prerequisites..."
    
    # Check Flutter
    if ! command -v flutter &> /dev/null; then
        echo "❌ Flutter not found. Please install Flutter first."
        exit 1
    fi
    
    # Check Xcode
    if ! command -v xcodebuild &> /dev/null; then
        echo "❌ Xcode command line tools not found."
        echo "   Run: xcode-select --install"
        exit 1
    fi
    
    echo "✅ Prerequisites check passed"
}

# Function to setup wireless debugging
setup_wireless_debugging() {
    echo ""
    echo "📲 Setting up Wireless Debugging for iPhone 15 Pro Max"
    echo "======================================================"
    echo ""
    echo "🔌 FIRST: Connect your iPhone 15 Pro Max via USB cable"
    echo ""
    read -p "Press Enter when iPhone is connected via USB..."
    
    echo ""
    echo "📋 Follow these steps in Xcode:"
    echo "1. Open Xcode"
    echo "2. Go to Window → Devices and Simulators"
    echo "3. Select your iPhone 15 Pro Max from the left panel"
    echo "4. Check ✅ 'Connect via network' checkbox"
    echo "5. Wait for the network/WiFi icon to appear next to your device"
    echo "6. Once you see the WiFi icon, disconnect the USB cable"
    echo ""
    read -p "Press Enter when wireless connection is established..."
}

# Function to detect iPhone
detect_iphone() {
    echo ""
    echo "🔍 Scanning for connected iPhone devices..."
    echo ""
    
    # Get Flutter devices
    flutter devices > /tmp/flutter_devices.txt
    
    # Look for iPhone 15 Pro Max specifically
    IPHONE_DEVICE=$(grep -i "iphone.*15.*pro.*max\|iphone" /tmp/flutter_devices.txt | grep -v simulator | head -1)
    
    if [ -z "$IPHONE_DEVICE" ]; then
        echo "📱 Checking for any iOS devices..."
        IPHONE_DEVICE=$(flutter devices | grep "ios" | grep -v "simulator" | head -1)
    fi
    
    if [ -n "$IPHONE_DEVICE" ]; then
        echo "✅ Found iOS device:"
        echo "   $IPHONE_DEVICE"
        
        # Extract device ID
        DEVICE_ID=$(echo "$IPHONE_DEVICE" | grep -oE '[0-9A-Fa-f\-]{36}' | head -1)
        
        if [ -z "$DEVICE_ID" ]; then
            # Try alternative ID extraction
            DEVICE_ID=$(echo "$IPHONE_DEVICE" | awk '{print $NF}' | tr -d '()')
        fi
        
        echo "   Device ID: $DEVICE_ID"
        return 0
    else
        echo "❌ No iPhone found!"
        echo ""
        echo "🔧 Troubleshooting steps:"
        echo "1. Ensure iPhone is unlocked"
        echo "2. Trust this computer (if prompted)"
        echo "3. Enable Developer Mode: Settings → Privacy & Security → Developer Mode"
        echo "4. For wireless: Set up network connection in Xcode first"
        echo ""
        echo "📋 All detected devices:"
        flutter devices
        return 1
    fi
}

# Function to check device trust and developer mode
check_device_status() {
    echo ""
    echo "🔐 Checking device status..."
    
    # Use xcrun to check device status
    if command -v xcrun &> /dev/null; then
        echo "📋 iOS device status:"
        xcrun devicectl list devices --include-locked 2>/dev/null || echo "   Using legacy device detection..."
    fi
}

# Function to prepare app for deployment
prepare_app() {
    echo ""
    echo "🔨 Preparing TSH Admin App for deployment..."
    echo ""
    
    # Clean previous build
    echo "🧹 Cleaning previous build..."
    flutter clean
    
    # Get dependencies
    echo "📦 Getting dependencies..."
    flutter pub get
    
    # Check for iOS specific setup
    echo "🍎 Checking iOS configuration..."
    if [ -f "ios/Podfile" ]; then
        echo "✅ iOS Podfile found"
        cd ios
        pod install --repo-update
        cd ..
    fi
    
    echo "✅ App preparation complete"
}

# Function to deploy app
deploy_app() {
    echo ""
    echo "🚀 Deploying TSH Admin App to iPhone 15 Pro Max"
    echo "==============================================="
    
    if [ -n "$DEVICE_ID" ]; then
        echo "📱 Targeting device: $DEVICE_ID"
        echo "🔄 Starting deployment..."
        echo ""
        
        # Try deployment with device ID
        echo "🏃 Running: flutter run -d $DEVICE_ID"
        flutter run -d "$DEVICE_ID" --verbose
        
    else
        echo "🔄 Trying deployment without specific device ID..."
        flutter run --verbose
    fi
}

# Function to show post-deployment instructions
show_post_deployment() {
    echo ""
    echo "🎉 Deployment Process Complete!"
    echo ""
    echo "📱 If the app installed successfully on your iPhone 15 Pro Max:"
    echo "   • The app should launch automatically"
    echo "   • Look for 'TSH Admin Dashboard' on your home screen"
    echo ""
    echo "🔐 If you see 'Untrusted Developer' message:"
    echo "   1. Go to iPhone Settings"
    echo "   2. General → VPN & Device Management"
    echo "   3. Find your developer profile"
    echo "   4. Tap 'Trust' to enable the app"
    echo ""
    echo "🔄 For future wireless deployments:"
    echo "   • Keep iPhone and Mac on the same WiFi network"
    echo "   • Run this script again without USB cable"
    echo ""
}

# Function to run full deployment process
run_full_deployment() {
    check_prerequisites
    
    echo ""
    echo "🎯 Choose deployment method:"
    echo "1) USB deployment (recommended for first time)"
    echo "2) Wireless deployment (iPhone must be already configured)"
    echo ""
    read -p "Choose option (1 or 2): " deploy_method
    
    case $deploy_method in
        1)
            echo ""
            echo "📱 USB Deployment Selected"
            echo "Connect your iPhone 15 Pro Max via USB cable now"
            read -p "Press Enter when connected..."
            ;;
        2)
            echo ""
            echo "📡 Wireless Deployment Selected"
            setup_wireless_debugging
            ;;
        *)
            echo "Invalid choice. Using USB deployment."
            ;;
    esac
    
    check_device_status
    
    if detect_iphone; then
        prepare_app
        deploy_app
        show_post_deployment
    else
        echo ""
        echo "❌ Cannot proceed without a detected iPhone"
        echo "Please check your connection and try again"
    fi
}

# Main execution
echo "🍎 Welcome to TSH Admin App Deployment"
echo ""
echo "This script will help you deploy the TSH Admin Dashboard"
echo "to your iPhone 15 Pro Max wirelessly or via USB."
echo ""
read -p "Press Enter to continue..."

run_full_deployment

echo ""
echo "✅ Deployment script finished!"
echo "📞 If you need help, check the ios_deployment_guide.md file"
