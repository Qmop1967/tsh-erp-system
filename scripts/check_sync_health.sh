#!/bin/bash
###############################################################################
# TSH ERP - Zoho Sync Health Check
#
# Monitors the health of Zoho synchronization
#
# Usage:
#   ./scripts/check_sync_health.sh
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

# Database connection (use environment variables or defaults)
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-tsh_erp_production}"
DB_USER="${DB_USER:-tsh_app_user}"
DB_PASSWORD="${DB_PASSWORD:-changeme123}"

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}TSH ERP - Zoho Sync Health Check${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""

# Function to run SQL query
run_query() {
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "$1" 2>/dev/null
}

# Check database connection
echo -e "${YELLOW}Checking database connection...${NC}"
if run_query "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Database connected${NC}"
else
    echo -e "${RED}✗ Database connection failed${NC}"
    exit 1
fi
echo ""

# Check products sync
echo -e "${YELLOW}Checking products sync...${NC}"
PRODUCTS_COUNT=$(run_query "SELECT COUNT(*) FROM products WHERE is_active = true;" | tr -d ' ')
PRODUCTS_WITH_ZOHO=$(run_query "SELECT COUNT(*) FROM products WHERE zoho_item_id IS NOT NULL;" | tr -d ' ')
PRODUCTS_UPDATED_TODAY=$(run_query "SELECT COUNT(*) FROM products WHERE updated_at::date = CURRENT_DATE;" | tr -d ' ')

echo -e "  Total active products: ${GREEN}$PRODUCTS_COUNT${NC}"
echo -e "  Synced from Zoho: ${GREEN}$PRODUCTS_WITH_ZOHO${NC}"
echo -e "  Updated today: ${BLUE}$PRODUCTS_UPDATED_TODAY${NC}"
echo ""

# Check warehouses
echo -e "${YELLOW}Checking warehouses...${NC}"
WAREHOUSES_COUNT=$(run_query "SELECT COUNT(*) FROM warehouses;" | tr -d ' ')
echo -e "  Total warehouses: ${GREEN}$WAREHOUSES_COUNT${NC}"
echo ""

# Check branches
echo -e "${YELLOW}Checking branches...${NC}"
BRANCHES_COUNT=$(run_query "SELECT COUNT(*) FROM branches;" | tr -d ' ')
echo -e "  Total branches: ${GREEN}$BRANCHES_COUNT${NC}"
echo ""

# Check recent sync logs
echo -e "${YELLOW}Checking recent sync logs...${NC}"
LOG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/logs/zoho_sync"
if [ -d "$LOG_DIR" ]; then
    RECENT_LOGS=$(find "$LOG_DIR" -name "sync_*.log" -mtime -7 | wc -l | tr -d ' ')
    echo -e "  Sync logs (last 7 days): ${GREEN}$RECENT_LOGS${NC}"

    if [ -f "$LOG_DIR/cron.log" ]; then
        LAST_SYNC=$(tail -20 "$LOG_DIR/cron.log" | grep "Sync completed" | tail -1)
        if [ -n "$LAST_SYNC" ]; then
            echo -e "  Last sync: ${BLUE}$LAST_SYNC${NC}"
        fi
    fi
else
    echo -e "  ${YELLOW}No sync logs found${NC}"
fi
echo ""

# Check Zoho credentials
echo -e "${YELLOW}Checking Zoho credentials...${NC}"
if [ -f ".env" ]; then
    if grep -q "ZOHO_CLIENT_ID" .env && grep -q "ZOHO_ORGANIZATION_ID" .env; then
        ORG_ID=$(grep "ZOHO_ORGANIZATION_ID" .env | cut -d '=' -f2)
        echo -e "  ${GREEN}✓ Zoho credentials configured${NC}"
        echo -e "  Organization ID: ${BLUE}$ORG_ID${NC}"
    else
        echo -e "  ${RED}✗ Missing Zoho credentials${NC}"
    fi
else
    echo -e "  ${RED}✗ .env file not found${NC}"
fi
echo ""

# Health score calculation
HEALTH_SCORE=100

if [ "$PRODUCTS_COUNT" -lt 100 ]; then
    HEALTH_SCORE=$((HEALTH_SCORE - 30))
fi

if [ "$PRODUCTS_WITH_ZOHO" -lt "$((PRODUCTS_COUNT * 80 / 100))" ]; then
    HEALTH_SCORE=$((HEALTH_SCORE - 20))
fi

if [ "$WAREHOUSES_COUNT" -eq 0 ]; then
    HEALTH_SCORE=$((HEALTH_SCORE - 15))
fi

if [ "$BRANCHES_COUNT" -eq 0 ]; then
    HEALTH_SCORE=$((HEALTH_SCORE - 10))
fi

# Display health score
echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}Health Score: ${NC}"
if [ "$HEALTH_SCORE" -ge 90 ]; then
    echo -e "${GREEN}$HEALTH_SCORE/100 - EXCELLENT ✓${NC}"
elif [ "$HEALTH_SCORE" -ge 70 ]; then
    echo -e "${YELLOW}$HEALTH_SCORE/100 - GOOD${NC}"
elif [ "$HEALTH_SCORE" -ge 50 ]; then
    echo -e "${YELLOW}$HEALTH_SCORE/100 - FAIR ⚠️${NC}"
else
    echo -e "${RED}$HEALTH_SCORE/100 - POOR ✗${NC}"
fi
echo -e "${BLUE}==========================================${NC}"
echo ""

# Recommendations
if [ "$HEALTH_SCORE" -lt 90 ]; then
    echo -e "${YELLOW}Recommendations:${NC}"

    if [ "$PRODUCTS_COUNT" -lt 100 ]; then
        echo -e "  - Run full product sync: ${BLUE}./scripts/run_manual_sync.sh products${NC}"
    fi

    if [ "$WAREHOUSES_COUNT" -eq 0 ]; then
        echo -e "  - Set up warehouses in the database"
    fi

    if [ "$BRANCHES_COUNT" -eq 0 ]; then
        echo -e "  - Set up branches in the database"
    fi

    echo ""
fi

exit 0
