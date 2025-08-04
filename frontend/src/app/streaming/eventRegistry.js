// Streaming Event Registry - Simple state mapping
// Each event stores its transformed data under its own state variable name

import {
  transformLlmGenerationStarted,
  transformLlmGenerationUpdate,
  transformLlmGenerationCompleted,
  transformLlmGenerationFailed,
  transformLlmQueueUpdate,
  transformImageGenerationStarted,
  transformImageGenerationUpdate,
  transformImageGenerationCompleted,
  transformImageGenerationFailed,
  transformImageQueueUpdate
} from './transformers.js';

/**
 * Initial state structure for streaming events
 * Each event gets its own state variable
 */
export const initialStreamingState = {
  // LLM events
  llmGenerationStarted: null,
  llmGenerationUpdate: null,
  llmGenerationCompleted: null,
  llmGenerationFailed: null,
  llmQueueUpdate: null,
  
  // Image events
  imageGenerationStarted: null,
  imageGenerationUpdate: null,
  imageGenerationCompleted: null,
  imageGenerationFailed: null,
  imageQueueUpdate: null,
  
  // Connection events
  connected: null,
  ping: null,
};

/**
 * Registry of all streaming events and their processing logic
 */
export const streamingEventRegistry = {
  
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
      ping: transformed,
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
        llmGenerationStarted: transformed,
        lastActivity: new Date()
      };
    }
  },

  'llm.generation.update': {
    transform: transformLlmGenerationUpdate,
    updateState: (state, transformed) => {
      return {
        ...state,
        llmGenerationUpdate: transformed,
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
        llmGenerationCompleted: transformed,
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
        llmGenerationFailed: transformed,
        lastActivity: new Date()
      };
    }
  },

  'llm.queue.update': {
    transform: transformLlmQueueUpdate,
    updateState: (state, transformed) => {
      console.log('📥 LLM Queue Update:', transformed.action, 'Queue size:', transformed.queueSize);
      return {
        ...state,
        llmQueueUpdate: transformed,
        lastActivity: new Date()
      };
    }
  },

  // ===== IMAGE GENERATION EVENTS =====

  'image.generation.started': {
    transform: transformImageGenerationStarted,
    updateState: (state, transformed) => {
      console.log('🎨 Image Generation Started:', transformed.generationId);
      return {
        ...state,
        imageGenerationStarted: transformed,
        lastActivity: new Date()
      };
    }
  },

  'image.generation.update': {
    transform: transformImageGenerationUpdate,
    updateState: (state, transformed) => {
      return {
        ...state,
        imageGenerationUpdate: transformed,
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
        imageGenerationCompleted: transformed,
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
        imageGenerationFailed: transformed,
        lastActivity: new Date()
      };
    }
  },

  'image.queue.update': {
    transform: transformImageQueueUpdate,
    updateState: (state, transformed) => {
      console.log('📥 Image Queue Update:', transformed.action, 'Queue size:', transformed.queueSize);
      return {
        ...state,
        imageQueueUpdate: transformed,
        lastActivity: new Date()
      };
    }
  }
};

/**
 * Get list of all supported event types
 */
export function getSupportedEventTypes() {
  return Object.keys(streamingEventRegistry);
}

/**
 * Get list of LLM-specific event types
 */
export function getLlmEventTypes() {
  return Object.keys(streamingEventRegistry).filter(eventType => 
    eventType.startsWith('llm.')
  );
}

/**
 * Get list of Image-specific event types
 */
export function getImageEventTypes() {
  return Object.keys(streamingEventRegistry).filter(eventType => 
    eventType.startsWith('image.')
  );
}

/**
 * Validate that all events in registry have required properties
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