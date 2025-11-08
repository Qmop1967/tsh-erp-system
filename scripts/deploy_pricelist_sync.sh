#!/bin/bash
#===============================================================================
# TSH ERP - Price List Sync Deployment Script
#===============================================================================
# This script deploys the complete price list sync integration to production
#
# Author: Claude Code (Senior Software Engineer AI)
# Date: November 7, 2025
# Version: 1.0.0
#===============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VPS_HOST="root@167.71.39.50"
DEPLOY_DIR="/home/deploy/TSH_ERP_Ecosystem"
LOCAL_DIR="/Users/khaleelal-mulla/TSH_ERP_Ecosystem"

echo -e "${BLUE}===============================================================================${NC}"
echo -e "${BLUE}TSH ERP - Price List Sync Deployment${NC}"
echo -e "${BLUE}===============================================================================${NC}"
echo ""

# Step 1: Verify files exist locally
echo -e "${YELLOW}Step 1: Verifying local files...${NC}"
FILES_TO_DEPLOY=(
    "app/tds/integrations/zoho/processors/pricelists.py"
    "app/tds/integrations/zoho/processors/__init__.py"
    "app/tds/integrations/zoho/sync.py"
)

for file in "${FILES_TO_DEPLOY[@]}"; do
    if [ ! -f "$LOCAL_DIR/$file" ]; then
        echo -e "${RED}❌ Error: File not found: $file${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Found: $file${NC}"
done

echo ""

# Step 2: Backup production files
echo -e "${YELLOW}Step 2: Backing up production files...${NC}"
BACKUP_DIR="/home/deploy/backups/pricelist_sync_$(date +%Y%m%d_%H%M%S)"
ssh $VPS_HOST "mkdir -p $BACKUP_DIR"

for file in "${FILES_TO_DEPLOY[@]}"; do
    ssh $VPS_HOST "cp $DEPLOY_DIR/$file $BACKUP_DIR/ 2>/dev/null || true"
done

echo -e "${GREEN}✅ Backup created at: $BACKUP_DIR${NC}"
echo ""

# Step 3: Deploy files
echo -e "${YELLOW}Step 3: Deploying files to production...${NC}"

for file in "${FILES_TO_DEPLOY[@]}"; do
    echo -e "${BLUE}   Deploying: $file${NC}"
    scp "$LOCAL_DIR/$file" "$VPS_HOST:$DEPLOY_DIR/$file"
done

echo -e "${GREEN}✅ All files deployed successfully${NC}"
echo ""

# Step 4: Restart Docker container
echo -e "${YELLOW}Step 4: Restarting Docker container...${NC}"
ssh $VPS_HOST "docker restart tsh_erp_app"
echo -e "${GREEN}✅ Container restarted${NC}"
echo ""

# Step 5: Wait for health check
echo -e "${YELLOW}Step 5: Waiting for application to be healthy...${NC}"
sleep 15

# Check container health
CONTAINER_STATUS=$(ssh $VPS_HOST "docker inspect --format='{{.State.Health.Status}}' tsh_erp_app 2>/dev/null || echo 'unknown'")

if [ "$CONTAINER_STATUS" == "healthy" ]; then
    echo -e "${GREEN}✅ Application is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Container status: $CONTAINER_STATUS${NC}"
    echo -e "${YELLOW}   Checking logs...${NC}"
    ssh $VPS_HOST "docker logs tsh_erp_app --tail 20"
fi

echo ""

# Step 6: Run price list sync
echo -e "${YELLOW}Step 6: Running price list sync...${NC}"
echo -e "${BLUE}   This will sync all price lists from Zoho Books...${NC}"
echo ""

# Run sync via API
SYNC_RESULT=$(curl -X POST https://erp.tsh.sale/api/zoho/bulk-sync/pricelists \
    -H "Content-Type: application/json" \
    -s -w "\nHTTP_CODE:%{http_code}")

HTTP_CODE=$(echo "$SYNC_RESULT" | grep "HTTP_CODE" | cut -d':' -f2)
RESPONSE=$(echo "$SYNC_RESULT" | sed '/HTTP_CODE/d')

echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

if [ "$HTTP_CODE" == "200" ]; then
    echo -e "${GREEN}✅ Sync completed successfully${NC}"
else
    echo -e "${RED}❌ Sync failed with HTTP code: $HTTP_CODE${NC}"
fi

echo ""

# Step 7: Verify database
echo -e "${YELLOW}Step 7: Verifying price lists in database...${NC}"

PRICE_LIST_COUNT=$(ssh $VPS_HOST "docker exec tsh_postgres psql -U tsh_admin -d tsh_erp -t -c 'SELECT COUNT(*) FROM price_lists;'" | tr -d ' ')

if [ "$PRICE_LIST_COUNT" -gt "0" ]; then
    echo -e "${GREEN}✅ Found $PRICE_LIST_COUNT price lists in database${NC}"

    # Show price list details
    echo ""
    echo -e "${BLUE}Price Lists:${NC}"
    ssh $VPS_HOST "docker exec tsh_postgres psql -U tsh_admin -d tsh_erp -c \"SELECT code, name_en, currency, is_active FROM price_lists ORDER BY code;\""
else
    echo -e "${RED}❌ No price lists found in database${NC}"
    echo -e "${YELLOW}   Check sync logs for errors${NC}"
fi

echo ""
echo -e "${BLUE}===============================================================================${NC}"
echo -e "${GREEN}✨ Deployment Complete!${NC}"
echo -e "${BLUE}===============================================================================${NC}"
echo ""
echo -e "${BLUE}Backup location:${NC} $BACKUP_DIR"
echo -e "${BLUE}Deployed files:${NC} ${#FILES_TO_DEPLOY[@]}"
echo -e "${BLUE}Price lists in DB:${NC} $PRICE_LIST_COUNT"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Verify price lists are correct in database"
echo "  2. Test API endpoints: GET /api/pricelists"
echo "  3. Monitor sync logs for any issues"
echo ""
