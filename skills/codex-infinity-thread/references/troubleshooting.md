# Troubleshooting

## Crash signature

On launch (or when opening a specific chat), the Codex desktop app shows:

```
A JavaScript error occurred in the main process
Uncaught Exception:
RangeError: Invalid string length
    at ... (app.asar/.vite/build/...)
    at Socket.onStdoutData (...)
    ...
```

It happens on every launch because the app auto-restores the last session and
re-hits the same oversized rollout. Force-quitting alone does not help; the file
must be slimmed first.

Companion symptom after a *partial* fix: the session opens, but the first prompt
returns **"Invalid image in your last message. Please remove it and try again."**
That means an image (often a placeholder image) is still being replayed. The fix
is to replace images with **text**, not a tiny image - see the gotcha in
SKILL.md.

## Confirm you're on the right file

```bash
python scripts/repair_rollout.py --auto --dry-run
```

Match the chosen file's `<uuid>` to the session you want, or open the rollout and
check the first `session_meta` `cwd` / the first user message. The session id is
both the filename stem and the `id` in the first `session_meta` line.

## If the standard repair isn't enough

The default run drops superseded `compacted` records and converts images to text,
which is enough for almost all screenshot-driven bloat. If a rollout is still
over target (rare - usually means enormous text tool outputs or a genuinely huge
conversation):

1. Lower the target and let later steps engage:
   `repair_rollout.py <file> --target-mb 300`
   This brings in `truncate-output` (head+tail of large tool outputs) and, as a
   last resort, `truncate-turns` (keep header + most recent turns, cut on a
   user-message boundary).
2. Re-run `verify_rollout.py`. It must say **"safe to load"**.
3. Only then relaunch Codex.

## Reversibility

`repair_rollout.py` copies the original to `<file>.orig` (or into
`--backup-dir`) before swapping. To undo, with Codex quit:

```bash
mv /path/to/rollout-....jsonl.orig /path/to/rollout-....jsonl
```

For extra safety on an irreplaceable session, copy the original elsewhere before
repairing.

## Prevention

The bloat is driven by the `computer-use` / browser tool inlining a screenshot
per action into a long-running thread. To avoid hitting the wall again in a
session you intend to keep for a long time: lean on `/compact` periodically (it
writes a fresh checkpoint that supersedes the heavy history), and avoid
unnecessary screenshot-heavy browser loops inside the one megathread.

## Upstream status (as of 2026-05)

The crash is acknowledged in the Codex issue tracker but has **no merged fix, no
documented size limit, and no official repair command**:

- openai/codex #22004 - "RangeError: Invalid string length when loading sessions
  whose rollout JSONL exceeds V8's max string length" (matches this exactly).
- openai/codex #20269 - session > ~500 MB becomes unrecoverable on launch.
- openai/codex #15411 - macOS startup crash on a huge rollout.
- openai/codex #24191 - *feature request* for a `prune-session` command (not
  shipped).

If/when an official prune/repair command ships, prefer it; until then this skill
fills the gap. The community workaround circulating in those issues is "delete
the rollout file", which loses the whole session - this skill exists to keep the
session instead.
