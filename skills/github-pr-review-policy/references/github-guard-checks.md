# GitHub Guard Checks

The guard script is intentionally conservative. Its job is to prevent duplicate/cascading bot reviews and to distinguish real no-findings reviews from skipped or failed runs.

## Commands

```bash
python3 scripts/pr_review_guard.py pre-codex --repo OWNER/REPO --pr PR_NUMBER
python3 scripts/pr_review_guard.py pre-claude --repo OWNER/REPO --pr PR_NUMBER
python3 scripts/pr_review_guard.py pre-codex --repo OWNER/REPO --pr PR_NUMBER --emit-comment-body
python3 scripts/pr_review_guard.py pre-claude --repo OWNER/REPO --pr PR_NUMBER --emit-comment-body
python3 scripts/pr_review_guard.py classify --bot codex --repo OWNER/REPO --pr PR_NUMBER
python3 scripts/pr_review_guard.py classify --bot claude --repo OWNER/REPO --pr PR_NUMBER
python3 scripts/pr_review_guard.py classify --bot codex --repo OWNER/REPO --pr PR_NUMBER --timeout-minutes 45
python3 scripts/pr_review_guard.py snapshot --repo OWNER/REPO --pr PR_NUMBER
```

Each command prints JSON. Agents should read `allow_trigger`, `status`, and `reasons`.

When `--emit-comment-body` is set and triggering is allowed, the JSON includes the exact comment body to post. It includes a hidden marker:

```md
@codex review

<!-- pr-review-guard provider=codex head_sha=<sha> scope=head -->
```

The marker lets later checks correlate a generic/no-findings response to the exact provider and PR head. The script never posts comments itself.

## Data Sources

The script uses `gh api` for:

- `GET /repos/{owner}/{repo}/pulls/{number}` for PR head SHA/state/draft.
- `GET /repos/{owner}/{repo}/issues/{number}/comments` for trigger and bot issue comments.
- `GET /repos/{owner}/{repo}/pulls/{number}/reviews` for submitted review objects.
- `GET /repos/{owner}/{repo}/pulls/{number}/comments` for inline review comments.
- `GET /repos/{owner}/{repo}/commits/{head_sha}/check-runs` for bot check-runs on the current head.

## Classifications

- `review_completed_findings`: bot inline comments exist on the current head.
- `review_completed_no_findings`: current-head bot review/check-run evidence exists and the body indicates no findings. A bot issue comment that says it reviewed the current head SHA also counts.
- `in_progress`: relevant check-run is queued/in progress, or a trigger is newer than `--timeout-minutes` and no result has appeared yet.
- `skipped`: bot text says review was skipped, disabled, not configured, blocked by limits, or similar.
- `infra_or_review_error`: relevant check-run failed or completed with an error-like neutral result.
- `generic_unverified`: a generic positive/no-findings message exists, but there is no review/check-run evidence proving the bot actually reviewed the current head.
- `silent_timeout`: trigger exists but there is no bot review, bot result comment, or check-run evidence after `--timeout-minutes`.
- `no_review_evidence`: no matching trigger or bot evidence.

## Review Bot Matching

Bot identity is matched by login/check-run/app text:

- Codex: `codex`, `chatgpt`, `openai`.
- Claude: `claude`.

Keep these patterns narrow. If GitHub changes bot names, update the script and re-run validation on a known PR before trusting new classifications.
