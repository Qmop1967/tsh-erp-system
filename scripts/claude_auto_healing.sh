#!/bin/bash

# ============================================================================
# Claude Code Auto-Healing Agent Integration
# ============================================================================
# This script receives auto-healing suggestions from GitHub Actions
# and executes them using Claude Code Agent on the VPS
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
HEALING_DIR="/tmp/tsh_autoheal"
LOG_FILE="/var/log/tsh_erp/auto_healing.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# Logging Functions
# ============================================================================
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1" | tee -a "$LOG_FILE"
}

# ============================================================================
# Create Healing Directory
# ============================================================================
mkdir -p "$HEALING_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

log "============================================"
log "🤖 Claude Code Auto-Healing Agent Started"
log "============================================"

# ============================================================================
# Check if suggestions file exists
# ============================================================================
SUGGESTIONS_FILE="$HEALING_DIR/auto_healing_suggestions.txt"

if [ ! -f "$SUGGESTIONS_FILE" ]; then
    log_error "Suggestions file not found: $SUGGESTIONS_FILE"
    log_info "Waiting for GitHub Actions to upload suggestions..."
    exit 0
fi

log "📄 Reading auto-healing suggestions from: $SUGGESTIONS_FILE"
log ""

# ============================================================================
# Parse Suggestions and Execute Healing Commands
# ============================================================================

# Function to execute healing command safely
execute_healing_command() {
    local command="$1"
    local description="$2"

    log_info "Executing: $description"
    log_info "Command: $command"

    # Execute command and capture output
    if eval "$command" >> "$LOG_FILE" 2>&1; then
        log "  ✅ Success: $description"
        return 0
    else
        log_error "  ❌ Failed: $description"
        return 1
    fi
}

# ============================================================================
# Issue Type 1: Zoho Sync Mismatch
# ============================================================================
if grep -q "zoho_sync_mismatch" "$SUGGESTIONS_FILE"; then
    log "🔧 Detected: Zoho Data Sync Mismatch"
    log "Starting healing process..."

    # Check TDS Core worker status
    execute_healing_command \
        "systemctl status tds-core-worker --no-pager" \
        "Check TDS Core worker status"

    # Restart worker if needed
    if ! systemctl is-active --quiet tds-core-worker; then
        log_warning "TDS Core worker is not running - restarting..."
        execute_healing_command \
            "systemctl restart tds-core-worker" \
            "Restart TDS Core worker"
    fi

    # Check sync queue for failed items
    log_info "Checking sync queue for failed items..."
    execute_healing_command \
        "cd $PROJECT_ROOT && python3 -c \"
import psycopg2
conn = psycopg2.connect('postgresql://tsh_admin:TSH@2025Secure!Production@localhost:5432/tsh_erp')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM tds_sync_queue WHERE status=\\'failed\\'')
failed_count = cur.fetchone()[0]
print(f'Failed sync items: {failed_count}')
if failed_count > 0:
    print('Retrying failed sync items...')
    cur.execute('UPDATE tds_sync_queue SET status=\\'pending\\', retry_count=0 WHERE status=\\'failed\\' AND retry_count < 3')
    conn.commit()
    print(f'Marked {cur.rowcount} items for retry')
cur.close()
conn.close()
\"" \
        "Check and retry failed sync items"

    log "✅ Zoho sync mismatch healing completed"
    log ""
fi

# ============================================================================
# Issue Type 2: Sync Timestamp Delay
# ============================================================================
if grep -q "sync_delay" "$SUGGESTIONS_FILE"; then
    log "🔧 Detected: Sync Timestamp Delay"
    log "Starting healing process..."

    # Restart sync worker
    execute_healing_command \
        "systemctl restart tds-core-worker" \
        "Restart TDS Core sync worker"

    # Wait for worker to start
    sleep 5

    # Check worker logs
    execute_healing_command \
        "journalctl -u tds-core-worker -n 50 --no-pager" \
        "Check worker logs for errors"

    # Trigger manual sync for recent changes (last 24 hours)
    if [ -f "$PROJECT_ROOT/scripts/sync_recent.py" ]; then
        log_info "Triggering manual sync for last 24 hours..."
        execute_healing_command \
            "cd $PROJECT_ROOT && python3 scripts/sync_recent.py --hours=24" \
            "Manual sync of recent changes"
    fi

    log "✅ Sync timestamp delay healing completed"
    log ""
fi

# ============================================================================
# Issue Type 3: Webhook Failures
# ============================================================================
if grep -q "webhook_failures" "$SUGGESTIONS_FILE"; then
    log "🔧 Detected: Webhook Failures"
    log "Starting healing process..."

    # Check SSL certificate
    execute_healing_command \
        "curl -v https://erp.tsh.sale 2>&1 | grep -E 'SSL|certificate'" \
        "Check SSL certificate status"

    # Verify Nginx configuration
    execute_healing_command \
        "nginx -t" \
        "Verify Nginx configuration"

    # Check backend service
    execute_healing_command \
        "systemctl status tsh-erp --no-pager" \
        "Check backend service status"

    # Restart backend if needed
    if ! systemctl is-active --quiet tsh-erp; then
        log_warning "Backend service is not running - restarting..."
        execute_healing_command \
            "systemctl restart tsh-erp" \
            "Restart backend service"
    fi

    # Re-register webhooks
    if [ -f "$PROJECT_ROOT/scripts/register_webhooks.py" ]; then
        log_info "Re-registering Zoho webhooks..."
        execute_healing_command \
            "cd $PROJECT_ROOT && python3 scripts/register_webhooks.py" \
            "Re-register Zoho webhooks"
    fi

    # Check firewall status
    execute_healing_command \
        "ufw status" \
        "Check firewall status"

    log "✅ Webhook failures healing completed"
    log ""
fi

# ============================================================================
# Final Health Check
# ============================================================================
log "🏥 Performing final health check..."

# Check all critical services
SERVICES=("tsh-erp" "tsh_erp-green" "tds-core-api" "tds-core-worker" "postgresql" "nginx")

for service in "${SERVICES[@]}"; do
    if systemctl list-units --full -all | grep -q "$service.service"; then
        if systemctl is-active --quiet "$service"; then
            log "  ✅ $service is running"
        else
            log_warning "  ⚠️ $service is not running"
        fi
    fi
done

# Check health endpoints
log_info "Checking health endpoints..."

HEALTH_ENDPOINTS=(
    "http://127.0.0.1:8001/health"
    "http://127.0.0.1:8002/health"
    "https://erp.tsh.sale/health"
)

for endpoint in "${HEALTH_ENDPOINTS[@]}"; do
    if curl -sf "$endpoint" > /dev/null 2>&1; then
        log "  ✅ $endpoint is responding"
    else
        log_warning "  ⚠️ $endpoint is not responding"
    fi
done

# ============================================================================
# Generate Healing Report
# ============================================================================
REPORT_FILE="$HEALING_DIR/healing_report_$(date +%Y%m%d_%H%M%S).txt"

cat > "$REPORT_FILE" <<EOF
============================================
🤖 AUTO-HEALING EXECUTION REPORT
============================================

Execution Time: $(date)
Suggestions File: $SUGGESTIONS_FILE

ACTIONS TAKEN:
$(grep "✅ Success" "$LOG_FILE" | tail -20)

WARNINGS:
$(grep "WARNING" "$LOG_FILE" | tail -10)

ERRORS:
$(grep "ERROR" "$LOG_FILE" | tail -10)

CURRENT SYSTEM STATUS:
--------------------------------------------
$(for service in "${SERVICES[@]}"; do
    if systemctl list-units --full -all | grep -q "$service.service"; then
        status=$(systemctl is-active "$service" 2>/dev/null || echo "inactive")
        echo "  $service: $status"
    fi
done)

HEALTH ENDPOINTS:
--------------------------------------------
$(for endpoint in "${HEALTH_ENDPOINTS[@]}"; do
    if curl -sf "$endpoint" > /dev/null 2>&1; then
        echo "  ✅ $endpoint"
    else
        echo "  ❌ $endpoint"
    fi
done)

============================================
HEALING PROCESS COMPLETED
============================================

Next Steps:
1. Review this report
2. Re-run GitHub Actions staging workflow
3. Monitor system for 15 minutes
4. If issues persist, escalate to manual intervention

Full logs: $LOG_FILE
============================================
EOF

log ""
log "📊 Healing report generated: $REPORT_FILE"
log ""

# ============================================================================
# Send Report Back to GitHub (Optional)
# ============================================================================
if command -v gh &> /dev/null; then
    log_info "Uploading healing report to GitHub..."

    # This would create a comment on the related issue or PR
    # gh issue comment <issue-number> --body-file "$REPORT_FILE"

    log_info "Report upload skipped (configure GitHub CLI if needed)"
fi

# ============================================================================
# Cleanup
# ============================================================================
log "🧹 Cleaning up old healing files..."
find "$HEALING_DIR" -name "healing_report_*.txt" -mtime +7 -delete
find "$HEALING_DIR" -name "auto_healing_suggestions_*.txt" -mtime +7 -delete

log ""
log "============================================"
log "✅ Auto-Healing Process Completed"
log "============================================"
log "📊 Summary report: $REPORT_FILE"
log "📝 Full logs: $LOG_FILE"
log ""

exit 0
