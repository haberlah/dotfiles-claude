---
name: architecture-pack
description: >
  Use whenever working on BellaAssist (Bella Assist) product, runtime, schema,
  API, AI skills, auth/RLS, CRM integration, ops, compliance registers, or
  architecture documentation — including phrases like "architecture pack",
  "arch-pack", "arch pack", "current-state docs", "how does X work in Bella",
  "endpoint inventory", "schema inventory", or "before coding BellaAssist".
  Routes agents to the BellaAssist architecture-pack for business logic maps,
  schemas, and generated inventories, and enforces the regenerate → validate →
  snapshot-sync loop. Also use when updating docs after a BellaAssist behaviour
  change, checking documentation drift, or deciding which regression tests to run.
---

# BellaAssist Architecture Pack

## Before You Use This Skill

Read `references/organisation-config.md` for local clone paths and repo names.
Default layout assumes GitHub Desktop clones under `~/Documents/GitHub/`.

| Surface | Role |
| --- | --- |
| **Standalone pack** (`bella-assist-architecture-pack`) | Canonical current-state wiki + generated inventories |
| **V1 embed** (`BellaAssist-V1/docs/architecture-pack/`) | Snapshot of pack `content/` + `generated/` for in-repo agent access |
| **V1 code** | Runtime source of truth for behaviour |
| **Obsidian** | Personal working notes only — never the SSOT |

> [!CRITICAL]
> **Code is the runtime SSOT. The pack is the current-state map.** Prefer pack + generated inventories for orientation; verify behaviour in code before shipping. Never invent product behaviour, production release IDs, or live RLS/table counts without citing a current content page, generated inventory, or a fresh probe.

> [!CRITICAL]
> **Do not hand-edit `generated/`.** Change generators or source inputs, then run `npm run generate` in the pack against a clean BellaAssist-V1 tree (prefer `origin/main` worktree). Hand edits are drift.

> [!CRITICAL]
> **Never update only the V1 embed.** The standalone pack is canonical. After pack changes merge, refresh the embed and run `npm run check:architecture-pack`. Editing only `BellaAssist-V1/docs/architecture-pack/` creates silent dual-source drift.

> [!CRITICAL]
> **Never claim production schema/RLS state from source declarations alone.** Source can lead production until setup-db apply + verify-applied + db-proof evidence. Content pages must distinguish source-declared vs live-proofed.

> [!NOTE]
> **Obsidian is the working notebook.** Plans, drift audits, and checklists belong under `BellaAssist Architecture Pack/` in `~/Documents/Obsidian Vault/` with `canonical_source` frontmatter pointing at pack/V1 paths. See the Document Map note for surface ownership.

## When To Invoke

Load this skill when any of the following is true:

- Implementing or reviewing BellaAssist product behaviour
- Answering “how does X work”, “where is Y stored”, “what routes exist”, “what AI skills run”
- Changing schema, auth, RLS, CRM facade, evaluation pipeline, or ops runbooks
- Refreshing or auditing architecture documentation
- Choosing unit / release / e2e regression commands for BellaAssist

## Read Path (every non-trivial BellaAssist task)

1. **Orient** — `docs/architecture-pack/README.md` (inside V1) **or** pack `content/00-start-here/overview.md`.
2. **Route by question** — follow `references/reader-map.md` (and the overview Reader Map).
3. **Lists and counts** — open the matching file under `generated/` (endpoints, schema, AI skills, tests, env, lineage, etc.).
4. **Design intent** — `content/25-design-intent/` for why a module exists and active vs dormant.
5. **Code** — only after the map; treat code as final authority for runtime.
6. **Risks / QA** — `content/60-risk-review/` when changing high-risk surfaces or tests.

Prefer the **embedded** snapshot when already in the V1 repo. Prefer the **standalone** pack when regenerating inventories or editing docs.

## Write Path (behaviour or docs changed)

1. Implement / verify in **BellaAssist-V1** code.
2. If the change affects current-state behaviour:
   - Update curated `content/` pages (status `current` or `draft` as appropriate), **and/or**
   - Regenerate inventories from a clean V1 tree (see `references/regenerate-loop.md`).
3. Run the pack change loop (`npm run qa` or at least generate + validate + check + test).
4. Open a PR on **architecture-pack**.
5. After pack merge: refresh V1 `docs/architecture-pack/{content,generated}/`, run `npm run check:architecture-pack`, open a **separate** V1 PR.
6. Log material programme notes in Obsidian with links to the PRs.

### Content rules

- Frontmatter `status`: `current` | `generated` | `decision` | `draft`.
- Reader-facing pages describe **current** product behaviour only — no roadmap, migration diary, or “how we built the docs” noise.
- Current-state claims need code, generated inventory, live schema evidence, or an explicit decision record.
- Safe Markdown + Mermaid only in the wiki app.

## Personas

Pack pages carry `personas: [...]`. Useful filters: `architect`, `backend`, `frontend`, `data`, `ai-engineer`, `security`, `privacy`, `qa-ops`. When reading the hosted wiki, the persona query/cookie narrows nav; when reading files, use frontmatter to prioritise pages.

## Tests And Regression

See `references/test-and-regression.md` for the full matrix.

**Defaults:**

| Context | Default command |
| --- | --- |
| BellaAssist code change | `npm run test:release` |
| Quick unit only | `npm test` |
| Architecture-pack docs change | `npm run qa` in the pack repo |
| Pre-promote hosted behaviour | green `e2e-full` on the commit (`docs/testing/e2e-operations.md`) |

Canonical unit inventory: pack `generated/test-inventory.md`.  
Coverage narrative: pack `content/60-risk-review/qa-coverage.md`.  
E2E policy SSOT: V1 `docs/testing/e2e-operations.md` (not fully duplicated in the pack).

## When To Stop And Ask A Human

1. Live production probe / db-proof / Cloud Run traffic claims need new evidence IDs.
2. Unclear whether a fact is source-declared vs production-applied.
3. Closing or force-pushing open documentation PRs that others own (e.g. draft regen PRs).
4. Drive/gws writes of signed compliance documents.
5. Any temptation to “just patch the embed” without a pack PR.

## Quick Links (relative to pack root)

| Topic | Start |
| --- | --- |
| Overview | `content/00-start-here/overview.md` |
| System | `content/20-architecture/system-overview.md` |
| API | `content/20-architecture/api-and-route-model.md` + `generated/endpoint-contract-inventory.md` |
| Schema | `content/30-schema/schema-current-state.md` + `generated/schema-inventory.md` |
| AI | `content/20-architecture/ai-evaluation-pipeline.md` + `generated/ai-skill-catalogue.md` |
| Auth / isolation | `content/20-architecture/auth-access-data-isolation.md` |
| CRM (when present) | `content/20-architecture/crm-integration.md` |
| Ops | `content/40-operations/` + `generated/ops-control-inventory.md` |
| Tests | `generated/test-inventory.md` + `content/60-risk-review/qa-coverage.md` |
| Risks | `content/60-risk-review/current-risk-register.md` |
