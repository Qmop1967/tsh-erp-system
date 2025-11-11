#!/bin/bash
################################################################################
# Quick Deployment Trigger Script
# Triggers deployment to production server
# Usage: ./trigger-deploy.sh
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SERVER="167.71.39.50"
USER="root"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   TSH ERP - Production Deployment Trigger               ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if we can connect to server
echo -e "${BLUE}Checking server connectivity...${NC}"
if ! ssh -o ConnectTimeout=10 "$USER@$SERVER" "echo ''" 2>/dev/null; then
    echo -e "${RED}✗ Cannot connect to server${NC}"
    echo -e "${YELLOW}Make sure you can SSH to $USER@$SERVER${NC}"
    echo -e "${YELLOW}Run: ssh-copy-id $USER@$SERVER${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Server connected${NC}"
echo ""

# Ask for confirmation
echo -e "${YELLOW}This will deploy the latest code from main branch to production.${NC}"
echo -e "${YELLOW}Server: $SERVER${NC}"
echo ""
read -p "Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${YELLOW}Deployment cancelled${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}Starting deployment...${NC}"
echo ""

# Execute deployment on server
ssh "$USER@$SERVER" 'bash -s' << 'ENDSSH'
echo "Connected to server. Running deployment script..."
echo ""

# Check if deployment script exists
if [ ! -f /opt/tsh_erp/bin/deploy.sh ]; then
    echo "ERROR: Deployment script not found at /opt/tsh_erp/bin/deploy.sh"
    echo "Please set up the server infrastructure first (see DEPLOY_NOW.md)"
    exit 1
fi

# Run deployment
bash /opt/tsh_erp/bin/deploy.sh main

ENDSSH

DEPLOY_STATUS=$?

echo ""
if [ $DEPLOY_STATUS -eq 0 ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   ✓ Deployment Successful!                              ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Verify deployment:${NC}"
    echo "  curl http://$SERVER/health"
    echo ""
    echo -e "${BLUE}Check logs:${NC}"
    echo "  ssh $USER@$SERVER 'journalctl -u tsh_erp-blue -f'"
    echo "  ssh $USER@$SERVER 'journalctl -u tsh_erp-green -f'"
    echo ""
else
    echo -e "${RED}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║   ✗ Deployment Failed                                    ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Check deployment logs:${NC}"
    echo "  ssh $USER@$SERVER 'tail -f /opt/tsh_erp/shared/logs/api/deploy_*.log'"
    echo ""
    echo -e "${YELLOW}Check service logs:${NC}"
    echo "  ssh $USER@$SERVER 'journalctl -u tsh_erp-blue -n 100'"
    echo "  ssh $USER@$SERVER 'journalctl -u tsh_erp-green -n 100'"
    echo ""
    exit 1
fi
