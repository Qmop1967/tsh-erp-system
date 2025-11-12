#!/bin/bash

################################################################################
# DIRECT DEPLOYMENT TO PRODUCTION
################################################################################
#
# Deploys code directly from development environment to production VPS
# WITHOUT going through GitHub
#
# This is the PRIMARY deployment method for TSH ERP System
#
# Author: TSH Development Team
# Date: November 9, 2025
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PRODUCTION_HOST="tsh-vps"
PRODUCTION_PATH="/home/deploy/TSH_ERP_Ecosystem"
LOCAL_PATH="$(cd "$(dirname "$0")/.." && pwd)"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         DIRECT DEPLOYMENT TO PRODUCTION                          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo

# Step 1: Pre-deployment validation
echo -e "${YELLOW}[1/6] Pre-deployment validation...${NC}"

# Check if we're in the correct directory
if [ ! -f "$LOCAL_PATH/app/main.py" ]; then
    echo -e "${RED}❌ Error: Not in TSH_ERP_Ecosystem directory${NC}"
    exit 1
fi

# Check SSH connection
if ! ssh -q "$PRODUCTION_HOST" exit; then
    echo -e "${RED}❌ Error: Cannot connect to production server${NC}"
    echo -e "${YELLOW}   Make sure SSH is configured: ssh $PRODUCTION_HOST${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Pre-deployment validation passed${NC}"
echo

# Step 2: Show what will be deployed
echo -e "${YELLOW}[2/6] Checking for changes...${NC}"

# Get list of modified files
MODIFIED_FILES=$(git status --short | wc -l)
CURRENT_BRANCH=$(git branch --show-current)
LAST_COMMIT=$(git log -1 --pretty=format:"%h - %s")

echo -e "   Current branch: ${GREEN}$CURRENT_BRANCH${NC}"
echo -e "   Last commit: ${GREEN}$LAST_COMMIT${NC}"
echo -e "   Modified files: ${GREEN}$MODIFIED_FILES${NC}"
echo

# Step 3: Confirm deployment
echo -e "${YELLOW}[3/6] Deployment confirmation...${NC}"
echo -e "${BLUE}   This will deploy the following to production:${NC}"
echo -e "   Source: $LOCAL_PATH"
echo -e "   Target: $PRODUCTION_HOST:$PRODUCTION_PATH"
echo

read -p "   Continue with deployment? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo -e "${RED}Deployment cancelled${NC}"
    exit 0
fi

# Step 4: Sync files to production
echo -e "${YELLOW}[4/6] Syncing files to production...${NC}"

# Exclude patterns
EXCLUDE_PATTERNS=(
    ".git"
    ".github"
    "__pycache__"
    "*.pyc"
    ".env"
    ".venv"
    "venv"
    "node_modules"
    ".DS_Store"
    "*.log"
    ".pytest_cache"
    ".coverage"
    "htmlcov"
    "dist"
    "build"
    "*.egg-info"
)

# Build rsync exclude arguments
RSYNC_EXCLUDES=""
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    RSYNC_EXCLUDES="$RSYNC_EXCLUDES --exclude=$pattern"
done

# Sync files using rsync
rsync -avz --delete \
    $RSYNC_EXCLUDES \
    --progress \
    "$LOCAL_PATH/" \
    "$PRODUCTION_HOST:$PRODUCTION_PATH/"

echo -e "${GREEN}✅ Files synced successfully${NC}"
echo

# Step 5: Clear Python cache and rebuild Docker
echo -e "${YELLOW}[5/6] Rebuilding production environment...${NC}"

ssh "$PRODUCTION_HOST" bash << 'ENDSSH'
set -e

cd /home/deploy/TSH_ERP_Ecosystem

# Clear Python cache
echo "   Clearing Python cache..."
find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find . -name '*.pyc' -delete 2>/dev/null || true

# Rebuild and restart Docker containers
echo "   Rebuilding Docker containers..."
docker compose build app

echo "   Restarting containers..."
docker compose up -d app

echo "   Waiting for container to be healthy..."
sleep 10

ENDSSH

echo -e "${GREEN}✅ Production environment rebuilt${NC}"
echo

# Step 6: Verify deployment
echo -e "${YELLOW}[6/6] Verifying deployment...${NC}"

# Wait a bit for the service to fully start
sleep 5

# Check if the service is healthy
HEALTH_CHECK=$(ssh "$PRODUCTION_HOST" "curl -s http://localhost:8000/api/bff/tds/health | python3 -c 'import sys, json; d=json.load(sys.stdin); print(d.get(\"status\", \"unknown\"))'" 2>/dev/null || echo "failed")

if [ "$HEALTH_CHECK" = "healthy" ]; then
    echo -e "${GREEN}✅ Deployment successful - Service is healthy${NC}"

    # Get version info
    VERSION=$(ssh "$PRODUCTION_HOST" "curl -s http://localhost:8000/api/bff/tds/health | python3 -c 'import sys, json; d=json.load(sys.stdin); print(d.get(\"version\", \"unknown\"))'" 2>/dev/null || echo "unknown")

    echo
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                 DEPLOYMENT COMPLETED SUCCESSFULLY                 ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "${GREEN}   TDS Version: $VERSION${NC}"
    echo -e "${GREEN}   Status: HEALTHY${NC}"
    echo -e "${GREEN}   Production URL: https://erp.tsh.sale${NC}"
    echo
else
    echo -e "${RED}❌ Warning: Service health check failed${NC}"
    echo -e "${YELLOW}   Please check logs manually:${NC}"
    echo -e "${YELLOW}   ssh $PRODUCTION_HOST 'docker logs tsh_erp_app --tail 50'${NC}"
    exit 1
fi

# Show deployment summary
echo -e "${BLUE}Deployment Summary:${NC}"
echo -e "   Branch deployed: $CURRENT_BRANCH"
echo -e "   Last commit: $LAST_COMMIT"
echo -e "   Deployment time: $(date '+%Y-%m-%d %H:%M:%S')"
echo
echo -e "${GREEN}🚀 Production deployment complete!${NC}"
