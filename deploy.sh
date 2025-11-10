#!/bin/bash
# TSH ERP System - Deployment Script
# Usage: ./deploy.sh [build|start|stop|restart|logs|status]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    print_success "Docker and Docker Compose are installed"
}

# Build Docker images
build() {
    print_info "Building Docker images..."
    docker-compose build --no-cache
    print_success "Docker images built successfully"
}

# Start services
start() {
    print_info "Starting TSH ERP System..."

    # Check if .env.production exists
    if [ ! -f ".env.production" ]; then
        print_error ".env.production file not found!"
        exit 1
    fi

    # Start services
    docker-compose up -d

    print_info "Waiting for services to be healthy..."
    sleep 10

    # Check health
    if docker-compose ps | grep -q "healthy"; then
        print_success "TSH ERP System started successfully!"
        print_info "Access the application at: http://localhost:8000"
        print_info "View logs with: ./deploy.sh logs"
    else
        print_error "Services are not healthy. Check logs with: ./deploy.sh logs"
        exit 1
    fi
}

# Stop services
stop() {
    print_info "Stopping TSH ERP System..."
    docker-compose down
    print_success "TSH ERP System stopped"
}

# Restart services
restart() {
    print_info "Restarting TSH ERP System..."
    docker-compose restart
    print_success "TSH ERP System restarted"
}

# View logs
logs() {
    docker-compose logs -f --tail=100
}

# Check status
status() {
    print_info "TSH ERP System Status:"
    docker-compose ps
    echo ""
    print_info "Container Health:"
    docker-compose ps | grep -E "(healthy|unhealthy)" || echo "No health status available"
}

# Run database migrations
migrate() {
    print_info "Running database migrations..."
    docker-compose exec app alembic upgrade head
    print_success "Database migrations completed"
}

# Create database backup
backup() {
    print_info "Creating database backup..."
    BACKUP_FILE="backups/tsh_erp_$(date +%Y%m%d_%H%M%S).sql"
    docker-compose exec -T postgres pg_dump -U tsh_admin tsh_erp > "$BACKUP_FILE"
    print_success "Database backup created: $BACKUP_FILE"
}

# Update application (pull latest code and restart)
update() {
    print_info "Updating TSH ERP System..."

    # Pull latest code
    git pull origin main

    # Rebuild images
    build

    # Stop services
    stop

    # Run migrations
    start
    migrate

    print_success "TSH ERP System updated successfully!"
}

# Show help
help() {
    echo "TSH ERP System - Deployment Script"
    echo ""
    echo "Usage: ./deploy.sh [command]"
    echo ""
    echo "Commands:"
    echo "  build      - Build Docker images"
    echo "  start      - Start all services"
    echo "  stop       - Stop all services"
    echo "  restart    - Restart all services"
    echo "  logs       - View application logs"
    echo "  status     - Show service status"
    echo "  migrate    - Run database migrations"
    echo "  backup     - Create database backup"
    echo "  update     - Pull latest code and restart"
    echo "  help       - Show this help message"
    echo ""
}

# Main script
main() {
    check_docker

    case "$1" in
        build)
            build
            ;;
        start)
            start
            ;;
        stop)
            stop
            ;;
        restart)
            restart
            ;;
        logs)
            logs
            ;;
        status)
            status
            ;;
        migrate)
            migrate
            ;;
        backup)
            backup
            ;;
        update)
            update
            ;;
        help|--help|-h|"")
            help
            ;;
        *)
            print_error "Unknown command: $1"
            help
            exit 1
            ;;
    esac
}

main "$@"
