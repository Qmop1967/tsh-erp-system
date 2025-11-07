#!/usr/bin/env bash
set -euo pipefail

# Tiny wrapper to SSH into the VPS using the configured alias (defaults to tsh-vps)

HOST_ALIAS="${HOST_ALIAS:-tsh-vps}"

exec ssh "$HOST_ALIAS" "$@"



