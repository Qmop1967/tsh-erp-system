#!/bin/bash

echo "🔐 TSH Admin Dashboard - iOS Code Signing Setup"
echo "==============================================="

# Navigate to iOS directory
cd "$(dirname "$0")/ios"

echo "📱 Setting up iOS code signing..."

# Open Xcode project
echo "🔧 Opening Xcode project for signing configuration..."
open Runner.xcworkspace

echo ""
echo "📋 Manual steps to complete in Xcode:"
echo "   1. Select 'Runner' project in navigator"
echo "   2. Go to 'Signing & Capabilities' tab"
echo "   3. Check 'Automatically manage signing'"
echo "   4. Select your Apple Developer Team"
echo "   5. Change Bundle Identifier if needed"
echo "   6. Close Xcode when done"
echo ""
echo "Press Enter when you've completed the signing setup..."
read -r

echo "✅ Code signing setup completed!"
echo "🚀 You can now run ./launch_iphone.sh to deploy to your iPhone"
