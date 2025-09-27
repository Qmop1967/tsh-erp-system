#!/bin/bash

echo "🔑 TSH Admin Dashboard - Code Signing Fix"
echo "========================================"

cd "/Users/khaleelal-mulla/TSH_ERP_System_Local/mobile/flutter_apps/admin_dashboard"

echo "📱 Available provisioning profiles and teams:"
security find-identity -v -p codesigning

echo ""
echo "🔧 Let's try to sign and run the app..."

# Try to run with automatic signing
flutter run -d 00008130-0004310C1ABA001C --debug

echo ""
echo "📋 If signing fails:"
echo "   1. In Xcode: Runner → Signing & Capabilities"  
echo "   2. Select your Apple ID under Team"
echo "   3. Change Bundle ID to: com.yourname.tshadmin"
echo "   4. Click Play button in Xcode"
