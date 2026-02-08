# Accessible Authentication Patterns

Authentication methods and implementation patterns meeting WCAG 2.2 AA requirements, specifically 3.3.8 Accessible Authentication (Minimum).

## Table of Contents

1. [WCAG 3.3.8 Requirements](#wcag-338-requirements)
2. [Recommended Methods](#recommended-authentication-methods)
3. [Password Authentication](#password-authentication)
4. [Passwordless Authentication](#passwordless-authentication)
5. [Biometric Authentication](#biometric-authentication)
6. [Multi-Factor Authentication](#multi-factor-authentication)
7. [Session Management](#session-management)

---

## WCAG 3.3.8 Requirements

### Prohibited (Without Alternatives)

**Cognitive function tests** that require users to:
- **Memorize** passwords without password manager support
- **Transcribe** one-time codes from one device to another
- **Solve puzzles** (CAPTCHAs, math problems)
- **Recognize patterns** (image CAPTCHAs)
- **Perform calculations**

### Allowed Authentication Methods

| Method | AA Compliant | Notes |
|--------|--------------|-------|
| Password + paste + autocomplete | ✅ | Must support password managers |
| Passkeys/WebAuthn | ✅ | Best option |
| Magic links (email) | ✅ | Recommended |
| Biometrics | ✅ | With fallback options |
| OAuth/Social login | ✅ | Recommended |
| Hardware security keys | ✅ | FIDO2/U2F |
| Object recognition CAPTCHA | ⚠️ AA only | Not AAA compliant |
| SMS OTP (with paste) | ⚠️ | Must support paste |
| TOTP with copy/paste | ⚠️ | Must support paste |

### Prohibited at AA Level

| Method | Issue |
|--------|-------|
| Pattern lock gestures | Memorization + motor skills |
| Text-based CAPTCHA | Transcription |
| Math CAPTCHA | Cognitive function |
| Blocked paste in password fields | Blocks password managers |
| `autocomplete="off"` on login | Blocks password managers |

---

## Recommended Authentication Methods

### Priority Order for NDIS Applications

1. **Magic links** - Lowest cognitive load
2. **Passkeys** - Modern, secure, accessible
3. **OAuth/Social login** - Familiar to users
4. **Password + password manager support** - Universal fallback

---

## Password Authentication

### Accessible Password Form

```jsx
function LoginForm() {
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState(null);

  return (
    <form method="post" action="/login">
      <div>
        <label htmlFor="email">Email address</label>
        <input
          id="email"
          name="email"
          type="email"
          autoComplete="username email"  // CRITICAL
          required
          aria-required="true"
          aria-describedby="email-hint"
        />
        <p id="email-hint" className="hint">
          Enter the email you used to register
        </p>
      </div>

      <div>
        <label htmlFor="password">Password</label>
        <div className="password-field">
          <input
            id="password"
            name="password"
            type={showPassword ? 'text' : 'password'}
            autoComplete="current-password"  // CRITICAL
            required
            aria-required="true"
            aria-describedby={error ? 'password-error' : undefined}
            aria-invalid={!!error}
            // NEVER block paste
            // NEVER use autocomplete="off"
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            aria-label={showPassword ? 'Hide password' : 'Show password'}
            aria-pressed={showPassword}
          >
            {showPassword ? '🙈' : '👁️'}
          </button>
        </div>
        {error && (
          <p id="password-error" role="alert">
            {error}
          </p>
        )}
      </div>

      <button type="submit">Sign in</button>

      {/* Alternative authentication options */}
      <div>
        <p>Or sign in with:</p>
        <button type="button" onClick={handleMagicLink}>
          Email me a sign-in link
        </button>
        <button type="button" onClick={handlePasskey}>
          Use passkey
        </button>
      </div>
    </form>
  );
}
```

### Password Requirements Display

```jsx
// Show requirements BEFORE user enters password
<div id="password-requirements" aria-live="polite">
  <p>Password must contain:</p>
  <ul>
    <li aria-label={hasLength ? 'Requirement met: ' : 'Requirement not met: '}>
      {hasLength ? '✓' : '○'} At least 8 characters
    </li>
    <li aria-label={hasNumber ? 'Requirement met: ' : 'Requirement not met: '}>
      {hasNumber ? '✓' : '○'} At least one number
    </li>
  </ul>
</div>

<input
  type="password"
  aria-describedby="password-requirements"
  autoComplete="new-password"
/>
```

### Critical Rules

```jsx
// ❌ NEVER DO THESE
<input type="password" autocomplete="off" />           // Blocks password managers
<input type="password" onPaste={e => e.preventDefault()} />  // Blocks paste
<input type="password" maxlength="16" />              // Limits password managers

// ✅ ALWAYS DO THESE
<input type="password" autocomplete="current-password" />  // For login
<input type="password" autocomplete="new-password" />      // For registration
```

---

## Passwordless Authentication

### Magic Link Implementation

```jsx
function MagicLinkLogin() {
  const [email, setEmail] = useState('');
  const [sent, setSent] = useState(false);
  const [error, setError] = useState(null);

  const handleSendLink = async (e) => {
    e.preventDefault();
    try {
      await sendMagicLink(email);
      setSent(true);
    } catch (err) {
      setError('Unable to send link. Please try again.');
    }
  };

  if (sent) {
    return (
      <div role="status" aria-live="polite">
        <h2>Check your email</h2>
        <p>
          We've sent a sign-in link to <strong>{email}</strong>.
          Click the link in the email to sign in.
        </p>
        <p>The link expires in 15 minutes.</p>
        <button onClick={() => setSent(false)}>
          Use a different email
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSendLink}>
      <h2>Sign in with email</h2>
      <p>We'll send you a link to sign in - no password needed.</p>

      <label htmlFor="magic-email">Email address</label>
      <input
        id="magic-email"
        type="email"
        value={email}
        onChange={e => setEmail(e.target.value)}
        autoComplete="email"
        required
        aria-describedby={error ? 'magic-error' : 'magic-hint'}
        aria-invalid={!!error}
      />
      <p id="magic-hint" className="hint">
        Enter your email and we'll send you a link to sign in
      </p>
      {error && (
        <p id="magic-error" role="alert">{error}</p>
      )}

      <button type="submit">Send sign-in link</button>
    </form>
  );
}
```

### Passkey Authentication (WebAuthn)

```jsx
function PasskeyLogin() {
  const [error, setError] = useState(null);
  const [isSupported, setIsSupported] = useState(true);

  useEffect(() => {
    // Check WebAuthn support
    if (!window.PublicKeyCredential) {
      setIsSupported(false);
    }
  }, []);

  const handlePasskeyLogin = async () => {
    try {
      // Get challenge from server
      const options = await fetch('/api/auth/passkey/challenge').then(r => r.json());
      
      // Prompt user for passkey
      const credential = await navigator.credentials.get({
        publicKey: options
      });
      
      // Verify with server
      const result = await fetch('/api/auth/passkey/verify', {
        method: 'POST',
        body: JSON.stringify(credential)
      });
      
      if (result.ok) {
        window.location.href = '/dashboard';
      }
    } catch (err) {
      if (err.name === 'NotAllowedError') {
        setError('Authentication cancelled. Please try again.');
      } else {
        setError('Unable to sign in with passkey. Please try another method.');
      }
    }
  };

  if (!isSupported) {
    return null; // Don't show option if not supported
  }

  return (
    <div>
      <button 
        onClick={handlePasskeyLogin}
        aria-describedby={error ? 'passkey-error' : 'passkey-hint'}
      >
        Sign in with passkey
      </button>
      <p id="passkey-hint" className="hint">
        Use your fingerprint, face, or device PIN
      </p>
      {error && (
        <p id="passkey-error" role="alert">{error}</p>
      )}
    </div>
  );
}
```

---

## Biometric Authentication

### React Native Biometric Login

```jsx
import ReactNativeBiometrics from 'react-native-biometrics';

const rnBiometrics = new ReactNativeBiometrics({
  allowDeviceCredentials: true  // CRITICAL: Always allow PIN/passcode fallback
});

function BiometricLogin({ onSuccess, onFallback }) {
  const [biometricType, setBiometricType] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    checkBiometrics();
  }, []);

  const checkBiometrics = async () => {
    const { available, biometryType } = await rnBiometrics.isSensorAvailable();
    if (available) {
      setBiometricType(biometryType);
    }
  };

  const handleBiometricAuth = async () => {
    try {
      const { success } = await rnBiometrics.simplePrompt({
        promptMessage: 'Verify your identity to sign in',
        cancelButtonText: 'Use password instead',
        fallbackPromptMessage: 'Use device passcode'  // iOS fallback text
      });

      if (success) {
        onSuccess();
      }
    } catch (err) {
      // User cancelled or biometric failed
      setError('Authentication failed. Please try again or use another method.');
    }
  };

  const getBiometricLabel = () => {
    switch (biometricType) {
      case 'FaceID':
        return 'Sign in with Face ID';
      case 'TouchID':
        return 'Sign in with Touch ID';
      case 'Biometrics':
        return 'Sign in with fingerprint';
      default:
        return 'Sign in with biometrics';
    }
  };

  if (!biometricType) {
    return null;
  }

  return (
    <View>
      <Pressable
        accessible={true}
        accessibilityRole="button"
        accessibilityLabel={getBiometricLabel()}
        accessibilityHint="Uses your device biometrics to sign in"
        onPress={handleBiometricAuth}
      >
        <Text>{getBiometricLabel()}</Text>
      </Pressable>

      {/* ALWAYS provide alternative */}
      <Pressable
        accessible={true}
        accessibilityRole="button"
        accessibilityLabel="Sign in with password instead"
        onPress={onFallback}
      >
        <Text>Use password instead</Text>
      </Pressable>

      {error && (
        <Text accessibilityRole="alert" accessibilityLiveRegion="assertive">
          {error}
        </Text>
      )}
    </View>
  );
}
```

### Biometric Accessibility Considerations

| User Group | Consideration | Solution |
|------------|---------------|----------|
| Facial differences | Face ID may not work | Provide passcode/password fallback |
| Amputees | Fingerprint may not work | Provide passcode/password fallback |
| Motor impairments | May struggle with positioning | Extended timeout, alternative methods |
| Cognitive disabilities | May forget biometric enrolled | Clear instructions, alternative methods |

---

## Multi-Factor Authentication

### Accessibility Matrix

| MFA Method | Cognitive | Motor | Visual | Deaf/HoH | Recommended |
|------------|-----------|-------|--------|----------|-------------|
| Push notification | ✅ | ✅ | ⚠️ | ⚠️ | ✅ |
| Biometrics | ✅ | ⚠️ | ✅ | ✅ | ✅ |
| Hardware key | ✅ | ⚠️ | ✅ | ✅ | ✅ |
| SMS code (with paste) | ⚠️ | ⚠️ | ✅ | ✅ | ⚠️ |
| TOTP app | ❌ | ⚠️ | ⚠️ | ✅ | ⚠️ |
| Email code | ⚠️ | ✅ | ✅ | ✅ | ⚠️ |

### Accessible OTP Input

```jsx
function OTPInput({ length = 6, onComplete }) {
  const [values, setValues] = useState(Array(length).fill(''));
  const inputRefs = useRef([]);

  // Support paste of full code
  const handlePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').trim();
    
    if (/^\d+$/.test(pastedData)) {
      const digits = pastedData.slice(0, length).split('');
      const newValues = [...values];
      digits.forEach((digit, i) => {
        newValues[i] = digit;
      });
      setValues(newValues);
      
      if (digits.length === length) {
        onComplete(newValues.join(''));
      }
    }
  };

  return (
    <div>
      <label id="otp-label">
        Enter the {length}-digit code sent to your phone
      </label>
      <p id="otp-hint">
        You can paste the code from your messages
      </p>
      
      <div 
        role="group" 
        aria-labelledby="otp-label"
        aria-describedby="otp-hint"
      >
        {values.map((value, index) => (
          <input
            key={index}
            ref={el => inputRefs.current[index] = el}
            type="text"
            inputMode="numeric"
            pattern="\d"
            maxLength={1}
            value={value}
            onChange={(e) => handleChange(index, e.target.value)}
            onPaste={handlePaste}
            onKeyDown={(e) => handleKeyDown(index, e)}
            aria-label={`Digit ${index + 1} of ${length}`}
            autoComplete={index === 0 ? 'one-time-code' : 'off'}
          />
        ))}
      </div>
      
      <button type="button" onClick={handleResend}>
        Resend code
      </button>
    </div>
  );
}
```

### Extended TOTP Timeout

```jsx
// Standard TOTP: 30 seconds
// Accessible TOTP: 90+ seconds for users who need more time

function TOTPVerification() {
  return (
    <form>
      <label htmlFor="totp">
        Enter the code from your authenticator app
      </label>
      <input
        id="totp"
        type="text"
        inputMode="numeric"
        pattern="\d{6}"
        autoComplete="one-time-code"
        aria-describedby="totp-hint"
      />
      <p id="totp-hint">
        The code changes every 90 seconds. You can paste it from your authenticator app.
      </p>
    </form>
  );
}
```

---

## Session Management

### WCAG 2.2.1 Timing Adjustable

```jsx
function SessionTimeoutWarning({ 
  timeRemaining, 
  onExtend, 
  onSignOut,
  maxExtensions = 10 
}) {
  const [extensions, setExtensions] = useState(0);
  const dialogRef = useRef(null);

  useEffect(() => {
    // Focus dialog when it appears
    dialogRef.current?.focus();
  }, []);

  const handleExtend = () => {
    setExtensions(prev => prev + 1);
    onExtend();
  };

  // Only show when within 20 seconds of timeout (WCAG requirement)
  if (timeRemaining > 20) return null;

  return (
    <div
      ref={dialogRef}
      role="alertdialog"
      aria-modal="true"
      aria-labelledby="timeout-title"
      aria-describedby="timeout-description"
      tabIndex={-1}
    >
      <h2 id="timeout-title">Your session is about to expire</h2>
      <p id="timeout-description">
        You will be signed out in {timeRemaining} seconds due to inactivity.
        {extensions < maxExtensions 
          ? ' Press any key or click the button below to stay signed in.'
          : ' Maximum session extensions reached.'}
      </p>
      
      <div role="status" aria-live="polite">
        Time remaining: {timeRemaining} seconds
      </div>

      {extensions < maxExtensions && (
        <button onClick={handleExtend} autoFocus>
          Stay signed in
        </button>
      )}
      <button onClick={onSignOut}>
        Sign out now
      </button>
    </div>
  );
}
```

### Recommended Session Durations for NDIS Users

| Context | Duration | Rationale |
|---------|----------|-----------|
| General browsing | 60 minutes | Users may need breaks |
| Form filling | 120 minutes | Complex forms take time |
| Document upload | 90 minutes | May need to gather documents |
| With auto-save | 30 minutes | Data preserved on timeout |

### Auto-Save Implementation

```jsx
function FormWithAutoSave({ initialData, onSave }) {
  const [formData, setFormData] = useState(initialData);
  const [lastSaved, setLastSaved] = useState(null);
  const [saveStatus, setSaveStatus] = useState('saved');

  // Auto-save every 30 seconds
  useEffect(() => {
    const interval = setInterval(async () => {
      if (saveStatus !== 'saving') {
        setSaveStatus('saving');
        try {
          await onSave(formData);
          setLastSaved(new Date());
          setSaveStatus('saved');
        } catch (err) {
          setSaveStatus('error');
        }
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [formData, saveStatus]);

  return (
    <form>
      {/* Save status indicator */}
      <div role="status" aria-live="polite" aria-atomic="true">
        {saveStatus === 'saving' && 'Saving...'}
        {saveStatus === 'saved' && lastSaved && 
          `Last saved: ${lastSaved.toLocaleTimeString()}`}
        {saveStatus === 'error' && 
          'Unable to save. Your changes are stored locally.'}
      </div>

      {/* Form fields */}
    </form>
  );
}
```
