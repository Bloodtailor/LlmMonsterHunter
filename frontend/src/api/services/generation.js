// Generation API Service - PERFECT ARCHITECTURE VERSION
// Co-located: HTTP calls + transformations + defaults in one place  
// 1:1 with backend routes, no separate constants needed
// Functions carry their own defaults for perfect pairing with useAsyncState

import { get, post, getWithParams } from '../core/client.js';
import { transformGenerationLogs } from '../transformers/generation.js';

// ===== GENERATION LOGS (UNIFIED SYSTEM) =====

/**
 * Get generation logs with filtering and pagination
 * @param {object} options - Query options
 * @param {number} options.limit - Number of logs to return (1-100, default: 20)
 * @param {number} options.offset - Offset for pagination (0+, default: 0)
 * @param {string} options.type - Filter by type ('llm', 'image')
 * @param {string} options.status - Filter by status ('pending', 'generating', 'completed', 'failed')
 * @param {string} options.promptType - Filter by prompt type
 * @param {string} options.promptName - Filter by prompt name
 * @param {string} options.priority - Filter by priority
 * @param {string} options.startTime - Filter by start time
 * @param {string} options.sortBy - Comma-separated fields to sort by
 * @param {string} options.sortOrder - Sort order ('asc' or 'desc')
 * @returns {Promise<object>} Clean transformed response with generation logs
 */
export async function getGenerationLogs(options = {}) {
  const params = {};
  
  // Only include non-empty parameters
  if (options.limit !== undefined) params.limit = options.limit;
  if (options.offset !== undefined) params.offset = options.offset;
  if (options.type) params.type = options.type;
  if (options.status) params.status = options.status;
  if (options.promptType) params.prompt_type = options.promptType;
  if (options.promptName) params.prompt_name = options.promptName;
  if (options.priority) params.priority = options.priority;
  if (options.startTime) params.start_time = options.startTime;
  if (options.sortBy) params.sort_by = options.sortBy;
  if (options.sortOrder) params.sort_order = options.sortOrder;
  
  const response = await getWithParams('/api/generation/logs', params);
  
  return {
    logs: transformGenerationLogs(response.data?.logs ?? getGenerationLogs.defaults.logs),
    count: response.data?.count ?? getGenerationLogs.defaults.count,
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
  
  return {
    filterOptions: response.data?.filter_options ?? getGenerationLogOptions.defaults.filterOptions,
    sortOptions: response.data?.sort_options ?? getGenerationLogOptions.defaults.sortOptions,
    _raw: response
  };
}

getGenerationLogOptions.defaults = {
  filterOptions: {
    types: [],
    statuses: [],
    promptTypes: [],
    promptNames: [],
    priorities: []
  },
  sortOptions: {
    fields: [],
    orders: []
  }
};
