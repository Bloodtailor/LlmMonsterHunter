// Streaming Event Registry - Configuration for all SSE events
// UPDATED TO MATCH BACKEND API REFERENCE EXACTLY
// Each event defines its transformation and state update logic

import {
  transformQueueUpdate,
  transformGenerationStarted,
  transformGenerationUpdate,
  transformGenerationCompleted,
  transformGenerationFailed,
  transformImageGenerationStarted,
  transformImageGenerationUpdate,
  transformImageGenerationCompleted,
  transformImageGenerationFailed,
  transformSseConnected,
  transformPing
} from './transformers.js';

/**
 * Initial state structure for streaming events
 * This defines what data the streaming system manages
 */
export const initialStreamingState = {
  currentGeneration: null,
  streamingText: '',
  queueStatus: null,
  imageGeneration: null,
  imageProgress: '',
  lastPing: null
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
  'sse.connected': {
    transform: transformSseConnected,
    updateState: (state, transformed) => {
      console.log('✅ SSE Connected:', transformed.message);
      return state; // No state change needed, just logging
    }
  },

  /**
   * Keep-alive ping events
   */
  'ping': {
    transform: transformPing,
    updateState: (state, transformed) => ({
      ...state,
      lastPing: transformed
    })
  },

  /**
   * Queue update events (action, item, queue_size)
   */
  'queue_update': {
    transform: transformQueueUpdate,
    updateState: (state, transformed) => ({
      ...state,
      queueStatus: transformed
    })
  },

  /**
   * LLM Generation started event
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
   * LLM Generation update (streaming text)
   */
  'generation_update': {
    transform: transformGenerationUpdate,
    updateState: (state, transformed) => ({
      ...state,
      streamingText: transformed.partialText,
      currentGeneration: state.currentGeneration ? {
        ...state.currentGeneration,
        tokensSoFar: transformed.tokensSoFar,
        generationId: transformed.generationId
      } : null
    })
  },

  /**
   * LLM Generation completed event
   */
  'generation_completed': {
    transform: transformGenerationCompleted,
    updateState: (state, transformed) => ({
      ...state,
      currentGeneration: transformed,
      streamingText: transformed.result?.final_text || state.streamingText
    })
  },

  /**
   * LLM Generation failed event
   */
  'generation_failed': {
    transform: transformGenerationFailed,
    updateState: (state, transformed) => ({
      ...state,
      currentGeneration: transformed
    })
  },

  /**
   * Image Generation started event
   */
  'image.generation.started': {
    transform: transformImageGenerationStarted,
    updateState: (state, transformed) => ({
      ...state,
      imageGeneration: transformed,
      imageProgress: 'Starting image generation...'
    })
  },

  /**
   * Image Generation update (progress)
   */
  'image.generation.update': {
    transform: transformImageGenerationUpdate,
    updateState: (state, transformed) => ({
      ...state,
      imageProgress: transformed.progressMessage,
      imageGeneration: state.imageGeneration ? {
        ...state.imageGeneration,
        generationId: transformed.generationId
      } : null
    })
  },

  /**
   * Image Generation completed event
   */
  'image.generation.completed': {
    transform: transformImageGenerationCompleted,
    updateState: (state, transformed) => ({
      ...state,
      imageGeneration: transformed,
      imageProgress: 'Image generation completed!'
    })
  },

  /**
   * Image Generation failed event
   */
  'image.generation.failed': {
    transform: transformImageGenerationFailed,
    updateState: (state, transformed) => ({
      ...state,
      imageGeneration: transformed,
      imageProgress: `Image generation failed: ${transformed.error}`
    })
  }
};

/**
 * Get all supported event types
 * @returns {string[]} Array of supported event type names
 */
export function getSupportedEventTypes() {
  return Object.keys(streamingEventRegistry);
}

/**
 * Validate that event registry is properly configured
 * @returns {boolean} True if valid, throws error if invalid
 */
export function validateEventRegistry() {
  const requiredEvents = [
    'sse.connected',
    'ping', 
    'queue_update',
    'generation_started',
    'generation_update', 
    'generation_completed',
    'generation_failed',
    'image.generation.started',
    'image.generation.update',
    'image.generation.completed',
    'image.generation.failed'
  ];

  const registeredEvents = getSupportedEventTypes();
  const missingEvents = requiredEvents.filter(event => !registeredEvents.includes(event));

  if (missingEvents.length > 0) {
    throw new Error(`Missing required event types in registry: ${missingEvents.join(', ')}`);
  }

  // Validate each event has required functions
  for (const [eventType, config] of Object.entries(streamingEventRegistry)) {
    if (typeof config.transform !== 'function') {
      throw new Error(`Event '${eventType}' missing transform function`);
    }
    if (typeof config.updateState !== 'function') {
      throw new Error(`Event '${eventType}' missing updateState function`);
    }
  }

  console.log('✅ Event registry validation passed');
  return true;
}