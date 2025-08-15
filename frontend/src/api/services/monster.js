// Monster API Service - PERFECT ARCHITECTURE VERSION
// Co-located: HTTP calls + transformations + defaults in one place  
// 1:1 with backend routes, no separate constants needed
// Functions carry their own defaults for perfect pairing with useAsyncState

import { get, post, getWithParams } from '../core/client.js';
import {
  transformMonster,
  transformMonsters,
  transformAbility,
} from '../transformers/monsters.js';

// ===== MONSTER COLLECTION =====

/**
 * Load monsters with server-side pagination, filtering, and sorting
 * @param {object} options - Query options
 * @param {number} options.limit - Number of monsters per page (1-1000, default: 50)
 * @param {number} options.offset - Offset for pagination (0+, default: 0)
 * @param {string} options.filter - Filter type ('all', 'with_art', 'without_art', default: 'all')
 * @param {string} options.sort - Sort order ('newest', 'oldest', 'name', 'species', default: 'newest')
 * @returns {Promise<object>} Clean transformed response with monsters array and pagination info
 */
export async function loadMonsters(options = {}) {
  const params = {};
  
  // Only include non-empty parameters
  if (options.limit !== undefined) params.limit = options.limit;
  if (options.offset !== undefined) params.offset = options.offset;
  if (options.filter && options.filter !== 'all') params.filter = options.filter;
  if (options.sort) params.sort = options.sort;
  
  const response = await getWithParams('/api/monsters', params);
  
  return {
    monsters: transformMonsters(response.monsters ?? loadMonsters.defaults.monsters),
    total: response.total ?? loadMonsters.defaults.total,
    count: response.count ?? loadMonsters.defaults.count,
    limit: response.limit ?? loadMonsters.defaults.limit,
    offset: response.offset ?? loadMonsters.defaults.offset,
    _raw: response // Raw response for debugging
  };
}

// Defaults attached to function - perfect pairing!
loadMonsters.defaults = {
  monsters: [],
  total: 0,
  count: 0,
  limit: 50,
  offset: 0
};


/**
 * Generate a new monster using the new monnster generation workflow
 * @returns {Promise<object>} Clean transformed response with workflowId
 */
export async function generateMonsterWithWorkflow() {

  const response = await get('/api/monsters/generate-workflow');
  
  return {
    success: response.success ?? generateMonsterWithWorkflow.defaults.success,
    workflowId: response.workflow_id ?? generateMonsterWithWorkflow.defaults.workflowId,
  };
}
generateMonsterWithWorkflow.defaults = {
  success: null,
  workflowId: null,
};

/**
 * Generate a new monster
 * @param {object} options - Generation options
 * @param {string} options.prompt_name - Type of prompt to use (default: 'detailed_monster')
 * @param {boolean} options.generate_card_art - Whether to generate card art (default: true)
 * @param {boolean} options.wait_for_completion - Whether to wait for generation to complete
 * @returns {Promise<object>} Clean transformed response with monster data and generation stats
 */
export async function generateMonster(options = {}) {
  const requestBody = {
    prompt_name: options.prompt_name || 'detailed_monster',
    ...options
  };
  
  const response = await post('/api/monsters/generate', requestBody);
  
  return {
    success: response.success ?? generateMonster.defaults.success,
    monster: response.monster ? transformMonster(response.monster) : generateMonster.defaults.monster,
    requestId: response.request_id ?? generateMonster.defaults.requestId,
    logId: response.log_id ?? generateMonster.defaults.logId,
    error: response.error ?? generateMonster.defaults.error,
    _raw: response
  };
}

generateMonster.defaults = {
  success: false,
  monster: null,
  requestId: null,
  logId: null,
  error: null
};

/**
 * Generate an ability for a specific monster
 * @param {number} monsterId - ID of the monster
 * @param {object} options - Generation options
 * @param {boolean} options.wait_for_completion - Whether to wait for completion (default: true)
 * @returns {Promise<object>} Clean transformed response with ability data
 */
export async function generateAbility(monsterId) {

  
  const response = await post(`/api/monsters/${monsterId}/abilities`);
  
  return {
    success: response.success ?? generateAbility.defaults.success,
    ability: response.ability ? transformAbility(response.ability) : generateAbility.defaults.ability,
    requestId: response.request_id ?? generateAbility.defaults.requestId,
    logId: response.log_id ?? generateAbility.defaults.logId,
    error: response.error ?? generateAbility.defaults.error,
    _raw: response
  };
}

generateAbility.defaults = {
  success: false,
  ability: null,
  requestId: null,
  logId: null,
  error: null
};

/**
 * Get monster card art file URL
 * Note: This returns the full URL for the card art file endpoint
 * @param {string} relativePath - Relative path from monster.card_art.relative_path
 * @returns {string} Full URL to the card art image endpoint
 */
export function getCardArtUrl(relativePath) {
  if (!relativePath) return null;
  return `http://localhost:5000/api/monsters/card-art/file/${relativePath}`;
}