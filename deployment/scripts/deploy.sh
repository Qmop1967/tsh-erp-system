#!/usr/bin/env bash
################################################################################
# TSH ERP - Zero-Downtime Blue/Green Deployment Script
# Usage: /opt/tsh_erp/bin/deploy.sh [branch]
################################################################################

set -euo pipefail

# Configuration
REPO="https://github.com/Qmop1967/tsh-erp-system.git"
APP_DIR="/opt/tsh_erp"
RELEASES_DIR="$APP_DIR/releases"
VENVS_DIR="$APP_DIR/venvs"
SHARED_DIR="$APP_DIR/shared"
LOGS_DIR="$SHARED_DIR/logs/api"
BRANCH="${1:-main}"
PYTHON_VERSION="python3"

# Create timestamped log file
TIMESTAMP=$(date +%F_%H-%M-%S)
LOG_FILE="$LOGS_DIR/deploy_$TIMESTAMP.log"
mkdir -p "$LOGS_DIR"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "=========================================="
echo "TSH ERP Deployment Started"
echo "Time: $(date)"
echo "Branch: $BRANCH"
echo "=========================================="

# 1) Determine active and idle colors
################################################################################
echo "[1/12] Determining active deployment color..."
ACTIVE_CONF=$(readlink -f /etc/nginx/upstreams/tsh_erp_active.conf 2>/dev/null || echo "")

if [[ "$ACTIVE_CONF" =~ "tsh_erp_blue.conf" ]]; then
    ACTIVE_COLOR="blue"
    IDLE_COLOR="green"
    IDLE_PORT=8002
    IDLE_SERVICE="tsh_erp-green.service"
    ACTIVE_SERVICE="tsh_erp-blue.service"
else
    ACTIVE_COLOR="green"
    IDLE_COLOR="blue"
    IDLE_PORT=8001
    IDLE_SERVICE="tsh_erp-blue.service"
    ACTIVE_SERVICE="tsh_erp-green.service"
fi

IDLE_DIR="$RELEASES_DIR/$IDLE_COLOR"
IDLE_VENV="$VENVS_DIR/$IDLE_COLOR"

echo "✓ Active: $ACTIVE_COLOR | Deploying to: $IDLE_COLOR (port $IDLE_PORT)"

# 2) Stop idle service if running
################################################################################
echo "[2/12] Stopping idle service ($IDLE_SERVICE)..."
sudo systemctl stop "$IDLE_SERVICE" 2>/dev/null || true
echo "✓ Idle service stopped"

# 3) Sync code to idle release directory
################################################################################
echo "[3/12] Syncing code from GitHub..."
sudo rm -rf "$IDLE_DIR"
mkdir -p "$IDLE_DIR"

TMP_DIR=$(mktemp -d)
trap "rm -rf $TMP_DIR" EXIT

git clone --depth 1 --branch "$BRANCH" "$REPO" "$TMP_DIR"
rsync -a --delete \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='node_modules' \
    "$TMP_DIR/" "$IDLE_DIR/"

echo "✓ Code synced to $IDLE_DIR"

# 4) Create/update virtual environment
################################################################################
echo "[4/12] Setting up Python virtual environment..."
if [[ ! -d "$IDLE_VENV" ]]; then
    $PYTHON_VERSION -m venv "$IDLE_VENV"
fi

source "$IDLE_VENV/bin/activate"
pip install --upgrade pip setuptools wheel
pip install -r "$IDLE_DIR/requirements.txt"
echo "✓ Virtual environment ready"

# 5) Database backup (before any migrations)
################################################################################
echo "[5/12] Backing up production database..."
source "$SHARED_DIR/env/prod.env"
BACKUP_DIR="/opt/backups"
mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/tsh_erp_prod_${TIMESTAMP}.dump"

pg_dump --file="$BACKUP_FILE" --format=custom "$DATABASE_URL" || {
    echo "❌ Database backup failed!"
    exit 1
}
echo "✓ Database backed up to $BACKUP_FILE"

# 6) Test migrations on staging database
################################################################################
echo "[6/12] Testing migrations on staging database..."
if [[ -f "$SHARED_DIR/env/staging.env" ]]; then
    source "$SHARED_DIR/env/staging.env"
    cd "$IDLE_DIR"

    if [[ -d "alembic" && -f "alembic.ini" ]]; then
        alembic upgrade head || {
            echo "❌ Staging migration failed! Aborting deployment."
            exit 1
        }
        echo "✓ Staging migrations successful"
    else
        echo "⚠ No Alembic configuration found, skipping migration test"
    fi
fi

# 7) Start idle service
################################################################################
echo "[7/12] Starting idle service ($IDLE_SERVICE)..."
sudo systemctl start "$IDLE_SERVICE"
sleep 3
echo "✓ Idle service started"

# 8) Health check on idle instance
################################################################################
echo "[8/12] Running health checks on idle instance..."
HEALTH_URL="http://127.0.0.1:${IDLE_PORT}/ready"
MAX_ATTEMPTS=30
ATTEMPT=1

while [[ $ATTEMPT -le $MAX_ATTEMPTS ]]; do
    if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
        echo "✓ Health check passed (attempt $ATTEMPT/$MAX_ATTEMPTS)"
        break
    fi

    if [[ $ATTEMPT -eq $MAX_ATTEMPTS ]]; then
        echo "❌ Health check failed after $MAX_ATTEMPTS attempts!"
        echo "Check logs: journalctl -u $IDLE_SERVICE -n 50"
        sudo systemctl stop "$IDLE_SERVICE"
        exit 1
    fi

    echo "  Waiting for service to be healthy... (attempt $ATTEMPT/$MAX_ATTEMPTS)"
    sleep 2
    ((ATTEMPT++))
done

# 9) Switch Nginx traffic to idle (now becomes active)
################################################################################
echo "[9/12] Switching Nginx traffic to $IDLE_COLOR..."
sudo ln -sfn "/etc/nginx/upstreams/tsh_erp_${IDLE_COLOR}.conf" \
    /etc/nginx/upstreams/tsh_erp_active.conf

sudo nginx -t || {
    echo "❌ Nginx configuration test failed!"
    exit 1
}

sudo systemctl reload nginx
echo "✓ Traffic switched to $IDLE_COLOR"

# 10) Run production database migrations
################################################################################
echo "[10/12] Running production database migrations..."
source "$SHARED_DIR/env/prod.env"
cd "$IDLE_DIR"

if [[ -d "alembic" && -f "alembic.ini" ]]; then
    alembic upgrade head || {
        echo "❌ Production migration failed!"
        echo "Rolling back..."
        bash /opt/tsh_erp/bin/rollback.sh
        exit 1
    }
    echo "✓ Production migrations complete"
fi

# 11) Stop old active service
################################################################################
echo "[11/12] Stopping old service ($ACTIVE_SERVICE)..."
sudo systemctl stop "$ACTIVE_SERVICE"
echo "✓ Old service stopped"

# 12) Cleanup old logs
################################################################################
echo "[12/12] Cleaning up old deployment logs..."
find "$LOGS_DIR" -name "deploy_*.log" -mtime +30 -delete 2>/dev/null || true
find "$BACKUP_DIR" -name "*.dump" -mtime +7 -delete 2>/dev/null || true
echo "✓ Cleanup complete"

echo "=========================================="
echo "✅ Deployment Complete!"
echo "New active: $IDLE_COLOR"
echo "Previous: $ACTIVE_COLOR"
echo "Time: $(date)"
echo "=========================================="

# Optional: Send notification
# curl -X POST https://hooks.slack.com/YOUR_WEBHOOK \
#     -H 'Content-Type: application/json' \
#     -d "{\"text\":\"🚀 TSH ERP deployed to $IDLE_COLOR successfully\"}"

exit 0
