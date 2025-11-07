#!/bin/bash

# ============================================================================
# TSH ERP - BFF Deployment Script
# Deploys the BFF (Backend For Frontend) layer to production
# ============================================================================

set -e  # Exit on error

echo "========================================="
echo "TSH ERP - BFF Deployment"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ============================================================================
# Step 1: Pre-deployment Checks
# ============================================================================

echo -e "${YELLOW}[1/7] Running pre-deployment checks...${NC}"

# Check if we're in the correct directory
if [ ! -f "app/main.py" ]; then
    echo -e "${RED}Error: Not in TSH_ERP_Ecosystem directory${NC}"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✓ Python version: $PYTHON_VERSION"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

echo -e "${GREEN}✓ Pre-deployment checks passed${NC}"
echo ""

# ============================================================================
# Step 2: Install/Update Dependencies
# ============================================================================

echo -e "${YELLOW}[2/7] Installing dependencies...${NC}"

pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# ============================================================================
# Step 3: Database Migrations
# ============================================================================

echo -e "${YELLOW}[3/7] Running database migrations...${NC}"

# Check if alembic is configured
if [ -d "alembic" ]; then
    alembic upgrade head
    echo -e "${GREEN}✓ Database migrations completed${NC}"
else
    echo -e "${YELLOW}⚠ Alembic not configured, skipping migrations${NC}"
fi

echo ""

# ============================================================================
# Step 4: Verify BFF Routes
# ============================================================================

echo -e "${YELLOW}[4/7] Verifying BFF routes...${NC}"

# Count BFF router files
BFF_ROUTERS=$(find app/bff/routers -name "*.py" -type f | wc -l)
echo "✓ BFF router files: $BFF_ROUTERS"

# Check if main.py includes BFF
if grep -q "bff_router" app/main.py; then
    echo "✓ BFF router is integrated in main.py"
else
    echo -e "${RED}✗ BFF router NOT found in main.py${NC}"
    exit 1
fi

echo -e "${GREEN}✓ BFF routes verified${NC}"
echo ""

# ============================================================================
# Step 5: Run Tests
# ============================================================================

echo -e "${YELLOW}[5/7] Running tests...${NC}"

if [ -d "tests/bff" ]; then
    pytest tests/bff/ -v --maxfail=5 || {
        echo -e "${YELLOW}⚠ Some tests failed, continue anyway? (y/n)${NC}"
        read -r response
        if [[ "$response" != "y" ]]; then
            exit 1
        fi
    }
    echo -e "${GREEN}✓ Tests completed${NC}"
else
    echo -e "${YELLOW}⚠ No BFF tests found, skipping${NC}"
fi

echo ""

# ============================================================================
# Step 6: Stop Existing Server
# ============================================================================

echo -e "${YELLOW}[6/7] Stopping existing server...${NC}"

# Find and kill existing uvicorn processes
pkill -f "uvicorn app.main:app" || echo "No existing server found"

echo -e "${GREEN}✓ Existing server stopped${NC}"
echo ""

# ============================================================================
# Step 7: Start Server
# ============================================================================

echo -e "${YELLOW}[7/7] Starting production server...${NC}"

# Start server with gunicorn + uvicorn workers
nohup gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --daemon

# Wait for server to start
sleep 5

# Verify server is running
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Server started successfully${NC}"
else
    echo -e "${RED}✗ Server failed to start${NC}"
    exit 1
fi

echo ""

# ============================================================================
# Deployment Complete
# ============================================================================

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}✓ BFF Deployment Completed Successfully!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Server running at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "BFF Endpoints: http://localhost:8000/api/bff/mobile/"
echo ""
echo "Logs:"
echo "  - Access: logs/access.log"
echo "  - Error: logs/error.log"
echo ""
echo "To stop the server:"
echo "  pkill -f 'gunicorn app.main:app'"
echo ""
