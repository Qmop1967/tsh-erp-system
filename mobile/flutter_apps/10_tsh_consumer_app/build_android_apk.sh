#!/bin/bash

# TSH Consumer App - Android APK Build Script
# This script builds the Android APK for distribution via WhatsApp

set -e  # Exit on error

echo "=========================================="
echo "TSH Consumer App - Android APK Builder"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get project directory
PROJECT_DIR="/Users/khaleelal-mulla/TSH_ERP_Ecosystem/mobile/flutter_apps/10_tsh_consumer_app"
FLUTTER_BIN="/Users/khaleelal-mulla/development/flutter/bin/flutter"

echo -e "${YELLOW}Step 1: Checking Flutter installation...${NC}"
if [ ! -f "$FLUTTER_BIN" ]; then
    echo -e "${RED}Error: Flutter not found at $FLUTTER_BIN${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Flutter found${NC}"
echo ""

echo -e "${YELLOW}Step 2: Navigating to project directory...${NC}"
cd "$PROJECT_DIR"
echo -e "${GREEN}✓ Current directory: $(pwd)${NC}"
echo ""

echo -e "${YELLOW}Step 3: Cleaning previous build...${NC}"
rm -rf build/app
echo -e "${GREEN}✓ Cleaned previous Android builds${NC}"
echo ""

echo -e "${YELLOW}Step 4: Getting Flutter dependencies...${NC}"
$FLUTTER_BIN pub get
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

echo -e "${YELLOW}Step 5: Building Android APK (Release mode)...${NC}"
echo -e "${YELLOW}This may take 3-5 minutes...${NC}"
echo ""
$FLUTTER_BIN build apk --release --no-tree-shake-icons

echo ""
echo -e "${GREEN}=========================================="
echo -e "✓ APK BUILD SUCCESSFUL!"
echo -e "==========================================${NC}"
echo ""
echo -e "${GREEN}APK Location:${NC}"
echo -e "${YELLOW}$PROJECT_DIR/build/app/outputs/flutter-apk/app-release.apk${NC}"
echo ""

# Get APK file size
APK_PATH="$PROJECT_DIR/build/app/outputs/flutter-apk/app-release.apk"
if [ -f "$APK_PATH" ]; then
    APK_SIZE=$(ls -lh "$APK_PATH" | awk '{print $5}')
    echo -e "${GREEN}APK Size: $APK_SIZE${NC}"
    echo ""
    echo -e "${GREEN}Next Steps:${NC}"
    echo "1. Locate the APK file in Finder"
    echo "2. Right-click on app-release.apk"
    echo "3. Share via WhatsApp to your team"
    echo ""
    echo -e "${YELLOW}Opening APK location in Finder...${NC}"
    open "$PROJECT_DIR/build/app/outputs/flutter-apk/"
else
    echo -e "${RED}Error: APK file not found!${NC}"
    exit 1
fi
