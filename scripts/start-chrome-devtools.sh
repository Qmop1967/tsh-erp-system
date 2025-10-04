#!/bin/bash

# Chrome DevTools MCP Quick Start Script
# This script starts Chrome with debugging enabled for use with MCP

echo "🚀 Starting Chrome DevTools MCP Setup..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Chrome is already running with debugging
if lsof -i :9222 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Chrome is already running with debugging on port 9222${NC}"
    echo ""
    echo "Options:"
    echo "1. Kill the existing Chrome instance: pkill -9 'Google Chrome'"
    echo "2. Use the existing instance"
    echo ""
    exit 0
fi

# Start Chrome with debugging enabled
echo -e "${BLUE}📱 Starting Google Chrome with debugging enabled...${NC}"
echo ""

# Create temporary profile directory
PROFILE_DIR="/tmp/chrome-mcp-profile-$(date +%s)"
mkdir -p "$PROFILE_DIR"

# Start Chrome in background
open -a "Google Chrome" --args \
    --remote-debugging-port=9222 \
    --user-data-dir="$PROFILE_DIR" \
    --no-first-run \
    --no-default-browser-check \
    http://localhost:5173

echo -e "${GREEN}✅ Chrome started with debugging enabled${NC}"
echo ""
echo "📍 Debugging Details:"
echo "   Port: 9222"
echo "   Profile: $PROFILE_DIR"
echo "   URL: http://localhost:5173"
echo ""
echo "🔗 DevTools Protocol:"
echo "   http://localhost:9222/json"
echo ""
echo -e "${BLUE}💡 To use Chrome DevTools MCP:${NC}"
echo "   npx chrome-devtools-mcp"
echo ""
echo -e "${BLUE}📊 To check if debugging is active:${NC}"
echo "   curl http://localhost:9222/json/version"
echo ""
echo -e "${GREEN}✨ Chrome DevTools MCP is ready!${NC}"
