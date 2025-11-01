#!/usr/bin/env bash
################################################################################
# Health Check Script
# Usage: /opt/tsh_erp/bin/healthcheck.sh [url] [timeout_seconds]
################################################################################

set -euo pipefail

URL="${1:-http://127.0.0.1:8001/ready}"
TIMEOUT="${2:-30}"

echo "Checking health: $URL (timeout: ${TIMEOUT}s)"

for i in $(seq 1 "$TIMEOUT"); do
    if curl -fsS --max-time 5 "$URL" >/dev/null 2>&1; then
        echo "✓ Health check PASSED (${i}s)"
        exit 0
    fi
    echo "  Attempt $i/$TIMEOUT..."
    sleep 1
done

echo "❌ Health check FAILED after ${TIMEOUT}s"
exit 1
