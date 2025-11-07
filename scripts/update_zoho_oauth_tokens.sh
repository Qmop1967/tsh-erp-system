#!/bin/bash

# Zoho OAuth Token Update Script
# This script helps you update Zoho OAuth tokens after updating the scope in Zoho API Console

set -e

echo "=========================================="
echo "Zoho OAuth Token Update Helper"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${YELLOW}This script will help you update Zoho OAuth tokens after updating the scope.${NC}"
echo ""
echo -e "${BLUE}Prerequisites:${NC}"
echo "1. You must have updated the OAuth scope in Zoho API Console"
echo "2. You need your Zoho Client ID, Client Secret, and Redirect URI"
echo ""

# Step 1: Get OAuth credentials from current .env
echo -e "${YELLOW}Step 1: Checking current OAuth configuration...${NC}"
ssh root@167.71.39.50 'cd /home/deploy/TSH_ERP_Ecosystem && grep -E "ZOHO_CLIENT_ID|ZOHO_CLIENT_SECRET|ZOHO_REDIRECT_URI" app/.env' > /tmp/zoho_oauth_config.txt 2>/dev/null || true

if [ -f /tmp/zoho_oauth_config.txt ] && [ -s /tmp/zoho_oauth_config.txt ]; then
    echo -e "${GREEN}✓ Found OAuth configuration${NC}"
    cat /tmp/zoho_oauth_config.txt
    echo ""

    # Extract values
    CLIENT_ID=$(grep ZOHO_CLIENT_ID /tmp/zoho_oauth_config.txt | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    CLIENT_SECRET=$(grep ZOHO_CLIENT_SECRET /tmp/zoho_oauth_config.txt | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    REDIRECT_URI=$(grep ZOHO_REDIRECT_URI /tmp/zoho_oauth_config.txt | cut -d'=' -f2 | tr -d '"' | tr -d "'")
else
    echo -e "${YELLOW}OAuth configuration not found in .env file.${NC}"
    echo -e "${YELLOW}Please enter your Zoho OAuth credentials manually:${NC}"
    echo ""

    read -p "Zoho Client ID: " CLIENT_ID
    read -p "Zoho Client Secret: " CLIENT_SECRET
    read -p "Zoho Redirect URI: " REDIRECT_URI
fi

echo ""

# Step 2: Generate authorization URL
echo -e "${YELLOW}Step 2: Generating Authorization URL...${NC}"
echo ""

AUTH_URL="https://accounts.zoho.com/oauth/v2/auth?scope=ZohoInventory.fullaccess.all,ZohoBooks.fullaccess.all&client_id=${CLIENT_ID}&response_type=code&access_type=offline&redirect_uri=${REDIRECT_URI}"

echo -e "${GREEN}✓ Authorization URL Generated!${NC}"
echo ""
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}COPY AND PASTE THIS URL IN YOUR BROWSER:${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""
echo -e "${YELLOW}${AUTH_URL}${NC}"
echo ""
echo -e "${BLUE}======================================${NC}"
echo ""

echo "Instructions:"
echo "1. Copy the URL above"
echo "2. Paste it in your web browser"
echo "3. Log in to your Zoho account (if not already logged in)"
echo "4. Authorize the application"
echo "5. You will be redirected to your redirect URI with a 'code' parameter"
echo "6. Copy the authorization code from the URL"
echo ""
echo "Example redirect URL:"
echo "https://yourdomain.com/callback?code=YOUR_AUTHORIZATION_CODE"
echo "                                      ^^^^^^^^^^^^^^^^^^^^^^^^"
echo "                                      Copy this part"
echo ""

# Step 3: Get authorization code from user
read -p "Enter the authorization code from the redirect URL: " AUTH_CODE
echo ""

# Step 4: Exchange code for tokens
echo -e "${YELLOW}Step 3: Exchanging authorization code for tokens...${NC}"
echo ""

TOKEN_RESPONSE=$(curl -s -X POST "https://accounts.zoho.com/oauth/v2/token" \
  -d "code=${AUTH_CODE}" \
  -d "client_id=${CLIENT_ID}" \
  -d "client_secret=${CLIENT_SECRET}" \
  -d "redirect_uri=${REDIRECT_URI}" \
  -d "grant_type=authorization_code")

# Check if response contains access_token
if echo "$TOKEN_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✓ Successfully obtained tokens!${NC}"
    echo ""

    # Extract tokens
    ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    REFRESH_TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"refresh_token":"[^"]*"' | cut -d'"' -f4)

    echo "Access Token: ${ACCESS_TOKEN:0:30}..."
    echo "Refresh Token: ${REFRESH_TOKEN:0:30}..."
    echo ""

    # Step 5: Update .env file on VPS
    echo -e "${YELLOW}Step 4: Updating .env file on VPS...${NC}"

    ssh root@167.71.39.50 << EOF
cd /home/deploy/TSH_ERP_Ecosystem/app
cp .env .env.backup.\$(date +%Y%m%d_%H%M%S)
sed -i 's/ZOHO_ACCESS_TOKEN=.*/ZOHO_ACCESS_TOKEN="${ACCESS_TOKEN}"/' .env
sed -i 's/ZOHO_REFRESH_TOKEN=.*/ZOHO_REFRESH_TOKEN="${REFRESH_TOKEN}"/' .env
echo "✓ Updated .env file"
echo "✓ Created backup: .env.backup.\$(date +%Y%m%d_%H%M%S)"
EOF

    echo -e "${GREEN}✓ Environment file updated${NC}"
    echo ""

    # Step 6: Restart service
    echo -e "${YELLOW}Step 5: Restarting TSH ERP service...${NC}"
    ssh root@167.71.39.50 'systemctl restart tsh-erp && sleep 2 && systemctl status tsh-erp --no-pager | head -20'
    echo ""
    echo -e "${GREEN}✓ Service restarted${NC}"
    echo ""

    # Step 7: Test image access
    echo -e "${YELLOW}Step 6: Testing image access...${NC}"
    echo ""

    TEST_ITEM_ID="2646610000000114330"
    TEST_URL="https://erp.tsh.sale/api/zoho/image/${TEST_ITEM_ID}"

    echo "Testing image endpoint: ${TEST_URL}"

    CONTENT_TYPE=$(curl -s -I "${TEST_URL}" | grep -i "content-type" | cut -d':' -f2 | tr -d ' \r\n')

    if echo "$CONTENT_TYPE" | grep -q "image"; then
        echo -e "${GREEN}✓ SUCCESS! Image endpoint is working!${NC}"
        echo -e "${GREEN}Content-Type: ${CONTENT_TYPE}${NC}"
        echo ""
        echo -e "${GREEN}=========================================="
        echo -e "✓ OAuth Update Complete!"
        echo -e "==========================================${NC}"
        echo ""
        echo "Next steps:"
        echo "1. Visit https://consumer.tsh.sale/clear-cache.html to clear Flutter cache"
        echo "2. Visit https://consumer.tsh.sale to see product images"
        echo "3. Images should now load correctly!"
        echo ""
    else
        echo -e "${RED}⚠ Warning: Image endpoint returned unexpected content type${NC}"
        echo "Content-Type: ${CONTENT_TYPE}"
        echo ""
        echo "Please check the logs:"
        echo "ssh root@167.71.39.50 'journalctl -u tsh-erp -n 50 --no-pager'"
    fi

else
    echo -e "${RED}✗ Failed to obtain tokens${NC}"
    echo ""
    echo "Response from Zoho:"
    echo "$TOKEN_RESPONSE"
    echo ""
    echo "Common issues:"
    echo "1. Authorization code might have expired (try again)"
    echo "2. Client ID, Client Secret, or Redirect URI might be incorrect"
    echo "3. The code might have already been used (get a new one)"
    exit 1
fi

# Cleanup
rm -f /tmp/zoho_oauth_config.txt

echo ""
echo -e "${BLUE}Script completed!${NC}"
