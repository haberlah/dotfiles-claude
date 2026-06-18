# GitHub Enforcement

Bot reviews are advisory unless GitHub itself enforces them through branch protection, rulesets, required reviews, CODEOWNERS, or required status checks.

## Inspect Before Merge

Use `gh` to inspect the actual gate:

```bash
gh pr view PR_NUMBER --repo OWNER/REPO \
  --json author,headRefOid,reviewDecision,mergeStateStatus,mergeable,statusCheckRollup,reviewRequests

gh api /repos/OWNER/REPO/branches/BASE_BRANCH/protection \
  --jq '{required_pull_request_reviews:.required_pull_request_reviews, required_status_checks:.required_status_checks, enforce_admins:.enforce_admins.enabled}'
```

## Bella-Slainte Defaults

- `Bella-Slainte/BellaAssist-MVP-2`: code-owner approval from `@haberlah` is required; bot review is advisory.
- `Bella-Slainte/bella-assist-architecture-pack`: code-owner approval from `@haberlah` and `validate` status check are required; bot review is advisory.
- `Bella-Slainte/bella-assist-kb`: one approval is required; code-owner review is not required unless GitHub config changes.

Always verify live GitHub branch protection before merging; this reference can drift.
