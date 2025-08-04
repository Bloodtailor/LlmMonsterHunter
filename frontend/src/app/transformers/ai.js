// AI Queue Item Transformer - Reusable for all events with queue items
// Transforms snake_case backend queue item data to camelCase frontend format
// Used by events that include 'item' field (LLM/image generation events)

/**
 * Transform AI queue item from backend format to frontend format
 * Backend item structure from QueueItem.to_dict():
 * {
 *   generation_id, generation_type, prompt_type, prompt_name,
 *   priority, created_at, status, result, error, started_at, completed_at
 * }
 * 
 * @param {Object|null} aiQueueItem - Queue item from backend event
 * @returns {Object|null} Transformed queue item in camelCase
 */
export function transformAiQueueItem(aiQueueItem) {
  // Handle null/undefined items
  if (!aiQueueItem) {
    return null;
  }

  return {
    generationId: aiQueueItem.generation_id || null,
    generationType: aiQueueItem.generation_type || null,
    promptType: aiQueueItem.prompt_type || null,
    promptName: aiQueueItem.prompt_name || null,
    priority: aiQueueItem.priority || null,
    createdAt: aiQueueItem.created_at || null,
    status: aiQueueItem.status || null,
    result: aiQueueItem.result || null,
    error: aiQueueItem.error || null,
    startedAt: aiQueueItem.started_at || null,
    completedAt: aiQueueItem.completed_at || null
  };
}

/**
 * Transform array of AI queue items
 * Used by ai.queue.update event which sends all_items array
 * 
 * @param {Array|null} aiQueueItems - Array of queue items from backend
 * @returns {Array|null} Array of transformed queue items
 */
export function transformAiQueueItems(aiQueueItems) {
  // Handle null/undefined arrays
  if (!Array.isArray(aiQueueItems)) {
    return null;
  }

  return aiQueueItems.map(item => transformAiQueueItem(item));
}

/**
 * Transform LLM generation result from backend format to frontend format
 * Backend LLM result structure:
 * {
 *   text, parsed_data, tokens, duration, tokens_per_second,
 *   generation_id, attempt, parsing_success, parsing_error
 * }
 * 
 * @param {Object|null} LlmResult - LLM result from backend event
 * @returns {Object|null} Transformed LLM result in camelCase
 */
export function transformLlmGenerationResult(LlmResult) {
  // Handle null/undefined results
  if (!LlmResult) {
    return null;
  }

  return {
    text: LlmResult.text || null,
    parsedData: LlmResult.parsed_data || null,
    tokens: LlmResult.tokens || null,
    duration: LlmResult.duration || null,
    tokensPerSecond: LlmResult.tokens_per_second || null,
    generationId: LlmResult.generation_id || null,
    attempt: LlmResult.attempt || null,
    parsingSuccess: LlmResult.parsing_success || null,
    parsingError: LlmResult.parsing_error || null
  };
}

/**
 * Transform image generation result from backend format to frontend format
 * Backend image result structure:
 * {
 *   image_path, execution_time, generation_id, workflow_used,
 *   prompt_id, image_dimensions
 * }
 * 
 * @param {Object|null} imageResult - Image result from backend event
 * @returns {Object|null} Transformed image result in camelCase
 */
export function transformImageGenerationResult(imageResult) {
  // Handle null/undefined results
  if (!imageResult) {
    return null;
  }

  return {
    imagePath: imageResult.image_path || null,
    executionTime: imageResult.execution_time || null,
    generationId: imageResult.generation_id || null,
    workflowUsed: imageResult.workflow_used || null,
    promptId: imageResult.prompt_id || null,
    imageDimensions: imageResult.image_dimensions || null
  };
}