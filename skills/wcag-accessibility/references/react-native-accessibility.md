# React Native Accessibility Patterns

Platform-specific accessibility implementation for iOS (VoiceOver) and Android (TalkBack).

## Table of Contents

1. [Core Props](#core-accessibility-props)
2. [iOS VoiceOver](#ios-voiceover)
3. [Android TalkBack](#android-talkback)
4. [Dynamic Type & Font Scaling](#dynamic-type--font-scaling)
5. [Reduce Motion](#reduce-motion)
6. [Focus Management](#focus-management)
7. [Common Patterns](#common-patterns)

---

## Core Accessibility Props

### Essential Props (Cross-Platform)

```jsx
<Pressable
  accessible={true}                    // Groups children as single element
  accessibilityLabel="Submit form"     // VoiceOver/TalkBack text
  accessibilityHint="Double tap to submit your application"
  accessibilityRole="button"
  accessibilityState={{ 
    disabled: isDisabled,
    selected: isSelected,
    checked: isChecked,      // boolean or 'mixed'
    expanded: isExpanded,
    busy: isLoading 
  }}
  onPress={handlePress}
>
  <Text>Submit</Text>
</Pressable>
```

### accessibilityRole Values

| Role | Use Case |
|------|----------|
| `button` | Pressable elements performing actions |
| `link` | Navigation to another screen/URL |
| `header` | Section headings |
| `image` | Images (with accessibilityLabel for alt text) |
| `imagebutton` | Clickable images |
| `checkbox` | Two-state selection |
| `radio` | Single selection from group |
| `switch` | Toggle on/off |
| `adjustable` | Sliders, steppers (iOS uses increment/decrement gestures) |
| `alert` | Important messages requiring attention |
| `search` | Search inputs |
| `text` | Static text (default for Text) |
| `none` | Element should be ignored by screen reader |

### accessibilityState Object

```jsx
accessibilityState={{
  disabled: boolean,    // Element cannot be interacted with
  selected: boolean,    // Currently selected (tabs, list items)
  checked: boolean | 'mixed',  // Checkbox/radio state
  expanded: boolean,    // Collapsible content state
  busy: boolean         // Content loading/updating
}}
```

### accessibilityValue (for adjustable elements)

```jsx
<View
  accessibilityRole="adjustable"
  accessibilityLabel="Volume"
  accessibilityValue={{
    min: 0,
    max: 100,
    now: 65,
    text: "65 percent"  // Announced instead of now if provided
  }}
/>
```

---

## iOS VoiceOver

### iOS-Specific Props

```jsx
// Make modal content the only thing VoiceOver can access
<View accessibilityViewIsModal={true}>
  <ModalContent />
</View>

// Hide decorative elements from VoiceOver
<View accessibilityElementsHidden={true}>
  <DecorativeImage />
</View>

// Accessibility actions for custom gestures
<View
  accessibilityActions={[
    { name: 'increment', label: 'Increase volume' },
    { name: 'decrement', label: 'Decrease volume' },
    { name: 'delete', label: 'Delete item' },
    { name: 'magicTap', label: 'Play/Pause' },
    { name: 'escape', label: 'Close' }
  ]}
  onAccessibilityAction={(event) => {
    switch (event.nativeEvent.actionName) {
      case 'increment':
        setVolume(v => Math.min(v + 10, 100));
        break;
      case 'decrement':
        setVolume(v => Math.max(v - 10, 0));
        break;
      case 'delete':
        handleDelete();
        break;
    }
  }}
/>
```

### VoiceOver Gestures

| Gesture | Action |
|---------|--------|
| Single tap | Select item |
| Double tap | Activate selected |
| Three-finger swipe | Scroll |
| Two-finger scrub (Z) | Go back / dismiss |
| Two-finger double tap | Magic tap (context action) |
| Swipe up/down on adjustable | Increment/decrement |

### Rotor Support

VoiceOver users navigate by element type using the rotor. Ensure proper roles:

```jsx
// Headers navigable via rotor
<Text accessibilityRole="header">Section Title</Text>

// Links navigable via rotor  
<Text 
  accessibilityRole="link"
  onPress={() => Linking.openURL(url)}
>
  Visit website
</Text>
```

---

## Android TalkBack

### Android-Specific Props

```jsx
// Live region for dynamic content announcements
<Text accessibilityLiveRegion="polite">
  {`Cart contains ${count} items`}
</Text>
// "polite" - waits for current speech
// "assertive" - interrupts current speech
// "none" - no announcement

// Hide from accessibility (entire subtree)
<View importantForAccessibility="no-hide-descendants">
  <DecorativeContent />
</View>
// Values: "auto", "yes", "no", "no-hide-descendants"

// Associate label with input (Android-only)
<View>
  <Text nativeID="emailLabel">Email Address</Text>
  <TextInput
    accessibilityLabelledBy="emailLabel"
    keyboardType="email-address"
  />
</View>
```

### TalkBack Gestures

| Gesture | Action |
|---------|--------|
| Single tap | Read item |
| Double tap | Activate |
| Swipe right | Next item |
| Swipe left | Previous item |
| Two-finger scroll | Scroll |
| Swipe down then right | Context menu |

---

## Dynamic Type & Font Scaling

### Respecting System Font Size

```jsx
// Font scaling enabled by default
<Text allowFontScaling={true}>
  Scales with system settings
</Text>

// Cap maximum scaling if layout breaks
<Text maxFontSizeMultiplier={1.5}>
  Limited to 150% max
</Text>

// Disable scaling (avoid - accessibility issue)
<Text allowFontScaling={false}>
  Never scales
</Text>
```

### App-Wide Font Scale Defaults

```jsx
// In index.js or App.js
import { Text, TextInput } from 'react-native';

// Set defaults for all Text components
Text.defaultProps = Text.defaultProps || {};
Text.defaultProps.allowFontScaling = true;
Text.defaultProps.maxFontSizeMultiplier = 2.0;

// Set defaults for all TextInput components
TextInput.defaultProps = TextInput.defaultProps || {};
TextInput.defaultProps.allowFontScaling = true;
TextInput.defaultProps.maxFontSizeMultiplier = 1.5;
```

### Responsive Layouts for Large Text

```jsx
import { PixelRatio, useWindowDimensions } from 'react-native';

function ResponsiveComponent() {
  const fontScale = PixelRatio.getFontScale();
  const { width } = useWindowDimensions();
  
  // Adapt layout for large text
  const isLargeText = fontScale > 1.3;
  
  return (
    <View style={{ 
      flexDirection: isLargeText ? 'column' : 'row',
      alignItems: isLargeText ? 'stretch' : 'center'
    }}>
      <Icon name="settings" />
      <Text>Settings</Text>
    </View>
  );
}
```

---

## Reduce Motion

### Detecting and Respecting Motion Preferences

```jsx
import { AccessibilityInfo } from 'react-native';

function useReducedMotion() {
  const [reduceMotion, setReduceMotion] = useState(false);

  useEffect(() => {
    // Get initial value
    AccessibilityInfo.isReduceMotionEnabled().then(setReduceMotion);
    
    // Listen for changes
    const subscription = AccessibilityInfo.addEventListener(
      'reduceMotionChanged',
      setReduceMotion
    );
    
    return () => subscription.remove();
  }, []);

  return reduceMotion;
}
```

### Applying Reduced Motion

```jsx
function AnimatedComponent() {
  const reduceMotion = useReducedMotion();
  const animation = useSharedValue(0);
  
  const animatedStyle = useAnimatedStyle(() => {
    if (reduceMotion) {
      // Instant opacity change instead of slide
      return { opacity: animation.value };
    }
    // Full slide animation
    return {
      transform: [{ translateX: interpolate(animation.value, [0, 1], [-100, 0]) }],
      opacity: animation.value
    };
  });
  
  return <Animated.View style={animatedStyle} />;
}
```

---

## Focus Management

### Setting Accessibility Focus Programmatically

```jsx
import { AccessibilityInfo, findNodeHandle } from 'react-native';

function FormWithFocus() {
  const errorRef = useRef(null);
  
  const focusOnError = () => {
    const node = findNodeHandle(errorRef.current);
    if (node) {
      AccessibilityInfo.setAccessibilityFocus(node);
    }
  };
  
  const handleSubmit = async () => {
    const error = await validate();
    if (error) {
      setError(error);
      focusOnError();  // Move focus to error message
    }
  };
  
  return (
    <>
      {error && (
        <Text 
          ref={errorRef}
          accessibilityRole="alert"
          accessibilityLiveRegion="assertive"
        >
          {error}
        </Text>
      )}
      <Button onPress={handleSubmit} title="Submit" />
    </>
  );
}
```

### Announcing to Screen Readers

```jsx
import { AccessibilityInfo } from 'react-native';

// Announce without changing focus
AccessibilityInfo.announceForAccessibility('Form submitted successfully');

// Announce with optional queue behavior (iOS 15+)
AccessibilityInfo.announceForAccessibilityWithOptions(
  'Loading complete',
  { queue: true }  // Queue behind current speech
);
```

### Modal Focus Trapping

```jsx
function AccessibleModal({ visible, onClose, children }) {
  const closeButtonRef = useRef(null);
  
  useEffect(() => {
    if (visible) {
      // Focus close button when modal opens
      const node = findNodeHandle(closeButtonRef.current);
      if (node) {
        AccessibilityInfo.setAccessibilityFocus(node);
      }
    }
  }, [visible]);
  
  if (!visible) return null;
  
  return (
    <View accessibilityViewIsModal={true}>
      <Pressable
        ref={closeButtonRef}
        accessibilityLabel="Close"
        accessibilityRole="button"
        onPress={onClose}
      >
        <Icon name="close" />
      </Pressable>
      {children}
    </View>
  );
}
```

---

## Common Patterns

### Accessible Button with Loading State

```jsx
function AccessibleButton({ onPress, loading, disabled, children }) {
  return (
    <Pressable
      accessible={true}
      accessibilityRole="button"
      accessibilityLabel={loading ? 'Loading' : undefined}
      accessibilityState={{ 
        disabled: disabled || loading,
        busy: loading 
      }}
      disabled={disabled || loading}
      onPress={onPress}
      style={({ pressed }) => [
        styles.button,
        pressed && styles.pressed,
        (disabled || loading) && styles.disabled
      ]}
    >
      {loading ? (
        <ActivityIndicator accessibilityElementsHidden={true} />
      ) : (
        <Text>{children}</Text>
      )}
    </Pressable>
  );
}
```

### Accessible Form Input

```jsx
function AccessibleInput({ 
  label, 
  error, 
  hint,
  required,
  ...props 
}) {
  const inputId = useId();
  
  return (
    <View>
      <Text nativeID={`${inputId}-label`}>
        {label}
        {required && <Text accessibilityLabel="required"> *</Text>}
      </Text>
      
      {hint && (
        <Text 
          nativeID={`${inputId}-hint`}
          style={styles.hint}
        >
          {hint}
        </Text>
      )}
      
      <TextInput
        accessible={true}
        accessibilityLabel={label}
        accessibilityLabelledBy={`${inputId}-label`}
        accessibilityHint={hint}
        accessibilityState={{ 
          disabled: props.editable === false 
        }}
        aria-invalid={!!error}
        aria-describedby={error ? `${inputId}-error` : undefined}
        {...props}
      />
      
      {error && (
        <Text 
          nativeID={`${inputId}-error`}
          accessibilityRole="alert"
          accessibilityLiveRegion="polite"
          style={styles.error}
        >
          {error}
        </Text>
      )}
    </View>
  );
}
```

### Accessible List with Swipe Actions

```jsx
function AccessibleSwipeableItem({ item, onDelete, onEdit }) {
  return (
    <View
      accessible={true}
      accessibilityLabel={item.title}
      accessibilityHint="Swipe for options or use accessibility actions"
      accessibilityActions={[
        { name: 'delete', label: 'Delete item' },
        { name: 'activate', label: 'Edit item' }
      ]}
      onAccessibilityAction={(event) => {
        switch (event.nativeEvent.actionName) {
          case 'delete':
            onDelete(item.id);
            break;
          case 'activate':
            onEdit(item.id);
            break;
        }
      }}
    >
      <SwipeableRow 
        onDelete={() => onDelete(item.id)}
        onEdit={() => onEdit(item.id)}
      >
        <Text>{item.title}</Text>
      </SwipeableRow>
    </View>
  );
}
```

### Accessible Tab Navigation

```jsx
function AccessibleTabs({ tabs, activeIndex, onChange }) {
  return (
    <View 
      accessibilityRole="tablist"
      style={styles.tabBar}
    >
      {tabs.map((tab, index) => (
        <Pressable
          key={tab.key}
          accessibilityRole="tab"
          accessibilityLabel={tab.title}
          accessibilityState={{ selected: index === activeIndex }}
          onPress={() => onChange(index)}
          style={[
            styles.tab,
            index === activeIndex && styles.activeTab
          ]}
        >
          <Text>{tab.title}</Text>
        </Pressable>
      ))}
    </View>
  );
}
```

### Touch Target Sizing

```jsx
// Ensure minimum 44×44pt touch targets
<Pressable
  hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
  style={{ 
    minWidth: 44, 
    minHeight: 44,
    justifyContent: 'center',
    alignItems: 'center'
  }}
>
  <Icon name="settings" size={24} />
</Pressable>
```

---

## Testing Checklist

### iOS VoiceOver Testing

1. Enable: Settings → Accessibility → VoiceOver
2. Navigate with swipe left/right
3. Verify all interactive elements focusable
4. Verify labels make sense out of context
5. Test with rotor (twist two fingers)
6. Verify adjustable elements work with swipe up/down
7. Test modal focus trapping

### Android TalkBack Testing

1. Enable: Settings → Accessibility → TalkBack
2. Navigate with swipe left/right
3. Verify live regions announce updates
4. Test with local context menu (swipe down then right)
5. Verify landmarks work with navigation
6. Test keyboard navigation with external keyboard

### Automated Testing

```jsx
// Using @testing-library/react-native
import { render, screen } from '@testing-library/react-native';

test('button has accessible name', () => {
  render(<SubmitButton />);
  expect(screen.getByRole('button', { name: /submit/i })).toBeTruthy();
});

test('error is announced', () => {
  render(<FormWithError error="Email is required" />);
  expect(screen.getByRole('alert')).toHaveTextContent('Email is required');
});
```
