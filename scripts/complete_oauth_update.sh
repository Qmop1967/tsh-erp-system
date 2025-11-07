#!/bin/bash

# TSH ERP - Complete OAuth Update Script
# This script will help you update Zoho OAuth tokens with image access scope

set -e

echo "============================================================"
echo "TSH ERP - Zoho OAuth Update for Image Access"
echo "============================================================"
echo ""

# OAuth credentials
CLIENT_ID="1000.SLY5X93N58VN46HXQIIZSOQKG8J3ZJ"
CLIENT_SECRET="0581c245cd951e1453042ff2bcf223768e128fed9f"
REDIRECT_URI="https://www.zoho.com"

# Generate authorization URL
AUTH_URL="https://accounts.zoho.com/oauth/v2/auth?scope=ZohoInventory.fullaccess.all,ZohoBooks.fullaccess.all&client_id=${CLIENT_ID}&response_type=code&access_type=offline&redirect_uri=${REDIRECT_URI}&prompt=consent"

echo "📋 Step 1: Get Authorization Code"
echo "=================================="
echo ""
echo "I will open your browser to the Zoho authorization page."
echo "Please:"
echo "  1. Sign in to Zoho (if not already logged in)"
echo "  2. Click 'Accept' to grant permissions"
echo "  3. Copy the authorization code from the URL"
echo "     (the part after 'code=')"
echo ""
echo "⚠️  IMPORTANT: The code expires in 60 seconds!"
echo ""
read -p "Press Enter to open the browser..."

# Open browser
open "$AUTH_URL"

echo ""
echo "Browser opened. After you authorize, the URL will look like:"
echo "https://www.zoho.com/?code=XXXXXXXXX"
echo ""
read -p "Enter the authorization code: " AUTH_CODE

if [ -z "$AUTH_CODE" ]; then
    echo "❌ Error: No authorization code provided"
    exit 1
fi

echo ""
echo "📋 Step 2: Exchange Code for Tokens"
echo "===================================="
echo ""
echo "Requesting tokens from Zoho..."

# Exchange code for tokens
RESPONSE=$(curl -s -X POST "https://accounts.zoho.com/oauth/v2/token" \
  -d "code=$AUTH_CODE" \
  -d "client_id=$CLIENT_ID" \
  -d "client_secret=$CLIENT_SECRET" \
  -d "redirect_uri=$REDIRECT_URI" \
  -d "grant_type=authorization_code")

# Check if response contains error
if echo "$RESPONSE" | grep -q "error"; then
    echo "❌ Error getting tokens:"
    echo "$RESPONSE"
    echo ""
    echo "Common issues:"
    echo "  - Authorization code expired (try again, you have 60 seconds)"
    echo "  - Invalid authorization code"
    echo "  - Code already used (get a new one)"
    exit 1
fi

# Extract tokens
ACCESS_TOKEN=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))")
REFRESH_TOKEN=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('refresh_token', ''))")

if [ -z "$ACCESS_TOKEN" ] || [ -z "$REFRESH_TOKEN" ]; then
    echo "❌ Error: Could not extract tokens from response"
    echo "$RESPONSE"
    exit 1
fi

echo "✅ Tokens received successfully!"
echo ""
echo "Access Token: ${ACCESS_TOKEN:0:20}..."
echo "Refresh Token: ${REFRESH_TOKEN:0:20}..."
echo ""

echo "📋 Step 3: Update .env File on VPS"
echo "==================================="
echo ""
echo "Updating tokens on VPS..."

# Update .env file on VPS
ssh root@167.71.39.50 "cd /home/deploy/TSH_ERP_Ecosystem && \
  sed -i 's|^ZOHO_ACCESS_TOKEN=.*|ZOHO_ACCESS_TOKEN=\"$ACCESS_TOKEN\"|' app/.env && \
  sed -i 's|^ZOHO_REFRESH_TOKEN=.*|ZOHO_REFRESH_TOKEN=\"$REFRESH_TOKEN\"|' app/.env"

echo "✅ .env file updated"
echo ""

echo "📋 Step 4: Restart TSH ERP Service"
echo "==================================="
echo ""
echo "Restarting service..."

ssh root@167.71.39.50 "systemctl restart tsh-erp"
sleep 3

# Check service status
SERVICE_STATUS=$(ssh root@167.71.39.50 "systemctl is-active tsh-erp")

if [ "$SERVICE_STATUS" = "active" ]; then
    echo "✅ Service restarted successfully"
else
    echo "⚠️  Service status: $SERVICE_STATUS"
    echo "Check logs: ssh root@167.71.39.50 'journalctl -u tsh-erp -n 50'"
fi

echo ""

echo "📋 Step 5: Test Image Access"
echo "============================="
echo ""
echo "Testing image endpoint..."

# Test image access
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://erp.tsh.sale/api/zoho/image/2646610000000114330")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Image access working! (HTTP $HTTP_CODE)"
    echo ""
    echo "🎉 SUCCESS! OAuth update complete!"
    echo ""
    echo "📋 Next Steps:"
    echo "=============="
    echo ""
    echo "1. Download all product images:"
    echo "   ssh root@167.71.39.50 'cd /home/deploy/TSH_ERP_Ecosystem && source venv/bin/activate && python3 scripts/download_zoho_images.py'"
    echo ""
    echo "2. Clear Flutter cache on your device:"
    echo "   Visit: https://consumer.tsh.sale/force-reload.html?auto=1"
    echo ""
    echo "3. Check the consumer app:"
    echo "   Visit: https://consumer.tsh.sale"
    echo ""
    echo "✨ Your product images should now display!"

else
    echo "⚠️  Image endpoint returned HTTP $HTTP_CODE"
    echo ""
    echo "Expected: 200"
    echo "Got: $HTTP_CODE"
    echo ""
    echo "Troubleshooting:"
    echo "  - Check service logs: ssh root@167.71.39.50 'journalctl -u tsh-erp -n 50'"
    echo "  - Verify tokens: ssh root@167.71.39.50 'cat /home/deploy/TSH_ERP_Ecosystem/app/.env | grep ZOHO_'"
    echo "  - Try manual test: curl -I https://erp.tsh.sale/api/zoho/image/2646610000000114330"
fi

echo ""
echo "============================================================"
echo "Script complete!"
echo "============================================================"
