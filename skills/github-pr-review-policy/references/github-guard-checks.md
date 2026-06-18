# GitHub Guard Checks

The guard script is intentionally conservative. Its job is to prevent duplicate or cascading bot reviews and to distinguish real no-findings reviews from skipped, failed, stale, or unverified runs.

## Commands

```bash
python3 scripts/pr_review_guard.py policy
python3 scripts/pr_review_guard.py snapshot --repo OWNER/REPO --pr PR_NUMBER
python3 scripts/pr_review_guard.py pre-codex --repo OWNER/REPO --pr PR_NUMBER
python3 scripts/pr_review_guard.py pre-claude --repo OWNER/REPO --pr PR_NUMBER
python3 scripts/pr_review_guard.py pre-codex --repo OWNER/REPO --pr PR_NUMBER --emit-comment-body
python3 scripts/pr_review_guard.py pre-claude --repo OWNER/REPO --pr PR_NUMBER --emit-comment-body
python3 scripts/pr_review_guard.py classify --bot codex --repo OWNER/REPO --pr PR_NUMBER
python3 scripts/pr_review_guard.py classify --bot claude --repo OWNER/REPO --pr PR_NUMBER
python3 scripts/pr_review_guard.py classify --bot codex --repo OWNER/REPO --pr PR_NUMBER --timeout-minutes 45
```

Pass `--policy /path/to/review-policy.json` before the subcommand, or set `PR_REVIEW_POLICY_PATH`.

## Trigger Markers

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

List endpoints are paginated.

## Classifications

- `review_completed_findings`: bot inline comments exist on the current head.
- `review_completed_no_findings`: current-head bot review/check-run evidence exists and the body indicates no findings. A bot issue comment that says it reviewed the current head SHA also counts.
- `in_progress`: relevant check-run is queued/in progress, or a trigger is newer than `--timeout-minutes` and no result has appeared yet.
- `skipped`: bot text says review was skipped, disabled, not configured, blocked by limits, or similar.
- `infra_or_review_error`: relevant check-run failed or completed with an error-like neutral result.
- `generic_unverified`: a generic positive/no-findings message exists, but there is no review/check-run/head-SHA evidence proving the bot actually reviewed the current head.
- `silent_timeout`: trigger exists but there is no bot review, bot result comment, or check-run evidence after `--timeout-minutes`.
- `trigger_comment_not_found`: `--trigger-comment-id` was provided but no matching issue comment exists.
- `head_changed_after_trigger`: `--trigger-head-sha` differs from the current PR head.
- `no_review_evidence`: no matching trigger or bot evidence.

## Bot Matching

Bot identity is matched by login/check-run/app text configured in `review-policy.json`:

- Codex default: `codex`, `chatgpt`, `openai`.
- Claude default: `claude`, `anthropic`.

Keep these patterns narrow. If bot names change, update policy and validate on a known PR before trusting classifications.
