---
name: github-replit-production-release
description: "Use when the user wants to ship local repo changes through GitHub and Replit production: submit or update a GitHub PR, run Codex or Claude PR review, fix issues, handle required human/code-owner approval gates, merge, pull or sync into Replit, run Replit checks, publish production, verify the live app, and confirm GitHub, Replit, and local clones are synced. Trigger on deploy to GitHub/Replit, submit PR then publish, pull into Replit, production release, required PR approval, or verify all repos are synced."
---

# GitHub Replit Production Release

Use this as the release controller for local code changes that must reach a Replit production app through GitHub. Completion means the remote GitHub state, Replit workspace/deployment, live app, and local clone are all checked from evidence.

## Operating assumptions

- Prefer local clones under `~/Documents/GitHub/`.
- Use `gh` for GitHub truth: PRs, checks, comments, merge state, branch state.
- Replit does not have a reliable local CLI on this machine unless a command check proves otherwise. Use Replit workspace shell, Git pane, Security Center, and Publishing UI for Replit pull, scan, publish, and verification.
- If the native Replit app is available or the user asks for it, use Computer Use against `Replit.app` for Replit UI work. Do not substitute Chrome for Replit publish/sync steps; reserve Chrome/browser checks for the live production app or profile-authenticated flows that truly need browser cookies.
- External writes are high impact. If the user has not already asked to commit, open PR, merge, or publish, get clear approval before that step.
- Never use `git reset --hard`, force-push shared branches, or discard unrelated work unless the user explicitly requests it.

## Start here

Resolve the repo and run the helper:

```bash
SKILL_DIR="${CODEX_HOME:-$HOME/.codex}/skills/github-replit-production-release"
"$SKILL_DIR/scripts/release_preflight.sh" /path/to/repo
```

For Claude Code, set `SKILL_DIR` to the actual installed/source skill path. On this machine the Claude copy lives at `$HOME/dotfiles-claude/skills/github-replit-production-release`; if installed into Claude's default skill directory, use `$HOME/.claude/skills/github-replit-production-release`.

Use the preflight output to identify:

- repo root, branch, remote, GitHub repo, default branch, current SHA
- dirty/untracked files and whether they are in scope
- local branch divergence from `origin/<default>`
- open PR for the current branch, if any
- package scripts and `.replit` deployment hints

## Release workflow

1. **Preflight and scope**
   - Fetch `origin` before comparing state.
   - Inspect untracked files before deciding whether they belong in the change.
   - Compare against `origin/<default>`, not only a clean working tree.
   - Identify the live Replit URL and Replit project before promising production completion.

2. **Local validation**
   - Run the repo's real gates, usually typecheck, tests, and build.
   - If dependencies are missing, install from the lockfile using the repo's package manager.
   - Avoid production data mutation. Treat commands like `db:push`, migrations, seeders, and backfills as live-change paths unless the repo proves otherwise.
   - For database-backed previews, use a disposable local/dev database or explicitly state that the gate could not be run.

3. **GitHub PR**
   - Create a purpose branch from current `main`/default unless continuing an existing feature branch.
   - Commit only scoped files with a concrete message.
   - Push and create or update a PR with a body that includes validation run, risks, and Replit follow-up steps.
   - If an auto PR workflow exists, verify it actually created or updated the PR.

4. **Codex PR review**
   - Use the repo's configured review mechanism. For Codex GitHub review, use the supported `@codex review` trigger only when the repo/account has that integration active.
   - Poll PR checks, review comments, and requested changes. Fix actionable issues, push follow-up commits, and repeat until checks are green and review items are resolved or explicitly waived.
   - Separate true blockers from style nits, stale comments, and known unrelated validation debt.
   - Before asking for merge or code-owner approval, bring the GitHub review state back into the current Codex or Claude console. Include:
     - PR number, branch, author, and current review decision.
     - GitHub checks and Actions status, including failing job names and links when available.
     - Codex/Claude/GitHub review findings, grouped as fixed, waived, or still blocking.
     - Follow-up commits pushed after review, with short SHAs and what they changed.
     - Any remaining risk or verification surface that could not be checked.
   - If review findings or failing checks required fixes, state exactly what was changed and re-run or re-read the relevant GitHub checks before continuing.

5. **Required human approval gate**
   - Before merge, inspect branch protection, CODEOWNERS, PR author, requested reviewers, and the active `gh` identity:

     ```bash
     gh auth status
     gh api user --jq .login
     gh pr view <number> --repo <owner/repo> --json author,reviewRequests,reviewDecision,mergeStateStatus,statusCheckRollup
     gh api /repos/<owner>/<repo>/branches/<default>/protection \
       --jq '{required_pull_request_reviews:.required_pull_request_reviews}'
     ```

   - For Bella-Slainte private repos with mandatory `@haberlah` CODEOWNERS approval, a Codex or Claude review is advisory only. It does not satisfy the required `@haberlah` approval.
   - If the active `gh` account is `haberlah`, the PR author is not `haberlah`, checks/reviews are acceptable, and the user explicitly authorizes approval, submit the code-owner approval with:

     ```bash
     gh pr review <number> --repo <owner/repo> --approve --body "Approved as code owner."
     ```

   - If the PR author is `haberlah`, never attempt `gh pr review --approve`, even when `haberlah` is repo admin and CODEOWNER. GitHub rejects author self-approval (`Review Can not approve your own pull request`) and it does not satisfy required reviews. Offer either a different eligible reviewer/code-owner path or an explicitly authorized solo-admin merge path.
   - If the user explicitly authorizes a solo-admin path, treat it as an explicit bypass merge, not a self-approval. Verify branch protection, mergeability, checks, and advisory reviews first. For Bella-Slainte repos, the preferred protection standard is `enforce_admins: true` with `haberlah` listed in `required_pull_request_reviews.bypass_pull_request_allowances.users`; older repos may still have `enforce_admins: false`, but tighten that before relying on it when practical. For a mergeable PR blocked only by `REVIEW_REQUIRED`, use:

    ```bash
    gh api /repos/<owner>/<repo>/branches/<default>/protection \
      --jq '{required_pull_request_reviews:.required_pull_request_reviews,enforce_admins:.enforce_admins.enabled}'
    gh pr view <number> --repo <owner/repo> --json author,reviewDecision,mergeStateStatus,mergeable,statusCheckRollup
    gh pr merge <number> --repo <owner/repo> --squash --admin --delete-branch
    ```

    This was originally confirmed on BellaAssist-MVP-2 PR #40 on 2026-05-14: the PR was authored by `haberlah`, self-approval was rejected, and `gh pr merge --squash --admin --delete-branch` succeeded. The Bella-Slainte active-repo standard was then tightened to enforce protections for admins while allowing `haberlah` as the explicit bypass user. If `gh pr merge --admin` is rejected, stop and report the exact blocker.
   - Check repo-specific review policy before requesting approval. Most active Bella-Slainte repos are David-gated (`require_code_owner_reviews: true`, `CODEOWNERS` `* @haberlah`). The KB repo (`bella-assist-kb`) is intentionally looser: it requires one approval, but `require_code_owner_reviews` is false, so any eligible writer/admin reviewer can approve someone else's PR. Do not re-tighten KB to David-only unless the user explicitly asks.
   - After any approval, re-read the PR mergeability and review decision before merging. Before any admin-bypass merge, re-read mergeability and protection state. Do not assume either path satisfied the gate.
   - Make the approval or bypass decision easy for the user to answer in the active interface. If the PR author is not `haberlah`, ask exactly: `Approve this PR as @haberlah now? Reply yes or no.` If the PR author is `haberlah`, ask exactly: `Admin-bypass merge this PR as @haberlah now? Reply yes or no.` Do not proceed on ambiguous responses.

6. **Merge**
   - Merge only after required checks and review gates are satisfied and the user has authorized merge/publish for this run.
   - After merge, fetch and fast-forward the local default branch. Confirm the local default SHA equals `origin/<default>`.

7. **Replit sync and checks**
   - Pull or sync the merged default branch into Replit through the Replit Git pane or workspace shell.
   - If the Replit workspace has its own publish/checkpoint commits, merge `origin/<default>` into the workspace instead of rewriting Replit history. Do not push Replit-generated history directly back to GitHub unless the user explicitly asks.
   - Confirm the GitHub default branch content is present in Replit. Exact SHA equality is ideal, but Replit may remain ahead because of platform commits; in that case use concrete evidence: merge commit, file content, Git pane status, deployment logs, and live behavior.
   - Inspect Replit-local config after sync, especially `.replit`, `[env]`, `[userenv.production]`, and `[userenv.shared]`. Replit can preserve stale runtime values across merges; for access changes, search active config for removed users, emails, domains, IDs, and tokens before publishing.
   - Run Replit workspace checks that are safe for the app: install, typecheck, tests, build, and Replit security scanner when available.
   - For Replit Security Center, the automatic dependency scan refresh is a normal check. Do not start paid/credit agent scans unless the user explicitly asks for that deeper scan.
   - Do not run live schema/data mutation in Replit unless the user explicitly asks and the migration path is understood.

8. **Publish production**
   - Publish/deploy from Replit only after Replit checks pass or the user accepts documented residual risk.
   - Watch deployment logs until completion or clear failure.
   - Capture the production deployment URL, deployment time, deployment ID, and any commit/build identifier Replit exposes. A successful Replit deploy log should show all stages complete and end with a clear success line such as `Deployment successful`.

9. **Live verification**
   - Open the production URL in a browser and verify the actual changed behavior.
   - Exercise the relevant auth route or smoke flow. For auth-gated apps, verify unauthenticated behavior and, if credentials/session are available, authenticated behavior.
   - For GitHub-OAuth apps without the target user's credentials, verify what can be proven: `/api/login` redirects to GitHub OAuth with expected scopes, `/api/auth/user` rejects unauthenticated requests, production serves the current build, and tests/config prove the allowlist behavior. State clearly that the target user's actual login was not credential-tested.
   - Check server responses or browser console/network only as needed; do not treat a successful HTTP 200 for the shell as proof of the feature.

10. **Final sync report**
   - Report GitHub default branch SHA, local default branch SHA, Replit workspace/deployment SHA or evidence, live URL, and verification result.
   - Check for other local clones before claiming "all local clones" are synced. Search `~/Documents` for matching repo directories, inspect their remotes, and fast-forward clean stale clones with `git pull --ff-only origin <default>` when safe.
   - Call out any surface that could not be verified and why.
   - If a branch, PR, or deployment is left open, state the exact next action.

## Access and auth releases

- For explicit external GitHub access, prefer immutable GitHub user IDs over usernames or email addresses. Usernames can change and GitHub often hides account email addresses; the numeric user ID is the stable allowlist key.
- Keep removed-user regression tests when practical. It is acceptable for removed emails or users to appear in tests that prove rejection, but they must not remain in active runtime config such as `.replit`, `.env.example`, secrets, or server allowlists.
- If sessions embed allowlist provenance, verify removed allowlist users lose access on the next authenticated request, not just on future login.

## Common blockers

- GitHub review integration is not installed or does not respond to `@codex`.
- Required `@haberlah` code-owner approval is blocked because the PR author is also `haberlah`; GitHub rejects author self-approval. Do not attempt approval in this case. Use a non-author approval path, or an explicitly authorized `gh pr merge --admin` bypass when the user accepts the solo-admin path.
- Replit requires browser-authenticated UI action and cannot be completed from local shell.
- The user expects Replit app actions to happen in the native Replit app when they say so; using Chrome for that stage is a workflow bug.
- Replit workspace is dirty or behind GitHub after merge.
- Replit workspace is ahead of GitHub because of platform publish/checkpoint commits. This is not automatically wrong; report the divergence and prove deployed content instead of trying to force identical histories.
- Required checks depend on secrets or databases not available locally.
- Build passes but live deployment points at an older commit.

## Final response shape

Use a concise release report:

```markdown
Done.

GitHub: PR #N merged into `main` at `<sha>`.
Replit: pulled or merged `<sha>`, checks passed, production published as `<deployment-id>`.
Live verification: `<url>` verified for `<behavior>`.
Local sync: `/path/to/repo` and any other local clones found are at `origin/main` `<sha>`.

Notes: <blockers or residual risks, if any>
```
