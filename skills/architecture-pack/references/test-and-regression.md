# Tests and regression — BellaAssist + architecture pack

## Where documentation lives

| Need | Canonical location |
| --- | --- |
| Per-file unit inventory + class breakdown | pack `generated/test-inventory.md` |
| Narrative coverage strengths / gaps | pack `content/60-risk-review/qa-coverage.md` |
| Detected gate commands | pack `generated/qa-release-gate-inventory.md` |
| E2E tiers, flake policy, promote rules | **V1** `docs/testing/e2e-operations.md` |
| Local Playwright setup | **V1** `docs/E2E-LOCAL.md` |
| Release harness implementation | **V1** `scripts/test-release.ts` |

Always prefer regenerated inventories for counts. Prefer `test-release.ts` for the exact skill-contract file list.

## Command matrix (BellaAssist-V1)

| When | Command | Notes |
| --- | --- | --- |
| Default code PR / local release gate | `npm run test:release` | `check` → full `vitest run` → focused skill contracts → `build` |
| Fast unit only | `npm test` | `vitest run` |
| Typecheck + ontology taxonomy drift | `npm run check` | fails on taxonomy drift |
| AI skill smoke (real LLM) | `npm run test:ai-smoke` | needs DB + provider config; limited skills |
| Production HTTP smoke | `npm run test:prod-smoke` | health, auth denial, security headers |
| E2E smoke (local) | Playwright `@smoke` | see `docs/E2E-LOCAL.md` |
| CI unit gate | GitHub Actions `unit` job | required on PRs (see e2e-operations) |
| CI e2e-smoke | Playwright smoke in CI | burn-in / required per branch protection policy |
| Pre-promote | green `e2e-full` on the commit | do not promote without it |
| Nightly | full browsers + optional live-AI | triage next day; not a PR blocker |
| Gateway image changes | `pytest infra/litellm-gateway/tests` | manual gate; not in `test:release` |

## Command matrix (architecture-pack)

| When | Command |
| --- | --- |
| Docs / inventory change | `npm run qa` (or generate + validate + check + test + build) |
| Embed drift after pack merge | from V1: `npm run check:architecture-pack` |

## Classification of unit tests (inventory)

Generated inventory classes:

- `route-handler` — Express handlers under `test/unit/routes/` (supertest, storage mocked)
- `schema-contract` — pins literals / schemas / registries
- `pure-unit` — deterministic helpers
- `pytest` — gateway Python tests
- `factory` / `setup` / `support` — non-case fixtures

## Agent rules

1. For BellaAssist behaviour PRs, run at least `npm run test:release` unless the user scopes narrower.
2. Do not claim “no CI unit gate” — V1 has GitHub Actions unit (and e2e tiers).
3. Do not treat missing browser e2e as absolute: smoke journeys exist; gaps remain for some role matrices.
4. After regenerating the pack, re-read `generated/test-inventory.md` for current counts — do not hardcode file counts in content without regeneration.
