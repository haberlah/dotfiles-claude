# Reader map — question → pack path

Paths are relative to the architecture-pack root (or V1 `docs/architecture-pack/`).

| Reader question | Start here | Then |
| --- | --- | --- |
| What runs and where? | `content/20-architecture/system-overview.md` | `content/20-architecture/services-integrations-operations.md` |
| What does each API accept/return? | `content/20-architecture/api-and-route-model.md` | `generated/endpoint-contract-inventory.md`, `generated/endpoint-catalogue.md` |
| Where is participant data stored/derived? | `content/30-schema/schema-current-state.md` | `generated/schema-inventory.md`, `generated/jsonb-contract-inventory.md`, `generated/data-lineage-inventory.md` |
| Frontend by role/workflow? | `content/20-architecture/frontend-client.md` | `generated/client-route-map.md`, `generated/client-api-call-inventory.md` |
| AI routing and constraints? | `content/20-architecture/ai-evaluation-pipeline.md` | `generated/ai-model-call-matrix.md`, `generated/ai-call-inventory.md` |
| AI skills organisation? | `content/00-start-here/ai-skill-runtime-current-state.md` | `content/20-architecture/ai-skills-prompt-lifecycle.md`, `generated/ai-skill-catalogue.md` |
| Gateway / redaction / PII? | `content/20-architecture/ai-gateway-redaction-pipeline.md` | LiteLLM `qa/` evidence, gateway tests |
| CRM / provisioning facade? | `content/20-architecture/crm-integration.md` (when present) | V1 ADRs under `docs/adr/`, `generated/endpoint-catalogue.md` (`/api/internal/crm`) |
| Why does a module exist? | `content/25-design-intent/design-intent-overview.md` | `runtime-module-intent.md`, dormant index |
| Privacy / auth / isolation? | `content/20-architecture/auth-access-data-isolation.md` | `content/30-security/rls-activation.md`, `generated/route-access-matrix.md`, `generated/access-register.md` |
| Ops / deploy / runbooks? | `content/40-operations/` | `generated/ops-control-inventory.md`, `generated/env-var-inventory.md` |
| What do release checks prove? | `content/60-risk-review/qa-coverage.md` | `generated/qa-release-gate-inventory.md`, `generated/test-inventory.md` |
| E2E tiers / promote rules? | V1 `docs/testing/e2e-operations.md` | V1 `docs/E2E-LOCAL.md` |
| Compliance registers? | `content/50-compliance/` | `generated/*-register.md`, `generated/ropa-runtime.md` |
| Residual risk? | `content/60-risk-review/current-risk-register.md` | |

## Status meanings

| Status | Meaning |
| --- | --- |
| `current` | Maintained narrative of live product behaviour |
| `generated` | Machine inventory — regenerate, do not hand-edit |
| `decision` | Explicit decision record |
| `draft` | Not yet promoted to current |
