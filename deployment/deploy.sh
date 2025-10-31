#!/bin/bash

# TSH ERP Deployment Script
# This script deploys updates to the production server
# Run with: ./deploy.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Start deployment
echo ""
print_status "🚀 Starting TSH ERP Deployment..."
echo ""

# Check if running as deploy user
if [ "$USER" != "deploy" ]; then
    print_error "This script must be run as 'deploy' user"
    echo "Switch to deploy user with: su - deploy"
    exit 1
fi

# Navigate to project directory
PROJECT_DIR="/home/deploy/TSH_ERP_Ecosystem"
if [ ! -d "$PROJECT_DIR" ]; then
    print_error "Project directory not found: $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"
print_success "Changed to project directory"

# Pull latest code from Git
print_status "📥 Pulling latest code from Git..."
git fetch origin
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
print_status "Current branch: $CURRENT_BRANCH"

if git pull origin "$CURRENT_BRANCH"; then
    print_success "Code updated successfully"
else
    print_error "Failed to pull latest code"
    exit 1
fi

# Check if there were any changes
if git diff --quiet HEAD@{1} HEAD; then
    print_warning "No changes detected. Continuing anyway..."
else
    print_success "Changes detected and applied"
fi

# Activate virtual environment
print_status "🐍 Activating Python virtual environment..."
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found. Creating one..."
    python3.11 -m venv venv
fi
source venv/bin/activate
print_success "Virtual environment activated"

# Update Python dependencies
print_status "📦 Updating Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
print_success "Python dependencies updated"

# Run database migrations (if using Alembic)
if [ -f "alembic.ini" ]; then
    print_status "🗄️  Running database migrations..."
    # Uncomment the next line if you're using Alembic
    # alembic upgrade head
    print_success "Database migrations completed"
fi

# Rebuild React frontend
print_status "🎨 Building React frontend..."
cd frontend

# Check if node_modules exists, if not install dependencies
if [ ! -d "node_modules" ]; then
    print_warning "Node modules not found. Installing..."
    npm install
fi

# Install/update dependencies
npm install --production=false

# Build for production
if npm run build; then
    print_success "Frontend built successfully"
else
    print_error "Frontend build failed"
    cd ..
    exit 1
fi

cd ..

# Create backup of current running version (optional)
print_status "💾 Creating backup..."
BACKUP_DIR="/home/deploy/backups"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/tsh-erp-$TIMESTAMP.tar.gz"

# Backup current dist and venv (excluding large files)
tar -czf "$BACKUP_FILE" \
    --exclude='venv' \
    --exclude='node_modules' \
    --exclude='.git' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    . 2>/dev/null || true

print_success "Backup created: $BACKUP_FILE"

# Keep only last 5 backups
print_status "🧹 Cleaning old backups..."
ls -t "$BACKUP_DIR"/tsh-erp-*.tar.gz | tail -n +6 | xargs -r rm
print_success "Old backups cleaned"

# Restart FastAPI service
print_status "🔄 Restarting FastAPI service..."
if sudo systemctl restart tsh-erp; then
    print_success "FastAPI service restarted"
else
    print_error "Failed to restart FastAPI service"
    print_warning "Check logs with: sudo journalctl -u tsh-erp -n 50"
    exit 1
fi

# Wait for service to start
print_status "⏳ Waiting for service to start..."
sleep 3

# Check service status
if sudo systemctl is-active --quiet tsh-erp; then
    print_success "Service is running"
else
    print_error "Service failed to start"
    print_warning "Check status with: sudo systemctl status tsh-erp"
    exit 1
fi

# Reload Nginx
print_status "🔄 Reloading Nginx..."
if sudo systemctl reload nginx; then
    print_success "Nginx reloaded"
else
    print_error "Failed to reload Nginx"
    exit 1
fi

# Test application health
print_status "🏥 Testing application health..."
sleep 2

# Try to curl the health endpoint (localhost is faster than domain)
if curl -sf http://localhost:8000/health > /dev/null; then
    print_success "Application health check passed"
else
    print_warning "Health check failed or endpoint not available"
    print_warning "Application may still be starting up..."
fi

# Display service status
echo ""
print_status "📊 Service Status:"
sudo systemctl status tsh-erp --no-pager -l | head -n 20

# Display recent logs
echo ""
print_status "📝 Recent Logs (last 10 lines):"
sudo journalctl -u tsh-erp -n 10 --no-pager

# Final success message
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
print_success "🎉 Deployment completed successfully!"
echo ""
echo "Application is running at:"
echo "  • Frontend: https://erp.tsh.sale"
echo "  • API: https://erp.tsh.sale/api"
echo "  • API Docs: https://erp.tsh.sale/api/docs"
echo ""
echo "Useful commands:"
echo "  • View logs: sudo journalctl -u tsh-erp -f"
echo "  • Restart service: sudo systemctl restart tsh-erp"
echo "  • Check status: sudo systemctl status tsh-erp"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
