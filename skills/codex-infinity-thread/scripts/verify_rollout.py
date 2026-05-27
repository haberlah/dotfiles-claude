#!/usr/bin/env python3
"""
verify_rollout.py - confirm a Codex rollout is safe to load and resume.

Run this before AND after repair_rollout.py. It checks the invariants that
decide whether the Codex desktop app will reload the session and whether the
next prompt will replay cleanly against the Responses API:

  * every line is valid JSON (the loader skips bad lines, but corruption is a
    smell worth surfacing)
  * at least one `session_meta` line carries an `id` - without it the loader
    fails with "failed to parse thread ID"
  * function_call / function_call_output pairing (a mismatch is usually
    self-healed by Codex's normalize_history, but large gaps are worth knowing)
  * no embedded images remain (they should be text after repair; a replayed
    image - even a 1x1 - can be rejected as "Invalid image in your last message")
  * the file is comfortably under V8's 536,870,888-byte single-string ceiling,
    which is what the desktop app's aggregate load hits

Exit code 0 if safe to load, 1 if not. Stdlib only.
"""

import argparse
import json
import os
import sys

V8_MAX_STRING = 536_870_888
SAFE_MARGIN_MB = 480     # warn if within margin of the ceiling


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if abs(n) < 1024 or unit == "GB":
            return f"{n:.1f}{unit}" if unit != "B" else f"{n}B"
        n /= 1024


def count_images(obj):
    c = 0
    if isinstance(obj, dict):
        t = obj.get("type")
        if t == "input_image":
            c += 1
        elif t == "image" and isinstance(obj.get("data"), str):
            c += 1
        for v in obj.values():
            c += count_images(v)
    elif isinstance(obj, list):
        for x in obj:
            c += count_images(x)
    return c


def main():
    ap = argparse.ArgumentParser(description="Verify a Codex rollout is safe to load/resume.")
    ap.add_argument("rollout", help="path to rollout-*.jsonl")
    ap.add_argument("--limit-mb", type=float, default=None,
                    help="size ceiling to check against in MB (default: V8 max string)")
    args = ap.parse_args()

    path = os.path.expanduser(args.rollout)
    if not os.path.isfile(path):
        print(f"error: not a file: {path}", file=sys.stderr)
        return 2

    ceiling = int(args.limit_mb * 1024 * 1024) if args.limit_mb else V8_MAX_STRING
    size = os.path.getsize(path)

    lines = bad = fc = fco = images = 0
    max_line = 0
    meta_id = None
    first_is_meta = False

    with open(path, encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f):
            max_line = max(max_line, len(line.encode("utf-8", "replace")))
            s = line.strip()
            if not s:
                continue
            lines += 1
            try:
                o = json.loads(s)
            except Exception:
                bad += 1
                continue
            t = o.get("type")
            if t == "session_meta" and meta_id is None:
                meta_id = (o.get("payload") or {}).get("id")
                first_is_meta = (i == 0)
            elif t == "response_item":
                p = o.get("payload") or {}
                pt = p.get("type")
                if pt == "function_call":
                    fc += 1
                elif pt == "function_call_output":
                    fco += 1
            images += count_images(o)

    checks = []
    checks.append(("valid JSON on every line", bad == 0, f"{bad} unparseable line(s)" if bad else f"{lines} lines OK"))
    checks.append(("session_meta id present", bool(meta_id), meta_id or "MISSING - loader will fail"))
    checks.append(("no embedded images remain", images == 0, f"{images} image part(s) remain" if images else "0"))
    checks.append(("under size ceiling", size < ceiling, f"{human(size)} / ceiling {human(ceiling)}"))

    # Pairing is informational: normalize_history self-heals it in release builds.
    pairing_ok = (fc == fco)

    print(f"File            : {path}")
    print(f"Size            : {human(size)}  (V8 ceiling {human(V8_MAX_STRING)})")
    print(f"Lines           : {lines}  (max line {human(max_line)})")
    print(f"session_meta id : {meta_id}  (first line: {first_is_meta})")
    print(f"function_call / function_call_output : {fc} / {fco}  ({'matched' if pairing_ok else 'mismatch - normalize_history will reconcile on load'})")
    print()
    ok = True
    for name, passed, detail in checks:
        mark = "PASS" if passed else "FAIL"
        if not passed:
            ok = False
        print(f"  [{mark}] {name}: {detail}")

    if ok and size > SAFE_MARGIN_MB * 1024 * 1024:
        print(f"\n  note: under the ceiling but large ({human(size)}); consider a lower --target-mb when repairing for more margin.")

    print()
    print("VERDICT:", "safe to load" if ok else "NOT safe - address the FAIL(s) above")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
