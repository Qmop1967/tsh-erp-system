#!/bin/bash

# TDS Admin Dashboard Deployment Script
# Deploys the dashboard to VPS via Docker

set -e

echo "🚀 TDS Admin Dashboard Deployment Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DASHBOARD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$DASHBOARD_DIR/../.." && pwd)"
ENV_FILE="${ENV_FILE:-.env.production}"

echo -e "${YELLOW}Dashboard Directory: $DASHBOARD_DIR${NC}"
echo -e "${YELLOW}Root Directory: $ROOT_DIR${NC}"
echo -e "${YELLOW}Environment File: $ENV_FILE${NC}"
echo ""

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Use 'docker compose' or 'docker-compose' based on availability
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"
echo ""

# Step 1: Build the dashboard
echo "📦 Building TDS Admin Dashboard..."
cd "$ROOT_DIR"

$DOCKER_COMPOSE build tds_admin_dashboard

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dashboard built successfully${NC}"
else
    echo -e "${RED}❌ Dashboard build failed${NC}"
    exit 1
fi

echo ""

# Step 2: Stop existing container (if running)
echo "🛑 Stopping existing dashboard container (if any)..."
$DOCKER_COMPOSE --profile dashboard down tds_admin_dashboard || true
echo ""

# Step 3: Start the dashboard
echo "🚀 Starting TDS Admin Dashboard..."
$DOCKER_COMPOSE --profile dashboard up -d tds_admin_dashboard

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dashboard started successfully${NC}"
else
    echo -e "${RED}❌ Dashboard failed to start${NC}"
    exit 1
fi

echo ""

# Step 4: Wait for health check
echo "⏳ Waiting for dashboard to be healthy..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    health_status=$($DOCKER_COMPOSE ps tds_admin_dashboard --format json | grep -o '"Health":"[^"]*"' | cut -d'"' -f4 || echo "")

    if [ "$health_status" = "healthy" ]; then
        echo -e "${GREEN}✓ Dashboard is healthy and running${NC}"
        break
    fi

    attempt=$((attempt + 1))
    echo -e "${YELLOW}Attempt $attempt/$max_attempts: Status = $health_status${NC}"
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${YELLOW}⚠️  Dashboard health check timed out, but container is running${NC}"
fi

echo ""

# Step 5: Show container status
echo "📊 Container Status:"
$DOCKER_COMPOSE ps tds_admin_dashboard

echo ""

# Step 6: Show logs (last 20 lines)
echo "📝 Recent Logs:"
$DOCKER_COMPOSE logs --tail=20 tds_admin_dashboard

echo ""
echo -e "${GREEN}=========================================="
echo "✅ Deployment Complete!"
echo "==========================================${NC}"
echo ""
echo "Dashboard URL: http://localhost:3000"
echo ""
echo "Useful commands:"
echo "  View logs:     $DOCKER_COMPOSE logs -f tds_admin_dashboard"
echo "  Restart:       $DOCKER_COMPOSE restart tds_admin_dashboard"
echo "  Stop:          $DOCKER_COMPOSE stop tds_admin_dashboard"
echo "  Remove:        $DOCKER_COMPOSE down tds_admin_dashboard"
echo ""
