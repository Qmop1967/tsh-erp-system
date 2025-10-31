#!/bin/bash

echo "🔐 Xcode Signing Setup Guide"
echo "=============================="
echo ""

# Open Xcode workspace
echo "Opening Xcode workspace..."
open /Users/khaleelal-mulla/TSH_ERP_System_Local/tsh_salesperson_app/ios/Runner.xcworkspace

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Manual Steps to Complete in Xcode:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "STEP 1: Add Your Apple Account (if not already added)"
echo "------------------------------------------------------"
echo "  1. Go to: Xcode > Settings (⌘,)"
echo "  2. Click 'Accounts' tab"
echo "  3. Click '+' button (bottom left)"
echo "  4. Select 'Apple ID'"
echo "  5. Enter your Apple ID email and password"
echo "  6. Click 'Sign In'"
echo ""
echo "STEP 2: Configure Signing in Your Project"
echo "------------------------------------------------------"
echo "  1. In Xcode left sidebar, click 'Runner' (blue icon)"
echo "  2. Select 'Runner' target (not the project)"
echo "  3. Click 'Signing & Capabilities' tab"
echo "  4. Check ✓ 'Automatically manage signing'"
echo "  5. In 'Team' dropdown, select your Apple ID or Team"
echo "     (e.g., 'Your Name (Personal Team)' or your organization)"
echo "  6. Verify Bundle Identifier is: com.tsh.salesperson"
echo "  7. Xcode will automatically create/download provisioning profile"
echo ""
echo "STEP 3: Verify No Errors"
echo "------------------------------------------------------"
echo "  • You should see: ✓ 'Provisioning profile: Xcode Managed Profile'"
echo "  • No red error messages"
echo "  • If you see a device warning, ignore it (you can deploy wirelessly)"
echo ""
echo "STEP 4: Build to Verify"
echo "------------------------------------------------------"
echo "  • Press ⌘B or Product > Build"
echo "  • Wait for 'Build Succeeded'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 IMPORTANT NOTES:"
echo ""
echo "• FREE Apple Developer Account: You can use any Apple ID (free)"
echo "  - This creates a 'Personal Team'"
echo "  - Apps expire after 7 days (need to reinstall)"
echo "  - Limited to 3 apps per device"
echo ""
echo "• PAID Apple Developer Account (\$99/year):"
echo "  - Team ID: 3BJB4453J5 or similar"
echo "  - Apps don't expire"
echo "  - Can distribute to TestFlight/App Store"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "After completing these steps in Xcode, press ENTER to continue..."
read -r

echo ""
echo "🚀 Now attempting to launch on your iPhone..."
echo ""

# Return to app directory
cd /Users/khaleelal-mulla/TSH_ERP_System_Local/tsh_salesperson_app

# Check for connected devices
echo "Connected devices:"
flutter devices

echo ""
echo "Launching app..."
flutter run -d 00008130-0004310C1ABA001C

if [ $? -eq 0 ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ SUCCESS! App is running on your iPhone!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "❌ Launch failed. Please check the error messages above."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Common solutions:"
    echo "  1. Make sure you selected a Team in Xcode Signing settings"
    echo "  2. Make sure 'Automatically manage signing' is checked"
    echo "  3. Try disconnecting and reconnecting your iPhone"
    echo "  4. On iPhone: Settings > General > Device Management"
    echo "     Tap your Apple ID and 'Trust' the app"
    echo ""
fi

