#!/bin/bash

# TSH ERP Ecosystem - Direct Docker Deployment Script
# TEMPORARY DEVELOPMENT MODE
#
# This script deploys the TSH ERP system directly via Docker commands
# GitHub CI/CD and Staging are DISABLED during this temporary mode
#
# Created: 2025-11-17
# Status: TEMPORARY DEVELOPMENT MODE

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVER_IP="167.71.39.50"
SERVER_USER="root"
PROJECT_PATH="/var/www/tsh-erp"
BRANCH="develop"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  TSH ERP - Direct Docker Deployment${NC}"
echo -e "${BLUE}  TEMPORARY DEVELOPMENT MODE${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Warning about temporary mode
echo -e "${YELLOW}⚠️  WARNING: TEMPORARY DEVELOPMENT MODE ACTIVE${NC}"
echo -e "${YELLOW}   - GitHub CI/CD: DISABLED${NC}"
echo -e "${YELLOW}   - Staging Environment: DISABLED${NC}"
echo -e "${YELLOW}   - Database: READ-ONLY${NC}"
echo ""

# Function to deploy
deploy() {
    local service=$1

    echo -e "${GREEN}Connecting to server ${SERVER_IP}...${NC}"

    if [ -z "$service" ] || [ "$service" == "all" ]; then
        echo -e "${GREEN}Deploying ALL services...${NC}"

        ssh ${SERVER_USER}@${SERVER_IP} << 'EOF'
            cd /var/www/tsh-erp

            echo "Pulling latest code..."
            git pull origin develop

            echo "Building and restarting containers..."
            docker-compose down
            docker-compose build --no-cache
            docker-compose up -d

            echo "Waiting for services to start..."
            sleep 10

            echo "Checking health..."
            echo "Backend:"
            curl -s http://localhost:8000/health || echo "Backend health check failed"

            echo ""
            echo "TDS Core:"
            curl -s http://localhost:8001/api/health || echo "TDS Core health check failed"

            echo ""
            echo "BFF:"
            curl -s http://localhost:8002/health || echo "BFF health check failed"

            echo ""
            echo "Container Status:"
            docker ps
EOF
    else
        echo -e "${GREEN}Deploying ${service} service...${NC}"

        ssh ${SERVER_USER}@${SERVER_IP} << EOF
            cd /var/www/tsh-erp

            echo "Pulling latest code..."
            git pull origin develop

            echo "Rebuilding ${service}..."
            docker-compose build ${service} --no-cache
            docker-compose restart ${service}

            echo "Waiting for service to start..."
            sleep 5

            echo "Checking ${service} logs..."
            docker-compose logs ${service} --tail=20
EOF
    fi

    echo -e "${GREEN}Deployment complete!${NC}"
}

# Function to check status
check_status() {
    echo -e "${GREEN}Checking deployment status...${NC}"

    ssh ${SERVER_USER}@${SERVER_IP} << 'EOF'
        cd /var/www/tsh-erp

        echo "Container Status:"
        docker ps

        echo ""
        echo "Git Status:"
        git status

        echo ""
        echo "Recent Commits:"
        git log --oneline -5

        echo ""
        echo "Database Connection Test:"
        PGPASSWORD='TSH@2025Secure!Production' psql -h localhost -U tsh_app_user -d tsh_erp_production -c "SELECT NOW();" 2>&1 || echo "Database connection failed"
EOF
}

# Function to view logs
view_logs() {
    local service=$1

    if [ -z "$service" ]; then
        service="backend"
    fi

    echo -e "${GREEN}Viewing ${service} logs...${NC}"

    ssh ${SERVER_USER}@${SERVER_IP} << EOF
        cd /var/www/tsh-erp
        docker-compose logs ${service} --tail=100 -f
EOF
}

# Function to restart services
restart() {
    local service=$1

    if [ -z "$service" ] || [ "$service" == "all" ]; then
        echo -e "${GREEN}Restarting ALL services...${NC}"

        ssh ${SERVER_USER}@${SERVER_IP} << 'EOF'
            cd /var/www/tsh-erp
            docker-compose restart

            echo "Waiting for services to start..."
            sleep 10

            echo "Container Status:"
            docker ps
EOF
    else
        echo -e "${GREEN}Restarting ${service}...${NC}"

        ssh ${SERVER_USER}@${SERVER_IP} << EOF
            cd /var/www/tsh-erp
            docker-compose restart ${service}

            echo "Waiting for service to start..."
            sleep 5

            echo "Container Status:"
            docker ps
EOF
    fi
}

# Main script
case "$1" in
    deploy)
        deploy "$2"
        ;;
    status)
        check_status
        ;;
    logs)
        view_logs "$2"
        ;;
    restart)
        restart "$2"
        ;;
    *)
        echo "Usage: $0 {deploy|status|logs|restart} [service]"
        echo ""
        echo "Commands:"
        echo "  deploy [service]   - Deploy all services or specific service"
        echo "  status            - Check current deployment status"
        echo "  logs [service]    - View logs (default: backend)"
        echo "  restart [service] - Restart all services or specific service"
        echo ""
        echo "Services: backend, tds-core, bff, frontend, all"
        echo ""
        echo "Examples:"
        echo "  $0 deploy all        # Deploy all services"
        echo "  $0 deploy backend    # Deploy only backend"
        echo "  $0 status            # Check status"
        echo "  $0 logs tds-core     # View TDS Core logs"
        echo "  $0 restart backend   # Restart backend service"
        echo ""
        echo -e "${YELLOW}NOTE: This script is for TEMPORARY DEVELOPMENT MODE only.${NC}"
        echo -e "${YELLOW}GitHub CI/CD and Staging are DISABLED.${NC}"
        exit 1
        ;;
esac
