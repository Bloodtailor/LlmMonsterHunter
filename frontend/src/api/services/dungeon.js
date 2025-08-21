// Dungeon API Service - PERFECT ARCHITECTURE VERSION
// Co-located: HTTP calls + transformations + defaults in one place  
// 1:1 with backend routes, no separate constants needed
// Functions carry their own defaults for perfect pairing with useAsyncState

import { get } from '../core/client.js';


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

