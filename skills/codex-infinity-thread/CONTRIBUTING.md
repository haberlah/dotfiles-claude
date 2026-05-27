# Contributing

Thanks for your interest. This is a small, focused tool, and contributions that
keep it simple and dependency-free are very welcome.

## Ground rules

- **Standard library only.** No third-party dependencies, so the scripts run
  anywhere Python 3 does.
- **Safe and reversible.** `repair_rollout.py` must always archive the original
  before writing, and `verify_rollout.py` must pass on the result.
- **Never commit real session data.** `.jsonl` and `.orig` files are gitignored;
  please keep it that way.

## Proposing a change

1. For anything non-trivial, open an issue describing the problem or improvement
   first.
2. Test against a **copy** of a real rollout, never your live session:
   ```bash
   cp <rollout>.jsonl /tmp/test.jsonl
   python scripts/repair_rollout.py /tmp/test.jsonl
   python scripts/verify_rollout.py /tmp/test.jsonl
   ```
3. Validate the skill metadata (name + description required, kebab-case name,
   description under 1024 characters, no angle brackets):
   ```bash
   python /path/to/skill-creator/scripts/quick_validate.py .
   ```
4. Open a pull request with a clear description and the before/after sizes from
   your test.

## Style

Match the existing code: clear names, comments that explain the *why*, and a
strong bias toward not surprising the user when their session files are being
modified.
