// Game State API Service - PERFECT ARCHITECTURE VERSION
// Co-located: HTTP calls + transformations + defaults in one place
// 1:1 with backend routes, no separate constants needed
// Functions carry their own defaults for perfect pairing with useAsyncState

import { get, post } from '../core/client.js';
import { transformMonsters } from '../transformers/monsters.js';

// ===== FOLLOWING MONSTERS (Player Collection) =====

/**
 * Get following monsters (player's collection)
 * @returns {Promise<object>} Clean transformed response with following monsters data
 */
export async function getFollowingMonsters() {
  const response = await get('/api/game-state/following');
  
  return {
    ids: response.following_monsters?.ids ?? getFollowingMonsters.defaults.ids,
    count: response.following_monsters?.count ?? getFollowingMonsters.defaults.count,
    followingMonsters: transformMonsters(response.following_monsters?.details ?? getFollowingMonsters.defaults.followingMonsters),
    _raw: response
  };
}

getFollowingMonsters.defaults = {
  ids: [],
  count: 0,
  followingMonsters: []
};

// ===== ACTIVE PARTY MANAGEMENT =====

/**
 * Get active party
 * @returns {Promise<object>} Clean transformed response with active party data
 */
export async function getActiveParty() {
  const response = await get('/api/game-state/party');
  
  return {
    ids: response.active_party?.ids ?? getActiveParty.defaults.ids,
    count: response.active_party?.count ?? getActiveParty.defaults.count,
    partyMonsters: transformMonsters(response.active_party?.details ?? getActiveParty.defaults.partyMonsters),
    _raw: response
  };
}

getActiveParty.defaults = {
  ids: [],
  count: 0,
  partyMonsters: []
};

/**
 * Set active party
 * @param {number[]} monsterIds - Array of monster IDs for active party (max 4)
 * @returns {Promise<object>} Clean response with party update status
 */
export async function setActiveParty(monsterIds) {
  const response = await post('/api/game-state/party/set', { monster_ids: monsterIds });
  
  return {
    success: response.success ?? setActiveParty.defaults.success,
    message: response.message ?? setActiveParty.defaults.message,
    partyCount: response.active_party?.count ?? setActiveParty.defaults.partyCount,
    partyIds: response.active_party?.ids ?? setActiveParty.defaults.partyIds,
    _raw: response
  };
}

setActiveParty.defaults = {
  success: false,
  message: null,
  partyCount: 0,
  partyIds: []
};