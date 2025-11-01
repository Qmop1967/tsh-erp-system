#!/usr/bin/env bash
################################################################################
# Nginx Upstream Switcher
# Usage: /opt/tsh_erp/bin/switch_upstream.sh [blue|green]
################################################################################

set -euo pipefail

TARGET="${1:-}"

if [[ -z "$TARGET" ]] || [[ ! "$TARGET" =~ ^(blue|green)$ ]]; then
    echo "Usage: $0 [blue|green]"
    exit 1
fi

ACTIVE_LINK="/etc/nginx/upstreams/tsh_erp_active.conf"
TARGET_CONF="/etc/nginx/upstreams/tsh_erp_${TARGET}.conf"

if [[ ! -f "$TARGET_CONF" ]]; then
    echo "❌ Target configuration not found: $TARGET_CONF"
    exit 1
fi

echo "Switching Nginx upstream to: $TARGET"

# Update symlink
sudo ln -sfn "$TARGET_CONF" "$ACTIVE_LINK"

# Test configuration
if ! sudo nginx -t; then
    echo "❌ Nginx configuration test failed!"
    exit 1
fi

# Reload Nginx
sudo systemctl reload nginx

echo "✓ Nginx successfully switched to $TARGET"
exit 0
