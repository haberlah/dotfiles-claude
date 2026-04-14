# Archetype Anti-Patterns

Common mistakes that render archetypes ineffective. Use this checklist during Stage 4 (Validation) to stress-test drafted archetypes.

## Table of contents

1. [Aspirational over real](#1-aspirational-over-real)
2. [Gut feeling over research](#2-gut-feeling-over-research)
3. [Demographics as organiser](#3-demographics-as-organiser)
4. [Wrong granularity](#4-wrong-granularity)
5. [Static monuments](#5-static-monuments)
6. [Shelf-ware archetypes](#6-shelf-ware-archetypes)
7. [Buyer-user conflation](#7-buyer-user-conflation)
8. [Stereotype reinforcement](#8-stereotype-reinforcement)

---

## 1. Aspirational over real

**What it looks like:** The archetype describes who the organisation *wishes* users were, not who they actually are. Features and messaging target the idealised user rather than the real one.

**Why it's harmful:** Leads to products and marketing that miss real users entirely. Honda's "Jason" archetype for the Acura RDX was built to reinforce brand positioning rather than observed buyer behaviour — it failed to guide effective decisions.

**How to detect it:**
- Ask: "Have we observed this behaviour in research, or is this who we want users to be?"
- Check whether the archetype conveniently validates a pre-existing product strategy
- Look for suspiciously aspirational language ("discerning", "forward-thinking", "passionate about innovation")

**How to fix it:** Trace every attribute back to observed data. If an attribute is aspirational, either remove it or move it to a separate "aspirational user" note clearly distinguished from the core archetype.

---

## 2. Gut feeling over research

**What it looks like:** Archetypes are built from team assumptions, stakeholder opinions, or "what we've always known about our users" without grounding in actual user research.

**Why it's harmful:** Internal assumptions systematically miss genuine user diversity and reinforce organisational blind spots. Teams end up designing for their mental model of users, not real users.

**How to detect it:**
- Check the confidence level column — if most attributes are "assumed", this is a red flag
- Ask: "What research data supports this specific attribute?"
- Look for archetypes that suspiciously mirror the team's own demographics or preferences

**How to fix it:** Be transparent about evidence gaps. Mark all assumed attributes explicitly and create a validation plan to test them. If no research exists at all, frame the entire archetype set as "hypothesis archetypes" requiring validation.

---

## 3. Demographics as organiser

**What it looks like:** Archetypes are primarily differentiated by age, gender, income, education, or location rather than by behaviour, goals, and motivations.

**Why it's harmful:** Two users with identical demographics can have completely different goals, pain points, and behaviours. Demographic-primary archetypes miss the behavioural variation that actually matters for design decisions and risk activating stereotypes.

**How to detect it:**
- Read the archetype labels — do they reference age groups, genders, or income brackets?
- Check whether removing all demographic information would make two archetypes indistinguishable
- Ask: "If I changed this archetype's age/gender/income, would the behavioural profile change?"

**How to fix it:** Reorganise around behaviours. Demographics become context within the archetype, not the defining characteristic. If an archetype can only be distinguished from another by demographics, they are likely the same archetype.

---

## 4. Wrong granularity

**What it looks like:** Archetypes are either too specific (representing <10% of users, resulting in too many archetypes to manage) or too broad (representing >40% of users, too generic to inform decisions).

**Why it's harmful:**
- Too specific → teams can't remember or use them; decision paralysis
- Too broad → "everyone is this archetype" makes it useless for prioritisation

**How to detect it:**
- Apply the 20% heuristic: each archetype should represent roughly 20% of the user base
- If you have more than 6-7 archetypes, consider whether some can be merged
- If an archetype applies to nearly half your users, consider whether it can be split

**How to fix it:** Merge overly specific archetypes that share core behaviours. Split overly broad archetypes along the most consequential behavioural dimension — the one that changes the design response.

---

## 5. Static monuments

**What it looks like:** Archetypes are created once, polished into PDFs or printed posters, and never updated. They become frozen-in-time artefacts that progressively diverge from reality.

**Why it's harmful:** User populations shift. Market conditions change. New features attract new user types. Static archetypes become actively misleading over time, worse than having no archetypes at all.

**How to detect it:**
- Check the format — is it a "final" PDF or an editable document?
- Ask: "When was the last time these archetypes were reviewed or updated?"
- Look for archetypes that reference products, features, or market conditions that no longer exist

**How to fix it:** Use editable formats (Google Docs, Confluence, Notion). Schedule quarterly archetype reviews. Layer in insights from ongoing research, analytics, support tickets, and market surveys. The deliverable should visually signal that it's a living document.

---

## 6. Shelf-ware archetypes

**What it looks like:** Well-researched, well-documented archetypes that sit in a wiki or shared drive and are never referenced in actual decision-making.

**Why it's harmful:** The effort invested in creating archetypes yields zero return. Teams continue making decisions based on assumptions rather than user understanding.

**How to detect it:**
- Ask: "Can you name the archetypes without looking them up?"
- Ask: "When was the last time an archetype was referenced in a design review or prioritisation discussion?"
- Check whether archetype names are used as shorthand in team communication

**How to fix it:** Embed archetypes into existing rituals — design reviews, sprint planning, feature prioritisation, content strategy. Use archetype names as shorthand in meetings. Evaluate new ideas from the perspective of each archetype. If nobody uses them, diagnose why: are they not actionable? Not memorable? Not trusted?

---

## 7. Buyer-user conflation

**What it looks like:** A single archetype represents both the person who decides to purchase/adopt a product and the person who uses it daily, despite these being different people with different needs.

**Why it's harmful:** In B2B contexts especially, buyers and users have fundamentally different goals, pain points, and decision criteria. A procurement manager cares about cost, compliance, and vendor reputation; a daily user cares about workflow efficiency, learning curve, and reliability.

**How to detect it:**
- Ask: "Is the person who chooses this product the same person who uses it?"
- Look for archetypes with contradictory goals (e.g., "values cost savings" AND "wants the most feature-rich option")
- Check whether the archetype's pain points mix purchasing frustrations with usage frustrations

**How to fix it:** Create separate archetypes for buyers and users. Map the relationship between them — who influences whom, what information flows between them, and where their goals conflict.

---

## 8. Stereotype reinforcement

**What it looks like:** Archetype descriptions unconsciously encode stereotypical assumptions about user groups. This can be subtle — attributing tech-savviness to younger archetypes, price-sensitivity to certain demographics, or "simplicity" preferences to older users.

**Why it's harmful:** Reinforces organisational biases about who users are. Leads to designs that serve stereotyped user images rather than real users. Excludes users who don't fit the stereotype.

**How to detect it:**
- Read each archetype as if you were a user who doesn't fit the implicit demographic assumption — would you feel represented?
- Check whether removing any implicit demographic assumptions changes the archetype
- Ask diverse team members to review for assumptions they wouldn't make
- Look for language that "others" any group

**How to fix it:** Ground every attribute in observed behaviour, not assumed behaviour based on demographic categories. Run the inclusive design checklist (see `inclusive-design-checklist.md`). Have diverse reviewers assess the archetypes before finalising.
