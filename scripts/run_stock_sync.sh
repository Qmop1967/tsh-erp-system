#!/bin/bash
# TDS Stock Sync Wrapper Script
# This script sets up the environment and runs the stock sync

# Set working directory
cd /Users/khaleelal-mulla/TSH_ERP_Ecosystem || exit 1

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Activate virtual environment if it exists
if [ -d .venv ]; then
    source .venv/bin/activate
fi

# Run the sync via API call (more reliable)
# This assumes the backend is running
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"

echo "=================================================="
echo "TDS Stock Sync - $(date)"
echo "=================================================="

# Check if backend is running
if curl -s -f "${BACKEND_URL}/api/bff/tds/health" > /dev/null 2>&1; then
    echo "✓ Backend is running"

    # Trigger stock sync via API
    echo "Triggering stock sync..."
    response=$(curl -s -X POST "${BACKEND_URL}/api/bff/tds/sync/stock?batch_size=200&active_only=true")

    # Check if successful
    if echo "$response" | grep -q '"success":true'; then
        echo "✓ Stock sync completed successfully"
        echo "$response" | python3 -m json.tool
    else
        echo "✗ Stock sync failed"
        echo "$response"
        exit 1
    fi
else
    echo "✗ Backend is not running at ${BACKEND_URL}"
    echo "  Please start the backend with: uvicorn app.main:app --host 0.0.0.0 --port 8000"
    exit 1
fi

echo "=================================================="
echo "Sync completed at $(date)"
echo "=================================================="
