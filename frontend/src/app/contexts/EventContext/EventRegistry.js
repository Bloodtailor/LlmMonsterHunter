// Streaming Event Registry - Simple state mapping
// Each event stores its transformed data under its own state variable name
// Updated with "event" prefix for clarity

import {
  transformLlmGenerationStarted,
  transformLlmGenerationUpdate,
  transformLlmGenerationCompleted,
  transformLlmGenerationFailed,
  transformAiQueueUpdate,
  transformImageGenerationStarted,
  transformImageGenerationUpdate,
  transformImageGenerationCompleted,
  transformImageGenerationFailed
} from './transformers.js';

/**
 * Initial state structure for streaming events
 * Each event gets its own state variable with "event" prefix
 */
export const initialEventState = {
  // LLM events
  eventLlmGenerationStarted: null,
  eventLlmGenerationUpdate: null,
  eventLlmGenerationCompleted: null,
  eventLlmGenerationFailed: null,
  eventAiQueueUpdate: null,
  
  // Image events
  eventImageGenerationStarted: null,
  eventImageGenerationUpdate: null,
  eventImageGenerationCompleted: null,
  eventImageGenerationFailed: null,
  
  // Connection events
  eventPing: null
};

/**
 * Registry of all streaming events and their processing logic
 */
export const EventRegistry = {
  
  // ===== CONNECTION EVENTS =====
  
  'connected': {
    transform: (data) => ({
      message: data.message || 'Connected to streaming'
    }),
    updateState: (state, transformed) => {
      console.log('✅ SSE Connected:', transformed.message);
      return {
        ...state,
        connected: transformed,
        isConnected: true,
        connectionError: null,
        lastActivity: new Date()
      };
    }
  },

  'ping': {
    transform: (data) => ({}),
    updateState: (state, transformed) => ({
      ...state,
      eventPing: transformed,
      lastActivity: new Date()
    })
  },

  // ===== LLM GENERATION EVENTS =====

  'llm.generation.started': {
    transform: transformLlmGenerationStarted,
    updateState: (state, transformed) => {
      console.log('🚀 LLM Generation Started:', transformed.generationId);
      return {
        ...state,
        eventLlmGenerationStarted: transformed,
        lastActivity: new Date()
      };
    }
  },

  'llm.generation.update': {
    transform: transformLlmGenerationUpdate,
    updateState: (state, transformed) => {
      return {
        ...state,
        eventLlmGenerationUpdate: transformed,
        lastActivity: new Date()
      };
    }
  },

  'llm.generation.completed': {
    transform: transformLlmGenerationCompleted,
    updateState: (state, transformed) => {
      console.log('✅ LLM Generation Completed:', transformed.generationId);
      return {
        ...state,
        eventLlmGenerationCompleted: transformed,
        lastActivity: new Date()
      };
    }
  },

  'llm.generation.failed': {
    transform: transformLlmGenerationFailed,
    updateState: (state, transformed) => {
      console.error('❌ LLM Generation Failed:', transformed.error);
      return {
        ...state,
        eventLlmGenerationFailed: transformed,
        lastActivity: new Date()
      };
    }
  },

  // ===== AI QUEUE EVENTS =====

  'ai.queue.update': {
    transform: transformAiQueueUpdate,
    updateState: (state, transformed) => {
      console.log('📋 AI Queue Update:', transformed.trigger);
      return {
        ...state,
        eventAiQueueUpdate: transformed,
        lastActivity: new Date()
      };
    }
  },

  // ===== IMAGE GENERATION EVENTS =====

  'image.generation.started': {
    transform: transformImageGenerationStarted,
    updateState: (state, transformed) => {
      console.log('🖼️ Image Generation Started:', transformed.generationId);
      return {
        ...state,
        eventImageGenerationStarted: transformed,
        lastActivity: new Date()
      };
    }
  },

  'image.generation.update': {
    transform: transformImageGenerationUpdate,
    updateState: (state, transformed) => {
      return {
        ...state,
        eventImageGenerationUpdate: transformed,
        lastActivity: new Date()
      };
    }
  },

  'image.generation.completed': {
    transform: transformImageGenerationCompleted,
    updateState: (state, transformed) => {
      console.log('✅ Image Generation Completed:', transformed.generationId);
      return {
        ...state,
        eventImageGenerationCompleted: transformed,
        lastActivity: new Date()
      };
    }
  },

  'image.generation.failed': {
    transform: transformImageGenerationFailed,
    updateState: (state, transformed) => {
      console.error('❌ Image Generation Failed:', transformed.error);
      return {
        ...state,
        eventImageGenerationFailed: transformed,
        lastActivity: new Date()
      };
    }
  }
};

/**
 * Get list of all supported event types
 */
export function getSupportedEventTypes() {
  return Object.keys(EventRegistry);
}

/**
 * Validate that all events in registry have required properties
 */
export function validateEventRegistry() {
  const errors = [];
  
  Object.entries(EventRegistry).forEach(([eventType, config]) => {
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