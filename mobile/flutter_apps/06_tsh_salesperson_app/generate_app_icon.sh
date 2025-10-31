#!/bin/bash

# TSH Salesperson App - Icon Generator Script
# This script generates app icons for all platforms

echo "🎨 TSH Salesperson App - Icon Generator"
echo "========================================"
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Navigate to app directory
cd "$(dirname "$0")"

# Check if icon file exists
if [ ! -f "assets/icons/app_icon.png" ]; then
    echo -e "${RED}❌ Error: Icon file not found!${NC}"
    echo ""
    echo "Please save your TSH logo image to:"
    echo "  assets/icons/app_icon.png"
    echo ""
    echo "Requirements:"
    echo "  - Format: PNG with transparency"
    echo "  - Size: 1024x1024 pixels (recommended)"
    echo "  - Square aspect ratio"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Icon file found: assets/icons/app_icon.png${NC}"
echo ""

# Install dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
flutter pub get
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Generate icons
echo -e "${BLUE}🎨 Generating app icons for all platforms...${NC}"
flutter pub run flutter_launcher_icons
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to generate icons${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Icons generated successfully!${NC}"
echo ""

# Summary
echo "========================================"
echo -e "${GREEN}🎉 Icon generation complete!${NC}"
echo ""
echo "Generated icons for:"
echo "  ✅ iOS (all sizes)"
echo "  ✅ Android (all densities)"
echo "  ✅ Web (favicon and manifests)"
echo ""
echo "Next steps:"
echo "  1. Run: flutter clean"
echo "  2. Run: flutter run"
echo "  3. Verify the new icon appears on your device"
echo ""
echo "Icon locations:"
echo "  - iOS: ios/Runner/Assets.xcassets/AppIcon.appiconset/"
echo "  - Android: android/app/src/main/res/mipmap-*/"
echo "========================================"
