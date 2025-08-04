// Streaming Module Exports - Clean exports for streaming domain logic
// Only exports the real transformers that match backend events

// ===== EVENT REGISTRY =====
export { 
  streamingEventRegistry, 
  initialStreamingState,
  getSupportedEventTypes,
  getLlmEventTypes,
  getImageEventTypes,
  validateEventRegistry 
} from './eventRegistry.js';

// ===== LLM EVENT TRANSFORMERS =====
export {
  transformLlmGenerationStarted,
  transformLlmGenerationUpdate,
  transformLlmGenerationCompleted,
  transformLlmGenerationFailed,
  transformLlmQueueUpdate
} from './transformers.js';

// ===== IMAGE EVENT TRANSFORMERS =====
export {
  transformImageGenerationStarted,
  transformImageGenerationUpdate,
  transformImageGenerationCompleted,
  transformImageGenerationFailed,
  transformImageQueueUpdate
} from './transformers.js';

// ===== DEFAULT EXPORT =====
export { streamingEventRegistry as default } from './eventRegistry.js';