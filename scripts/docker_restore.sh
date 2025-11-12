#!/bin/bash

################################################################################
# Docker Volumes Restore Script
# TSH ERP System
################################################################################
#
# This script restores Docker volumes from backups
#
# Usage:
#   ./scripts/docker_restore.sh <backup_timestamp> [postgres|redis|all]
#
# Example:
#   ./scripts/docker_restore.sh 20250108_143000 all
#
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKUP_DIR="./backups/docker_volumes"
COMPOSE_PROJECT="${COMPOSE_PROJECT_NAME:-tsh_erp_ecosystem}"

# Compose command detection
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    echo -e "${RED}Error: Docker Compose not found${NC}"
    exit 1
fi

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

confirm() {
    read -p "$(echo -e ${YELLOW}$1 [y/N]: ${NC})" -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_error "Restore cancelled by user"
        exit 1
    fi
}

################################################################################
# Restore Functions
################################################################################

# Restore PostgreSQL from dump
restore_postgres() {
    local timestamp=$1
    local dump_file="$BACKUP_DIR/postgres_dump_${timestamp}.sql.gz"

    if [ ! -f "$dump_file" ]; then
        log_error "PostgreSQL dump not found: $dump_file"
        return 1
    fi

    log_warning "This will REPLACE all data in PostgreSQL database!"
    confirm "Are you sure you want to restore PostgreSQL from $dump_file?"

    # Stop the app container to prevent connections
    log_info "Stopping app container..."
    $DOCKER_COMPOSE_CMD stop app || true

    # Ensure postgres is running
    log_info "Starting PostgreSQL container..."
    $DOCKER_COMPOSE_CMD --profile core up -d tsh_postgres
    sleep 5

    # Drop and recreate database
    log_info "Recreating database..."
    docker exec tsh_postgres psql -U ${POSTGRES_USER:-tsh_admin} -d postgres -c \
        "DROP DATABASE IF EXISTS ${POSTGRES_DB:-tsh_erp};"
    docker exec tsh_postgres psql -U ${POSTGRES_USER:-tsh_admin} -d postgres -c \
        "CREATE DATABASE ${POSTGRES_DB:-tsh_erp};"

    # Restore from dump
    log_info "Restoring database from dump..."
    gunzip -c "$dump_file" | docker exec -i tsh_postgres psql -U ${POSTGRES_USER:-tsh_admin} -d ${POSTGRES_DB:-tsh_erp}

    if [ $? -eq 0 ]; then
        log_success "PostgreSQL restored successfully!"
    else
        log_error "PostgreSQL restore failed!"
        return 1
    fi

    # Restart app
    log_info "Restarting app container..."
    $DOCKER_COMPOSE_CMD --profile core up -d app
}

# Restore Redis from volume backup
restore_redis() {
    local timestamp=$1
    local volume_file="$BACKUP_DIR/redis_volume_${timestamp}.tar.gz"

    if [ ! -f "$volume_file" ]; then
        log_error "Redis volume backup not found: $volume_file"
        return 1
    fi

    log_warning "This will REPLACE all data in Redis cache!"
    confirm "Are you sure you want to restore Redis from $volume_file?"

    # Stop redis container
    log_info "Stopping Redis container..."
    $DOCKER_COMPOSE_CMD stop redis

    # Restore volume
    log_info "Restoring Redis volume..."
    docker run --rm \
        -v ${COMPOSE_PROJECT}_redis_data:/data \
        -v $(pwd)/$BACKUP_DIR:/backup \
        alpine sh -c "rm -rf /data/* && tar xzf /backup/redis_volume_${timestamp}.tar.gz -C /data"

    if [ $? -eq 0 ]; then
        log_success "Redis volume restored successfully!"
    else
        log_error "Redis volume restore failed!"
        return 1
    fi

    # Restart redis
    log_info "Restarting Redis container..."
    $DOCKER_COMPOSE_CMD --profile core up -d redis
}

# Restore uploads
restore_uploads() {
    local timestamp=$1
    local uploads_file="$BACKUP_DIR/uploads_${timestamp}.tar.gz"

    if [ ! -f "$uploads_file" ]; then
        log_error "Uploads backup not found: $uploads_file"
        return 1
    fi

    log_warning "This will REPLACE all uploaded files!"
    confirm "Are you sure you want to restore uploads from $uploads_file?"

    # Backup current uploads first
    if [ -d "./uploads" ]; then
        log_info "Backing up current uploads..."
        mv ./uploads ./uploads.bak.$(date +%Y%m%d_%H%M%S)
    fi

    # Restore uploads
    log_info "Restoring uploads..."
    tar xzf "$uploads_file"

    if [ $? -eq 0 ]; then
        log_success "Uploads restored successfully!"
    else
        log_error "Uploads restore failed!"
        return 1
    fi
}

# List available backups
list_backups() {
    log_info "Available backups in $BACKUP_DIR:"
    echo ""

    if [ -d "$BACKUP_DIR" ]; then
        # Extract unique timestamps from backup files
        ls -1 "$BACKUP_DIR" | grep -oE '[0-9]{8}_[0-9]{6}' | sort -u | while read timestamp; do
            echo "  Timestamp: $timestamp"
            ls -lh "$BACKUP_DIR" | grep "$timestamp" | awk '{print "    - "$9" ("$5")"}'
            echo ""
        done
    else
        log_warning "Backup directory not found: $BACKUP_DIR"
    fi
}

################################################################################
# Main Script
################################################################################

# Check arguments
if [ "$1" == "list" ]; then
    list_backups
    exit 0
fi

if [ $# -lt 1 ]; then
    log_error "Missing required argument: backup timestamp"
    log_info "Usage: $0 <backup_timestamp> [postgres|redis|uploads|all]"
    log_info "   or: $0 list"
    echo ""
    list_backups
    exit 1
fi

TIMESTAMP=$1
RESTORE_TYPE="${2:-all}"

log_info "Starting Docker restore process..."
log_info "Restore type: $RESTORE_TYPE"
log_info "Timestamp: $TIMESTAMP"
echo ""

# Perform restore based on type
case "$RESTORE_TYPE" in
    postgres)
        restore_postgres "$TIMESTAMP"
        ;;
    redis)
        restore_redis "$TIMESTAMP"
        ;;
    uploads)
        restore_uploads "$TIMESTAMP"
        ;;
    all)
        restore_postgres "$TIMESTAMP"
        restore_redis "$TIMESTAMP"
        restore_uploads "$TIMESTAMP"
        ;;
    *)
        log_error "Invalid restore type: $RESTORE_TYPE"
        log_info "Usage: $0 <backup_timestamp> [postgres|redis|uploads|all]"
        exit 1
        ;;
esac

echo ""
log_success "Restore completed successfully!"
echo ""

exit 0
