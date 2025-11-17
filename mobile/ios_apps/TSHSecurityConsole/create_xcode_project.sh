#!/bin/bash
# TSH Security Console - Xcode Project Setup Script
# This script creates a new Xcode project and adds all source files

set -e

PROJECT_NAME="TSHSecurityConsole"
BUNDLE_ID="com.tsh.securityconsole"
TEAM_ID="${APPLE_TEAM_ID:-YOUR_TEAM_ID}"
DEPLOYMENT_TARGET="16.0"

echo "🔐 TSH Security Console - Xcode Project Setup"
echo "============================================"
echo ""

# Check if we're in the right directory
if [ ! -f "TSHSecurityConsole/App/TSHSecurityConsoleApp.swift" ]; then
    echo "❌ Error: Must run from the TSHSecurityConsole directory"
    echo "   cd mobile/ios_apps/TSHSecurityConsole"
    exit 1
fi

# Check for Xcode
if ! command -v xcodebuild &> /dev/null; then
    echo "❌ Error: Xcode is not installed"
    echo "   Install Xcode from the Mac App Store"
    exit 1
fi

echo "📦 Creating Xcode project structure..."

# Create project directory if not exists
mkdir -p "$PROJECT_NAME.xcodeproj"

# Create project.pbxproj (minimal)
cat > "$PROJECT_NAME.xcodeproj/project.pbxproj" << 'EOF'
// !$*UTF8*$!
{
	archiveVersion = 1;
	classes = {
	};
	objectVersion = 56;
	objects = {
	};
	rootObject = PROJECT_ID;
}
EOF

echo "✅ Base project structure created"
echo ""
echo "⚠️  IMPORTANT: Manual Steps Required"
echo "======================================"
echo ""
echo "1. Open Xcode"
echo "2. File → New → Project"
echo "3. Choose 'App' under iOS"
echo "4. Configure:"
echo "   - Product Name: $PROJECT_NAME"
echo "   - Team: Your Apple Developer Team"
echo "   - Organization Identifier: com.tsh"
echo "   - Bundle Identifier: $BUNDLE_ID"
echo "   - Interface: SwiftUI"
echo "   - Language: Swift"
echo "   - Storage: None"
echo "   - Include Tests: Yes"
echo "5. Save project in THIS directory (replace existing)"
echo ""
echo "6. After project is created:"
echo "   - Remove default ContentView.swift and App file"
echo "   - Drag & drop the TSHSecurityConsole folder into Xcode"
echo "   - Select 'Create groups' and your target"
echo ""
echo "7. Configure Capabilities:"
echo "   - Go to project target → Signing & Capabilities"
echo "   - Add 'Push Notifications'"
echo "   - Add 'Background Modes' → Enable 'Remote notifications'"
echo "   - Add 'Keychain Sharing'"
echo ""
echo "8. Add to Info.plist:"
cat << 'PLIST'
   <!-- Camera for QR scanning -->
   <key>NSCameraUsageDescription</key>
   <string>TSH Security Console needs camera access to scan QR codes for quick approval</string>

   <!-- Face ID -->
   <key>NSFaceIDUsageDescription</key>
   <string>TSH Security Console uses Face ID for secure authentication</string>

   <!-- Location (optional for session tracking) -->
   <key>NSLocationWhenInUseUsageDescription</key>
   <string>TSH Security Console uses location to verify security events</string>

   <!-- Background modes -->
   <key>UIBackgroundModes</key>
   <array>
       <string>remote-notification</string>
   </array>
PLIST
echo ""
echo "9. Update API base URL in APIClient.swift:"
echo "   - Development: http://localhost:8000/api"
echo "   - Staging: https://staging.erp.tsh.sale/api"
echo "   - Production: https://erp.tsh.sale/api"
echo ""
echo "10. Build and run on device (Cmd+R)"
echo ""
echo "📚 For APNS setup, see: APNS_SETUP.md"
echo ""
echo "🚀 Quick Commands:"
echo "   xcodebuild -list                    # List targets"
echo "   xcodebuild -scheme $PROJECT_NAME    # Build project"
echo "   xcrun simctl list devices           # List simulators"
echo ""
