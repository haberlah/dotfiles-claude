# Claude Code Review

Claude Code Review is optional, manual, and deliberately narrower than Codex review.

## Scope

- Allowed repository: `Bella-Slainte/BellaAssist-MVP-2` only.
- Do not use Claude GitHub review for architecture-pack, KB, Mountwinter, SOW, or other Bella-Slainte repos unless David explicitly changes this policy.
- The GitHub-side Claude App should be restricted to selected repositories with only `BellaAssist-MVP-2` selected. If the app still has `repository_selection: all`, report that as configuration drift before triggering Claude.

## Triggering

- Trigger only after David explicitly asks for Claude Code Review on the current PR.
- Use exactly: `@claude review once`.
- Do not prefix the trigger comment.
- Do not use bare `@claude review`; it can enable repeated review behavior and unnecessary cost.

## First-Cycle Rule

The allowed Claude cycle is the first review cycle for the first reviewable PR head only.

Allowed inside the same first cycle:

- Polling for the original run.
- Classifying billing, quota, infra, skipped, or timeout outcomes.
- Retrying only when the existing Claude review workflow classifies the prior run as infrastructure failure and the retry cap allows it.

Not allowed:

- Triggering Claude after fix commits are pushed.
- Triggering Claude because Codex found issues.
- Triggering Claude for a later PR head after an earlier Claude review completed, skipped, or produced any bot-side review/check-run evidence.

Use Codex for every later review.

## Generic or No-Findings Responses

Never accept a generic Claude "looks good", thumbs-up, or no-findings message without checking whether a real review ran. Verify at least one of:

- A Claude review object exists on the current head SHA and has inline review comments.
- A Claude check-run for the current head SHA completed successfully after the trigger and the review/comment body is a no-findings result.

If the response body mentions spend limits, overage, credits, skipped, disabled, not installed, not configured, or errors, classify as skipped or failed, not clean.
