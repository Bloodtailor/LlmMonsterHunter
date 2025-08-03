// Streaming Transformers - Transform SSE event data to camelCase
// Follows the same pattern as app/transformers/monsters.js
// Handles snake_case → camelCase transformation for streaming events

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
    startedAt: item.started_at || null,
    completedAt: item.completed_at || null,
    requestId: item.request_id || null,
    
    // Text content
    partialText: item.partial_text || '',
    finalText: item.final_text || '',
    
    // Progress tracking  
    tokensSoFar: item.tokens_so_far || 0,
    tokensGenerated: item.tokens_generated || 0,
    duration: item.duration || null,
    
    // Status and errors
    status: item.status || 'unknown',
    error: item.error || null
  };
}

/**
 * Transform queue status data
 * @param {object} queueData - Raw queue status from backend  
 * @returns {object} Transformed queue status in camelCase
 */
export function transformQueueStatus(queueData) {
  if (!queueData) return null;
  
  return {
    queueSize: queueData.queue_size || 0,
    totalItems: queueData.total_items || 0,
    statusCounts: {
      pending: queueData.status_counts?.pending || 0,
      generating: queueData.status_counts?.generating || 0,
      completed: queueData.status_counts?.completed || 0,
      failed: queueData.status_counts?.failed || 0
    }
  };
}

/**
 * Transform generation update data
 * @param {object} updateData - Raw generation update from backend
 * @returns {object} Transformed update data in camelCase  
 */
export function transformGenerationUpdate(updateData) {
  if (!updateData) return null;
  
  return {
    partialText: updateData.partial_text || '',
    tokensSoFar: updateData.tokens_so_far || 0
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
    status: 'generating', // Override status for started events
    requestId: eventData.request_id || baseItem.requestId
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
    status: 'completed', // Override status for completed events
    finalText: eventData.final_text || baseItem.finalText,
    tokensGenerated: eventData.tokens_generated || baseItem.tokensGenerated,
    duration: eventData.duration || baseItem.duration
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
    status: 'failed', // Override status for failed events
    error: eventData.error || baseItem.error
  };
}