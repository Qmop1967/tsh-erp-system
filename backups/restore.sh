#!/bin/bash

# TSH ERP System - Restore Script
# Restores database, images, and environment files from backup

set -e

# Configuration
BACKUP_ROOT="/Users/khaleelal-mulla/TSH_ERP_System_Local/backups"
PROJECT_ROOT="/Users/khaleelal-mulla/TSH_ERP_System_Local"
DB_NAME="tsh_erp_db"
DB_USER="khaleelal-mulla"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "TSH ERP System - Restore from Backup"
echo "=========================================="
echo ""

# Function to restore database
restore_database() {
    local backup_file="$1"

    echo -e "${YELLOW}→ Restoring database...${NC}"

    if [ ! -f "$backup_file" ]; then
        echo -e "${RED}✗ Backup file not found: $backup_file${NC}"
        return 1
    fi

    # Decompress if needed
    if [[ "$backup_file" == *.gz ]]; then
        echo "  Decompressing backup..."
        gunzip -k "$backup_file"
        backup_file="${backup_file%.gz}"
    fi

    # Drop and recreate database
    echo "  Recreating database..."
    psql -U "$DB_USER" -c "DROP DATABASE IF EXISTS ${DB_NAME};"
    psql -U "$DB_USER" -c "CREATE DATABASE ${DB_NAME};"

    # Restore
    echo "  Restoring data..."
    psql -U "$DB_USER" -d "$DB_NAME" -f "$backup_file"

    echo -e "${GREEN}✓ Database restored successfully!${NC}"
}

# Function to restore images
restore_images() {
    local backup_file="$1"
    local target_dir="${PROJECT_ROOT}/static/images"

    echo -e "${YELLOW}→ Restoring product images...${NC}"

    if [ ! -f "$backup_file" ]; then
        echo -e "${RED}✗ Backup file not found: $backup_file${NC}"
        return 1
    fi

    # Create backup of existing images
    if [ -d "$target_dir/products" ]; then
        echo "  Backing up existing images..."
        mv "$target_dir/products" "$target_dir/products.backup.$(date +%Y%m%d_%H%M%S)"
    fi

    # Extract images
    echo "  Extracting images..."
    tar -xzf "$backup_file" -C "$target_dir"

    echo -e "${GREEN}✓ Product images restored successfully!${NC}"
}

# Function to restore environment files
restore_env() {
    local backup_file="$1"

    echo -e "${YELLOW}→ Restoring environment files...${NC}"

    if [ ! -f "$backup_file" ]; then
        echo -e "${RED}✗ Backup file not found: $backup_file${NC}"
        return 1
    fi

    # Create backup of existing .env files
    echo "  Backing up existing .env files..."
    find "$PROJECT_ROOT" -name ".env*" -not -path "*/backups/*" -exec cp {} {}.backup.$(date +%Y%m%d_%H%M%S) \;

    # Extract environment files
    echo "  Extracting environment files..."
    tar -xzf "$backup_file" -C "$PROJECT_ROOT"

    echo -e "${GREEN}✓ Environment files restored successfully!${NC}"
}

# Main menu
echo "Select restore option:"
echo "1) Restore from latest backups"
echo "2) Restore from specific full backup"
echo "3) Restore database only"
echo "4) Restore images only"
echo "5) Restore environment files only"
echo "6) Exit"
echo ""
read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        echo ""
        echo -e "${YELLOW}Restoring from latest backups...${NC}"
        echo ""
        restore_database "${BACKUP_ROOT}/database/latest.sql.gz"
        restore_images "${BACKUP_ROOT}/images/latest.tar.gz"
        restore_env "${BACKUP_ROOT}/env/latest.tar.gz"
        ;;
    2)
        echo ""
        echo "Available full backups:"
        ls -lh "${BACKUP_ROOT}/full/"tsh_erp_full_*.tar.gz 2>/dev/null || echo "No full backups found"
        echo ""
        read -p "Enter full backup file path: " full_backup

        if [ -f "$full_backup" ]; then
            # Extract full backup to temp directory
            temp_dir=$(mktemp -d)
            tar -xzf "$full_backup" -C "$temp_dir"

            restore_database "$temp_dir/database/latest.sql.gz"
            restore_images "$temp_dir/images/latest.tar.gz"
            restore_env "$temp_dir/env/latest.tar.gz"

            rm -rf "$temp_dir"
        else
            echo -e "${RED}✗ Backup file not found${NC}"
        fi
        ;;
    3)
        read -p "Enter database backup file path (or press Enter for latest): " db_backup
        db_backup=${db_backup:-"${BACKUP_ROOT}/database/latest.sql.gz"}
        restore_database "$db_backup"
        ;;
    4)
        read -p "Enter images backup file path (or press Enter for latest): " img_backup
        img_backup=${img_backup:-"${BACKUP_ROOT}/images/latest.tar.gz"}
        restore_images "$img_backup"
        ;;
    5)
        read -p "Enter env backup file path (or press Enter for latest): " env_backup
        env_backup=${env_backup:-"${BACKUP_ROOT}/env/latest.tar.gz"}
        restore_env "$env_backup"
        ;;
    6)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo -e "${GREEN}✓ RESTORE COMPLETED SUCCESSFULLY!${NC}"
echo "=========================================="
echo "Completed at: $(date)"
