#!/bin/bash

echo "🚀 TSH Salesperson App - iOS Deep Clean Script"
echo "================================================="

# Ensure we are in the correct directory
cd "$(dirname "$0")"

echo ""
echo "⚠️ Please make sure you have closed Xcode completely before proceeding."
echo "Press Enter to continue..."
read

echo "🧹 Step 1: Cleaning Flutter build artifacts..."
flutter clean
if [ $? -ne 0 ]; then
    echo "❌ Flutter clean failed. Please check your Flutter installation."
    exit 1
fi
echo "✅ Flutter clean complete."

echo ""
echo "🗑️ Step 2: Removing old iOS Pods and Podfile.lock..."
rm -rf "ios/Pods"
rm -f "ios/Podfile.lock"
echo "✅ Old Pods removed."

echo ""
echo "📦 Step 3: Getting Flutter packages..."
flutter pub get
if [ $? -ne 0 ]; then
    echo "❌ flutter pub get failed. Check your pubspec.yaml file."
    exit 1
fi
echo "✅ Packages retrieved."

echo ""
echo "🍫 Step 4: Reinstalling CocoaPods dependencies..."
cd ios
pod install --repo-update
if [ $? -ne 0 ]; then
    echo "❌ pod install failed. This is the critical step."
    echo "   Please review the error messages above."
    echo "   Common causes include network issues or problems in the Podfile."
    cd ..
    exit 1
fi
cd ..
echo "✅ CocoaPods installation complete."

echo ""
echo "🎉 Deep Clean Finished Successfully! 🎉"
echo ""
echo "Next Steps:"
echo "1. Open the iOS project in Xcode using this specific file:"
echo "   open ios/Runner.xcworkspace"
echo ""
echo "2. Once Xcode is open, select your iPhone as the build target."
echo "3. Click the 'Run' button (▶) to build and install the app."
echo ""
echo "If you still see the 'not codesigned' error, follow the manual signing steps I provided earlier."
