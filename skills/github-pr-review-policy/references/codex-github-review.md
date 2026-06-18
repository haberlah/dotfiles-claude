# Codex GitHub Review

Codex is the default PR review bot for BellaAssist/Bella-Slainte work.

## Required Setup

- ChatGPT Codex GitHub connector installed for the repository or organization.
- Codex code review enabled in ChatGPT/Codex settings for the repository.
- `AGENTS.md` in the repo when review guidance should be durable.
- `gh` authenticated locally when an agent needs to inspect PR comments, checks, and branch protection.

## Triggering

- Manual trigger: `@codex review`.
- Focused manual trigger: `@codex review for <short focus>`.
- Automatic review should be enabled for repos where every PR should be reviewed. If automatic review is active, verify current-head evidence before posting a duplicate manual trigger.

## Review Guidance

Use top-level `AGENTS.md`:

```md
## Review guidelines

- Treat privacy, auth, RLS, data isolation, and migration safety regressions as blocking.
- Flag documentation-only typos only when the repo explicitly treats them as review findings.
```

Place narrower `AGENTS.md` files deeper in the repo only when a subtree needs different guidance.

## Follow-up Fixes

Use Codex as the re-review path after fixes are pushed. For a fix task, a GitHub comment such as `@codex fix the P1 issue` starts a Codex cloud task when the connector has permission to push back.

## GitHub Action Alternative

Use `openai/codex-action@v1` only when the repo needs CI-controlled review instead of, or in addition to, hosted Codex reviews. Store `OPENAI_API_KEY` as a GitHub secret, check out the PR, run the action with a review prompt, and post the final output or structured findings back to the PR. Keep the sandbox/read-only posture as narrow as practical and restrict who can trigger the workflow.
