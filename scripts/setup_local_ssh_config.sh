#!/usr/bin/env bash
set -euo pipefail

# Minimal helper to append/update an SSH config entry for the TSH VPS.
# Safe to run multiple times. Requires: bash, sed, mkdir.

VPS_HOSTNAME_DEFAULT="167.71.39.50"
VPS_USER_DEFAULT="root"
VPS_PORT_DEFAULT="22"
SSH_KEY_PATH_DEFAULT="$HOME/.ssh/tsh_vps"

VPS_HOSTNAME="${VPS_HOSTNAME:-$VPS_HOSTNAME_DEFAULT}"
VPS_USER="${VPS_USER:-$VPS_USER_DEFAULT}"
VPS_PORT="${VPS_PORT:-$VPS_PORT_DEFAULT}"
SSH_KEY_PATH="${SSH_KEY_PATH:-$SSH_KEY_PATH_DEFAULT}"
HOST_ALIAS="${HOST_ALIAS:-tsh-vps}"

CONFIG_DIR="$HOME/.ssh"
CONFIG_FILE="$CONFIG_DIR/config"

mkdir -p "$CONFIG_DIR"
touch "$CONFIG_FILE"
chmod 700 "$CONFIG_DIR"
chmod 600 "$CONFIG_FILE"

# Remove any existing block we previously added for this alias
tmp_file="$(mktemp)"
awk -v alias="$HOST_ALIAS" '
  BEGIN {skip=0}
  /^# BEGIN TSH SSH CONFIG for alias/ { if ($0 ~ alias) { skip=1; next } }
  /^# END TSH SSH CONFIG for alias/ { if ($0 ~ alias) { skip=0; next } }
  skip==0 { print }
' "$CONFIG_FILE" > "$tmp_file"
mv "$tmp_file" "$CONFIG_FILE"

cat >> "$CONFIG_FILE" <<EOF
# BEGIN TSH SSH CONFIG for alias: $HOST_ALIAS
Host $HOST_ALIAS
    HostName $VPS_HOSTNAME
    User $VPS_USER
    Port $VPS_PORT
    IdentitiesOnly yes
    IdentityFile $SSH_KEY_PATH
    StrictHostKeyChecking accept-new
    ServerAliveInterval 30
    ServerAliveCountMax 4
# END TSH SSH CONFIG for alias: $HOST_ALIAS
EOF

echo "Added/updated SSH config for host alias '$HOST_ALIAS' -> $VPS_USER@$VPS_HOSTNAME:$VPS_PORT using key $SSH_KEY_PATH"
echo "Test: ssh $HOST_ALIAS 'echo connected'"



