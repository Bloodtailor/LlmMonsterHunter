# UI Components Reference

## Button
```javascript
/**
 * Primary Button component with variants, sizes, and states
 * @param {object} props - Button props
 * @param {React.ReactNode} props.children - Button content
 * @param {string} props.variant - Button style variant
 * @param {string} props.size - Button size
 * @param {boolean} props.loading - Show loading state
 * @param {boolean} props.disabled - Disable button
 * @param {string} props.icon - Icon to display (emoji or icon class)
 * @param {string} props.iconPosition - Icon position ('left' or 'right')
 * @param {Function} props.onClick - Click handler
 * @param {string} props.type - Button type ('button', 'submit', 'reset')
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @param {string} props.ariaLabel - Accessibility label
 * @param {object} props.rest - Additional HTML button attributes
 * @returns {React.ReactElement} Button component
 */

// Constants
export const BUTTON_VARIANTS = {
  PRIMARY: 'primary',
  SECONDARY: 'secondary', 
  DANGER: 'danger',
  SUCCESS: 'success',
  WARNING: 'warning',
  GHOST: 'ghost',
  LINK: 'link'
};

export const BUTTON_SIZES = {
  SM: 'sm',
  MD: 'md', 
  LG: 'lg',
  XL: 'xl'
};
```

## IconButton
```javascript
/**
 * Icon-only button component with optimized styling and behavior
 * @param {object} props - IconButton props
 * @param {string} props.icon - Icon to display (emoji or icon class) - REQUIRED
 * @param {string} props.variant - Button style variant (default: 'secondary')
 * @param {string} props.size - Button size (default: 'md')
 * @param {boolean} props.loading - Show loading state
 * @param {boolean} props.disabled - Disable button
 * @param {Function} props.onClick - Click handler
 * @param {string} props.ariaLabel - Accessibility label - REQUIRED for icon-only
 * @param {string} props.title - Tooltip text (will also be used as ariaLabel if not provided)
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.rest - Additional props passed to Button
 * @returns {React.ReactElement} IconButton component
 */
```

## ButtonGroup
```javascript
/**
 * Container component for grouping multiple buttons
 * @param {object} props - ButtonGroup props
 * @param {React.ReactNode} props.children - Button components to group
 * @param {string} props.orientation - Layout direction ('horizontal' or 'vertical')
 * @param {string} props.spacing - Space between buttons ('tight', 'normal', 'loose')
 * @param {string} props.alignment - Button alignment ('start', 'center', 'end', 'stretch')
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @param {object} props.rest - Additional HTML div attributes
 * @returns {React.ReactElement} ButtonGroup component
 */

// Constants
export const BUTTON_GROUP_ORIENTATIONS = {
  HORIZONTAL: 'horizontal',
  VERTICAL: 'vertical'
};

export const BUTTON_GROUP_SPACING = {
  TIGHT: 'tight',
  NORMAL: 'normal',
  LOOSE: 'loose'
};

export const BUTTON_GROUP_ALIGNMENT = {
  START: 'start',
  CENTER: 'center', 
  END: 'end',
  STRETCH: 'stretch'
};
```

## Badge
```javascript
/**
 * Base Badge component for labels, tags, and indicators
 * @param {object} props - Badge props
 * @param {React.ReactNode} props.children - Badge content
 * @param {string} props.variant - Badge style variant
 * @param {string} props.size - Badge size
 * @param {string} props.color - Color override (overrides variant colors)
 * @param {boolean} props.pill - Rounded pill styling
 * @param {boolean} props.outlined - Outlined instead of filled
 * @param {Function} props.onClick - Click handler (makes badge interactive)
 * @param {boolean} props.removable - Show remove button
 * @param {Function} props.onRemove - Remove button click handler
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @param {string} props.ariaLabel - Accessibility label
 * @param {Object} props.rest - Additional HTML span attributes
 * @returns {React.ReactElement} Badge component
 */

// Constants
export const BADGE_VARIANTS = {
  PRIMARY: 'primary',
  SECONDARY: 'secondary',
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info'
};

export const BADGE_SIZES = {
  SM: 'sm',
  MD: 'md',
  LG: 'lg'
};
```

## StatusBadge
```javascript
/**
 * Status-specific badge with predefined icons and styling
 * @param {object} props - StatusBadge props
 * @param {string} props.status - Status type (success, error, pending, warning, info)
 * @param {React.ReactNode} props.children - Status text content
 * @param {boolean} props.showIcon - Whether to show status icon (default: true)
 * @param {string} props.iconOverride - Custom icon to override default status icon
 * @param {string} props.size - Badge size (sm, md, lg)
 * @param {boolean} props.outlined - Outlined instead of filled
 * @param {string} props.className - Additional CSS classes
 * @param {Object} props.rest - Additional props passed to Badge
 * @returns {React.ReactElement} StatusBadge component
 */

// Constants
export const STATUS_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  PENDING: 'pending',
  WARNING: 'warning',
  INFO: 'info',
  GENERATING: 'generating',
  COMPLETED: 'completed',
  FAILED: 'failed',
  READY: 'ready',
  LOADING: 'loading'
};
```

## CountBadge
```javascript
/**
 * Count/numeric badge with intelligent formatting and state indication
 * @param {object} props - CountBadge props
 * @param {number} props.count - Current count number
 * @param {number} props.max - Maximum count (optional, shows count/max format)
 * @param {string} props.label - Label text to show before count
 * @param {string} props.format - Format style ('fraction', 'simple', 'percentage')
 * @param {boolean} props.showIcon - Whether to show an icon
 * @param {string} props.icon - Custom icon to display
 * @param {string} props.size - Badge size (sm, md, lg)
 * @param {boolean} props.outlined - Outlined instead of filled
 * @param {string} props.warningThreshold - When to show warning (percentage like '80%' or number)
 * @param {string} props.className - Additional CSS classes
 * @param {Object} props.rest - Additional props passed to Badge
 * @returns {React.ReactElement} CountBadge component
 */

// Constants
export const COUNT_FORMATS = {
  SIMPLE: 'simple',
  FRACTION: 'fraction', 
  PERCENTAGE: 'percentage'
};
```

## LoadingSpinner
```javascript
/**
 * Pure CSS loading spinner component with size and animation variants
 * @param {object} props - LoadingSpinner props
 * @param {string} props.size - Spinner size (xs, sm, md, lg, xl)
 * @param {string} props.color - Color variant (primary, secondary, light, dark)
 * @param {string} props.type - Animation type (spin, pulse, bounce, dots, bars)
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @param {string} props.ariaLabel - Accessibility label
 * @param {Object} props.rest - Additional HTML div attributes
 * @returns {React.ReactElement} LoadingSpinner component
 */

// Constants
export const LOADING_SIZES = {
  XS: 'xs',
  SM: 'sm',
  MD: 'md',
  LG: 'lg',
  XL: 'xl',
  CARD: 'card',
  SECTION: 'section',
  SCREEN: 'screen'
};

export const LOADING_COLORS = {
  PRIMARY: 'primary',
  SECONDARY: 'secondary',
  LIGHT: 'light',
  DARK: 'dark',
  SUCCESS: 'success',
  WARNING: 'warning',
  ERROR: 'error'
};

export const LOADING_TYPES = {
  SPIN: 'spin',
  PULSE: 'pulse',
  BOUNCE: 'bounce',
  DOTS: 'dots',
  BARS: 'bars',
  CARD_FLIP: 'cardFlip'
};
```

## LoadingContainer
```javascript
/**
 * Simplified full-screen or inline loading container
 * @param {string} message - Text to show while loading
 * @param {boolean} overlay - If true, shows full-screen overlay
 * @param {boolean} centered - Center content (default: true)
 * @param {Function} onCancel - If provided, shows cancel button
 * @param {React.ReactNode} children - Optional extra info/content
 * @returns {React.ReactElement}
 */
```

## LoadingSkeleton
```javascript
/**
 * Minimal Skeleton placeholder component for loading content
 * @param {string} type - 'monsterCard' | 'text'
 * @param {number} count - Number of skeletons to render
 * @param {boolean} animated - Enable shimmer animation
 * @param {object} style - Optional inline styles
 * @returns {React.ReactElement}
 */
```

## Alert
```javascript
/**
 * Alert component for displaying important messages to users
 * @param {object} props - Alert props
 * @param {string} props.type - Alert type (success, error, warning, info, loading)
 * @param {string} props.title - Alert title (optional)
 * @param {React.ReactNode} props.children - Alert message content
 * @param {boolean} props.closeable - Show close button (default: false)
 * @param {Function} props.onClose - Close button click handler
 * @param {string} props.icon - Custom icon (overrides type default)
 * @param {boolean} props.showIcon - Whether to show icon (default: true)
 * @param {string} props.size - Alert size (sm, md, lg)
 * @param {boolean} props.outlined - Outlined instead of filled
 * @param {React.ReactNode} props.action - Optional action button/element
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @param {Object} props.rest - Additional HTML div attributes
 * @returns {React.ReactElement} Alert component
 */

// Constants
export const ALERT_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info',
  LOADING: 'loading'
};

export const ALERT_SIZES = {
  SM: 'sm',
  MD: 'md',
  LG: 'lg'
};
```

## EmptyState
```javascript
/**
 * EmptyState component for displaying "no data" states
 * @param {object} props - EmptyState props
 * @param {string} props.icon - Icon to display (emoji or icon class)
 * @param {string} props.title - Primary heading text
 * @param {React.ReactNode} props.message - Description message (can be string or JSX)
 * @param {React.ReactNode} props.action - Optional action button or element
 * @param {string} props.size - EmptyState size (sm, md, lg, xl)
 * @param {string} props.variant - Visual variant (default, subdued, highlighted)
 * @param {boolean} props.centered - Center align content (default: true)
 * @param {string} props.illustration - Optional illustration/image URL
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @param {Object} props.rest - Additional HTML div attributes
 * @returns {React.ReactElement} EmptyState component
 */

// Constants
export const EMPTY_STATE_SIZES = {
  SM: 'sm',
  MD: 'md',
  LG: 'lg',
  XL: 'xl'
};

export const EMPTY_STATE_VARIANTS = {
  DEFAULT: 'default',
  SUBDUED: 'subdued',
  HIGHLIGHTED: 'highlighted'
};

export const EMPTY_STATE_PRESETS = {
  NO_MONSTERS: {
    icon: '🏛️',
    title: 'No Monsters Found',
    message: 'Your collection is empty. Generate some monsters to get started!'
  },
  NO_PARTY: {
    icon: '👥',
    title: 'No Party Members',
    message: 'Add monsters to your party to begin your adventure.'
  },
  NO_SEARCH_RESULTS: {
    icon: '🔍',
    title: 'No Results Found',
    message: 'Try adjusting your search criteria or filters.'
  }
};
```

## Card
```javascript
/**
 * Enhanced card container component
 * @param {object} props - Card props
 * @param {React.ReactNode} props.children - Card content
 * @param {string} props.variant - Card style variant (default, outlined, elevated, flat)
 * @param {string} props.size - Card size (sm, md, lg, xl)
 * @param {boolean} props.fullWidth - Make card span full width of container
 * @param {string} props.padding - Padding variant (none, sm, md, lg)
 * @param {boolean} props.interactive - Make card clickable/hoverable
 * @param {Function} props.onClick - Click handler (makes card interactive)
 * @param {boolean} props.disabled - Disable card interactions
 * @param {string} props.background - Background variant (default, light, dark, transparent)
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @param {string} props.ariaLabel - Accessibility label for interactive cards
 * @param {Object} props.rest - Additional HTML div attributes
 * @returns {React.ReactElement} Card component
 */

// Constants
export const CARD_VARIANTS = {
  DEFAULT: 'default',
  OUTLINED: 'outlined', 
  ELEVATED: 'elevated',
  FLAT: 'flat'
};

export const CARD_PADDING = {
  NONE: 'none',
  SM: 'sm',
  MD: 'md',
  LG: 'lg',
  XL: 'xl'
};

export const CARD_BACKGROUNDS = {
  DEFAULT: 'default',
  LIGHT: 'light',
  DARK: 'dark',
  TRANSPARENT: 'transparent'
};
```

## CardSection
```javascript
/**
 * Simplified CardSection component with clear usage patterns
 * @param {object} props - CardSection props
 * @param {React.ReactNode} props.children - Section content
 * @param {string} props.type - Section type (header, content, footer)
 * @param {string} props.size - Section size for spacing (sm, md, lg, xl)
 * @param {string} props.title - Title text (required for header, optional for content, forbidden for footer)
 * @param {React.ReactNode} props.action - Optional action element (button, link, etc.)
 * @param {string} props.classType - Optional card class type for typography scaling
 * @param {boolean} props.bordered - Add debug border (development only)
 * @param {boolean} props.highlighted - Add debug highlight (development only)
 * @param {string} props.alignment - Content alignment (left, center, right)
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @param {Object} props.rest - Additional HTML div attributes
 * @returns {React.ReactElement} CardSection component
 */

// Constants
export const CARD_SECTION_TYPES = {
  HEADER: 'header',
  CONTENT: 'content', 
  FOOTER: 'footer'
};

export const CARD_SECTION_ALIGNMENT = {
  LEFT: 'left',
  CENTER: 'center',
  RIGHT: 'right'
};
```

## Input
```javascript
/**
 * Simple Input component for text inputs with error handling
 * @param {object} props - Input props
 * @param {string} props.type - Input type (text, email, password, number)
 * @param {string} props.value - Current input value
 * @param {Function} props.onChange - Change handler  
 * @param {string} props.placeholder - Placeholder text
 * @param {boolean} props.disabled - Disable input
 * @param {string} props.error - Error message to display
 * @param {string} props.className - Additional CSS classes
 * @param {Object} props.rest - Additional HTML input attributes
 */
```

## Textarea
```javascript
/**
 * Simple Textarea component for multi-line text input
 * @param {object} props - Textarea props
 * @param {string} props.value - Current textarea value
 * @param {Function} props.onChange - Change handler  
 * @param {string} props.placeholder - Placeholder text
 * @param {boolean} props.disabled - Disable textarea
 * @param {string} props.error - Error message to display
 * @param {number} props.rows - Number of visible text lines (default: 4)
 * @param {string} props.className - Additional CSS classes
 * @param {Object} props.rest - Additional HTML textarea attributes
 */
```

## Select
```javascript
/**
 * Simple Select component for dropdowns with error handling
 * @param {object} props - Select props
 * @param {Array} props.options - Options (strings or {value, label, icon?} objects)
 * @param {string} props.value - Current selected value
 * @param {Function} props.onChange - Change handler
 * @param {string} props.placeholder - Placeholder text (optional)
 * @param {boolean} props.disabled - Disable select
 * @param {string} props.error - Error message to display
 * @param {string} props.className - Additional CSS classes
 * @param {Object} props.rest - Additional HTML select attributes
 */
```

## SearchInput
```javascript
/**
 * Simple SearchInput component with icon, clear button, and error handling
 * @param {object} props - SearchInput props
 * @param {string} props.value - Current search value
 * @param {Function} props.onChange - Change handler
 * @param {string} props.placeholder - Placeholder text (default: "Search...")
 * @param {Function} props.onClear - Clear button handler (optional)
 * @param {boolean} props.disabled - Disable input
 * @param {string} props.error - Error message to display
 * @param {string} props.className - Additional CSS classes
 * @param {Object} props.rest - Additional props
 */
```

## FormField
```javascript
/**
 * Simple FormField wrapper for label + input combinations with error handling
 * @param {object} props - FormField props
 * @param {React.ReactElement} props.children - Input component (Input, Select, SearchInput)
 * @param {string} props.label - Field label text
 * @param {string} props.error - Error message to display
 * @param {string} props.className - Additional CSS classes
 * @param {Object} props.rest - Additional HTML div attributes
 */
```

## Form
```javascript
/**
 * Simple Form container component with submission handling
 * @param {object} props - Form props
 * @param {React.ReactNode} props.children - Form content (FormField components, etc.)
 * @param {Function} props.onSubmit - Form submission handler
 * @param {boolean} props.loading - Show loading state during submission
 * @param {boolean} props.disabled - Disable entire form
 * @param {string} props.error - Form-level error message
 * @param {string} props.className - Additional CSS classes
 * @param {Object} props.rest - Additional HTML form attributes
 */
```

## Pagination
```javascript
/**
 * Complete pagination component with clean layout options
 * @param {object} props - Pagination props
 * @param {object} props.pagination - Pagination object from usePagination hook
 * @param {string} props.itemName - Name of items being paginated (default: 'items')
 * @param {string} props.layout - Layout style ('default', 'simple', 'full') (default: 'default')
 * @param {Array} props.itemsPerPageOptions - Options for items per page (default: [5, 10, 25, 50])
 * @param {number} props.currentLimit - Current items per page value
 * @param {Function} props.onLimitChange - Callback when items per page changes
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.rest - Additional HTML div attributes
 * @returns {React.ReactElement} Complete pagination component
 */
```

## Table
```javascript
/**
 * Responsive table component with automatic text truncation
 * @param {object} props - Table props
 * @param {Array} props.columns - Column definitions (key, header, and width%)
 * @param {Array} props.data - Row data (for simple API)
 * @param {React.ReactNode} props.children - Manual table content
 * @param {string} props.size - Table size (sm, md, lg)
 * @param {boolean} props.striped - Alternating row colors
 * @param {boolean} props.bordered - Show borders
 * @param {boolean} props.hover - Hover effects on rows
 * @param {string} props.emptyMessage - Message when no data
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.rest - Additional table attributes
 * @returns {React.ReactElement} Table component
 */

// Constants
export const TABLE_SIZES = {
  SM: 'sm',
  MD: 'md',
  LG: 'lg'
};
```

## ExpandableTable
```javascript
/**
 * Expandable table component with inline row expansion
 * @param {object} props - ExpandableTable props
 * @param {Array} props.columns - Column definitions (same as Table)
 * @param {Array} props.data - Row data (same as Table)
 * @param {object} props.expandableRows - Result from useExpandableRows hook
 * @param {Function} props.renderExpandedContent - Function to render expanded content: (row) => ReactElement
 * @param {string} props.expandIconColumn - Column key to show expand icon (default: first column)
 * @param {string} props.emptyMessage - Message when no data (default: 'No data available')
 * @param {string} props.size - Table size (sm, md, lg) (default: 'md')
 * @param {boolean} props.striped - Alternating row colors (default: false)
 * @param {boolean} props.bordered - Show borders (default: false)
 * @param {boolean} props.hover - Hover effects on rows (default: false)
 * @param {boolean} props.animateExpansion - Animate expand/collapse (default: true)
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.rest - Additional table attributes
 * @returns {React.ReactElement} ExpandableTable component
 */
```

## Scroll
```javascript
/**
 * Scrollable container component with custom styling
 * @param {object} props - Scroll props
 * @param {React.ReactNode} props.children - Content to scroll
 * @param {string} props.maxHeight - Maximum height (CSS value like '200px', '50vh')
 * @param {string} props.direction - Scroll direction ('vertical', 'horizontal', 'both')
 * @param {string} props.size - Scrollbar size (sm, md, lg)
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @param {object} props.rest - Additional div attributes
 * @returns {React.ReactElement} Scroll component
 */

// Constants
export const SCROLL_DIRECTIONS = {
  VERTICAL: 'vertical',
  HORIZONTAL: 'horizontal',
  BOTH: 'both'
};

export const SCROLL_SIZES = {
  SM: 'sm',
  MD: 'md',
  LG: 'lg'
};
```

## ToggleButton
```javascript
/**
 * Generic toggle button for collection management
 * @param {object} props - ToggleButton props
 * @param {boolean} props.isInCollection - Whether item is currently in the collection
 * @param {boolean} props.isCollectionFull - Whether collection is at max capacity
 * @param {boolean} props.isLoading - Whether a toggle operation is in progress
 * @param {boolean} props.hasError - Whether there's an error state
 * @param {Function} props.onToggle - Function to call when toggled
 * @param {string} props.itemName - Name of the item (for accessibility)
 * @param {string} props.collectionName - Name of the collection (for accessibility)
 * @param {string} props.size - Button size (sm, md, lg)
 * @param {number} props.maxItems - Maximum items in collection (for tooltips)
 * @param {boolean} props.disabled - Additional disabled state
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.rest - Additional props passed to the rendered component
 * @returns {React.ReactElement} ToggleButton component
 */
```

## FilterSelectGroup
```javascript
/**
 * FilterSelectGroup Component - Creates multiple filter dropdowns from options object
 * @param {object} props - FilterSelectGroup props
 * @param {object} props.filterOptions - Object with filter field names as keys and option arrays as values
 * @param {object} props.values - Current filter values object (e.g., {generation_type: 'llm', priority: 5})
 * @param {Function} props.onChange - Called when any filter changes: (fieldName, value, allValues) => {}
 * @param {boolean} props.disabled - Disable all dropdowns
 * @param {object} props.errors - Errors object with field names as keys
 * @param {string} props.layout - Layout style: 'grid' | 'horizontal' | 'vertical' (default: 'grid')
 * @param {object} props.customLabels - Override labels for specific fields (e.g., {prompt_name: 'Custom Prompt'})
 * @param {boolean} props.showPlaceholders - Show "Select..." placeholders (default: true)
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.rest - Additional HTML div attributes
 * @returns {React.ReactElement} FilterSelectGroup component
 */
```

## CoCaTok
```javascript
/**
 * Interactive collectable card token that spins in 3D space
 * @param {object} props - CoCaTok props
 * @param {string} props.color - Color name from color system (e.g., 'red-intense', 'blue-electric')
 * @param {string} props.size - Size variant ('sm', 'md', 'lg', 'xl')
 * @param {string} props.emoji - Emoji to display on the card (required)
 * @param {Function} props.onActivate - Callback when card completes its animation
 * @param {boolean} props.disabled - Disable interaction
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.style - Inline styles
 * @returns {React.ReactElement} CoCaTok component
 */

// Constants
export const COCATOK_SIZES = {
  SM: 'sm',
  MD: 'md', 
  LG: 'lg',
  XL: 'xl'
};
```

## Explosion
```javascript
/**
 * High-level preset-based explosion component
 * @param {string} props.type - Explosion type from EXPLOSION_TYPES (required)
 * @param {string} props.colorTheme - Color theme from COLOR_THEMES or color family name (default: 'fire')
 * @param {string} props.size - Size: 'sm', 'md', 'lg', 'xl', 'massive' (default: 'md')
 * @param {number} props.intensity - Intensity multiplier (0.5-3, default: 1)
 * @param {number} props.speed - Speed multiplier (0.5-3, default: 1)
 * @param {boolean} props.randomize - Randomize type and colors (default: false)
 * @param {Function} props.onComplete - Callback when finished
 * @param {boolean} props.autoStart - Start immediately (default: true)
 */

// Constants
export const EXPLOSION_TYPES = {
  PARTICLE_STORM: 'particle-storm',
  LIGHTNING_CRACK: 'lightning-crack',
  GRAVITY_IMPLOSION: 'gravity-implosion',
  PLASMA_VORTEX: 'plasma-vortex',
  NUCLEAR_DOME: 'nuclear-dome',
  CHAIN_REACTION: 'chain-reaction',
  SHOCKWAVE_BLAST: 'shockwave-blast',
  SHATTER_BREAK: 'shatter-break'
};
```

## BasicColorSelection
```javascript
/**
 * Basic color selection dropdown component
 * @param {object} props - BasicColorSelection props
 * @param {string} props.value - Currently selected color name (e.g., 'red-intense')
 * @param {Function} props.onChange - Called when color selection changes
 * @param {string} props.placeholder - Placeholder text (default: 'Select a color')
 * @param {boolean} props.disabled - Disable the selection
 * @param {string} props.error - Error message to display
 * @param {boolean} props.showHex - Show hex values in labels (default: false)
 * @param {boolean} props.showPreview - Show color preview box (default: true)
 * @param {string} props.className - Additional CSS classes
 * @param {Object} props.rest - Additional props passed to Select
 * @returns {React.ReactElement} BasicColorSelection component
 */
```