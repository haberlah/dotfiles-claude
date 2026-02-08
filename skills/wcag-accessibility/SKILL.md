---
name: wcag-accessibility
description: "WCAG 2.2 AA accessibility compliance for React Native and Next.js applications serving users with disabilities. Use when: (1) Building accessible mobile apps (iOS/Android), (2) Building accessible web apps, (3) Implementing accessible authentication flows, (4) Creating accessible forms or multi-step wizards, (5) Adding screen reader support, (6) Implementing keyboard navigation, (7) Meeting NDIS or disability service accessibility requirements, (8) Testing accessibility compliance, (9) Creating Easy Read or cognitively accessible content, (10) Supporting assistive technologies (VoiceOver, TalkBack, NVDA, switch access, voice control)"
---

# WCAG 2.2 AA Accessibility Skill

Build accessible applications serving users with cognitive disabilities, vision impairments, motor impairments, and multiple disabilities.

## Quick Reference

| Task | Reference |
|------|-----------|
| Check specific criterion | [references/wcag-criteria.md](references/wcag-criteria.md) |
| React Native (iOS/Android) | [references/react-native-accessibility.md](references/react-native-accessibility.md) |
| Next.js web accessibility | [references/nextjs-accessibility.md](references/nextjs-accessibility.md) |
| Authentication patterns | [references/authentication-patterns.md](references/authentication-patterns.md) |
| Accessible components | [references/components.md](references/components.md) |
| Cognitive accessibility | [references/cognitive-accessibility.md](references/cognitive-accessibility.md) |
| Testing & validation | [references/testing-validation.md](references/testing-validation.md) |
| AAA criteria (optional) | [references/aaa-criteria.md](references/aaa-criteria.md) |

## Core Workflow

When building any feature:

1. **Design phase**: Check [wcag-criteria.md](references/wcag-criteria.md) for applicable criteria
2. **Implementation**: Use platform-specific patterns from [react-native-accessibility.md](references/react-native-accessibility.md) or [nextjs-accessibility.md](references/nextjs-accessibility.md)
3. **Validation**: Run automated tests + manual testing per [testing-validation.md](references/testing-validation.md)

## Critical WCAG 2.2 New Criteria

Six new criteria added in WCAG 2.2 — implement these for all new development:

| Criterion | Level | Key Requirement |
|-----------|-------|-----------------|
| 2.4.11 Focus Not Obscured | AA | Focused elements at least partially visible (not hidden by sticky headers/overlays) |
| 2.5.7 Dragging Movements | AA | Single-pointer alternatives for all drag operations |
| 2.5.8 Target Size (Minimum) | AA | Touch targets minimum 24×24 CSS pixels |
| 3.2.6 Consistent Help | A | Help mechanisms in same relative location across pages |
| 3.3.7 Redundant Entry | A | Auto-populate previously entered information |
| 3.3.8 Accessible Authentication | AA | No cognitive function tests (puzzles, memorization) — use passkeys, magic links, biometrics |

## Platform Minimums

### Touch/Click Targets

| Platform | WCAG Minimum | Recommended |
|----------|--------------|-------------|
| Web | 24×24 CSS px | 44×44 CSS px |
| iOS | 24×24 pt | 44×44 pt |
| Android | 24×24 dp | 48×48 dp |

### Color Contrast

| Element | AA Minimum | AAA Enhanced |
|---------|------------|--------------|
| Normal text (<18pt) | 4.5:1 | 7:1 |
| Large text (≥18pt or ≥14pt bold) | 3:1 | 4.5:1 |
| UI components, graphics | 3:1 | — |
| Focus indicators | 3:1 | — |

## Accessibility Props Quick Reference

### React Native

```jsx
<Pressable
  accessible={true}
  accessibilityLabel="Submit form"
  accessibilityHint="Submits your application"
  accessibilityRole="button"
  accessibilityState={{ disabled: isSubmitting }}
  accessibilityLiveRegion="polite"  // Android
>
```

**Essential roles**: `button`, `link`, `header`, `image`, `checkbox`, `radio`, `switch`, `adjustable`, `alert`

**States**: `disabled`, `selected`, `checked`, `expanded`, `busy`

### Next.js/Web

```jsx
<button
  aria-label="Submit form"
  aria-describedby="form-help"
  aria-disabled={isSubmitting}
  aria-live="polite"
>
```

**Essential ARIA**: `aria-label`, `aria-describedby`, `aria-labelledby`, `aria-live`, `aria-expanded`, `aria-current`, `aria-invalid`

**Landmarks**: `<main>`, `<nav>`, `<header>`, `<footer>`, `<aside>`, or `role="main|navigation|banner|contentinfo|complementary"`

## Form Accessibility Pattern

```jsx
// Required field with error handling
<div>
  <label htmlFor="email">
    Email <span aria-hidden="true">*</span>
  </label>
  <input
    id="email"
    type="email"
    required
    aria-required="true"
    aria-invalid={!!error}
    aria-describedby={error ? "email-error email-help" : "email-help"}
    autoComplete="email"
  />
  <p id="email-help">We'll never share your email.</p>
  {error && <p id="email-error" role="alert">{error}</p>}
</div>
```

## Decision Trees

### Authentication Method Selection

```
Is cognitive load a concern? (NDIS users: YES)
├── YES → Prefer passwordless: magic links, passkeys, biometrics
└── NO → Standard password OK if:
         ├── Supports password managers (no autocomplete="off")
         ├── Allows paste
         └── No CAPTCHAs without alternatives
```

### Multi-Step Form Design

```
Long form (>7 fields)?
├── YES → Split into steps with:
│         ├── Step indicator: "Step 2 of 5: Personal Details"
│         ├── aria-current="step" on current step
│         ├── Auto-save every 30-60 seconds
│         ├── Session timeout warnings (20+ seconds before expiry)
│         └── Pre-fill from previous steps (WCAG 3.3.7)
└── NO → Single page with clear sections
```

### Component Needs Drag-and-Drop?

```
Drag interaction required?
├── YES → MUST provide single-pointer alternative:
│         ├── Reorderable list → Up/Down buttons
│         ├── Slider → Input field + buttons
│         ├── File upload → "Choose files" button
│         └── Kanban → Dropdown to select destination
└── NO → Standard click/tap interactions
```

## Testing Checklist

Run for every feature before merge:

**Automated** (catches ~30-40% of issues):
- [ ] axe-core / jest-axe passes
- [ ] Lighthouse accessibility ≥90
- [ ] No color contrast failures

**Keyboard-only**:
- [ ] All interactive elements reachable via Tab
- [ ] Visible focus indicator on all focusable elements
- [ ] Logical tab order
- [ ] No keyboard traps
- [ ] Enter/Space activates buttons
- [ ] Escape closes modals

**Screen reader**:
- [ ] Page title announced
- [ ] Headings properly structured (h1-h6)
- [ ] Form labels announced
- [ ] Errors announced via live regions
- [ ] Dynamic content updates announced

## Do NOT

- ❌ Use `autocomplete="off"` on login forms
- ❌ Block paste in password fields
- ❌ Use color alone to convey information
- ❌ Create keyboard traps
- ❌ Use `outline: none` without replacement focus style
- ❌ Auto-play audio/video with sound
- ❌ Implement time limits without extension option
- ❌ Use images of text (except logos)
- ❌ Require drag-only interactions
- ❌ Use CAPTCHAs without accessible alternatives

## NDIS-Specific Considerations

For applications serving NDIS participants:

1. **Cognitive accessibility** is as important as technical compliance — see [cognitive-accessibility.md](references/cognitive-accessibility.md)
2. **Easy Read** alternatives for critical content
3. **Generous timeouts** — default 30-60 minute sessions
4. **Multi-language support** — NDIA supports 17 languages
5. **Support for carers/nominees** — may assist with form completion
