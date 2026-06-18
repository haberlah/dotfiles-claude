# Claude Code Review

Claude Code Review is disabled by default in the public policy. Enable it only by setting `providers.claude.enabled` to `true` and listing allowed repositories in `providers.claude.allowedRepos`.

## Manual Only

- Trigger Claude only after the user explicitly asks for Claude review on the current PR.
- Use the configured exact trigger, normally `@claude review once`.
- Do not use bare `@claude review` unless the local policy intentionally permits repeated behavior.

## Allowed Repositories

GitHub App repository access is the hard security boundary. The policy is a behavioral guard that prevents agents from requesting Claude outside the intended repositories.

Keep both layers aligned:

- GitHub App installation: selected repositories where Claude is allowed.
- `review-policy.json`: same allowed repositories in `providers.claude.allowedRepos`.

If the GitHub App has broader access than policy, report configuration drift before triggering Claude.

## First Cycle

When `firstCycleOnly` is enabled, the first Claude trigger/review/check on a PR consumes the Claude review cycle. Subsequent reviews after fixes should use `reviewFlow.rerunProviderAfterFixes`, normally Codex.
