# WCAG 2.2 AA Complete Criteria Reference

All 50 success criteria required for WCAG 2.2 AA compliance (30 Level A + 20 Level AA).

## Table of Contents

1. [Perceivable](#principle-1-perceivable)
2. [Operable](#principle-2-operable)
3. [Understandable](#principle-3-understandable)
4. [Robust](#principle-4-robust)

---

## Principle 1: Perceivable

### Level A

**1.1.1 Non-text Content**
- All images need `alt` text (or `alt=""` if decorative)
- Icons need accessible labels
- CAPTCHA needs text alternative describing purpose + audio alternative

**1.2.1 Audio-only and Video-only (Prerecorded)**
- Audio-only: Provide transcript
- Video-only: Provide audio description or transcript

**1.2.2 Captions (Prerecorded)**
- All prerecorded video with audio needs synchronized captions

**1.2.3 Audio Description or Media Alternative (Prerecorded)**
- Video needs audio description track OR full text transcript

**1.3.1 Info and Relationships**
- Structure conveyed through semantic HTML, not just visual presentation
- Use proper heading hierarchy (h1-h6)
- Use `<table>` for data tables with `<th scope="col|row">`
- Use `<fieldset>`/`<legend>` for form groups
- Use `<label>` associated with inputs

**1.3.2 Meaningful Sequence**
- Reading order must be programmatically determinable
- CSS visual order must match DOM order for interactive elements

**1.3.3 Sensory Characteristics**
- Instructions don't rely solely on shape, color, size, or location
- ❌ "Click the green button"
- ✅ "Click Submit (the green button below)"

**1.4.1 Use of Color**
- Color never the only means of conveying information
- Links need underline OR 3:1 contrast + non-color indicator on hover/focus
- Form errors need icon + text, not just red color
- Charts need patterns/textures in addition to colors

**1.4.2 Audio Control**
- Auto-playing audio >3 seconds can be paused, stopped, or volume controlled
- Control at top of page, keyboard accessible

### Level AA

**1.2.4 Captions (Live)**
- Live audio content has synchronized captions

**1.2.5 Audio Description (Prerecorded)**
- Prerecorded video includes audio description for visual-only content

**1.3.4 Orientation**
- Content not restricted to portrait or landscape
- Exception: Essential orientation (piano keyboard, check deposit)

**1.3.5 Identify Input Purpose**
- Form inputs have programmatic purpose via `autocomplete` attribute
- Required for: name, email, password, address, phone, credit card, etc.

```html
<input type="email" autocomplete="email">
<input type="tel" autocomplete="tel">
<input type="text" autocomplete="given-name">
<input type="text" autocomplete="street-address">
```

**1.4.3 Contrast (Minimum)**
- Normal text: **4.5:1** contrast ratio
- Large text (18pt+ or 14pt+ bold): **3:1** contrast ratio
- Test with WebAIM Contrast Checker or Chrome DevTools

**1.4.4 Resize Text**
- Text resizable to **200%** without loss of content or functionality
- Use relative units (rem, em, %) not fixed pixels for text
- Avoid fixed-height containers for text

**1.4.5 Images of Text**
- Use real text, not images of text
- Exception: Logos, essential images (screenshots)

**1.4.10 Reflow**
- Content reflows at 400% zoom without horizontal scrolling
- Equivalent to 320px viewport width
- Use responsive design, avoid fixed widths

```css
.container {
  max-width: 75ch;
  width: 100%;
}
img {
  max-width: 100%;
  height: auto;
}
```

**1.4.11 Non-text Contrast**
- UI components (buttons, inputs, icons) have **3:1** contrast
- Graphical objects (charts, icons) have **3:1** contrast
- Focus indicators have **3:1** contrast

**1.4.12 Text Spacing**
- No content loss when user applies:
  - Line height: 1.5× font size
  - Paragraph spacing: 2× font size
  - Letter spacing: 0.12× font size
  - Word spacing: 0.16× font size

```css
/* Test with these values */
p {
  line-height: 1.5 !important;
  letter-spacing: 0.12em !important;
  word-spacing: 0.16em !important;
}
p + p {
  margin-top: 2em !important;
}
```

**1.4.13 Content on Hover or Focus**
- Hover/focus-triggered content (tooltips, submenus):
  - **Dismissible**: Can close with Escape without moving pointer/focus
  - **Hoverable**: User can move pointer to new content without it disappearing
  - **Persistent**: Remains visible until dismissed, hover/focus removed, or invalid

---

## Principle 2: Operable

### Level A

**2.1.1 Keyboard**
- All functionality accessible via keyboard
- All interactive elements focusable and operable
- Custom widgets need keyboard handlers

**2.1.2 No Keyboard Trap**
- Focus never becomes trapped
- Users can always Tab away from any component
- If non-standard keys needed (arrows in widget), document the method

**2.1.4 Character Key Shortcuts**
- Single-character shortcuts (a-z, 0-9, punctuation) can be:
  - Turned off, OR
  - Remapped to include modifier key, OR
  - Active only when component has focus

**2.2.1 Timing Adjustable**
- Time limits can be:
  - **Turned off** before encountering, OR
  - **Adjusted** (10× default), OR
  - **Extended** (warned 20+ seconds before, allow 10+ extensions via simple action)
- Exceptions: Real-time events (auctions), essential timing, >20 hour limit

**2.2.2 Pause, Stop, Hide**
- Moving, blinking, scrolling content >5 seconds can be paused/stopped/hidden
- Auto-updating information can be paused/stopped/controlled
- Exception: Essential animations

**2.3.1 Three Flashes or Below Threshold**
- No content flashes more than 3 times per second
- Or flash is below general flash and red flash thresholds

**2.4.1 Bypass Blocks**
- Skip link to bypass repeated content
- Proper heading structure
- ARIA landmarks

```jsx
<a href="#main-content" className="sr-only focus:not-sr-only">
  Skip to main content
</a>
```

**2.4.2 Page Titled**
- Pages have descriptive, unique titles
- Format: "Page Name | Site Name" or "Page Name - Site Name"

**2.4.3 Focus Order**
- Focus order is logical and meaningful
- Matches visual reading order
- Modal focus trapped within modal

**2.4.4 Link Purpose (In Context)**
- Link purpose determinable from link text alone OR link text + context
- ❌ "Click here", "Read more"
- ✅ "Read more about accessibility testing"

**2.5.1 Pointer Gestures**
- Multi-point gestures (pinch, multi-finger swipe) have single-pointer alternatives
- Path-based gestures (drawing) have alternatives

**2.5.2 Pointer Cancellation**
- Down-event doesn't trigger action (use up-event)
- Action can be aborted by moving pointer off target before release
- Up-event reverses down-event action
- Exception: Essential down-event (piano keys)

**2.5.3 Label in Name**
- Visible text labels included in accessible name
- Accessible name starts with visible text

```jsx
// ❌ Bad
<button aria-label="Submit this contact form">Submit</button>

// ✅ Good  
<button aria-label="Submit">Submit</button>
```

**2.5.4 Motion Actuation**
- Motion-triggered functions (shake to undo) have UI alternatives
- Motion can be disabled to prevent accidental actuation
- Exception: Motion essential for function

### Level AA

**2.4.5 Multiple Ways**
- Multiple ways to locate pages within a site:
  - Navigation menu
  - Search function
  - Site map
  - Table of contents

**2.4.6 Headings and Labels**
- Headings and labels describe topic or purpose
- ❌ "Section 1", "Form"
- ✅ "Personal Information", "Contact Form"

**2.4.7 Focus Visible**
- Keyboard focus indicator always visible
- Minimum 2px solid outline recommended

```css
:focus {
  outline: 3px solid #0066cc;
  outline-offset: 2px;
}
:focus:not(:focus-visible) {
  outline: none;
}
:focus-visible {
  outline: 3px solid #0066cc;
  outline-offset: 2px;
}
```

**2.4.11 Focus Not Obscured (Minimum)** 🆕
- Focused element not entirely hidden by sticky headers, overlays, or banners
- At least part of the focused element must be visible

```css
html {
  scroll-padding-top: 100px;  /* Height of sticky header */
  scroll-padding-bottom: 80px;
}
*:focus {
  scroll-margin-top: 120px;
  scroll-margin-bottom: 100px;
}
```

**2.5.7 Dragging Movements** 🆕
- All drag-and-drop has single-pointer alternative
- Reorderable lists: Add up/down buttons
- Sliders: Add input field or +/- buttons
- File upload zones: Add file picker button

```jsx
<li draggable>
  <button aria-label="Move up" onClick={() => moveUp(i)}>↑</button>
  <button aria-label="Move down" onClick={() => moveDown(i)}>↓</button>
  <span>{item.name}</span>
</li>
```

**2.5.8 Target Size (Minimum)** 🆕
- Touch targets minimum **24×24 CSS pixels**
- OR adequate spacing (24px circle centered on target doesn't overlap others)
- Exceptions: Inline links in text, user agent controlled, essential small size

| Platform | Minimum | Recommended |
|----------|---------|-------------|
| Web | 24×24 CSS px | 44×44 CSS px |
| iOS | 24×24 pt | 44×44 pt |
| Android | 24×24 dp | 48×48 dp |

---

## Principle 3: Understandable

### Level A

**3.1.1 Language of Page**
- Default language specified via `lang` attribute

```html
<html lang="en">
<html lang="en-AU">
```

**3.2.1 On Focus**
- No context change on focus alone
- ❌ Submitting form when field receives focus
- ❌ Opening new window on focus

**3.2.2 On Input**
- No unexpected context change on input
- ❌ Auto-submit on dropdown selection
- ✅ OK if user advised beforehand

**3.2.6 Consistent Help** 🆕
- Help mechanisms in **same relative order** across pages:
  - Human contact details
  - Human contact mechanism (chat, form)
  - Self-help option (FAQ)
  - Automated contact (chatbot)

**3.3.1 Error Identification**
- Errors identified and described in text
- Error message near the erroneous input
- Use `aria-invalid="true"` on invalid fields

**3.3.2 Labels or Instructions**
- Labels or instructions provided for user input
- Required fields indicated (asterisk + legend or aria-required)
- Format requirements shown (e.g., "MM/DD/YYYY")

**3.3.7 Redundant Entry** 🆕
- Previously entered info auto-populated or selectable
- ❌ Asking for email again on page 3 of form
- ✅ "Use same as shipping address" checkbox
- Exception: Essential re-entry (confirmation), security, expired data

### Level AA

**3.1.2 Language of Parts**
- Language changes marked with `lang` attribute

```html
<p>The French word <span lang="fr">bonjour</span> means hello.</p>
```

**3.2.3 Consistent Navigation**
- Navigation mechanisms in same relative order across pages
- Don't move navigation between pages

**3.2.4 Consistent Identification**
- Components with same function identified consistently
- Search icon always labeled "Search", not sometimes "Find"
- Submit buttons consistently labeled

**3.3.3 Error Suggestion**
- Specific error correction suggestions provided
- ❌ "Invalid email"
- ✅ "Please include an @ symbol in the email address"

**3.3.4 Error Prevention (Legal, Financial, Data)**
- For legal/financial submissions, at least one of:
  - **Reversible**: Submissions can be reversed
  - **Checked**: Data checked for errors with correction opportunity
  - **Confirmed**: Review/confirm before final submission

**3.3.8 Accessible Authentication (Minimum)** 🆕
- No cognitive function tests for authentication:
  - ❌ Memorizing password without manager support
  - ❌ Transcribing one-time codes
  - ❌ Solving puzzles/CAPTCHAs (without alternative)
  - ❌ Pattern recognition
  
- **Allowed methods**:
  - Password managers (support autocomplete, allow paste)
  - Passkeys/WebAuthn
  - Magic links (email-based)
  - Biometric authentication
  - OAuth/social login
  - Hardware security keys
  - Object recognition CAPTCHAs (at AA level)

```html
<!-- Support password managers -->
<input type="email" autocomplete="username email">
<input type="password" autocomplete="current-password">
<!-- Never use autocomplete="off", never block paste -->
```

---

## Principle 4: Robust

### Level A

**4.1.2 Name, Role, Value**
- All UI components have accessible name, role, value, and states
- Use semantic HTML OR proper ARIA
- Custom widgets must expose states (expanded, selected, checked)

```jsx
<button 
  aria-expanded={isOpen}
  aria-controls="menu-id"
>
  Menu
</button>
```

### Level AA

**4.1.3 Status Messages**
- Status messages announced without receiving focus
- Use ARIA live regions

```jsx
// Polite - non-urgent updates
<div aria-live="polite" aria-atomic="true">
  {statusMessage}
</div>

// Assertive - errors (use sparingly)
<div role="alert">
  {errorMessage}
</div>

// Status role - implicitly polite
<div role="status">
  {loadingMessage}
</div>
```

---

## Removed Criterion

**4.1.1 Parsing** — Removed in WCAG 2.2. Modern browsers handle parsing errors.

---

## Quick Compliance Checklist

### Must-Have (Blocking Issues)

- [ ] All images have alt text
- [ ] Color contrast meets minimums (4.5:1 text, 3:1 UI)
- [ ] All interactive elements keyboard accessible
- [ ] Focus visible on all focusable elements
- [ ] Form inputs have associated labels
- [ ] Page has proper heading hierarchy
- [ ] Language declared on html element
- [ ] No keyboard traps
- [ ] Touch targets ≥24×24px
- [ ] No cognitive tests for authentication

### Should-Have (Important)

- [ ] Skip link provided
- [ ] Error messages descriptive and near fields
- [ ] ARIA live regions for dynamic content
- [ ] Consistent navigation order
- [ ] Multiple ways to find content
- [ ] Help in consistent location
- [ ] Previously entered data preserved
- [ ] Drag operations have alternatives

### Nice-to-Have (Enhanced)

- [ ] AAA contrast ratios (7:1)
- [ ] Extended audio descriptions
- [ ] Sign language interpretation
- [ ] 44×44px touch targets (exceeds minimum)
