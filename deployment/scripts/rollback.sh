#!/usr/bin/env bash
################################################################################
# Rollback Script - Switch back to previous deployment
# Usage: /opt/tsh_erp/bin/rollback.sh
################################################################################

set -euo pipefail

echo "=========================================="
echo "TSH ERP ROLLBACK Started"
echo "Time: $(date)"
echo "=========================================="

# 1) Determine current active
ACTIVE_CONF=$(readlink -f /etc/nginx/upstreams/tsh_erp_active.conf 2>/dev/null || echo "")

if [[ "$ACTIVE_CONF" =~ "tsh_erp_blue.conf" ]]; then
    CURRENT="blue"
    TARGET="green"
    TARGET_PORT=8002
    TARGET_SERVICE="tsh_erp-green.service"
    CURRENT_SERVICE="tsh_erp-blue.service"
else
    CURRENT="green"
    TARGET="blue"
    TARGET_PORT=8001
    TARGET_SERVICE="tsh_erp-blue.service"
    CURRENT_SERVICE="tsh_erp-green.service"
fi

echo "Current: $CURRENT"
echo "Rolling back to: $TARGET"

# 2) Start target service (should still have previous release)
echo "[1/4] Starting $TARGET service..."
sudo systemctl start "$TARGET_SERVICE"
sleep 3
echo "✓ Service started"

# 3) Health check
echo "[2/4] Running health check..."
/opt/tsh_erp/bin/healthcheck.sh "http://127.0.0.1:${TARGET_PORT}/ready" 30 || {
    echo "❌ Health check failed on $TARGET!"
    echo "Cannot rollback. Check logs: journalctl -u $TARGET_SERVICE"
    exit 1
}
echo "✓ Health check passed"

# 4) Switch Nginx
echo "[3/4] Switching Nginx to $TARGET..."
/opt/tsh_erp/bin/switch_upstream.sh "$TARGET"
echo "✓ Traffic switched"

# 5) Stop current service
echo "[4/4] Stopping $CURRENT service..."
sudo systemctl stop "$CURRENT_SERVICE"
echo "✓ Old service stopped"

echo "=========================================="
echo "✅ Rollback Complete!"
echo "Active: $TARGET (was: $CURRENT)"
echo "Time: $(date)"
echo "=========================================="

# Optional: Send notification
# curl -X POST https://hooks.slack.com/YOUR_WEBHOOK \
#     -H 'Content-Type: application/json' \
#     -d "{\"text\":\"⚠️ TSH ERP rolled back to $TARGET\"}"

exit 0
