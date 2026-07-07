// Monster API Service - PERFECT ARCHITECTURE VERSION
// Co-located: HTTP calls + transformations + defaults in one place  
// 1:1 with backend routes, no separate constants needed
// Functions carry their own defaults for perfect pairing with useAsyncState

import { get, post, getWithParams } from '../core/client.js';
import {
  transformMonster,
  transformMonsters,
  transformAbility,
  transformMemories,
  transformEvolutions,
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
 * Load one monster's permanent memories (oldest first - its life in order)
 * @param {number} monsterId - Monster database ID
 * @returns {Promise<object>} Clean transformed response with memories array
 */
export async function loadMonsterMemories(monsterId) {
  const response = await get(`/api/monsters/${monsterId}/memories`);

  return {
    memories: transformMemories(response.memories ?? loadMonsterMemories.defaults.memories),
    _raw: response
  };
}
loadMonsterMemories.defaults = {
  memories: []
};

/**
 * Generate a new monster using the new monnster generation workflow
 * @returns {Promise<object>} Clean transformed response with workflowId
 */
export async function generateMonster() {

  const response = await get('/api/monsters/generate');
  
  return {
    success: response.success ?? generateMonster.defaults.success,
    workflowId: response.workflow_id ?? generateMonster.defaults.workflowId,
    _raw: response
  };
}
generateMonster.defaults = {
  success: null,
  workflowId: null,
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
 * Evolve a following monster at home base using the evolve_monster
 * workflow. The transform arrives via SSE (monster.updated +
 * monster.evolved), the ceremony narration streams (workflow.update step
 * emit_generation_id -> data.evolution_text_generation_id), and the full
 * outcome lands in workflow.completed.
 * @param {number} monsterId - The monster to evolve
 * @param {string} [guidance] - Optional whisper steering the evolved form (<=200 chars)
 * @returns {Promise<object>} Clean transformed response with workflowId
 */
export async function evolveMonster(monsterId, guidance) {

  const body = guidance && String(guidance).trim() ? { guidance: String(guidance).trim() } : {};
  const response = await post(`/api/monsters/${monsterId}/evolve`, body);

  return {
    success: response.success ?? evolveMonster.defaults.success,
    workflowId: response.workflow_id ?? evolveMonster.defaults.workflowId,
    _raw: response
  };
}
evolveMonster.defaults = {
  success: null,
  workflowId: null,
};

/**
 * Load one monster's evolution lineage (oldest first - its forms in order)
 * @param {number} monsterId - Monster database ID
 * @returns {Promise<object>} Clean transformed response with evolutions array
 */
export async function loadMonsterEvolutions(monsterId) {
  const response = await get(`/api/monsters/${monsterId}/evolutions`);

  return {
    evolutions: transformEvolutions(response.evolutions ?? loadMonsterEvolutions.defaults.evolutions),
    _raw: response
  };
}
loadMonsterEvolutions.defaults = {
  evolutions: []
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