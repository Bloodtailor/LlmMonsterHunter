// Monster API Service - Complete API communication layer for monsters
// Handles all HTTP requests to monster-related endpoints
// Returns raw API responses - no business logic or data transformation
// Updated to match complete backend API reference

import { get, post, getWithParams } from '../core/client.js';
import { API_ENDPOINTS } from '../core/config.js';

// ===== MONSTER CRUD OPERATIONS =====

/**
 * Get a specific monster by ID
 * @param {number} monsterId - ID of the monster to retrieve
 * @returns {Promise<object>} Raw API response with monster data
 */
export async function getMonster(monsterId) {
  return await get(API_ENDPOINTS.MONSTERS_BY_ID(monsterId));
}

/**
 * Load monsters with server-side pagination, filtering, and sorting
 * @param {object} options - Query options
 * @param {number} options.limit - Number of monsters per page (1-1000, default: 50)
 * @param {number} options.offset - Offset for pagination (0+, default: 0)
 * @param {string} options.filter - Filter type ('all', 'with_art', 'without_art', default: 'all')
 * @param {string} options.sort - Sort order ('newest', 'oldest', 'name', 'species', default: 'newest')
 * @returns {Promise<object>} Raw API response with monsters array and pagination info
 */
export async function loadMonsters(options = {}) {
  const params = {};
  
  // Only include non-empty parameters
  if (options.limit !== undefined) params.limit = options.limit;
  if (options.offset !== undefined) params.offset = options.offset;
  if (options.filter && options.filter !== 'all') params.filter = options.filter;
  if (options.sort) params.sort = options.sort;
  
  return await getWithParams(API_ENDPOINTS.MONSTERS, params);
}

/**
 * Get available monster templates
 * @returns {Promise<object>} Raw API response with template definitions
 */
export async function getMonsterTemplates() {
  return await get(API_ENDPOINTS.MONSTERS_TEMPLATES);
}

/**
 * Load monster statistics
 * @param {string} filter - Filter to apply ('all', 'with_art', 'without_art', default: 'all')
 * @returns {Promise<object>} Raw API response with statistics
 */
export async function loadMonsterStats(filter = 'all') {
  const params = {};
  if (filter && filter !== 'all') params.filter = filter;
  
  return await getWithParams(API_ENDPOINTS.MONSTERS_STATS, params);
}

// ===== MONSTER GENERATION =====

/**
 * Generate a new monster
 * @param {object} options - Generation options
 * @param {string} options.prompt_name - Type of prompt to use (default: 'detailed_monster')
 * @param {boolean} options.generate_card_art - Whether to generate card art (default: true)
 * @param {boolean} options.wait_for_completion - Whether to wait for generation to complete
 * @returns {Promise<object>} Raw API response with monster data and generation stats
 */
export async function generateMonster(options = {}) {
  const requestBody = {
    prompt_name: options.prompt_name || 'detailed_monster',
    ...options
  };
  
  return await post(API_ENDPOINTS.MONSTERS_GENERATE, requestBody);
}

// ===== MONSTER ABILITIES =====

/**
 * Get all abilities for a specific monster
 * @param {number} monsterId - ID of the monster
 * @returns {Promise<object>} Raw API response with abilities array
 */
export async function getMonsterAbilities(monsterId) {
  return await get(API_ENDPOINTS.MONSTER_ABILITIES(monsterId));
}

/**
 * Generate an ability for a specific monster
 * @param {number} monsterId - ID of the monster
 * @param {object} options - Generation options
 * @param {boolean} options.wait_for_completion - Whether to wait for completion (default: true)
 * @returns {Promise<object>} Raw API response with ability data
 */
export async function generateAbility(monsterId, options = {}) {
  const requestBody = {
    wait_for_completion: options.wait_for_completion !== false, // Default to true
    ...options
  };
  
  return await post(API_ENDPOINTS.MONSTER_GENERATE_ABILITY(monsterId), requestBody);
}

// ===== MONSTER CARD ART =====

/**
 * Generate card art for a specific monster
 * @param {number} monsterId - ID of the monster
 * @param {object} options - Generation options
 * @returns {Promise<object>} Raw API response with image path and generation info
 */
export async function generateCardArt(monsterId, options = {}) {
  return await post(API_ENDPOINTS.MONSTER_GENERATE_CARD_ART(monsterId), options);
}

/**
 * Get card art metadata for a specific monster
 * @param {number} monsterId - ID of the monster
 * @returns {Promise<object>} Raw API response with card art info
 */
export async function getMonsterCardArt(monsterId) {
  return await get(API_ENDPOINTS.MONSTER_GET_CARD_ART(monsterId));
}

/**
 * Get monster card art file URL
 * Note: This returns the full URL for the card art file endpoint
 * @param {string} relativePath - Relative path from monster.card_art.relative_path
 * @returns {string} Full URL to the card art image endpoint
 */
export function getCardArtUrl(relativePath) {
  if (!relativePath) return null;
  return `http://localhost:5000${API_ENDPOINTS.MONSTER_CARD_ART_FILE(relativePath)}`;
}

// ===== UTILITY FUNCTIONS =====

/**
 * Test monsters API connectivity
 * Useful for debugging and health checks
 * @returns {Promise<object>} Raw API response
 */
export async function testMonstersApi() {
  return await get(API_ENDPOINTS.MONSTERS + '?limit=1');
}