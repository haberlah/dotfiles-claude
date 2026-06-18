#!/usr/bin/env python3
"""Classify GitHub PR review bot state for Codex and Claude."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import os
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY_PATH = SKILL_ROOT / "references" / "review-policy.json"
EXAMPLE_POLICY_PATH = SKILL_ROOT / "references" / "review-policy.example.json"
USER_POLICY_PATH = Path.home() / ".config" / "github-pr-review-policy" / "review-policy.json"

DEFAULT_POLICY: dict[str, Any] = {
    "reviewFlow": {
        "defaultProvider": "codex",
        "rerunProviderAfterFixes": "codex",
        "verifyGenericNoFindings": True,
    },
    "providers": {
        "codex": {
            "enabled": True,
            "trigger": "@codex review",
            "dedupeScope": "head",
            "allowTriggerSuffix": True,
            "botLoginPatterns": ["codex", "chatgpt", "openai"],
            "checkRunPatterns": ["codex", "chatgpt", "openai"],
        },
        "claude": {
            "enabled": False,
            "trigger": "@claude review once",
            "dedupeScope": "pr-once",
            "allowTriggerSuffix": False,
            "allowedRepos": [],
            "manualOnly": True,
            "firstCycleOnly": True,
            "botLoginPatterns": ["claude", "anthropic"],
            "checkRunPatterns": ["claude", "anthropic"],
        },
    },
    "skipTextPatterns": [
        "usage limit",
        "spend limit",
        "overage",
        "credits?",
        "quota",
        "skipp?ed",
        "disabled",
        "not enabled",
        "not configured",
        "not installed",
        "connect to github",
        "no access",
        "permission",
        "unauthori[sz]ed",
        "billing",
        "could not",
        "couldn't",
        "failed to",
        "error",
    ],
    "genericOkPatterns": [
        "\\blgtm\\b",
        "looks good",
        "thumbs?\\s*up",
        "no issues",
        "no major issues",
        "no findings",
        "did(?:n't| not) find any .*issues",
        "clean review",
        "nothing to flag",
        "approved",
        "all good",
        "no problems found",
    ],
}


def merge_dict(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_dict(merged[key], value)
        else:
            merged[key] = value
    return merged


def find_policy_path(path: str | None = None) -> Path | None:
    if path:
        return Path(path).expanduser()
    env_path = os.environ.get("PR_REVIEW_POLICY_PATH")
    if env_path:
        return Path(env_path).expanduser()
    if USER_POLICY_PATH.exists():
        return USER_POLICY_PATH
    if DEFAULT_POLICY_PATH.exists():
        return DEFAULT_POLICY_PATH
    if EXAMPLE_POLICY_PATH.exists():
        return EXAMPLE_POLICY_PATH
    return None


def load_policy(path: str | None = None) -> dict[str, Any]:
    policy_path = find_policy_path(path)
    if not policy_path:
        return DEFAULT_POLICY
    try:
        raw = json.loads(policy_path.read_text())
    except FileNotFoundError:
        raise SystemExit(json.dumps({"status": "policy_error", "error": f"Policy file not found: {policy_path}"}, indent=2))
    except json.JSONDecodeError as exc:
        raise SystemExit(json.dumps({"status": "policy_error", "error": f"Invalid JSON in {policy_path}: {exc}"}, indent=2))
    policy = merge_dict(DEFAULT_POLICY, raw)
    policy["_policyPath"] = str(policy_path)
    return policy


def configure_policy(policy: dict[str, Any]) -> None:
    global POLICY, PROVIDERS, REPOSITORIES, TRIGGER_TEXT, TRIGGER_RE, SKIP_RE, GENERIC_OK_RE
    POLICY = policy
    PROVIDERS = POLICY["providers"]
    REPOSITORIES = POLICY.get("repositories", {})
    TRIGGER_TEXT = {provider: cfg["trigger"] for provider, cfg in PROVIDERS.items()}
    TRIGGER_RE = {provider: trigger_re(provider) for provider in PROVIDERS}
    SKIP_RE = union_re(POLICY.get("skipTextPatterns", []))
    GENERIC_OK_RE = union_re(POLICY.get("genericOkPatterns", []))


POLICY: dict[str, Any] = {}
PROVIDERS: dict[str, dict[str, Any]] = {}
REPOSITORIES: dict[str, dict[str, Any]] = {}
TRIGGER_TEXT: dict[str, str] = {}
TRIGGER_RE: dict[str, re.Pattern[str]] = {}
SKIP_RE: re.Pattern[str]
GENERIC_OK_RE: re.Pattern[str]


def trigger_re(provider: str) -> re.Pattern[str]:
    trigger = re.escape(TRIGGER_TEXT[provider])
    suffix = r"\b" if PROVIDERS[provider].get("allowTriggerSuffix") else r"\s*$"
    return re.compile(r"^\s*" + trigger + suffix, re.I)


def union_re(patterns: list[str]) -> re.Pattern[str]:
    if not patterns:
        return re.compile(r"a\A")
    return re.compile(r"(" + "|".join(patterns) + r")", re.I)


configure_policy(load_policy())

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
        "head_ref": pr_obj.get("head", {}).get("ref"),
        "base_ref": pr_obj.get("base", {}).get("ref"),
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


def repo_policy(repo: str) -> dict[str, Any]:
    return REPOSITORIES.get(repo) or REPOSITORIES.get("*") or {}


def text_map_get(mapping: dict[str, Any], key: str | None) -> str | None:
    if not key:
        return None
    for candidate, message in mapping.items():
        if str(candidate).lower() == key.lower():
            return str(message)
    return None


def base_branch_guidance(state: dict[str, Any]) -> dict[str, Any]:
    cfg = repo_policy(state["repo"]).get("pullRequestBaseGuidance", {})
    base = state.get("base_ref")
    if not cfg:
        return {"status": "not_configured", "base_ref": base, "message": None, "severity": "none"}

    normal_bases = [str(branch) for branch in cfg.get("normalBases", [])]
    informational_bases = cfg.get("informationalBases", {})
    promotion_only_bases = cfg.get("promotionOnlyBases", {})

    if base and any(base.lower() == branch.lower() for branch in normal_bases):
        return {
            "status": "normal",
            "base_ref": base,
            "severity": "none",
            "message": cfg.get("normalMessage") or f"PR targets the normal base branch `{base}`.",
        }

    info_message = text_map_get(informational_bases, base)
    if info_message:
        return {
            "status": "informational",
            "base_ref": base,
            "severity": "info",
            "message": info_message,
        }

    promotion_message = text_map_get(promotion_only_bases, base)
    if promotion_message:
        return {
            "status": "promotion_only",
            "base_ref": base,
            "severity": "warning",
            "message": promotion_message,
        }

    return {
        "status": "nonstandard",
        "base_ref": base,
        "severity": "warning",
        "message": cfg.get("nonstandardMessage")
        or "PR targets a nonstandard base branch. Confirm this is intentional before treating it as the normal deployment path.",
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

    if not PROVIDERS["codex"].get("enabled", True):
        allow = False
        reasons.append("Codex review provider is disabled by policy")
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
        reasons.append(f"No current-head Codex review evidence found; trigger {TRIGGER_TEXT['codex']}")

    result = {
        "allow_trigger": allow,
        "bot": "codex",
        "base_branch_guidance": base_branch_guidance(state),
        "reasons": reasons,
        **classification,
    }
    if emit_comment_body and allow:
        result["comment_body"] = trigger_body("codex", state["head_sha"], "head")
    return result


def pre_claude(state: dict[str, Any], allow_retry: bool, emit_comment_body: bool, timeout_minutes: int = 30) -> dict[str, Any]:
    classification = classify_state(state, "claude", timeout_minutes)
    rel = relevant_items(state, "claude")
    reasons: list[str] = []
    allow = True

    allowed_repos = PROVIDERS["claude"].get("allowedRepos", [])
    if not PROVIDERS["claude"].get("enabled", False):
        allow = False
        reasons.append("Claude review provider is disabled by policy")
    if not allowed_repos:
        allow = False
        reasons.append("Claude review has no allowed repositories configured")
    if state["repo"] not in allowed_repos:
        allow = False
        configured = ", ".join(allowed_repos) if allowed_repos else "none"
        reasons.append(f"Claude review is limited to configured repositories: {configured}")
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
        reasons.append("Manual Claude first-cycle trigger is allowed only after an explicit user request")

    result = {
        "allow_trigger": allow,
        "bot": "claude",
        "base_branch_guidance": base_branch_guidance(state),
        "reasons": reasons,
        **classification,
    }
    if emit_comment_body and allow:
        result["comment_body"] = trigger_body("claude", state["head_sha"], "pr-once")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--policy",
        help="Path to review-policy.json. Defaults to PR_REVIEW_POLICY_PATH, then the skill references directory.",
    )
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

    sub.add_parser("policy")

    args = parser.parse_args()
    configure_policy(load_policy(args.policy))

    if args.command == "policy":
        result = {
            "status": "ok",
            "policy_path": POLICY.get("_policyPath"),
            "reviewFlow": POLICY.get("reviewFlow", {}),
            "providers": {
                name: {
                    "enabled": cfg.get("enabled", True),
                    "trigger": cfg.get("trigger"),
                    "dedupeScope": cfg.get("dedupeScope"),
                    "allowedRepos": cfg.get("allowedRepos", []),
                    "manualOnly": cfg.get("manualOnly", False),
                    "firstCycleOnly": cfg.get("firstCycleOnly", False),
                }
                for name, cfg in PROVIDERS.items()
            },
            "repositories": REPOSITORIES,
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

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
            "head_ref": state.get("head_ref"),
            "base_ref": state.get("base_ref"),
            "base_branch_guidance": base_branch_guidance(state),
            "counts": {
                "issue_comments": len(state["comments"]),
                "reviews": len(state["reviews"]),
                "inline_comments": len(state["review_comments"]),
                "check_runs": len(state["check_runs"]),
            },
        }
    else:
        trigger_seen = None
        if args.trigger_comment_id:
            trigger_seen = any(str(c.get("id")) == str(args.trigger_comment_id) for c in state["comments"])
        result = {
            "allow_trigger": False,
            "bot": args.bot,
            "base_branch_guidance": base_branch_guidance(state),
            "reasons": ["classification only"],
            "trigger_comment_id": args.trigger_comment_id,
            "trigger_comment_seen": trigger_seen,
            **classify_state(state, args.bot, args.timeout_minutes),
        }
        if args.trigger_comment_id and not trigger_seen:
            result["status"] = "trigger_comment_not_found"
            result["reasons"] = [f"Trigger comment {args.trigger_comment_id} was not found on this PR"]
        if args.trigger_head_sha and args.trigger_head_sha != state["head_sha"]:
            result["status"] = "head_changed_after_trigger"
            result["reasons"] = [f"Current head {state['head_sha']} differs from trigger head {args.trigger_head_sha}"]

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
