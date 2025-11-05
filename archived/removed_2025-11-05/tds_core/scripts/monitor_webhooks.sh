#!/bin/bash
# Webhook Health Monitoring Script
# Run this via cron every 5 minutes to monitor webhook health
# Example cron: */5 * * * * /opt/tds_core/scripts/monitor_webhooks.sh

set -e

# Configuration
API_URL="${TDS_API_URL:-http://localhost:8001}"
ALERT_THRESHOLD=70  # Alert if health score below 70
LOG_FILE="/var/log/tds-core/webhook-monitor.log"
ALERT_EMAIL="${ALERT_EMAIL:-admin@tsh.sale}"

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Timestamp function
timestamp() {
    date "+%Y-%m-%d %H:%M:%S"
}

# Log function
log() {
    echo "[$(timestamp)] $1" | tee -a "$LOG_FILE"
}

# Check webhook health
log "🔍 Checking webhook health..."

# Fetch health metrics
HEALTH_RESPONSE=$(curl -s "${API_URL}/webhooks/health?hours=1" || echo '{"success": false}')
SUCCESS=$(echo "$HEALTH_RESPONSE" | jq -r '.success // false')

if [ "$SUCCESS" != "true" ]; then
    log "${RED}❌ Failed to fetch webhook health metrics${NC}"
    exit 1
fi

# Extract metrics
HEALTH_SCORE=$(echo "$HEALTH_RESPONSE" | jq -r '.metrics.health_score')
STATUS=$(echo "$HEALTH_RESPONSE" | jq -r '.metrics.status')
DUPLICATE_RATE=$(echo "$HEALTH_RESPONSE" | jq -r '.metrics.inbox_stats.duplicate_rate')
SUCCESS_RATE=$(echo "$HEALTH_RESPONSE" | jq -r '.metrics.processing_stats.success_rate')
ISSUES_COUNT=$(echo "$HEALTH_RESPONSE" | jq -r '.metrics.issues | length')

log "📊 Health Score: ${HEALTH_SCORE}/100 (${STATUS})"
log "📈 Success Rate: ${SUCCESS_RATE}%"
log "🔄 Duplicate Rate: ${DUPLICATE_RATE}%"
log "⚠️  Issues Found: ${ISSUES_COUNT}"

# Check if health score is below threshold
if (( $(echo "$HEALTH_SCORE < $ALERT_THRESHOLD" | bc -l) )); then
    log "${RED}🚨 ALERT: Webhook health score is below threshold!${NC}"

    # Get detailed issues
    ISSUES=$(echo "$HEALTH_RESPONSE" | jq -r '.metrics.issues[] | "- [\(.severity)] \(.message)"')
    RECOMMENDATIONS=$(echo "$HEALTH_RESPONSE" | jq -r '.metrics.recommendations[] | "  • \(.)"')

    # Create alert message
    ALERT_MSG="Webhook Health Alert\n\n"
    ALERT_MSG+="Health Score: ${HEALTH_SCORE}/100 (${STATUS})\n"
    ALERT_MSG+="Success Rate: ${SUCCESS_RATE}%\n"
    ALERT_MSG+="Duplicate Rate: ${DUPLICATE_RATE}%\n\n"
    ALERT_MSG+="Issues:\n${ISSUES}\n\n"
    ALERT_MSG+="Recommendations:\n${RECOMMENDATIONS}\n\n"
    ALERT_MSG+="Check details at: ${API_URL}/webhooks/health"

    log "$ALERT_MSG"

    # Send alert email (if mail is configured)
    if command -v mail &> /dev/null; then
        echo -e "$ALERT_MSG" | mail -s "🚨 TDS Core Webhook Health Alert" "$ALERT_EMAIL"
        log "📧 Alert email sent to ${ALERT_EMAIL}"
    fi

    exit 2
else
    log "${GREEN}✅ Webhook health is good${NC}"
fi

# Check for excessive duplicates
if (( $(echo "$DUPLICATE_RATE > 10" | bc -l) )); then
    log "${YELLOW}⚠️  Warning: High duplicate webhook rate (${DUPLICATE_RATE}%)${NC}"

    # Get duplicate analysis
    DUPLICATE_RESPONSE=$(curl -s "${API_URL}/webhooks/duplicates?hours=1")
    DUPLICATE_GROUPS=$(echo "$DUPLICATE_RESPONSE" | jq -r '.analysis.duplicate_event_groups')

    log "📊 Duplicate event groups: ${DUPLICATE_GROUPS}"

    # Log top 5 most retried events
    TOP_RETRIED=$(echo "$DUPLICATE_RESPONSE" | jq -r '.analysis.events[:5][] | "  - \(.entity_type) \(.entity_id): \(.retry_count) retries"')
    log "Top retried events:\n${TOP_RETRIED}"
fi

log "✅ Monitoring check complete"
exit 0
