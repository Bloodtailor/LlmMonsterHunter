import { useState } from 'react';
import { transformAiQueueItem, transformAiQueueItems, transformImageGenerationResult, transformLlmGenerationResult } from "../transformers/ai.js"

export const useAiEvents = () => {
  // Create one useState(null) per event
  const [llmGenerationStartedEvent, setLlmGenerationStartedEvent] = useState(null);
  const [llmGenerationUpdateEvent, setLlmGenerationUpdateEvent] = useState(null);
  const [llmGenerationCompletedEvent, setLlmGenerationCompletedEvent] = useState(null);
  const [llmGenerationFailedEvent, setLlmGenerationFailedEvent] = useState(null);
  const [aiQueueUpdateEvent, setAiQueueUpdateEvent] = useState(null);
  const [imageGenerationStartedEvent, setImageGenerationStartedEvent] = useState(null);
  const [imageGenerationUpdateEvent, setImageGenerationUpdateEvent] = useState(null);
  const [imageGenerationCompletedEvent, setImageGenerationCompletedEvent] = useState(null);
  const [imageGenerationFailedEvent, setImageGenerationFailedEvent] = useState(null);

  // Define eventHandlers object
  const eventHandlers = {
    'llm.generation.started': (eventData) => {
      // Transform eventData directly
      const transformedData = {
        aiQueueItem: transformAiQueueItem(eventData.item),
        generationId: eventData.generation_id || null
      };
      setLlmGenerationStartedEvent(transformedData);
    },
    'llm.generation.update': (eventData) => {
      // Transform eventData directly
      const transformedData = {
        generationId: eventData.generation_id || null,
        partialText: eventData.partial_text || '',
        tokensSoFar: eventData.tokens_so_far || ''
      };
      setLlmGenerationUpdateEvent(transformedData);
    },
    'llm.generation.completed': (eventData) => {
      // Transform eventData directly
      const transformedData = {
        aiQueueItem: transformAiQueueItem(eventData.item),
        generationId: eventData.generation_id || null,
        result: transformLlmGenerationResult(eventData.result)
      };
      setLlmGenerationCompletedEvent(transformedData);
    },
    'llm.generation.failed': (eventData) => {
      // Transform eventData directly
      const transformedData = {
        aiQueueItem: transformAiQueueItem(eventData.item),
        generationId: eventData.generation_id || null,
        error: eventData.error || null
      };
      setLlmGenerationFailedEvent(transformedData);
    },
    'ai.queue.update': (eventData) => {
      // Transform eventData directly
      const transformedData = {
        trigger: eventData.trigger || null,
        allAiQueueItems: transformAiQueueItems(eventData.all_items)
      };
      setAiQueueUpdateEvent(transformedData);
    },
    'image.generation.started': (eventData) => {
      // Transform eventData directly
      const transformedData = {
        aiQueueItem: transformAiQueueItem(eventData.item),
        generationId: eventData.generation_id || null
      };
      setImageGenerationStartedEvent(transformedData);
    },
    'image.generation.update': (eventData) => {
      // Transform eventData directly
      const transformedData = {
        aiQueueItem: transformAiQueueItem(eventData.item),
        generationId: eventData.generation_id || null,
        elapsedSeconds: eventData.elapsed_seconds || null
      };
      setImageGenerationUpdateEvent(transformedData);
    },
    'image.generation.completed': (eventData) => {
      // Transform eventData directly
      const transformedData = {
        aiQueueItem: transformAiQueueItem(eventData.item),
        generationId: eventData.generation_id || null,
        result: transformImageGenerationResult(eventData.result)
      };
      setImageGenerationCompletedEvent(transformedData);
    },
    'image.generation.failed': (eventData) => {
      // Transform eventData directly
      const transformedData = {
        aiQueueItem: transformAiQueueItem(eventData.item),
        generationId: eventData.generation_id || null,
        error: eventData.error || null
      };
      setImageGenerationFailedEvent(transformedData);
    }
  };

  return {
    state: {
      llmGenerationStartedEvent,
      llmGenerationUpdateEvent,
      llmGenerationCompletedEvent,
      llmGenerationFailedEvent,
      aiQueueUpdateEvent,
      imageGenerationStartedEvent,
      imageGenerationUpdateEvent,
      imageGenerationCompletedEvent,
      imageGenerationFailedEvent
    },
    eventHandlers
  };
};