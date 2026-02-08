# Cognitive Accessibility for NDIS Applications

Guidelines for serving users with intellectual disabilities, acquired brain injuries, autism spectrum conditions, ADHD, anxiety, depression, and other cognitive disabilities.

## Table of Contents

1. [Core Principles](#core-principles)
2. [Plain Language](#plain-language)
3. [Easy Read Standards](#easy-read-standards)
4. [Navigation and Wayfinding](#navigation-and-wayfinding)
5. [Forms and Data Entry](#forms-and-data-entry)
6. [Error Prevention and Recovery](#error-prevention-and-recovery)
7. [Memory and Attention](#memory-and-attention)
8. [Implementation Patterns](#implementation-patterns)

---

## Core Principles

### W3C Cognitive Accessibility Guidance

1. **Help users understand what things are and how to use them**
2. **Help users find what they need**
3. **Use clear content**
4. **Help users avoid mistakes**
5. **Help users maintain focus**
6. **Ensure processes do not rely on memory**
7. **Provide help and support**
8. **Support adaptation and personalization**

### NDIS-Specific Considerations

| User Group | Common Challenges | Design Response |
|------------|-------------------|-----------------|
| Intellectual disability | Reading, memory, abstraction | Easy Read, chunked info, concrete examples |
| Acquired brain injury | Fatigue, attention, processing | Short sessions, auto-save, clear progress |
| Autism spectrum | Sensory overload, routine disruption | Predictable layout, minimal animation |
| ADHD | Attention, task completion | Clear structure, progress feedback |
| Anxiety/depression | Decision fatigue, overwhelm | Simplified choices, supportive messaging |
| Dementia | Memory, orientation | Consistent layout, clear landmarks |

---

## Plain Language

### Readability Targets

| Level | Flesch-Kincaid Grade | Use Case |
|-------|---------------------|----------|
| Standard | Grade 8 (age 13-14) | General content |
| Simple | Grade 6 (age 11-12) | Critical information |
| Easy Read | Grade 3-4 (age 8-10) | Accessibility version |

### Plain Language Rules

**Sentence structure:**
- One idea per sentence
- Maximum 15-20 words per sentence
- Active voice: "We will send you a letter" not "A letter will be sent"
- Positive framing: "Please include" not "Do not forget to include"

**Word choice:**
- Use common words: "use" not "utilise", "help" not "facilitate"
- Define technical terms on first use
- Avoid acronyms; if necessary, spell out first time
- Use the same word consistently (don't switch between "form" and "application")

**Structure:**
- Most important information first
- Break complex info into numbered steps
- Use headings to chunk content
- Provide summaries for long content

### Plain Language Examples

```
❌ "Failure to provide requisite documentation may result in 
   the rejection of your application and necessitate resubmission."

✅ "Please include all required documents with your application.
   If documents are missing, we will ask you to send them again."
```

```
❌ "The NDIS provides funding for reasonable and necessary supports 
   to help participants pursue their goals and live an ordinary life."

✅ "The NDIS gives you money for the support you need.
   This support helps you reach your goals.
   This support helps you live the life you want."
```

---

## Easy Read Standards

### Australian Easy Read Guidelines

**Format requirements:**
- Sans-serif font (Arial, Calibri)
- Minimum 14pt font size (16pt preferred)
- 1.5 line spacing minimum
- Left-aligned text (never justified)
- High contrast (black on white/cream)
- Plenty of white space

**Content structure:**
- One idea per sentence
- One sentence per line (or logical phrase)
- Maximum 5 pages per document
- Start each section on a new page
- Number pages clearly

**Images:**
- Place image to the left of text
- Image should directly illustrate the text
- Use consistent image style
- Caption images if meaning not obvious
- Avoid decorative images

### Easy Read Content Pattern

```html
<article class="easy-read">
  <section>
    <div class="easy-read-item">
      <img src="form-icon.png" alt="" class="easy-read-image">
      <p class="easy-read-text">
        You need to fill in a form.
      </p>
    </div>
    
    <div class="easy-read-item">
      <img src="documents-icon.png" alt="" class="easy-read-image">
      <p class="easy-read-text">
        You need to send us some documents.
      </p>
    </div>
    
    <div class="easy-read-item">
      <img src="letter-icon.png" alt="" class="easy-read-image">
      <p class="easy-read-text">
        We will send you a letter with our decision.
      </p>
    </div>
  </section>
</article>
```

```css
.easy-read {
  font-family: Arial, sans-serif;
  font-size: 16pt;
  line-height: 1.8;
  max-width: 600px;
}

.easy-read-item {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 24px;
}

.easy-read-image {
  width: 80px;
  height: 80px;
  flex-shrink: 0;
}

.easy-read-text {
  margin: 0;
}
```

### Easy Read Toggle Component

```jsx
function EasyReadToggle({ children, easyReadContent }) {
  const [isEasyRead, setIsEasyRead] = useState(false);

  return (
    <div>
      <button
        onClick={() => setIsEasyRead(!isEasyRead)}
        aria-pressed={isEasyRead}
        className="easy-read-toggle"
      >
        <img src="/easy-read-icon.png" alt="" />
        {isEasyRead ? 'Standard version' : 'Easy Read version'}
      </button>

      {isEasyRead ? (
        <div className="easy-read" aria-label="Easy Read version">
          {easyReadContent}
        </div>
      ) : (
        <div className="standard">
          {children}
        </div>
      )}
    </div>
  );
}
```

---

## Navigation and Wayfinding

### Consistent Navigation (WCAG 3.2.3)

**Requirements:**
- Navigation in same order on every page
- Same labels for same functions
- Predictable layout
- Clear "you are here" indicators

**Implementation:**
```jsx
function Navigation({ currentPath }) {
  const links = [
    { href: '/', label: 'Home' },
    { href: '/applications', label: 'My Applications' },
    { href: '/documents', label: 'My Documents' },
    { href: '/help', label: 'Help' },
  ];

  return (
    <nav aria-label="Main navigation">
      <ul>
        {links.map(link => (
          <li key={link.href}>
            <a
              href={link.href}
              aria-current={currentPath === link.href ? 'page' : undefined}
            >
              {link.label}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
}
```

### Consistent Help (WCAG 3.2.6)

Help must appear in same relative location on every page:

```jsx
function PageLayout({ children }) {
  return (
    <div>
      <Header />
      <main>{children}</main>
      
      {/* Help section always in same position */}
      <aside aria-label="Help and support" className="help-panel">
        <h2>Need help?</h2>
        <ul>
          <li><a href="/faq">Frequently asked questions</a></li>
          <li><a href="/contact">Contact us</a></li>
          <li>
            <a href="tel:1800800110">
              Call NDIS: 1800 800 110
            </a>
          </li>
        </ul>
      </aside>
      
      <Footer />
    </div>
  );
}
```

### Breadcrumbs

```jsx
function Breadcrumbs({ items }) {
  return (
    <nav aria-label="Breadcrumb">
      <ol className="breadcrumbs">
        {items.map((item, index) => (
          <li key={item.href}>
            {index === items.length - 1 ? (
              <span aria-current="page">{item.label}</span>
            ) : (
              <a href={item.href}>{item.label}</a>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}
```

---

## Forms and Data Entry

### Chunked Form Design

Break long forms into logical sections:

```jsx
function ChunkedForm() {
  const [currentSection, setCurrentSection] = useState(0);
  
  const sections = [
    { id: 'personal', title: 'About you', fields: personalFields },
    { id: 'disability', title: 'Your disability', fields: disabilityFields },
    { id: 'support', title: 'Support you need', fields: supportFields },
    { id: 'review', title: 'Check your answers', fields: null },
  ];

  return (
    <form>
      {/* Progress indicator */}
      <div role="progressbar" 
           aria-valuenow={currentSection + 1} 
           aria-valuemin={1} 
           aria-valuemax={sections.length}
           aria-label={`Step ${currentSection + 1} of ${sections.length}`}
      >
        <div className="progress-bar" 
             style={{ width: `${((currentSection + 1) / sections.length) * 100}%` }} 
        />
      </div>

      {/* Section heading */}
      <h2>
        <span className="sr-only">Step {currentSection + 1} of {sections.length}: </span>
        {sections[currentSection].title}
      </h2>

      {/* Limit visible fields */}
      <div className="form-section">
        {sections[currentSection].fields?.map(field => (
          <FormField key={field.id} {...field} />
        ))}
      </div>

      {/* Navigation */}
      <div className="form-navigation">
        {currentSection > 0 && (
          <button type="button" onClick={() => setCurrentSection(c => c - 1)}>
            Back
          </button>
        )}
        {currentSection < sections.length - 1 ? (
          <button type="button" onClick={() => setCurrentSection(c => c + 1)}>
            Continue
          </button>
        ) : (
          <button type="submit">Submit application</button>
        )}
      </div>

      {/* Save progress */}
      <p className="save-notice" role="status">
        Your progress is saved automatically.
      </p>
    </form>
  );
}
```

### Clear Labels and Instructions

```jsx
function AccessibleField({ label, hint, required, error, children }) {
  const id = useId();
  
  return (
    <div className={`form-field ${error ? 'has-error' : ''}`}>
      <label htmlFor={id}>
        {label}
        {required && <span aria-hidden="true"> *</span>}
        {required && <span className="sr-only"> (required)</span>}
      </label>
      
      {hint && (
        <p id={`${id}-hint`} className="hint">
          {hint}
        </p>
      )}
      
      {React.cloneElement(children, {
        id,
        'aria-describedby': [
          hint && `${id}-hint`,
          error && `${id}-error`
        ].filter(Boolean).join(' ') || undefined,
        'aria-invalid': !!error,
        'aria-required': required,
      })}
      
      {error && (
        <p id={`${id}-error`} className="error" role="alert">
          <span className="sr-only">Error: </span>
          {error}
        </p>
      )}
    </div>
  );
}
```

### Date Input for Cognitive Accessibility

```jsx
// Separate fields are easier than date pickers for many users
function AccessibleDateInput({ label, value, onChange, error }) {
  const [day, setDay] = useState(value?.day || '');
  const [month, setMonth] = useState(value?.month || '');
  const [year, setYear] = useState(value?.year || '');

  return (
    <fieldset>
      <legend>
        {label}
        <span className="hint">For example, 15 3 1980</span>
      </legend>
      
      <div className="date-inputs">
        <div>
          <label htmlFor="dob-day">Day</label>
          <input
            id="dob-day"
            type="text"
            inputMode="numeric"
            pattern="[0-9]*"
            maxLength={2}
            value={day}
            onChange={e => setDay(e.target.value)}
            aria-describedby={error ? 'date-error' : undefined}
          />
        </div>
        
        <div>
          <label htmlFor="dob-month">Month</label>
          <input
            id="dob-month"
            type="text"
            inputMode="numeric"
            pattern="[0-9]*"
            maxLength={2}
            value={month}
            onChange={e => setMonth(e.target.value)}
          />
        </div>
        
        <div>
          <label htmlFor="dob-year">Year</label>
          <input
            id="dob-year"
            type="text"
            inputMode="numeric"
            pattern="[0-9]*"
            maxLength={4}
            value={year}
            onChange={e => setYear(e.target.value)}
          />
        </div>
      </div>
      
      {error && (
        <p id="date-error" role="alert">{error}</p>
      )}
    </fieldset>
  );
}
```

---

## Error Prevention and Recovery

### Clear Error Messages

```jsx
// Error message patterns for cognitive accessibility
const errorMessages = {
  required: (fieldName) => `Please enter your ${fieldName}`,
  email: 'Please enter a valid email address, like name@example.com',
  phone: 'Please enter a valid phone number, like 0412 345 678',
  date: 'Please enter a valid date, like 15 3 1980',
  minLength: (fieldName, min) => `${fieldName} must be at least ${min} characters`,
  maxLength: (fieldName, max) => `${fieldName} must be no more than ${max} characters`,
  pattern: (fieldName, example) => `Please enter a valid ${fieldName}. For example: ${example}`,
};

// Example usage
function validateEmail(email) {
  if (!email) {
    return errorMessages.required('email address');
  }
  if (!email.includes('@')) {
    return errorMessages.email;
  }
  return null;
}
```

### Error Summary Pattern

```jsx
function ErrorSummary({ errors }) {
  const summaryRef = useRef(null);

  useEffect(() => {
    if (Object.keys(errors).length > 0) {
      summaryRef.current?.focus();
    }
  }, [errors]);

  if (Object.keys(errors).length === 0) return null;

  return (
    <div
      ref={summaryRef}
      tabIndex={-1}
      role="alert"
      aria-labelledby="error-summary-title"
      className="error-summary"
    >
      <h2 id="error-summary-title">
        There {Object.keys(errors).length === 1 ? 'is a problem' : 'are some problems'}
      </h2>
      <p>Please fix the following:</p>
      <ul>
        {Object.entries(errors).map(([field, message]) => (
          <li key={field}>
            <a href={`#${field}`}>{message}</a>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### Confirmation Before Destructive Actions

```jsx
function DeleteConfirmation({ itemName, onConfirm, onCancel }) {
  const headingRef = useRef(null);

  useEffect(() => {
    headingRef.current?.focus();
  }, []);

  return (
    <div role="alertdialog" aria-modal="true" aria-labelledby="confirm-title">
      <h2 id="confirm-title" ref={headingRef} tabIndex={-1}>
        Are you sure?
      </h2>
      
      <p>
        You are about to delete <strong>{itemName}</strong>.
      </p>
      <p>
        This cannot be undone.
      </p>
      
      <div className="button-group">
        <button onClick={onCancel} autoFocus>
          No, keep it
        </button>
        <button onClick={onConfirm} className="destructive">
          Yes, delete it
        </button>
      </div>
    </div>
  );
}
```

---

## Memory and Attention

### Redundant Entry Prevention (WCAG 3.3.7)

```jsx
function AddressForm({ shippingAddress }) {
  const [useSameAddress, setUseSameAddress] = useState(true);

  return (
    <fieldset>
      <legend>Billing address</legend>
      
      <div className="checkbox-field">
        <input
          id="same-address"
          type="checkbox"
          checked={useSameAddress}
          onChange={e => setUseSameAddress(e.target.checked)}
        />
        <label htmlFor="same-address">
          Same as my home address
        </label>
      </div>

      {!useSameAddress && (
        <AddressFields 
          defaultValues={shippingAddress}  // Pre-fill from previous entry
        />
      )}
    </fieldset>
  );
}
```

### Display Entered Information

```jsx
function ReviewSection({ data, sectionName, editLink }) {
  return (
    <section aria-labelledby={`review-${sectionName}`}>
      <div className="review-header">
        <h3 id={`review-${sectionName}`}>{sectionName}</h3>
        <a href={editLink}>
          Change
          <span className="sr-only"> {sectionName}</span>
        </a>
      </div>
      
      <dl className="review-data">
        {Object.entries(data).map(([key, value]) => (
          <div key={key}>
            <dt>{key}</dt>
            <dd>{value || 'Not provided'}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
```

### Progress Saving

```jsx
function SaveProgressIndicator({ status, lastSaved }) {
  return (
    <div 
      role="status" 
      aria-live="polite" 
      aria-atomic="true"
      className="save-indicator"
    >
      {status === 'saving' && (
        <span>
          <span className="spinner" aria-hidden="true" />
          Saving...
        </span>
      )}
      {status === 'saved' && lastSaved && (
        <span>
          ✓ Saved at {lastSaved.toLocaleTimeString()}
        </span>
      )}
      {status === 'error' && (
        <span className="error">
          Unable to save. Don't worry, we'll try again.
        </span>
      )}
    </div>
  );
}
```

---

## Implementation Patterns

### Distraction-Free Mode

```jsx
function FocusMode({ enabled, children }) {
  if (!enabled) return children;

  return (
    <div className="focus-mode">
      <style>{`
        .focus-mode {
          max-width: 700px;
          margin: 0 auto;
          padding: 40px;
        }
        .focus-mode aside,
        .focus-mode .sidebar,
        .focus-mode .ads,
        .focus-mode .related-content {
          display: none;
        }
      `}</style>
      {children}
    </div>
  );
}
```

### Reading Progress Indicator

```jsx
function ReadingProgress() {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      const scrolled = window.scrollY;
      const total = document.body.scrollHeight - window.innerHeight;
      setProgress(Math.round((scrolled / total) * 100));
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div
      role="progressbar"
      aria-valuenow={progress}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={`Reading progress: ${progress}%`}
      className="reading-progress"
      style={{ width: `${progress}%` }}
    />
  );
}
```

### Timeout Preferences

```jsx
function TimeoutSettings() {
  const [timeoutPreference, setTimeoutPreference] = useState('default');

  return (
    <fieldset>
      <legend>Session timeout preference</legend>
      
      <div>
        <input
          type="radio"
          id="timeout-default"
          name="timeout"
          value="default"
          checked={timeoutPreference === 'default'}
          onChange={e => setTimeoutPreference(e.target.value)}
        />
        <label htmlFor="timeout-default">
          Standard (30 minutes of inactivity)
        </label>
      </div>
      
      <div>
        <input
          type="radio"
          id="timeout-extended"
          name="timeout"
          value="extended"
          checked={timeoutPreference === 'extended'}
          onChange={e => setTimeoutPreference(e.target.value)}
        />
        <label htmlFor="timeout-extended">
          Extended (2 hours of inactivity)
          <span className="hint">
            Choose this if you need more time to complete tasks
          </span>
        </label>
      </div>
      
      <div>
        <input
          type="radio"
          id="timeout-none"
          name="timeout"
          value="none"
          checked={timeoutPreference === 'none'}
          onChange={e => setTimeoutPreference(e.target.value)}
        />
        <label htmlFor="timeout-none">
          No timeout
          <span className="hint">
            You will stay signed in until you sign out
          </span>
        </label>
      </div>
    </fieldset>
  );
}
```

### Content Complexity Indicator

```jsx
function ContentComplexity({ readingTime, complexity }) {
  return (
    <div className="content-meta" aria-label="Content information">
      <span>
        <span aria-hidden="true">⏱</span>
        About {readingTime} minutes to read
      </span>
      <span>
        <span aria-hidden="true">
          {complexity === 'simple' ? '📗' : complexity === 'medium' ? '📘' : '📕'}
        </span>
        {complexity === 'simple' && 'Easy to understand'}
        {complexity === 'medium' && 'Some technical terms'}
        {complexity === 'complex' && 'Detailed information'}
      </span>
    </div>
  );
}
```
