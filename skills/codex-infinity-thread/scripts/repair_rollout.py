#!/usr/bin/env python3
"""
repair_rollout.py - slim an oversized OpenAI Codex session rollout so the Codex
desktop app can reload it.

The Codex desktop app loads a session by aggregating its entire JSONL rollout
into a single in-memory string. Node/V8 caps a string at 536,870,888 bytes
(~512 MB); past that the main process throws "RangeError: Invalid string length"
and the app crashes on launch. This script shrinks the rollout below that limit
while preserving as much resumable context as possible.

It applies operations in LEAST-LOSSY-FIRST order, stopping as soon as the file
is under the target size:

  1. drop-compacted   Keep only the newest `compacted` checkpoint. Codex resumes
                      from the newest one and treats it as superseding everything
                      older, so earlier checkpoints are dead weight. Zero context
                      loss.
  2. images-to-text   Replace every embedded screenshot with a short text marker.
                      Images are the usual cause of the bloat (the computer-use
                      tool stores one per action, often twice). The model does
                      not need stale screenshots to continue. IMPORTANT: the
                      replacement is TEXT, never a tiny placeholder image - the
                      Responses API rejects sub-minimum-dimension images when the
                      history is replayed ("Invalid image in your last message").
  3. truncate-output  Trim oversized text tool outputs to head+tail with an
                      elision marker. Loses the middle of large outputs only.
  4. truncate-turns   Last resort: keep the session header plus the most recent
                      turns, cutting on a user-message boundary (never mid-turn,
                      which would orphan a reasoning item and 400 the API).
                      Drops early conversation context.

The first `session_meta` line is always preserved (without it the loader fails
with "failed to parse thread ID"). The original is archived before any change,
and the swap is atomic, so the operation is fully reversible.

Stdlib only. See SKILL.md and references/rollout-format.md for the rationale.
"""

import argparse
import json
import os
import re
import shutil
import sys
import tempfile

V8_MAX_STRING = 536_870_888          # bytes; the hard ceiling the desktop app hits
DEFAULT_TARGET_MB = 400              # leave generous margin under the ceiling
IMG_PLACEHOLDER = "[image removed to reduce session size]"
DATA_URI_RE = re.compile(r"data:image/[A-Za-z0-9.+\-]+;base64,[A-Za-z0-9+/=]+")
TEXT_TRUNCATE_THRESHOLD = 32_768     # only trim text fields larger than this
TEXT_TRUNCATE_KEEP = 4_000           # bytes kept at each of head and tail


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if abs(n) < 1024 or unit == "GB":
            return f"{n:.1f}{unit}" if unit != "B" else f"{n}B"
        n /= 1024


def dump(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


# ---------------------------------------------------------------------------
# Metadata pre-scan (streaming; keeps only small facts, never the whole file)
# ---------------------------------------------------------------------------
def scan(path):
    info = {
        "lines": 0, "bad_json": 0, "bytes": os.path.getsize(path),
        "meta_id": None, "first_is_meta": False,
        "last_compacted": -1, "compacted_count": 0,
        "user_msg_lines": [],          # 0-based line indices of user-message turn starts
        "line_bytes": [],              # byte length per line (for turn-cut math)
    }
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f):
            info["line_bytes"].append(len(line.encode("utf-8", "replace")))
            s = line.strip()
            if not s:
                continue
            info["lines"] += 1
            try:
                o = json.loads(s)
            except Exception:
                info["bad_json"] += 1
                continue
            t = o.get("type")
            if t == "session_meta":
                if info["meta_id"] is None:
                    info["meta_id"] = (o.get("payload") or {}).get("id")
                    info["first_is_meta"] = (i == 0)
            elif t == "compacted":
                info["last_compacted"] = i
                info["compacted_count"] += 1
            elif t == "response_item":
                p = o.get("payload") or {}
                if p.get("type") == "message" and p.get("role") == "user":
                    info["user_msg_lines"].append(i)
    return info


# ---------------------------------------------------------------------------
# Operation 1: drop superseded compacted checkpoints
# ---------------------------------------------------------------------------
def op_drop_compacted(src, dst, info):
    last = info["last_compacted"]
    if last < 0 or info["compacted_count"] <= 1:
        return False
    removed = 0
    with open(src, encoding="utf-8", errors="replace") as fin, \
         open(dst, "w", encoding="utf-8") as fout:
        for i, line in enumerate(fin):
            s = line.strip()
            if s and '"compacted"' in line:
                try:
                    if json.loads(s).get("type") == "compacted" and i != last:
                        removed += 1
                        continue
                except Exception:
                    pass
            fout.write(line)
    return removed > 0


# ---------------------------------------------------------------------------
# Operation 2: replace every image with a text placeholder
# ---------------------------------------------------------------------------
def _scrub_images(obj):
    if isinstance(obj, dict):
        t = obj.get("type")
        if t == "input_image":
            return {"type": "input_text", "text": IMG_PLACEHOLDER}
        if t == "image" and isinstance(obj.get("data"), str):
            return {"type": "text", "text": IMG_PLACEHOLDER}
        out = {}
        for k, v in obj.items():
            if k == "images" and isinstance(v, list) and any(
                isinstance(x, str) and x.startswith("data:image") for x in v
            ):
                out[k] = []
            else:
                out[k] = _scrub_images(v)
        return out
    if isinstance(obj, list):
        return [_scrub_images(x) for x in obj]
    if isinstance(obj, str):
        return DATA_URI_RE.sub(IMG_PLACEHOLDER, obj) if ";base64," in obj else obj
    return obj


def op_images_to_text(src, dst, info):
    triggers = ('"input_image"', '"type":"image"', '"images":', '"image_url"', ";base64,")
    changed = False
    with open(src, encoding="utf-8", errors="replace") as fin, \
         open(dst, "w", encoding="utf-8") as fout:
        for line in fin:
            if not any(t in line for t in triggers):
                fout.write(line)
                continue
            s = line.strip()
            try:
                o = json.loads(s)
            except Exception:
                fout.write(line)
                continue
            scrubbed = _scrub_images(o)
            fout.write(dump(scrubbed) + "\n")
            changed = True
    return changed


# ---------------------------------------------------------------------------
# Operation 3: truncate oversized text tool outputs (head + tail)
# ---------------------------------------------------------------------------
def _truncate_text(s):
    raw = s.encode("utf-8", "replace")
    if len(raw) <= TEXT_TRUNCATE_THRESHOLD:
        return s, False
    head = raw[:TEXT_TRUNCATE_KEEP].decode("utf-8", "ignore")
    tail = raw[-TEXT_TRUNCATE_KEEP:].decode("utf-8", "ignore")
    elided = len(raw) - 2 * TEXT_TRUNCATE_KEEP
    return f"{head}\n...[{elided} bytes elided to reduce session size]...\n{tail}", True


def _truncate_outputs(obj):
    changed = False
    if isinstance(obj, dict):
        if obj.get("type") in ("input_text", "text") and isinstance(obj.get("text"), str):
            new, did = _truncate_text(obj["text"])
            if did:
                obj = dict(obj)
                obj["text"] = new
                return obj, True
        out = {}
        for k, v in obj.items():
            if k == "output" and isinstance(v, str):
                new, did = _truncate_text(v)
                out[k] = new
                changed = changed or did
            else:
                nv, did = _truncate_outputs(v)
                out[k] = nv
                changed = changed or did
        return out, changed
    if isinstance(obj, list):
        res = []
        for x in obj:
            nx, did = _truncate_outputs(x)
            res.append(nx)
            changed = changed or did
        return res, changed
    return obj, False


def op_truncate_outputs(src, dst, info):
    changed = False
    with open(src, encoding="utf-8", errors="replace") as fin, \
         open(dst, "w", encoding="utf-8") as fout:
        for line in fin:
            s = line.strip()
            if not s or '"function_call_output"' not in line and '"custom_tool_call_output"' not in line:
                fout.write(line)
                continue
            try:
                o = json.loads(s)
            except Exception:
                fout.write(line)
                continue
            new, did = _truncate_outputs(o)
            fout.write(dump(new) + "\n")
            changed = changed or did
    return changed


# ---------------------------------------------------------------------------
# Operation 4 (last resort): keep header + most recent turns
# ---------------------------------------------------------------------------
def op_truncate_turns(src, dst, info, target_bytes):
    boundaries = info["user_msg_lines"]
    line_bytes = info["line_bytes"]
    if not boundaries:
        return False
    # Header = everything up to and including the first session_meta line, plus
    # the standing preamble that immediately follows it (kept verbatim).
    header_end = 0
    for i, b in enumerate(line_bytes):
        header_end = i
        if i >= 4:
            break
    header_bytes = sum(line_bytes[: header_end + 1])
    # Find the earliest user-message boundary whose kept tail fits the target.
    total = sum(line_bytes)
    cut = None
    for c in boundaries:
        if c <= header_end:
            continue
        kept = header_bytes + (total - sum(line_bytes[:c]))
        if kept <= target_bytes:
            cut = c
            break
    if cut is None:
        return False
    with open(src, encoding="utf-8", errors="replace") as fin, \
         open(dst, "w", encoding="utf-8") as fout:
        for i, line in enumerate(fin):
            if i <= header_end or i >= cut:
                fout.write(line)
    return True


OPS = [
    ("drop-compacted", op_drop_compacted, "drop superseded compacted checkpoints"),
    ("images-to-text", op_images_to_text, "replace embedded images with text markers"),
    ("truncate-output", op_truncate_outputs, "trim oversized text tool outputs"),
    ("truncate-turns", None, "keep header + most recent turns (last resort)"),
]


def find_oversized(target_bytes):
    base = os.path.expanduser("~/.codex/sessions")
    hits = []
    for root, _, files in os.walk(base):
        for fn in files:
            if fn.endswith(".jsonl"):
                p = os.path.join(root, fn)
                try:
                    sz = os.path.getsize(p)
                except OSError:
                    continue
                if sz > target_bytes:
                    hits.append((sz, p))
    return sorted(hits, reverse=True)


def main():
    ap = argparse.ArgumentParser(description="Slim an oversized Codex rollout so the desktop app can reload it.")
    ap.add_argument("rollout", nargs="?", help="path to rollout-*.jsonl (omit with --auto)")
    ap.add_argument("--auto", action="store_true", help="scan ~/.codex/sessions for oversized rollouts")
    ap.add_argument("--target-mb", type=float, default=DEFAULT_TARGET_MB, help=f"target max size in MB (default {DEFAULT_TARGET_MB})")
    ap.add_argument("--dry-run", action="store_true", help="report what would happen; do not modify anything")
    ap.add_argument("--backup-dir", default=None, help="where to archive the original (default: alongside the file)")
    ap.add_argument("--keep-images", action="store_true", help="skip the images-to-text step")
    args = ap.parse_args()

    target_bytes = int(args.target_mb * 1024 * 1024)
    if target_bytes >= V8_MAX_STRING:
        print(f"warning: target {human(target_bytes)} is above the V8 ceiling {human(V8_MAX_STRING)}; lower --target-mb", file=sys.stderr)

    if args.auto:
        hits = find_oversized(target_bytes)
        if not hits:
            print(f"No rollouts over {args.target_mb} MB under ~/.codex/sessions.")
            return 0
        print("Oversized rollouts (largest first):")
        for sz, p in hits:
            print(f"  {human(sz):>10}  {p}")
        path = hits[0][1]
        print(f"\nSelecting the largest: {path}\n")
    elif args.rollout:
        path = os.path.expanduser(args.rollout)
    else:
        ap.error("provide a rollout path or use --auto")

    if not os.path.isfile(path):
        print(f"error: not a file: {path}", file=sys.stderr)
        return 2

    start = os.path.getsize(path)
    print(f"Rollout : {path}")
    print(f"Size    : {human(start)}  (target {human(target_bytes)}, V8 ceiling {human(V8_MAX_STRING)})")
    if start <= target_bytes:
        print("Already under target - nothing to do.")
        return 0

    workdir = os.path.dirname(os.path.abspath(path))
    tmpfiles = []

    def new_tmp():
        fd, p = tempfile.mkstemp(suffix=".jsonl.tmp", dir=workdir)
        os.close(fd)
        tmpfiles.append(p)
        return p

    cur = path
    applied = []
    keep_image_step = args.keep_images
    for name, fn, desc in OPS:
        if os.path.getsize(cur) <= target_bytes:
            break
        if name == "images-to-text" and keep_image_step:
            continue
        info = scan(cur)
        out = new_tmp()
        if name == "truncate-turns":
            did = op_truncate_turns(cur, out, info, target_bytes)
        else:
            did = fn(cur, out, info)
        if not did:
            os.remove(out)
            tmpfiles.remove(out)
            continue
        size_after = os.path.getsize(out)
        print(f"  - {name:16} {desc}: {human(os.path.getsize(cur))} -> {human(size_after)}")
        applied.append(name)
        cur = out

    final = os.path.getsize(cur)
    print(f"\nResult  : {human(start)} -> {human(final)}  (applied: {', '.join(applied) or 'none'})")

    if final > target_bytes:
        print(f"warning: still above target {human(target_bytes)} after all operations.", file=sys.stderr)
    if final >= V8_MAX_STRING:
        print(f"ERROR: still above the V8 ceiling - the app will still crash. Inspect manually.", file=sys.stderr)

    if args.dry_run:
        print("\n[dry-run] no files modified. Re-run without --dry-run to apply.")
        for p in tmpfiles:
            os.remove(p)
        return 0

    if cur == path:
        print("No operations changed the file.")
        return 0

    # Archive the original, then atomically swap the slimmed file into place.
    backup_dir = os.path.expanduser(args.backup_dir) if args.backup_dir else os.path.join(workdir)
    os.makedirs(backup_dir, exist_ok=True)
    backup = os.path.join(backup_dir, os.path.basename(path) + ".orig")
    n = 1
    while os.path.exists(backup):
        backup = os.path.join(backup_dir, os.path.basename(path) + f".orig.{n}")
        n += 1
    shutil.copy2(path, backup)
    os.replace(cur, path)
    tmpfiles.remove(cur)
    for p in tmpfiles:
        try:
            os.remove(p)
        except OSError:
            pass

    print(f"\nArchived original -> {backup}")
    print(f"Slimmed file in place -> {path}")
    print("\nNext: run verify_rollout.py on it, then FORCE-QUIT and relaunch Codex,")
    print("reopen the session, and send a test prompt to confirm it replays.")
    print(f"To undo: mv '{backup}' '{path}'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
