// Streaming Event Registry - Configuration for all SSE events
// Each event defines its transformation and state update logic
// Adding new events = adding new config objects (no code changes)

import {
  transformQueueStatus,
  transformGenerationStarted,
  transformGenerationUpdate,
  transformGenerationCompleted,
  transformGenerationFailed
} from './transformers.js';

/**
 * Initial state structure for streaming events
 * This defines what data the streaming system manages
 */
export const initialStreamingState = {
  currentGeneration: null,
  streamingText: '',
  queueStatus: null
};

/**
 * Registry of all streaming events and their processing logic
 * Each event defines:
 * - transform: function to convert raw data to camelCase
 * - updateState: function to update the streaming state
 */
export const streamingEventRegistry = {
  
  /**
   * SSE connection established
   */
  'connected': {
    transform: (data) => ({
      message: data.message || 'Connected to streaming'
    }),
    updateState: (state, transformed) => {
      console.log('✅ SSE Connected:', transformed.message);
      return state; // No state change needed, just logging
    }
  },

  /**
   * Queue status update
   */
  'queue_status': {
    transform: transformQueueStatus,
    updateState: (state, transformed) => ({
      ...state,
      queueStatus: transformed
    })
  },

  /**
   * Generation started event
   */
  'generation_started': {
    transform: transformGenerationStarted,
    updateState: (state, transformed) => ({
      ...state,
      currentGeneration: transformed,
      streamingText: '' // Reset streaming text for new generation
    })
  },

  /**
   * Generation update (streaming text)
   */
  'generation_update': {
    transform: transformGenerationUpdate,
    updateState: (state, transformed) => ({
      ...state,
      streamingText: transformed.partialText,
      currentGeneration: state.currentGeneration ? {
        ...state.currentGeneration,
        partialText: transformed.partialText,
        tokensSoFar: transformed.tokensSoFar
      } : null
    })
  },

  /**
   * Generation completed successfully
   */
  'generation_completed': {
    transform: transformGenerationCompleted,
    updateState: (state, transformed) => ({
      ...state,
      currentGeneration: transformed,
      streamingText: transformed.finalText || state.streamingText
    })
  },

  /**
   * Generation failed with error
   */
  'generation_failed': {
    transform: transformGenerationFailed,
    updateState: (state, transformed) => ({
      ...state,
      currentGeneration: transformed
    })
  },

  /**
   * Queue update notification
   */
  'queue_update': {
    transform: (data) => ({
      action: data.action || 'unknown',
      details: data.details || null
    }),
    updateState: (state, transformed) => {
      console.log('📥 Queue update:', transformed.action);
      return state; // No state change needed, just logging
    }
  },

  /**
   * Keep-alive ping
   */
  'ping': {
    transform: (data) => ({}),
    updateState: (state, transformed) => {
      // No action needed - lastActivity updated automatically by useEventSource
      return state;
    }
  }
};

/**
 * Get list of all supported event types
 * Useful for debugging and documentation
 */
export function getSupportedEventTypes() {
  return Object.keys(streamingEventRegistry);
}

/**
 * Validate that all events in registry have required properties
 * Useful for development error checking
 */
export function validateEventRegistry() {
  const errors = [];
  
  Object.entries(streamingEventRegistry).forEach(([eventType, config]) => {
    if (!config.transform || typeof config.transform !== 'function') {
      errors.push(`Event '${eventType}' missing transform function`);
    }
    if (!config.updateState || typeof config.updateState !== 'function') {
      errors.push(`Event '${eventType}' missing updateState function`);
    }
  });
  
  if (errors.length > 0) {
    console.error('Event Registry Validation Errors:', errors);
    return false;
  }
  
  return true;
}