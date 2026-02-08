# Next.js Web Accessibility Patterns

Accessibility implementation for Next.js applications targeting Chrome, Safari, Firefox with screen reader support (NVDA, JAWS, VoiceOver).

## Table of Contents

1. [Document Structure](#document-structure)
2. [ARIA Landmarks](#aria-landmarks)
3. [Focus Management](#focus-management)
4. [Keyboard Navigation](#keyboard-navigation)
5. [Live Regions](#live-regions)
6. [Component Patterns](#component-patterns)
7. [Testing](#testing)

---

## Document Structure

### HTML Document Setup

```jsx
// app/layout.tsx (App Router)
export default function RootLayout({ children }) {
  return (
    <html lang="en-AU">  {/* Always set language */}
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body>
        <SkipLink />
        <Header />
        <main id="main-content" tabIndex={-1}>
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}
```

### Skip Link

```jsx
function SkipLink() {
  return (
    <a 
      href="#main-content"
      className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:bg-white focus:p-4 focus:border-2 focus:border-blue-600"
      onClick={(e) => {
        e.preventDefault();
        const main = document.getElementById('main-content');
        main?.focus();
        main?.scrollIntoView();
      }}
    >
      Skip to main content
    </a>
  );
}
```

### Screen Reader Only Utility

```css
/* Tailwind includes sr-only, or use this */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.sr-only-focusable:focus {
  position: static;
  width: auto;
  height: auto;
  padding: inherit;
  margin: inherit;
  overflow: visible;
  clip: auto;
  white-space: normal;
}
```

### Page Titles

```jsx
// App Router - page.tsx
export const metadata = {
  title: 'Application Status | Bella Assist',
};

// Pages Router - _app.tsx
import Head from 'next/head';
<Head>
  <title>Application Status | Bella Assist</title>
</Head>
```

---

## ARIA Landmarks

### Landmark Structure

```jsx
export default function Layout({ children }) {
  return (
    <>
      <header role="banner">
        <nav aria-label="Main navigation">
          {/* Primary navigation */}
        </nav>
      </header>
      
      <div className="content-wrapper">
        <main id="main-content" tabIndex={-1} role="main">
          {children}
        </main>
        
        <aside aria-label="Related resources">
          {/* Sidebar content */}
        </aside>
      </div>
      
      <footer role="contentinfo">
        <nav aria-label="Footer navigation">
          {/* Footer links */}
        </nav>
      </footer>
    </>
  );
}
```

### Landmark Roles Reference

| Element | Implicit Role | When to Add Explicit Role |
|---------|---------------|---------------------------|
| `<header>` | banner | Only when direct child of body |
| `<nav>` | navigation | Always (use aria-label for multiple) |
| `<main>` | main | Always |
| `<footer>` | contentinfo | Only when direct child of body |
| `<aside>` | complementary | Always |
| `<section>` | region | Only with aria-label/aria-labelledby |
| `<form>` | form | Only with aria-label/aria-labelledby |

### Multiple Navigation Regions

```jsx
<nav aria-label="Main navigation">
  {/* Primary nav */}
</nav>

<nav aria-label="Breadcrumb">
  <ol>...</ol>
</nav>

<nav aria-label="Pagination">
  {/* Pagination links */}
</nav>
```

---

## Focus Management

### Focus on Route Changes (App Router)

```jsx
'use client';
import { usePathname } from 'next/navigation';
import { useEffect, useRef } from 'react';

export function useFocusOnNavigation() {
  const pathname = usePathname();
  const mainRef = useRef(null);
  const isFirstRender = useRef(true);

  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    
    // Focus main content or h1 on navigation
    const target = mainRef.current || document.querySelector('h1');
    if (target) {
      target.tabIndex = -1;
      target.focus();
    }
  }, [pathname]);

  return mainRef;
}

// Usage
export default function Page() {
  const mainRef = useFocusOnNavigation();
  return <main ref={mainRef}>...</main>;
}
```

### Focus on Route Changes (Pages Router)

```jsx
import { useRouter } from 'next/router';
import { useEffect } from 'react';

export function useFocusOnNavigation() {
  const router = useRouter();

  useEffect(() => {
    const handleRouteChange = () => {
      const h1 = document.querySelector('h1');
      if (h1) {
        h1.setAttribute('tabindex', '-1');
        h1.focus();
      }
    };

    router.events.on('routeChangeComplete', handleRouteChange);
    return () => router.events.off('routeChangeComplete', handleRouteChange);
  }, [router.events]);
}
```

### Focus Visible Styles

```css
/* Always visible focus indicator */
:focus {
  outline: 3px solid #0066cc;
  outline-offset: 2px;
}

/* Keyboard-only focus (remove for mouse) */
:focus:not(:focus-visible) {
  outline: none;
}

:focus-visible {
  outline: 3px solid #0066cc;
  outline-offset: 2px;
  box-shadow: 0 0 0 6px rgba(0, 102, 204, 0.25);
}

/* Ensure focus visible despite sticky elements (WCAG 2.4.11) */
html {
  scroll-padding-top: 100px;  /* Height of sticky header + buffer */
  scroll-padding-bottom: 80px;
}

*:focus {
  scroll-margin-top: 120px;
  scroll-margin-bottom: 100px;
}
```

---

## Keyboard Navigation

### Roving TabIndex Pattern

```jsx
function TabList({ tabs, activeIndex, onChange }) {
  const tabRefs = useRef([]);

  const handleKeyDown = (e, index) => {
    let newIndex = index;
    
    switch (e.key) {
      case 'ArrowRight':
      case 'ArrowDown':
        e.preventDefault();
        newIndex = (index + 1) % tabs.length;
        break;
      case 'ArrowLeft':
      case 'ArrowUp':
        e.preventDefault();
        newIndex = index === 0 ? tabs.length - 1 : index - 1;
        break;
      case 'Home':
        e.preventDefault();
        newIndex = 0;
        break;
      case 'End':
        e.preventDefault();
        newIndex = tabs.length - 1;
        break;
      default:
        return;
    }
    
    onChange(newIndex);
    tabRefs.current[newIndex]?.focus();
  };

  return (
    <div role="tablist">
      {tabs.map((tab, index) => (
        <button
          key={tab.id}
          ref={el => tabRefs.current[index] = el}
          role="tab"
          id={`tab-${tab.id}`}
          aria-selected={index === activeIndex}
          aria-controls={`panel-${tab.id}`}
          tabIndex={index === activeIndex ? 0 : -1}
          onKeyDown={(e) => handleKeyDown(e, index)}
          onClick={() => onChange(index)}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
```

### Focus Trap for Modals

```jsx
function AccessibleDialog({ isOpen, onClose, title, children }) {
  const dialogRef = useRef(null);
  const previousFocusRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      previousFocusRef.current = document.activeElement;
      
      // Find first focusable element
      const focusable = dialogRef.current?.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      focusable?.[0]?.focus();
    }
    
    return () => {
      previousFocusRef.current?.focus();
    };
  }, [isOpen]);

  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      onClose();
      return;
    }

    if (e.key === 'Tab') {
      const focusable = dialogRef.current?.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      const first = focusable?.[0];
      const last = focusable?.[focusable.length - 1];

      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last?.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first?.focus();
      }
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
        onKeyDown={handleKeyDown}
        onClick={e => e.stopPropagation()}
      >
        <h2 id="dialog-title">{title}</h2>
        {children}
        <button onClick={onClose}>Close</button>
      </div>
    </div>
  );
}
```

---

## Live Regions

### ARIA Live Region Types

```jsx
// Polite - waits for current speech to finish
<div aria-live="polite" aria-atomic="true">
  {statusMessage}
</div>

// Assertive - interrupts current speech (use sparingly)
<div aria-live="assertive">
  {urgentMessage}
</div>

// Alert role - implicitly assertive
<div role="alert">
  {errorMessage}
</div>

// Status role - implicitly polite
<div role="status">
  {successMessage}
</div>

// Log role - new content added to end
<div role="log" aria-live="polite">
  {chatMessages}
</div>
```

### Announce Pattern Hook

```jsx
function useAnnounce() {
  const [message, setMessage] = useState('');
  
  const announce = useCallback((text, priority = 'polite') => {
    setMessage('');
    // Force re-render to trigger announcement
    requestAnimationFrame(() => {
      setMessage(text);
    });
  }, []);
  
  const Announcer = () => (
    <div
      aria-live="polite"
      aria-atomic="true"
      className="sr-only"
    >
      {message}
    </div>
  );
  
  return { announce, Announcer };
}

// Usage
function Form() {
  const { announce, Announcer } = useAnnounce();
  
  const handleSubmit = async () => {
    await submitForm();
    announce('Form submitted successfully');
  };
  
  return (
    <>
      <Announcer />
      <form onSubmit={handleSubmit}>...</form>
    </>
  );
}
```

---

## Component Patterns

### Accessible Form with Error Handling

```jsx
function AccessibleForm() {
  const [errors, setErrors] = useState({});
  const errorSummaryRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    const newErrors = validate(formData);
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      // Focus error summary
      errorSummaryRef.current?.focus();
    }
  };

  return (
    <form onSubmit={handleSubmit} noValidate aria-describedby="form-instructions">
      <p id="form-instructions">
        Required fields are marked with an asterisk (*).
      </p>

      {/* Error Summary */}
      {Object.keys(errors).length > 0 && (
        <div
          ref={errorSummaryRef}
          tabIndex={-1}
          role="alert"
          aria-labelledby="error-summary-title"
          className="error-summary"
        >
          <h2 id="error-summary-title">There is a problem</h2>
          <ul>
            {Object.entries(errors).map(([field, message]) => (
              <li key={field}>
                <a href={`#${field}`}>{message}</a>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Form Field */}
      <div className={errors.email ? 'field-error' : ''}>
        <label htmlFor="email">
          Email address <span aria-hidden="true">*</span>
        </label>
        <input
          id="email"
          name="email"
          type="email"
          required
          aria-required="true"
          aria-invalid={!!errors.email}
          aria-describedby={errors.email ? 'email-error email-hint' : 'email-hint'}
          autoComplete="email"
        />
        <p id="email-hint" className="hint">
          We'll never share your email.
        </p>
        {errors.email && (
          <p id="email-error" className="error">
            <span className="sr-only">Error: </span>
            {errors.email}
          </p>
        )}
      </div>

      <button type="submit">Submit</button>
    </form>
  );
}
```

### Multi-Step Wizard

```jsx
function StepWizard({ steps, currentStep, totalSteps }) {
  const stepHeadingRef = useRef(null);
  
  useEffect(() => {
    // Focus heading on step change
    stepHeadingRef.current?.focus();
  }, [currentStep]);

  return (
    <div>
      {/* Progress indicator */}
      <nav aria-label="Progress">
        <ol>
          {steps.map((step, index) => (
            <li
              key={step.id}
              className={index < currentStep ? 'completed' : ''}
              aria-current={index === currentStep ? 'step' : undefined}
            >
              <span className="sr-only">
                {index < currentStep ? 'Completed: ' : ''}
              </span>
              {step.name}
              {index === currentStep && (
                <span className="sr-only"> (current step)</span>
              )}
            </li>
          ))}
        </ol>
      </nav>

      {/* Step content */}
      <section aria-labelledby="step-heading">
        <h2 
          id="step-heading" 
          ref={stepHeadingRef} 
          tabIndex={-1}
        >
          <span className="sr-only">Step </span>
          {currentStep + 1}
          <span className="sr-only"> of {totalSteps}: </span>
          <span aria-hidden="true"> of {totalSteps}: </span>
          {steps[currentStep].name}
        </h2>
        
        {steps[currentStep].content}
      </section>
    </div>
  );
}
```

### Accessible Data Table

```jsx
function AccessibleTable({ data, sortColumn, sortDirection, onSort }) {
  return (
    <table>
      <caption>NDIS Service Providers in your area</caption>
      <thead>
        <tr>
          <th 
            scope="col"
            aria-sort={sortColumn === 'name' ? sortDirection : 'none'}
          >
            <button onClick={() => onSort('name')}>
              Name
              <span aria-hidden="true">
                {sortColumn === 'name' && (sortDirection === 'ascending' ? ' ↑' : ' ↓')}
              </span>
            </button>
          </th>
          <th scope="col">Services</th>
          <th scope="col">
            <span className="sr-only">Actions</span>
          </th>
        </tr>
      </thead>
      <tbody>
        {data.map((row) => (
          <tr key={row.id}>
            <th scope="row">{row.name}</th>
            <td>{row.services}</td>
            <td>
              <button aria-label={`View details for ${row.name}`}>
                View
              </button>
              <button aria-label={`Contact ${row.name}`}>
                Contact
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

### Accordion

```jsx
function Accordion({ items }) {
  const [expandedItems, setExpandedItems] = useState(new Set());

  const toggleItem = (id) => {
    setExpandedItems(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  return (
    <div className="accordion">
      {items.map((item) => (
        <div key={item.id}>
          <h3>
            <button
              aria-expanded={expandedItems.has(item.id)}
              aria-controls={`panel-${item.id}`}
              onClick={() => toggleItem(item.id)}
            >
              {item.title}
            </button>
          </h3>
          <div
            id={`panel-${item.id}`}
            role="region"
            aria-labelledby={`heading-${item.id}`}
            hidden={!expandedItems.has(item.id)}
          >
            {item.content}
          </div>
        </div>
      ))}
    </div>
  );
}
```

---

## Testing

### Jest + Testing Library

```jsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

describe('Form', () => {
  it('has no accessibility violations', async () => {
    const { container } = render(<Form />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('focuses error summary on validation failure', async () => {
    render(<Form />);
    await userEvent.click(screen.getByRole('button', { name: /submit/i }));
    expect(screen.getByRole('alert')).toHaveFocus();
  });

  it('announces success message', async () => {
    render(<Form />);
    await userEvent.type(screen.getByLabelText(/email/i), 'test@example.com');
    await userEvent.click(screen.getByRole('button', { name: /submit/i }));
    expect(screen.getByRole('status')).toHaveTextContent(/success/i);
  });
});
```

### Playwright Accessibility Testing

```js
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('home page has no accessibility violations', async ({ page }) => {
  await page.goto('/');
  
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag22aa'])
    .analyze();
  
  expect(results.violations).toEqual([]);
});

test('keyboard navigation works', async ({ page }) => {
  await page.goto('/');
  
  // Tab to skip link
  await page.keyboard.press('Tab');
  await expect(page.locator('text=Skip to main content')).toBeFocused();
  
  // Tab through navigation
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link', { name: /home/i })).toBeFocused();
});
```

### Screen Reader Testing Procedures

**NVDA (Windows - Firefox)**:
1. Enable Speech Viewer: NVDA → Tools → Speech Viewer
2. Browse mode: H (headings), B (buttons), D (landmarks), K (links), F (forms)
3. Element lists: NVDA+F7
4. Toggle forms mode: NVDA+Space

**VoiceOver (macOS - Safari)**:
1. Enable: Cmd+F5
2. Rotor: VO+U (twist two fingers on trackpad)
3. Navigate: VO+Right/Left arrows
4. Interact with groups: VO+Shift+Down/Up

**Chrome DevTools**:
1. Open DevTools → More Tools → Accessibility
2. View accessibility tree
3. Check computed accessible name and role
