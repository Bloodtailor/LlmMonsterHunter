// Streaming Transformers - 1:1 mapping with backend events
// Only transforms the exact fields that exist in each event
// No made-up fields, no shared helpers, just clean transformation


import { transformAiQueueItem, transformAiQueueItems, transformImageGenerationResult, transformLlmGenerationResult } from "../transformers/ai";

// ===== LLM EVENT TRANSFORMERS =====

/**
 * Transform llm.generation.started event
 * Event data: { item, generation_id }
 */
export function transformLlmGenerationStarted(eventData) {
  return {
    aiQueueItem: transformAiQueueItem(eventData.item),
    generationId: eventData.generation_id || null
  };
}

/**
 * Transform llm.generation.update event
 * Event data: { generation_id, partial_text, tokens_so_far }
 */
export function transformLlmGenerationUpdate(eventData) {
  return {
    generationId: eventData.generation_id || null,
    partialText: eventData.partial_text || '',
    tokensSoFar: eventData.tokens_so_far  || ''
  };
}

/**
 * Transform llm.generation.completed event
 * Event data: { item, generation_id, result }
 */
export function transformLlmGenerationCompleted(eventData) {
  return {
    aiQueueItem: transformAiQueueItem(eventData.item),
    generationId: eventData.generation_id || null,
    result: transformLlmGenerationResult(eventData.result)
  };
}

/**
 * Transform llm.generation.failed event
 * Event data: { item, generation_id, error }
 */
export function transformLlmGenerationFailed(eventData) {
  return {
    aiQueueItem: transformAiQueueItem(eventData.item),
    generationId: eventData.generation_id || null,
    error: eventData.error || null
  };
}

/**
 * Transform ai.queue.update event
 * Event data: { trigger, all_items }
 */
export function transformAiQueueUpdate(eventData) {
  return {
    trigger: eventData.trigger || null,
    allAiQueueItems: transformAiQueueItems(eventData.all_items)
  };
}

// ===== IMAGE EVENT TRANSFORMERS =====

/**
 * Transform image.generation.started event
 * Event data: { item, generation_id }
 */
export function transformImageGenerationStarted(eventData) {
  return {
    aiQueueItem: transformAiQueueItem(eventData.item),
    generationId: eventData.generation_id || null
  };
}

/**
 * Transform image.generation.update event
 * Event data: { item, generation_id, comfyui_queue_status_response }
 */
export function transformImageGenerationUpdate(eventData) {
  return {
    aiQueueItem: transformAiQueueItem(eventData.item),
    generationId: eventData.generation_id || null,
    elapsedSeconds: eventData.elapsed_seconds || null
  };
}

/**
 * Transform image.generation.completed event
 * Event data: { item, generation_id, result }
 */
export function transformImageGenerationCompleted(eventData) {
  return {
    aiQueueItem: transformAiQueueItem(eventData.item),
    generationId: eventData.generation_id || null,
    result: transformImageGenerationResult(eventData.result)
  };
}

/**
 * Transform image.generation.failed event
 * Event data: { item, generation_id, error }
 */
export function transformImageGenerationFailed(eventData) {
  return {
    aiQueueItem: transformAiQueueItem(eventData.item),
    generationId: eventData.generation_id || null,
    error: eventData.error || null
  };
}