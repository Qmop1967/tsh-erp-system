#!/bin/bash
###############################################################################
# TDS Dashboard 404 Fix Deployment Script
#
# This script deploys the TDS dashboard fix to production:
# 1. Updates Next.js basePath configuration
# 2. Rebuilds Docker image
# 3. Updates Nginx configuration
# 4. Restarts services
#
# Usage:
#   ./scripts/deploy_tds_dashboard_fix.sh
#
# Author: TSH ERP Team
# Date: November 14, 2025
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}TDS Dashboard 404 Fix - Production Deployment${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""

# Production server details
PROD_SERVER="root@167.71.39.50"
APP_DIR="/root/tsh-erp-deployment"

echo -e "${YELLOW}Step 1: Building Docker image locally...${NC}"
cd apps/tds_admin_dashboard
docker build -t tds-admin-dashboard:latest .
cd ../..
echo -e "${GREEN}✓ Docker image built successfully${NC}"
echo ""

echo -e "${YELLOW}Step 2: Saving Docker image...${NC}"
docker save tds-admin-dashboard:latest | gzip > /tmp/tds-admin-dashboard.tar.gz
echo -e "${GREEN}✓ Docker image saved${NC}"
echo ""

echo -e "${YELLOW}Step 3: Transferring image to production...${NC}"
scp /tmp/tds-admin-dashboard.tar.gz $PROD_SERVER:/tmp/
echo -e "${GREEN}✓ Image transferred${NC}"
echo ""

echo -e "${YELLOW}Step 4: Loading image on production...${NC}"
ssh $PROD_SERVER "docker load < /tmp/tds-admin-dashboard.tar.gz"
echo -e "${GREEN}✓ Image loaded${NC}"
echo ""

echo -e "${YELLOW}Step 5: Updating Nginx configuration...${NC}"
ssh $PROD_SERVER "sed -i.backup 's|proxy_pass http://tds_dashboard/;|proxy_pass http://tds_dashboard;|g' /etc/nginx/sites-enabled/tsh_erp.conf"
echo -e "${GREEN}✓ Nginx configuration updated${NC}"
echo ""

echo -e "${YELLOW}Step 6: Testing Nginx configuration...${NC}"
ssh $PROD_SERVER "nginx -t"
echo -e "${GREEN}✓ Nginx configuration valid${NC}"
echo ""

echo -e "${YELLOW}Step 7: Reloading Nginx...${NC}"
ssh $PROD_SERVER "systemctl reload nginx"
echo -e "${GREEN}✓ Nginx reloaded${NC}"
echo ""

echo -e "${YELLOW}Step 8: Restarting TDS dashboard container...${NC}"
ssh $PROD_SERVER "docker stop tds_admin_dashboard && docker rm tds_admin_dashboard"
ssh $PROD_SERVER "docker run -d \
  --name tds_admin_dashboard \
  --network tsh_network \
  -p 3000:3000 \
  --restart unless-stopped \
  -e NEXT_PUBLIC_API_URL=https://erp.tsh.sale/api \
  tds-admin-dashboard:latest"
echo -e "${GREEN}✓ TDS dashboard restarted${NC}"
echo ""

echo -e "${YELLOW}Step 9: Waiting for container to be healthy...${NC}"
for i in {1..10}; do
    if ssh $PROD_SERVER "docker ps --filter name=tds_admin_dashboard --filter health=healthy --format '{{.Names}}'" | grep -q tds_admin_dashboard; then
        echo -e "${GREEN}✓ Container is healthy${NC}"
        break
    fi
    echo -e "  Waiting... ($i/10)"
    sleep 3
done
echo ""

echo -e "${YELLOW}Step 10: Testing the fix...${NC}"
echo -e "  Testing: https://erp.tsh.sale/tds-admin/"
if curl -skL https://erp.tsh.sale/tds-admin/ | grep -q "TDS Admin Dashboard"; then
    echo -e "${GREEN}✓ TDS Admin Dashboard is accessible!${NC}"
else
    echo -e "${RED}⚠️  Dashboard may not be fully accessible yet${NC}"
fi
echo ""

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}Deployment Complete!${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""
echo -e "${GREEN}✓ TDS Dashboard is now accessible at:${NC}"
echo -e "  ${BLUE}https://erp.tsh.sale/tds-admin/${NC}"
echo ""
echo -e "${YELLOW}Cleanup commands:${NC}"
echo -e "  ${BLUE}rm /tmp/tds-admin-dashboard.tar.gz${NC}"
echo -e "  ${BLUE}ssh $PROD_SERVER 'rm /tmp/tds-admin-dashboard.tar.gz'${NC}"
echo ""
