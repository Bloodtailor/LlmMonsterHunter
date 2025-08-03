// StreamingContext Exports - Clean imports for streaming context components
// Simplified exports since we no longer need domain hooks

// ===== CONTEXT & PROVIDER =====
export { StreamingContext } from './StreamingContext.js';
export { default as StreamingProvider } from './StreamingProvider.js';

// ===== CONSUMER HOOKS =====
export { useStreaming } from './useStreamingContext.js';

// ===== DEFAULT EXPORT =====
// Default to the provider for easy import
export { default } from './StreamingProvider.js';