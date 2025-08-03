// Streaming Module Exports - Clean imports for streaming domain logic
// Follows the established pattern from other domain modules

// ===== EVENT REGISTRY =====
export { 
  streamingEventRegistry, 
  initialStreamingState,
  getSupportedEventTypes,
  validateEventRegistry 
} from './eventRegistry.js';

// ===== TRANSFORMERS =====
export {
  transformGenerationItem,
  transformQueueStatus,
  transformGenerationUpdate,
  transformGenerationStarted,
  transformGenerationCompleted,
  transformGenerationFailed
} from './transformers.js';

// ===== DEFAULT EXPORT =====
// Default to the event registry for easy import
export { streamingEventRegistry as default } from './eventRegistry.js';