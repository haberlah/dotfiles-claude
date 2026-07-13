# Regenerate and validate loop

## Preconditions

1. Clean BellaAssist-V1 tree at the intended head (prefer **origin/main** worktree — not a dirty feature branch).
2. Pack checkout on a docs branch from pack `main`.
3. Node deps installed in the pack (`npm install` if needed).

```bash
export BELLAASSIST_REPO_PATH=/path/to/clean/BellaAssist-V1
cd /path/to/bella-assist-architecture-pack
```

## Standard loop

```bash
npm run migrate:schema   # if schema viewer migration is part of the change
npm run generate         # writes generated/* from V1 source
npm run validate
npm run check
npm test
npm run build
# full: npm run qa
```

Do **not** hand-edit files under `generated/`. If an inventory is wrong, fix the generator (`scripts/generate-inventories.mjs`) or the source inputs, then regenerate.

## After pack merge — V1 embed

From BellaAssist-V1 (clean branch):

```bash
# Sync content/ and generated/ from standalone pack main into docs/architecture-pack/
# (rsync or scripted copy — preserve V1-specific README.md for the embed)

npm run check:architecture-pack
# or with explicit path:
ARCHITECTURE_PACK_REPO=/path/to/bella-assist-architecture-pack npm run check:architecture-pack
```

Open a **separate** V1 PR for the snapshot only (no unrelated runtime changes).

## Provenance

`generated/source-provenance.json` must record:

- `sourceHead` / `sourceOriginMain` for promoted regen
- `sourceScope: promoted-origin-main` when regenerating from clean main
- Digests of key source inputs

Reject or re-run regenerations that leave branch-specific provenance on pack main without an explicit draft-only intent.

## Draft / branch regenerations

Branch-specific regenerations (e.g. stacked feature docs) may use a non-main V1 head **only on draft pack PRs**, with a clear “regenerate from promoted main before ready” gate in the PR body.
