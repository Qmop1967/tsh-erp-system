#!/bin/bash

# =====================================================
# Zoho Sync Auto-Healing Script
# Automatically fixes common sync issues
# =====================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Server details
SERVER="root@167.71.39.50"
DB_NAME="tsh_erp"

# Timestamp
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

echo -e "${BLUE}🔧 Zoho Sync Auto-Healing - $TIMESTAMP${NC}"
echo "=========================================="
echo ""

ACTIONS_TAKEN=0

# =====================================================
# 1. Re-queue Failed Items (< 5 retries)
# =====================================================
echo "📋 Checking failed items..."

FAILED_COUNT=$(ssh $SERVER "sudo -u postgres psql $DB_NAME -t -c \"SELECT COUNT(*) FROM tds_sync_queue WHERE status='failed' AND retry_count < 5;\" 2>/dev/null" | xargs || echo "0")

if [ "$FAILED_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}Found $FAILED_COUNT failed items (retriable)${NC}"
    echo "  → Re-queuing..."

    ssh $SERVER "sudo -u postgres psql $DB_NAME -c \"UPDATE tds_sync_queue SET status='pending', retry_count=retry_count+1, locked_until=NULL WHERE status='failed' AND retry_count < 5;\" >/dev/null 2>&1"

    echo -e "${GREEN}  ✅ Re-queued $FAILED_COUNT items${NC}"
    ACTIONS_TAKEN=$((ACTIONS_TAKEN + 1))
else
    echo "  ✅ No retriable failed items"
fi
echo ""

# =====================================================
# 2. Clear Stuck Locks (> 30 minutes)
# =====================================================
echo "🔒 Checking for stuck locks..."

STUCK_COUNT=$(ssh $SERVER "sudo -u postgres psql $DB_NAME -t -c \"SELECT COUNT(*) FROM tds_sync_queue WHERE locked_until < NOW() - INTERVAL '30 minutes' AND status='processing';\" 2>/dev/null" | xargs || echo "0")

if [ "$STUCK_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}Found $STUCK_COUNT stuck locks (> 30 min)${NC}"
    echo "  → Clearing locks and re-queuing..."

    ssh $SERVER "sudo -u postgres psql $DB_NAME -c \"UPDATE tds_sync_queue SET locked_until=NULL, status='pending' WHERE locked_until < NOW() - INTERVAL '30 minutes' AND status='processing';\" >/dev/null 2>&1"

    echo -e "${GREEN}  ✅ Cleared $STUCK_COUNT stuck locks${NC}"
    ACTIONS_TAKEN=$((ACTIONS_TAKEN + 1))
else
    echo "  ✅ No stuck locks found"
fi
echo ""

# =====================================================
# 3. Move Permanently Failed to Dead Letter Queue
# =====================================================
echo "💀 Checking permanently failed items..."

PERM_FAILED=$(ssh $SERVER "sudo -u postgres psql $DB_NAME -t -c \"SELECT COUNT(*) FROM tds_sync_queue WHERE status='failed' AND retry_count >= 5;\" 2>/dev/null" | xargs || echo "0")

if [ "$PERM_FAILED" -gt 0 ]; then
    echo -e "${YELLOW}Found $PERM_FAILED permanently failed items (≥ 5 retries)${NC}"
    echo "  → Moving to dead letter queue..."

    ssh $SERVER "sudo -u postgres psql $DB_NAME -c \"INSERT INTO tds_dead_letter_queue (original_id, entity_type, entity_id, operation, payload, error_message, failed_at) SELECT id, entity_type, entity_id, operation, payload, error_message, updated_at FROM tds_sync_queue WHERE status='failed' AND retry_count >= 5 ON CONFLICT DO NOTHING;\" >/dev/null 2>&1"

    ssh $SERVER "sudo -u postgres psql $DB_NAME -c \"DELETE FROM tds_sync_queue WHERE status='failed' AND retry_count >= 5;\" >/dev/null 2>&1"

    echo -e "${GREEN}  ✅ Moved $PERM_FAILED items to dead letter queue${NC}"
    ACTIONS_TAKEN=$((ACTIONS_TAKEN + 1))
else
    echo "  ✅ No permanently failed items"
fi
echo ""

# =====================================================
# 4. Check Worker Status
# =====================================================
echo "👷 Checking worker status..."

RECENT_ACTIVITY=$(ssh $SERVER "journalctl -u tsh-erp --since '5 minutes ago' --no-pager 2>/dev/null | grep -c 'worker.*processing' || echo '0'")

if [ "$RECENT_ACTIVITY" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  No worker activity in last 5 minutes${NC}"
    echo "  → Checking if service is running..."

    SERVICE_STATUS=$(ssh $SERVER "systemctl is-active tsh-erp" 2>/dev/null || echo "inactive")

    if [ "$SERVICE_STATUS" != "active" ]; then
        echo -e "${RED}  ❌ Service is not running!${NC}"
        echo "  → Restarting service..."

        ssh $SERVER "systemctl restart tsh-erp"
        sleep 5

        NEW_STATUS=$(ssh $SERVER "systemctl is-active tsh-erp" 2>/dev/null || echo "inactive")

        if [ "$NEW_STATUS" = "active" ]; then
            echo -e "${GREEN}  ✅ Service restarted successfully${NC}"
            ACTIONS_TAKEN=$((ACTIONS_TAKEN + 1))
        else
            echo -e "${RED}  ❌ Service restart failed - MANUAL INTERVENTION REQUIRED${NC}"
        fi
    else
        echo "  ℹ️  Service is running, but workers may be idle (no items to process)"
    fi
else
    echo -e "${GREEN}  ✅ Workers are active ($RECENT_ACTIVITY processing events)${NC}"
fi
echo ""

# =====================================================
# 5. Vacuum Old Completed Items (> 30 days)
# =====================================================
echo "🧹 Cleaning old completed items..."

OLD_COUNT=$(ssh $SERVER "sudo -u postgres psql $DB_NAME -t -c \"SELECT COUNT(*) FROM tds_sync_queue WHERE status='completed' AND updated_at < NOW() - INTERVAL '30 days';\" 2>/dev/null" | xargs || echo "0")

if [ "$OLD_COUNT" -gt 100 ]; then
    echo -e "${YELLOW}Found $OLD_COUNT old completed items (> 30 days)${NC}"
    echo "  → Archiving to logs and deleting..."

    # Archive to a log file first (optional)
    # ssh $SERVER "sudo -u postgres psql $DB_NAME -c \"COPY (SELECT * FROM tds_sync_queue WHERE status='completed' AND updated_at < NOW() - INTERVAL '30 days') TO '/tmp/archived_sync_$(date +%Y%m%d).csv' CSV HEADER;\" >/dev/null 2>&1"

    ssh $SERVER "sudo -u postgres psql $DB_NAME -c \"DELETE FROM tds_sync_queue WHERE status='completed' AND updated_at < NOW() - INTERVAL '30 days';\" >/dev/null 2>&1"

    echo -e "${GREEN}  ✅ Cleaned $OLD_COUNT old items${NC}"
    ACTIONS_TAKEN=$((ACTIONS_TAKEN + 1))
else
    echo "  ✅ No significant old items to clean"
fi
echo ""

# =====================================================
# 6. Check Database Connections
# =====================================================
echo "🔌 Checking database connections..."

DB_CONNS=$(ssh $SERVER "sudo -u postgres psql $DB_NAME -t -c \"SELECT count(*) FROM pg_stat_activity WHERE datname='$DB_NAME';\" 2>/dev/null" | xargs || echo "0")

echo "  Active connections: $DB_CONNS"

if [ "$DB_CONNS" -gt 80 ]; then
    echo -e "${YELLOW}  ⚠️  High connection count (> 80)${NC}"
    echo "  ℹ️  Consider checking for connection leaks"
else
    echo -e "${GREEN}  ✅ Connection count is normal${NC}"
fi
echo ""

# =====================================================
# SUMMARY
# =====================================================
echo "=========================================="
echo -e "${BLUE}🎯 Auto-Healing Summary${NC}"
echo "=========================================="
echo "Timestamp: $TIMESTAMP"
echo "Actions taken: $ACTIONS_TAKEN"
echo ""

if [ "$ACTIONS_TAKEN" -eq 0 ]; then
    echo -e "${GREEN}✅ System is healthy - no healing actions needed${NC}"
else
    echo -e "${YELLOW}🔧 Applied $ACTIONS_TAKEN healing action(s)${NC}"
    echo "Recommended: Monitor system for next 10-15 minutes"
fi
echo ""
echo "=========================================="

exit 0
