// Battle API Service - PERFECT ARCHITECTURE VERSION
// Co-located: HTTP calls + transformations + defaults in one place
// 1:1 with backend routes, no separate constants needed
// Functions carry their own defaults for perfect pairing with useAsyncState

import { get, post } from '../core/client.js';


/**
 * Submit the player's actions for this battle round (queues battle_round workflow)
 * @param {Array} actions - [{ monster_id, action: 'attack'|'ability'|'defend', ability_id?, target_id? }]
 * @returns {Promise<object>} Clean transformed response with workflowId
 */
export async function submitRound(actions) {

  const response = await post('/api/battle/round', { actions });

  return {
    success: response.success ?? submitRound.defaults.success,
    workflowId: response.workflow_id ?? submitRound.defaults.workflowId,
    _raw: response
  };
}
submitRound.defaults = {
  success: null,
  workflowId: null,
};

/**
 * Get the current public battle state
 * @returns {Promise<object>} Battle snapshot (allies/enemies with conditions, round, phase)
 */
export async function getBattleState() {

  const response = await get('/api/battle/state');

  return {
    success: response.success ?? getBattleState.defaults.success,
    battle: response.battle ?? getBattleState.defaults.battle,
    _raw: response
  };
}
getBattleState.defaults = {
  success: null,
  battle: null,
};
