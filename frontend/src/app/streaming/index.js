// Streaming Module Exports - Clean exports for streaming domain logic
// Only exports the real transformers that match backend events

// ===== EVENT REGISTRY =====
export { 
  streamingEventRegistry, 
  initialStreamingState,
  getSupportedEventTypes,
  validateEventRegistry 
} from './eventRegistry.js';

// ===== DEFAULT EXPORT =====
export { streamingEventRegistry as default } from './eventRegistry.js';