---
name: github-pr-review-policy
description: Review GitHub pull requests against the shared Codex/Claude PR review policy. Use before creating, triggering, checking, re-running, or summarizing PR reviews; when deciding between @codex review and @claude review once; when inspecting bot review results, required checks, branch protection, or merge readiness; and when verifying whether generic thumbs-up/no-findings review text actually means the bot ran.
---

# GitHub PR Review Policy

Use this skill as the source of truth for BellaAssist/Bella-Slainte PR review routing across Codex, Claude Code, and GitHub.

## Policy

- Request Codex review on every new PR as soon as the PR exists, unless Codex automatic review has already produced evidence on the current head SHA.
- Use the exact Codex trigger: `@codex review`. Add a short focus only when useful, for example `@codex review for auth and RLS regressions`.
- Treat Claude Code Review as manual-only. Never trigger it unless David explicitly asks for Claude review for that PR.
- Limit Claude Code Review to `Bella-Slainte/BellaAssist-MVP-2`.
- Limit Claude Code Review to the first review cycle only. After any fix commit or subsequent PR head, use Codex for re-review.
- Use the exact Claude trigger when manually authorized: `@claude review once`. Do not use bare `@claude review`.
- Treat Codex and Claude bot reviews as advisory. They do not satisfy GitHub branch protection, required human approval, CODEOWNERS, required status checks, or explicit merge authorization.
- If a handover says `@claude review`, treat that as stale unless the user explicitly requests Claude review in the current task.
- Do not place literal bot mentions in PR templates or routine PR bodies. Use checklist wording such as "Codex review requested" so templates do not accidentally trigger a bot.

## Workflow

1. Identify the repository, PR number, current head SHA, base branch, PR author, and open/closed/draft state.
2. Run the guard script before any review trigger:

   ```bash
   python3 <skill>/scripts/pr_review_guard.py pre-codex --repo OWNER/REPO --pr PR_NUMBER
   python3 <skill>/scripts/pr_review_guard.py pre-claude --repo OWNER/REPO --pr PR_NUMBER
   ```

3. Trigger only when the guard returns `allow_trigger: true`.
4. After a bot posts a generic approval, "looks good", "no issues", thumbs-up, or similar no-findings response, classify the run before accepting it:

   ```bash
   python3 <skill>/scripts/pr_review_guard.py classify --bot codex --repo OWNER/REPO --pr PR_NUMBER
   python3 <skill>/scripts/pr_review_guard.py classify --bot claude --repo OWNER/REPO --pr PR_NUMBER
   ```

5. If classification is `generic_unverified`, `skipped`, `silent_timeout`, `infra_or_review_error`, or `no_review_evidence`, do not report the review as clean. Report the exact classification and fall back to Codex or self-review according to the policy.
6. After fixes are pushed, run Codex review again when review evidence is required. Do not trigger another Claude review.

## Reporting

When summarizing PR review state, include:

- PR number, repo, branch, and head SHA.
- Which bot was triggered, exact trigger comment, and whether it was automatic or manual.
- Guard classification, not just the bot's prose.
- Inline findings grouped as fixed, waived, still blocking, or pre-existing.
- GitHub checks and branch-protection status.
- Required human/code-owner approval status.
- Whether any no-findings review was verified as actually run.

## References

- Read `references/codex-github-review.md` for Codex review behavior, `AGENTS.md` review guidelines, automatic reviews, and `openai/codex-action`.
- Read `references/claude-code-review.md` for Claude manual review limits and first-cycle rules.
- Read `references/github-enforcement.md` when branch protection, required checks, CODEOWNERS, or merge readiness matter.
- Read `references/github-guard-checks.md` before modifying the guard script or changing review classification logic.
- `references/review-policy.json` is the machine-readable provider/repo policy used by the guard script.
