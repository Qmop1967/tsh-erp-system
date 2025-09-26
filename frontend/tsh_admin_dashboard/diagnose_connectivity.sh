#!/bin/bash

echo "🔍 TSH Admin App - Connectivity Diagnostics"
echo "============================================"
echo ""

# Get Mac IP address
MAC_IP=$(ifconfig | grep -E "inet.*broadcast" | grep -v "127.0.0.1" | awk '{print $2}' | head -1)

echo "📊 Network Information:"
echo "   • Mac IP Address: $MAC_IP"
echo "   • Current localhost endpoints in app: http://localhost:8000"
echo "   • Required iPhone endpoint: http://$MAC_IP:8000"
echo ""

echo "🔍 Backend Server Status:"
# Check if backend is running on localhost
if curl -s "http://localhost:8000/health" > /dev/null 2>&1; then
    echo "   ✅ Backend server is running on localhost:8000"
    
    # Check if accessible from network IP
    if curl -s "http://$MAC_IP:8000/health" > /dev/null 2>&1; then
        echo "   ✅ Backend server is accessible from network IP"
    else
        echo "   ❌ Backend server is NOT accessible from network IP"
        echo "   💡 Server may be bound to localhost only"
    fi
else
    echo "   ❌ Backend server is NOT running"
    echo "   💡 Start with: python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
fi
echo ""

echo "🔥 Firewall Status:"
if sudo pfctl -sr | grep -q "block.*8000" 2>/dev/null; then
    echo "   ⚠️  Port 8000 may be blocked by firewall"
else
    echo "   ✅ No obvious firewall blocks detected"
fi
echo ""

echo "📱 iPhone Connection Checklist:"
echo "   1. ✓ App installed on iPhone"
echo "   2. ? App configured for correct IP address"
echo "   3. ? Backend server accessible from network"
echo "   4. ? Developer certificate trusted on iPhone"
echo "   5. ? iPhone and Mac on same WiFi network"
echo ""

echo "🛠️  Recommended Fix Steps:"
echo "   1. Run the main script with option 2 (Fix app accessibility)"
echo "   2. Ensure backend is started with --host 0.0.0.0"
echo "   3. Trust developer certificate on iPhone"
echo "   4. Rebuild and redeploy the app"
echo ""

echo "📋 Quick Commands:"
echo "   • Check WiFi network: networksetup -getairportnetwork en0"
echo "   • Test connectivity: ping $MAC_IP"
echo "   • View firewall rules: sudo pfctl -sr | grep 8000"
echo ""
