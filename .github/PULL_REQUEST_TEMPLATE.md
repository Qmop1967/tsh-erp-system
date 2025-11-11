# Pull Request

## Description
<!-- Provide a clear and concise description of what this PR does -->


## Type of Change
<!-- Mark the relevant option with an 'x' -->

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Refactoring (code improvements without changing functionality)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Security fix
- [ ] Dependency update
- [ ] CI/CD improvement

## Related Issues
<!-- Link to related issues using #issue_number -->

Fixes #
Relates to #

## Changes Made
<!-- List the main changes in this PR -->

-
-
-

## Testing Performed
<!-- Describe the tests you ran to verify your changes -->

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] E2E tests added/updated
- [ ] Manual testing performed
- [ ] Tested on staging environment

### Test Details:
<!-- Provide details about your testing -->


## Database Changes
<!-- Mark if applicable -->

- [ ] No database changes
- [ ] Database migration included
- [ ] Schema changes (describe below)
- [ ] Data seeding required

### Migration Details (if applicable):
<!-- Describe any database migrations -->


## Deployment Impact
<!-- Assess the impact of this change -->

- [ ] No deployment impact
- [ ] Requires environment variable changes
- [ ] Requires configuration update
- [ ] Requires Docker rebuild
- [ ] Requires database migration
- [ ] Requires service restart

### Deployment Notes:
<!-- Any special considerations for deployment -->


## Breaking Changes
<!-- If this is a breaking change, describe the impact -->

- [ ] No breaking changes
- [ ] Breaking changes (describe below)

### Breaking Change Details:
<!-- Detail what breaks and migration path -->


## Checklist
<!-- Ensure all items are complete before requesting review -->

### Code Quality
- [ ] Code follows project style guidelines (ruff, mypy pass)
- [ ] Self-review of code completed
- [ ] Comments added for complex logic
- [ ] No debugging code left (console.logs, print statements, etc.)
- [ ] Error handling implemented
- [ ] Security best practices followed

### Testing
- [ ] All tests pass locally
- [ ] Test coverage maintained/improved (≥60%)
- [ ] No failing tests in CI
- [ ] Edge cases considered and tested

### Documentation
- [ ] Code is self-documenting or well-commented
- [ ] README updated (if needed)
- [ ] API documentation updated (if applicable)
- [ ] CHANGELOG updated (if applicable)

### Dependencies
- [ ] New dependencies justified and documented
- [ ] Dependency versions pinned
- [ ] Security vulnerabilities checked (no HIGH/CRITICAL)

### Git
- [ ] Commits are atomic and well-described
- [ ] Branch is up to date with target branch
- [ ] No merge conflicts

## Performance Considerations
<!-- Describe any performance implications -->

- [ ] No performance impact
- [ ] Performance tested
- [ ] Performance concerns (describe below)

### Performance Notes:
<!-- Details about performance -->


## Security Considerations
<!-- Security review -->

- [ ] No security implications
- [ ] Security review completed
- [ ] Secrets/credentials handled properly
- [ ] Input validation implemented
- [ ] SQL injection prevented
- [ ] XSS prevention implemented
- [ ] CSRF protection maintained

## Zoho Integration Impact
<!-- If this affects TDS or Zoho integration -->

- [ ] No Zoho integration impact
- [ ] TDS Core changes
- [ ] Zoho sync logic modified
- [ ] Webhook processing affected

### Zoho Impact Details:
<!-- Details about Zoho-related changes -->


## Screenshots/Videos
<!-- If applicable, add screenshots or videos demonstrating the changes -->


## Reviewer Notes
<!-- Any specific areas you want reviewers to focus on -->


## Post-Deployment Tasks
<!-- Tasks to be done after deployment -->

- [ ] Monitor error logs
- [ ] Verify health checks
- [ ] Check Zoho sync status
- [ ] Verify integrations
- [ ] Update documentation site

---

## For Reviewers
<!-- Reviewer checklist -->

### Review Checklist
- [ ] Code quality and style
- [ ] Logic and implementation correctness
- [ ] Test coverage and quality
- [ ] Security considerations
- [ ] Performance implications
- [ ] Documentation completeness
- [ ] Breaking changes acknowledged
- [ ] Deployment plan clear

---

**PR Author:** @{{ github.actor }}
**Target Branch:** {{ github.base_ref }}
**Source Branch:** {{ github.head_ref }}
