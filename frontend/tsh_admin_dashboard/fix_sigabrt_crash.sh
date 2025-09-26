#!/bin/bash

# iOS SIGABRT Crash Fix Script
# This script helps diagnose and fix the Thread 1: Signal SIGABRT crash

echo "🚨 Diagnosing iOS SIGABRT Crash..."

APP_DIR="/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard"
cd "$APP_DIR"

echo "📱 Current bundle identifier and team settings:"
grep -A 5 -B 5 "PRODUCT_BUNDLE_IDENTIFIER\|DEVELOPMENT_TEAM" ios/Runner.xcodeproj/project.pbxproj

echo ""
echo "🔑 Checking code signing settings..."
echo "In Xcode, please verify:"
echo "1. Team is set to 'Khaleel Ahmed (3BJB4453J5)'"
echo "2. Bundle Identifier matches your provisioning profile"
echo "3. Device is selected and properly connected"
echo ""

echo "🔧 Recommended fixes:"
echo "1. In Xcode Project Settings:"
echo "   - Go to Signing & Capabilities tab"
echo "   - Ensure 'Automatically manage signing' is checked"
echo "   - Select Team: Khaleel Ahmed (3BJB4453J5)"
echo "   - Bundle Identifier: com.tsh.admin (or com.tsh.admin.dev for testing)"
echo ""
echo "2. Device Setup:"
echo "   - Make sure your iPhone 15 Pro Max is connected"
echo "   - Device should appear in Xcode's device list"
echo "   - Device must be registered in Apple Developer Portal"
echo ""
echo "3. Clean and Rebuild:"
echo "   - In Xcode: Product → Clean Build Folder (Cmd+Shift+K)"
echo "   - Then: Product → Build (Cmd+B)"
echo ""

echo "🔍 Checking if device is connected..."
xcrun devicectl list devices

echo ""
echo "💡 If the crash persists:"
echo "1. Try using a temporary bundle ID like com.tsh.admin.test"
echo "2. Use Personal Team instead of Developer Account temporarily"
echo "3. Check Xcode console for more detailed error messages"
