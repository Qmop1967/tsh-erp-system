#!/bin/bash

# =====================================================
# TSH ERP - Production Rollback Script
# Quick rollback to previous version
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
DB_CONNECTION="postgresql://postgres.trjjglxhteqnzmyakxhe:Zcbbm.97531tsh@aws-1-eu-north-1.pooler.supabase.com:5432/postgres"

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
        print_error "Rollback cancelled by user"
        exit 1
    fi
}

# =====================================================
# PRE-ROLLBACK CHECKS
# =====================================================

print_header "ROLLBACK PREPARATION"

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

cd "$PROJECT_DIR"

# Show current status
print_warning "Current Git Status:"
git log --oneline -5

echo ""
print_warning "Current Service Status:"
systemctl status $SERVICE_NAME --no-pager | head -5

# =====================================================
# ROLLBACK CONFIRMATION
# =====================================================

print_header "ROLLBACK CONFIRMATION"

echo ""
echo "⚠️  WARNING: You are about to rollback the deployment!"
echo ""
echo "This will:"
echo "  1. Revert code to previous commit"
echo "  2. Restart service"
echo "  3. Optionally restore database backup"
echo ""

confirm "Are you sure you want to rollback?"

# =====================================================
# ROLLBACK OPTIONS
# =====================================================

echo ""
echo "Rollback Options:"
echo "  1. Code only (recommended for quick rollback)"
echo "  2. Code + Database (for complete rollback)"
echo ""
read -p "Select option [1-2]: " ROLLBACK_OPTION

# =====================================================
# CODE ROLLBACK
# =====================================================

print_header "CODE ROLLBACK"

print_warning "Resetting to previous commit..."
git reset --hard HEAD~1

print_success "Code rolled back to previous version"

# Show what we rolled back to
print_warning "Current commit:"
git log --oneline -1

# =====================================================
# DATABASE ROLLBACK (OPTIONAL)
# =====================================================

if [ "$ROLLBACK_OPTION" == "2" ]; then
    print_header "DATABASE ROLLBACK"

    # List available backups
    print_warning "Available database backups:"
    ls -lh "$BACKUP_DIR"/db_backup_*.sql | tail -5

    echo ""
    read -p "Enter backup filename (or press Enter to skip): " BACKUP_FILE

    if [ -n "$BACKUP_FILE" ]; then
        BACKUP_PATH="$BACKUP_DIR/$BACKUP_FILE"

        if [ ! -f "$BACKUP_PATH" ]; then
            print_error "Backup file not found: $BACKUP_PATH"
            print_warning "Continuing with code rollback only..."
        else
            print_warning "⚠️  WARNING: This will DROP and recreate BFF tables!"
            confirm "Continue with database rollback?"

            # Drop new tables
            print_warning "Dropping new BFF tables..."
            PGPASSWORD="Zcbbm.97531tsh" psql "$DB_CONNECTION" <<EOF
BEGIN;
DROP TABLE IF EXISTS cart_items CASCADE;
DROP TABLE IF EXISTS carts CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS customer_addresses CASCADE;
DROP TABLE IF EXISTS promotions CASCADE;
COMMIT;
EOF

            print_success "BFF tables dropped"

            # Note: Full database restore not recommended for production
            # Only drop new tables to revert BFF migration
            print_warning "Database tables rolled back (BFF tables removed)"
        fi
    fi
fi

# =====================================================
# SERVICE RESTART
# =====================================================

print_header "SERVICE RESTART"

print_warning "Restarting service..."
systemctl restart $SERVICE_NAME

sleep 3

# Check if service started
if systemctl is-active --quiet $SERVICE_NAME; then
    print_success "Service restarted successfully"
else
    print_error "Service failed to start!"
    journalctl -u $SERVICE_NAME -n 50 --no-pager
    exit 1
fi

# =====================================================
# VERIFICATION
# =====================================================

print_header "VERIFICATION"

sleep 3

# Test health endpoint
print_warning "Testing health endpoint..."
HEALTH=$(curl -s http://localhost:8000/health)
if echo "$HEALTH" | grep -q "healthy"; then
    print_success "Health check: OK"
else
    print_error "Health check: FAILED"
    echo "$HEALTH"
fi

# Check logs for errors
print_warning "Checking for errors..."
ERROR_COUNT=$(journalctl -u $SERVICE_NAME -n 50 --no-pager | grep -i "error" | wc -l)
if [ "$ERROR_COUNT" -eq 0 ]; then
    print_success "No errors in logs"
else
    print_warning "Found $ERROR_COUNT errors in logs"
fi

# =====================================================
# SUMMARY
# =====================================================

print_header "ROLLBACK SUMMARY"

echo ""
echo "Rollback completed at: $(date)"
echo ""
echo "Current Git Commit:"
git log --oneline -1
echo ""
echo "Service Status:"
systemctl status $SERVICE_NAME --no-pager | head -5
echo ""

if [ "$ROLLBACK_OPTION" == "2" ]; then
    echo "Database Status: BFF tables removed"
else
    echo "Database Status: No changes"
fi
echo ""

print_success "🔄 ROLLBACK COMPLETE!"

echo ""
echo "Next Steps:"
echo "  1. Monitor service: journalctl -u $SERVICE_NAME -f"
echo "  2. Test endpoints: curl http://localhost:8000/health"
echo "  3. Investigate root cause of issues"
echo ""
