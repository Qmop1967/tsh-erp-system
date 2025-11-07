#!/bin/bash
# Unify Endpoints Script
# Ensures all API endpoints and authentication remain centralized and consistent
# Part of TSH ERP Unified Skills

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
TDS_API_URL="${TDS_API_URL:-http://localhost:8001}"
MAIN_ERP_URL="${MAIN_ERP_URL:-http://localhost:8000}"
LOG_FILE="/var/log/tds-core/endpoint-unification.log"

# Timestamp
timestamp() {
    date "+%Y-%m-%d %H:%M:%S"
}

# Log function
log() {
    echo "[$(timestamp)] $1" | tee -a "$LOG_FILE"
}

log "${GREEN}Starting endpoint unification check...${NC}"

# Track issues
ISSUES_FOUND=0

# ============================================================================
# 1. Check TDS Core API Availability
# ============================================================================

log "1️⃣  Checking TDS Core API availability..."

if curl -s -f "${TDS_API_URL}/health" > /dev/null 2>&1; then
    log "${GREEN}✓ TDS Core API is available${NC}"
else
    log "${RED}✗ TDS Core API is NOT available at ${TDS_API_URL}${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# ============================================================================
# 2. Check Main ERP API Availability
# ============================================================================

log "2️⃣  Checking Main ERP API availability..."

if curl -s -f "${MAIN_ERP_URL}/health" > /dev/null 2>&1; then
    log "${GREEN}✓ Main ERP API is available${NC}"
else
    log "${RED}✗ Main ERP API is NOT available at ${MAIN_ERP_URL}${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# ============================================================================
# 3. Verify Webhook Endpoints are Consistent
# ============================================================================

log "3️⃣  Verifying webhook endpoints..."

# Check products webhook
if curl -s -f "${TDS_API_URL}/webhooks/products" \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{}' 2>&1 | grep -q "422"; then
    log "${GREEN}✓ Products webhook endpoint exists and validates input${NC}"
else
    log "${YELLOW}⚠  Products webhook may have issues${NC}"
fi

# Check customers webhook
if curl -s -f "${TDS_API_URL}/webhooks/customers" \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{}' 2>&1 | grep -q "422"; then
    log "${GREEN}✓ Customers webhook endpoint exists and validates input${NC}"
else
    log "${YELLOW}⚠  Customers webhook may have issues${NC}"
fi

# Check invoices webhook
if curl -s -f "${TDS_API_URL}/webhooks/invoices" \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{}' 2>&1 | grep -q "422"; then
    log "${GREEN}✓ Invoices webhook endpoint exists and validates input${NC}"
else
    log "${YELLOW}⚠  Invoices webhook may have issues${NC}"
fi

# ============================================================================
# 4. Check Database Connectivity
# ============================================================================

log "4️⃣  Checking database connectivity..."

if PGPASSWORD="TSH@2025Secure!Production" psql \
    -h localhost \
    -U tsh_erp \
    -d tsh_erp \
    -c "SELECT 1" > /dev/null 2>&1; then
    log "${GREEN}✓ Database connection successful${NC}"
else
    log "${RED}✗ Database connection FAILED${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# ============================================================================
# 5. Verify Critical Tables Exist
# ============================================================================

log "5️⃣  Verifying critical TDS tables exist..."

TABLES=(
    "tds_inbox_events"
    "tds_sync_queue"
    "tds_dead_letter_queue"
    "products"
    "product_prices"
    "pricelists"
)

for TABLE in "${TABLES[@]}"; do
    if PGPASSWORD="TSH@2025Secure!Production" psql \
        -h localhost \
        -U tsh_erp \
        -d tsh_erp \
        -c "SELECT 1 FROM ${TABLE} LIMIT 1" > /dev/null 2>&1; then
        log "${GREEN}✓ Table ${TABLE} exists${NC}"
    else
        log "${RED}✗ Table ${TABLE} is MISSING${NC}"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
done

# ============================================================================
# 6. Check API Documentation Endpoints
# ============================================================================

log "6️⃣  Checking API documentation availability..."

if curl -s -f "${TDS_API_URL}/docs" > /dev/null 2>&1; then
    log "${GREEN}✓ TDS Core API docs available at ${TDS_API_URL}/docs${NC}"
else
    log "${YELLOW}⚠  TDS Core API docs not available${NC}"
fi

if curl -s -f "${MAIN_ERP_URL}/docs" > /dev/null 2>&1; then
    log "${GREEN}✓ Main ERP API docs available at ${MAIN_ERP_URL}/docs${NC}"
else
    log "${YELLOW}⚠  Main ERP API docs not available${NC}"
fi

# ============================================================================
# 7. Verify Service Status
# ============================================================================

log "7️⃣  Verifying service status..."

if systemctl is-active --quiet tds-core-api.service; then
    log "${GREEN}✓ TDS Core service is running${NC}"
else
    log "${RED}✗ TDS Core service is NOT running${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

if systemctl is-active --quiet tsh-erp.service; then
    log "${GREEN}✓ Main ERP service is running${NC}"
else
    log "${RED}✗ Main ERP service is NOT running${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# ============================================================================
# 8. Check Nginx/Reverse Proxy Configuration
# ============================================================================

log "8️⃣  Checking reverse proxy configuration..."

if systemctl is-active --quiet nginx; then
    log "${GREEN}✓ Nginx is running${NC}"

    # Check if TDS endpoints are proxied correctly
    if curl -s -f "https://erp.tsh.sale/api/tds/health" > /dev/null 2>&1; then
        log "${GREEN}✓ TDS endpoints are accessible via reverse proxy${NC}"
    else
        log "${YELLOW}⚠  TDS endpoints may not be properly proxied${NC}"
    fi
else
    log "${YELLOW}⚠  Nginx is not running${NC}"
fi

# ============================================================================
# 9. Verify Webhook Health
# ============================================================================

log "9️⃣  Checking webhook health..."

HEALTH_RESPONSE=$(curl -s "${TDS_API_URL}/webhooks/health?hours=1" || echo '{}')
HEALTH_SCORE=$(echo "$HEALTH_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('metrics', {}).get('health_score', 0))" 2>/dev/null || echo "0")

if [ "$HEALTH_SCORE" -ge 90 ]; then
    log "${GREEN}✓ Webhook health score: ${HEALTH_SCORE}/100${NC}"
elif [ "$HEALTH_SCORE" -ge 70 ]; then
    log "${YELLOW}⚠ Webhook health score: ${HEALTH_SCORE}/100 (degraded)${NC}"
else
    log "${RED}✗ Webhook health score: ${HEALTH_SCORE}/100 (unhealthy)${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# ============================================================================
# 10. Check Log Files
# ============================================================================

log "🔟  Checking log files..."

LOG_FILES=(
    "/var/log/tds-core/webhook-monitor.log"
    "/var/log/tds-core/tds_monitor.log"
    "/var/log/tds-core/endpoint-unification.log"
)

for LOG in "${LOG_FILES[@]}"; do
    if [ -f "$LOG" ]; then
        SIZE=$(du -h "$LOG" | cut -f1)
        log "${GREEN}✓ Log file exists: ${LOG} (${SIZE})${NC}"
    else
        log "${YELLOW}⚠  Log file missing: ${LOG}${NC}"
        # Create if missing
        mkdir -p "$(dirname "$LOG")"
        touch "$LOG"
        log "${GREEN}✓ Created missing log file${NC}"
    fi
done

# ============================================================================
# Summary
# ============================================================================

log ""
log "==============================================="
log "ENDPOINT UNIFICATION CHECK COMPLETE"
log "==============================================="

if [ $ISSUES_FOUND -eq 0 ]; then
    log "${GREEN}✅ ALL CHECKS PASSED - System is unified and operational${NC}"
    log ""
    log "Key Endpoints:"
    log "  - TDS Core API: ${TDS_API_URL}"
    log "  - Main ERP API: ${MAIN_ERP_URL}"
    log "  - Public TDS: https://erp.tsh.sale/api/tds"
    log "  - Webhook Health: ${TDS_API_URL}/webhooks/health"
    log "  - API Docs: ${TDS_API_URL}/docs"
    exit 0
else
    log "${RED}❌ FOUND ${ISSUES_FOUND} ISSUE(S) - Attention required${NC}"
    log ""
    log "Please review the issues above and take corrective action."
    log "Refer to /opt/tds_core/WEBHOOK_TROUBLESHOOTING.md for help."
    exit 1
fi
