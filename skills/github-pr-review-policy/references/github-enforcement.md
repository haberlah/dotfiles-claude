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

If the branch uses repository rulesets instead of classic branch protection, inspect the rulesets in GitHub or through the appropriate GitHub API.

## Configuration Boundaries

- GitHub App repository access controls which repositories a bot can reach.
- Branch protection and rulesets control merge eligibility.
- `review-policy.json` controls agent behavior before comments are posted.
- The guard script classifies observed evidence; it does not post comments or merge PRs.

Always verify live GitHub configuration before merging. Any static reference can drift.
