// Generation API Service - Complete API communication for unified generation system
// Handles generation status, logs, streaming, and real-time functionality
// Returns raw API responses - no business logic or data transformation
// Updated to match complete backend API reference

import { get, post, getWithParams } from '../core/client.js';
import { API_ENDPOINTS } from '../core/config.js';

// ===== GENERATION SYSTEM STATUS =====

/**
 * Get generation system status
 * Includes LLM status, image status, queue info, and supported types
 * @returns {Promise<object>} Raw API response with generation system status
 */
export async function getGenerationStatus() {
  return await get(API_ENDPOINTS.GENERATION_STATUS);
}

/**
 * Get generation system statistics
 * Includes overall, LLM, and image generation statistics
 * @returns {Promise<object>} Raw API response with generation statistics
 */
export async function getGenerationStats() {
  return await get(API_ENDPOINTS.GENERATION_STATS);
}

// ===== GENERATION LOGS (New Unified System) =====

/**
 * Get generation logs with filtering and pagination
 * @param {object} options - Query options
 * @param {number} options.limit - Number of logs to return (1-100, default: 20)
 * @param {string} options.type - Filter by type ('llm', 'image')
 * @param {string} options.status - Filter by status ('pending', 'generating', 'completed', 'failed')
 * @param {string} options.prompt_type - Filter by prompt type
 * @returns {Promise<object>} Raw API response with generation logs
 */
export async function getGenerationLogs(options = {}) {
  const params = {};
  
  // Only include non-empty parameters
  if (options.limit !== undefined) params.limit = options.limit;
  if (options.type) params.type = options.type;
  if (options.status) params.status = options.status;
  if (options.prompt_type) params.prompt_type = options.prompt_type;
  
  return await getWithParams(API_ENDPOINTS.GENERATION_LOGS, params);
}

/**
 * Get detailed information about a specific generation log
 * @param {number} logId - ID of the log to retrieve
 * @returns {Promise<object>} Raw API response with detailed log data
 */
export async function getGenerationLogDetail(logId) {
  return await get(API_ENDPOINTS.GENERATION_LOG_DETAIL(logId));
}

// ===== STREAMING & REAL-TIME =====

/**
 * Get streaming connections information
 * Shows active connections and supported event types
 * @returns {Promise<object>} Raw API response with streaming connection info
 */
export async function getStreamingConnections() {
  return await get(API_ENDPOINTS.STREAMING_CONNECTIONS);
}

/**
 * Test streaming functionality with simple generation
 * @param {object} options - Test options
 * @returns {Promise<object>} Raw API response with test initiation results
 */
export async function testStreaming(options = {}) {
  return await post(API_ENDPOINTS.STREAMING_TEST, options);
}

/**
 * Get Server-Sent Events stream URL for real-time generation updates
 * Note: This is not an API call but returns the SSE endpoint URL
 * @returns {string} SSE endpoint URL for EventSource connection
 */
export function getStreamingEventsUrl() {
  return `http://localhost:5000${API_ENDPOINTS.STREAMING_EVENTS}`;
}


// ===== UTILITY FUNCTIONS =====

/**
 * Test generation API connectivity
 * Useful for debugging and health checks
 * @returns {Promise<object>} Raw API response
 */
export async function testGenerationApi() {
  return await get(API_ENDPOINTS.GENERATION_STATUS);
}