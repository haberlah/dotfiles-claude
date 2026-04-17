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

**Concurrency awareness:** The bot's multi-agent framework shares compute across all Claude Code Reviews in the same org. Back-to-back triggers (e.g. multiple PRs plus review/fix cycles within ~30 minutes) can exhaust the shared worker pool, causing sub-agents to error in clusters (see 3c.1 below). If a previous review on ANY PR in the same repo completed within the last 5 minutes, wait out the remainder before triggering:

```bash
LAST_REVIEW_COMPLETED_AT=$(gh api "repos/${REPO}/commits?per_page=20" \
  --jq '[.[] | .sha] | .[]' | while read sha; do
    gh api "repos/${REPO}/commits/${sha}/check-runs" \
      --jq '.check_runs[] | select(.name | test("Claude"; "i") and .status == "completed") | .completed_at'
  done | sort -r | head -1)
```

If non-empty and within 5 minutes of now, `sleep` the remainder.

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

**3c.1. Classify outcome — distinguish review vs billing skip vs infra error vs silent timeout:**

After the poll exits, the check-run may be in one of five states. Treating any of them as "done" without inspecting is how you ship an unreviewed PR or waste budget re-triggering something that was silently skipped. Classify explicitly:

```bash
# Filter check-runs by started_at (NOT completed_at) — in-progress runs have
# null completed_at and would be excluded otherwise, leaving the classifier
# stuck in "pending" even when a run is actually running.
CHECK_CONCLUSION=$(gh api "repos/${REPO}/commits/${AUTO_BRANCH//\//%2F}/check-runs" \
  --jq '[.check_runs[] | select(.name | test("Claude"; "i")) | select(.started_at > "'"${TRIGGER_TIME}"'")] | last | .conclusion // "unknown"' 2>/dev/null)
CHECK_TITLE=$(gh api "repos/${REPO}/commits/${AUTO_BRANCH//\//%2F}/check-runs" \
  --jq '[.check_runs[] | select(.name | test("Claude"; "i")) | select(.started_at > "'"${TRIGGER_TIME}"'")] | last | .output.title // ""' 2>/dev/null)

# Fetch the LATEST review body (for BILLING_SKIPPED detection) AND the
# inline-comment count (the real "was this a review" signal).
LATEST_REVIEW=$(gh api "repos/${REPO}/pulls/${PR_NUMBER}/reviews" \
  --jq "[.[] | select(.user.login == \"claude[bot]\" and .submitted_at > \"${TRIGGER_TIME}\")] | last" 2>/dev/null)
REVIEW_ID=$(echo "$LATEST_REVIEW" | jq -r '.id // empty')
REVIEW_BODY=$(echo "$LATEST_REVIEW" | jq -r '.body // ""')
REVIEW_COMMENT_COUNT=0
if [ -n "$REVIEW_ID" ]; then
  REVIEW_COMMENT_COUNT=$(gh api "repos/${REPO}/pulls/${PR_NUMBER}/reviews/${REVIEW_ID}/comments" --jq 'length' 2>/dev/null || echo 0)
fi

BOT_COMMENT=$(gh api "repos/${REPO}/issues/${PR_NUMBER}/comments" \
  --jq "[.[] | select(.user.login == \"claude[bot]\" and .created_at > \"${TRIGGER_TIME}\")] | last | .body // \"\"" 2>/dev/null)

CHECK_STATUS=$(gh api "repos/${REPO}/commits/${AUTO_BRANCH//\//%2F}/check-runs" \
  --jq '[.check_runs[] | select(.name | test("Claude"; "i")) | select(.started_at > "'"${TRIGGER_TIME}"'")] | last | .status // "none"' 2>/dev/null)

if [ "$REVIEW_COMMENT_COUNT" -gt 0 ] 2>/dev/null; then
  OUTCOME="REVIEW_COMPLETED"            # Inline comments exist — real review
elif echo "$REVIEW_BODY" | grep -qiE "spend limit|overage|skipped|credits"; then
  OUTCOME="BILLING_SKIPPED"             # Review object with body only, billing-related
elif [ "$CHECK_CONCLUSION" = "neutral" ] && echo "$CHECK_TITLE" | grep -qi "error"; then
  OUTCOME="INFRA_ERROR"                 # Bot's framework crashed mid-review
elif [ "$CHECK_STATUS" = "in_progress" ]; then
  OUTCOME="STILL_RUNNING"               # Legitimately mid-review, poll window too short
elif [ -n "$BOT_COMMENT" ]; then
  OUTCOME="BOT_COMMENT_ONLY"            # Non-review bot comment (rare)
else
  OUTCOME="SILENT_TIMEOUT"              # Nothing happened — no check-run at all
fi
```

| Outcome | Signal | Next step |
|---------|--------|-----------|
| `REVIEW_COMPLETED` | A review object exists AND has ≥1 inline comment | Proceed to 3d |
| `BILLING_SKIPPED` | Review object exists with NO inline comments, body contains `spend limit` / `overage` / `skipped` / `credits` | Report to user with remediation link; do NOT retry; fall back to self-review |
| `INFRA_ERROR` | Check-run completed `neutral` with title containing `"error"` (e.g. `"12 agents exited with errors (threshold=10)"`), no review | Go to 3c.2 auto-retry (max 2 attempts) |
| `STILL_RUNNING` | Check-run is `in_progress` after 20 polls (the review is legitimately mid-work) | Extend polling — another 10–15 iterations at 45s cadence. Do NOT fall back or re-trigger. |
| `BOT_COMMENT_ONLY` | Bot issue comment after trigger, no review object | Report message to user; fall back |
| `SILENT_TIMEOUT` | No check-run exists at all, no review, no comment after 20 polls | Fall back; do NOT re-trigger |

**Critical distinction:** `SILENT_TIMEOUT` means "the bot never even started work" (no check-run). `STILL_RUNNING` means "the bot is actively working but takes longer than 15 minutes" — fine for large diffs or slow days. Conflating them was the original poll's bug: a legitimate long-running review was misclassified as silent and would have been falsely retried or self-reviewed.

**Critical bug the new classifier fixes:** a review object with only a body and zero inline comments is NOT a real review. The earlier heuristic `NEW_REVIEW_COUNT > 0` misclassified billing-skip messages ("spend limit reached") as `REVIEW_COMPLETED`, because the bot submits a review object to carry the skip message. Always count inline comments, not review objects.

**3c.2. Auto-retry on infrastructure error:**

When `OUTCOME=INFRA_ERROR`, the failure is upstream (not a findings result). The check-run `output.summary` typically contains a truncated Python traceback reporting N sub-agents crashed past the threshold. The bot itself failed — the PR has not been reviewed. Retry with care:

1. **Persist the failure for later diagnostic.** GitHub truncates `output.summary` at ~500 chars and `output.text` is usually `null`, so saving the full check-run metadata is the only way to have a record:
   ```bash
   mkdir -p ~/.claude/logs/pr-review-infra-errors
   gh api "repos/${REPO}/commits/${AUTO_BRANCH//\//%2F}/check-runs" \
     --jq '[.check_runs[] | select(.name | test("Claude"; "i"))] | last' \
     > "$HOME/.claude/logs/pr-review-infra-errors/$(date +%Y%m%d-%H%M%S)-${REPO##*/}-pr${PR_NUMBER}-attempt${ATTEMPT:-1}.json"
   ```
   Retain `html_url` from the JSON — it links to the browser-rendered log with the full traceback that the API hides.

2. **Wait at least 5 minutes** before retriggering. Back-to-back triggers against the same upstream hit the same rate-limit / worker-pool wall.
   ```bash
   sleep 300
   ```

3. **Re-run step 3a guards.** A failed check-run doesn't count as a review, so `LATEST_REVIEW_SHA != LATEST_SHA` still holds. Guard 1 (in_progress) may need to wait for the old check to release.

4. **Re-trigger:** `gh pr comment "$PR_NUMBER" --body "@claude review once"`.

5. **Poll (step 3c) and classify (step 3c.1) again.**

6. **Retry cap = 2 attempts total.** If `OUTCOME=INFRA_ERROR` after the second attempt, stop. Tell the user:

   > "Claude Code Review hit an infrastructure error on both attempts. Full check-run metadata saved to `~/.claude/logs/pr-review-infra-errors/`. The stderr traceback at [html_url] is the canonical source. Falling back to self-review of the diff."

   Then proceed as per the "Fallback" section.

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

## Fallback — self-review

Enter fallback when any of the following holds:

- `OUTCOME=SILENT_TIMEOUT` from step 3c.1 — 20 polls elapsed, check-run never transitioned to `completed`
- `OUTCOME=BILLING_SKIPPED` — bot explicitly returned a skip-with-body message (billing/quota/overage)
- `OUTCOME=BOT_COMMENT_ONLY` — bot posted an issue comment, no review object
- `OUTCOME=INFRA_ERROR` persists after the 2-attempt retry cap in step 3c.2

Protocol:

1. Read the diff: `gh pr diff "$PR_NUMBER"`
2. Provide your own assessment (clearly labelled as self-review in the conversation)
3. Post a PR comment explaining the fallback. Use the phrasing matched to the outcome:
   - `SILENT_TIMEOUT`: `"[Claude Code] Official review did not complete within 20 minutes. Self-review provided in conversation."`
   - `BILLING_SKIPPED`: `"[Claude Code] Review skipped — the bot reported: <first 200 chars of review body, which usually includes the remediation link>. Self-review provided in conversation."`
   - `BOT_COMMENT_ONLY`: `"[Claude Code] Review did not run (bot reported: <summary>). Self-review provided in conversation."`
   - `INFRA_ERROR` after retries: `"[Claude Code] Review hit infrastructure errors on 2 attempts. Metadata saved locally. Self-review provided in conversation."`
4. **Do NOT re-trigger** beyond what step 3c.2 already attempted — stops cascading cost.
5. Still wait for user approval before merging.

Common causes (per outcome):

- `SILENT_TIMEOUT` — Code Review disabled in org settings, no `CLAUDE.md` in repo root, Zero Data Retention enabled (incompatible), or bot simply not installed on the repo's org.
- `BILLING_SKIPPED` — the org's Claude Code credit balance / overage pool hit its cap. Note this is distinct from the general Claude.ai plan spend. Remediation is usually in `claude.ai/admin-settings/claude-code`: raise the Code Review-specific spend limit, top up credits, or enable auto-reload. A per-repo setting of `"After every push"` (visible on the same admin page) multiplies cost — switching to `Manual (@claude review)` avoids billing for every intermediate commit.
- `BOT_COMMENT_ONLY` — rare; bot posted an issue-level note without a review object. Inspect the comment body for the reason.
- `INFRA_ERROR` — upstream Anthropic issue: rate-limit cliff, shared sub-agent worker pool exhaustion, cache cascade. Often the billing cap teetering at the edge can surface as an infra error rather than a clean `BILLING_SKIPPED` — if you see `INFRA_ERROR` followed by `BILLING_SKIPPED` on retry, the original was most likely billing all along. Persistent `INFRA_ERROR` after 2 retries warrants an incident report to Anthropic using the saved metadata in `~/.claude/logs/pr-review-infra-errors/`.

## Anti-spam rules

1. **One trigger per push.** Never post another `@claude review once` until a review arrives, the current attempt is classified as `INFRA_ERROR`, OR new commits are pushed.
2. **Check before triggering.** Always run all three guards first.
3. **Retry only on classified infra error.** `SILENT_TIMEOUT` → fallback, do not re-trigger. `INFRA_ERROR` → up to 2 retries with a 5-minute gap between attempts per step 3c.2, then fallback. Never re-trigger on silence alone.
4. **Use `review once`.** Never bare `@claude review` — prevents cascading costs.
5. **Prefix automated comments** with `[Claude Code]` — **except** the trigger comment, which must start with `@claude` (no prefix).
6. **One decision comment per review cycle.**
7. **Space reviews on the same repo.** If any prior review (on any PR in this repo) completed within the last 5 minutes, wait out the remainder before triggering — see the concurrency note at the top of Option 3.

## Related tools

- **claude-code-action** (GitHub Action) — Anthropic's official Action for CI/CD. Supports structured output, fix links, comment classification.
- **REVIEW.md** — review-specific instructions, separate from CLAUDE.md.
- **Dispatch API** (emerging) — programmatic Claude Code execution for background review orchestration.
