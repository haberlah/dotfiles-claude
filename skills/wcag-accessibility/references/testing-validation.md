# Accessibility Testing and Validation

Comprehensive testing methodology for WCAG 2.2 AA compliance using automated tools, manual testing, and user testing.

## Table of Contents

1. [Testing Strategy](#testing-strategy)
2. [Automated Testing](#automated-testing)
3. [Manual Testing](#manual-testing)
4. [Screen Reader Testing](#screen-reader-testing)
5. [Mobile Testing](#mobile-testing)
6. [CI/CD Integration](#cicd-integration)
7. [User Testing](#user-testing)

---

## Testing Strategy

### Coverage Pyramid

```
                    ┌─────────────────┐
                    │   User Testing  │  ← 5-10% (highest value)
                    │   with AT users │
                    ├─────────────────┤
                    │  Screen Reader  │  ← 15-20%
                    │   & Keyboard    │
                    ├─────────────────┤
                    │ Manual Checklist│  ← 20-25%
                    │   Inspection    │
                    ├─────────────────┤
                    │ Automated Tests │  ← 50-60% (broadest coverage)
                    │  axe, jest-axe  │
                    └─────────────────┘
```

### What Each Layer Catches

| Layer | Catches | Misses |
|-------|---------|--------|
| Automated | Missing alt text, color contrast, ARIA errors, label associations | Reading order, focus logic, AT announcements, user experience |
| Manual checklist | Keyboard navigation, visible focus, heading structure | Screen reader experience, cognitive accessibility |
| Screen reader | Announcement quality, navigation patterns, live regions | Cross-AT differences, user comprehension |
| User testing | Real usability issues, cognitive barriers, workflow problems | Edge cases, technical compliance |

---

## Automated Testing

### Jest + Testing Library + jest-axe

**Setup:**
```bash
npm install --save-dev jest-axe @testing-library/react @testing-library/jest-dom
```

**Configuration:**
```js
// jest.setup.js
import '@testing-library/jest-dom';
import { toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);
```

**Component Test:**
```jsx
import { render, screen } from '@testing-library/react';
import { axe } from 'jest-axe';

describe('LoginForm', () => {
  it('has no accessibility violations', async () => {
    const { container } = render(<LoginForm />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('has proper form labels', () => {
    render(<LoginForm />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });

  it('shows error with proper ARIA', async () => {
    render(<LoginForm />);
    await userEvent.click(screen.getByRole('button', { name: /sign in/i }));
    
    const alert = screen.getByRole('alert');
    expect(alert).toBeInTheDocument();
    expect(alert).toHaveTextContent(/please enter your email/i);
  });

  it('maintains focus order', async () => {
    render(<LoginForm />);
    const email = screen.getByLabelText(/email/i);
    const password = screen.getByLabelText(/password/i);
    const submit = screen.getByRole('button', { name: /sign in/i });

    email.focus();
    await userEvent.tab();
    expect(password).toHaveFocus();
    
    await userEvent.tab();
    expect(submit).toHaveFocus();
  });
});
```

**Page-Level Test:**
```jsx
import { axe } from 'jest-axe';
import { render } from '@testing-library/react';

const pages = [
  { name: 'Home', component: HomePage },
  { name: 'Login', component: LoginPage },
  { name: 'Dashboard', component: DashboardPage },
];

describe.each(pages)('$name page accessibility', ({ name, component: Page }) => {
  it('has no accessibility violations', async () => {
    const { container } = render(<Page />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

### Axe-core Configuration

```jsx
import { axe, toHaveNoViolations } from 'jest-axe';

// Custom configuration
const axeConfig = {
  rules: {
    // WCAG 2.2 AA rules
    'color-contrast': { enabled: true },
    'target-size': { enabled: true },  // 2.5.8
    'focus-not-obscured-minimum': { enabled: true },  // 2.4.11
    
    // Disable specific rules if needed
    'region': { enabled: false },  // Disable landmark requirement
  }
};

it('passes custom axe config', async () => {
  const { container } = render(<Component />);
  const results = await axe(container, axeConfig);
  expect(results).toHaveNoViolations();
});
```

### React Native Testing

```jsx
// Using @testing-library/react-native
import { render, screen } from '@testing-library/react-native';

describe('AccessibleButton', () => {
  it('has correct accessibility props', () => {
    render(<Button label="Submit" />);
    
    const button = screen.getByRole('button', { name: 'Submit' });
    expect(button).toBeTruthy();
    expect(button.props.accessibilityRole).toBe('button');
  });

  it('announces loading state', () => {
    render(<Button label="Submit" loading />);
    
    const button = screen.getByRole('button');
    expect(button.props.accessibilityState?.busy).toBe(true);
  });
});
```

---

## Manual Testing

### Keyboard-Only Testing Checklist

**Navigation:**
- [ ] All interactive elements reachable via Tab
- [ ] Tab order matches visual layout
- [ ] Can navigate backwards with Shift+Tab
- [ ] Skip link present and functional
- [ ] No keyboard traps

**Focus:**
- [ ] Focus indicator visible on all focusable elements
- [ ] Focus indicator has 3:1 contrast
- [ ] Focus not obscured by sticky elements
- [ ] Focus moves logically after actions

**Activation:**
- [ ] Enter activates buttons and links
- [ ] Space activates checkboxes and buttons
- [ ] Escape closes modals and dropdowns
- [ ] Arrow keys navigate within composite widgets

**Forms:**
- [ ] Can complete entire form with keyboard
- [ ] Error messages reachable and announced
- [ ] Required fields identifiable

### Visual Inspection Checklist

**Color & Contrast:**
- [ ] Text contrast ≥4.5:1 (3:1 for large text)
- [ ] UI components contrast ≥3:1
- [ ] Information not conveyed by color alone
- [ ] Focus indicators visible

**Text:**
- [ ] Text resizes to 200% without loss
- [ ] Content reflows at 320px width (400% zoom)
- [ ] No images of text (except logos)
- [ ] Text spacing adjustable without breakage

**Structure:**
- [ ] Proper heading hierarchy (h1-h6)
- [ ] Landmarks present (main, nav, header, footer)
- [ ] Tables have proper headers
- [ ] Lists use proper markup

**Interaction:**
- [ ] Touch targets ≥24×24px (44×44px recommended)
- [ ] Drag operations have alternatives
- [ ] No time limits (or can extend)
- [ ] No auto-playing media

### Content Checklist

**Text alternatives:**
- [ ] All images have alt text
- [ ] Decorative images have empty alt
- [ ] Complex images have long descriptions
- [ ] Icons have accessible labels

**Forms:**
- [ ] All inputs have visible labels
- [ ] Labels associated with inputs
- [ ] Required fields indicated
- [ ] Error messages clear and specific
- [ ] Help text available

**Navigation:**
- [ ] Navigation consistent across pages
- [ ] Multiple ways to find content
- [ ] Help in consistent location
- [ ] Links have clear purpose

---

## Screen Reader Testing

### Testing Matrix

| Screen Reader | Platform | Browser | Priority |
|---------------|----------|---------|----------|
| VoiceOver | iOS | Safari | High |
| TalkBack | Android | Chrome | High |
| VoiceOver | macOS | Safari | Medium |
| NVDA | Windows | Firefox | High |
| NVDA | Windows | Chrome | Medium |
| JAWS | Windows | Chrome | Medium |

### NVDA Testing (Windows)

**Setup:**
1. Download NVDA from nvaccess.org
2. Enable Speech Viewer: NVDA → Tools → Speech Viewer

**Key Commands:**
| Action | Shortcut |
|--------|----------|
| Stop speech | Ctrl |
| Read from cursor | NVDA+Down |
| Next focusable | Tab |
| Previous focusable | Shift+Tab |
| Browse mode | NVDA+Space (toggle) |
| Element list | NVDA+F7 |
| Next heading | H |
| Next button | B |
| Next landmark | D |
| Next link | K |
| Next form field | F |

**Test Procedure:**
1. Load page, note title announcement
2. Press H to navigate headings - verify hierarchy
3. Press D to navigate landmarks - verify structure
4. Tab through all interactive elements
5. Complete form interactions
6. Verify error announcements
7. Test dynamic content (live regions)

### VoiceOver Testing (macOS)

**Setup:**
1. Enable: System Settings → Accessibility → VoiceOver
2. Or press Cmd+F5

**Key Commands:**
| Action | Shortcut |
|--------|----------|
| VoiceOver modifier | Control+Option (VO) |
| Read all | VO+A |
| Next item | VO+Right |
| Previous item | VO+Left |
| Interact with group | VO+Shift+Down |
| Stop interacting | VO+Shift+Up |
| Open rotor | VO+U |
| Activate | VO+Space |

**Test with Rotor:**
1. Open rotor with VO+U
2. Navigate categories with Left/Right
3. Navigate items with Up/Down
4. Verify headings, links, landmarks, form controls

### VoiceOver Testing (iOS)

**Enable:** Settings → Accessibility → VoiceOver

**Gestures:**
| Action | Gesture |
|--------|---------|
| Read item | Single tap |
| Activate | Double tap |
| Next item | Swipe right |
| Previous item | Swipe left |
| Scroll | Three-finger swipe |
| Rotor | Twist two fingers |
| Magic tap | Two-finger double tap |
| Escape | Two-finger scrub (Z) |

**Test Procedure:**
1. Swipe through all elements
2. Verify labels make sense
3. Double tap to activate
4. Use rotor for navigation
5. Test forms and buttons

### TalkBack Testing (Android)

**Enable:** Settings → Accessibility → TalkBack

**Gestures:**
| Action | Gesture |
|--------|---------|
| Read item | Single tap |
| Activate | Double tap |
| Next item | Swipe right |
| Previous item | Swipe left |
| Scroll | Two-finger swipe |
| Context menu | Swipe down then right |

**Test Procedure:**
1. Explore by touch
2. Swipe through all elements
3. Verify contentDescription values
4. Test with local context menu
5. Verify live region announcements

---

## Mobile Testing

### iOS Accessibility Inspector

1. Open Xcode
2. Window → Accessibility Inspector
3. Select device/simulator
4. Point to elements to inspect

**Verify:**
- Label
- Value
- Traits (role)
- Frame (size)
- Enabled state

### Android Accessibility Scanner

1. Install from Play Store
2. Enable in Settings → Accessibility
3. Open app to test
4. Tap floating button to scan

**Checks:**
- Touch target size (48dp minimum)
- Color contrast
- Content labeling
- Text scaling

### Responsive Testing

Test at these viewport widths:
- 320px (WCAG reflow requirement)
- 375px (iPhone SE)
- 390px (iPhone 14)
- 412px (Pixel)
- 768px (Tablet)
- 1024px (Desktop)
- 1440px (Large desktop)

**Test at each breakpoint:**
- [ ] Layout doesn't break
- [ ] Text remains readable
- [ ] Touch targets adequate
- [ ] No horizontal scrolling (except data tables)

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/accessibility.yml
name: Accessibility Tests

on: [push, pull_request]

jobs:
  accessibility:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run unit tests with jest-axe
        run: npm test -- --coverage
      
      - name: Build application
        run: npm run build
      
      - name: Start server
        run: npm start &
        
      - name: Wait for server
        run: npx wait-on http://localhost:3000
      
      - name: Run Lighthouse CI
        run: |
          npm install -g @lhci/cli
          lhci autorun
        env:
          LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}
```

### Lighthouse CI Configuration

```js
// lighthouserc.js
module.exports = {
  ci: {
    collect: {
      url: [
        'http://localhost:3000/',
        'http://localhost:3000/login',
        'http://localhost:3000/dashboard',
      ],
      numberOfRuns: 3,
    },
    assert: {
      assertions: {
        'categories:accessibility': ['error', { minScore: 0.9 }],
        'color-contrast': 'error',
        'heading-order': 'warn',
        'image-alt': 'error',
        'label': 'error',
        'link-name': 'error',
        'button-name': 'error',
      },
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
};
```

### Pa11y CI

```json
// .pa11yci
{
  "defaults": {
    "standard": "WCAG2AA",
    "runners": ["axe", "htmlcs"],
    "timeout": 30000,
    "wait": 2000
  },
  "urls": [
    "http://localhost:3000/",
    {
      "url": "http://localhost:3000/login",
      "actions": [
        "set field #email to test@example.com",
        "click element button[type=submit]",
        "wait for element .error-message to be visible"
      ]
    }
  ]
}
```

### Playwright Accessibility Testing

```js
// e2e/accessibility.spec.ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Accessibility', () => {
  test('home page', async ({ page }) => {
    await page.goto('/');
    
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag22aa'])
      .analyze();
    
    expect(results.violations).toEqual([]);
  });

  test('keyboard navigation', async ({ page }) => {
    await page.goto('/');
    
    // Tab to skip link
    await page.keyboard.press('Tab');
    const skipLink = page.locator('a:has-text("Skip to main")');
    await expect(skipLink).toBeFocused();
    
    // Use skip link
    await page.keyboard.press('Enter');
    const main = page.locator('main');
    await expect(main).toBeFocused();
  });

  test('focus trap in modal', async ({ page }) => {
    await page.goto('/');
    await page.click('button:has-text("Open modal")');
    
    // Tab through modal
    const focusableCount = await page.evaluate(() => {
      const modal = document.querySelector('[role="dialog"]');
      return modal?.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      ).length;
    });
    
    // Tab should cycle within modal
    for (let i = 0; i < focusableCount + 1; i++) {
      await page.keyboard.press('Tab');
    }
    
    // Should still be inside modal
    const focused = await page.evaluate(() => 
      document.activeElement?.closest('[role="dialog"]') !== null
    );
    expect(focused).toBe(true);
  });
});
```

---

## User Testing

### Recruiting Participants

**For NDIS applications, recruit users who:**
- Use screen readers regularly
- Use switch access or voice control
- Have cognitive disabilities
- Have low vision (use magnification)
- Have motor impairments

**Australian resources:**
- Intopia (intopia.digital)
- Centre for Inclusive Design (centreforinclusivedesign.org.au)
- NDIS-registered LACs and Support Coordinators

### Testing Protocol

**Session structure (60-90 minutes):**
1. Introduction (5 min) - Explain purpose, get consent
2. Setup (5 min) - Participant uses own AT
3. Warm-up task (5 min) - Simple navigation
4. Core tasks (40-60 min) - Key user journeys
5. Debrief (10-15 min) - Open feedback

**Sample tasks for NDIS app:**
1. Find information about applying for NDIS
2. Start a new application
3. Upload a document
4. Check application status
5. Find help/contact information

### Recording and Documentation

```
## Participant Information
- ID: P01
- AT used: VoiceOver on iPhone 13
- Disability type: Vision impairment
- NDIS experience: Current participant

## Task: Upload supporting document
- Completion: ✅ Completed with difficulty
- Time: 4 minutes
- Issues observed:
  - Couldn't find upload button initially
  - Confirmation message not announced
- Severity: Medium
- Quote: "I wasn't sure if it worked until I checked the documents list"

## Recommendations
1. Add aria-live region for upload confirmation
2. Improve button labeling
3. Provide upload progress feedback
```

### Compensation Guidelines

| Participant Type | Duration | Suggested Rate (AUD) |
|-----------------|----------|---------------------|
| General user | 60 min | $75-100 |
| AT user | 60 min | $100-150 |
| Expert AT user | 60 min | $150-200 |
| Remote session | 60 min | Same + add 10% |

### Ethical Considerations

- Provide materials in accessible formats
- Allow participants to use their own AT setup
- Schedule flexibly (fatigue, appointments)
- Don't push if participant struggles
- Respect confidentiality
- Report honestly even if results are negative
