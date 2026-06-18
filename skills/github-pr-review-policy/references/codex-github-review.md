# Codex GitHub Review

Codex is the default review provider in the bundled policy because it can run on every configured repository and can be rerun after fix commits.

## Preconditions

- The Codex GitHub connector or equivalent workflow has access to the repository.
- Repository instructions such as `AGENTS.md` describe review expectations where needed.
- The PR is open and not draft.

## Triggers

- Manual trigger: `@codex review`.
- Focused trigger: `@codex review for <short focus>`.

Only use suffix/focus text when the provider policy has `allowTriggerSuffix: true`.

## Reruns

Use Codex as the re-review path after fixes when `reviewFlow.rerunProviderAfterFixes` is `codex`. The guard dedupes by current PR head, so a new head SHA can permit a new Codex review while avoiding duplicate reviews on the same head.

## CI Alternative

Teams that prefer CI-owned review can use a GitHub Action or other automation instead of comment triggers. Keep those workflows read-only by default, limit who can trigger them, and treat bot output as advisory unless GitHub branch protection requires the workflow.
