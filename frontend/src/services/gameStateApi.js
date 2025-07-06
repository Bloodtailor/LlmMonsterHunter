// Game State API Service
// Handles all game state management API calls
// Provides clean interface for following monsters, party management, and game state

const API_BASE_URL = 'http://localhost:5000/api';

/**
 * Generic API request helper with error handling
 * @param {string} endpoint - API endpoint (e.g., '/game-state')
 * @param {object} options - Fetch options (method, body, etc.)
 * @returns {Promise<object>} - API response data
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultOptions = {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    ...options
  };

  try {
    const response = await fetch(url, defaultOptions);
    const data = await response.json();
    
    // Log API calls in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`🔗 API ${defaultOptions.method} ${endpoint}:`, data);
    }
    
    return data;
  } catch (error) {
    console.error(`❌ API Error ${defaultOptions.method} ${endpoint}:`, error);
    return {
      success: false,
      error: `Network error: ${error.message}`
    };
  }
}

/**
 * Get complete game state
 * @returns {Promise<object>} Game state with following monsters, party, and dungeon status
 */
export async function getGameState() {
  return await apiRequest('/game-state');
}

/**
 * Reset game state to initial values
 * @returns {Promise<object>} Reset confirmation and new game state
 */
export async function resetGameState() {
  return await apiRequest('/game-state/reset', { method: 'POST' });
}

/**
 * Get following monsters (player's collection)
 * @returns {Promise<object>} Following monsters with IDs, count, and full details
 */
export async function getFollowingMonsters() {
  return await apiRequest('/game-state/following');
}

/**
 * Add monster to following list
 * @param {number} monsterId - ID of monster to add to following
 * @returns {Promise<object>} Success status and updated following count
 */
export async function addMonsterToFollowing(monsterId) {
  return await apiRequest('/game-state/following/add', {
    method: 'POST',
    body: JSON.stringify({ monster_id: monsterId })
  });
}

/**
 * Remove monster from following list
 * @param {number} monsterId - ID of monster to remove from following
 * @returns {Promise<object>} Success status and updated counts
 */
export async function removeMonsterFromFollowing(monsterId) {
  return await apiRequest('/game-state/following/remove', {
    method: 'POST',
    body: JSON.stringify({ monster_id: monsterId })
  });
}

/**
 * Get active party
 * @returns {Promise<object>} Active party with IDs, count, and full details
 */
export async function getActiveParty() {
  return await apiRequest('/game-state/party');
}

/**
 * Set active party
 * @param {number[]} monsterIds - Array of monster IDs for active party (max 4)
 * @returns {Promise<object>} Success status and active party details
 */
export async function setActiveParty(monsterIds) {
  return await apiRequest('/game-state/party/set', {
    method: 'POST',
    body: JSON.stringify({ monster_ids: monsterIds })
  });
}

/**
 * Check if party is ready for dungeon
 * @returns {Promise<object>} Ready status, party summary, and message
 */
export async function isPartyReady() {
  return await apiRequest('/game-state/party/ready');
}

/**
 * Utility function to check if game state API response is successful
 * @param {object} response - API response object
 * @returns {boolean} True if successful, false otherwise
 */
export function isSuccessfulResponse(response) {
  return response && response.success === true;
}

/**
 * Utility function to extract error message from API response
 * @param {object} response - API response object
 * @returns {string} Error message or default message
 */
export function getErrorMessage(response) {
  if (!response) return 'Network error occurred';
  return response.error || response.message || 'Unknown error occurred';
}