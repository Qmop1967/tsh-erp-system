# Reference Documentation (Lazy Loading)

**Purpose:** Detailed documentation loaded on-demand using @docs/ prefix
**Last Updated:** 2025-11-14

## Lazy Loading Strategy

Instead of loading all documentation at session start, reference materials are loaded only when needed using the `@docs/` prefix.

## Usage Pattern

```markdown
# In CLAUDE.md or core files:
For detailed code templates, see @docs/reference/code-templates/

# When needed, Claude will read:
Read /Users/khaleelal-mulla/TSH_ERP_Ecosystem/.claude/reference/code-templates/...
```

## Directory Structure

```
reference/
├── code-templates/          # Reusable code patterns
│   ├── auth.md             # Authentication patterns
│   ├── crud.md             # CRUD operation templates
│   ├── zoho-sync.md        # TDS Core/Zoho patterns
│   └── mobile-api.md       # Mobile API patterns
│
├── reasoning-patterns.md    # Problem-solving frameworks
├── performance-guide.md     # Optimization techniques
└── security-guide.md        # Security best practices
```

## Benefits

1. **Faster Session Init** - Only load what's needed
2. **Reduced Context** - Save tokens for actual work
3. **Better Caching** - Stable core context, dynamic references
4. **Selective Access** - Load only relevant documentation

## Migration Status

Files to be moved here:
- [ ] CODE_TEMPLATES.md → code-templates/*.md (split by category)
- [ ] REASONING_PATTERNS.md → reasoning-patterns.md (keep as-is)
- [ ] PERFORMANCE_OPTIMIZATION.md → performance-guide.md
- [ ] Detailed deployment guides → deployment/

## When to Use

**Use reference/ for:**
- Detailed code examples
- Comprehensive guides (>500 lines)
- Specialized knowledge (used occasionally)
- Historical documentation
- Advanced patterns

**Keep in core/ for:**
- Essential business context
- Critical technical rules
- Common workflows
- Frequently used patterns
