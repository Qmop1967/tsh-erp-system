#!/bin/bash

echo "Fixing iOS Team ID configuration..."

cd "/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard"

# Clean everything first
echo "Cleaning project..."
flutter clean
rm -rf ios/build
rm -rf build

# Update Team ID in project.pbxproj
echo "Updating Team ID in Xcode project..."
sed -i '' 's/38U844SAJ5/3BJB4453J5/g' ios/Runner.xcodeproj/project.pbxproj

# Reinstall dependencies
echo "Getting dependencies..."
flutter pub get

# Reinstall pods
echo "Installing CocoaPods..."
cd ios
pod install --repo-update
cd ..

echo "Team ID fix complete!"
echo "Current configuration:"
grep -n "DEVELOPMENT_TEAM" ios/Runner.xcodeproj/project.pbxproj
