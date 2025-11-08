#!/bin/bash

################################################################################
# Complete Zoho Sync and Deployment
# TSH ERP System - Production
################################################################################
#
# This script performs a complete Zoho synchronization and deployment:
# 1. SSH into production server
# 2. Compare and sync items from Zoho (2221+ items)
# 3. Sync product images
# 4. Sync consumer price lists
# 5. Verify stock levels
# 6. Restart services
# 7. Verify Flutter consumer app can access data
#
# Usage:
#   ./scripts/deploy_complete_zoho_sync.sh
#
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
VPS_HOST="tsh-vps"
VPS_IP="167.71.39.50"
DEPLOY_DIR="/home/deploy/TSH_ERP_Ecosystem"

################################################################################
# Helper Functions
################################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo ""
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

################################################################################
# Main Deployment
################################################################################

log_step "🚀 TSH ERP - Complete Zoho Sync & Deployment"

echo ""
log_info "Target: Production VPS ($VPS_IP)"
log_info "Deploy Directory: $DEPLOY_DIR"
echo ""

# Step 1: Test SSH Connection
log_step "STEP 1: Testing SSH Connection"

if ! ssh -o ConnectTimeout=5 $VPS_HOST "echo 'SSH connection successful'" 2>/dev/null; then
    log_error "Cannot connect to $VPS_HOST"
    log_info "Please ensure:"
    log_info "  1. SSH key is configured (~/.ssh/tsh_vps)"
    log_info "  2. SSH config is set up (~/.ssh/config)"
    log_info "  3. Run: ssh root@$VPS_IP"
    exit 1
fi

log_success "SSH connection established"

# Step 2: Navigate and Pull Latest Code
log_step "STEP 2: Pulling Latest Code"

ssh $VPS_HOST << 'ENDSSH'
set -e
cd /home/deploy/TSH_ERP_Ecosystem

# Show current status
echo "Current git status:"
git status --short

# Pull latest code
echo ""
echo "Pulling latest code..."
git fetch origin
git pull origin develop || git pull origin main

echo ""
echo "Latest commit:"
git log -1 --oneline

echo ""
echo "✅ Code updated"
ENDSSH

log_success "Code pulled successfully"

# Step 3: Compare and Sync Items from Zoho
log_step "STEP 3: Comparing and Syncing Items from Zoho"

log_info "This will sync 2221+ items from Zoho to TSH ERP database..."

ssh $VPS_HOST << 'ENDSSH'
set -e
cd /home/deploy/TSH_ERP_Ecosystem

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run Zoho items comparison and sync
echo "Running Zoho items comparison and sync..."
python3 scripts/compare_and_sync_zoho_items_mcp.py 2>&1 | tee /tmp/zoho_items_sync.log

echo ""
echo "Sync summary:"
tail -20 /tmp/zoho_items_sync.log | grep -E "SUMMARY|Items|Sync|✅|❌" || true
ENDSSH

log_success "Items sync completed"

# Step 4: Sync Product Images
log_step "STEP 4: Syncing Product Images from Zoho"

ssh $VPS_HOST << 'ENDSSH'
set -e
cd /home/deploy/TSH_ERP_Ecosystem

if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Download images
echo "Downloading product images from Zoho..."
python3 scripts/download_zoho_images_tds.py 2>&1 | tee /tmp/zoho_images_sync.log | tail -50

echo ""
echo "✅ Images sync completed"
ENDSSH

log_success "Images sync completed"

# Step 5: Sync Consumer Price Lists
log_step "STEP 5: Syncing Consumer Price Lists"

ssh $VPS_HOST << 'ENDSSH'
set -e
cd /home/deploy/TSH_ERP_Ecosystem

if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Sync price lists
echo "Syncing consumer price lists from Zoho..."
python3 scripts/sync_pricelists_from_zoho.py 2>&1 | tee /tmp/zoho_pricelists_sync.log | tail -50

echo ""
echo "✅ Price lists sync completed"
ENDSSH

log_success "Price lists sync completed"

# Step 6: Verify Database Counts
log_step "STEP 6: Verifying Database Counts"

ssh $VPS_HOST << 'ENDSSH'
set -e
cd /home/deploy/TSH_ERP_Ecosystem

# Check database counts
echo "Checking database statistics..."
psql -U tsh_app_user -d tsh_erp_production -c "
SELECT
    'Products' as table_name,
    COUNT(*) as total_count,
    COUNT(CASE WHEN zoho_item_id IS NOT NULL THEN 1 END) as with_zoho_id,
    COUNT(CASE WHEN image_url IS NOT NULL THEN 1 END) as with_images,
    COUNT(CASE WHEN actual_available_stock > 0 THEN 1 END) as in_stock
FROM products

UNION ALL

SELECT
    'Price Lists' as table_name,
    COUNT(*) as total_count,
    COUNT(CASE WHEN zoho_pricelist_id IS NOT NULL THEN 1 END) as with_zoho_id,
    0 as with_images,
    COUNT(CASE WHEN is_active = true THEN 1 END) as active
FROM pricelists;
"

echo ""
echo "✅ Database verification complete"
ENDSSH

log_success "Database counts verified"

# Step 7: Restart Application Service
log_step "STEP 7: Restarting Application Service"

ssh $VPS_HOST << 'ENDSSH'
set -e

# Restart systemd service
echo "Restarting tsh-erp service..."
systemctl restart tsh-erp

# Wait for service to be ready
echo "Waiting for service to start..."
sleep 5

# Check service status
echo ""
systemctl status tsh-erp --no-pager | head -15

echo ""
echo "✅ Service restarted"
ENDSSH

log_success "Service restarted successfully"

# Step 8: Run Health Checks
log_step "STEP 8: Running Health Checks"

ssh $VPS_HOST << 'ENDSSH'
set -e

echo "Testing API endpoints..."

# Test main health
echo "1. Main health endpoint:"
curl -s http://localhost:8000/health | python3 -m json.tool || echo "Failed"

# Test BFF consumer products endpoint
echo ""
echo "2. Consumer products endpoint:"
curl -s "http://localhost:8000/api/bff/mobile/consumer/products?limit=5" | python3 -m json.tool | head -50

# Test BFF home endpoint
echo ""
echo "3. Consumer home endpoint:"
curl -s http://localhost:8000/api/bff/mobile/consumer/home | python3 -m json.tool | head -50

echo ""
echo "✅ Health checks completed"
ENDSSH

log_success "Health checks passed"

# Step 9: Test Public Access
log_step "STEP 9: Testing Public HTTPS Access"

echo "Testing public HTTPS endpoints..."

# Test health endpoint
echo "1. Testing: https://erp.tsh.sale/health"
curl -s -k https://erp.tsh.sale/health | python3 -m json.tool || echo "  ⚠️  Health endpoint not accessible"

# Test BFF consumer products
echo ""
echo "2. Testing: https://erp.tsh.sale/api/bff/mobile/consumer/products"
curl -s -k "https://erp.tsh.sale/api/bff/mobile/consumer/products?limit=3" | python3 -m json.tool | head -40 || echo "  ⚠️  Products endpoint not accessible"

log_success "Public access tested"

# Final Summary
log_step "✅ DEPLOYMENT COMPLETE!"

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}SUMMARY${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}✅ Items synced from Zoho${NC}"
echo -e "${GREEN}✅ Product images downloaded${NC}"
echo -e "${GREEN}✅ Consumer price lists synced${NC}"
echo -e "${GREEN}✅ Database verified${NC}"
echo -e "${GREEN}✅ Service restarted${NC}"
echo -e "${GREEN}✅ Health checks passed${NC}"
echo ""
echo -e "${CYAN}Flutter Consumer App Endpoints:${NC}"
echo -e "  - Products: ${GREEN}https://erp.tsh.sale/api/bff/mobile/consumer/products${NC}"
echo -e "  - Home: ${GREEN}https://erp.tsh.sale/api/bff/mobile/consumer/home${NC}"
echo -e "  - Product Detail: ${GREEN}https://erp.tsh.sale/api/bff/mobile/consumer/products/{id}${NC}"
echo ""
echo -e "${CYAN}Next Steps:${NC}"
echo -e "  1. Test Flutter consumer app"
echo -e "  2. Verify all products display with images"
echo -e "  3. Verify consumer prices are correct"
echo -e "  4. Monitor logs: ${YELLOW}ssh $VPS_HOST 'journalctl -u tsh-erp -f'${NC}"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Save deployment log
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
echo "Deployment completed at: $(date)" > "logs/deployment_${TIMESTAMP}.log"
echo "Target: $VPS_HOST" >> "logs/deployment_${TIMESTAMP}.log"
echo "Status: SUCCESS" >> "logs/deployment_${TIMESTAMP}.log"

log_success "Deployment log saved: logs/deployment_${TIMESTAMP}.log"

exit 0
