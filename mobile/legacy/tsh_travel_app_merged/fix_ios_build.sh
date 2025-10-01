#!/bin/bash

# TSH Travel App - iOS Build Fix Script
echo "🔧 Starting iOS build fix process..."

# Change to the Flutter app directory
cd /Users/khaleelal-mulla/TSH_ERP_System_Local/tsh_travel_app

# Clean Flutter build
echo "🧹 Cleaning Flutter build..."
flutter clean

# Get Flutter packages
echo "📦 Getting Flutter packages..."
flutter pub get

# Change to iOS directory
cd ios

# Remove old Pods and build artifacts
echo "🗑️  Removing old Pods and build artifacts..."
rm -rf Pods
rm -rf Podfile.lock
rm -rf .symlinks
rm -rf Flutter/Flutter.framework
rm -rf Flutter/Flutter.podspec
rm -rf build

# Install CocoaPods dependencies
echo "📥 Installing CocoaPods dependencies..."
pod install --repo-update

# Go back to root directory
cd ..

# Build iOS app
echo "🔨 Building iOS app..."
flutter build ios --debug --no-codesign

echo "✅ iOS build process completed!"
echo ""
echo "Next steps:"
echo "1. Open Xcode: open ios/Runner.xcworkspace"
echo "2. Select your development team in Signing & Capabilities"
echo "3. Build and run the app from Xcode"
