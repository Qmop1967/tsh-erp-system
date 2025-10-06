#!/bin/bash

# Chrome DevTools MCP Status Check Script
# This script checks the complete status of Chrome DevTools MCP setup

echo "========================================="
echo "CHROME DEVTOOLS MCP STATUS CHECK"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Check Installation
echo -e "${BLUE}1. INSTALLATION STATUS${NC}"
echo "-------------------------------------"

if command -v chrome-devtools-mcp &> /dev/null; then
    echo -e "${GREEN}✅ Global installation found${NC}"
    echo "   Location: $(which chrome-devtools-mcp)"
else
    echo -e "${RED}❌ Global installation not found${NC}"
fi

if npm list -g chrome-devtools-mcp 2>/dev/null | grep -q chrome-devtools-mcp; then
    VERSION=$(npm list -g chrome-devtools-mcp 2>/dev/null | grep chrome-devtools-mcp | awk '{print $2}')
    echo -e "${GREEN}✅ NPM Global: chrome-devtools-mcp@${VERSION}${NC}"
else
    echo -e "${YELLOW}⚠️  NPM Global: Not found${NC}"
fi

if npm list chrome-devtools-mcp 2>/dev/null | grep -q chrome-devtools-mcp; then
    VERSION=$(npm list chrome-devtools-mcp 2>/dev/null | grep chrome-devtools-mcp | awk '{print $2}')
    echo -e "${GREEN}✅ Project: chrome-devtools-mcp@${VERSION}${NC}"
else
    echo -e "${YELLOW}⚠️  Project: Not found${NC}"
fi

echo ""

# 2. Check MCP Configuration
echo -e "${BLUE}2. MCP CONFIGURATION${NC}"
echo "-------------------------------------"

MCP_CONFIG="$HOME/Library/Application Support/Code/User/mcp.json"
if [ -f "$MCP_CONFIG" ]; then
    echo -e "${GREEN}✅ MCP config file exists${NC}"
    echo "   Location: $MCP_CONFIG"
    
    # Count servers
    SERVER_COUNT=$(grep -o '"chrome-devtools[^"]*"' "$MCP_CONFIG" 2>/dev/null | wc -l | xargs)
    echo -e "${GREEN}✅ Configured servers: ${SERVER_COUNT}${NC}"
else
    echo -e "${RED}❌ MCP config file not found${NC}"
fi

echo ""

# 3. Check Chrome Browser
echo -e "${BLUE}3. CHROME BROWSER STATUS${NC}"
echo "-------------------------------------"

CHROME_PROCESSES=$(ps aux | grep -i "google chrome" | grep -v grep | wc -l | xargs)
if [ "$CHROME_PROCESSES" -gt 0 ]; then
    echo -e "${GREEN}✅ Chrome is running${NC}"
    echo "   Processes: $CHROME_PROCESSES"
else
    echo -e "${YELLOW}⚠️  Chrome is not running${NC}"
fi

echo ""

# 4. Check Chrome DevTools Protocol
echo -e "${BLUE}4. CHROME DEVTOOLS PROTOCOL${NC}"
echo "-------------------------------------"

if lsof -i :9222 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Port 9222 is ACTIVE (Chrome debugging enabled)${NC}"
    
    # Try to get version info
    VERSION_INFO=$(curl -s http://localhost:9222/json/version 2>/dev/null)
    if [ ! -z "$VERSION_INFO" ]; then
        echo -e "${GREEN}✅ DevTools Protocol responding${NC}"
        BROWSER_VERSION=$(echo $VERSION_INFO | grep -o '"Browser":"[^"]*"' | cut -d'"' -f4)
        echo "   Browser: $BROWSER_VERSION"
    fi
else
    echo -e "${YELLOW}⚠️  Port 9222 is NOT active${NC}"
    echo "   Chrome is not running with remote debugging"
    echo ""
    echo "   To start Chrome with debugging:"
    echo "   ${BLUE}./scripts/start-chrome-devtools.sh${NC}"
fi

echo ""

# 5. Check MCP Process
echo -e "${BLUE}5. MCP PROCESS STATUS${NC}"
echo "-------------------------------------"

if ps aux | grep -E "(chrome-devtools-mcp|browser-tools-mcp)" | grep -v grep > /dev/null; then
    echo -e "${GREEN}✅ MCP process is running${NC}"
    ps aux | grep -E "(chrome-devtools-mcp|browser-tools-mcp)" | grep -v grep | head -2
else
    echo -e "${YELLOW}⚠️  MCP process is not running${NC}"
fi

echo ""

# 6. Check Frontend and Backend
echo -e "${BLUE}6. TSH ERP SERVICES${NC}"
echo "-------------------------------------"

if lsof -i :8000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend API (port 8000)${NC}"
else
    echo -e "${YELLOW}⚠️  Backend API not running${NC}"
fi

if lsof -i :5173 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend Dev Server (port 5173)${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend not running${NC}"
fi

echo ""

# 7. Summary and Recommendations
echo -e "${BLUE}7. SUMMARY & NEXT STEPS${NC}"
echo "-------------------------------------"

# Determine overall status
OVERALL_STATUS="READY"

if ! command -v chrome-devtools-mcp &> /dev/null; then
    OVERALL_STATUS="NEEDS INSTALLATION"
fi

if ! lsof -i :9222 > /dev/null 2>&1; then
    OVERALL_STATUS="NEEDS CHROME DEBUGGING"
fi

case $OVERALL_STATUS in
    "READY")
        echo -e "${GREEN}✅ STATUS: READY TO USE${NC}"
        echo ""
        echo "Your Chrome DevTools MCP is fully configured and ready!"
        echo ""
        echo "Quick start:"
        echo "  ${BLUE}npx chrome-devtools-mcp@latest --browserUrl http://localhost:9222${NC}"
        ;;
    "NEEDS CHROME DEBUGGING")
        echo -e "${YELLOW}⚠️  STATUS: NEEDS CHROME WITH DEBUGGING${NC}"
        echo ""
        echo "Start Chrome with remote debugging:"
        echo "  ${BLUE}./scripts/start-chrome-devtools.sh${NC}"
        echo ""
        echo "Then connect MCP:"
        echo "  ${BLUE}npx chrome-devtools-mcp@latest --browserUrl http://localhost:9222${NC}"
        ;;
    "NEEDS INSTALLATION")
        echo -e "${RED}❌ STATUS: NEEDS INSTALLATION${NC}"
        echo ""
        echo "Install Chrome DevTools MCP:"
        echo "  ${BLUE}npm install -g chrome-devtools-mcp@latest${NC}"
        ;;
esac

echo ""
echo "========================================="
echo "For detailed documentation, see:"
echo "  CHROME_DEVTOOLS_MCP_RECONFIGURED.md"
echo "========================================="
