// Dungeon API Service - PERFECT ARCHITECTURE VERSION
// Co-located: HTTP calls + transformations + defaults in one place
// 1:1 with backend routes, no separate constants needed
// Functions carry their own defaults for perfect pairing with useAsyncState

import { get, post } from '../core/client.js';


/**
 * Enter the dungeon using the enter_dungeon workflow
 * @returns {Promise<object>} Clean transformed response with workflowId
 */
export async function enterDungeon() {

  const response = await get('/api/dungeon/enter');

  return {
    success: response.success ?? enterDungeon.defaults.success,
    workflowId: response.workflow_id ?? enterDungeon.defaults.workflowId,
    _raw: response
  };
}
enterDungeon.defaults = {
  success: null,
  workflowId: null,
};

/**
 * Take a chosen path using the choose_path workflow
 * @param {string} pathId - The id of the path to take (e.g., 'path_1')
 * @returns {Promise<object>} Clean transformed response with workflowId
 */
export async function choosePath(pathId) {

  const response = await post('/api/dungeon/choose-path', { path_id: pathId });

  return {
    success: response.success ?? choosePath.defaults.success,
    workflowId: response.workflow_id ?? choosePath.defaults.workflowId,
    _raw: response
  };
}
choosePath.defaults = {
  success: null,
  workflowId: null,
};

/**
 * Speak to the encounter monsters using the respond_to_monster workflow
 * (answer their question, keep talking, or open talks with monsters
 * spotted while exploring - the LLM decides what comes of it)
 * @param {string} message - What the party says
 * @returns {Promise<object>} Clean transformed response with workflowId
 */
export async function respondToMonster(message) {

  const response = await post('/api/dungeon/respond', { message });

  return {
    success: response.success ?? respondToMonster.defaults.success,
    workflowId: response.workflow_id ?? respondToMonster.defaults.workflowId,
    _raw: response
  };
}
respondToMonster.defaults = {
  success: null,
  workflowId: null,
};

/**
 * Attempt to sneak past the monsters using the sneak_past workflow
 * @returns {Promise<object>} Clean transformed response with workflowId
 */
export async function sneakPast() {

  const response = await post('/api/dungeon/sneak');

  return {
    success: response.success ?? sneakPast.defaults.success,
    workflowId: response.workflow_id ?? sneakPast.defaults.workflowId,
    _raw: response
  };
}
sneakPast.defaults = {
  success: null,
  workflowId: null,
};

/**
 * Spring a surprise attack using the surprise_attack workflow
 * @returns {Promise<object>} Clean transformed response with workflowId
 */
export async function surpriseAttack() {

  const response = await post('/api/dungeon/surprise-attack');

  return {
    success: response.success ?? surpriseAttack.defaults.success,
    workflowId: response.workflow_id ?? surpriseAttack.defaults.workflowId,
    _raw: response
  };
}
surpriseAttack.defaults = {
  success: null,
  workflowId: null,
};

/**
 * Set up camp in a monster-free location using the setup_camp workflow
 * @returns {Promise<object>} Clean transformed response with workflowId
 */
export async function setupCamp() {

  const response = await post('/api/dungeon/camp');

  return {
    success: response.success ?? setupCamp.defaults.success,
    workflowId: response.workflow_id ?? setupCamp.defaults.workflowId,
    _raw: response
  };
}
setupCamp.defaults = {
  success: null,
  workflowId: null,
};

/**
 * Use a party monster's ability on anything using the use_dungeon_ability
 * workflow (outside battle - the LLM decides if it does anything at all)
 * @param {object} params
 * @param {number} params.monsterId - The acting party monster
 * @param {number} params.abilityId - The ability being used
 * @param {string} params.targetType - 'path' | 'monster' | 'location' | 'custom'
 * @param {string|number} [params.targetId] - Path id or monster id (for path/monster targets)
 * @param {string} [params.targetText] - Free-text target description (for custom targets)
 * @returns {Promise<object>} Clean transformed response with workflowId
 */
export async function useDungeonAbility({ monsterId, abilityId, targetType, targetId, targetText }) {

  const response = await post('/api/dungeon/use-ability', {
    monster_id: monsterId,
    ability_id: abilityId,
    target_type: targetType,
    target_id: targetId,
    target_text: targetText
  });

  return {
    success: response.success ?? useDungeonAbility.defaults.success,
    workflowId: response.workflow_id ?? useDungeonAbility.defaults.workflowId,
    _raw: response
  };
}
useDungeonAbility.defaults = {
  success: null,
  workflowId: null,
};

/**
 * DEVELOPER ONLY: full LLM context X-ray for the debug panel
 * Returns the dungeon log, party/encounter/battle context blocks exactly
 * as the LLM prompts receive them, plus paths WITH hidden info
 * @returns {Promise<object>} The raw context payload (kept snake_case on
 *   purpose - the panel shows backend truth)
 */
export async function getDungeonDebugContext() {

  const response = await get('/api/dungeon/debug-context');

  return {
    success: response.success ?? getDungeonDebugContext.defaults.success,
    inDungeon: response.in_dungeon ?? getDungeonDebugContext.defaults.inDungeon,
    currentLocation: response.current_location ?? getDungeonDebugContext.defaults.currentLocation,
    dungeonLog: response.dungeon_log ?? getDungeonDebugContext.defaults.dungeonLog,
    party: response.party ?? getDungeonDebugContext.defaults.party,
    encounter: response.encounter ?? getDungeonDebugContext.defaults.encounter,
    pathsFull: response.paths_full ?? getDungeonDebugContext.defaults.pathsFull,
    battle: response.battle ?? getDungeonDebugContext.defaults.battle,
    _raw: response
  };
}
getDungeonDebugContext.defaults = {
  success: null,
  inDungeon: false,
  currentLocation: null,
  dungeonLog: { entries: [], clamped_text: '' },
  party: null,
  encounter: null,
  pathsFull: {},
  battle: { in_battle: false },
};

/**
 * Generate fresh paths from the current location using continue_exploring
 * @returns {Promise<object>} Clean transformed response with workflowId
 */
export async function continueExploring() {

  const response = await post('/api/dungeon/continue');

  return {
    success: response.success ?? continueExploring.defaults.success,
    workflowId: response.workflow_id ?? continueExploring.defaults.workflowId,
    _raw: response
  };
}
continueExploring.defaults = {
  success: null,
  workflowId: null,
};
