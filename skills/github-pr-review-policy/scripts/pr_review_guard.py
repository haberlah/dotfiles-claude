#!/usr/bin/env python3
"""Classify GitHub PR review bot state for Codex and Claude."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


DEFAULT_POLICY_PATH = Path(__file__).resolve().parents[1] / "references" / "review-policy.json"


def load_policy() -> dict[str, Any]:
    try:
        return json.loads(DEFAULT_POLICY_PATH.read_text())
    except FileNotFoundError:
        return {
            "providers": {
                "codex": {
                    "trigger": "@codex review",
                    "dedupeScope": "head",
                    "allowTriggerSuffix": True,
                    "botLoginPatterns": ["codex", "chatgpt", "openai"],
                    "checkRunPatterns": ["codex", "chatgpt", "openai"],
                },
                "claude": {
                    "trigger": "@claude review once",
                    "dedupeScope": "pr-once",
                    "allowTriggerSuffix": False,
                    "allowedRepos": ["Bella-Slainte/BellaAssist-MVP-2"],
                    "botLoginPatterns": ["claude", "anthropic"],
                    "checkRunPatterns": ["claude", "anthropic"],
                },
            }
        }


POLICY = load_policy()
PROVIDERS = POLICY["providers"]
TRIGGER_TEXT = {provider: cfg["trigger"] for provider, cfg in PROVIDERS.items()}


def trigger_re(provider: str) -> re.Pattern[str]:
    trigger = re.escape(TRIGGER_TEXT[provider])
    suffix = r"\b" if PROVIDERS[provider].get("allowTriggerSuffix") else r"\s*$"
    return re.compile(r"^\s*" + trigger + suffix, re.I)

TRIGGER_RE = {provider: trigger_re(provider) for provider in PROVIDERS}


def union_re(patterns: list[str]) -> re.Pattern[str]:
    if not patterns:
        return re.compile(r"a\A")
    return re.compile(r"(" + "|".join(patterns) + r")", re.I)


SKIP_RE = union_re(POLICY.get("skipTextPatterns", []))
GENERIC_OK_RE = union_re(POLICY.get("genericOkPatterns", []))

ERROR_RE = re.compile(r"(error|failed|failure|cancelled|timed out|timeout|neutral)", re.I)
MARKER_RE = re.compile(
    r"<!--\s*pr-review-guard\s+provider=(?P<provider>\w+)\s+head_sha=(?P<head>[0-9a-fA-F]+)\s+scope=(?P<scope>[\w-]+)",
    re.I,
)


def run_gh(path: str, *, paginate: bool = False) -> Any:
    cmd = ["gh", "api", path]
    if paginate:
        cmd.extend(["--paginate", "--slurp"])
    proc = subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(
            json.dumps(
                {
                    "status": "gh_error",
                    "allow_trigger": False,
                    "error": proc.stderr.strip() or proc.stdout.strip(),
                    "path": path,
                },
                indent=2,
            )
        )
    return json.loads(proc.stdout or "null")


def flatten_paginated(data: Any, *, object_array_key: str | None = None) -> list[dict[str, Any]]:
    if data is None:
        return []
    pages = data if isinstance(data, list) else [data]
    flattened: list[dict[str, Any]] = []
    for page in pages:
        if isinstance(page, list):
            flattened.extend(item for item in page if isinstance(item, dict))
        elif isinstance(page, dict) and object_array_key:
            flattened.extend(item for item in page.get(object_array_key, []) if isinstance(item, dict))
        elif isinstance(page, dict):
            flattened.append(page)
    return flattened


def run_gh_paginated_array(path: str) -> list[dict[str, Any]]:
    return flatten_paginated(run_gh(path, paginate=True))


def run_gh_paginated_object_array(path: str, key: str) -> list[dict[str, Any]]:
    return flatten_paginated(run_gh(path, paginate=True), object_array_key=key)


def iso_parse(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def item_time(item: dict[str, Any]) -> dt.datetime:
    for key in ("submitted_at", "created_at", "started_at", "completed_at", "updated_at"):
        parsed = iso_parse(item.get(key))
        if parsed:
            return parsed
    return dt.datetime.min.replace(tzinfo=dt.timezone.utc)


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def age_minutes(item: dict[str, Any] | None) -> float | None:
    if not item:
        return None
    timestamp = item_time(item)
    if timestamp == dt.datetime.min.replace(tzinfo=dt.timezone.utc):
        return None
    return max(0.0, (now_utc() - timestamp).total_seconds() / 60)


def user_login(item: dict[str, Any]) -> str:
    user = item.get("user") or {}
    return str(user.get("login") or "").lower()


def checkrun_text(item: dict[str, Any]) -> str:
    app = item.get("app") or {}
    output = item.get("output") or {}
    return " ".join(
        str(part or "")
        for part in (
            item.get("name"),
            app.get("slug"),
            app.get("name"),
            output.get("title"),
            output.get("summary"),
        )
    )


def body_text(item: dict[str, Any]) -> str:
    return str(item.get("body") or "")


def body_mentions_head(item: dict[str, Any], head_sha: str) -> bool:
    text = body_text(item).lower()
    head = head_sha.lower()
    return head in text or head[:10] in text or head[:8] in text or head[:7] in text


def marker_for(provider: str, head_sha: str, scope: str) -> str:
    return f"<!-- pr-review-guard provider={provider} head_sha={head_sha} scope={scope} -->"


def trigger_body(provider: str, head_sha: str, scope: str) -> str:
    return f"{TRIGGER_TEXT[provider]}\n\n{marker_for(provider, head_sha, scope)}"


def marker_matches(item: dict[str, Any], provider: str, head_sha: str | None = None) -> bool:
    match = MARKER_RE.search(body_text(item))
    if not match:
        return False
    if match.group("provider").lower() != provider:
        return False
    if head_sha and match.group("head").lower() != head_sha.lower():
        return False
    return True


def matches_bot(bot: str, item: dict[str, Any], *, check_run: bool = False) -> bool:
    text = checkrun_text(item).lower() if check_run else user_login(item)
    key = "checkRunPatterns" if check_run else "botLoginPatterns"
    return any(pattern.lower() in text for pattern in PROVIDERS[bot].get(key, []))


def repo_parts(repo: str) -> tuple[str, str]:
    if "/" not in repo:
        raise SystemExit("repo must be OWNER/NAME")
    owner, name = repo.split("/", 1)
    return owner, name


def load_state(repo: str, pr: int) -> dict[str, Any]:
    owner, name = repo_parts(repo)
    pr_obj = run_gh(f"/repos/{owner}/{name}/pulls/{pr}")
    head_sha = pr_obj.get("head", {}).get("sha")
    if not head_sha:
        raise SystemExit("could not determine PR head SHA")
    return {
        "repo": repo,
        "pr": pr,
        "head_sha": head_sha,
        "state": pr_obj.get("state"),
        "draft": bool(pr_obj.get("draft")),
        "comments": run_gh_paginated_array(f"/repos/{owner}/{name}/issues/{pr}/comments?per_page=100"),
        "reviews": run_gh_paginated_array(f"/repos/{owner}/{name}/pulls/{pr}/reviews?per_page=100"),
        "review_comments": run_gh_paginated_array(f"/repos/{owner}/{name}/pulls/{pr}/comments?per_page=100"),
        "check_runs": run_gh_paginated_object_array(
            f"/repos/{owner}/{name}/commits/{head_sha}/check-runs?per_page=100",
            "check_runs",
        ),
    }


def relevant_items(state: dict[str, Any], bot: str) -> dict[str, list[dict[str, Any]]]:
    head = state["head_sha"]
    bot_comments = [c for c in state["comments"] if matches_bot(bot, c)]
    reviews = [r for r in state["reviews"] if matches_bot(bot, r)]
    head_reviews = [r for r in reviews if r.get("commit_id") in (None, "", head)]
    inline = [c for c in state["review_comments"] if matches_bot(bot, c) and c.get("commit_id") in (None, "", head)]
    checks = [c for c in state["check_runs"] if matches_bot(bot, c, check_run=True)]
    triggers = [c for c in state["comments"] if TRIGGER_RE[bot].search(body_text(c))]
    markers = [c for c in state["comments"] if marker_matches(c, bot)]
    head_markers = [c for c in state["comments"] if marker_matches(c, bot, head)]
    return {
        "comments": bot_comments,
        "reviews": reviews,
        "head_reviews": head_reviews,
        "inline_comments": inline,
        "check_runs": checks,
        "triggers": triggers,
        "markers": markers,
        "head_markers": head_markers,
    }


def latest(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not items:
        return None
    return sorted(items, key=item_time)[-1]


def collect_text(items: list[dict[str, Any]], *, check_run: bool = False) -> str:
    if check_run:
        return "\n".join(checkrun_text(i) for i in items)
    return "\n".join(body_text(i) for i in items)


def classify_state(state: dict[str, Any], bot: str, timeout_minutes: int = 30) -> dict[str, Any]:
    rel = relevant_items(state, bot)
    latest_trigger = latest(rel["triggers"])
    trigger_age = age_minutes(latest_trigger)
    texts = "\n".join(
        [
            collect_text(rel["comments"]),
            collect_text(rel["reviews"]),
            collect_text(rel["check_runs"], check_run=True),
        ]
    )

    in_progress = [
        c for c in rel["check_runs"]
        if c.get("status") in {"queued", "in_progress", "waiting", "requested", "pending"}
    ]
    completed = [c for c in rel["check_runs"] if c.get("status") == "completed"]
    latest_check = latest(rel["check_runs"])
    latest_review = latest(rel["head_reviews"]) or latest(rel["reviews"])
    latest_comment = latest(rel["comments"])

    if in_progress:
        status = "in_progress"
    elif SKIP_RE.search(texts):
        status = "skipped"
    elif rel["inline_comments"]:
        status = "review_completed_findings"
    elif latest_check and latest_check.get("conclusion") in {"failure", "timed_out", "cancelled", "action_required"}:
        status = "infra_or_review_error"
    elif latest_check and ERROR_RE.search(checkrun_text(latest_check)) and latest_check.get("conclusion") in {"neutral", "failure", "cancelled"}:
        status = "infra_or_review_error"
    elif latest_review and GENERIC_OK_RE.search(body_text(latest_review)):
        if latest_check and latest_check.get("status") == "completed" and latest_check.get("conclusion") in {"success", "neutral", "skipped"}:
            status = "review_completed_no_findings"
        elif latest_review.get("commit_id") == state["head_sha"]:
            status = "review_completed_no_findings"
        else:
            status = "generic_unverified"
    elif latest_comment and GENERIC_OK_RE.search(body_text(latest_comment)):
        if latest_check and latest_check.get("status") == "completed" and latest_check.get("conclusion") in {"success", "neutral", "skipped"}:
            status = "review_completed_no_findings"
        elif body_mentions_head(latest_comment, state["head_sha"]):
            status = "review_completed_no_findings"
        else:
            status = "generic_unverified"
    elif rel["triggers"] and not (rel["head_reviews"] or rel["inline_comments"] or rel["comments"] or rel["check_runs"]):
        status = "in_progress" if trigger_age is not None and trigger_age < timeout_minutes else "silent_timeout"
    else:
        status = "no_review_evidence"

    return {
        "status": status,
        "head_sha": state["head_sha"],
        "counts": {
            "triggers": len(rel["triggers"]),
            "markers": len(rel["markers"]),
            "head_markers": len(rel["head_markers"]),
            "bot_comments": len(rel["comments"]),
            "bot_reviews": len(rel["reviews"]),
            "head_reviews": len(rel["head_reviews"]),
            "inline_comments": len(rel["inline_comments"]),
            "check_runs": len(rel["check_runs"]),
        },
        "latest": {
            "trigger_at": (latest_trigger or {}).get("created_at"),
            "trigger_age_minutes": round(trigger_age, 1) if trigger_age is not None else None,
            "timeout_minutes": timeout_minutes,
            "review_at": (latest_review or {}).get("submitted_at"),
            "review_commit": (latest_review or {}).get("commit_id"),
            "comment_at": (latest_comment or {}).get("created_at"),
            "check_name": (latest_check or {}).get("name"),
            "check_status": (latest_check or {}).get("status"),
            "check_conclusion": (latest_check or {}).get("conclusion"),
        },
    }


def pre_codex(state: dict[str, Any], emit_comment_body: bool, timeout_minutes: int = 30) -> dict[str, Any]:
    classification = classify_state(state, "codex", timeout_minutes)
    rel = relevant_items(state, "codex")
    reasons: list[str] = []
    allow = True

    if state["state"] != "open":
        allow = False
        reasons.append("PR is not open")
    if state["draft"]:
        allow = False
        reasons.append("PR is draft")
    if rel["head_markers"]:
        allow = False
        reasons.append("A Codex trigger marker already exists for the current head")
    if classification["status"] in {
        "in_progress",
        "review_completed_findings",
        "review_completed_no_findings",
        "generic_unverified",
    }:
        allow = False
        reasons.append(f"Codex status is {classification['status']} on current head or needs verification")

    if allow:
        reasons.append("No current-head Codex review evidence found; trigger @codex review")

    result = {"allow_trigger": allow, "bot": "codex", "reasons": reasons, **classification}
    if emit_comment_body and allow:
        result["comment_body"] = trigger_body("codex", state["head_sha"], "head")
    return result


def pre_claude(state: dict[str, Any], allow_retry: bool, emit_comment_body: bool, timeout_minutes: int = 30) -> dict[str, Any]:
    classification = classify_state(state, "claude", timeout_minutes)
    rel = relevant_items(state, "claude")
    reasons: list[str] = []
    allow = True

    allowed_repos = PROVIDERS["claude"].get("allowedRepos", [])
    if state["repo"] not in allowed_repos:
        allow = False
        reasons.append(f"Claude review is limited to {', '.join(allowed_repos)}")
    if state["state"] != "open":
        allow = False
        reasons.append("PR is not open")
    if state["draft"]:
        allow = False
        reasons.append("PR is draft")

    already_touched = (
        classification["counts"]["triggers"]
        or classification["counts"]["markers"]
        or classification["counts"]["bot_reviews"]
        or classification["counts"]["check_runs"]
    )
    retryable = allow_retry and classification["status"] == "infra_or_review_error"
    if already_touched and not retryable:
        allow = False
        reasons.append("Claude review cycle already exists; use Codex for subsequent review")
    if rel["markers"] and not retryable:
        allow = False
        reasons.append("A Claude trigger marker already exists on this PR")

    if allow:
        reasons.append("Manual Claude first-cycle trigger is allowed only if David explicitly requested it")

    result = {"allow_trigger": allow, "bot": "claude", "reasons": reasons, **classification}
    if emit_comment_body and allow:
        result["comment_body"] = trigger_body("claude", state["head_sha"], "pr-once")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    for name in ("pre-codex", "pre-claude"):
        p = sub.add_parser(name)
        p.add_argument("--repo", required=True)
        p.add_argument("--pr", required=True, type=int)
        p.add_argument("--emit-comment-body", action="store_true")
        p.add_argument("--timeout-minutes", type=int, default=30)
    sub.choices["pre-claude"].add_argument("--allow-infra-retry", action="store_true")

    c = sub.add_parser("classify")
    c.add_argument("--bot", required=True, choices=("codex", "claude"))
    c.add_argument("--repo", required=True)
    c.add_argument("--pr", required=True, type=int)
    c.add_argument("--trigger-comment-id")
    c.add_argument("--trigger-head-sha")
    c.add_argument("--timeout-minutes", type=int, default=30)

    s = sub.add_parser("snapshot")
    s.add_argument("--repo", required=True)
    s.add_argument("--pr", required=True, type=int)

    args = parser.parse_args()
    state = load_state(args.repo, args.pr)

    if args.command == "pre-codex":
        result = pre_codex(state, args.emit_comment_body, args.timeout_minutes)
    elif args.command == "pre-claude":
        result = pre_claude(state, args.allow_infra_retry, args.emit_comment_body, args.timeout_minutes)
    elif args.command == "snapshot":
        result = {
            "repo": state["repo"],
            "pr": state["pr"],
            "state": state["state"],
            "draft": state["draft"],
            "head_sha": state["head_sha"],
            "counts": {
                "issue_comments": len(state["comments"]),
                "reviews": len(state["reviews"]),
                "inline_comments": len(state["review_comments"]),
                "check_runs": len(state["check_runs"]),
            },
        }
    else:
        result = {
            "allow_trigger": False,
            "bot": args.bot,
            "reasons": ["classification only"],
            **classify_state(state, args.bot, args.timeout_minutes),
        }
        if args.trigger_head_sha and args.trigger_head_sha != state["head_sha"]:
            result["status"] = "head_changed_after_trigger"
            result["reasons"] = [f"Current head {state['head_sha']} differs from trigger head {args.trigger_head_sha}"]

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
