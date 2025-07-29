// Game State API Service - Pure API communication for game state management
// Handles following monsters, active party, and overall game state
// Returns raw API responses - no business logic or data transformation

import { get, post } from '../core/client.js';
import { API_ENDPOINTS } from '../core/config.js';

/**
 * Get complete game state
 * @returns {Promise<object>} Raw API response with game state data
 */
export async function getGameState() {
  return await get(API_ENDPOINTS.GAME_STATE);
}

/**
 * Reset game state to initial values
 * @returns {Promise<object>} Raw API response with reset confirmation
 */
export async function resetGameState() {
  return await post(API_ENDPOINTS.GAME_STATE_RESET);
}

// ===== FOLLOWING MONSTERS (Player Collection) =====

/**
 * Get following monsters (player's collection)
 * @returns {Promise<object>} Raw API response with following monsters data
 */
export async function getFollowingMonsters() {
  return await get(API_ENDPOINTS.FOLLOWING);
}

/**
 * Add monster to following list
 * @param {number} monsterId - ID of monster to add to following
 * @returns {Promise<object>} Raw API response with success status
 */
export async function addMonsterToFollowing(monsterId) {
  return await post(API_ENDPOINTS.FOLLOWING_ADD, { monster_id: monsterId });
}

/**
 * Remove monster from following list
 * @param {number} monsterId - ID of monster to remove from following
 * @returns {Promise<object>} Raw API response with success status
 */
export async function removeMonsterFromFollowing(monsterId) {
  return await post(API_ENDPOINTS.FOLLOWING_REMOVE, { monster_id: monsterId });
}

// ===== ACTIVE PARTY MANAGEMENT =====

/**
 * Get active party
 * @returns {Promise<object>} Raw API response with active party data
 */
export async function getActiveParty() {
  return await get(API_ENDPOINTS.PARTY);
}

/**
 * Set active party
 * @param {number[]} monsterIds - Array of monster IDs for active party (max 4)
 * @returns {Promise<object>} Raw API response with party update status
 */
export async function setActiveParty(monsterIds) {
  return await post(API_ENDPOINTS.PARTY_SET, { monster_ids: monsterIds });
}

/**
 * Check if party is ready for dungeon
 * @returns {Promise<object>} Raw API response with ready status and party info
 */
export async function isPartyReady() {
  return await get(API_ENDPOINTS.PARTY_READY);
}

/**
 * Test game state API connectivity
 * Useful for debugging and health checks
 * @returns {Promise<object>} Raw API response
 */
export async function testGameStateApi() {
  return await get(API_ENDPOINTS.GAME_STATE);
}