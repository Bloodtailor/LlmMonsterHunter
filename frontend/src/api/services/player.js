// Player API Service - the player character's HTTP surface
// Co-located: HTTP calls + transformations + defaults in one place
// 1:1 with backend/routes/player_routes.py. The async pieces (options,
// create, portrait paint) answer { workflowId } - results arrive over
// SSE as workflowCompleted events carrying the workflow result.

import { get, post } from '../core/client.js';
import { getApiConfig } from '../core/config.js';
import { transformMonster } from '../transformers/monsters.js';

/**
 * The player character, or null when none exists yet (a 404 is a
 * normal answer here, not a failure - pre-creation moments)
 * @returns {Promise<object>} { player: monster|null }
 */
export async function getPlayer() {
  try {
    const response = await get('/api/player');
    return {
      player: response.player ? transformMonster(response.player) : getPlayer.defaults.player,
      _raw: response,
    };
  } catch (error) {
    return { player: null, _raw: null };
  }
}
getPlayer.defaults = {
  player: null,
};

/**
 * Queue option generation for one creation field
 * @param {string} field - kind|name|background|personality|wish|appearance
 * @param {object} choices - everything chosen so far (field -> text)
 * @returns {Promise<object>} { success, workflowId, error }
 */
export async function generateOptions(field, choices = {}) {
  const response = await post('/api/player/options', { field, choices });
  return {
    success: response.success ?? generateOptions.defaults.success,
    workflowId: response.workflow_id ?? generateOptions.defaults.workflowId,
    error: response.error ?? generateOptions.defaults.error,
    _raw: response,
  };
}
generateOptions.defaults = {
  success: false,
  workflowId: null,
  error: null,
};

/**
 * Queue the character finalize workflow
 * @param {object} choices - { kind, name, background, personality, wish, role, appearance }
 * @returns {Promise<object>} { success, workflowId, error }
 */
export async function createCharacter(choices) {
  const response = await post('/api/player/create', choices);
  return {
    success: response.success ?? createCharacter.defaults.success,
    workflowId: response.workflow_id ?? createCharacter.defaults.workflowId,
    error: response.error ?? createCharacter.defaults.error,
    _raw: response,
  };
}
createCharacter.defaults = {
  success: false,
  workflowId: null,
  error: null,
};

/**
 * Queue ONE portrait candidate paint (repeatable; each result is a
 * candidate path - nothing becomes THE portrait until selectPortrait)
 * @param {string} description - the portrait brief (appearance text)
 * @returns {Promise<object>} { success, workflowId, error }
 */
export async function generatePortrait(description) {
  const response = await post('/api/player/portrait/generate', { description });
  return {
    success: response.success ?? generatePortrait.defaults.success,
    workflowId: response.workflow_id ?? generatePortrait.defaults.workflowId,
    error: response.error ?? generatePortrait.defaults.error,
    _raw: response,
  };
}
generatePortrait.defaults = {
  success: false,
  workflowId: null,
  error: null,
};

/**
 * Make a painted candidate (or an upload) THE portrait
 * @param {string} imagePath - relative path from a candidate result
 * @returns {Promise<object>} { success, imagePath, player, error }
 */
export async function selectPortrait(imagePath) {
  const response = await post('/api/player/portrait/select', { image_path: imagePath });
  return {
    success: response.success ?? selectPortrait.defaults.success,
    imagePath: response.image_path ?? selectPortrait.defaults.imagePath,
    player: response.monster ? transformMonster(response.monster) : selectPortrait.defaults.player,
    error: response.error ?? selectPortrait.defaults.error,
    _raw: response,
  };
}
selectPortrait.defaults = {
  success: false,
  imagePath: null,
  player: null,
  error: null,
};

/**
 * Upload an image file as the portrait (multipart - bypasses the JSON
 * client on purpose; the browser sets the multipart boundary itself).
 * Uploads auto-select.
 * @param {File} file - png/jpg/webp, max 8MB
 * @returns {Promise<object>} { success, imagePath, player, error }
 */
export async function uploadPortrait(file) {
  const formData = new FormData();
  formData.append('image', file);

  const response = await fetch(`${getApiConfig().BASE_URL}/api/player/portrait/upload`, {
    method: 'POST',
    body: formData,
  });
  const data = await response.json();

  return {
    success: data.success ?? uploadPortrait.defaults.success,
    imagePath: data.image_path ?? uploadPortrait.defaults.imagePath,
    player: data.monster ? transformMonster(data.monster) : uploadPortrait.defaults.player,
    error: data.error ?? uploadPortrait.defaults.error,
    _raw: data,
  };
}
uploadPortrait.defaults = {
  success: false,
  imagePath: null,
  player: null,
  error: null,
};

/**
 * Display URL for any portrait candidate path (served by the existing
 * card-art route - uploads and painted candidates live in the same tree)
 * @param {string} relativePath
 * @returns {string|null}
 */
export function getPortraitUrl(relativePath) {
  if (!relativePath) return null;
  return `${getApiConfig().BASE_URL}/api/monsters/card-art/${relativePath}`;
}
