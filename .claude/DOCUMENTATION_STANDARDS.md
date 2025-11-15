# TSH ERP Documentation Standards

**Version:** 1.0.0
**Last Updated:** 2025-11-15
**Purpose:** Establish consistent documentation practices across the TSH ERP Ecosystem

---

## 🎯 Core Principles

### 1. Clarity Over Cleverness
- Write for the reader, not to impress
- Use simple, direct language
- Explain technical terms when first used
- Avoid jargon unless defined in glossary

### 2. Consistency is Key
- Follow the **DOCUMENTATION_GLOSSARY.md** for all terminology
- Use consistent formatting across all documents
- Maintain uniform structure within document categories
- Apply standard metadata to every file

### 3. Accuracy Above All
- Verify technical details before publishing
- Test code examples before including them
- Update docs when code changes
- Mark deprecated information clearly

### 4. Maintainability Matters
- Keep files focused and scoped
- Use modular documentation (link, don't repeat)
- Include last updated dates
- Version significant changes

---

## 📋 File Structure Standards

### Required Metadata (All Files)

Every documentation file MUST include this metadata block at the top:

```markdown
# Document Title

**Version:** X.Y.Z
**Last Updated:** YYYY-MM-DD
**Status:** [Draft | Active | Deprecated]
**Purpose:** One-sentence description of this document

---
```

**Example:**
```markdown
# API Authentication Guide

**Version:** 2.1.0
**Last Updated:** 2025-11-15
**Status:** Active
**Purpose:** Comprehensive guide to implementing JWT authentication in TSH ERP

---
```

### Version Numbering

Follow semantic versioning for documentation:

**MAJOR.MINOR.PATCH**
- **MAJOR:** Breaking changes (complete rewrites, major restructuring)
- **MINOR:** Significant additions (new sections, new concepts)
- **PATCH:** Minor updates (typo fixes, clarifications, small additions)

**Examples:**
- `1.0.0` → Initial release
- `1.1.0` → Added new section on OAuth
- `1.1.1` → Fixed typos and broken links
- `2.0.0` → Complete rewrite with new structure

### Document Status

- **Draft:** Work in progress, not yet reviewed
- **Active:** Current and accurate documentation
- **Deprecated:** Outdated, kept for historical reference
- **Archived:** No longer relevant, moved to archive

---

## 📝 Writing Style Guide

### Headers and Structure

**Hierarchy:**
```markdown
# Level 1: Document Title (Only ONE per file)

## Level 2: Major Section

### Level 3: Subsection

#### Level 4: Detail (use sparingly)
```

**Emoji Usage in Headers:**
- **Allowed:** In Level 2 headers for visual organization
- **Recommended emoji:**
  - 🎯 Goals/Objectives
  - 📋 Lists/Checklists
  - 🚨 Critical Information/Warnings
  - ✅ Success/Completion
  - ❌ Errors/Don't Do This
  - 🔒 Security
  - 🌐 Internationalization
  - 📦 Deployment/Infrastructure
  - 🔄 Sync/Integration
  - 💡 Tips/Best Practices

**Not allowed:** Emoji in Level 1 headers, body text (except lists)

### Code Blocks

**Always specify language:**
```markdown
```python
# Good: Language specified
def hello_world():
    print("Hello, World!")
```

```
# Bad: No language
def hello_world():
    print("Hello, World!")
```
```

**Supported languages:**
- `python` - Python code
- `typescript` - TypeScript/JavaScript
- `dart` - Flutter/Dart code
- `bash` - Shell commands
- `sql` - Database queries
- `yaml` - Configuration files
- `json` - JSON data
- `markdown` - Nested markdown

### Lists

**Bulleted Lists:**
```markdown
- Use hyphens for bullets
- Keep items parallel in structure
- Start with capital letter
- End without punctuation (unless multiple sentences)
```

**Numbered Lists:**
```markdown
1. For sequential steps
2. For priority orders
3. For ranked items
```

**Checklists:**
```markdown
- [ ] Pending task
- [x] Completed task
```

### Links

**Internal Links (within project):**
```markdown
See [Architecture Rules](.claude/ARCHITECTURE_RULES.md)
```

**External Links:**
```markdown
See [FastAPI Documentation](https://fastapi.tiangolo.com/)
```

**Anchor Links (same document):**
```markdown
Jump to [Glossary](#glossary)
```

**Best Practices:**
- Use descriptive link text (not "click here")
- Test all links before committing
- Use relative paths for internal links
- Include domain for external links

### Tables

**Format:**
```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |
```

**Alignment:**
```markdown
| Left-aligned | Center-aligned | Right-aligned |
|:-------------|:--------------:|--------------:|
| Data 1       | Data 2         | Data 3        |
```

**Best Practices:**
- Use tables for structured data comparisons
- Keep tables simple (max 5 columns if possible)
- Use headers for every table
- Don't use tables for layout

### Code Examples

**Complete Example:**
```markdown
### User Authentication Example

**Context:** Implementing JWT authentication in FastAPI endpoint

**Code:**
```python
from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.schemas.user import UserResponse

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile.

    Requires valid JWT token in Authorization header.
    """
    return current_user
```

**Usage:**
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     https://erp.tsh.sale/api/v1/users/me
```

**Expected Response:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@tsh.sale",
  "role": "admin"
}
```
```

**Best Practices:**
- Include context before code
- Show complete, runnable examples
- Include expected output when helpful
- Add comments for complex logic
- Test examples before publishing

---

## 🗂️ File Organization

### Directory Structure

```
TSH_ERP_Ecosystem/
├── .claude/                    # AI context and standards
│   ├── core/                   # Core documentation
│   │   ├── engineering-standards.md
│   │   ├── project-context.md
│   │   ├── architecture.md
│   │   └── workflows.md
│   ├── reference/              # Reference materials
│   │   ├── code-templates/
│   │   ├── ai-guidelines/
│   │   └── failsafe/
│   ├── DOCUMENTATION_GLOSSARY.md    # THIS FILE: Terminology standards
│   ├── DOCUMENTATION_STANDARDS.md   # Writing and formatting standards
│   └── DOCUMENTATION_INDEX.md       # Master index of all docs
│
└── docs/                       # Project documentation
    ├── README.md               # Documentation hub
    ├── architecture/           # System design
    ├── deployment/             # Deployment guides
    ├── integrations/           # External integrations
    ├── security/               # Security documentation
    └── status/                 # Project status reports
```

### File Naming Conventions

**Documentation Files (.claude/):**
- Use `UPPERCASE_WITH_UNDERSCORES.md`
- Examples: `PROJECT_VISION.md`, `DEPLOYMENT_GUIDE.md`

**Reference Files (docs/):**
- Use `lowercase-with-hyphens.md` or `Title_Case_With_Underscores.md`
- Examples: `api-reference.md`, `Deployment_Checklist.md`

**README Files:**
- Always `README.md` (all caps)
- Never `readme.md`, `Readme.md`, or `ReadMe.md`

### File Size Guidelines

**Target Sizes:**
- Quick reference: < 500 lines (fits in single screen/cache)
- Guides: 500-1500 lines (single focused topic)
- Comprehensive docs: 1500-3000 lines (multiple related topics)
- Avoid: > 3000 lines (split into multiple files)

**When to Split:**
- Document exceeds 3000 lines
- Multiple distinct topics covered
- Different audiences for different sections
- Frequent updates to specific sections

---

## 🎯 Document Types & Templates

### 1. Architecture Documents

**Purpose:** Explain system design, patterns, and technical decisions

**Required Sections:**
```markdown
# [Component/Pattern Name]

**Version:** X.Y.Z
**Last Updated:** YYYY-MM-DD
**Status:** Active
**Purpose:** Brief description

---

## Overview
High-level description of the component/pattern

## Architecture Diagram
Visual representation (ASCII art or link to image)

## Components
Detailed breakdown of parts

## Data Flow
How information moves through the system

## Implementation
Code examples and patterns

## Constraints
Technical limitations and requirements

## Related Documentation
Links to related docs
```

### 2. API Documentation

**Purpose:** Document REST API endpoints

**Required Sections:**
```markdown
# [API Name]

**Version:** X.Y.Z
**Last Updated:** YYYY-MM-DD
**Status:** Active
**Purpose:** Brief description

---

## Authentication
Required authentication method

## Endpoints

### GET /api/v1/resource
**Description:** What this endpoint does

**Parameters:**
- `param1` (required): Description
- `param2` (optional): Description

**Response:**
```json
{
  "example": "response"
}
```

**Error Codes:**
- `404`: Resource not found
- `401`: Unauthorized

**Example:**
```bash
curl -X GET https://erp.tsh.sale/api/v1/resource
```
```

### 3. Deployment Guides

**Purpose:** Step-by-step deployment procedures

**Required Sections:**
```markdown
# [Deployment Type]

**Version:** X.Y.Z
**Last Updated:** YYYY-MM-DD
**Status:** Active
**Purpose:** Brief description

---

## Prerequisites
- [ ] Requirement 1
- [ ] Requirement 2

## Environment Setup
Configuration needed

## Deployment Steps
1. Step one
2. Step two
3. Step three

## Verification
How to confirm deployment succeeded

## Rollback Procedure
How to revert if deployment fails

## Troubleshooting
Common issues and solutions
```

### 4. Troubleshooting Guides

**Purpose:** Diagnose and fix common issues

**Required Sections:**
```markdown
# [Issue/Component] Troubleshooting

**Version:** X.Y.Z
**Last Updated:** YYYY-MM-DD
**Status:** Active
**Purpose:** Brief description

---

## Symptoms
How to recognize this issue

## Root Causes
Why this happens

## Diagnosis Steps
1. Check X
2. Verify Y
3. Inspect Z

## Solutions

### Solution 1: [Quick Fix]
For minor cases

### Solution 2: [Complete Fix]
For recurring issues

## Prevention
How to avoid this issue

## Related Issues
Links to similar problems
```

### 5. Feature Documentation

**Purpose:** Explain features and usage

**Required Sections:**
```markdown
# [Feature Name]

**Version:** X.Y.Z
**Last Updated:** YYYY-MM-DD
**Status:** Active
**Purpose:** Brief description

---

## Overview
What this feature does

## Use Cases
When to use this feature

## Setup/Configuration
How to enable

## Usage
Step-by-step instructions with examples

## Best Practices
Recommended patterns

## Limitations
What this feature doesn't do

## Related Features
Links to complementary features
```

---

## ✅ Quality Checklist

Before publishing ANY documentation, verify:

### Content Quality
- [ ] Information is accurate and tested
- [ ] Technical details are verified
- [ ] Code examples are complete and runnable
- [ ] Links are valid and working
- [ ] References are up-to-date

### Formatting
- [ ] Metadata block at top (version, date, status, purpose)
- [ ] Headers follow hierarchy (# → ## → ###)
- [ ] Code blocks specify language
- [ ] Lists use consistent formatting
- [ ] Tables are properly formatted

### Terminology
- [ ] Uses preferred terms from DOCUMENTATION_GLOSSARY.md
- [ ] Technical terms defined on first use
- [ ] Consistent capitalization
- [ ] Consistent product names

### Structure
- [ ] Clear table of contents (if >500 lines)
- [ ] Logical section organization
- [ ] Appropriate document length
- [ ] Related docs linked

### Accessibility
- [ ] Clear, simple language
- [ ] Jargon explained
- [ ] Examples provided
- [ ] Diagrams described in text

---

## 🔄 Maintenance Procedures

### Regular Reviews

**Monthly:**
- Check for outdated version numbers
- Verify external links still work
- Update "Last Updated" dates for reviewed docs

**Quarterly:**
- Review for accuracy against current codebase
- Update examples to match current patterns
- Consolidate or split documents as needed

**Annually:**
- Major version bump if significant changes
- Archive truly obsolete documentation
- Reorganize if directory structure is unclear

### Update Triggers

Update documentation immediately when:
- **Code changes:** API contracts, function signatures
- **Architecture changes:** New patterns, deprecated patterns
- **Process changes:** Deployment procedures, workflows
- **Tool changes:** New versions with breaking changes

### Deprecation Process

When deprecating documentation:

1. **Mark as deprecated:**
   ```markdown
   **Status:** Deprecated
   **Deprecated:** 2025-11-15
   **Replacement:** Link to new documentation
   ```

2. **Add deprecation notice at top:**
   ```markdown
   > **⚠️ DEPRECATED:** This document is outdated.
   > See [New Documentation](link) for current information.
   ```

3. **Move to archive after 6 months:**
   - Create `docs/archive/` if needed
   - Move deprecated file
   - Update index to remove entry

---

## 🎓 Best Practices

### Do's

✅ **Write for your future self**
- You'll forget details in 6 months
- Document the "why" not just the "what"

✅ **Use examples liberally**
- Code examples
- Command examples
- Output examples

✅ **Link, don't duplicate**
- Reference existing documentation
- Avoid copy-paste between files

✅ **Keep it updated**
- Fix errors immediately
- Update when code changes
- Mark outdated sections

✅ **Make it scannable**
- Use headers for structure
- Use lists for items
- Use bold for emphasis
- Use code blocks for code

### Don'ts

❌ **Don't assume knowledge**
- Explain technical terms
- Provide context
- Link to prerequisite docs

❌ **Don't use ambiguous terms**
- "Soon" (when?)
- "Recently" (how recent?)
- "Usually" (how often?)
- "Most" (what percentage?)

❌ **Don't hard-code values**
- Use environment variables
- Use configuration references
- Use placeholders (`<your-value-here>`)

❌ **Don't skip metadata**
- Every file needs version, date, status
- Future you will thank you

❌ **Don't create orphan docs**
- Link from index
- Link from related docs
- Make it discoverable

---

## 📚 Additional Resources

### Internal References
- **DOCUMENTATION_GLOSSARY.md** - Terminology standards
- **DOCUMENTATION_INDEX.md** - Master index of all documentation
- **PROJECT_VISION.md** - Business context and goals
- **ARCHITECTURE_RULES.md** - Technical constraints

### External Resources
- [GitHub Flavored Markdown](https://github.github.com/gfm/) - Markdown syntax
- [Semantic Versioning](https://semver.org/) - Version numbering
- [Google Developer Documentation Style Guide](https://developers.google.com/style) - Writing style

---

## 🤝 Contributing to Documentation

### Proposing Changes

1. **Check existing docs first**
   - Search for existing content
   - Avoid duplication

2. **Follow templates**
   - Use appropriate document type template
   - Include all required sections

3. **Get review**
   - Submit PR with docs changes
   - Tag for documentation review

4. **Update index**
   - Add to DOCUMENTATION_INDEX.md
   - Link from related docs

### Review Checklist (for Reviewers)

When reviewing documentation PRs:

- [ ] Metadata complete and correct
- [ ] Terminology matches glossary
- [ ] Code examples tested and working
- [ ] Links valid and correct
- [ ] Formatting consistent
- [ ] Appropriate level of detail
- [ ] Added to documentation index
- [ ] No sensitive information exposed

---

## 📞 Questions or Feedback

**Documentation maintainer:** Khaleel Al-Mulla
**Last reviewed:** 2025-11-15
**Next review:** 2025-12-15

**To provide feedback:**
1. Create GitHub issue with `documentation` label
2. Propose changes via PR
3. Discuss in team meeting

---

**END OF DOCUMENTATION STANDARDS**

*Follow these standards for consistent, maintainable documentation across the TSH ERP Ecosystem.*
