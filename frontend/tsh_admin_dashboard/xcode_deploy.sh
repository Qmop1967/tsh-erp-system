#!/bin/bash

echo "🔧 TSH Admin App - Xcode Build & Deploy Script"
echo "=============================================="

PROJECT_PATH="/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard"
DEVICE_ID="00008130-0004310C1ABA001C"

echo ""
echo "📱 Building and deploying to iPhone 15 Pro Max"
echo "Device ID: $DEVICE_ID"
echo ""

cd "$PROJECT_PATH"

# Clean Flutter build
echo "🧹 Cleaning Flutter build..."
flutter clean
flutter pub get

# Build iOS app using Xcode
echo ""
echo "🔨 Building iOS app with Xcode..."
echo "This will take a few minutes..."

# Use xcodebuild to build and deploy
xcodebuild \
    -workspace ios/Runner.xcworkspace \
    -scheme Runner \
    -configuration Debug \
    -destination "id=$DEVICE_ID" \
    -allowProvisioningUpdates \
    build

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful! Now installing on iPhone..."
    
    # Install the app
    xcodebuild \
        -workspace ios/Runner.xcworkspace \
        -scheme Runner \
        -configuration Debug \
        -destination "id=$DEVICE_ID" \
        -allowProvisioningUpdates \
        install
        
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 SUCCESS! TSH Admin app has been installed on your iPhone!"
        echo ""
        echo "📱 Next steps:"
        echo "1. Check your iPhone home screen for 'TSH Admin Dashboard'"
        echo "2. If you see 'Untrusted Developer', go to:"
        echo "   Settings → General → VPN & Device Management → Trust Developer"
        echo "3. Open the app and test connectivity"
        echo ""
        echo "🌐 The app is now configured to connect to:"
        echo "   http://192.168.0.237:8000"
        echo ""
    else
        echo "❌ Installation failed. Please check device connection."
    fi
else
    echo "❌ Build failed. Opening Xcode for manual debugging..."
    open ios/Runner.xcworkspace
    echo ""
    echo "In Xcode:"
    echo "1. Select your iPhone from the device dropdown"
    echo "2. Click the Play button to build and run"
    echo "3. If signing issues occur, go to Runner → Signing & Capabilities"
    echo "4. Ensure 'Automatically manage signing' is checked"
    echo "5. Select Team: Khaleel Ahmed (38U844SAJ5)"
fi
