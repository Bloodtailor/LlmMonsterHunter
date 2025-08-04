// Streaming Transformers - 1:1 mapping with backend events
// Only transforms the exact fields that exist in each event
// No made-up fields, no shared helpers, just clean transformation

// ===== LLM EVENT TRANSFORMERS =====

/**
 * Transform llm.generation.started event
 * Event data: { item, generation_id }
 */
export function transformLlmGenerationStarted(eventData) {
  return {
    item: eventData.item || null,
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
    item: eventData.item || null,
    generationId: eventData.generation_id || null,
    result: eventData.result || null
  };
}

/**
 * Transform llm.generation.failed event
 * Event data: { item, generation_id, error }
 */
export function transformLlmGenerationFailed(eventData) {
  return {
    item: eventData.item || null,
    generationId: eventData.generation_id || null,
    error: eventData.error || null
  };
}

/**
 * Transform llm.queue.update event
 * Event data: { action, item, queue_size }
 */
export function transformLlmQueueUpdate(eventData) {
  return {
    action: eventData.action || null,
    item: eventData.item || null,
    queueSize: eventData.queue_size || 0
  };
}

// ===== IMAGE EVENT TRANSFORMERS =====

/**
 * Transform image.generation.started event
 * Event data: { item, generation_id }
 */
export function transformImageGenerationStarted(eventData) {
  return {
    item: eventData.item || null,
    generationId: eventData.generation_id || null
  };
}

/**
 * Transform image.generation.update event
 * Event data: { item, generation_id, comfyui_queue_status_response }
 */
export function transformImageGenerationUpdate(eventData) {
  return {
    item: eventData.item || null,
    generationId: eventData.generation_id || null,
    elapsed_seconds: eventData.elapsed_seconds || null
  };
}

/**
 * Transform image.generation.completed event
 * Event data: { item, generation_id, result }
 */
export function transformImageGenerationCompleted(eventData) {
  return {
    item: eventData.item || null,
    generationId: eventData.generation_id || null,
    result: eventData.result || null
  };
}

/**
 * Transform image.generation.failed event
 * Event data: { item, generation_id, error }
 */
export function transformImageGenerationFailed(eventData) {
  return {
    item: eventData.item || null,
    generationId: eventData.generation_id || null,
    error: eventData.error || null
  };
}

/**
 * Transform image.queue.update event
 * Event data: { action, item, queue_size }
 */
export function transformImageQueueUpdate(eventData) {
  return {
    action: eventData.action || null,
    item: eventData.item || null,
    queueSize: eventData.queue_size || 0
  };
}