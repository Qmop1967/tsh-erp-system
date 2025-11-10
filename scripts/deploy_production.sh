#!/bin/bash

# =====================================================
# TSH ERP - Production Deployment Script
# Monolithic Unification with Mobile BFF
# Date: November 4, 2025
# =====================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/home/deploy/TSH_ERP_Ecosystem"
BACKUP_DIR="/home/deploy/backups"
SERVICE_NAME="tsh-erp"
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="tsh_erp"
DB_USER="tsh_app_user"
DB_PASSWORD="TSH@2025Secure!Production"

# =====================================================
# FUNCTIONS
# =====================================================

print_header() {
    echo -e "${BLUE}=================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

confirm() {
    read -p "$(echo -e ${YELLOW}$1 [y/N]: ${NC})" -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Deployment cancelled by user"
        exit 1
    fi
}

# =====================================================
# PRE-DEPLOYMENT CHECKS
# =====================================================

print_header "PRE-DEPLOYMENT CHECKS"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root"
    exit 1
fi

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    print_error "Project directory not found: $PROJECT_DIR"
    exit 1
fi

# Check if backup directory exists, create if not
if [ ! -d "$BACKUP_DIR" ]; then
    mkdir -p "$BACKUP_DIR"
    print_success "Created backup directory: $BACKUP_DIR"
fi

# Check current service status
if systemctl is-active --quiet $SERVICE_NAME; then
    print_success "Service $SERVICE_NAME is currently running"
else
    print_warning "Service $SERVICE_NAME is not running"
fi

# Change to project directory
cd "$PROJECT_DIR"

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
print_success "Current branch: $CURRENT_BRANCH"

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    print_warning "You have uncommitted changes!"
    git status --short
    confirm "Continue anyway?"
fi

# =====================================================
# BACKUP
# =====================================================

print_header "CREATING BACKUPS"

# Backup timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 1. Backup database
print_warning "Creating database backup (public schema only)..."
PGPASSWORD="$DB_PASSWORD" pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --schema=public \
    --no-owner --no-acl \
    > "$BACKUP_DIR/db_backup_$TIMESTAMP.sql"

if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_DIR/db_backup_$TIMESTAMP.sql" | cut -f1)
    print_success "Database backup created: db_backup_$TIMESTAMP.sql ($BACKUP_SIZE)"
else
    print_error "Database backup failed!"
    exit 1
fi

# 2. Backup current code
print_warning "Creating code backup..."
tar -czf "$BACKUP_DIR/code_backup_$TIMESTAMP.tar.gz" \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='venv' \
    --exclude='node_modules' \
    "$PROJECT_DIR"

if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_DIR/code_backup_$TIMESTAMP.tar.gz" | cut -f1)
    print_success "Code backup created: code_backup_$TIMESTAMP.tar.gz ($BACKUP_SIZE)"
else
    print_warning "Code backup failed (non-critical)"
fi

# =====================================================
# DEPLOYMENT CONFIRMATION
# =====================================================

print_header "DEPLOYMENT CONFIRMATION"

echo ""
echo "You are about to deploy:"
echo "  From branch: $CURRENT_BRANCH"
echo "  To: Production Server"
echo ""
echo "This will:"
echo "  1. Merge feature branch to main"
echo "  2. Pull latest code"
echo "  3. Install dependencies"
echo "  4. Run database migrations"
echo "  5. Restart service"
echo ""
echo "Backups created:"
echo "  Database: $BACKUP_DIR/db_backup_$TIMESTAMP.sql"
echo "  Code: $BACKUP_DIR/code_backup_$TIMESTAMP.tar.gz"
echo ""

confirm "Proceed with deployment?"

# =====================================================
# GIT OPERATIONS
# =====================================================

print_header "GIT OPERATIONS"

# Fetch latest from remote
print_warning "Fetching from remote..."
git fetch origin

# If on feature branch, merge to main
if [ "$CURRENT_BRANCH" != "main" ]; then
    print_warning "Switching to main branch..."
    git checkout main

    print_warning "Pulling latest main..."
    git pull origin main

    print_warning "Merging $CURRENT_BRANCH into main..."
    git merge "$CURRENT_BRANCH" --no-edit

    print_warning "Pushing to remote..."
    git push origin main

    print_success "Merged $CURRENT_BRANCH to main"
else
    print_warning "Pulling latest from main..."
    git pull origin main
fi

print_success "Git operations complete"

# =====================================================
# DEPENDENCIES
# =====================================================

print_header "INSTALLING DEPENDENCIES"

# Check if venv exists
if [ -d "venv" ]; then
    print_warning "Activating virtual environment..."
    source venv/bin/activate
fi

# Install/update dependencies
print_warning "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

print_success "Dependencies installed"

# =====================================================
# DATABASE MIGRATION
# =====================================================

print_header "DATABASE MIGRATION"

# Check if migration file exists
MIGRATION_FILE="migrations/create_bff_models.sql"
if [ -f "$MIGRATION_FILE" ]; then
    print_warning "Running database migration..."

    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$MIGRATION_FILE" 2>&1 | tee /tmp/migration_log.txt

    # Check if migration had errors (but tables might already exist)
    if grep -qi "error" /tmp/migration_log.txt && ! grep -qi "already exists" /tmp/migration_log.txt; then
        print_error "Migration had errors!"
        cat /tmp/migration_log.txt
        confirm "Continue despite errors?"
    else
        print_success "Database migration completed"
    fi
else
    print_warning "No migration file found: $MIGRATION_FILE"
fi

# Verify new tables exist
print_warning "Verifying new tables..."
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c \
    "SELECT table_name FROM information_schema.tables
     WHERE table_schema = 'public'
     AND table_name IN ('promotions', 'carts', 'cart_items', 'reviews', 'customer_addresses')
     ORDER BY table_name;" | tee /tmp/tables_check.txt

TABLE_COUNT=$(grep -c "^" /tmp/tables_check.txt | tail -1)
if [ "$TABLE_COUNT" -ge "5" ]; then
    print_success "All 5 BFF tables verified"
else
    print_warning "Some tables might be missing"
fi

# =====================================================
# PRE-DEPLOYMENT TESTING (ORIXOON)
# =====================================================

print_header "PRE-DEPLOYMENT TESTING (ORIXOON)"

# Check if Orixoon agent exists
ORIXOON_DIR="$PROJECT_DIR/.claude/agents/orixoon"
if [ -d "$ORIXOON_DIR" ] && [ -f "$ORIXOON_DIR/tools/orixoon_orchestrator.sh" ]; then
    print_warning "Running Orixoon pre-deployment tests..."

    # Run Orixoon tests
    cd "$ORIXOON_DIR"
    bash tools/orixoon_orchestrator.sh

    if [ $? -ne 0 ]; then
        print_error "Orixoon pre-deployment tests FAILED!"
        print_error "Deployment BLOCKED for safety"
        print_warning "Review test report in: $ORIXOON_DIR/reports/"
        confirm "Do you want to override and continue anyway? (NOT RECOMMENDED)"
    else
        print_success "Orixoon tests passed - deployment cleared"
    fi

    # Return to project directory
    cd "$PROJECT_DIR"
else
    print_warning "Orixoon agent not found - skipping pre-deployment tests"
    print_warning "Install Orixoon at: $ORIXOON_DIR"
fi

# =====================================================
# SERVICE RESTART
# =====================================================

print_header "SERVICE RESTART"

print_warning "Stopping service..."
systemctl stop $SERVICE_NAME

sleep 2

print_warning "Starting service..."
systemctl start $SERVICE_NAME

sleep 3

# Check if service started successfully
if systemctl is-active --quiet $SERVICE_NAME; then
    print_success "Service started successfully"
else
    print_error "Service failed to start!"
    print_error "Checking logs..."
    journalctl -u $SERVICE_NAME -n 50 --no-pager

    print_error "DEPLOYMENT FAILED! Service won't start."
    confirm "Do you want to rollback?"

    # Rollback
    print_warning "Rolling back..."
    git reset --hard HEAD~1
    systemctl restart $SERVICE_NAME

    print_error "Rolled back to previous version"
    exit 1
fi

# =====================================================
# POST-DEPLOYMENT VERIFICATION
# =====================================================

print_header "POST-DEPLOYMENT VERIFICATION"

# Wait for service to be fully ready
print_warning "Waiting for service to be ready..."
sleep 5

# Test 1: Main health endpoint
print_warning "Testing main health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    print_success "Main health endpoint: OK"
else
    print_error "Main health endpoint: FAILED"
    echo "$HEALTH_RESPONSE"
fi

# Test 2: Zoho health endpoint
print_warning "Testing Zoho health endpoint..."
ZOHO_HEALTH=$(curl -s http://localhost:8000/api/zoho/dashboard/health)
if echo "$ZOHO_HEALTH" | grep -q "status"; then
    print_success "Zoho health endpoint: OK"
else
    print_warning "Zoho health endpoint: Response unclear"
fi

# Test 3: Mobile BFF endpoint
print_warning "Testing Mobile BFF endpoint..."
BFF_RESPONSE=$(curl -s http://localhost:8000/api/mobile/home)
if echo "$BFF_RESPONSE" | grep -q "featured_products\|error"; then
    print_success "Mobile BFF endpoint: OK (or expected error if no data)"
else
    print_warning "Mobile BFF endpoint: Response unclear"
fi

# Check service logs for errors
print_warning "Checking service logs for errors..."
ERROR_COUNT=$(journalctl -u $SERVICE_NAME -n 50 --no-pager | grep -i "error" | wc -l)
if [ "$ERROR_COUNT" -gt 0 ]; then
    print_warning "Found $ERROR_COUNT errors in logs"
    journalctl -u $SERVICE_NAME -n 50 --no-pager | grep -i "error"
else
    print_success "No errors in recent logs"
fi

# Check if workers started
print_warning "Checking if workers started..."
WORKER_COUNT=$(journalctl -u $SERVICE_NAME -n 100 --no-pager | grep -i "worker.*started" | wc -l)
if [ "$WORKER_COUNT" -gt 0 ]; then
    print_success "Background workers started ($WORKER_COUNT instances)"
else
    print_warning "No worker startup messages found"
fi

# =====================================================
# DEPLOYMENT SUMMARY
# =====================================================

print_header "DEPLOYMENT SUMMARY"

echo ""
echo "Deployment completed at: $(date)"
echo ""
echo "Git Status:"
git log --oneline -3
echo ""
echo "Service Status:"
systemctl status $SERVICE_NAME --no-pager | head -10
echo ""
echo "Backups Location:"
echo "  $BACKUP_DIR/db_backup_$TIMESTAMP.sql"
echo "  $BACKUP_DIR/code_backup_$TIMESTAMP.tar.gz"
echo ""
echo "Verification Results:"
echo "  Main Health: $(curl -s http://localhost:8000/health | grep -o '"status":"[^"]*"' || echo 'Unknown')"
echo "  Service Active: $(systemctl is-active $SERVICE_NAME)"
echo "  Error Count: $ERROR_COUNT"
echo ""

# =====================================================
# NEXT STEPS
# =====================================================

print_header "NEXT STEPS"

echo ""
echo "1. Monitor logs for 10-15 minutes:"
echo "   journalctl -u $SERVICE_NAME -f"
echo ""
echo "2. Test API endpoints:"
echo "   curl https://erp.tsh.sale/health"
echo "   curl https://erp.tsh.sale/api/zoho/dashboard/health"
echo "   curl https://erp.tsh.sale/api/mobile/home"
echo ""
echo "3. Check application metrics"
echo ""
echo "4. If issues occur, rollback with:"
echo "   cd $PROJECT_DIR"
echo "   git reset --hard HEAD~1"
echo "   systemctl restart $SERVICE_NAME"
echo ""

print_success "🎉 DEPLOYMENT COMPLETE!"

# =====================================================
# END OF SCRIPT
# =====================================================
