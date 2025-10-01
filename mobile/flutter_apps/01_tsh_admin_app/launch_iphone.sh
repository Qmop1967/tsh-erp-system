#!/bin/bash

echo "🚀 TSH Admin Dashboard - iPhone Launch Script"
echo "============================================="

# Navigate to the project directory
cd "/Users/khaleelal-mulla/TSH_ERP_System_Local/mobile/flutter_apps/admin_dashboard"

echo "📱 Checking for connected devices..."
flutter devices

echo ""
echo "🔍 Looking for connected iPhone..."

# Check if iPhone is connected (look for physical iOS device - wired or wireless)
IPHONE_DEVICE=$(flutter devices | grep "ios" | grep -v "simulator" | head -1)

if [ -z "$IPHONE_DEVICE" ]; then
    echo "❌ No physical iPhone found. Please:"
    echo "   1. Connect your iPhone with USB cable or WiFi"
    echo "   2. Unlock your iPhone and trust this computer"
    echo "   3. Enable Developer Mode in Settings > Privacy & Security"
    echo "   4. For WiFi: Enable 'Connect via network' in Xcode > Window > Devices and Simulators"
    echo ""
    echo "🔄 Would you like to run on the iOS Simulator instead? (y/n)"
    read -r response
    if [[ $response =~ ^[Yy]$ ]]; then
        echo "📱 Finding an available iOS Simulator..."
        # Find the first available iPhone simulator
        SIMULATOR_ID=$(xcrun simctl list devices available | grep 'iPhone' | head -n 1 | grep -o '[A-F0-9-]\{36\}')
        
        if [ -z "$SIMULATOR_ID" ]; then
            echo "❌ Could not find any available iOS Simulators."
            echo "Please open Xcode and create a new simulator."
            exit 1
        fi

        echo "📱 Launching on iOS Simulator (ID: $SIMULATOR_ID)..."
        flutter run -d "$SIMULATOR_ID"
    else
        echo "🛑 Please connect your iPhone and try again."
        exit 1
    fi
else
    # Extract device ID (handle both wired and wireless connections)
    DEVICE_ID=$(echo "$IPHONE_DEVICE" | grep -o '[A-F0-9-]\{36\}' | head -1)
    if [ -z "$DEVICE_ID" ]; then
        # Try alternative parsing for wireless devices
        DEVICE_ID=$(echo "$IPHONE_DEVICE" | awk '{for(i=1;i<=NF;i++) if($i ~ /^[A-F0-9-]{8}-[A-F0-9-]{4}-[A-F0-9-]{4}-[A-F0-9-]{4}-[A-F0-9-]{12}$|^[A-F0-9]{8}-[A-F0-9]{16}$/) print $i}' | head -1)
    fi
    
    DEVICE_NAME=$(echo "$IPHONE_DEVICE" | awk -F'•' '{gsub(/^ +| +$/, "", $1); print $1}')
    
    echo "✅ Found iPhone: $DEVICE_NAME"
    echo "📱 Device ID: $DEVICE_ID"
    echo "🔧 Ensuring proper code signing..."
    
    # Clean and build with proper signing
    echo "🧹 Cleaning previous builds..."
    flutter clean
    flutter pub get
    
    # Ensure pods are properly configured
    echo "🍫 Updating CocoaPods..."
    cd ios && pod install && cd ..
    
    echo "🚀 Launching TSH Admin Dashboard on your iPhone..."
    
    if [ -n "$DEVICE_ID" ]; then
        # Run with release mode for better signing
        if ! flutter run -d "$DEVICE_ID" --release; then
            echo "------------------------------------------------------"
            echo "🚨 Flutter run command failed."
            echo "This is likely a code signing issue."
            echo "Please run the signing setup script to fix it:"
            echo ""
            echo "    ./setup_ios_signing.sh"
            echo ""
            echo "------------------------------------------------------"
        fi
    else
        echo "⚠️  Could not parse device ID, trying with full device string..."
        if ! flutter run --release; then
            echo "------------------------------------------------------"
            echo "🚨 Flutter run command failed."
            echo "This is likely a code signing issue."
            echo "Please run the signing setup script to fix it:"
            echo ""
            echo "    ./setup_ios_signing.sh"
            echo ""
            echo "------------------------------------------------------"
        fi
    fi
fi
