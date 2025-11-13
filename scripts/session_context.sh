#!/bin/bash
# Session Context Helper for TSH ERP
# Purpose: Show recent work context for faster session recovery
# Usage: ./scripts/session_context.sh

echo "📋 TSH ERP Session Context"
echo "=========================="
echo ""

# Navigate to project root
cd "$(dirname "$0")/.." || exit 1

# Current branch
echo "🌿 Current Branch:"
BRANCH=$(git branch --show-current 2>/dev/null)
if [ -n "$BRANCH" ]; then
    echo "  $BRANCH"
else
    echo "  (Not a git repository)"
fi
echo ""

# Recent commits (last 5)
echo "📝 Recent Commits:"
git log --oneline --graph --decorate -5 2>/dev/null || echo "  (No git history available)"
echo ""

# Uncommitted changes
echo "🔄 Working Directory Status:"
STATUS=$(git status -s 2>/dev/null)
if [ -n "$STATUS" ]; then
    echo "$STATUS"
else
    echo "  ✓ Working directory clean"
fi
echo ""

# Recent deployments (GitHub Actions)
echo "🚀 Recent Deployments:"
if command -v gh &> /dev/null; then
    gh run list --limit 3 2>/dev/null || echo "  (GitHub CLI authentication required)"
else
    echo "  (GitHub CLI not installed)"
fi
echo ""

# Environment check
echo "🌍 Environment URLs:"
echo "  Staging:    https://staging.erp.tsh.sale"
echo "  Production: https://erp.tsh.sale"
echo "  Consumer:   https://consumer.tsh.sale"
echo "  TDS:        https://tds.tsh.sale"
echo ""

# Database status (if accessible)
echo "💾 Database Quick Check:"
DB_COUNT=$(PGPASSWORD='TSH@2025Secure!Production' psql -h localhost -U tsh_app_user -d tsh_erp_production -t -c "SELECT COUNT(*) FROM products WHERE is_active = true;" 2>/dev/null | xargs)
if [ -n "$DB_COUNT" ]; then
    echo "  ✓ Active Products: $DB_COUNT"
else
    echo "  ⚠ Database not accessible from this machine"
fi
echo ""

# Project scale reminder
echo "📊 Project Scale (Reminder):"
echo "  • 500+ wholesale clients"
echo "  • 2,218+ active products"
echo "  • 30+ daily orders"
echo "  • Phase: Zoho Migration Phase 1 (read-only)"
echo ""

echo "✅ Context loaded. Ready to work!"
