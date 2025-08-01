// UI Primitives Master Export - Single source for all UI components
// Allows for clean imports like: import { Button, StatusBadge, Alert, Input, Select } from 'shared/components/ui'
// Organizes all primitives for easy discovery and consistent imports

// ===== BUTTON COMPONENTS =====
export {
  Button,
  IconButton, 
  ButtonGroup,
  BUTTON_VARIANTS,
  BUTTON_SIZES,
  BUTTON_GROUP_ORIENTATIONS,
  BUTTON_GROUP_SPACING,
  BUTTON_GROUP_ALIGNMENT
} from './primitives/Button/index.js';

// ===== BADGE COMPONENTS =====
export {
  Badge,
  StatusBadge,
  CountBadge,
  BADGE_VARIANTS,
  BADGE_SIZES,
  STATUS_TYPES,
  COUNT_FORMATS
} from './primitives/Badge/index.js';

// ===== LOADING COMPONENTS =====
export {
  LoadingSpinner,
  LoadingContainer,
  LoadingSkeleton,
  LOADING_SIZES,
  LOADING_COLORS,
  LOADING_TYPES
} from './primitives/LoadingStates/index.js';

// ===== FEEDBACK COMPONENTS =====
export {
  Alert,
  EmptyState,
  ALERT_TYPES,
  ALERT_SIZES,
  EMPTY_STATE_SIZES,
  EMPTY_STATE_VARIANTS,
  EMPTY_STATE_PRESETS
} from './primitives/Feedback/index.js';

// ===== CARD COMPONENTS =====
export {
  Card,
  CardSection,
  CARD_VARIANTS,
  CARD_SIZES,
  CARD_PADDING,
  CARD_BACKGROUNDS,
  CARD_SECTION_TYPES,
  CARD_SECTION_ALIGNMENT
} from './primitives/Card/index.js';

// ===== FORM COMPONENTS (CORRECTED) =====
export {
  Input,
  Textarea,
  Select,
  SearchInput,
  FormField,
  Form
} from './primitives/Form/index.js';

// ===== PAGINATION COMPONENTS =====
export {
  Pagination,
  PaginationInfo,
  PageJumper,
  ItemsPerPageSelector
} from './Pagination/index.js';