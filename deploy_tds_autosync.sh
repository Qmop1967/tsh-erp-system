#!/bin/bash
###############################################################################
# TDS Auto-Sync Deployment Script
###############################################################################
# Deploys TDS Auto-Sync system to production server
#
# Usage:
#   ./deploy_tds_autosync.sh
#
# نشر نظام المزامنة التلقائية TDS
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PRODUCTION_SERVER="root@167.71.39.50"
REMOTE_DIR="/root/TSH_ERP_Ecosystem"
LOCAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         TDS Auto-Sync Deployment to Production Server          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Validate local setup
echo -e "${YELLOW}📋 Step 1: Validating local files...${NC}"
required_files=(
    "tds_compare_and_sync.py"
    "tds_auto_sync_scheduler.py"
    "test_tds_setup.py"
    "app/tds/statistics/engine.py"
    "requirements.txt"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$LOCAL_DIR/$file" ]; then
        echo -e "${RED}❌ Missing required file: $file${NC}"
        exit 1
    fi
done
echo -e "${GREEN}✅ All required files present${NC}"
echo ""

# Step 2: Test SSH connection
echo -e "${YELLOW}📋 Step 2: Testing SSH connection to production...${NC}"
if ssh -o ConnectTimeout=5 -o BatchMode=yes $PRODUCTION_SERVER "echo 2>&1" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ SSH connection successful${NC}"
else
    echo -e "${RED}❌ Cannot connect to production server${NC}"
    echo -e "${YELLOW}ℹ️  Please ensure SSH key is configured${NC}"
    exit 1
fi
echo ""

# Step 3: Sync TDS files to production
echo -e "${YELLOW}📋 Step 3: Syncing TDS Auto-Sync files to production...${NC}"

# Sync entire app directory and TDS scripts
rsync -av --progress \
    --exclude='.git' \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.DS_Store' \
    --exclude='node_modules' \
    --exclude='screenshots' \
    --exclude='backups' \
    $LOCAL_DIR/tds_compare_and_sync.py \
    $LOCAL_DIR/tds_auto_sync_scheduler.py \
    $LOCAL_DIR/test_tds_setup.py \
    $LOCAL_DIR/run_tds_statistics.py \
    $LOCAL_DIR/TDS_AUTO_SYNC_GUIDE.md \
    $LOCAL_DIR/TDS_AUTO_SYNC_IMPLEMENTATION_SUMMARY.md \
    $LOCAL_DIR/requirements.txt \
    $LOCAL_DIR/.env \
    $LOCAL_DIR/app \
    $PRODUCTION_SERVER:$REMOTE_DIR/

echo -e "${GREEN}✅ Files synced to production${NC}"
echo ""

# Step 4: Install dependencies on production
echo -e "${YELLOW}📋 Step 4: Installing dependencies on production...${NC}"
ssh $PRODUCTION_SERVER << 'ENDSSH'
cd /root/TSH_ERP_Ecosystem

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    python3 -m venv .venv
    source .venv/bin/activate
fi

# Upgrade pip
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

echo "✅ All dependencies installed"
ENDSSH

echo -e "${GREEN}✅ Dependencies installed on production${NC}"
echo ""

# Step 5: Test TDS setup on production
echo -e "${YELLOW}📋 Step 5: Testing TDS setup on production...${NC}"
ssh $PRODUCTION_SERVER << 'ENDSSH'
cd /root/TSH_ERP_Ecosystem
source .venv/bin/activate

# Run setup validation
python3 test_tds_setup.py
ENDSSH

echo ""

# Step 6: Create systemd service for scheduler
echo -e "${YELLOW}📋 Step 6: Setting up systemd service...${NC}"
ssh $PRODUCTION_SERVER << 'ENDSSH'
cat > /etc/systemd/system/tds-autosync.service << 'EOF'
[Unit]
Description=TDS Auto-Sync Scheduler
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/TSH_ERP_Ecosystem
Environment="PATH=/root/TSH_ERP_Ecosystem/.venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/root/TSH_ERP_Ecosystem/.venv/bin/python3 /root/TSH_ERP_Ecosystem/tds_auto_sync_scheduler.py
Restart=always
RestartSec=10
StandardOutput=append:/root/TSH_ERP_Ecosystem/logs/tds_autosync_service.log
StandardError=append:/root/TSH_ERP_Ecosystem/logs/tds_autosync_service.log

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

echo "✅ Systemd service created"
ENDSSH

echo -e "${GREEN}✅ Systemd service configured${NC}"
echo ""

# Step 7: Summary
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                     Deployment Complete!                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✅ TDS Auto-Sync deployed successfully to production${NC}"
echo ""
echo -e "${YELLOW}📋 Next Steps:${NC}"
echo ""
echo -e "1. ${BLUE}Test the system (on production server):${NC}"
echo -e "   ssh $PRODUCTION_SERVER"
echo -e "   cd /root/TSH_ERP_Ecosystem"
echo -e "   source .venv/bin/activate"
echo -e "   python3 tds_compare_and_sync.py --sync --dry-run"
echo ""
echo -e "2. ${BLUE}Start the scheduler service:${NC}"
echo -e "   ssh $PRODUCTION_SERVER"
echo -e "   sudo systemctl start tds-autosync"
echo -e "   sudo systemctl enable tds-autosync  # Start on boot"
echo ""
echo -e "3. ${BLUE}Monitor the service:${NC}"
echo -e "   sudo systemctl status tds-autosync"
echo -e "   sudo journalctl -u tds-autosync -f"
echo -e "   tail -f /root/TSH_ERP_Ecosystem/logs/tds_auto_sync.log"
echo ""
echo -e "4. ${BLUE}Stop the service:${NC}"
echo -e "   sudo systemctl stop tds-autosync"
echo ""
echo -e "${GREEN}📖 Full documentation: TDS_AUTO_SYNC_GUIDE.md${NC}"
echo ""
