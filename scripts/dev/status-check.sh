#!/bin/bash
# Quick status check for TSH ERP System

echo "🏢 TSH ERP System - Status Check"
echo "==============================="

cd "/Users/khaleelal-mulla/Desktop/TSH ERP System"

# Check Git status
echo "📦 Git Status:"
git status --porcelain
echo ""

# Check if dev server is running
echo "🌐 Development Server Status:"
if lsof -Pi :3003 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Frontend dev server is running on port 3003"
    echo "🌐 URL: http://localhost:3003"
else
    echo "❌ Frontend dev server is not running on port 3003"
    echo "💡 Run './dev-start.sh' to start it"
fi

# Check recent commits
echo ""
echo "📋 Recent Commits:"
git log --oneline -3

# Check working files
echo ""
echo "🔍 Critical Files Status:"
if [ -f "frontend/src/App.tsx" ]; then
    echo "✅ App.tsx exists"
else
    echo "❌ App.tsx missing!"
fi

if [ -f "frontend/src/main.tsx" ]; then
    echo "✅ main.tsx exists"
else
    echo "❌ main.tsx missing!"
fi

if [ -f "frontend/src/components/layout/NewLayout.tsx" ]; then
    echo "✅ NewLayout.tsx exists"
else
    echo "❌ NewLayout.tsx missing!"
fi

echo ""
echo "🎯 Ready for development!"
