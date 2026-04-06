---
name: claude-pr-review
description: Commit, push, and optionally create a PR with Claude Code Review for any repo. Presents the user with workflow options before taking action. Use after completing any task that changes files in a project repo. Triggers on task completion — look for phrases like "done", "finished", "completed", "push", "commit", "create a PR", "review", or when you've made substantive file changes.
---

# Claude PR Review

After completing work on a repo, run this workflow to commit, push, and optionally create a PR with Claude Code Review. The user chooses the workflow path.

## Prerequisites

- `gh` CLI authenticated
- For option 3 (Code Review): Claude GitHub App installed on the repo's org, Code Review enabled (claude.ai → Organisation → Claude Code), overage spend limit set (claude.ai → Organisation → Usage)
- For option 3: repo has a `CLAUDE.md` in root (required for the App to activate)
- Optional: `REVIEW.md` in repo root for review-specific instructions

## Cost awareness

Claude Code Review (option 3) costs approximately **A$15-25 per review**. The review runs multi-agent analysis with a verification step (<1% false positive rate). Options 1 and 2 are free.

## Workflow

### Step 0 — Detect context and present options

Before doing anything, check:
- Are there uncommitted changes? (`git status --short`) — if none, inform the user and exit
- Current branch name (`git branch --show-current`)
- Repo name (`gh repo view --json nameWithOwner --jq '.nameWithOwner'` or from git remote)

Then present the decision using the **AskUserQuestion** tool for an interactive selection menu:

```
AskUserQuestion with:
  question: "How would you like to push these changes to GitHub?"
  header: "Push method"
  options:
    - label: "Commit and push"
      description: "Push directly to [current branch] (no PR, no review)"
    - label: "Create PR"
      description: "Push to auto/ branch and open a PR (no review)"
    - label: "Create PR + Claude Code Review"
      description: "Full review workflow with Claude GitHub App (~$15-25, 5-20 min)"
```

**Smart detection — skip the prompt if intent is already clear:**
- User said "push it", "commit this", "push to main" → option 1
- User said "create a PR", "open a PR" → option 2
- User said "review", "review it", "get a review", "PR with review" → option 3
- User said "done", "finished" or similar without specifying → show the interactive menu

### Step 1 — Commit

Stage and commit changed files with a descriptive message:

```bash
git add <specific files that changed>
git commit -m "<descriptive message>"
```

Use a meaningful commit message — not "auto: files". Describe what changed and why.

### Step 2 — Execute chosen path

#### Option 1: Commit and push (direct)

Push to the current branch:

```bash
git push origin "$(git branch --show-current)"
```

Report the commit SHA and branch. Done.

#### Option 2: Create PR (no review)

Push to an `auto/YYYY-MM-DD` branch and create a PR:

```bash
AUTO_BRANCH="auto/$(date +%Y-%m-%d)"
git push --force-with-lease origin "HEAD:refs/heads/${AUTO_BRANCH}"
```

If `--force-with-lease` fails with "stale info", use `--force` (auto/ branches are ephemeral).

Check for existing PR, create if needed:

```bash
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')
EXISTING=$(gh pr list --head "$AUTO_BRANCH" --state open --json number --jq '.[0].number')

if [ -n "$EXISTING" ]; then
  PR_NUMBER=$EXISTING
else
  PR_URL=$(gh pr create --head "$AUTO_BRANCH" --base main \
    --title "<short title>" \
    --body "<summary of changes>")
  PR_NUMBER=$(echo "$PR_URL" | grep -o '[0-9]*$')
fi
```

Report the PR URL. Done (unless user wants to continue to option 3).

#### Option 3: Create PR + Claude Code Review

Execute option 2 first (push + create PR), then continue:

**3a. Guard checks — ALL must pass before triggering:**

```bash
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')

# Guard 1: No review already in progress (check runs)
IN_PROGRESS=$(gh api "repos/${REPO}/commits/${AUTO_BRANCH//\//%2F}/check-runs" \
  --jq '[.check_runs[] | select(.name | test("Claude"; "i")) | select(.status == "in_progress")] | length' 2>/dev/null || echo "0")

# Guard 2: Last comment isn't already a trigger
LAST_COMMENT=$(gh api "repos/${REPO}/issues/${PR_NUMBER}/comments" \
  --jq '.[-1].body // ""' 2>/dev/null)

# Guard 3: Latest commit not already reviewed (exclude the auto-tip "configured for manual reviews" comment — it has a commit_id but is not a real review)
LATEST_SHA=$(git rev-parse HEAD)
LATEST_REVIEW_SHA=$(gh api "repos/${REPO}/pulls/${PR_NUMBER}/reviews" \
  --jq '[.[] | select(.user.login == "claude[bot]") | select(.body | test("configured for manual") | not)] | last | .commit_id // ""' 2>/dev/null)
```

**Trigger rules:**
- `IN_PROGRESS` must be "0"
- `LAST_COMMENT` must NOT contain `@claude`
- `LATEST_REVIEW_SHA` must NOT equal `LATEST_SHA`

If any guard fails, inform the user why and wait.

**3b. Trigger exactly one review:**

```bash
gh pr comment "$PR_NUMBER" --body "@claude review once"
TRIGGER_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)
```

**CRITICAL: The trigger comment must start with `@claude`.** Do NOT prefix it with `[Claude Code]` or any other text — the GitHub App's mention parser requires `@claude` at the start of the comment body. Prefixed mentions are acknowledged (👀 reaction) but silently ignored as triggers.

Use `@claude review once` — not bare `@claude review`. The `once` variant prevents automatic push-triggered reviews, avoiding cascading costs.

**3c. Wait for the review (patient polling):**

Reviews take **5-20 minutes**. Poll check runs every 60 seconds, max 20 attempts:

```bash
for i in $(seq 1 20); do
  sleep 60

  # Primary: check for completed review check run
  CHECK=$(gh api "repos/${REPO}/commits/${AUTO_BRANCH//\//%2F}/check-runs" \
    --jq '[.check_runs[] | select(.name | test("Claude"; "i")) | select(.status == "completed")] | last' 2>/dev/null)

  # Secondary: check for new review from claude[bot]
  NEW_REVIEW=$(gh api "repos/${REPO}/pulls/${PR_NUMBER}/reviews" \
    --jq "[.[] | select(.user.login == \"claude[bot]\" and .submitted_at > \"${TRIGGER_TIME}\")] | last" 2>/dev/null)

  if [ -n "$NEW_REVIEW" ] && [ "$NEW_REVIEW" != "null" ]; then
    break
  fi

  # Check for billing/error comment
  BOT_COMMENT=$(gh api "repos/${REPO}/issues/${PR_NUMBER}/comments" \
    --jq "[.[] | select(.user.login == \"claude[bot]\" and .created_at > \"${TRIGGER_TIME}\")] | last | .body // \"\"" 2>/dev/null)

  if [ -n "$BOT_COMMENT" ] && [ "$BOT_COMMENT" != "" ]; then
    break  # Bot responded (possibly billing error)
  fi
done
```

**3d. Retrieve and present findings:**

```bash
REVIEW_ID=$(echo "$NEW_REVIEW" | jq -r '.id')
gh api "repos/${REPO}/pulls/${PR_NUMBER}/reviews/${REVIEW_ID}/comments" \
  --jq '.[] | {path: .path, line: .line, body: .body}'
```

Parse severity markers when presenting:
- **🔴 Important** — bugs to fix before merging
- **🟡 Nit** — minor, worth fixing but not blocking
- **🟣 Pre-existing** — bugs in the codebase, not from this PR

If no issues found: "Clean review — no issues found."
If review was skipped (billing): inform user, suggest checking claude.ai → Organisation → Usage.

**3e. Get user decision on each finding:**
- **Fix** — will address
- **Skip** — decline with reason
- **Discuss** — need more context

**3f. Post decision to PR (audit trail):**

Confirm with user first: "I'll post this decision to the PR — OK?"

```markdown
**Review response** (via Claude Code)

**Findings addressed:**
- [Summary] — fixed in commit [sha]

**Findings declined:**
- [Summary] — [user's reason]

**Decision:** [Ready to merge / Pushing fixes]
```

```bash
gh pr comment "$PR_NUMBER" --body "<decision comment>"
```

**3g. Push fixes (if needed):**

If fixes were requested:
1. Make changes, commit referencing the finding
2. Push to same auto/ branch
3. Ask user if they want a re-review ($15-25 cost). If yes, run guards and trigger once more.

**3h. Merge (on user approval only):**

```bash
gh pr merge "$PR_NUMBER" --merge --delete-branch
git checkout main && git pull origin main
```

Use `--merge` (not `--squash`) to keep local and remote aligned.

## Fallback — review timeout

If the Claude GitHub App doesn't respond within 20 minutes:

1. Read the diff: `gh pr diff "$PR_NUMBER"`
2. Provide your own assessment (clearly labelled as self-review)
3. Post a PR comment: `"[Claude Code] Official review timed out after 20 minutes. Self-review provided in conversation."`
4. **Do NOT re-trigger** — the App may still be processing
5. Still wait for user approval before merging

Common causes:
- Overage spend limit exhausted
- Code Review not enabled in org settings
- No `CLAUDE.md` in repo root
- Org has Zero Data Retention enabled (incompatible)

## Anti-spam rules

1. **One trigger per push.** Never post another `@claude review once` until a review arrives OR new commits are pushed.
2. **Check before triggering.** Always run all three guards first.
3. **Never retry on silence.** 20-min timeout → fallback. Do not re-trigger.
4. **Use `review once`.** Never bare `@claude review` — prevents cascading costs.
5. **Prefix automated comments** with `[Claude Code]` — **except** the trigger comment, which must start with `@claude` (no prefix).
6. **One decision comment per review cycle.**

## Related tools

- **claude-code-action** (GitHub Action) — Anthropic's official Action for CI/CD. Supports structured output, fix links, comment classification.
- **REVIEW.md** — review-specific instructions, separate from CLAUDE.md.
- **Dispatch API** (emerging) — programmatic Claude Code execution for background review orchestration.
