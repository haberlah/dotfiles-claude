# Inclusive Design Checklist for Archetypes

Run this checklist during Stage 4 (Validation) to ensure archetypes support equitable, non-stereotypical design. Each item is pass/flag/fail.

## Table of contents

1. [Organising principle](#1-organising-principle)
2. [Diversity within, not between](#2-diversity-within-not-between)
3. [Accessibility integration](#3-accessibility-integration)
4. [Language audit](#4-language-audit)
5. [Cultural context](#5-cultural-context)
6. [Representation in research](#6-representation-in-research)
7. [Power dynamics](#7-power-dynamics)

---

## 1. Organising principle

**Check:** Are archetypes organised by behaviour and motivation, NOT by demographic categories?

| Result | Criteria |
|---|---|
| **Pass** | Every archetype is defined entirely by behavioural patterns, goals, and pain points. Demographics appear only as contextual information. |
| **Flag** | Demographics are mentioned prominently but aren't the organising principle. Risk of readers anchoring on demographics. |
| **Fail** | Archetypes are named after or primarily differentiated by age, gender, ethnicity, income, or education. |

**Remediation:** Rewrite archetype labels and summaries to lead with behaviour. Move any demographic context to a clearly secondary section. If two archetypes can only be distinguished by demographics, they are likely the same archetype.

---

## 2. Diversity within, not between

**Check:** Does diversity exist *within* each archetype, rather than being captured by separate "diverse" or "accessible" archetypes?

| Result | Criteria |
|---|---|
| **Pass** | Each archetype implicitly or explicitly encompasses users of varied backgrounds, abilities, and contexts. No archetype is defined by a marginalised identity. |
| **Flag** | Diversity isn't explicitly addressed within archetypes, but no archetype is othering either. |
| **Fail** | There is a separate archetype for "users with disabilities", "non-English speakers", or any group defined by a marginalised identity. |

**Remediation:** Integrate diverse characteristics into existing archetypes where relevant. For example, if some users in "The Efficiency Seeker" archetype use screen readers, note that within the archetype's context section rather than creating a separate "Accessible User" archetype.

**Why this matters:** Creating separate "diverse" archetypes implies that diversity is exceptional rather than normal. It also concentrates all accessibility and inclusion considerations into one archetype rather than making them a cross-cutting concern.

---

## 3. Accessibility integration

**Check:** Are accessibility needs and assistive technology usage acknowledged where relevant within archetypes?

| Result | Criteria |
|---|---|
| **Pass** | Archetypes note relevant accessibility considerations (e.g., screen reader use, keyboard navigation, colour contrast needs, cognitive load sensitivity) within their context and design implications sections. |
| **Flag** | Accessibility isn't mentioned, but there's nothing that would actively exclude users with disabilities. |
| **Fail** | Archetype descriptions assume able-bodied, neurotypical users throughout (e.g., "quickly scans visual layouts", "multitasks across three screens"). |

**Remediation:** For each archetype, consider: "How might a user with a visual, motor, hearing, or cognitive difference experience this archetype's needs and pain points?" Add relevant notes to the context and design implications sections.

**Functional performance criteria to consider:**
- Vision (low vision, blindness, colour vision differences)
- Hearing (deaf, hard of hearing)
- Motor/manipulation (limited dexterity, tremor, use of switch devices)
- Cognitive/learning (attention, memory, processing speed, literacy)
- Speech (for voice-interface products)

---

## 4. Language audit

**Check:** Does the language in archetype descriptions avoid stereotypes, othering, and assumptions tied to demographic categories?

| Result | Criteria |
|---|---|
| **Pass** | All language is neutral, behaviour-focused, and wouldn't activate demographic stereotypes in a reader's mind. |
| **Flag** | Some phrasing could be read as implicitly gendered, age-coded, or culturally specific, even if unintentionally. |
| **Fail** | Descriptions use stereotypical language, othering terms ("they prefer simple things"), or coded demographic assumptions. |

**Red flags to scan for:**
- Gendered language or assumptions ("she values aesthetics", "he wants control")
- Age-coded language ("digital native", "not tech-savvy", "traditional")
- Socioeconomic assumptions ("budget-conscious" as euphemism, "premium" as proxy for wealth)
- Ability assumptions ("easily navigates", "quickly scans", "intuitively understands")
- Cultural assumptions presented as universal truths

**Remediation:** Rewrite flagged language to be behaviour-specific without demographic coding. Replace "not tech-savvy" with "prefers established tools and resists workflow changes". Replace "digital native" with "comfortable adopting new tools and self-serving through documentation".

---

## 5. Cultural context

**Check:** Are cultural contexts acknowledged without stereotyping, and is the archetype set relevant across the product's actual user geography?

| Result | Criteria |
|---|---|
| **Pass** | Archetypes account for cultural variation in behaviour and context where relevant (e.g., privacy norms, communication styles, payment preferences) without attributing behaviours to specific cultures. |
| **Flag** | Cultural context isn't mentioned. This is fine for single-culture products but a gap for international ones. |
| **Fail** | Cultural behaviours are stereotyped or entire cultures are reduced to a single archetype. |

**Remediation:** For international products, note where cultural context shapes behaviour *within* archetypes (e.g., "In some contexts, this archetype prefers group decision-making; in others, individual authority"). Never create archetypes named after cultures or geographies.

---

## 6. Representation in research

**Check:** Did the research that informed these archetypes include diverse participants?

| Result | Criteria |
|---|---|
| **Pass** | Research participants included diversity across relevant dimensions (ability, age, gender, ethnicity, socioeconomic background, geography) proportionate to the actual or intended user base. |
| **Flag** | Research participant demographics are unknown or undocumented. |
| **Fail** | Research participants were predominantly from a single demographic group, and archetypes are presented as universal. |

**Remediation:** If research lacked diversity, document this as a limitation. Mark attributes that may only reflect the researched population's experience. Plan follow-up research with underrepresented groups. Never present narrow-sample findings as universal truths.

---

## 7. Power dynamics

**Check:** Do the archetypes account for power imbalances between user types, and between users and the system?

| Result | Criteria |
|---|---|
| **Pass** | Where relevant, archetypes note differences in agency, access, and power (e.g., admin vs. end-user, employer vs. employee, expert vs. novice) and the design implications of these dynamics. |
| **Flag** | Power dynamics exist but aren't addressed in the archetypes. |
| **Fail** | Archetypes implicitly assume equal agency for all users, masking real power imbalances that affect how users experience the product. |

**Remediation:** For products where power dynamics are relevant (multi-stakeholder systems, B2B, platforms), note each archetype's position in the power structure and how this shapes their experience, constraints, and needs.
