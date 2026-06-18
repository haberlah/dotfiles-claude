---
name: github-pr-review-policy
description: Review GitHub pull requests against a configurable AI review policy for Codex and Claude Code. Use before creating, triggering, checking, re-running, or summarizing PR reviews; when deciding between @codex review and @claude review once; when inspecting bot review results, GitHub checks, branch protection, CODEOWNERS, or merge readiness; and when verifying whether generic thumbs-up/no-findings review text actually means the review bot ran.
---

# GitHub PR Review Policy

Use this skill to route GitHub PR review requests across Codex, Claude Code, and GitHub without relying on bot prose alone.

## Policy

- Treat GitHub repository access, branch protection, required checks, CODEOWNERS, and required approvals as the source of truth for merge eligibility.
- Use the configured default provider for new PR review requests. The default policy uses Codex with `@codex review`.
- Treat Claude Code Review as manual-only when enabled. Never trigger Claude unless the user explicitly asks for Claude review for the current PR.
- Limit Claude Code Review to the configured `allowedRepos` list. If no repositories are configured, Claude is disabled.
- Limit Claude Code Review to the first review cycle when `firstCycleOnly` is enabled. After fix commits or subsequent review cycles, use the configured rerun provider, usually Codex.
- Use the configured exact Claude trigger, normally `@claude review once`. Do not use bare `@claude review` unless the local policy explicitly changes that.
- Treat Codex and Claude bot reviews as advisory unless GitHub itself enforces them through required status checks or required reviews.
- Do not place literal bot mentions in PR templates or routine PR bodies. Use checklist wording such as "AI review requested" so templates do not accidentally trigger a bot.
- Apply configured PR base-branch guidance as an education/checkpoint signal, not a merge gate unless GitHub policy says otherwise. Normal PRs usually target the configured trunk branch. Informational branches such as demo or sandbox deploy branches may be valid but differ from the normal deployment plan. Promotion environments such as testing, staging, and production should usually be handled by deployment promotion, not GitHub PR base branches.

## Workflow

1. Identify the repository, PR number, current head SHA, base branch, PR author, and open/closed/draft state.
2. Inspect the loaded policy:

   ```bash
   python3 <skill>/scripts/pr_review_guard.py policy
   ```

3. Run the guard before any review trigger:

   ```bash
   python3 <skill>/scripts/pr_review_guard.py pre-codex --repo OWNER/REPO --pr PR_NUMBER
   python3 <skill>/scripts/pr_review_guard.py pre-claude --repo OWNER/REPO --pr PR_NUMBER
   ```

4. Trigger only when the guard returns `allow_trigger: true`.
5. Inspect `base_branch_guidance` in the guard output. Report `informational`, `promotion_only`, or `nonstandard` guidance to the user before summarizing review/deploy readiness. Do not silently treat an alternate base branch as the normal deployment path.
6. After a bot posts a generic approval, "looks good", "no issues", thumbs-up, or similar no-findings response, classify the run before accepting it:

   ```bash
   python3 <skill>/scripts/pr_review_guard.py classify --bot codex --repo OWNER/REPO --pr PR_NUMBER
   python3 <skill>/scripts/pr_review_guard.py classify --bot claude --repo OWNER/REPO --pr PR_NUMBER
   ```

7. If classification is `generic_unverified`, `skipped`, `silent_timeout`, `infra_or_review_error`, `trigger_comment_not_found`, `head_changed_after_trigger`, or `no_review_evidence`, do not report the review as clean. Report the exact classification and fall back according to policy.
8. After fixes are pushed, use the configured rerun provider. In the default policy, that means Codex.

## Configuration

The guard loads policy in this order:

1. `--policy /path/to/review-policy.json`
2. `PR_REVIEW_POLICY_PATH`
3. `~/.config/github-pr-review-policy/review-policy.json`
4. `<skill>/references/review-policy.json`
5. `<skill>/references/review-policy.example.json`
6. built-in conservative defaults

Read `references/review-policy.example.json` before configuring a team policy. Claude is disabled unless the policy explicitly enables it and lists allowed repositories.

## Reporting

When summarizing PR review state, include:

- PR number, repo, branch, and head SHA.
- PR base branch guidance, especially when the base is informational, promotion-only, or nonstandard.
- Which bot was triggered, exact trigger comment, and whether it was automatic or manual.
- Guard classification, not just the bot's prose.
- Inline findings grouped as fixed, waived, still blocking, or pre-existing.
- GitHub checks and branch-protection status.
- Required human/code-owner approval status.
- Whether any no-findings review was verified as actually run.

## References

- Read `references/review-policy.example.json` for policy fields and safe defaults.
- Read `references/github-guard-checks.md` before changing review classification logic.
- Read `references/codex-github-review.md` for Codex review behavior and rerun guidance.
- Read `references/claude-code-review.md` for Claude manual review, allowed-repo, and first-cycle guidance.
- Read `references/github-enforcement.md` when branch protection, required checks, CODEOWNERS, or merge readiness matter.
