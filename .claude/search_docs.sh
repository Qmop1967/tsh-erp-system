#!/bin/bash
# TSH ERP Documentation Search Script
# Purpose: Quickly search across all .claude/ documentation
# Usage: ./.claude/search_docs.sh "search term"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$SCRIPT_DIR"

# Color codes
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if search term provided
if [ -z "$1" ]; then
    echo "Usage: search_docs.sh <search_term>"
    echo ""
    echo "Examples:"
    echo "  ./search_docs.sh 'Zoho sync'"
    echo "  ./search_docs.sh 'pagination'"
    echo "  ./search_docs.sh 'TDS Core'"
    echo "  ./search_docs.sh 'FastAPI'"
    echo ""
    echo "Searches across all markdown files in .claude/ directory"
    exit 1
fi

echo "🔍 Searching .claude/ documentation for: '$1'"
echo "=============================================="
echo ""

# Search with context (2 lines before and after)
RESULTS=$(grep -rn -C 2 -i "$1" "$CLAUDE_DIR"/*.md 2>/dev/null)

if [ -n "$RESULTS" ]; then
    echo "$RESULTS" | head -50

    # Count total matches
    MATCH_COUNT=$(echo "$RESULTS" | grep -c "^" 2>/dev/null)
    echo ""
    echo "=============================================="
    echo "Found matches in documentation"
    if [ "$MATCH_COUNT" -gt 50 ]; then
        echo -e "${YELLOW}Note: Showing first 50 lines. Total results may be more.${NC}"
    fi
else
    echo "❌ No matches found for: '$1'"
    echo ""
    echo "Tips:"
    echo "  • Try different keywords"
    echo "  • Check spelling"
    echo "  • Try broader search terms"
    echo "  • Search is case-insensitive"
fi
echo ""

# Suggest related files based on search term
echo "📚 Suggested documentation files:"
case "$1" in
    *zoho*|*sync*|*tds*)
        echo "  → ZOHO_SYNC_RULES.md"
        echo "  → PROJECT_VISION.md (Zoho Migration section)"
        ;;
    *deploy*|*staging*|*production*)
        echo "  → COMPLETE_PROJECT_DEPLOYMENT_RULES.md"
        echo "  → STAGING_TO_PRODUCTION_WORKFLOW.md"
        echo "  → DEPLOYMENT_RULES.md"
        ;;
    *code*|*template*|*example*)
        echo "  → CODE_TEMPLATES.md"
        echo "  → ARCHITECTURE_RULES.md"
        ;;
    *task*|*workflow*)
        echo "  → TASK_PATTERNS.md"
        echo "  → SESSION_CHECKLIST.md"
        ;;
    *error*|*fail*|*emergency*)
        echo "  → FAILSAFE_PROTOCOL.md"
        echo "  → CONSUMER_APP_TROUBLESHOOTING.md"
        ;;
    *performance*|*optimize*|*slow*)
        echo "  → PERFORMANCE_OPTIMIZATION.md"
        echo "  → ARCHITECTURE_RULES.md"
        ;;
    *arabic*|*rtl*)
        echo "  → ARCHITECTURE_RULES.md (Arabic RTL section)"
        echo "  → CODE_TEMPLATES.md (Bilingual patterns)"
        ;;
    *)
        echo "  → KNOWLEDGE_PORTAL.md (full documentation index)"
        echo "  → QUICK_REFERENCE.md (quick facts)"
        ;;
esac
echo ""
