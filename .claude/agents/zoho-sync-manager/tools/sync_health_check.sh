#!/bin/bash

# =====================================================
# Zoho Sync Health Check Script
# Comprehensive monitoring for Zoho sync system
# =====================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Server details
SERVER="root@167.71.39.50"
DB_NAME="tsh_erp"

# Thresholds
WARN_PENDING=50
CRITICAL_PENDING=200
WARN_FAILED=5
CRITICAL_FAILED=10
WARN_DELAY_MINUTES=30
CRITICAL_DELAY_MINUTES=120

# Output file
REPORT_FILE="/tmp/zoho_sync_health_$(date +%Y%m%d_%H%M%S).txt"

echo "🔍 Zoho Sync Health Check - $(date)" | tee $REPORT_FILE
echo "========================================" | tee -a $REPORT_FILE
echo "" | tee -a $REPORT_FILE

# =====================================================
# 1. SERVICE STATUS CHECK
# =====================================================
echo "📊 Service Status Check" | tee -a $REPORT_FILE
echo "---" | tee -a $REPORT_FILE

SERVICE_STATUS=$(ssh $SERVER "systemctl is-active tsh-erp" 2>/dev/null || echo "unknown")

if [ "$SERVICE_STATUS" = "active" ]; then
    echo -e "${GREEN}✅ TSH ERP service is running${NC}" | tee -a $REPORT_FILE
else
    echo -e "${RED}❌ TSH ERP service is NOT running (status: $SERVICE_STATUS)${NC}" | tee -a $REPORT_FILE
    echo "🔧 Auto-heal: Attempting to restart service..." | tee -a $REPORT_FILE
    ssh $SERVER "systemctl restart tsh-erp"
    sleep 5
    SERVICE_STATUS=$(ssh $SERVER "systemctl is-active tsh-erp" 2>/dev/null || echo "unknown")
    if [ "$SERVICE_STATUS" = "active" ]; then
        echo -e "${GREEN}✅ Service restarted successfully${NC}" | tee -a $REPORT_FILE
    else
        echo -e "${RED}❌ Service restart failed - MANUAL INTERVENTION REQUIRED${NC}" | tee -a $REPORT_FILE
    fi
fi
echo "" | tee -a $REPORT_FILE

# =====================================================
# 2. QUEUE STATUS CHECK
# =====================================================
echo "📋 Queue Status Check" | tee -a $REPORT_FILE
echo "---" | tee -a $REPORT_FILE

QUEUE_STATS=$(ssh $SERVER "sudo -u postgres psql $DB_NAME -t -c \"SELECT status, COUNT(*) FROM tds_sync_queue GROUP BY status ORDER BY status;\" 2>/dev/null" || echo "ERROR")

if [ "$QUEUE_STATS" = "ERROR" ]; then
    echo -e "${RED}❌ Failed to query queue status${NC}" | tee -a $REPORT_FILE
else
    echo "$QUEUE_STATS" | while IFS='|' read -r status count; do
        status=$(echo $status | xargs)
        count=$(echo $count | xargs)

        if [ "$status" = "pending" ]; then
            if [ "$count" -lt "$WARN_PENDING" ]; then
                echo -e "${GREEN}✅ Pending: $count items${NC}" | tee -a $REPORT_FILE
            elif [ "$count" -lt "$CRITICAL_PENDING" ]; then
                echo -e "${YELLOW}⚠️  Pending: $count items (threshold: $WARN_PENDING)${NC}" | tee -a $REPORT_FILE
            else
                echo -e "${RED}🔴 Pending: $count items (CRITICAL: > $CRITICAL_PENDING)${NC}" | tee -a $REPORT_FILE
            fi
        elif [ "$status" = "failed" ]; then
            if [ "$count" -lt "$WARN_FAILED" ]; then
                echo -e "${GREEN}✅ Failed: $count items${NC}" | tee -a $REPORT_FILE
            elif [ "$count" -lt "$CRITICAL_FAILED" ]; then
                echo -e "${YELLOW}⚠️  Failed: $count items${NC}" | tee -a $REPORT_FILE
                echo "  🔧 Auto-heal: Re-queuing failed items..." | tee -a $REPORT_FILE
                ssh $SERVER "sudo -u postgres psql $DB_NAME -c \"UPDATE tds_sync_queue SET status='pending', retry_count=retry_count+1, locked_until=NULL, error_message=NULL WHERE status='failed' AND retry_count < 5;\" >/dev/null 2>&1"
                echo "  ✅ Failed items re-queued" | tee -a $REPORT_FILE
            else
                echo -e "${RED}🔴 Failed: $count items (CRITICAL: > $CRITICAL_FAILED)${NC}" | tee -a $REPORT_FILE
                echo "  ⚠️  Too many failures - check error patterns" | tee -a $REPORT_FILE
            fi
        else
            echo "  $status: $count items" | tee -a $REPORT_FILE
        fi
    done
fi
echo "" | tee -a $REPORT_FILE

# =====================================================
# 3. SYNC DELAY CHECK
# =====================================================
echo "⏰ Sync Delay Check" | tee -a $REPORT_FILE
echo "---" | tee -a $REPORT_FILE

SYNC_DELAYS=$(ssh $SERVER "sudo -u postgres psql $DB_NAME -t -c \"SELECT entity_type, EXTRACT(EPOCH FROM (NOW() - MAX(updated_at)))/60 as delay_minutes FROM tds_sync_queue WHERE status='completed' GROUP BY entity_type;\" 2>/dev/null" || echo "ERROR")

if [ "$SYNC_DELAYS" = "ERROR" ]; then
    echo -e "${RED}❌ Failed to check sync delays${NC}" | tee -a $REPORT_FILE
else
    echo "$SYNC_DELAYS" | while IFS='|' read -r entity delay; do
        entity=$(echo $entity | xargs)
        delay=$(echo $delay | xargs)
        delay_int=$(printf "%.0f" "$delay" 2>/dev/null || echo "0")

        if [ "$delay_int" -lt "$WARN_DELAY_MINUTES" ]; then
            echo -e "${GREEN}✅ $entity: ${delay_int} min ago${NC}" | tee -a $REPORT_FILE
        elif [ "$delay_int" -lt "$CRITICAL_DELAY_MINUTES" ]; then
            echo -e "${YELLOW}⚠️  $entity: ${delay_int} min ago (warning threshold: ${WARN_DELAY_MINUTES}min)${NC}" | tee -a $REPORT_FILE
        else
            echo -e "${RED}🔴 $entity: ${delay_int} min ago (CRITICAL: > ${CRITICAL_DELAY_MINUTES}min)${NC}" | tee -a $REPORT_FILE
        fi
    done
fi
echo "" | tee -a $REPORT_FILE

# =====================================================
# 4. WORKER STATUS CHECK
# =====================================================
echo "👷 Worker Status Check" | tee -a $REPORT_FILE
echo "---" | tee -a $REPORT_FILE

WORKER_LOGS=$(ssh $SERVER "journalctl -u tsh-erp -n 200 --no-pager 2>/dev/null | grep -i 'worker.*started\|worker.*processing' | tail -10" || echo "ERROR")

if [ "$WORKER_LOGS" = "ERROR" ]; then
    echo -e "${RED}❌ Failed to check worker logs${NC}" | tee -a $REPORT_FILE
else
    WORKER_COUNT=$(echo "$WORKER_LOGS" | grep -c "worker.*started" || echo "0")
    if [ "$WORKER_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✅ Workers active (found $WORKER_COUNT startup messages)${NC}" | tee -a $REPORT_FILE
    else
        echo -e "${YELLOW}⚠️  No recent worker activity detected${NC}" | tee -a $REPORT_FILE
    fi
fi
echo "" | tee -a $REPORT_FILE

# =====================================================
# 5. ERROR PATTERN ANALYSIS
# =====================================================
echo "🔍 Error Pattern Analysis" | tee -a $REPORT_FILE
echo "---" | tee -a $REPORT_FILE

ERROR_PATTERNS=$(ssh $SERVER "sudo -u postgres psql $DB_NAME -t -c \"SELECT SUBSTRING(error_message, 1, 80) as error, COUNT(*) FROM tds_sync_queue WHERE status='failed' GROUP BY error ORDER BY COUNT(*) DESC LIMIT 5;\" 2>/dev/null" || echo "ERROR")

if [ "$ERROR_PATTERNS" = "ERROR" ] || [ -z "$ERROR_PATTERNS" ]; then
    echo "  No errors found or unable to query" | tee -a $REPORT_FILE
else
    echo "$ERROR_PATTERNS" | while IFS='|' read -r error count; do
        error=$(echo $error | xargs)
        count=$(echo $count | xargs)
        echo "  ❌ [$count] $error" | tee -a $REPORT_FILE
    done
fi
echo "" | tee -a $REPORT_FILE

# =====================================================
# 6. LOCKED ITEMS CHECK
# =====================================================
echo "🔒 Locked Items Check" | tee -a $REPORT_FILE
echo "---" | tee -a $REPORT_FILE

STUCK_LOCKS=$(ssh $SERVER "sudo -u postgres psql $DB_NAME -t -c \"SELECT COUNT(*) FROM tds_sync_queue WHERE locked_until < NOW() - INTERVAL '30 minutes' AND status='processing';\" 2>/dev/null" || echo "ERROR")

if [ "$STUCK_LOCKS" = "ERROR" ]; then
    echo -e "${RED}❌ Failed to check locked items${NC}" | tee -a $REPORT_FILE
else
    STUCK_LOCKS=$(echo $STUCK_LOCKS | xargs)
    if [ "$STUCK_LOCKS" -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Found $STUCK_LOCKS stuck locks (> 30 min old)${NC}" | tee -a $REPORT_FILE
        echo "  🔧 Auto-heal: Clearing stuck locks..." | tee -a $REPORT_FILE
        ssh $SERVER "sudo -u postgres psql $DB_NAME -c \"UPDATE tds_sync_queue SET locked_until=NULL, status='pending' WHERE locked_until < NOW() - INTERVAL '30 minutes' AND status='processing';\" >/dev/null 2>&1"
        echo "  ✅ Stuck locks cleared and re-queued" | tee -a $REPORT_FILE
    else
        echo -e "${GREEN}✅ No stuck locks detected${NC}" | tee -a $REPORT_FILE
    fi
fi
echo "" | tee -a $REPORT_FILE

# =====================================================
# 7. SYSTEM RESOURCES
# =====================================================
echo "💻 System Resources" | tee -a $REPORT_FILE
echo "---" | tee -a $REPORT_FILE

MEMORY=$(ssh $SERVER "free -h | grep Mem" || echo "ERROR")
DISK=$(ssh $SERVER "df -h / | tail -1" || echo "ERROR")

if [ "$MEMORY" != "ERROR" ]; then
    echo "  Memory: $MEMORY" | tee -a $REPORT_FILE
fi
if [ "$DISK" != "ERROR" ]; then
    echo "  Disk: $DISK" | tee -a $REPORT_FILE
fi
echo "" | tee -a $REPORT_FILE

# =====================================================
# SUMMARY
# =====================================================
echo "========================================" | tee -a $REPORT_FILE
echo "📊 Health Check Complete" | tee -a $REPORT_FILE
echo "Report saved to: $REPORT_FILE" | tee -a $REPORT_FILE
echo "Timestamp: $(date)" | tee -a $REPORT_FILE
echo "========================================" | tee -a $REPORT_FILE

# Return report file path for agent to read
echo ""
echo "📄 Full report available at: $REPORT_FILE"
