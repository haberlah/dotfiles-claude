---
name: replit-prd
description: >
  Generate sequential PRD prompt sequences optimized for Replit Agent development.
  Use when: building applications with Replit Agent, creating PRDs or technical
  specifications for Replit, experiencing Replit Agent failures and needing better
  prompting strategy, or decomposing complex projects for Replit Agent. Triggers on
  phrases like "build with Replit", "Replit Agent", "Replit PRD", "vibe coding".
license: MIT
metadata:
  version: "1.0"
  author: haberlah
---

# Replit PRD Generator

Create sequential, dependency-ordered prompt sequences that guide Replit Agent through complex project development.

## Workflow

### 1. Research (Mandatory)

Before writing any PRD, search for current Replit capabilities:

```
□ "Replit Agent [current year, current month] capabilities"
□ "Replit Database PostgreSQL [current year, current month]"
□ "Replit App Storage"
□ "[specific technology] Replit [current year, current month]"
```

See [references/research.md](references/research.md) for the complete checklist.

### 2. Clarify

Gather from user:
- Core functionality and features
- Deployment target (Autoscale vs Reserved VM)
- User expertise level
- Any existing code or constraints

### 3. Sequence

Map feature dependencies and determine phase order. Always establish foundations before dependent features:
- Database schema before queries
- Shared hooks/utilities before components using them
- Layout structure before features filling it
- API patterns before features calling them

### 4. Deliver

**Prompt 0 (Plan Mode):** Full project context. Ask Agent to confirm understanding before building.

**Prompts 1-N (Build Mode):** Sequential phases with:
- Clear objective
- Numbered requirements
- Technical details
- Integration notes
- Acceptance criteria (checkbox format)
- Checkpoint recommendation

See [references/templates.md](references/templates.md) for exact prompt format.

### 5. Adapt

When user returns mid-project with screenshots or new requirements:
- Layout/data model changes → Restructure NOW
- Isolated new feature → Add as additional prompt
- Visual polish → Scoped prompt with DO NOT CHANGE section

See [references/adaptation.md](references/adaptation.md) for patterns.

## Replit Agent Modes

**Plan Mode:** Discuss architecture without modifying code. No charges. Use for Prompt 0.

**Build Mode:** Write and modify code. Creates checkpoints. Use for Prompts 1-N.

## Key Principles

1. **Research before recommending** — Always search current Replit capabilities, software libraries and packages
2. **Native over external** — Replit Database and App Storage, not third-party
3. **Plan Mode first** — Establish context before building
4. **Sequence by dependency** — Foundations before features
5. **Testable phases** — Each prompt ends with verifiable functionality
6. **Checkpoint discipline** — Recommend saves after each phase

## Output Format

All prompts must be copyable text blocks:

```markdown
## Prompt N: [Phase Name]

> **Use [Plan/Build] Mode**

```
[Full prompt content]
```

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Previous functionality still works

**Create checkpoint: "[Phase name]"**
```

## Reference Files

- [references/research.md](references/research.md) — Pre-PRD research checklist
- [references/templates.md](references/templates.md) — Prompt structures and examples
- [references/adaptation.md](references/adaptation.md) — Mid-project change patterns
