// Streaming Components Export - Clean imports for all streaming-related components
// Follows your established export pattern from shared/ui/index.js
// Allows for clean imports like: import { StreamingDisplay, useStreamingState } from 'components/streaming'

// ===== MAIN COMPONENTS =====
export { default as StreamingDisplay } from './StreamingDisplay.js';
export { default as StreamingHeader } from './StreamingHeader.js';
export { default as StreamingContent } from './StreamingContent.js';

// ===== HOOKS =====
export { useStreamingConnection } from './useStreamingConnection.js';
export { useStreamingState } from './useStreamingState.js';

// ===== CONSTANTS =====
export {
  STREAMING_CONFIG,
  STREAMING_EVENT_TYPES,
  GENERATION_STATUS,
  DISPLAY_STATES,
  STREAMING_SIZES,
  STREAMING_POSITIONS
} from './streamingConstants.js';

// ===== DEFAULT EXPORT =====
// Main component for easy import
export { default } from './StreamingDisplay.js';