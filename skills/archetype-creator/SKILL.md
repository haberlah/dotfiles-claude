---
name: archetype-creator
description: >
  Create user archetypes from research data or product context. Use when the user wants to
  build, define, or refine user archetypes, behavioural user types, or abstract user profiles.
  Also triggers when user mentions "archetype", "user types", or wants a non-persona approach
  to user segmentation. Guides a multi-step workflow from scoping through data intake,
  pattern identification, drafting, validation, and deliverable generation.
author: David Haberlah
version: 1.0.0
---

# Archetype Creator

Build research-grounded user archetypes through a structured, interactive workflow.

Archetypes are abstract, label-based user profiles organised by **behaviour, motivations, and goals** — not demographics. They differ from personas in that they omit fictional names, photos, and biographical narratives, instead using descriptive labels (e.g., "The Reliability Researcher").

## Core principles

These principles are non-negotiable and must guide every stage of the workflow:

1. **Behaviour-first** — Demographics are context, never the organising principle.
2. **Real users over aspirational users** — Observe what users actually do, don't project what you wish they'd do.
3. **Authentic flaws** — Contradictions and limitations make archetypes useful. Reject over-idealisation.
4. **Living documents** — Archetypes are hypotheses, not monuments. Signal impermanence through editable formats.
5. **3-5 default** — Most products need 3-5 archetypes. Use the 20% heuristic: each archetype should represent roughly 20% of users. Justify deviations.
6. **JTBD-compatible** — Jobs-to-be-done can be referenced within archetypes. The two tools are complementary, not competing.
7. **Inclusive by default** — Diversity exists *within* archetypes, not as separate "diverse" archetypes. Accessibility needs are integrated, not siloed.
8. **Validation required** — Archetypes are hypotheses until tested with real users. Mark confidence levels honestly.

## Workflow

This is a 6-stage interactive workflow. **Never skip ahead without user approval at each gate.**

Present a brief overview of all stages at the start so the user knows what to expect, then proceed stage by stage.

---

### Stage 0: Scope

**Goal:** Understand the product/service, who the users are, and what decisions the archetypes will inform.

Ask the user:
1. What is the product or service these archetypes are for?
2. Who are the target users (broad strokes)?
3. What decisions will these archetypes inform? (e.g., feature prioritisation, content strategy, onboarding design, marketing positioning)
4. Are there existing personas, segments, or user research to build on?
5. What format do they want the deliverable in? (Markdown file, Google Doc, slide deck)

**Gate:** Present a summary of the scope and confirm before proceeding.

---

### Stage 1: Data intake

**Goal:** Gather and review whatever research inputs the user has.

Accepted inputs (any combination):
- Interview transcripts or notes
- Survey data or summaries
- Analytics reports or dashboards
- Support tickets or customer feedback
- Existing personas or market segments
- Product usage data
- Competitive research
- The user's own domain expertise (verbal description)

If the user has **no formal research data**, that's fine — work with what they know. Be explicit that the resulting archetypes will have lower confidence levels and should be treated as hypotheses requiring validation.

For each input provided:
1. Read/review the material
2. Extract behavioural patterns, goals, pain points, and contextual factors
3. Note the evidence type (observed, self-reported, inferred, assumed)

**Gate:** Summarise what you've received, what patterns are emerging, and any gaps. Confirm completeness before proceeding.

---

### Stage 2: Pattern identification

**Goal:** Identify behavioural clusters from the data.

Read `references/clustering-guide.md` for detailed methodology.

Process:
1. List all distinct behaviours, goals, pain points, and contexts identified in Stage 1
2. Group them into candidate clusters using behavioural affinity (not demographics)
3. For each candidate cluster, identify:
   - The defining behaviour or motivation that distinguishes this group
   - How this cluster differs from the others
   - Approximate proportion of the user base (use the 20% heuristic)
4. Present candidate clusters as a numbered list with:
   - Working label (behavioural descriptor)
   - 2-3 sentence summary
   - Key distinguishing characteristics
   - How confident you are in this cluster (high/medium/low)

Aim for 3-5 clusters. If you identify more, explain why and ask the user whether to merge or keep them separate.

**Gate:** Present candidate clusters for review. The user may merge, split, rename, add, or remove clusters. Iterate until they approve.

---

### Stage 3: Archetype drafting

**Goal:** Draft each archetype using the canonical template.

Read `references/archetype-template.md` for the full field guide.

For each approved cluster, draft an archetype with these fields:
- **Label** — Abstract behavioural descriptor (e.g., "The Efficiency Seeker")
- **Summary** — 1-2 sentences capturing the essence
- **Behavioural profile** — How they act, think, and make decisions
- **Motivations & goals** — Functional jobs (tasks to complete) + emotional jobs (how they want to feel)
- **Pain points & challenges** — Frustrations, barriers, unmet needs
- **Context** — When, where, and how they engage; environmental factors
- **Representative language** — Phrases or sentiments typical of this archetype (from research, or synthesised)
- **Design implications** — What this archetype means for product decisions
- **Confidence level** — Per-attribute evidence basis: observed / inferred / assumed

Draft **one archetype at a time**. Present it, get feedback, refine, then move to the next. This prevents the user from being overwhelmed and allows each archetype to inform the next.

**Gate:** Each archetype must be approved before drafting the next. After all are drafted, present them side-by-side for a holistic review.

---

### Stage 4: Validation and inclusivity check

**Goal:** Stress-test the archetypes against common failure modes and inclusive design principles.

Read `references/anti-patterns.md` and `references/inclusive-design-checklist.md`.

Run these checks and report findings:

**Anti-pattern review:**
- Are any archetypes aspirational rather than representative of real users?
- Are demographics driving any archetype definition rather than behaviour?
- Are any archetypes too specific (<10% of users) or too generic (>40%)?
- Is there a buyer vs. user confusion (especially in B2B)?
- Are archetypes actionable — do they inform specific design decisions?

**Inclusive design review:**
- Is diversity represented *within* archetypes, not as separate categories?
- Are accessibility needs integrated where relevant, not siloed?
- Does the language avoid stereotypes, othering, or demographic assumptions?
- Are cultural contexts acknowledged without stereotyping?
- Could any archetype description activate bias if read by a diverse team?

Present findings as a checklist with pass/flag/fail for each item. For any flags or fails, propose specific remediation.

**Gate:** User reviews flags and approves remediations before proceeding.

---

### Stage 5: Deliverable

**Goal:** Generate the final archetype artefact.

Read `assets/archetype-deliverable.md` for the output template.

Produce:
1. **Individual archetype profiles** — One section per archetype using the canonical template
2. **Comparison table** — All archetypes compared across key dimensions (goals, pain points, context, confidence)
3. **Usage guide** — Brief section on how to use these archetypes in decision-making (2-3 paragraphs)
4. **Validation roadmap** — What to test next, how to validate, when to revisit

Output format depends on Stage 0 preference:
- **Markdown file** — Write to the project directory using the Write tool
- **Google Doc** — Use `gws` CLI to create (requires user confirmation per CLAUDE.md write rules)
- **Slide deck** — Create as a Google Slides presentation via `gws` CLI

After generating, present the deliverable and ask if any final adjustments are needed.

**Gate:** Final sign-off from the user.

---

## Important notes

- **No fictional biography.** Archetypes use abstract labels, not names like "Marketing Mary." No photos, ages, or personal backstories.
- **Evidence over invention.** Every attribute should trace back to data. When you synthesise, say so. When you assume, mark it.
- **Editable formats only.** Never produce a "final" PDF. The deliverable should invite ongoing refinement.
- **One archetype at a time.** In Stage 3, draft and refine iteratively. Don't dump all archetypes at once.
- **The user drives clustering.** In Stage 2, you propose clusters but the user decides. Their domain knowledge overrides statistical elegance.
