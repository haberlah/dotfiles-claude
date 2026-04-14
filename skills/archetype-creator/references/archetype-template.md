# Archetype Template — Field Guide

This document defines each field in the canonical archetype template, what good vs. bad looks like, and how to fill each section.

## Table of contents

1. [Label](#label)
2. [Summary](#summary)
3. [Behavioural profile](#behavioural-profile)
4. [Motivations and goals](#motivations-and-goals)
5. [Pain points and challenges](#pain-points-and-challenges)
6. [Context](#context)
7. [Representative language](#representative-language)
8. [Design implications](#design-implications)
9. [Confidence level](#confidence-level)

---

## Label

An abstract, behavioural descriptor that immediately communicates who this archetype is.

**Format:** "The [Adjective] [Noun]" or "The [Noun] [Verb-er]"

**Good examples:**
- "The Reliability Researcher" — behaviour-first, memorable, distinct
- "The Reluctant Adopter" — captures attitude and action
- "The Efficiency Seeker" — motivation-centred
- "The Cautious Explorer" — captures a contradiction (cautious + explorer), which signals authenticity

**Bad examples:**
- "Marketing Mary" — biographical, gendered, persona-style
- "Millennials" — demographic, not behavioural
- "Power User" — too vague, means different things to different teams
- "Segment 3" — meaningless label

**Test:** Can someone unfamiliar with the research guess what this archetype cares about from the label alone? If yes, it's working.

---

## Summary

1-2 sentences capturing the essence of this archetype. Should answer: "Who is this person in the context of our product, and what defines their relationship to it?"

**Good:** "Methodical decision-makers who research extensively before committing. They value transparency and detailed specifications over brand appeal, and will delay a purchase indefinitely if they feel under-informed."

**Bad:** "A 35-year-old professional who uses our app regularly." (Demographic, vague, not behavioural.)

---

## Behavioural profile

How this archetype acts, thinks, and makes decisions in contexts relevant to the product. Focus on observable patterns, not personality traits.

**Include:**
- Decision-making style (impulsive vs. deliberate, independent vs. consensus-seeking)
- Information-seeking behaviour (depth, sources, frequency)
- Engagement patterns (when they engage, how often, in what mode)
- Workarounds and shortcuts they employ
- What they do when they encounter friction

**Exclude:**
- Personality labels (introvert/extrovert, Type A/B)
- Demographic descriptors
- Aspirational behaviours (what they wish they did)

**Good:** "Compares at least three options before deciding. Reads reviews, checks specifications, and seeks peer recommendations. Abandons a purchase flow if required information is missing. Returns to saved items multiple times before converting."

**Bad:** "An analytical thinker who values quality." (Trait-based, not behavioural.)

---

## Motivations and goals

What this archetype is trying to accomplish, split into two dimensions:

### Functional jobs
The concrete tasks or outcomes they need to achieve. These are objective, measurable, and outcome-focused.

**Format:** Verb + object + context
- "Find a reliable supplier within budget before the quarterly review"
- "Onboard new team members without disrupting existing workflows"
- "Track spending across multiple accounts in one view"

### Emotional jobs
How they want to feel as a result of using the product. These are subjective, personal, and often unstated.

**Format:** "Feel [emotion] when [context]"
- "Feel confident that they've made the right choice"
- "Feel in control of a complex process"
- "Feel respected as a knowledgeable professional, not talked down to"

**Why both matter:** Functional jobs tell you what to build. Emotional jobs tell you how it should feel. A product that completes the functional job but fails the emotional job will lose this archetype to a competitor that gets both right.

---

## Pain points and challenges

Frustrations, unmet needs, and barriers to success that this archetype experiences. These directly inform design priorities.

**Structure each pain point as:**
1. The frustration (what hurts)
2. The trigger (when/why it happens)
3. The consequence (what they do as a result — workaround, abandonment, complaint)

**Good:** "Overwhelmed by too many options without clear comparison criteria. Triggered when product pages emphasise marketing copy over specifications. Results in decision paralysis and eventual abandonment."

**Bad:** "Wants a better experience." (Vague, not actionable.)

---

## Context

The environment and situations in which this archetype operates. Behaviour is not consistent across all situations — context shapes everything.

**Include:**
- Physical environment (office, home, mobile, in-store)
- Time context (time-pressured vs. browsing, business hours vs. personal time)
- Social context (alone, with colleagues, presenting to stakeholders)
- Device and technology context (desktop, mobile, assistive technology)
- Emotional state (stressed, relaxed, curious, frustrated)
- Frequency and regularity of engagement

**Good:** "Primarily engages during work hours on a laptop, often with multiple tabs open. Time-pressured — typically has 10-15 minutes to evaluate a tool before a meeting. May use a screen reader part-time due to visual fatigue."

---

## Representative language

Phrases, sentiments, or vocabulary typical of this archetype. These should come directly from research data where possible, or be synthesised to reflect authentic voice.

**Format:** 3-5 short quotes in quotation marks.

**From research:** Direct quotes from interviews, support tickets, or survey responses.
**Synthesised:** Constructed to reflect the archetype's tone, priorities, and vocabulary based on observed patterns. Mark these as synthesised.

**Good:**
- "I just need to know it works — I don't have time to experiment." (from interview)
- "Why can't I see a side-by-side comparison?" (from support ticket)
- "I'd rather pay more for something I trust than save money on something unproven." (synthesised)

---

## Design implications

What this archetype means for product decisions. This is where archetypes become actionable. Each implication should connect an archetype characteristic to a specific design direction.

**Format:** Because [archetype characteristic], the product should [design direction].

**Good:**
- "Because this archetype researches extensively before deciding, the product should surface detailed specifications, comparison tools, and peer reviews prominently — not behind extra clicks."
- "Because this archetype is time-pressured and context-switches frequently, the product should support save-and-resume workflows and provide clear progress indicators."

**Bad:** "The product should be user-friendly." (Generic, not tied to this specific archetype.)

---

## Confidence level

An honest assessment of the evidence basis for each major attribute. This signals where the archetype is well-grounded and where it needs validation.

**Use three levels:**

| Level | Meaning | Example |
|-------|---------|---------|
| **Observed** | Directly witnessed in research data (interviews, analytics, contextual inquiry) | "5 of 8 interviewees described this exact behaviour" |
| **Inferred** | Logically derived from multiple data points but not directly observed | "Survey data shows high importance rating for reliability + analytics show comparison page visits → inferred comparison-driven decision style" |
| **Assumed** | Based on domain expertise or team judgement, not yet supported by data | "Team believes this group is price-sensitive based on market positioning, not yet validated" |

**Apply per attribute, not per archetype.** A single archetype will have a mix of observed, inferred, and assumed attributes. This granularity tells the team exactly where to focus validation efforts.
