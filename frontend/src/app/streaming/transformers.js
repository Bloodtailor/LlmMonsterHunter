// Streaming Transformers - Transform SSE event data to camelCase
// UPDATED TO MATCH BACKEND API REFERENCE EXACTLY
// Handles snake_case → camelCase transformation for all streaming events

/**
 * Transform generation item data (used in multiple events)
 * @param {object} item - Raw generation item from backend
 * @returns {object} Transformed generation item in camelCase
 */
export function transformGenerationItem(item) {
  if (!item) return null;
  
  return {
    id: item.id || null,
    promptType: item.prompt_type || null,
    promptName: item.prompt_name || null,
    generationType: item.generation_type || null,
    status: item.status || 'unknown',
    priority: item.priority || 0,
    
    // Timing
    startedAt: item.started_at || null,
    completedAt: item.completed_at || null,
    durationSeconds: item.duration_seconds || null,
    
    // Progress tracking  
    tokensSoFar: item.tokens_so_far || 0,
    tokensGenerated: item.tokens_generated || 0,
    attemptsUsed: item.attempts_used || 0,
    maxAttempts: item.max_attempts || 1,
    
    // Text content
    partialText: item.partial_text || '',
    finalText: item.final_text || '',
    
    // Status flags
    isCompleted: item.is_completed || false,
    isFailed: item.is_failed || false,
    
    // Request tracking
    requestId: item.request_id || null,
    
    // Error info
    error: item.error || null,
    
    // Type-specific data
    llmData: item.llm_data || null,
    imageData: item.image_data || null
  };
}

/**
 * Transform queue update data (from queue_update events)
 * @param {object} eventData - Raw queue update event
 * @returns {object} Transformed queue update in camelCase
 */
export function transformQueueUpdate(eventData) {
  if (!eventData) return null;
  
  return {
    action: eventData.action || null,
    queueSize: eventData.queue_size || 0,
    item: eventData.item ? transformGenerationItem(eventData.item) : null
  };
}

/**
 * Transform generation update data (from generation_update events)
 * @param {object} eventData - Raw generation update event
 * @returns {object} Transformed update data in camelCase  
 */
export function transformGenerationUpdate(eventData) {
  if (!eventData) return null;
  
  return {
    generationId: eventData.generation_id || null,
    partialText: eventData.partial_text || '',
    tokensSoFar: eventData.tokens_so_far || 0
  };
}

/**
 * Transform generation started event data
 * @param {object} eventData - Raw generation started event
 * @returns {object} Transformed generation data
 */
export function transformGenerationStarted(eventData) {
  const baseItem = transformGenerationItem(eventData.item);
  
  return {
    ...baseItem,
    generationId: eventData.generation_id || null,
    status: 'generating' // Override status for started events
  };
}

/**
 * Transform generation completed event data  
 * @param {object} eventData - Raw generation completed event
 * @returns {object} Transformed completion data
 */
export function transformGenerationCompleted(eventData) {
  const baseItem = transformGenerationItem(eventData.item);
  
  return {
    ...baseItem,
    generationId: eventData.generation_id || null,
    status: 'completed', // Override status for completed events
    result: eventData.result || null
  };
}

/**
 * Transform generation failed event data
 * @param {object} eventData - Raw generation failed event  
 * @returns {object} Transformed failure data
 */
export function transformGenerationFailed(eventData) {
  const baseItem = transformGenerationItem(eventData.item);
  
  return {
    ...baseItem,
    generationId: eventData.generation_id || null,
    status: 'failed', // Override status for failed events
    error: eventData.error || baseItem.error
  };
}

/**
 * Transform image generation started event data
 * @param {object} eventData - Raw image generation started event
 * @returns {object} Transformed image generation data
 */
export function transformImageGenerationStarted(eventData) {
  const baseItem = transformGenerationItem(eventData.item);
  
  return {
    ...baseItem,
    generationId: eventData.generation_id || null,
    status: 'generating', // Override status for started events
    generationType: 'image'
  };
}

/**
 * Transform image generation update data
 * @param {object} eventData - Raw image generation update event
 * @returns {object} Transformed image update data
 */
export function transformImageGenerationUpdate(eventData) {
  if (!eventData) return null;
  
  return {
    generationId: eventData.generation_id || null,
    progressMessage: eventData.progress_message || ''
  };
}

/**
 * Transform image generation completed event data
 * @param {object} eventData - Raw image generation completed event
 * @returns {object} Transformed image completion data
 */
export function transformImageGenerationCompleted(eventData) {
  const baseItem = transformGenerationItem(eventData.item);
  
  return {
    ...baseItem,
    generationId: eventData.generation_id || null,
    status: 'completed',
    generationType: 'image',
    result: eventData.result || null
  };
}

/**
 * Transform image generation failed event data
 * @param {object} eventData - Raw image generation failed event
 * @returns {object} Transformed image failure data
 */
export function transformImageGenerationFailed(eventData) {
  const baseItem = transformGenerationItem(eventData.item);
  
  return {
    ...baseItem,
    generationId: eventData.generation_id || null,
    status: 'failed',
    generationType: 'image',
    error: eventData.error || baseItem.error
  };
}

/**
 * Transform SSE connection event data
 * @param {object} eventData - Raw SSE connection event
 * @returns {object} Transformed connection data
 */
export function transformSseConnected(eventData) {
  return {
    message: eventData.message || 'Connected to streaming'
  };
}

/**
 * Transform ping event data
 * @param {object} eventData - Raw ping event
 * @returns {object} Transformed ping data
 */
export function transformPing(eventData) {
  return {
    timestamp: eventData.timestamp || Date.now(),
    receivedAt: new Date()
  };
}