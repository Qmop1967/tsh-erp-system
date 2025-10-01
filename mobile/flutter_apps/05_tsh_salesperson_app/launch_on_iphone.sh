#!/bin/bash

echo "📱 TSH Salesperson App - iPhone Launcher"
echo "========================================="
echo ""

# Navigate to the app directory
APP_DIR="/Users/khaleelal-mulla/TSH_ERP_System_Local/tsh_salesperson_app"
cd "$APP_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Checking for connected devices...${NC}"
echo ""

# Show all available devices
flutter devices

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if iPhone is connected
IPHONE_COUNT=$(flutter devices 2>/dev/null | grep -c "ios.*•.*mobile")

if [ "$IPHONE_COUNT" -eq 0 ]; then
    echo -e "${RED}❌ No physical iPhone detected!${NC}"
    echo ""
    echo "Troubleshooting Steps:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "1. 🔌 Connect your iPhone with USB cable"
    echo "2. 🔓 Unlock your iPhone"
    echo "3. 💬 Trust this computer (tap 'Trust' when prompted)"
    echo "4. ⚙️  Enable Developer Mode:"
    echo "   • iOS 16+: Settings > Privacy & Security > Developer Mode"
    echo "   • Toggle ON and restart iPhone"
    echo "5. 🔄 Run this script again"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${YELLOW}Would you like to run on iOS Simulator instead? (y/n)${NC}"
    read -r response
    
    if [[ $response =~ ^[Yy]$ ]]; then
        echo ""
        echo -e "${BLUE}Looking for available iOS Simulators...${NC}"
        
        # Open Simulator app
        open -a Simulator 2>/dev/null
        sleep 3
        
        # Try to run on any available simulator
        echo -e "${GREEN}Launching on iOS Simulator...${NC}"
        flutter run
    else
        echo ""
        echo "Please connect your iPhone and try again."
        exit 1
    fi
else
    echo -e "${GREEN}✅ iPhone detected!${NC}"
    echo ""
    
    # Get device details
    DEVICE_LINE=$(flutter devices 2>/dev/null | grep "ios.*•.*mobile" | head -1)
    DEVICE_NAME=$(echo "$DEVICE_LINE" | awk '{print $1}')
    
    echo -e "${BLUE}Device: ${GREEN}$DEVICE_NAME${NC}"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${YELLOW}Select build mode:${NC}"
    echo "  1) Debug (default - hot reload enabled)"
    echo "  2) Release (optimized, faster performance)"
    echo "  3) Profile (for performance testing)"
    echo ""
    echo -n "Enter choice [1-3] (press Enter for Debug): "
    read -r mode_choice
    
    # Set default to debug if no input
    mode_choice=${mode_choice:-1}
    
    case $mode_choice in
        2)
            echo ""
            echo -e "${BLUE}🚀 Building in ${GREEN}RELEASE${BLUE} mode...${NC}"
            echo ""
            flutter run --release
            ;;
        3)
            echo ""
            echo -e "${BLUE}🚀 Building in ${GREEN}PROFILE${BLUE} mode...${NC}"
            echo ""
            flutter run --profile
            ;;
        *)
            echo ""
            echo -e "${BLUE}🚀 Building in ${GREEN}DEBUG${BLUE} mode...${NC}"
            echo ""
            flutter run
            ;;
    esac
    
    # Check exit status
    if [ $? -eq 0 ]; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo -e "${GREEN}✅ App successfully deployed!${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    else
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo -e "${RED}❌ Build/Deploy Failed!${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "Common Solutions:"
        echo "1. Code Signing Issue:"
        echo "   • Open: ios/Runner.xcworkspace in Xcode"
        echo "   • Select Runner target"
        echo "   • Go to 'Signing & Capabilities'"
        echo "   • Check 'Automatically manage signing'"
        echo "   • Select your Team"
        echo ""
        echo "2. Re-run the fix script:"
        echo "   • ./fix_ios_complete.sh"
        echo ""
        echo "3. Check Flutter doctor:"
        echo "   • flutter doctor -v"
        echo ""
        exit 1
    fi
fi

