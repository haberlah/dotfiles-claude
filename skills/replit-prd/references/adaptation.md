# Adaptation Patterns

Handle mid-development changes when user returns with screenshots or new requirements.

## Decision Framework

```
IF change affects:
  └─ Layout/structure → Restructure NOW
  └─ Data model → Restructure NOW
  └─ Isolated new feature → Add prompt
  └─ Visual polish only → Scoped prompt

THEN:
  └─ Revise remaining prompts
  └─ Identify rollback point
  └─ Provide clear change prompt
```

## Polish Prompt

For visual/UX changes that don't affect core functionality:

```
## [Description]

> **Use Build Mode**

Make these targeted [category] improvements. Do not change core functionality.

1. [Specific change]
2. [Specific change]
3. [Specific change]

DO NOT CHANGE:
- [Protected functionality]
- API endpoints
- Database schema

**Acceptance Criteria:**
- [ ] Change 1 works
- [ ] Change 2 works
- [ ] Existing functionality unaffected

**Create checkpoint: "[Description]"**
```

## Structural Change

For changes affecting architecture or data model:

```
## Restructure: [What's Changing]

> **Use Build Mode**

[Explanation of change and rationale]

MODIFICATIONS:
1. [Database change, if any]
2. [Component structure change]
3. [State management change]

PRESERVED:
- [What remains unchanged]
- [Data to migrate]

**Acceptance Criteria:**
- [ ] New structure in place
- [ ] Data preserved/migrated
- [ ] Affected features work
- [ ] No regressions

**Create checkpoint: "Restructure - [description]"**
```

## New Feature

For isolated features that don't affect existing code:

```
## Add: [Feature Name]

> **Use Build Mode**

Add [feature description].

REQUIREMENTS:
1. [Requirement 1]
2. [Requirement 2]
3. [Requirement 3]

INTEGRATION:
- Add to [location] in existing UI
- Use [existing hook/component]
- Store in [existing/new table]

DO NOT CHANGE:
- Existing functionality
- Current layout structure
- API patterns

**Acceptance Criteria:**
- [ ] Feature works
- [ ] Integrates with existing UI
- [ ] No regressions

**Create checkpoint: "[Feature name]"**
```

## Rollback

When Agent made breaking changes:

```
Restore from checkpoint "[name]" and wait for further instructions.
```
