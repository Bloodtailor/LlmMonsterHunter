// Dungeon API Service - Pure API communication for dungeon exploration
// Handles dungeon state, entry, navigation, and door choices
// Returns raw API responses - no business logic or data transformation

import { get, post } from '../core/client.js';
import { API_ENDPOINTS } from '../core/config.js';

/**
 * Get current dungeon status (quick check)
 * @returns {Promise<object>} Raw API response with in_dungeon flag and basic info
 */
export async function getDungeonStatus() {
  return await get(API_ENDPOINTS.DUNGEON_STATUS);
}

/**
 * Get detailed dungeon state
 * @returns {Promise<object>} Raw API response with full dungeon state
 */
export async function getDungeonState() {
  return await get(API_ENDPOINTS.DUNGEON_STATE);
}

/**
 * Enter dungeon with current active party
 * @returns {Promise<object>} Raw API response with entry text, location, and door choices
 */
export async function enterDungeon() {
  return await post(API_ENDPOINTS.DUNGEON_ENTER);
}

/**
 * Choose a door in the dungeon
 * @param {string} doorChoice - Door ID to choose ('location_1', 'location_2', or 'exit')
 * @returns {Promise<object>} Raw API response with event text, new location, and next doors
 */
export async function chooseDoor(doorChoice) {
  return await post(API_ENDPOINTS.DUNGEON_CHOOSE_DOOR, { door_choice: doorChoice });
}

/**
 * Test dungeon API connectivity
 * Useful for debugging and health checks
 * @returns {Promise<object>} Raw API response
 */
export async function testDungeonApi() {
  return await get(API_ENDPOINTS.DUNGEON_STATUS);
}