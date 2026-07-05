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
 * Answer the active riddle using the answer_riddle workflow
 * @param {string} answer - The player's typed answer
 * @returns {Promise<object>} Clean transformed response with workflowId
 */
export async function answerRiddle(answer) {

  const response = await post('/api/dungeon/answer-riddle', { answer });

  return {
    success: response.success ?? answerRiddle.defaults.success,
    workflowId: response.workflow_id ?? answerRiddle.defaults.workflowId,
    _raw: response
  };
}
answerRiddle.defaults = {
  success: null,
  workflowId: null,
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
