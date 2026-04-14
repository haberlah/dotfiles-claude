# Clustering Guide — From Raw Data to Archetypes

How to identify behavioural clusters from research data and turn them into archetype candidates.

## Table of contents

1. [Approach selection](#approach-selection)
2. [Qualitative affinity mapping](#qualitative-affinity-mapping)
3. [Needs-based clustering](#needs-based-clustering)
4. [Attitudinal clustering](#attitudinal-clustering)
5. [Mixed-method clustering](#mixed-method-clustering)
6. [The 20% heuristic](#the-20-heuristic)
7. [How many archetypes](#how-many-archetypes)
8. [Cluster quality checks](#cluster-quality-checks)

---

## Approach selection

Choose your clustering approach based on what data you have:

| Data available | Recommended approach |
|---|---|
| Interview transcripts, field notes, diary studies | Qualitative affinity mapping |
| User's verbal description of their audience | Qualitative affinity mapping (lighter version) |
| Survey data (100+ respondents) | Mixed-method or statistical clustering |
| Analytics + qualitative data | Mixed-method clustering |
| User needs/problems well understood | Needs-based clustering |
| Attitude/belief survey data | Attitudinal clustering |

If the user only has verbal knowledge (no formal research), use a lightweight qualitative approach and mark all resulting archetypes as "hypothesis — assumed" confidence level.

---

## Qualitative affinity mapping

Best for: interview data, field notes, observation notes, support tickets.

### Process

1. **Extract atomic insights** — From each data source, extract individual observations about user behaviour, goals, pain points, and context. Each insight should be one discrete observation.
   - Good: "User checked three competitor sites before returning to make a purchase"
   - Bad: "User is thorough" (interpretation, not observation)

2. **Sort by behavioural dimension** — Group insights by the behavioural dimension they reveal:
   - Decision-making style
   - Information needs
   - Risk tolerance
   - Time orientation (planning vs. reactive)
   - Social influence (independent vs. peer-driven)
   - Goal orientation (efficiency vs. thoroughness vs. exploration)

3. **Identify natural clusters** — Look for groups of insights that co-occur. When the same users exhibit multiple related behaviours, those behaviours form a cluster.
   - Example: Users who research extensively also tend to be risk-averse, value transparency, and delay decisions under uncertainty. This is a natural cluster.

4. **Name the cluster** — Give each cluster a working label based on its defining behaviour or motivation. Use "The [Descriptor]" format.

5. **Validate distinctness** — Each cluster should be distinguishable from every other cluster on at least 2-3 behavioural dimensions. If two clusters only differ on one dimension, consider merging them.

### When working from verbal description only

If the user is describing their audience from experience rather than formal research:

1. Ask them to describe 3-5 "types" of users they see repeatedly
2. For each type, probe for specific behaviours (not demographics or personality):
   - "What do they actually *do* when they first encounter the product?"
   - "What makes them different from the other types in practice?"
   - "When do they struggle? When do they succeed?"
   - "What do they care about most?"
3. Look for behavioural patterns across their descriptions
4. Propose clusters and let the user validate against their experience

---

## Needs-based clustering

Best for: when underlying user needs/problems are well understood.

### Process

1. **List all user needs** identified in research, organised by type:
   - Functional needs (what they need to accomplish)
   - Emotional needs (how they need to feel)
   - Social needs (how they need to be perceived)
   - Contextual needs (what their environment demands)

2. **Identify need bundles** — Look for needs that consistently co-occur. Users who need X often also need Y and Z.
   - Example: Users who need speed also need mobile access and short-form content. Users who need depth also need desktop access and save-for-later.

3. **Form clusters around need bundles** — Each cluster represents a distinct combination of needs that drives different product requirements.

4. **Name by primary need** — The label should reference the most defining need in the bundle.

**Strength:** Directly actionable — each archetype maps to a distinct set of product requirements.
**Weakness:** May miss attitudinal and contextual nuances that shape *how* users pursue their needs.

---

## Attitudinal clustering

Best for: survey data with Likert-scale attitude questions.

### Process

1. **Identify key attitude dimensions** from survey data:
   - Trust in technology vs. scepticism
   - Preference for simplicity vs. control
   - Self-reliance vs. support-seeking
   - Risk tolerance vs. risk aversion
   - Price sensitivity vs. value orientation

2. **Map respondents along dimensions** — Where does each respondent fall on each attitude scale?

3. **Identify natural groupings** — Look for clusters of respondents who share similar positions across multiple attitude dimensions.

4. **Cross-reference with behaviours** — Validate that attitudinal clusters correspond to different behavioural patterns. Attitudes that don't translate to different behaviours aren't useful for design decisions.

**Strength:** Captures the *why* behind behaviour — two users might do the same thing for different reasons.
**Weakness:** Attitudes can shift over time; requires periodic re-validation.

---

## Mixed-method clustering

Best for: combining qualitative and quantitative data sources.

### Process

1. **Start qualitative** — Use affinity mapping or needs-based clustering on interview/observation data to identify candidate clusters (3-7 candidates).

2. **Validate quantitatively** — If survey data exists (100+ respondents), check whether the qualitative clusters hold up:
   - Do survey responses cluster along the same dimensions?
   - What proportion of respondents fall into each cluster?
   - Are there clusters visible in quantitative data that qualitative research missed?

3. **Enrich with analytics** — If product analytics are available, check whether each cluster corresponds to distinct usage patterns:
   - Engagement frequency and depth
   - Feature usage patterns
   - Conversion/retention differences
   - Path through the product

4. **Reconcile** — Merge qualitative and quantitative views. Qualitative provides the "why" and behavioural texture; quantitative provides proportional sizing and pattern validation.

**Strength:** Most robust approach — triangulates across data sources.
**Weakness:** Requires multiple data sources; not always available.

---

## The 20% heuristic

A practical rule for calibrating archetype granularity:

> If the level of detail in an archetype reflects roughly 20% of all users, the archetype is optimally scoped.

**Too broad (>40%):** "Everyone is this archetype" — it's not differentiating. Split along the most consequential behavioural dimension.

**About right (15-30%):** Each archetype represents a meaningful, manageable portion of the user base.

**Too narrow (<10%):** Too many archetypes to remember or use. Merge with the most behaviourally similar neighbour.

This is a heuristic, not a rule. Some products legitimately have one dominant archetype (50%+) and several smaller ones. The test is: does each archetype drive different design decisions?

---

## How many archetypes

| Team/product context | Recommended count | Reasoning |
|---|---|---|
| Early-stage product, limited research | 2-3 | Focus on the most consequential behavioural differences |
| Established product, moderate research | 3-5 | Covers primary user variation without overwhelming |
| Large/diverse user base, rich data | 5-7 | More granularity justified when data supports it |
| Enterprise with interactive tooling | 7+ | Feasible when teams have search/filter tools to access archetypes on demand |

**Cognitive limit:** Decision-makers can hold 5-7 archetypes in working memory. Beyond that, archetypes need interactive tooling (searchable wiki, database) rather than a static document.

**Default:** Start with 3-5 unless there's a strong reason to deviate. You can always split later; merging is harder once archetypes are socialised.

---

## Cluster quality checks

Before promoting a cluster to archetype status, it should pass these checks:

1. **Distinctness** — Is this cluster meaningfully different from every other cluster on at least 2-3 dimensions?
2. **Internal coherence** — Do the behaviours, goals, and pain points within this cluster logically co-occur?
3. **Actionability** — Would this cluster drive different design decisions than the others? If not, it's not a useful archetype.
4. **Recognisability** — Would someone familiar with the user base say "yes, I've seen this type of user"?
5. **Proportionality** — Does this cluster represent a meaningful portion of the user base (roughly 15-30%)?
6. **Stability** — Is this cluster likely to persist over time, or is it a temporary artefact of current conditions?
7. **Non-demographic** — Can this cluster be defined entirely by behaviour and motivation, without reference to demographics?
