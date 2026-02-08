# WCAG 2.2 AAA Criteria Reference

Optional enhanced accessibility criteria beyond AA compliance. Use when specifically requested or when serving users with severe disabilities where AA minimums are insufficient.

## When to Consider AAA

AAA criteria are recommended (not required) for:
- NDIS applications serving users with severe disabilities
- Content where users cannot access alternatives
- Critical safety or health information
- Legal documents affecting user rights

## High-Value AAA Criteria for NDIS Context

### Recommended for Implementation

| Criterion | Impact | Effort | Recommendation |
|-----------|--------|--------|----------------|
| 1.4.6 Enhanced Contrast (7:1) | High for low vision | Low | Implement |
| 2.5.5 Target Size (44×44px) | High for motor disabilities | Low | Implement |
| 2.4.13 Focus Appearance | High for keyboard users | Low | Implement |
| 3.1.5 Reading Level | High for cognitive disabilities | Medium | Implement |
| 2.2.3 No Timing | High for cognitive/motor | Medium | Implement |
| 3.3.5 Help | Medium for all users | Low | Implement |
| 1.2.6 Sign Language | Critical for Deaf Auslan users | High | Consider |
| 1.2.7 Extended Audio Description | Critical for blind users | High | Consider |

---

## Perceivable (AAA)

### 1.2.6 Sign Language (Prerecorded)

Sign language interpretation for prerecorded audio content.

**NDIS context**: Auslan (Australian Sign Language) for video content. Critical for Deaf NDIS participants whose primary language is Auslan.

**Implementation**:
- Embed Auslan interpreter in video frame
- Or provide separate Auslan video with synchronized playback
- Use qualified Auslan interpreters (NAATI certified)

### 1.2.7 Extended Audio Description (Prerecorded)

Extended audio description with pauses in video.

**When needed**: When standard audio description gaps are insufficient to describe visual content.

### 1.2.8 Media Alternative (Prerecorded)

Full text alternative for prerecorded video.

**Implementation**: Provide complete transcript including all visual and auditory information.

### 1.2.9 Audio-only (Live)

Text alternative for live audio-only content.

**Implementation**: Real-time captioning (CART services) for live audio.

### 1.4.6 Contrast (Enhanced)

**7:1** contrast ratio for normal text, **4.5:1** for large text.

**Implementation**:
```css
:root {
  --text-color: #1a1a1a;      /* On white: ~16:1 */
  --text-muted: #4a4a4a;       /* On white: ~7.5:1 */
  --background: #ffffff;
}
```

**Testing**: Same tools as AA (WebAIM, DevTools) but verify 7:1 threshold.

### 1.4.7 Low or No Background Audio

Speech audio has no background sounds, OR background ≥20dB lower, OR can be turned off.

**Implementation**:
- Use isolated voice recordings
- Provide audio version without background music
- Allow independent volume control for background audio

### 1.4.8 Visual Presentation

For blocks of text:
- User can select foreground and background colors
- Width ≤80 characters (40 for CJK)
- Text not justified
- Line spacing ≥1.5, paragraph spacing ≥2×
- Text resizable to 200% without assistive technology

**Implementation**:
```jsx
function ReadingSettings({ onUpdate }) {
  return (
    <fieldset>
      <legend>Reading preferences</legend>
      
      <div>
        <label>Text color</label>
        <input type="color" onChange={e => onUpdate({ textColor: e.target.value })} />
      </div>
      
      <div>
        <label>Background color</label>
        <input type="color" onChange={e => onUpdate({ bgColor: e.target.value })} />
      </div>
      
      <div>
        <label>Line spacing</label>
        <select onChange={e => onUpdate({ lineHeight: e.target.value })}>
          <option value="1.5">Normal (1.5)</option>
          <option value="2">Large (2)</option>
          <option value="2.5">Extra large (2.5)</option>
        </select>
      </div>
    </fieldset>
  );
}
```

### 1.4.9 Images of Text (No Exception)

No images of text, even for customizable ones. Only exception: Essential (logos).

---

## Operable (AAA)

### 2.1.3 Keyboard (No Exception)

All functionality operable via keyboard with no exceptions.

**Difference from AA**: AA allows exceptions for path-dependent input (drawing). AAA has no exceptions.

### 2.2.3 No Timing

No time limits except for real-time events and 20+ hour limits.

**NDIS context**: Critical for users with cognitive disabilities who need unlimited time.

**Implementation**:
```jsx
// Remove all session timeouts for logged-in users
function SessionManager({ children }) {
  // No automatic logout
  // User must explicitly sign out
  return children;
}

// Or provide "no timeout" preference
function TimeoutSettings() {
  return (
    <label>
      <input type="checkbox" onChange={setNoTimeout} />
      Keep me signed in until I sign out
    </label>
  );
}
```

### 2.2.4 Interruptions

Interruptions can be postponed or suppressed (except emergencies).

**Implementation**:
- Allow users to disable notifications
- Queue non-critical messages
- Only interrupt for genuine emergencies

### 2.2.5 Re-authenticating

Data preserved and submittable after re-authentication.

**Implementation**:
- Auto-save form data to local storage
- Restore session state after re-login
- Never lose user's work due to session expiry

### 2.2.6 Timeouts

Warn users about data loss from inactivity timeouts at start of process.

**Implementation**:
```jsx
function FormWithTimeoutWarning() {
  return (
    <>
      <div role="alert" className="timeout-warning">
        <strong>Important:</strong> Your session will expire after 30 minutes 
        of inactivity. Your progress is saved automatically every 60 seconds.
      </div>
      <Form />
    </>
  );
}
```

### 2.3.2 Three Flashes

No content flashes more than 3 times per second. Period. (AA allows if below threshold.)

### 2.3.3 Animation from Interactions

Motion animation triggered by interaction can be disabled.

**Implementation**:
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation: none !important;
    transition: none !important;
  }
}
```

```jsx
// Provide explicit toggle
function MotionSettings() {
  const [reduceMotion, setReduceMotion] = useState(false);
  
  useEffect(() => {
    document.body.classList.toggle('reduce-motion', reduceMotion);
  }, [reduceMotion]);
  
  return (
    <label>
      <input 
        type="checkbox" 
        checked={reduceMotion}
        onChange={e => setReduceMotion(e.target.checked)}
      />
      Reduce motion and animations
    </label>
  );
}
```

### 2.4.8 Location

Information about user's location within site available.

**Implementation**: Breadcrumbs, site map, "you are here" indicators.

### 2.4.9 Link Purpose (Link Only)

Link purpose determinable from link text alone (no context).

**Difference from AA**: AA allows context (surrounding paragraph). AAA requires standalone clarity.

```html
<!-- AA acceptable -->
<p>Read our <a href="/privacy">privacy policy</a>.</p>

<!-- AAA required -->
<a href="/privacy">Read our privacy policy</a>
```

### 2.4.10 Section Headings

Section headings used to organize content.

**Implementation**: Every distinct section has a heading. No content islands without headings.

### 2.4.12 Focus Not Obscured (Enhanced)

Focused element **entirely** visible (not just partially as in AA).

**Implementation**:
```css
html {
  scroll-padding-top: 120px;  /* Extra padding beyond AA */
  scroll-padding-bottom: 100px;
}

/* Ensure no overlapping sticky elements */
.sticky-header {
  max-height: 80px;  /* Limit sticky element size */
}
```

### 2.4.13 Focus Appearance

Focus indicator:
- Area ≥ perimeter × 2 CSS pixels
- Contrast ≥ 3:1 between focused and unfocused states
- Contrast ≥ 3:1 against adjacent colors

**Implementation**:
```css
:focus-visible {
  outline: 3px solid #0066cc;
  outline-offset: 3px;
  box-shadow: 0 0 0 6px rgba(0, 102, 204, 0.3);
}

/* For dark backgrounds */
.dark-section :focus-visible {
  outline-color: #66b3ff;
  box-shadow: 0 0 0 6px rgba(102, 179, 255, 0.3);
}
```

### 2.5.5 Target Size (Enhanced)

Touch targets **44×44 CSS pixels** minimum (vs 24×24 for AA).

**Implementation**:
```css
button, 
a,
[role="button"],
input[type="checkbox"],
input[type="radio"] {
  min-width: 44px;
  min-height: 44px;
}
```

```jsx
// React Native
<Pressable
  style={{ minWidth: 44, minHeight: 44, padding: 12 }}
  hitSlop={{ top: 0, bottom: 0, left: 0, right: 0 }}  /* No need with 44px */
>
```

### 2.5.6 Concurrent Input Mechanisms

Don't restrict input to single modality.

**Implementation**: Allow keyboard, mouse, touch, voice, switch all concurrently. Never disable one when another is detected.

---

## Understandable (AAA)

### 3.1.3 Unusual Words

Mechanism to identify definitions for unusual words, idioms, jargon.

**Implementation**:
```jsx
function GlossaryTerm({ term, definition, children }) {
  return (
    <span className="glossary-term">
      <dfn>{children}</dfn>
      <span className="definition" role="tooltip">
        <strong>{term}:</strong> {definition}
      </span>
    </span>
  );
}

// Usage
<p>
  Your <GlossaryTerm term="NDIS plan" definition="A document that lists the funded supports you can access">
    NDIS plan
  </GlossaryTerm> will be reviewed annually.
</p>
```

### 3.1.4 Abbreviations

Mechanism to identify expanded form of abbreviations.

**Implementation**:
```html
<abbr title="National Disability Insurance Scheme">NDIS</abbr>
```

Or provide glossary page linked from all abbreviations.

### 3.1.5 Reading Level

Content readable at lower secondary education level (Grade 7-9), OR supplementary content/version provided.

**NDIS context**: Critical. Many NDIS participants have intellectual disabilities or acquired brain injuries affecting reading comprehension.

**Implementation**:
1. Write at Grade 6-8 reading level
2. Test with Flesch-Kincaid Grade Level (target ≤8)
3. Provide Easy Read version for complex content

**Testing tools**:
- Hemingway Editor (hemingwayapp.com)
- Readable (readable.com)
- Microsoft Word readability statistics

### 3.1.6 Pronunciation

Mechanism to identify pronunciation of ambiguous words.

**Implementation**: For words where meaning depends on pronunciation, provide phonetic guide or audio.

```html
<span>
  The <ruby>lead<rp>(</rp><rt>leed</rt><rp>)</rp></ruby> developer 
  will <ruby>lead<rp>(</rp><rt>leed</rt><rp>)</rp></ruby> the project.
</span>
```

### 3.2.5 Change on Request

Context changes only on user request, OR can be turned off.

**Implementation**:
- No automatic redirects
- No auto-opening new windows
- Form submission only on explicit submit action
- Provide "open in new tab" as user choice, not default

### 3.3.5 Help

Context-sensitive help available.

**NDIS context**: Highly recommended. Users benefit from inline help.

**Implementation**:
```jsx
function FieldWithHelp({ label, help, children }) {
  const [showHelp, setShowHelp] = useState(false);
  const helpId = useId();
  
  return (
    <div>
      <label>
        {label}
        <button 
          type="button"
          aria-expanded={showHelp}
          aria-controls={helpId}
          onClick={() => setShowHelp(!showHelp)}
        >
          <span className="sr-only">Help for {label}</span>
          ?
        </button>
      </label>
      
      {showHelp && (
        <div id={helpId} className="help-text">
          {help}
        </div>
      )}
      
      {children}
    </div>
  );
}
```

### 3.3.6 Error Prevention (All)

For all user submissions (not just legal/financial as in AA):
- Reversible, OR
- Checked with correction opportunity, OR
- Confirmed before final submission

**Implementation**: Review page before all form submissions.

### 3.3.9 Accessible Authentication (Enhanced)

No cognitive function tests at all. Object recognition (allowed at AA) not permitted at AAA.

**Allowed methods**:
- Passkeys only
- Magic links only
- Biometrics only
- Hardware security keys only
- OAuth only

**Not allowed** (even with alternatives):
- Password entry (unless paste + autocomplete supported)
- Any CAPTCHA including object recognition
- SMS code transcription

---

## Robust (AAA)

No additional AAA criteria in Robust principle.

---

## Implementation Priority for NDIS Applications

### Phase 1: Quick Wins (Week 1-2)

Low effort, high impact:
- [ ] 1.4.6 Enhanced contrast (7:1) — CSS changes
- [ ] 2.5.5 Target size (44×44px) — CSS changes
- [ ] 2.4.13 Focus appearance — CSS changes
- [ ] 3.3.5 Help — Add contextual help

### Phase 2: Content Improvements (Week 3-4)

Medium effort:
- [ ] 3.1.5 Reading level — Rewrite content
- [ ] 3.1.3 Unusual words — Add glossary
- [ ] 3.1.4 Abbreviations — Mark up abbreviations
- [ ] 2.4.8 Location — Add breadcrumbs

### Phase 3: Session Management (Week 5-6)

Medium effort:
- [ ] 2.2.3 No timing — Remove timeouts
- [ ] 2.2.5 Re-authenticating — Preserve data
- [ ] 3.2.5 Change on request — Audit context changes

### Phase 4: Multimedia (Ongoing)

High effort:
- [ ] 1.2.6 Sign language (Auslan) — For key videos
- [ ] 1.2.7 Extended audio description — For key videos

---

## Cost-Benefit Summary

| Criterion | Implementation Cost | User Benefit | ROI |
|-----------|--------------------:|-------------:|----:|
| Enhanced contrast | Low | High | ⭐⭐⭐⭐⭐ |
| 44×44px targets | Low | High | ⭐⭐⭐⭐⭐ |
| Focus appearance | Low | Medium | ⭐⭐⭐⭐ |
| No timing | Medium | High | ⭐⭐⭐⭐ |
| Reading level | Medium | High | ⭐⭐⭐⭐ |
| Help | Low | Medium | ⭐⭐⭐⭐ |
| Glossary | Medium | Medium | ⭐⭐⭐ |
| Auslan interpretation | High | High (Deaf users) | ⭐⭐⭐ |
| Extended audio description | High | High (blind users) | ⭐⭐⭐ |
| Color customization | High | Medium | ⭐⭐ |
