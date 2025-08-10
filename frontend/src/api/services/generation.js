// Generation API Service - CORRECTED VERSION with minimal camelCase conversion
// Only converts main response keys ('filter_options' -> 'filterOptions')
// Keeps all actual option values exactly as they come from backend
// Properly converts parameters when sending to backend

import { get, post, getWithParams } from '../core/client.js';
import { transformGenerationLogs } from '../transformers/generation.js';

// ===== GENERATION LOGS (UNIFIED SYSTEM) =====

/**
 * Get generation logs with filtering and pagination
 * @param {object} options - Query options (camelCase for convenience)
 * @param {number} options.limit - Number of logs to return (1-100, default: 20)
 * @param {number} options.offset - Offset for pagination (0+, default: 0)
 * @param {string} options.type - Filter by type ('llm', 'image')
 * @param {string} options.status - Filter by status ('pending', 'generating', 'completed', 'failed')
 * @param {string} options.promptType - Filter by prompt type
 * @param {string} options.promptName - Filter by prompt name
 * @param {string} options.priority - Filter by priority
 * @param {string} options.startTime - Filter by start time
 * @param {string} options.sortBy - Field to sort by (backend field names like 'generation_type', 'id', etc)
 * @param {string} options.sortOrder - Sort order ('asc' or 'desc', default: 'desc')
 * @returns {Promise<object>} Clean transformed response with generation logs
 */
export async function getGenerationLogs(options = {}) {
  const params = {};
  
  // pagination options
  if (options.limit !== undefined) params.limit = options.limit;
  if (options.offset !== undefined) params.offset = options.offset;

  // sort options
  if (options.sortBy) params.sort_by = options.sortBy;
  if (options.sortOrder) params.sort_order = options.sortOrder;

  // filter options (snake_case)
  if (options.generation_type) params.generation_type = options.generation_type;
  if (options.status) params.status = options.status;
  if (options.prompt_type) params.prompt_type = options.prompt_type;
  if (options.prompt_name) params.prompt_name = options.prompt_name;
  if (options.priority) params.priority = options.priority;
  
  const response = await getWithParams('/api/generation/logs', params);
  
  return {
    logs: transformGenerationLogs(response.data?.logs ?? getGenerationLogs.defaults.logs),
    count: response.data?.count ?? getGenerationLogs.defaults.count,
    returnedCount: response.data?.returned_count ?? 0,
    filters: response.data?.filters ?? {},
    _raw: response
  };
}

getGenerationLogs.defaults = {
  logs: [],
  count: 0
};

/**
 * Get generation log filter and sort options
 * @returns {Promise<object>} Clean response with available filter and sort options
 */
export async function getGenerationLogOptions() {
  const response = await get('/api/generation/log-options');
  
  // Only convert the main response keys, keep all option values as-is from backend
  return {
    filterOptions: response.data?.filter_options ?? getGenerationLogOptions.defaults.filterOptions,
    sortOptions: response.data?.sort_options ?? getGenerationLogOptions.defaults.sortOptions,
    _raw: response
  };
}

getGenerationLogOptions.defaults = {
  filterOptions: [],
  sortOptions: {
    fields: [],
    orders: []
  }
};