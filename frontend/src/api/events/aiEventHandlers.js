// AI Event Handlers - External (non-React) event handling
// Transforms SSE events and broadcasts to state stores
// No React state - just pure event transformation and routing

import {
  transformAiQueueItem,
  transformAiQueueItems,
  transformImageGenerationResult,
  transformLlmGenerationResult,
} from '../transformers/ai.js';
import { broadcastEvent } from '../core/eventBroadcast.js';

/**
 * AI Event Handlers - External event processing system
 * Each handler transforms event data and broadcasts to state stores
 */
export const aiEventHandlers = {
  'llm.generation.started': (eventData) => {
    const transformedData = {
      aiQueueItem: transformAiQueueItem(eventData.item),
      generationId: eventData.generation_id || null,
    };
    broadcastEvent('llmGenerationStarted', transformedData);
  },

  'llm.generation.update': (eventData) => {
    const transformedData = {
      generationId: eventData.generation_id || null,
      partialText: eventData.partial_text || '',
      tokensSoFar: eventData.tokens_so_far || '',
    };
    broadcastEvent('llmGenerationUpdate', transformedData);
  },

  'llm.generation.completed': (eventData) => {
    const transformedData = {
      aiQueueItem: transformAiQueueItem(eventData.item),
      generationId: eventData.generation_id || null,
      result: transformLlmGenerationResult(eventData.result),
    };
    broadcastEvent('llmGenerationCompleted', transformedData);
  },

  'llm.generation.failed': (eventData) => {
    const transformedData = {
      aiQueueItem: transformAiQueueItem(eventData.item),
      generationId: eventData.generation_id || null,
      error: eventData.error || null,
    };
    broadcastEvent('llmGenerationFailed', transformedData);
  },

  'ai.queue.update': (eventData) => {
    const transformedData = {
      trigger: eventData.trigger || null,
      allAiQueueItems: transformAiQueueItems(eventData.all_items),
    };
    broadcastEvent('aiQueueUpdate', transformedData);
  },

  'image.generation.started': (eventData) => {
    const transformedData = {
      aiQueueItem: transformAiQueueItem(eventData.item),
      generationId: eventData.generation_id || null,
    };
    broadcastEvent('imageGenerationStarted', transformedData);
  },

  'image.generation.update': (eventData) => {
    const transformedData = {
      aiQueueItem: transformAiQueueItem(eventData.item),
      generationId: eventData.generation_id || null,
      elapsedSeconds: eventData.elapsed_seconds || null,
    };
    broadcastEvent('imageGenerationUpdate', transformedData);
  },

  'image.generation.completed': (eventData) => {
    const transformedData = {
      aiQueueItem: transformAiQueueItem(eventData.item),
      generationId: eventData.generation_id || null,
      result: transformImageGenerationResult(eventData.result),
    };
    broadcastEvent('imageGenerationCompleted', transformedData);
  },

  'image.generation.failed': (eventData) => {
    const transformedData = {
      aiQueueItem: transformAiQueueItem(eventData.item),
      generationId: eventData.generation_id || null,
      error: eventData.error || null,
    };
    broadcastEvent('imageGenerationFailed', transformedData);
  },
};
