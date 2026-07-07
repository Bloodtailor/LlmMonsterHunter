// Battle API Service - PERFECT ARCHITECTURE VERSION
// Co-located: HTTP calls + transformations + defaults in one place
// 1:1 with backend routes, no separate constants needed
// Functions carry their own defaults for perfect pairing with useAsyncState

import { get, post } from '../core/client.js';

/**
 * Take a battle turn (queues battle_turn workflow)
 * @param {object|null} action - null for opening initiative, or
 *   { type: 'attack'|'ability'|'defend'|'custom'|'talk', ability_id?, target_id?, text?, info? }
 * @returns {Promise<object>} Clean transformed response with workflowId
 */
export async function takeTurn(action) {
  const response = await post('/api/battle/turn', { action });

  return {
    success: response.success ?? takeTurn.defaults.success,
    workflowId: response.workflow_id ?? takeTurn.defaults.workflowId,
    _raw: response,
  };
}
takeTurn.defaults = {
  success: null,
  workflowId: null,
};

/**
 * Reply to an enemy's battlefield talk (queues battle_turn workflow)
 * @param {string} responseText - What the party says back
 * @returns {Promise<object>} Clean transformed response with workflowId
 */
export async function respondToTalk(responseText) {
  const response = await post('/api/battle/respond', { response: responseText });

  return {
    success: response.success ?? respondToTalk.defaults.success,
    workflowId: response.workflow_id ?? respondToTalk.defaults.workflowId,
    _raw: response,
  };
}
respondToTalk.defaults = {
  success: null,
  workflowId: null,
};

/**
 * Get the current public battle state
 * @returns {Promise<object>} Battle snapshot
 */
export async function getBattleState() {
  const response = await get('/api/battle/state');

  return {
    success: response.success ?? getBattleState.defaults.success,
    battle: response.battle ?? getBattleState.defaults.battle,
    _raw: response,
  };
}
getBattleState.defaults = {
  success: null,
  battle: null,
};
