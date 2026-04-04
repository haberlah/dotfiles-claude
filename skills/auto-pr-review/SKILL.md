---
name: auto-pr-review
description: Create a PR from the current branch, trigger Claude Code Review via the GitHub App, retrieve the review, and present it for approval. Use after completing any task that changes files in a project repo on main/master. Triggers on task completion when working in project repos — look for phrases like "done", "finished", "completed", "ready to review", or when you've made substantive file changes on main/master.
---

# Auto PR + Code Review

After completing work on a project repo (on main/master), run this workflow to create a PR, trigger an official Claude Code Review, and present the results.

## Prerequisites

- `gh` CLI authenticated
- Claude GitHub App installed on the repo's org (with Pull Requests read/write)
- Repo has a `CLAUDE.md` in root (required for Claude Code Review to activate)

## Workflow

### Step 1 — Commit and push

Stage and commit changed files with a descriptive message. Push to an `auto/YYYY-MM-DD` branch:

```bash
git add <files>
git commit -m "<descriptive message>"
git push --force-with-lease origin "HEAD:refs/heads/auto/$(date +%Y-%m-%d)"
```

Use `--force-with-lease` to handle re-pushes on the same day safely.

### Step 2 — Create or detect PR

Check for an existing open PR on today's auto branch. Create one if none exists:

```bash
AUTO_BRANCH="auto/$(date +%Y-%m-%d)"
EXISTING=$(gh pr list --head "$AUTO_BRANCH" --state open --json number --jq '.[0].number')

if [ -n "$EXISTING" ]; then
  PR_NUMBER=$EXISTING
  echo "Existing PR #$PR_NUMBER updated"
else
  PR_URL=$(gh pr create --head "$AUTO_BRANCH" --base main \
    --title "<short title>" \
    --body "<summary of changes>")
  PR_NUMBER=$(echo "$PR_URL" | grep -o '[0-9]*$')
  echo "Created PR #$PR_NUMBER"
fi
```

### Step 3 — Trigger Claude Code Review

Post a review request comment on the PR:

```bash
gh pr comment "$PR_NUMBER" --body "@claude review"
```

This triggers the Claude GitHub App to run a multi-agent review (correctness, security, code quality) using the org's Teams subscription.

### Step 4 — Poll for the review

Check for the review response. Poll every 30 seconds, up to 5 minutes:

```bash
for i in $(seq 1 10); do
  sleep 30
  REVIEW=$(gh api "repos/{owner}/{repo}/issues/${PR_NUMBER}/comments" \
    --jq '[.[] | select(.user.login != "haberlah")] | last | .body' 2>/dev/null)
  if [ -n "$REVIEW" ]; then
    echo "$REVIEW"
    break
  fi
done
```

Also check the PR reviews endpoint for inline review comments:

```bash
gh api "repos/{owner}/{repo}/pulls/${PR_NUMBER}/reviews" \
  --jq '.[] | select(.user.login != "haberlah") | {state: .state, body: .body}'
```

### Step 5 — Present review and wait for approval

Show the review findings to the user with:
- Summary of what the review found
- Any issues flagged (bugs, security, quality)
- Recommendation (merge / needs changes)

Wait for the user to approve before merging.

### Step 6 — Merge (on user approval)

```bash
gh pr merge "$PR_NUMBER" --merge --delete-branch
```

Use `--merge` (not `--squash`) to keep local and remote history aligned.

## Fallback — App review not available

If the Claude GitHub App doesn't respond within 5 minutes:

1. Read the diff: `gh pr diff "$PR_NUMBER"`
2. Provide your own assessment of the changes
3. Note that the official review is pending on GitHub
4. Still wait for user approval before merging

This can happen if:
- Code Review isn't enabled in the org's Anthropic Console (Teams > Integrations > GitHub)
- The repo doesn't have a `CLAUDE.md` (required for the App to activate)
- The App is temporarily unavailable

## Do not use this skill for

- **dotfiles-claude** — config repo pushes directly to main via the Stop hook
- **Feature branches** — push directly, no PR needed
- **Trivial changes** — when the user clearly wants a quick push without review
