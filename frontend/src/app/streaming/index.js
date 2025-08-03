// Streaming Module Exports - Clean imports for streaming domain logic
// UPDATED: Now exports all transformers to match API reference

// ===== EVENT REGISTRY =====
export { 
  streamingEventRegistry, 
  initialStreamingState,
  getSupportedEventTypes,
  validateEventRegistry 
} from './eventRegistry.js';

// ===== TRANSFORMERS =====
export {
  // Core transformers
  transformGenerationItem,
  
  // LLM Generation event transformers
  transformQueueUpdate,
  transformGenerationStarted,
  transformGenerationUpdate,
  transformGenerationCompleted,
  transformGenerationFailed,
  
  // Image Generation event transformers
  transformImageGenerationStarted,
  transformImageGenerationUpdate,
  transformImageGenerationCompleted,
  transformImageGenerationFailed,
  
  // Connection event transformers
  transformSseConnected,
  transformPing
} from './transformers.js';

// ===== DEFAULT EXPORT =====
// Default to the event registry for easy import
export { streamingEventRegistry as default } from './eventRegistry.js';