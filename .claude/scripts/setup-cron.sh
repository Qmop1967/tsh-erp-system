#!/bin/bash
#
# Setup Cron Job - TSH ERP Ecosystem
# Sets up weekly automated state updates
#
# Usage: ./setup-cron.sh [--install|--remove|--list]
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get absolute path to project
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
UPDATE_SCRIPT="$PROJECT_DIR/.claude/scripts/update-state.sh"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/state-update-cron.log"

# Helper functions
log_info() {
  echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
  echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
  echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
  echo -e "${RED}✗${NC} $1"
}

# Cron job definition
# Runs every Monday at 9 AM
CRON_SCHEDULE="0 9 * * 1"
CRON_COMMAND="cd $PROJECT_DIR && $UPDATE_SCRIPT >> $LOG_FILE 2>&1"
CRON_ENTRY="$CRON_SCHEDULE $CRON_COMMAND"
CRON_MARKER="# TSH ERP State Update"

# Functions
show_usage() {
  cat << EOF
Usage: $0 [COMMAND]

Commands:
  install    Install the cron job (default)
  remove     Remove the cron job
  list       List current cron jobs
  test       Test the update script
  help       Show this help message

Examples:
  $0 install       # Install weekly state updates
  $0 remove        # Remove the cron job
  $0 list          # Show all cron jobs
  $0 test          # Test update script

The cron job will run every Monday at 9 AM.
EOF
}

install_cron() {
  log_info "Installing cron job for weekly state updates..."
  echo ""

  # Check if script exists
  if [ ! -f "$UPDATE_SCRIPT" ]; then
    log_error "Update script not found: $UPDATE_SCRIPT"
    exit 1
  fi

  # Create log directory
  mkdir -p "$LOG_DIR"

  # Check if cron job already exists
  if crontab -l 2>/dev/null | grep -q "$CRON_MARKER"; then
    log_warning "Cron job already installed"
    echo ""
    log_info "To reinstall, first remove the existing job:"
    echo "  $0 remove"
    exit 1
  fi

  # Backup existing crontab
  if crontab -l > /dev/null 2>&1; then
    crontab -l > "${HOME}/.crontab.backup.$(date +%Y%m%d_%H%M%S)"
    log_success "Backed up existing crontab"
  fi

  # Add new cron job
  (
    crontab -l 2>/dev/null || true
    echo ""
    echo "$CRON_MARKER"
    echo "$CRON_ENTRY"
  ) | crontab -

  log_success "Cron job installed successfully!"
  echo ""
  log_info "Cron Schedule:"
  echo "  Schedule: Every Monday at 9:00 AM"
  echo "  Command: $UPDATE_SCRIPT"
  echo "  Log File: $LOG_FILE"
  echo ""
  log_info "To view logs:"
  echo "  tail -f $LOG_FILE"
  echo ""
  log_info "To list all cron jobs:"
  echo "  $0 list"
}

remove_cron() {
  log_info "Removing cron job..."
  echo ""

  # Check if cron job exists
  if ! crontab -l 2>/dev/null | grep -q "$CRON_MARKER"; then
    log_warning "Cron job not found"
    exit 0
  fi

  # Backup existing crontab
  crontab -l > "${HOME}/.crontab.backup.$(date +%Y%m%d_%H%M%S)"
  log_success "Backed up existing crontab"

  # Remove cron job
  crontab -l 2>/dev/null | grep -v "$CRON_MARKER" | grep -v "$UPDATE_SCRIPT" | crontab -

  log_success "Cron job removed successfully!"
}

list_cron() {
  log_info "Current cron jobs:"
  echo ""

  if crontab -l > /dev/null 2>&1; then
    crontab -l | while IFS= read -r line; do
      if echo "$line" | grep -q "$CRON_MARKER"; then
        echo -e "  ${GREEN}► $line${NC} (TSH ERP)"
      elif [ -n "$line" ] && ! echo "$line" | grep -q "^#"; then
        echo -e "  • $line"
      elif echo "$line" | grep -q "^#"; then
        echo -e "  ${BLUE}$line${NC}"
      fi
    done
  else
    log_warning "No cron jobs found"
  fi

  echo ""

  # Check if TSH ERP cron is installed
  if crontab -l 2>/dev/null | grep -q "$CRON_MARKER"; then
    log_success "TSH ERP cron job is installed"
    echo ""
    log_info "Log file: $LOG_FILE"
  else
    log_warning "TSH ERP cron job not installed"
    echo ""
    log_info "To install:"
    echo "  $0 install"
  fi
}

test_update() {
  log_info "Testing update script..."
  echo ""

  if [ ! -f "$UPDATE_SCRIPT" ]; then
    log_error "Update script not found: $UPDATE_SCRIPT"
    exit 1
  fi

  log_info "Running: $UPDATE_SCRIPT --dry-run"
  echo ""

  # Note: This may hang on macOS if database isn't accessible
  # Using a timeout would require gtimeout (brew install coreutils)
  if command -v gtimeout > /dev/null 2>&1; then
    gtimeout 30 "$UPDATE_SCRIPT" --dry-run || {
      log_warning "Script timed out (this is expected if database isn't accessible)"
    }
  else
    log_warning "gtimeout not found - running without timeout"
    log_info "Press Ctrl+C if script hangs"
    echo ""
    "$UPDATE_SCRIPT" --dry-run || {
      log_warning "Script failed (this may be expected if database isn't accessible)"
    }
  fi
}

# Main
ACTION="${1:-install}"

case "$ACTION" in
  install)
    install_cron
    ;;
  remove)
    remove_cron
    ;;
  list)
    list_cron
    ;;
  test)
    test_update
    ;;
  help|--help|-h)
    show_usage
    ;;
  *)
    log_error "Unknown command: $ACTION"
    echo ""
    show_usage
    exit 1
    ;;
esac
