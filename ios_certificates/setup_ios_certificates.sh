#!/bin/bash

echo "🍎 iOS Certificate Setup & Project Configuration"
echo "=============================================="
echo ""

PROJECT_DIR="/Users/khaleelal-mulla/Desktop/TSH ERP System/frontend/tsh_admin_dashboard"
CERT_DIR="/Users/khaleelal-mulla/Desktop/ios_certificates"

echo "📋 Current Certificate Status:"
echo ""
security find-identity -v -p codesigning
echo ""

echo "📱 Instructions for Apple Developer Portal:"
echo ""
echo "1. 🌐 Go to: https://developer.apple.com/account/resources/certificates/list"
echo "2. ➕ Click the '+' button to add a new certificate"
echo "3. 📋 Select 'Apple Development' certificate type"
echo "4. 📤 Upload the file: $CERT_DIR/TSH_iOS_Certificate_Request.csr"
echo "5. 📥 Download the certificate (usually named 'development.cer')"
echo "6. 🖱️  Double-click the downloaded certificate to install in Keychain"
echo ""

echo "📱 App ID Configuration:"
echo ""
echo "Current Bundle ID: com.tsh.tshAdminDashboard"
echo "Recommended Bundle ID: com.tsh.admin (from your certificates config)"
echo ""
echo "To create/verify App ID:"
echo "1. 🌐 Go to: https://developer.apple.com/account/resources/identifiers/list"
echo "2. ➕ Create new App ID if needed"
echo "3. 📝 Use Bundle ID: com.tsh.admin"
echo "4. 📱 Register your device UDID: 00008130-000431C1ABA001C"
echo ""

echo "🔧 Provisioning Profile:"
echo ""
echo "1. 🌐 Go to: https://developer.apple.com/account/resources/profiles/list"
echo "2. ➕ Create new Development Provisioning Profile"
echo "3. 📱 Select your App ID: com.tsh.admin"
echo "4. 📋 Select your new Development Certificate"
echo "5. 📱 Select your registered device"
echo "6. 📥 Download and double-click to install"
echo ""

echo "Press ENTER when you've completed the Apple Developer Portal steps..."
read -r

echo ""
echo "🔧 Configuring Xcode Project..."
echo ""

# Update bundle identifier in project
cd "$PROJECT_DIR" || exit

# Update the bundle identifier to match your Apple Developer account
echo "📝 Updating bundle identifier to com.tsh.admin..."

# Use sed to update the bundle identifier in the project file
sed -i '' 's/com\.tsh\.tshAdminDashboard/com.tsh.admin/g' ios/Runner.xcodeproj/project.pbxproj

# Also update in Info.plist if needed
if [ -f "ios/Runner/Info.plist" ]; then
    echo "📝 Updating Info.plist display name..."
    plutil -replace CFBundleDisplayName -string "TSH Admin" ios/Runner/Info.plist
fi

echo ""
echo "✅ Project Configuration Updated!"
echo ""
echo "📋 What was changed:"
echo "   - Bundle Identifier: com.tsh.admin"
echo "   - Display Name: TSH Admin"
echo ""

echo "🧪 Testing certificate installation..."
echo ""
security find-identity -v -p codesigning

echo ""
echo "🚀 Next Steps:"
echo ""
echo "1. ✅ Verify your new certificate appears in the list above"
echo "2. 🔧 Open Xcode to verify signing settings:"
echo "   - Team should be: 3BJB4453J5"
echo "   - Bundle ID should be: com.tsh.admin"
echo "   - Provisioning Profile should be automatic or your dev profile"
echo "3. 🚀 Try building: flutter build ios --device-id 00008130-0004310C1ABA001C"
echo ""

echo "Would you like to open Xcode now? (y/n)"
read -r open_xcode

if [[ $open_xcode =~ ^[Yy]$ ]]; then
    echo "🔧 Opening Xcode..."
    open ios/Runner.xcworkspace
fi

echo ""
echo "🎉 Setup complete! Your project is now configured for iOS development."
