// Dungeon API Service
// Handles all dungeon-related API calls
// Provides interface for entering dungeons, choosing doors, and tracking dungeon state

const API_BASE_URL = 'http://localhost:5000/api';

/**
 * Generic API request helper with error handling
 * @param {string} endpoint - API endpoint (e.g., '/dungeon/enter')
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
      console.log(`🏰 Dungeon API ${defaultOptions.method} ${endpoint}:`, data);
    }
    
    return data;
  } catch (error) {
    console.error(`❌ Dungeon API Error ${defaultOptions.method} ${endpoint}:`, error);
    return {
      success: false,
      error: `Network error: ${error.message}`
    };
  }
}

/**
 * Get current dungeon status (quick check)
 * @returns {Promise<object>} Dungeon status with in_dungeon flag and basic info
 */
export async function getDungeonStatus() {
  return await apiRequest('/dungeon/status');
}

/**
 * Get detailed dungeon state
 * @returns {Promise<object>} Full dungeon state with location, doors, and party info
 */
export async function getDungeonState() {
  return await apiRequest('/dungeon/state');
}

/**
 * Enter dungeon with current active party
 * @returns {Promise<object>} Entry text, initial location, and door choices
 */
export async function enterDungeon() {
  return await apiRequest('/dungeon/enter', { method: 'POST' });
}

/**
 * Choose a door in the dungeon
 * @param {string} doorChoice - Door ID to choose ('location_1', 'location_2', or 'exit')
 * @returns {Promise<object>} Event text, new location (if applicable), and next doors
 */
export async function chooseDoor(doorChoice) {
  return await apiRequest('/dungeon/choose-door', {
    method: 'POST',
    body: JSON.stringify({ door_choice: doorChoice })
  });
}

/**
 * Utility function to check if currently in dungeon
 * @param {object} dungeonResponse - Response from getDungeonStatus or getDungeonState
 * @returns {boolean} True if in dungeon, false otherwise
 */
export function isInDungeon(dungeonResponse) {
  return dungeonResponse && dungeonResponse.success && dungeonResponse.in_dungeon === true;
}

/**
 * Utility function to extract door choices from dungeon response
 * @param {object} dungeonResponse - Response from enterDungeon or chooseDoor
 * @returns {array} Array of door objects or empty array
 */
export function getDoorChoices(dungeonResponse) {
  if (!dungeonResponse || !dungeonResponse.success) return [];
  return dungeonResponse.doors || dungeonResponse.new_doors || [];
}

/**
 * Utility function to check if door choice resulted in dungeon exit
 * @param {object} doorResponse - Response from chooseDoor
 * @returns {boolean} True if player exited dungeon, false otherwise
 */
export function isExitResponse(doorResponse) {
  return doorResponse && 
         doorResponse.success && 
         (doorResponse.dungeon_completed === true || doorResponse.in_dungeon === false);
}