// Chat API Service - PERFECT ARCHITECTURE VERSION
// Co-located: HTTP calls + transformations + defaults in one place
// 1:1 with backend routes (backend/routes/chat_routes.py)
// Home-base conversations with following monsters: send a message
// (async workflow - the reply streams over SSE) and read the thread

import { get, post } from '../core/client.js';

/**
 * Speak to a following monster at home base using the chat_with_monster
 * workflow. The reply streams via SSE (workflow.update step
 * emit_generation_id -> data.chat_text_generation_id) and the final
 * exchange arrives in workflow.completed.
 * @param {number} monsterId - The monster to talk to
 * @param {string} message - What the adventurer says
 * @returns {Promise<object>} Clean transformed response with workflowId
 */
export async function sendChatMessage(monsterId, message) {
  const response = await post(`/api/chat/${monsterId}/message`, { message });

  return {
    success: response.success ?? sendChatMessage.defaults.success,
    workflowId: response.workflow_id ?? sendChatMessage.defaults.workflowId,
    _raw: response,
  };
}
sendChatMessage.defaults = {
  success: null,
  workflowId: null,
};

/**
 * One page of a monster's chat thread (synchronous read).
 * Pages walk backward from the newest message - pass beforeId (the
 * oldest loaded message id) to fetch the previous page.
 * @param {number} monsterId - The monster whose thread to read
 * @param {object} [options]
 * @param {number} [options.limit] - Messages per page (backend default 50)
 * @param {number} [options.beforeId] - Only messages older than this id
 * @returns {Promise<object>} Clean transformed response with messages
 */
export async function getChatHistory(monsterId, { limit, beforeId } = {}) {
  const params = new URLSearchParams();
  if (limit) params.set('limit', limit);
  if (beforeId) params.set('before_id', beforeId);
  const query = params.toString();

  const response = await get(`/api/chat/${monsterId}/history${query ? `?${query}` : ''}`);

  return {
    success: response.success ?? getChatHistory.defaults.success,
    monsterId: response.monster_id ?? getChatHistory.defaults.monsterId,
    monsterName: response.monster_name ?? getChatHistory.defaults.monsterName,
    messages: (response.messages ?? getChatHistory.defaults.messages).map((message) => ({
      id: message.id,
      role: message.role,
      text: message.text,
      createdAt: message.created_at ? new Date(message.created_at) : null,
    })),
    hasMore: response.has_more ?? getChatHistory.defaults.hasMore,
    total: response.total ?? getChatHistory.defaults.total,
    _raw: response,
  };
}
getChatHistory.defaults = {
  success: null,
  monsterId: null,
  monsterName: null,
  messages: [],
  hasMore: false,
  total: 0,
};
