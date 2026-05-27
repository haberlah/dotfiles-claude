# codex-infinity-thread

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Agent Skill](https://img.shields.io/badge/Claude%20Code-skill-8A63D2.svg)](SKILL.md)

A [Claude Code](https://docs.claude.com/en/docs/claude-code) skill for keeping a
long-lived **Codex** conversation usable across hundreds of tasks, and recovering
it when the session grows too large for the desktop app to open, by slimming its
on-disk rollout while preserving the thread.

## The problem

Codex stores each session as a JSONL "rollout" under
`~/.codex/sessions/.../rollout-<timestamp>-<uuid>.jsonl`. When the desktop app
opens a session it aggregates the whole rollout into one in-memory string.
Node/V8 caps a string at **536,870,888 bytes (~512 MB)**; past that the app
throws **`RangeError: Invalid string length`** and crashes on launch, every
launch, because it auto-restores the last session.

The bloat is almost always **base64 screenshots** from the `computer-use` or
browser tool (one per action, stored twice). It is an
[acknowledged but unfixed issue](https://github.com/openai/codex/issues/22004)
with no official repair command, so the workaround people find is to delete the
session. This skill keeps the session instead.

## Install

```bash
git clone https://github.com/haberlah/codex-infinity-thread.git \
  ~/.claude/skills/codex-infinity-thread
```

Claude Code discovers it on next launch and triggers it automatically when you
describe the symptom. The scripts are plain Python (standard library only), so
you can also run them directly without Claude Code.

## Usage

```bash
# Find oversized rollouts and preview the fix (changes nothing)
python scripts/repair_rollout.py --auto --dry-run

# Repair one (archives the original, then swaps in the slimmed file)
python scripts/repair_rollout.py ~/.codex/sessions/2026/05/20/rollout-....jsonl

# Confirm it is safe to load (run before and after)
python scripts/verify_rollout.py ~/.codex/sessions/2026/05/20/rollout-....jsonl
```

Then **force-quit and relaunch Codex**, reopen the session, and send a short test
prompt to confirm it replays.

| `repair_rollout.py` flag | Meaning |
| ------------------------ | ------- |
| `--auto` | scan `~/.codex/sessions` and pick the largest oversized rollout |
| `--dry-run` | report what would happen; modify nothing |
| `--target-mb N` | target size (default 400, well under the 512 MB ceiling) |
| `--backup-dir DIR` | where to archive the original (default: alongside the file) |
| `--keep-images` | skip the image-to-text step |

## How it works

The repair applies the **least-lossy operations first** and stops as soon as the
file is under target, so it removes only as much as necessary:

1. **Drop superseded compaction checkpoints.** Codex resumes from the newest one
   and treats it as superseding the rest, so older ones are dead weight. Zero
   context loss.
2. **Replace embedded images with text markers.** The model does not need stale
   screenshots to continue; on a screenshot-heavy session this does the real
   work. (It must be text, never a placeholder image. See below.)
3. **Truncate oversized text tool outputs** to head and tail.
4. **Keep the header plus most recent turns** (last resort, cut on a user-message
   boundary). The only step that drops conversation context.

On a real 1.27 GB session this reached **152 MB** using only steps 1 and 2, with
every turn preserved.

## Safety

- The original is copied to `<file>.orig` before any change. To undo, with Codex
  quit: `mv <file>.orig <file>`.
- `verify_rollout.py` must report **"safe to load"** before you relaunch.
- Screenshots are replaced with **text**, never a tiny placeholder image. A
  replayed sub-minimum image is rejected by the Responses API with *"Invalid
  image in your last message"*. See [`references/`](references/) for why.

## Project structure

```
codex-infinity-thread/
├── SKILL.md            # the skill: workflow + triggers (for Claude Code)
├── README.md           # this file (for humans)
├── LICENSE             # MIT
├── SECURITY.md         # how to report issues; what the tool does with data
├── CONTRIBUTING.md     # how to propose changes safely
├── scripts/
│   ├── repair_rollout.py
│   └── verify_rollout.py
└── references/
    ├── rollout-format.md
    └── troubleshooting.md
```

## Background

A full write-up, including the diagnosis, the generalised toolkit, and why this
matters if you run long-lived Codex "megathreads", is in
[`docs/keeping-a-codex-conversation-alive.md`](docs/keeping-a-codex-conversation-alive.md).

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md). In short:
standard library only, always reversible, and never commit session data.

## Licence

MIT, Copyright (c) 2026 David Haberlah. See [LICENSE](LICENSE).
