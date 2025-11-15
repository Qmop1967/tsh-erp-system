#!/bin/bash
# TSH ERP - Git Worktree Cleanup Script
# Version: 1.0.0
# Usage: ./scripts/cleanup-worktrees.sh [--all] [--force]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Parse flags
REMOVE_ALL=false
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            REMOVE_ALL=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Usage: ./scripts/cleanup-worktrees.sh [--all] [--force]"
            echo ""
            echo "Options:"
            echo "  --all    Remove all worktrees except main repository"
            echo "  --force  Skip confirmation prompts"
            exit 1
            ;;
    esac
done

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  TSH ERP - Worktree Cleanup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Get list of worktrees (excluding main repository)
WORKTREES=$(git worktree list --porcelain | grep "^worktree " | cut -d' ' -f2 | grep -v "$(pwd)")

if [ -z "$WORKTREES" ]; then
    echo -e "${GREEN}✅ No worktrees to clean up${NC}"
    echo ""
    exit 0
fi

# Display current worktrees
echo -e "${YELLOW}Current Worktrees:${NC}"
git worktree list
echo ""

if [ "$REMOVE_ALL" = true ]; then
    if [ "$FORCE" = false ]; then
        echo -e "${RED}WARNING: This will remove ALL worktrees!${NC}"
        echo ""
        echo "Worktrees to be removed:"
        echo "$WORKTREES"
        echo ""
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" != "yes" ]; then
            echo "Cancelled."
            exit 0
        fi
    fi

    echo ""
    echo -e "${YELLOW}Removing all worktrees...${NC}"
    while IFS= read -r worktree; do
        echo "  Removing: $worktree"
        git worktree remove "$worktree" --force || echo -e "${RED}  Failed to remove: $worktree${NC}"
    done <<< "$WORKTREES"
else
    # Interactive mode - ask for each worktree
    echo "Select worktrees to remove (or 'all' to remove all, 'quit' to exit):"
    echo ""

    COUNTER=1
    declare -a WORKTREE_ARRAY
    while IFS= read -r worktree; do
        WORKTREE_ARRAY[$COUNTER]="$worktree"
        BRANCH=$(git worktree list --porcelain | grep -A2 "^worktree $worktree" | grep "^branch " | cut -d' ' -f2 | sed 's/refs\/heads\///')
        echo "  [$COUNTER] $worktree"
        echo "      Branch: $BRANCH"
        COUNTER=$((COUNTER + 1))
    done <<< "$WORKTREES"

    echo ""
    read -p "Enter numbers to remove (space-separated), 'all', or 'quit': " selection

    if [ "$selection" = "quit" ]; then
        echo "Cancelled."
        exit 0
    fi

    if [ "$selection" = "all" ]; then
        echo ""
        echo -e "${YELLOW}Removing all worktrees...${NC}"
        while IFS= read -r worktree; do
            echo "  Removing: $worktree"
            git worktree remove "$worktree" --force || echo -e "${RED}  Failed to remove: $worktree${NC}"
        done <<< "$WORKTREES"
    else
        echo ""
        echo -e "${YELLOW}Removing selected worktrees...${NC}"
        for num in $selection; do
            if [ -n "${WORKTREE_ARRAY[$num]}" ]; then
                echo "  Removing: ${WORKTREE_ARRAY[$num]}"
                git worktree remove "${WORKTREE_ARRAY[$num]}" --force || echo -e "${RED}  Failed to remove: ${WORKTREE_ARRAY[$num]}${NC}"
            else
                echo -e "${RED}  Invalid selection: $num${NC}"
            fi
        done
    fi
fi

# Prune stale worktree metadata
echo ""
echo -e "${YELLOW}Pruning stale worktree metadata...${NC}"
git worktree prune

echo ""
echo -e "${GREEN}✅ Cleanup complete!${NC}"
echo ""
echo -e "${YELLOW}Remaining Worktrees:${NC}"
git worktree list
echo ""
