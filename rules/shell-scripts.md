---
paths:
  - "**/*.sh"
---

# Shell script conventions

These rules apply only when reading or editing shell scripts (such as the hooks in `hooks/`).
Because they are path-gated, they load on demand when Claude touches a `.sh` file and cost
nothing at session start.

- Start every script with `#!/bin/bash` and `set -e` (add `-u` and `-o pipefail` for anything
  non-trivial).
- Quote all variable expansions: `"$var"`, `"${arr[@]}"`. Unquoted expansions break on paths
  with spaces.
- Use explicit test operators: `[ -L "$p" ]` before assuming a symlink, `[ -e "$p" ]` (which
  follows links) to confirm a target resolves.
- For symlinks, prefer `ln -sfn` so re-linking is atomic and idempotent.
- Never echo secrets. When surfacing matched lines, truncate them.
- Keep hook scripts fast and side-effect-free unless side effects are their explicit purpose;
  they run on every relevant tool call.
