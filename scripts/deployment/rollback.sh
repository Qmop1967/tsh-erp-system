#!/bin/bash
# ============================================================================
# TSH ERP - Rollback Script
# ============================================================================
# Purpose: Quick rollback to previous deployment
# Usage: ./rollback.sh [target_version]
# ============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DEPLOY_DIR="/opt/tsh-erp"
COMPOSE_FILE="docker-compose.production.yml"
TARGET_VERSION="${1:-}"

# Functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} ✅ $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} ❌ $1"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} ⚠️  $1"
}

# Get current active slot
get_active_slot() {
    if docker ps --filter "name=tsh_erp_app_blue" --filter "status=running" -q | grep -q .; then
        echo "blue"
    elif docker ps --filter "name=tsh_erp_app_green" --filter "status=running" -q | grep -q .; then
        echo "green"
    else
        error "No active deployment found!"
        exit 1
    fi
}

# Get inactive slot
get_inactive_slot() {
    local active_slot="$1"
    if [ "$active_slot" == "blue" ]; then
        echo "green"
    else
        echo "blue"
    fi
}

# Main rollback logic
main() {
    warning "=========================================="
    warning "TSH ERP ROLLBACK PROCEDURE"
    warning "=========================================="

    if [ -z "$TARGET_VERSION" ]; then
        warning "No target version specified - will rollback to previous slot"
    else
        log "Target version: ${TARGET_VERSION}"
    fi

    cd "$DEPLOY_DIR"

    # Determine slots
    CURRENT_SLOT=$(get_active_slot)
    PREVIOUS_SLOT=$(get_inactive_slot "$CURRENT_SLOT")

    log "Current active slot: ${CURRENT_SLOT}"
    log "Rolling back to slot: ${PREVIOUS_SLOT}"

    # Confirm rollback (skip in non-interactive/CI mode)
    if [ -z "${CI:-}" ]; then
        echo ""
        read -p "Are you sure you want to rollback? (yes/no): " -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            warning "Rollback cancelled"
            exit 0
        fi
    else
        warning "Running in CI mode - automatic rollback confirmed"
    fi

    # Set ports
    if [ "$PREVIOUS_SLOT" == "blue" ]; then
        PREVIOUS_PORT=8001
        CURRENT_PORT=8011
    else
        PREVIOUS_PORT=8011
        CURRENT_PORT=8001
    fi

    # Step 1: Check if previous slot container exists
    log "Checking if ${PREVIOUS_SLOT} slot container exists..."
    if ! docker ps -a --filter "name=tsh_erp_app_${PREVIOUS_SLOT}" -q | grep -q .; then
        error "${PREVIOUS_SLOT} slot container not found"
        error "Cannot rollback - previous deployment not available"
        exit 1
    fi

    # Step 2: Start previous slot
    log "Starting ${PREVIOUS_SLOT} slot..."
    if [ "$PREVIOUS_SLOT" == "green" ]; then
        docker compose -f "$COMPOSE_FILE" --profile green up -d "app_${PREVIOUS_SLOT}"
    else
        docker compose -f "$COMPOSE_FILE" up -d "app_${PREVIOUS_SLOT}"
    fi

    # Step 3: Wait for health check
    log "Waiting for ${PREVIOUS_SLOT} slot to be healthy..."
    sleep 10

    MAX_ATTEMPTS=24
    ATTEMPT=0
    while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
        if curl -sf http://localhost:${PREVIOUS_PORT}/health > /dev/null 2>&1; then
            success "${PREVIOUS_SLOT} slot is healthy!"
            break
        fi
        ATTEMPT=$((ATTEMPT + 1))
        echo "Attempt $ATTEMPT/$MAX_ATTEMPTS..."
        sleep 5
    done

    if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
        error "${PREVIOUS_SLOT} slot failed health check"
        error "Rollback failed - manual intervention required"
        exit 1
    fi

    # Step 4: Update Nginx
    log "Updating Nginx to point to ${PREVIOUS_SLOT} slot..."
    if [ -f "/etc/nginx/sites-available/tsh-erp" ]; then
        sed -i "s|http://localhost:${CURRENT_PORT}|http://localhost:${PREVIOUS_PORT}|g" /etc/nginx/sites-available/tsh-erp
        nginx -t && nginx -s reload
        success "Nginx configuration updated"
    else
        warning "Nginx config not found - manual update required"
    fi

    # Step 5: Verify public endpoint
    log "Verifying public endpoint..."
    sleep 5
    if curl -sf https://erp.tsh.sale/health > /dev/null 2>&1; then
        success "Public endpoint is healthy!"
    else
        error "Public endpoint verification failed"
        warning "Service may be unstable - check immediately!"
    fi

    # Step 6: Stop current slot
    log "Stopping current ${CURRENT_SLOT} slot..."
    docker compose -f "$COMPOSE_FILE" stop "app_${CURRENT_SLOT}"

    # Step 7: Update environment
    if [ -f ".env.production" ]; then
        sed -i "s|ACTIVE_DEPLOYMENT_SLOT=.*|ACTIVE_DEPLOYMENT_SLOT=${PREVIOUS_SLOT}|g" .env.production
        sed -i "s|DEPLOYMENT_SLOT=.*|DEPLOYMENT_SLOT=${PREVIOUS_SLOT}|g" .env.production
    fi

    # Summary
    echo ""
    echo "============================================================================"
    success "Rollback Completed!"
    echo "============================================================================"
    echo "Rolled back from: ${CURRENT_SLOT}"
    echo "Now running on: ${PREVIOUS_SLOT}"
    echo "Rollback time: $(date)"
    echo "============================================================================"
    echo ""
    docker compose -f "$COMPOSE_FILE" ps
    echo ""
    success "TSH ERP has been rolled back successfully"
}

# Run main function
main "$@"
