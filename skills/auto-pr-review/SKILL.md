---
name: auto-pr-review
description: Create a PR from the current branch, trigger Claude Code Review via the GitHub App, retrieve the review, and present it for approval. Use after completing any task that changes files in a project repo on main/master. Triggers on task completion when working in project repos — look for phrases like "done", "finished", "completed", "ready to review", or when you've made substantive file changes on main/master.
---

# Auto PR + Code Review

After completing work on a project repo (on main/master), run this workflow to create a PR, trigger an official Claude Code Review, and present the results for approval — all within the current conversation.

## Prerequisites

- `gh` CLI authenticated
- Claude GitHub App installed on the repo's org (with Pull Requests read/write)
- Code Review enabled: claude.ai → Organisation settings → Claude Code → Code Review (toggle on)
- Review behaviour set to **Manual (@claude review)** for each repo
- Overage spend limit set: claude.ai → Organisation settings → Usage
- Repo has a `CLAUDE.md` in root (required for the App to activate)
- Optional: `REVIEW.md` in repo root for review-specific instructions (separate from CLAUDE.md project context)

## Cost awareness

Each Claude Code Review costs approximately **A$15-25** depending on PR size. The review runs multi-agent analysis (correctness, security, code quality) with a verification step that filters false positives (<1% false positive rate). Avoid duplicate triggers — every `@claude review once` comment costs real money.

## Workflow

### Step 1 — Commit and push

Stage and commit changed files with a descriptive message. Push to an `auto/YYYY-MM-DD` branch:

```bash
git add <files>
git commit -m "<descriptive message>"
git push --force-with-lease origin "HEAD:refs/heads/auto/$(date +%Y-%m-%d)"
```

If `--force-with-lease` fails with "stale info", use `--force` (auto/ branches are ephemeral).

### Step 2 — Create or detect PR

Check for an existing open PR on today's auto branch. Create one if none exists:

```bash
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')
AUTO_BRANCH="auto/$(date +%Y-%m-%d)"
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

### Step 3 — Trigger Claude Code Review (with guards)

**Before triggering, run all three checks.** Never post a duplicate trigger.

```bash
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')

# Check 1: Is a review already in progress? (check runs)
IN_PROGRESS=$(gh api "repos/${REPO}/commits/auto%2F$(date +%Y-%m-%d)/check-runs" \
  --jq '[.check_runs[] | select(.name | test("Claude"; "i")) | select(.status == "in_progress")] | length' 2>/dev/null)

# Check 2: Was the last comment already a trigger?
LAST_COMMENT=$(gh api "repos/${REPO}/issues/${PR_NUMBER}/comments" \
  --jq '.[-1].body // ""' 2>/dev/null)

# Check 3: Has claude[bot] already reviewed the latest commit?
LATEST_SHA=$(git rev-parse HEAD)
LATEST_REVIEW_SHA=$(gh api "repos/${REPO}/pulls/${PR_NUMBER}/reviews" \
  --jq '[.[] | select(.user.login == "claude[bot]")] | last | .commit_id // ""' 2>/dev/null)
```

**Trigger rules — ALL must pass:**
- `IN_PROGRESS` must be 0 (no review currently running)
- `LAST_COMMENT` must NOT contain `@claude` (no pending trigger)
- `LATEST_REVIEW_SHA` must NOT equal `LATEST_SHA` (latest commit not yet reviewed)

If all checks pass, trigger **exactly one** review:

```bash
gh pr comment "$PR_NUMBER" --body "[Claude Code] @claude review once"
TRIGGER_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)
```

**Use `@claude review once`** — not `@claude review`. The `once` variant prevents the PR from being subscribed to automatic push-triggered reviews, which avoids cascading review costs when fix commits are pushed.

**Prefix with `[Claude Code]`** to distinguish automated triggers from manual ones on GitHub.

If any check fails, inform the user:
- Review in progress → "A review is already running. Waiting for it to complete."
- Trigger pending → "A review was already requested. Waiting for the response."
- Already reviewed this commit → "This commit has already been reviewed. Push new changes first."

### Step 4 — Wait for the review (patient polling)

Claude Code Review takes **5-20 minutes** depending on PR size. Do NOT poll aggressively.

**Primary method: poll check runs** (more reliable than polling comments):

```bash
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')
BRANCH_ENCODED=$(echo "auto/$(date +%Y-%m-%d)" | sed 's|/|%2F|g')

for i in $(seq 1 20); do
  sleep 60

  # Check for completed Claude review check run
  CHECK=$(gh api "repos/${REPO}/commits/${BRANCH_ENCODED}/check-runs" \
    --jq '[.check_runs[] | select(.name | test("Claude"; "i")) | select(.status == "completed")] | last' 2>/dev/null)

  if [ -n "$CHECK" ] && [ "$CHECK" != "null" ]; then
    echo "Review complete"
    break
  fi
done
```

**Secondary method: poll reviews endpoint** (for inline findings):

```bash
NEW_REVIEW=$(gh api "repos/${REPO}/pulls/${PR_NUMBER}/reviews" \
  --jq "[.[] | select(.user.login == \"claude[bot]\" and .submitted_at > \"${TRIGGER_TIME}\")] | last" 2>/dev/null)
```

**Polling schedule:** wait 60s before first check, then every 60s, maximum 20 attempts (20 minutes). If no review after 20 minutes, fall back (see Fallback section). Do NOT re-trigger.

### Step 5 — Retrieve and present findings

Once the review lands, fetch the inline comments:

```bash
REVIEW_ID=$(echo "$NEW_REVIEW" | jq -r '.id')
gh api "repos/${REPO}/pulls/${PR_NUMBER}/reviews/${REVIEW_ID}/comments" \
  --jq '.[] | {path: .path, line: .line, body: .body}'
```

**Parse severity markers** when presenting to the user:
- **🔴 Important** — bugs that should be fixed before merging
- **🟡 Nit** — minor issues, worth fixing but not blocking
- **🟣 Pre-existing** — bugs in the codebase but not introduced by this PR

Present findings grouped by severity, with file paths and explanations. Collapse the extended reasoning sections (in `<details>` tags) into a short summary unless the user asks for detail.

**If the review found no issues**, it posts a short confirmation. Present this as "Clean review — no issues found."

**If the review was skipped** (billing error), inform the user and suggest checking claude.ai → Organisation → Usage.

### Step 6 — Get user decision

Ask the user for their decision on each finding:
- **Fix** — will address this finding
- **Skip** — decline with a reason
- **Discuss** — need more context before deciding

### Step 7 — Post decision to PR (audit trail)

**This is critical for team visibility.** The user's decision MUST be posted to the PR so team members can see the reasoning on GitHub.

Before posting, confirm: "I'll post this decision to the PR — OK?"

Format:

```markdown
**Review response** (via Claude Code)

**Findings addressed:**
- [Summary] — fixed in commit [sha]

**Findings declined:**
- [Summary] — [user's reason]

**Decision:** [Ready to merge / Pushing fixes]
```

Post via:
```bash
gh pr comment "$PR_NUMBER" --body "<decision comment>"
```

### Step 8 — Push fixes (if needed)

If the user requested fixes:
1. Make the changes
2. Commit referencing the review finding
3. Push to the same auto/ branch
4. **Ask the user** if they want a re-review before triggering. Re-reviews cost another $15-25.
5. If yes, run Step 3 again (guards will pass since new commits were pushed)
6. If no, proceed to merge

### Step 9 — Merge (on user approval)

Only after explicit user approval:

```bash
gh pr merge "$PR_NUMBER" --merge --delete-branch
git checkout main && git pull origin main
```

Use `--merge` (not `--squash`) to keep local and remote history aligned.

## Fallback — review timeout

If the Claude GitHub App doesn't respond within 20 minutes:

1. Read the diff: `gh pr diff "$PR_NUMBER"`
2. Provide your own assessment (clearly labelled as self-review, not official)
3. Post a PR comment: `"[Claude Code] Official review timed out after 20 minutes. Self-review provided in conversation."`
4. **Do NOT re-trigger `@claude review once`** — the App may still be processing. If it completes later, the review will appear on GitHub.
5. Still wait for user approval before merging

Common causes:
- Overage spend limit exhausted (claude.ai → Organisation → Usage)
- Code Review not enabled (claude.ai → Organisation → Claude Code)
- No `CLAUDE.md` in repo root
- Organisation has Zero Data Retention enabled (incompatible with Code Review)

## Anti-spam rules

These rules prevent duplicate triggers that waste review credits ($15-25 each):

1. **One trigger per push.** After posting `@claude review once`, do not post another until (a) a review arrives OR (b) new commits are pushed.
2. **Check before triggering.** Always run all three guards (check runs, last comment, review SHA) before posting.
3. **Never retry on silence.** If the App doesn't respond within 20 min, fall back. Do not re-trigger.
4. **Use `review once`.** Never use bare `@claude review` — it subscribes the PR to automatic push-triggered reviews, causing cascading costs.
5. **Prefix automated comments.** All comments from this skill start with `[Claude Code]` to distinguish from manual GitHub comments.
6. **One decision comment per review cycle.** Post the user's decision once per review round.

## Do not use this skill for

- **dotfiles-claude** — config repo pushes directly to main via the Stop hook
- **Feature branches** — push directly, no PR needed
- **Trivial changes** — when the user clearly wants a quick push without review (use judgement)
- **Orgs with Zero Data Retention** — Code Review is incompatible with ZDR

## Related tools

- **claude-code-action** (GitHub Action) — Anthropic's official Action for CI/CD integration. Supports structured JSON output, fix links, and comment classification. Use for fully automated CI pipelines.
- **REVIEW.md** — place review-specific instructions here (separate from CLAUDE.md). The App reads both.
- **Dispatch API** (emerging) — programmatic Claude Code execution without interactive sessions. Future direction for background review orchestration.
