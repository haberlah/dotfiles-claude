---
name: bella-archetypes
description: >
  Run BellaAssist co-design archetypes as virtual feedback agents for brand evaluation,
  pricing debates, feature prioritisation, and messaging testing. This skill should be used
  when the user mentions "archetypes", "virtual panel", "brand feedback", "archetype debate",
  "what would the SCs think", "what would participants think", "run the panel", "archetype
  feedback", or wants feedback on BellaAssist brand, product, or positioning from simulated
  user perspectives. Supports SC panel (4 B2B archetypes), Participant panel (4 end-user
  archetypes), full 8-voice panel, or specific archetype pairs and named debate presets.
---

# BellaAssist Archetype Panel

Run 8 research-grounded archetypes as virtual feedback agents. Built from 43+ co-design sessions across 18 individuals (~700K words of transcripts).

Two complementary panels evaluate from different market perspectives:

| ID | Name | Panel | One-liner |
|----|------|-------|-----------|
| SC-01 | The Growth Pragmatist | SC | Sole-trader SC optimising for efficiency and practice growth |
| SC-02 | The Evidence-Driven Advocate | SC | Conviction-driven SC building defensible evidence packages |
| SC-03 | The Institutional Navigator | SC | Org-embedded SC navigating compliance and team coordination |
| SC-04 | The Discerning Craftsperson | SC | Self-built-systems SC benchmarking tools against own solutions |
| P-01 | The Empowered Navigator | Participant | Self-managing adult with professional-grade NDIS navigation |
| P-02 | The Supported Participant | Participant | Willing but overwhelmed adult relying on SC for navigation |
| P-03 | The Proactive Parent-Advocate | Participant | High-agency parent treating the NDIS as a battleground |
| P-04 | The Anchoring Carer | Participant | Present-focused carer managing burden, not fighting systems |

## Panel Selection

| Evaluation type | Recommended panel |
|-----------------|-------------------|
| B2B positioning, pricing, enterprise messaging | SC Panel |
| Consumer messaging, accessibility, onboarding UX | Participant Panel |
| Comprehensive brand evaluation, launch readiness | Full Panel (8 voices) |
| Specific tension testing (trust vs efficiency, etc.) | Named pair |

## Invocation

The skill accepts optional arguments to select the panel:

- **No argument** or `interactive` - Ask the user which panel and what stimulus
- `sc` - SC Panel (4 voices)
- `p` or `participant` - Participant Panel (4 voices)
- `all` or `full` - Full 8-voice panel
- Archetype IDs (e.g., `sc01 sc02`) - Specific archetypes only
- Named pair (e.g., `trust-vs-efficiency`, `power-vs-simplicity`) - Pre-defined strategic pair

Named pairs: `trust-vs-efficiency`, `power-vs-simplicity`, `fighter-vs-maintainer`, `solo-vs-enterprise`, `craft-vs-conviction`, `cross-advocacy`, `cross-high-agency`.

For pair definitions and divergence interpretation, read `references/panel_guide.md`.

## Debate Workflow

### Step 1: Determine panel and stimulus

If the user has not specified a panel, ask: "Which panel — SC (B2B), Participant (end-user), Full (8-voice), or a specific pair?" Suggest the appropriate panel based on what they want to evaluate.

If the user has not yet provided the stimulus (brand concept, tagline, pricing page, feature description, visual, etc.), ask for it. Accept any format — text, screenshot, URL, document.

### Step 2: Load agent cards

Read only the relevant agent card files from the `agents/` directory:

- SC Panel: read all files in `agents/sc/`
- Participant Panel: read all files in `agents/p/`
- Full Panel: read all files in both directories
- Specific IDs: read only the matching files
- Named pair: resolve to archetype IDs via `references/panel_guide.md`, then read those files

Each agent card contains a complete system prompt with identity, evaluation lenses, communication style, calibrated voice, resonance/alienation triggers, and guardrails. Follow the agent card instructions precisely when generating each voice.

### Step 3: Generate voices

For each selected archetype, generate an in-character response to the stimulus. Follow the agent card's evaluation framework, communication style, and representative language.

Format each voice clearly:

```
### SC-01: The Growth Pragmatist
[In-character evaluation — 150-300 words. Reference specific elements of the stimulus.
Use the archetype's characteristic language and evaluation lenses.]

### SC-02: The Evidence-Driven Advocate
[In-character evaluation...]
```

Ground each response in the archetype's specific concerns — do not produce generic feedback. Each voice should reference different aspects of the stimulus and evaluate through its distinct lens.

For full 8-voice panels: consider spawning two parallel agents (one for SC panel, one for P panel) to avoid voice contamination and reduce latency. Merge outputs before synthesis.

### Step 4: Synthesise

After all voices have spoken, provide a structured synthesis:

**Consensus** - Where do the archetypes agree? What does universal agreement signal?

**Divergence** - Where do they disagree? Interpret each divergence using the framework in `references/panel_guide.md`. Identify what the specific pattern of agreement/disagreement signals about the stimulus.

**Recommendations** - Based on the divergence pattern, what specific adjustments would strengthen the concept? Prioritise changes that resolve the most significant tensions.

**Confidence caveat** - Note any relevant limitations from the archetype confidence levels (see `references/panel_guide.md`). Flag if a key demographic perspective is missing from the evaluation.

## Additional Resources

### Reference files (read on demand)
- **`references/panel_guide.md`** - Panel composition, strategic pair definitions, divergence signal interpretation framework, confidence levels
- **`references/sc_overview.md`** - SC archetype comparison table, data foundation, limitations
- **`references/p_overview.md`** - Participant archetype comparison table, data foundation, limitations

### Agent cards
- **`agents/sc/sc01_growth_pragmatist.md`** through **`agents/sc/sc04_discerning_craftsperson.md`**
- **`agents/p/p01_empowered_navigator.md`** through **`agents/p/p04_anchoring_carer.md`**

Each agent card is a self-contained system prompt. Read the full card before generating that archetype's voice. Do not summarise or paraphrase the agent card — use it as the complete persona instruction set.

### Source data
Agent cards and archetypes are synced from Google Drive: `Co-Design Program/Archetypes/`. The archetype-creator skill (`~/.claude/skills/archetype-creator/`) documents the methodology used to create these archetypes. If archetypes need updating, use that skill with new co-design data.
