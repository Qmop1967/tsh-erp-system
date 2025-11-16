#!/bin/bash
# ============================================================================
# TSH ERP - Blue-Green Deployment Script
# ============================================================================
# Purpose: Zero-downtime production deployment using blue-green strategy
# Usage: ./blue_green_deploy.sh [version]
# ============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOY_DIR="/opt/tsh-erp"
COMPOSE_FILE="docker-compose.production.yml"
VERSION="${1:-latest}"
HEALTH_CHECK_TIMEOUT=120
HEALTH_CHECK_INTERVAL=5

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

# Determine current active slot
get_active_slot() {
    if docker ps --filter "name=tsh_erp_app_blue" --filter "status=running" -q | grep -q .; then
        echo "blue"
    elif docker ps --filter "name=tsh_erp_app_green" --filter "status=running" -q | grep -q .; then
        echo "green"
    else
        echo "blue" # Default to blue if neither is running
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

# Health check function
check_health() {
    local port="$1"
    local max_attempts=$((HEALTH_CHECK_TIMEOUT / HEALTH_CHECK_INTERVAL))
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if curl -sf http://localhost:${port}/health > /dev/null 2>&1; then
            return 0
        fi
        attempt=$((attempt + 1))
        sleep $HEALTH_CHECK_INTERVAL
    done
    return 1
}

# Main deployment logic
main() {
    log "Starting blue-green deployment for TSH ERP..."
    log "Version: ${VERSION}"

    # Change to deployment directory
    cd "$DEPLOY_DIR"

    # Determine slots
    ACTIVE_SLOT=$(get_active_slot)
    INACTIVE_SLOT=$(get_inactive_slot "$ACTIVE_SLOT")

    log "Current active slot: ${ACTIVE_SLOT}"
    log "Deploying to inactive slot: ${INACTIVE_SLOT}"

    # Set ports based on slots
    if [ "$INACTIVE_SLOT" == "blue" ]; then
        INACTIVE_PORT=8001
        ACTIVE_PORT=8011
    else
        INACTIVE_PORT=8011
        ACTIVE_PORT=8001
    fi

    # Step 1: Pull latest code
    log "Pulling latest code from GitHub..."
    git fetch origin
    git checkout main
    git pull origin main

    # Step 2: Build new image
    log "Building new Docker image for ${INACTIVE_SLOT} slot..."
    export VERSION="$VERSION"
    docker compose -f "$COMPOSE_FILE" build "app_${INACTIVE_SLOT}"

    # Step 3: Start inactive slot
    log "Starting ${INACTIVE_SLOT} slot..."
    if [ "$INACTIVE_SLOT" == "green" ]; then
        docker compose -f "$COMPOSE_FILE" --profile green up -d "app_${INACTIVE_SLOT}"
    else
        docker compose -f "$COMPOSE_FILE" up -d "app_${INACTIVE_SLOT}"
    fi

    # Step 4: Wait for health check
    log "Waiting for ${INACTIVE_SLOT} slot to be healthy (port ${INACTIVE_PORT})..."
    if check_health "$INACTIVE_PORT"; then
        success "${INACTIVE_SLOT} slot is healthy!"
    else
        error "${INACTIVE_SLOT} slot failed health check"
        error "Rolling back by stopping ${INACTIVE_SLOT} slot..."
        docker compose -f "$COMPOSE_FILE" stop "app_${INACTIVE_SLOT}"
        exit 1
    fi

    # Step 5: Run smoke tests on inactive slot
    log "Running smoke tests on ${INACTIVE_SLOT} slot..."
    if ! ./scripts/deployment/health_check.sh "http://localhost:${INACTIVE_PORT}"; then
        error "Smoke tests failed on ${INACTIVE_SLOT} slot"
        error "Rolling back by stopping ${INACTIVE_SLOT} slot..."
        docker compose -f "$COMPOSE_FILE" stop "app_${INACTIVE_SLOT}"
        exit 1
    fi
    success "Smoke tests passed!"

    # Step 6: Update Nginx to point to new slot
    log "Updating Nginx configuration to point to ${INACTIVE_SLOT} slot..."

    # Update upstream in nginx config
    if [ -f "/etc/nginx/sites-available/tsh-erp" ]; then
        sed -i "s|http://localhost:${ACTIVE_PORT}|http://localhost:${INACTIVE_PORT}|g" /etc/nginx/sites-available/tsh-erp
        nginx -t && nginx -s reload
        success "Nginx configuration updated and reloaded"
    else
        warning "Nginx config not found at /etc/nginx/sites-available/tsh-erp"
        warning "Manual Nginx update may be required"
    fi

    # Step 7: Wait to ensure traffic is flowing correctly
    log "Monitoring new deployment for 30 seconds..."
    sleep 30

    # Step 8: Final health check on public endpoint
    log "Verifying public endpoint..."
    if curl -sf https://erp.tsh.sale/health > /dev/null 2>&1; then
        success "Public endpoint is healthy!"
    else
        error "Public endpoint health check failed"
        error "Manual intervention required!"
        exit 1
    fi

    # Step 9: Stop old slot
    log "Stopping old ${ACTIVE_SLOT} slot..."
    docker compose -f "$COMPOSE_FILE" stop "app_${ACTIVE_SLOT}"
    success "Old ${ACTIVE_SLOT} slot stopped"

    # Step 10: Update environment variable for active slot
    if [ -f ".env.production" ]; then
        sed -i "s|ACTIVE_DEPLOYMENT_SLOT=.*|ACTIVE_DEPLOYMENT_SLOT=${INACTIVE_SLOT}|g" .env.production
        sed -i "s|DEPLOYMENT_SLOT=.*|DEPLOYMENT_SLOT=${INACTIVE_SLOT}|g" .env.production
    fi

    # Step 11: Cleanup old images
    log "Cleaning up old Docker images..."
    docker image prune -f

    # Deployment summary
    echo ""
    echo "============================================================================"
    success "Blue-Green Deployment Completed Successfully!"
    echo "============================================================================"
    echo "Previous active slot: ${ACTIVE_SLOT}"
    echo "New active slot: ${INACTIVE_SLOT}"
    echo "Version deployed: ${VERSION}"
    echo "Deployment time: $(date)"
    echo "============================================================================"
    echo ""
    echo "Service Status:"
    docker compose -f "$COMPOSE_FILE" ps
    echo ""
    success "TSH ERP is now running on ${INACTIVE_SLOT} slot with zero downtime!"
}

# Run main function
main "$@"
