# Accessible Component Patterns

Production-ready accessible component patterns for React Native and Next.js.

## Table of Contents

1. [Buttons](#buttons)
2. [Forms](#forms)
3. [Modals and Dialogs](#modals-and-dialogs)
4. [Navigation](#navigation)
5. [Data Display](#data-display)
6. [Feedback](#feedback)
7. [File Upload](#file-upload)

---

## Buttons

### Web Button

```jsx
function Button({ 
  children, 
  onClick, 
  disabled, 
  loading, 
  variant = 'primary',
  type = 'button',
  ariaLabel,
  ariaDescribedBy,
  ...props 
}) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      aria-disabled={disabled || loading}
      aria-busy={loading}
      aria-label={ariaLabel}
      aria-describedby={ariaDescribedBy}
      className={`btn btn-${variant} ${loading ? 'btn-loading' : ''}`}
      {...props}
    >
      {loading ? (
        <>
          <span className="spinner" aria-hidden="true" />
          <span className="sr-only">Loading</span>
          <span aria-hidden="true">{children}</span>
        </>
      ) : (
        children
      )}
    </button>
  );
}
```

### React Native Button

```jsx
function Button({ 
  children, 
  onPress, 
  disabled, 
  loading,
  accessibilityLabel,
  accessibilityHint,
}) {
  return (
    <Pressable
      accessible={true}
      accessibilityRole="button"
      accessibilityLabel={loading ? 'Loading' : accessibilityLabel}
      accessibilityHint={accessibilityHint}
      accessibilityState={{ 
        disabled: disabled || loading,
        busy: loading 
      }}
      disabled={disabled || loading}
      onPress={onPress}
      style={({ pressed }) => [
        styles.button,
        pressed && styles.buttonPressed,
        (disabled || loading) && styles.buttonDisabled
      ]}
    >
      {loading ? (
        <ActivityIndicator accessibilityElementsHidden={true} />
      ) : (
        <Text style={styles.buttonText}>{children}</Text>
      )}
    </Pressable>
  );
}
```

### Icon Button (with accessible label)

```jsx
// Web
function IconButton({ icon, label, onClick, ...props }) {
  return (
    <button
      onClick={onClick}
      aria-label={label}
      className="icon-button"
      {...props}
    >
      {icon}
    </button>
  );
}

// React Native
function IconButton({ icon, label, onPress }) {
  return (
    <Pressable
      accessible={true}
      accessibilityRole="button"
      accessibilityLabel={label}
      onPress={onPress}
      hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
      style={styles.iconButton}
    >
      {icon}
    </Pressable>
  );
}
```

---

## Forms

### Text Input

```jsx
// Web
function TextInput({ 
  label, 
  id,
  hint, 
  error, 
  required,
  type = 'text',
  autoComplete,
  ...props 
}) {
  const inputId = id || useId();
  const hintId = hint ? `${inputId}-hint` : undefined;
  const errorId = error ? `${inputId}-error` : undefined;
  const describedBy = [hintId, errorId].filter(Boolean).join(' ') || undefined;

  return (
    <div className={`form-field ${error ? 'form-field-error' : ''}`}>
      <label htmlFor={inputId}>
        {label}
        {required && <span aria-hidden="true"> *</span>}
      </label>
      
      {hint && <p id={hintId} className="hint">{hint}</p>}
      
      <input
        id={inputId}
        type={type}
        required={required}
        aria-required={required}
        aria-invalid={!!error}
        aria-describedby={describedBy}
        autoComplete={autoComplete}
        {...props}
      />
      
      {error && (
        <p id={errorId} className="error" role="alert">
          <span className="sr-only">Error: </span>
          {error}
        </p>
      )}
    </div>
  );
}
```

```jsx
// React Native
function TextInput({ 
  label, 
  hint, 
  error, 
  required,
  ...props 
}) {
  const inputId = useId();

  return (
    <View style={styles.formField}>
      <Text nativeID={`${inputId}-label`} style={styles.label}>
        {label}
        {required && <Text accessibilityLabel="required"> *</Text>}
      </Text>
      
      {hint && (
        <Text nativeID={`${inputId}-hint`} style={styles.hint}>
          {hint}
        </Text>
      )}
      
      <RNTextInput
        accessible={true}
        accessibilityLabel={label}
        accessibilityLabelledBy={`${inputId}-label`}
        accessibilityHint={hint}
        accessibilityState={{ disabled: props.editable === false }}
        aria-invalid={!!error}
        style={[styles.input, error && styles.inputError]}
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

### Select / Dropdown

```jsx
// Web
function Select({ label, id, options, error, required, ...props }) {
  const selectId = id || useId();

  return (
    <div className="form-field">
      <label htmlFor={selectId}>
        {label}
        {required && <span aria-hidden="true"> *</span>}
      </label>
      
      <select
        id={selectId}
        required={required}
        aria-required={required}
        aria-invalid={!!error}
        aria-describedby={error ? `${selectId}-error` : undefined}
        {...props}
      >
        <option value="">Select an option</option>
        {options.map(opt => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      
      {error && (
        <p id={`${selectId}-error`} className="error" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
```

### Checkbox

```jsx
// Web
function Checkbox({ label, id, checked, onChange, description, ...props }) {
  const checkboxId = id || useId();

  return (
    <div className="checkbox-field">
      <input
        type="checkbox"
        id={checkboxId}
        checked={checked}
        onChange={onChange}
        aria-describedby={description ? `${checkboxId}-desc` : undefined}
        {...props}
      />
      <label htmlFor={checkboxId}>{label}</label>
      {description && (
        <p id={`${checkboxId}-desc`} className="checkbox-description">
          {description}
        </p>
      )}
    </div>
  );
}

// React Native
function Checkbox({ label, checked, onChange, description }) {
  return (
    <Pressable
      accessible={true}
      accessibilityRole="checkbox"
      accessibilityLabel={label}
      accessibilityHint={description}
      accessibilityState={{ checked }}
      onPress={() => onChange(!checked)}
      style={styles.checkboxContainer}
    >
      <View style={[styles.checkbox, checked && styles.checkboxChecked]}>
        {checked && <Text style={styles.checkmark}>✓</Text>}
      </View>
      <Text style={styles.checkboxLabel}>{label}</Text>
    </Pressable>
  );
}
```

### Radio Group

```jsx
// Web
function RadioGroup({ legend, name, options, value, onChange, error }) {
  return (
    <fieldset>
      <legend>{legend}</legend>
      
      {options.map(opt => (
        <div key={opt.value} className="radio-field">
          <input
            type="radio"
            id={`${name}-${opt.value}`}
            name={name}
            value={opt.value}
            checked={value === opt.value}
            onChange={e => onChange(e.target.value)}
            aria-describedby={opt.description ? `${name}-${opt.value}-desc` : undefined}
          />
          <label htmlFor={`${name}-${opt.value}`}>
            {opt.label}
          </label>
          {opt.description && (
            <p id={`${name}-${opt.value}-desc`} className="radio-description">
              {opt.description}
            </p>
          )}
        </div>
      ))}
      
      {error && <p className="error" role="alert">{error}</p>}
    </fieldset>
  );
}
```

---

## Modals and Dialogs

### Web Modal

```jsx
function Modal({ 
  isOpen, 
  onClose, 
  title, 
  children,
  initialFocusRef 
}) {
  const dialogRef = useRef(null);
  const previousFocusRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      previousFocusRef.current = document.activeElement;
      
      // Focus initial element or first focusable
      if (initialFocusRef?.current) {
        initialFocusRef.current.focus();
      } else {
        const focusable = dialogRef.current?.querySelector(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        focusable?.focus();
      }
      
      // Prevent body scroll
      document.body.style.overflow = 'hidden';
    }
    
    return () => {
      document.body.style.overflow = '';
      previousFocusRef.current?.focus();
    };
  }, [isOpen, initialFocusRef]);

  // Handle keyboard
  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      onClose();
      return;
    }

    // Focus trap
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
        aria-labelledby="modal-title"
        onKeyDown={handleKeyDown}
        onClick={e => e.stopPropagation()}
        className="modal"
      >
        <header className="modal-header">
          <h2 id="modal-title">{title}</h2>
          <button 
            onClick={onClose} 
            aria-label="Close"
            className="modal-close"
          >
            ×
          </button>
        </header>
        <div className="modal-content">
          {children}
        </div>
      </div>
    </div>
  );
}
```

### Alert Dialog (Confirmation)

```jsx
function AlertDialog({ 
  isOpen, 
  onConfirm, 
  onCancel, 
  title, 
  description,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  isDestructive = false
}) {
  const cancelRef = useRef(null);

  return (
    <Modal isOpen={isOpen} onClose={onCancel} title={title} initialFocusRef={cancelRef}>
      <div role="alertdialog" aria-describedby="alert-description">
        <p id="alert-description">{description}</p>
        
        <div className="button-group">
          <button 
            ref={cancelRef}
            onClick={onCancel}
          >
            {cancelLabel}
          </button>
          <button 
            onClick={onConfirm}
            className={isDestructive ? 'btn-destructive' : 'btn-primary'}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </Modal>
  );
}
```

### React Native Modal

```jsx
function AccessibleModal({ 
  visible, 
  onClose, 
  title, 
  children 
}) {
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

  return (
    <RNModal
      visible={visible}
      transparent
      animationType="fade"
      onRequestClose={onClose}
    >
      <View 
        style={styles.modalBackdrop}
        accessibilityViewIsModal={true}
      >
        <View style={styles.modalContent}>
          <View style={styles.modalHeader}>
            <Text 
              style={styles.modalTitle}
              accessibilityRole="header"
            >
              {title}
            </Text>
            <Pressable
              ref={closeButtonRef}
              accessible={true}
              accessibilityRole="button"
              accessibilityLabel="Close"
              onPress={onClose}
            >
              <Text>×</Text>
            </Pressable>
          </View>
          
          {children}
        </View>
      </View>
    </RNModal>
  );
}
```

---

## Navigation

### Tabs

```jsx
function Tabs({ tabs, activeIndex, onChange, children }) {
  const tabRefs = useRef([]);

  const handleKeyDown = (e, index) => {
    let newIndex = index;
    
    switch (e.key) {
      case 'ArrowRight':
        e.preventDefault();
        newIndex = (index + 1) % tabs.length;
        break;
      case 'ArrowLeft':
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
    <div>
      <div role="tablist" aria-label="Content sections">
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
            className={index === activeIndex ? 'tab-active' : ''}
          >
            {tab.label}
          </button>
        ))}
      </div>
      
      {tabs.map((tab, index) => (
        <div
          key={tab.id}
          role="tabpanel"
          id={`panel-${tab.id}`}
          aria-labelledby={`tab-${tab.id}`}
          hidden={index !== activeIndex}
          tabIndex={0}
        >
          {children[index]}
        </div>
      ))}
    </div>
  );
}
```

### Accordion

```jsx
function Accordion({ items, allowMultiple = false }) {
  const [expanded, setExpanded] = useState(new Set());

  const toggleItem = (id) => {
    setExpanded(prev => {
      const next = new Set(allowMultiple ? prev : []);
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
      {items.map((item, index) => (
        <div key={item.id} className="accordion-item">
          <h3>
            <button
              id={`accordion-header-${item.id}`}
              aria-expanded={expanded.has(item.id)}
              aria-controls={`accordion-panel-${item.id}`}
              onClick={() => toggleItem(item.id)}
              className="accordion-trigger"
            >
              <span>{item.title}</span>
              <span aria-hidden="true" className="accordion-icon">
                {expanded.has(item.id) ? '−' : '+'}
              </span>
            </button>
          </h3>
          <div
            id={`accordion-panel-${item.id}`}
            role="region"
            aria-labelledby={`accordion-header-${item.id}`}
            hidden={!expanded.has(item.id)}
            className="accordion-panel"
          >
            {item.content}
          </div>
        </div>
      ))}
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
        {items.map((item, index) => {
          const isLast = index === items.length - 1;
          
          return (
            <li key={item.href}>
              {isLast ? (
                <span aria-current="page">{item.label}</span>
              ) : (
                <>
                  <a href={item.href}>{item.label}</a>
                  <span aria-hidden="true" className="separator">/</span>
                </>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
```

---

## Data Display

### Data Table

```jsx
function DataTable({ 
  caption, 
  columns, 
  data, 
  sortColumn, 
  sortDirection, 
  onSort 
}) {
  return (
    <table>
      <caption>{caption}</caption>
      <thead>
        <tr>
          {columns.map(col => (
            <th 
              key={col.key}
              scope="col"
              aria-sort={
                sortColumn === col.key 
                  ? sortDirection 
                  : col.sortable ? 'none' : undefined
              }
            >
              {col.sortable ? (
                <button onClick={() => onSort(col.key)}>
                  {col.label}
                  {sortColumn === col.key && (
                    <span aria-hidden="true">
                      {sortDirection === 'ascending' ? ' ↑' : ' ↓'}
                    </span>
                  )}
                </button>
              ) : (
                col.label
              )}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map(row => (
          <tr key={row.id}>
            {columns.map((col, index) => (
              index === 0 ? (
                <th key={col.key} scope="row">
                  {row[col.key]}
                </th>
              ) : (
                <td key={col.key}>
                  {row[col.key]}
                </td>
              )
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

### Card List

```jsx
// Web
function CardList({ items, onSelect }) {
  return (
    <ul className="card-list" role="list">
      {items.map(item => (
        <li key={item.id}>
          <article className="card">
            <h3>
              <a href={`/items/${item.id}`}>
                {item.title}
              </a>
            </h3>
            <p>{item.description}</p>
            <button 
              onClick={() => onSelect(item.id)}
              aria-label={`Select ${item.title}`}
            >
              Select
            </button>
          </article>
        </li>
      ))}
    </ul>
  );
}

// React Native
function CardList({ items, onSelect }) {
  return (
    <FlatList
      data={items}
      keyExtractor={item => item.id}
      renderItem={({ item }) => (
        <Pressable
          accessible={true}
          accessibilityRole="button"
          accessibilityLabel={`${item.title}. ${item.description}`}
          accessibilityHint="Double tap to select"
          onPress={() => onSelect(item.id)}
          style={styles.card}
        >
          <Text 
            style={styles.cardTitle}
            accessibilityRole="header"
          >
            {item.title}
          </Text>
          <Text style={styles.cardDescription}>
            {item.description}
          </Text>
        </Pressable>
      )}
    />
  );
}
```

---

## Feedback

### Toast / Snackbar

```jsx
function Toast({ message, type = 'info', onDismiss, duration = 5000 }) {
  useEffect(() => {
    if (duration) {
      const timer = setTimeout(onDismiss, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, onDismiss]);

  return (
    <div
      role={type === 'error' ? 'alert' : 'status'}
      aria-live={type === 'error' ? 'assertive' : 'polite'}
      className={`toast toast-${type}`}
    >
      <span>{message}</span>
      <button 
        onClick={onDismiss}
        aria-label="Dismiss notification"
      >
        ×
      </button>
    </div>
  );
}
```

### Loading Indicator

```jsx
// Web
function LoadingIndicator({ label = 'Loading' }) {
  return (
    <div 
      role="status"
      aria-live="polite"
      aria-label={label}
      className="loading"
    >
      <span className="spinner" aria-hidden="true" />
      <span className="sr-only">{label}</span>
    </div>
  );
}

// React Native
function LoadingIndicator({ label = 'Loading' }) {
  return (
    <View 
      accessible={true}
      accessibilityRole="progressbar"
      accessibilityLabel={label}
      accessibilityLiveRegion="polite"
    >
      <ActivityIndicator />
      <Text style={styles.srOnly}>{label}</Text>
    </View>
  );
}
```

### Progress Bar

```jsx
function ProgressBar({ value, max = 100, label }) {
  const percentage = Math.round((value / max) * 100);

  return (
    <div className="progress-container">
      <div
        role="progressbar"
        aria-valuenow={value}
        aria-valuemin={0}
        aria-valuemax={max}
        aria-label={label}
        className="progress-bar"
        style={{ width: `${percentage}%` }}
      />
      <span className="progress-text">
        {percentage}% complete
      </span>
    </div>
  );
}
```

---

## File Upload

### Accessible File Upload

```jsx
function FileUpload({ 
  accept, 
  multiple, 
  onSelect, 
  maxSize,
  label = 'Upload files' 
}) {
  const inputRef = useRef(null);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState(null);

  const handleFiles = (files) => {
    const fileList = Array.from(files);
    
    // Validate file size
    const oversized = fileList.filter(f => f.size > maxSize);
    if (oversized.length > 0) {
      setError(`Some files exceed the ${formatBytes(maxSize)} limit`);
      return;
    }
    
    setError(null);
    onSelect(fileList);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    handleFiles(e.dataTransfer.files);
  };

  return (
    <div className="file-upload">
      {/* Always provide button alternative to drag-drop (WCAG 2.5.7) */}
      <div
        className={`drop-zone ${dragActive ? 'drag-active' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
      >
        <p>Drag and drop files here, or</p>
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          className="upload-button"
        >
          {label}
        </button>
        
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          multiple={multiple}
          onChange={(e) => handleFiles(e.target.files)}
          className="sr-only"
          aria-describedby="upload-hint"
        />
      </div>
      
      <p id="upload-hint" className="hint">
        Maximum file size: {formatBytes(maxSize)}
        {accept && `. Accepted formats: ${accept}`}
      </p>
      
      {error && (
        <p className="error" role="alert">{error}</p>
      )}
    </div>
  );
}
```

### Upload Progress

```jsx
function UploadProgress({ files }) {
  return (
    <ul className="upload-list" aria-label="Upload progress">
      {files.map(file => (
        <li key={file.name}>
          <span>{file.name}</span>
          <div
            role="progressbar"
            aria-valuenow={file.progress}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label={`${file.name} upload progress`}
          >
            <div 
              className="progress-fill" 
              style={{ width: `${file.progress}%` }}
            />
          </div>
          <span aria-live="polite">
            {file.progress === 100 
              ? 'Complete' 
              : `${file.progress}%`}
          </span>
        </li>
      ))}
    </ul>
  );
}
```
