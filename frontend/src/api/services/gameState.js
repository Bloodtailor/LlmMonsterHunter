// Game State API Service - PERFECT ARCHITECTURE VERSION
// Co-located: HTTP calls + transformations + defaults in one place
// 1:1 with backend routes, no separate constants needed
// Functions carry their own defaults for perfect pairing with useAsyncState

import { get, post } from '../core/client.js';
import { transformMonsters } from '../transformers/monsters.js';

// ===== GAME STATE (the title screen's save summary) =====

/**
 * High-level save state: has the guided opening ever been finished,
 * and what the world holds so far (drives the title screen)
 * @returns {Promise<object>} Clean transformed response
 */
export async function getGameState() {
  const response = await get('/api/game-state');

  return {
    success: response.success ?? getGameState.defaults.success,
    firstRunComplete: response.first_run_complete ?? getGameState.defaults.firstRunComplete,
    hasWorldData: response.has_world_data ?? getGameState.defaults.hasWorldData,
    hasPlayer: response.has_player ?? getGameState.defaults.hasPlayer,
    playerMonsterId: response.player_monster_id ?? getGameState.defaults.playerMonsterId,
    followingCount: response.following_count ?? getGameState.defaults.followingCount,
    partyCount: response.party_count ?? getGameState.defaults.partyCount,
    inDungeon: response.in_dungeon ?? getGameState.defaults.inDungeon,
    _raw: response,
  };
}
getGameState.defaults = {
  success: null,
  firstRunComplete: false,
  hasWorldData: false,
  hasPlayer: false,
  playerMonsterId: null,
  followingCount: 0,
  partyCount: 0,
  inDungeon: false,
};

/**
 * Erase the world so a new story can begin (the New Game promise).
 * The caller confirms with the player FIRST - this call is the point
 * of no return. Fails while a workflow is still queued or running.
 * @returns {Promise<object>} Clean response with erase status
 */
export async function startNewGame() {
  const response = await post('/api/game-state/new-game', {});

  return {
    success: response.success ?? startNewGame.defaults.success,
    message: response.message ?? startNewGame.defaults.message,
    error: response.error ?? startNewGame.defaults.error,
    _raw: response,
  };
}

startNewGame.defaults = {
  success: false,
  message: null,
  error: null,
};

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
    followingMonsters: transformMonsters(
      response.following_monsters?.details ?? getFollowingMonsters.defaults.followingMonsters,
    ),
    _raw: response,
  };
}

getFollowingMonsters.defaults = {
  ids: [],
  count: 0,
  followingMonsters: [],
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
    partyMonsters: transformMonsters(
      response.active_party?.details ?? getActiveParty.defaults.partyMonsters,
    ),
    _raw: response,
  };
}

getActiveParty.defaults = {
  ids: [],
  count: 0,
  partyMonsters: [],
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
    _raw: response,
  };
}

setActiveParty.defaults = {
  success: false,
  message: null,
  partyCount: 0,
  partyIds: [],
};
