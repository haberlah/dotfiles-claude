---
name: codex-infinity-thread
description: >-
  Keep long Codex conversations alive: repair an oversized session that crashes the Codex
  desktop app with "RangeError: Invalid string length" or won't open a
  conversation. Use whenever Codex won't reload a session, the desktop app
  crashes or white-screens on launch or when opening a chat, or a session
  rollout file under ~/.codex/sessions has grown huge (commonly from embedded
  base64 screenshots or large tool outputs). Slims the on-disk rollout in place
  - dropping superseded compaction checkpoints, replacing images with text,
  truncating oversized outputs, archiving the original first - so the session
  reloads and can be continued. Trigger on phrases like "Codex crashes on
  startup", "Invalid string length", "Codex won't open my conversation", "Codex
  session too big", "oversized rollout", or "recover my Codex session". Not for
  routine context-window pressure (use Codex's /compact) and not for Claude Code
  sessions, which store attachments by reference and do not hit this crash.
license: MIT
metadata:
  version: 1.0.0
---

# Codex Infinity Thread

Keep a long-lived Codex conversation usable across hundreds of tasks, and bring it
back when the session grows too large for the desktop app to open, by slimming its
on-disk rollout while preserving the thread.

## The failure this fixes

Codex stores each session as a JSONL "rollout" at
`~/.codex/sessions/YYYY/MM/DD/rollout-<timestamp>-<uuid>.jsonl`. When the desktop
app opens a session it aggregates the entire rollout into a single in-memory
string. Node/V8 caps a string at **536,870,888 bytes (~512 MB)**; past that the
main process throws **`RangeError: Invalid string length`** and the app crashes
on launch (it auto-restores the last session, so it re-crashes every time).

The bloat is almost always **base64 screenshots**: the `computer-use` / browser
tool records one per action, and each is stored twice (as a `data:image` URI in
the model-facing `function_call_output`, and as an MCP `{type:image,data,...}`
block in the display-only event). Text is tiny by comparison.

This is a real, unresolved issue (see references/troubleshooting.md for the
upstream bug reports). There is no official repair command - hence this skill.

## Quick start

```bash
# 1. Find the offender (or pass a path directly)
python {baseDir}/scripts/repair_rollout.py --auto --dry-run

# 2. Repair it (archives the original, swaps in the slimmed file)
python {baseDir}/scripts/repair_rollout.py /path/to/rollout-....jsonl

# 3. Confirm it's safe to load
python {baseDir}/scripts/verify_rollout.py /path/to/rollout-....jsonl
```

Then **force-quit and relaunch Codex**, reopen the session, and send a one-line
test prompt to confirm it replays.

## Workflow

Follow these steps. The scripts are deterministic and back up the original, so
this is reversible at every stage.

1. **Diagnose.** Run `repair_rollout.py --auto --dry-run`. It scans
   `~/.codex/sessions`, lists oversized rollouts largest-first, and reports what
   each slimming step would save - without changing anything. Confirm the file
   it picks is the session the user actually wants back (match the uuid, or the
   `cwd`/first prompt if unsure).

2. **Repair.** Run `repair_rollout.py <path>` (drop `--dry-run`). It applies the
   operations below **least-lossy first** and stops as soon as the file is under
   the target (default 400 MB, comfortably under the 512 MB ceiling). It copies
   the original to `<file>.orig` before swapping in the slimmed version.

3. **Verify.** Run `verify_rollout.py <path>`. It must report **"safe to load"**:
   valid JSON on every line, a `session_meta` id present, no images remaining,
   and the file under the ceiling. If any check FAILs, do not relaunch - inspect
   manually (see references/troubleshooting.md).

4. **Relaunch.** Tell the user to **force-quit** Codex (the crashed app holds the
   old session in memory - dismissing the error dialog is not enough), relaunch,
   reopen the session, and **send a short test prompt**. The first prompt is when
   the history is replayed to the model, so it's the real confirmation.

5. **Reversibility.** If anything looks wrong, restore the archive:
   `mv <file>.orig <file>` (with Codex quit), then relaunch.

## The least-lossy-first ladder

`repair_rollout.py` applies these in order and stops when the file is small
enough, so it removes only as much as necessary. Understanding the order matters
if you ever repair a rollout by hand.

1. **Drop superseded compaction checkpoints** (`drop-compacted`). Codex's
   `/compact` writes a `compacted` record whose `replacement_history` becomes the
   resume baseline; on reload the **newest** one supersedes everything older. So
   every earlier `compacted` record is dead weight - dropping them loses **zero**
   model context.

2. **Images to text** (`images-to-text`). Replace every screenshot with a short
   text marker. The model does not need stale screenshots to continue, and on a
   screenshot-heavy session this is the step that does the real work. This must
   produce **text**, never a placeholder image - see the gotcha below.

3. **Truncate oversized text outputs** (`truncate-output`). Trim large
   tool-output bodies to head + tail with an elision marker. Loses only the
   middle of big outputs; keeps the call/result structure and pairing intact.

4. **Keep header + recent turns** (`truncate-turns`, last resort). Preserve the
   `session_meta` header and the most recent turns, cutting on a **user-message
   boundary**. This is the only step that drops real conversation context, so it
   runs last and only if the steps above didn't get under target.

## Critical gotchas

- **Never replace a screenshot with a tiny placeholder image (e.g. a 1x1 PNG).**
  It looks harmless and the session reloads - but the first time the user
  prompts, Codex replays the history to the Responses API, which rejects the
  sub-minimum-dimension image with *"Invalid image in your last message. Please
  remove it and try again."* Use a **text** marker; there is then no image for
  the API to validate. (This was learned the hard way - it is the single most
  important rule here.)

- **Always keep the first `session_meta` line.** Without a `session_meta` record
  carrying an `id`, the loader fails with *"failed to parse thread ID"* and the
  session won't open at all.

- **Cut only on user-message boundaries.** Codex's `normalize_history` self-heals
  orphaned `function_call`/`function_call_output` pairs on load, but it does
  **not** fix an orphaned leading `reasoning` item - which the API will 400. A
  user-message boundary avoids leaving a dangling reasoning item.

- **Don't strip the newest `compacted` record.** It is the active resume
  checkpoint the model replays from; only the older, superseded ones are safe to
  drop.

- **Resume is stateless replay** (`store=false`, no `previous_response_id`): the
  local rollout *is* the model's context. Slimming really does change what the
  model sees - which is why the order above is least-lossy-first.

## Files

- `scripts/repair_rollout.py` - the slimmer (stdlib only; `--auto`, `--dry-run`,
  `--target-mb`, `--backup-dir`, `--keep-images`).
- `scripts/verify_rollout.py` - the safety check; run before and after.
- `references/rollout-format.md` - the rollout JSONL schema, what is replayed to
  the model vs display-only, and where bloat accumulates. Read this before
  hand-editing a rollout.
- `references/troubleshooting.md` - crash signatures, upstream bug references,
  and what to do when the standard repair isn't enough.
