#!/bin/bash

echo "🚀 TSH Admin Dashboard - iPhone Launch Script"
echo "============================================="

# Navigate to the project directory
cd "/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard"

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
        echo "📱 Launching on iOS Simulator..."
        flutter run -d "85FB8298-7B40-4A40-BA3D-D1B324B287F9"
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
    echo "🚀 Launching TSH Admin Dashboard on your iPhone..."
    
    if [ -n "$DEVICE_ID" ]; then
        flutter run -d "$DEVICE_ID"
    else
        echo "⚠️  Could not parse device ID, trying with full device string..."
        flutter run
    fi
fi
