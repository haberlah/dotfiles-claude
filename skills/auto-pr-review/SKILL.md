---
name: auto-pr-review
description: Create a PR from the current branch, trigger Claude Code Review via the GitHub App, retrieve the review, and present it for approval. Use after completing any task that changes files in a project repo on main/master. Triggers on task completion when working in project repos — look for phrases like "done", "finished", "completed", "ready to review", or when you've made substantive file changes on main/master.
---

# Auto PR + Code Review

After completing work on a project repo (on main/master), run this workflow to create a PR, trigger an official Claude Code Review, and present the results.

## Prerequisites

- `gh` CLI authenticated
- Claude GitHub App installed on the repo's org (with Pull Requests read/write)
- Code Review enabled in the org's Claude Code settings (claude.ai → Organisation → Claude Code)
- Repo has a `CLAUDE.md` in root (required for Claude Code Review to activate)
- Overage spend limit set (claude.ai → Organisation → Usage)

## Workflow

### Step 1 — Commit and push

Stage and commit changed files with a descriptive message. Push to an `auto/YYYY-MM-DD` branch:

```bash
git add <files>
git commit -m "<descriptive message>"
git push --force-with-lease origin "HEAD:refs/heads/auto/$(date +%Y-%m-%d)"
```

Use `--force-with-lease` to handle re-pushes on the same day safely. If it fails with "stale info", use `--force` (the auto/ branch is ephemeral).

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

### Step 3 — Trigger Claude Code Review (with guards)

**Before triggering, check that a review is not already in progress.** Never post duplicate `@claude review` comments.

```bash
# Get the owner/repo from gh
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')

# Count existing reviews from claude[bot]
REVIEW_COUNT=$(gh api "repos/${REPO}/pulls/${PR_NUMBER}/reviews" \
  --jq '[.[] | select(.user.login == "claude[bot]")] | length' 2>/dev/null)

# Check if the last comment is already a @claude review trigger
LAST_COMMENT=$(gh api "repos/${REPO}/issues/${PR_NUMBER}/comments" \
  --jq '.[-1].body // ""' 2>/dev/null)
```

**Trigger rules:**
- If `LAST_COMMENT` contains `@claude` → a review was already requested. Do NOT post another. Wait for it.
- If there are existing `claude[bot]` reviews and you just pushed new commits → you may trigger ONE new review.
- Never trigger more than once between pushes. One push = one review request maximum.

When safe to trigger:

```bash
gh pr comment "$PR_NUMBER" --body "@claude review"
```

Record the trigger timestamp so you know what you're waiting for:

```bash
TRIGGER_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)
```

### Step 4 — Wait for the review (patient polling)

Claude Code Review can take **2-15 minutes** depending on PR size. Do NOT poll aggressively.

**Polling strategy:**
1. Wait 60 seconds before first check
2. Then check every 60 seconds
3. Maximum 10 attempts (10 minutes total)
4. Check BOTH the reviews endpoint and the comments endpoint

```bash
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')

for i in $(seq 1 10); do
  sleep 60

  # Check for new review from claude[bot] submitted after our trigger
  NEW_REVIEW=$(gh api "repos/${REPO}/pulls/${PR_NUMBER}/reviews" \
    --jq "[.[] | select(.user.login == \"claude[bot]\" and .submitted_at > \"${TRIGGER_TIME}\")] | last" 2>/dev/null)

  if [ -n "$NEW_REVIEW" ] && [ "$NEW_REVIEW" != "null" ]; then
    # Review arrived — fetch inline comments
    REVIEW_ID=$(echo "$NEW_REVIEW" | jq -r '.id')
    REVIEW_STATE=$(echo "$NEW_REVIEW" | jq -r '.state')
    REVIEW_BODY=$(echo "$NEW_REVIEW" | jq -r '.body')

    # Get inline comments for this review
    INLINE=$(gh api "repos/${REPO}/pulls/${PR_NUMBER}/reviews/${REVIEW_ID}/comments" \
      --jq '.[] | {path: .path, line: .line, body: .body}' 2>/dev/null)

    break
  fi

  # Also check for a billing/error comment from claude[bot]
  BOT_COMMENT=$(gh api "repos/${REPO}/issues/${PR_NUMBER}/comments" \
    --jq "[.[] | select(.user.login == \"claude[bot]\" and .created_at > \"${TRIGGER_TIME}\")] | last | .body // \"\"" 2>/dev/null)

  if [ -n "$BOT_COMMENT" ] && [ "$BOT_COMMENT" != "" ]; then
    # Bot responded with a comment (likely billing error or skip notice)
    echo "claude[bot] comment: $BOT_COMMENT"
    break
  fi
done
```

**If no review arrives after 10 minutes:** fall back to self-review (see Fallback section). Do NOT re-trigger `@claude review` — the App may still be processing.

### Step 5 — Present review and wait for decision

Show the review findings to the user:
- Number of findings and severity
- Each finding with its file path and explanation
- Recommendation (merge / needs changes)

**Ask the user for their decision.** They may:
- **Approve as-is** → proceed to merge
- **Request fixes** → they'll specify which findings to address and which to skip
- **Decline the review** → they'll explain why

### Step 6 — Post decision to PR (audit trail)

**This is critical.** The user's decision MUST be posted to the PR as a comment so the full reasoning is visible on GitHub to team members.

Before posting, confirm with the user: "I'll post this decision to the PR — OK?"

Format the comment as:

```markdown
**Review response** (via Claude Code)

**Findings addressed:**
- [Finding 1 summary] — fixed in commit abc1234

**Findings declined:**
- [Finding 2 summary] — [user's reason]

**Decision:** [Ready to merge / Pushing fixes]
```

Post via:
```bash
gh pr comment "$PR_NUMBER" --body "<decision comment>"
```

### Step 7 — Push fixes (if needed)

If the user requested fixes:
1. Make the changes
2. Commit with a message referencing the review
3. Push to the same auto/ branch: `git push --force-with-lease origin "HEAD:refs/heads/auto/$(date +%Y-%m-%d)"`
4. **Trigger ONE new review** (only if the user wants re-review — ask first)
5. Repeat from Step 4

### Step 8 — Merge (on user approval)

Only after explicit user approval:

```bash
gh pr merge "$PR_NUMBER" --merge --delete-branch
```

Use `--merge` (not `--squash`) to keep local and remote history aligned. After merge, sync local main:

```bash
git checkout main && git pull origin main
```

## Fallback — App review not available

If the Claude GitHub App doesn't respond within 10 minutes:

1. Read the diff: `gh pr diff "$PR_NUMBER"`
2. Provide your own assessment of the changes
3. Post a PR comment noting the official review timed out
4. Still wait for user approval before merging
5. **Do NOT re-trigger `@claude review`** — the App may still be processing in the background. If it completes later, the review will appear on GitHub.

Common reasons for no response:
- Overage spend limit not set or exhausted (check claude.ai → Organisation → Usage)
- Code Review not enabled (check claude.ai → Organisation → Claude Code)
- Repo not added to Code Review repos list
- No `CLAUDE.md` in repo root

## Anti-spam rules

These rules prevent the kind of comment spam that occurred during initial testing:

1. **One trigger per push.** After posting `@claude review`, do not post another until either (a) a review arrives or (b) you push new commits.
2. **Check before triggering.** Always check if the last PR comment is already `@claude review`. If so, wait — don't stack triggers.
3. **Never retry on silence.** If the App doesn't respond, it may be processing. Wait the full 10 minutes before falling back. Do not re-trigger.
4. **One decision comment per review cycle.** Post the user's decision once. Don't duplicate.
5. **Prefix automated comments.** All comments posted by this skill should be clearly marked as coming from Claude Code, not typed by the user on GitHub.

## Do not use this skill for

- **dotfiles-claude** — config repo pushes directly to main via the Stop hook
- **Feature branches** — push directly, no PR needed
- **Trivial changes** — when the user clearly wants a quick push without review
