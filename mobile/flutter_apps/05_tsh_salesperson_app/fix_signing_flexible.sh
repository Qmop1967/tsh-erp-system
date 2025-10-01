#!/bin/bash

echo "🔧 Flexible iOS Signing Configuration"
echo "======================================"
echo ""
echo "This will configure the app to work with ANY Apple ID"
echo "(including free Personal Team accounts)"
echo ""

APP_DIR="/Users/khaleelal-mulla/TSH_ERP_System_Local/tsh_salesperson_app"
cd "$APP_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}Step 1: Removing hardcoded Team ID...${NC}"

# Backup the project file
cp ios/Runner.xcodeproj/project.pbxproj ios/Runner.xcodeproj/project.pbxproj.backup2

# Remove DEVELOPMENT_TEAM lines to let Xcode pick the team automatically
# This allows any Apple ID to be used
sed -i '' '/DEVELOPMENT_TEAM = /d' ios/Runner.xcodeproj/project.pbxproj

echo -e "${GREEN}✓${NC} Removed hardcoded team restrictions"

echo ""
echo -e "${BLUE}Step 2: Ensuring automatic code signing...${NC}"

# Ensure CODE_SIGN_STYLE is set to Automatic
sed -i '' 's/CODE_SIGN_STYLE = Manual/CODE_SIGN_STYLE = Automatic/g' ios/Runner.xcodeproj/project.pbxproj

echo -e "${GREEN}✓${NC} Set to automatic code signing"

echo ""
echo -e "${BLUE}Step 3: Cleaning build artifacts...${NC}"

flutter clean > /dev/null 2>&1
rm -rf ios/build/
rm -rf ios/Pods/
rm -rf ios/.symlinks/
rm -f ios/Podfile.lock

echo -e "${GREEN}✓${NC} Cleaned build artifacts"

echo ""
echo -e "${BLUE}Step 4: Reinstalling dependencies...${NC}"

# Set UTF-8 locale
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

flutter pub get > /dev/null 2>&1
cd ios && pod install > /dev/null 2>&1 && cd ..

echo -e "${GREEN}✓${NC} Dependencies installed"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Configuration Complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📱 Bundle ID: com.tsh.salesperson"
echo "👥 Team: Will be selected in Xcode (any Apple ID works!)"
echo ""
echo -e "${YELLOW}NEXT: Open Xcode to select your Apple account${NC}"
echo ""
echo "Choose one:"
echo "  1) Run automatic setup: ./setup_xcode_signing.sh"
echo "  2) Open manually: open ios/Runner.xcworkspace"
echo ""

