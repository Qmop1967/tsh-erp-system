#!/bin/bash
###############################################################################
# TSH ERP - Daily Zoho Sync Automation Setup
#
# This script sets up automated daily synchronization with Zoho Books
#
# Usage:
#   ./scripts/setup_daily_sync.sh
#
# Author: TSH ERP Team
# Date: November 14, 2025
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}TSH ERP - Daily Sync Automation Setup${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo -e "${YELLOW}⚠️  Running inside Docker container${NC}"
    PYTHON_CMD="python3"
    SCRIPT_PATH="/app/run_complete_zoho_sync.py"
else
    echo -e "${GREEN}✓ Running on host machine${NC}"
    PYTHON_CMD="python3"
    SCRIPT_PATH="$PROJECT_ROOT/run_complete_zoho_sync.py"
fi

# Create log directory
LOG_DIR="$PROJECT_ROOT/logs/zoho_sync"
mkdir -p "$LOG_DIR"
echo -e "${GREEN}✓ Log directory created: $LOG_DIR${NC}"

# Create cron script
CRON_SCRIPT="$PROJECT_ROOT/scripts/run_daily_sync.sh"

cat > "$CRON_SCRIPT" << 'EOF'
#!/bin/bash
###############################################################################
# Daily Zoho Sync - Cron Job Script
# Automatically syncs all Zoho Books data daily
###############################################################################

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Logging
LOG_DIR="$PROJECT_ROOT/logs/zoho_sync"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/sync_$(date +%Y%m%d_%H%M%S).log"

# Run sync
echo "======================================" | tee -a "$LOG_FILE"
echo "Starting Zoho Sync: $(date)" | tee -a "$LOG_FILE"
echo "======================================" | tee -a "$LOG_FILE"

# Activate virtual environment if exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Run complete sync
python3 run_complete_zoho_sync.py --mode incremental 2>&1 | tee -a "$LOG_FILE"

EXITCODE=$?

echo "======================================" | tee -a "$LOG_FILE"
echo "Sync completed: $(date)" | tee -a "$LOG_FILE"
echo "Exit code: $EXITCODE" | tee -a "$LOG_FILE"
echo "======================================" | tee -a "$LOG_FILE"

# Clean up old logs (keep last 30 days)
find "$LOG_DIR" -name "sync_*.log" -mtime +30 -delete

exit $EXITCODE
EOF

chmod +x "$CRON_SCRIPT"
echo -e "${GREEN}✓ Cron script created: $CRON_SCRIPT${NC}"

# Create cron job
echo ""
echo -e "${YELLOW}Setting up cron job...${NC}"

# Cron schedule: Every day at 2:00 AM
CRON_SCHEDULE="0 2 * * *"
CRON_JOB="$CRON_SCHEDULE $CRON_SCRIPT >> $LOG_DIR/cron.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "$CRON_SCRIPT"; then
    echo -e "${YELLOW}⚠️  Cron job already exists${NC}"
else
    # Add cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo -e "${GREEN}✓ Cron job added${NC}"
fi

# Display current cron jobs
echo ""
echo -e "${BLUE}Current cron jobs:${NC}"
crontab -l | grep -v "^#" | grep -v "^$" || echo "No cron jobs"

# Create manual run script
MANUAL_SCRIPT="$PROJECT_ROOT/scripts/run_manual_sync.sh"
cat > "$MANUAL_SCRIPT" << 'EOF'
#!/bin/bash
###############################################################################
# Manual Zoho Sync Runner
# Run this script to manually trigger a Zoho sync
###############################################################################

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "========================================"
echo "Manual Zoho Sync"
echo "========================================"
echo ""

# Check for arguments
if [ "$1" == "full" ]; then
    echo "Running FULL sync..."
    python3 run_complete_zoho_sync.py --mode full
elif [ "$1" == "products" ]; then
    echo "Syncing PRODUCTS only..."
    python3 run_complete_zoho_sync.py --entities products stock
elif [ "$1" == "customers" ]; then
    echo "Syncing CUSTOMERS only..."
    python3 run_complete_zoho_sync.py --entities customers
else
    echo "Running INCREMENTAL sync (default)..."
    python3 run_complete_zoho_sync.py --mode incremental
fi

echo ""
echo "========================================"
echo "Sync completed!"
echo "========================================"
EOF

chmod +x "$MANUAL_SCRIPT"
echo -e "${GREEN}✓ Manual run script created: $MANUAL_SCRIPT${NC}"

# Summary
echo ""
echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}Setup Complete!${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""
echo -e "${GREEN}✓ Daily sync scheduled at 2:00 AM${NC}"
echo -e "${GREEN}✓ Logs will be stored in: $LOG_DIR${NC}"
echo ""
echo -e "${YELLOW}Manual sync commands:${NC}"
echo -e "  Full sync:         ${BLUE}./scripts/run_manual_sync.sh full${NC}"
echo -e "  Products only:     ${BLUE}./scripts/run_manual_sync.sh products${NC}"
echo -e "  Customers only:    ${BLUE}./scripts/run_manual_sync.sh customers${NC}"
echo -e "  Incremental (default): ${BLUE}./scripts/run_manual_sync.sh${NC}"
echo ""
echo -e "${YELLOW}View logs:${NC}"
echo -e "  ${BLUE}tail -f $LOG_DIR/cron.log${NC}"
echo -e "  ${BLUE}ls -lth $LOG_DIR/${NC}"
echo ""
