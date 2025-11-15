#!/bin/bash
# ============================================================================
# TSH ERP - Health Check Script
# ============================================================================
# Purpose: Comprehensive health verification for deployment
# Usage: ./health_check.sh [base_url]
# ============================================================================

set -euo pipefail

# Configuration
BASE_URL="${1:-http://localhost:8000}"
TIMEOUT=10

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Counters
PASSED=0
FAILED=0

# Functions
test_endpoint() {
    local endpoint="$1"
    local expected_status="${2:-200}"
    local description="$3"

    echo -n "Testing: ${description}... "

    status_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "${BASE_URL}${endpoint}" || echo "000")

    if [ "$status_code" == "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} (${status_code})"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (Expected: ${expected_status}, Got: ${status_code})"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

echo "============================================================================"
echo "TSH ERP Health Check"
echo "============================================================================"
echo "Base URL: ${BASE_URL}"
echo "Timeout: ${TIMEOUT}s"
echo "============================================================================"
echo ""

# Test 1: Basic health endpoint
test_endpoint "/health" "200" "Health endpoint"

# Test 2: API documentation
test_endpoint "/docs" "200" "API documentation"

# Test 3: OpenAPI spec
test_endpoint "/openapi.json" "200" "OpenAPI specification"

# Test 4: Root endpoint
test_endpoint "/" "200" "Root endpoint"

# Test 5: Authentication endpoint (should return 422 for invalid input)
echo -n "Testing: Authentication endpoint... "
status_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" \
    -X POST "${BASE_URL}/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"wrong"}' || echo "000")

if [ "$status_code" == "401" ] || [ "$status_code" == "422" ]; then
    echo -e "${GREEN}✅ PASS${NC} (${status_code})"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ FAIL${NC} (Expected: 401 or 422, Got: ${status_code})"
    FAILED=$((FAILED + 1))
fi

# Test 6: Database connectivity (via health endpoint with detailed response)
echo -n "Testing: Database connectivity... "
db_status=$(curl -s --max-time "$TIMEOUT" "${BASE_URL}/health" | grep -o '"database":"ok"' || echo "")
if [ -n "$db_status" ]; then
    echo -e "${GREEN}✅ PASS${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${YELLOW}⚠️  WARN${NC} (Cannot verify database status)"
fi

# Test 7: Redis connectivity (via health endpoint with detailed response)
echo -n "Testing: Redis connectivity... "
redis_status=$(curl -s --max-time "$TIMEOUT" "${BASE_URL}/health" | grep -o '"redis":"ok"' || echo "")
if [ -n "$redis_status" ]; then
    echo -e "${GREEN}✅ PASS${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${YELLOW}⚠️  WARN${NC} (Cannot verify Redis status)"
fi

# Summary
echo ""
echo "============================================================================"
echo "Health Check Results"
echo "============================================================================"
echo -e "Passed: ${GREEN}${PASSED}${NC}"
echo -e "Failed: ${RED}${FAILED}${NC}"
echo "============================================================================"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All health checks passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some health checks failed!${NC}"
    exit 1
fi
