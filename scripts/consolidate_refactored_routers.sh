#!/bin/bash
#
# Router Consolidation Script
# Automates the consolidation of _refactored router pairs
#
# Following Tronix.md Principles:
# - Search: Find both versions
# - Fix: Keep the refactored (better) version
# - Consolidate: Merge into single file
# - Use: Update imports
# - Document: Log changes
#
# Author: Claude Code
# Date: November 7, 2025

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Router Consolidation Automation"
echo "=========================================="
echo ""

# List of router pairs to consolidate (excluding already done: products, customers)
ROUTERS=(
    "sales"
    "invoices"
    "items"
    "branches"
    "users"
    "vendors"
    "warehouses"
    "money_transfer"
    "trusted_devices"
    "permissions"
    "partner_salesmen"
    "expenses"
    "dashboard"
    "multi_price_system"
    "models"
)

ARCHIVE_DIR="archived/routers/consolidation_nov7_2025"
ROUTERS_DIR="app/routers"

# Counter
CONSOLIDATED=0
SKIPPED=0

for router in "${ROUTERS[@]}"; do
    echo -e "${YELLOW}Processing: ${router}${NC}"

    ORIGINAL="${ROUTERS_DIR}/${router}.py"
    REFACTORED="${ROUTERS_DIR}/${router}_refactored.py"

    # Check if both files exist
    if [ ! -f "$ORIGINAL" ]; then
        echo -e "${RED}  ✗ Original not found: ${ORIGINAL}${NC}"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    if [ ! -f "$REFACTORED" ]; then
        echo -e "${RED}  ✗ Refactored not found: ${REFACTORED}${NC}"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    echo "  ✓ Both files found"

    # Backup originals
    echo "  → Backing up files..."
    cp "$ORIGINAL" "${ARCHIVE_DIR}/${router}_old.py"
    cp "$REFACTORED" "${ARCHIVE_DIR}/${router}_refactored_before_rename.py"

    # Rename and consolidate
    echo "  → Consolidating..."
    mv "$ORIGINAL" "${ROUTERS_DIR}/${router}_deprecated.py"
    cp "$REFACTORED" "$ORIGINAL"

    # Update docstring (add consolidation note)
    sed -i '' '1,30s/Phase.*Router Migration/CONSOLIDATED VERSION - Nov 7, 2025/' "$ORIGINAL"

    # Delete duplicates
    rm "$REFACTORED"
    rm "${ROUTERS_DIR}/${router}_deprecated.py"

    CONSOLIDATED=$((CONSOLIDATED + 1))
    echo -e "${GREEN}  ✓ Consolidated: ${router}.py${NC}"
    echo ""
done

echo "=========================================="
echo "Consolidation Summary"
echo "=========================================="
echo -e "${GREEN}Consolidated: ${CONSOLIDATED}${NC}"
echo -e "${YELLOW}Skipped: ${SKIPPED}${NC}"
echo -e "${GREEN}Total Progress: ${CONSOLIDATED}/15 remaining routers${NC}"
echo ""
echo "✅ Next step: Update main.py imports manually"
echo ""
