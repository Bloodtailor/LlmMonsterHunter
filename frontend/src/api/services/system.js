// System API Service - Pure API communication for system health and status
// Handles health checks, game status, and system monitoring
// Returns raw API responses - no business logic or data transformation

import { get } from '../core/client.js';
import { API_ENDPOINTS } from '../core/config.js';

/**
 * Health check endpoint
 * Tests backend connectivity and database status
 * @returns {Promise<object>} Raw API response with health check data
 */
export async function healthCheck() {
  return await get(API_ENDPOINTS.HEALTH);
}

/**
 * Get game status information
 * Returns current game state and feature flags
 * @returns {Promise<object>} Raw API response with game status data
 */
export async function getGameStatus() {
  return await get(API_ENDPOINTS.GAME_STATUS);
}

/**
 * Test API connectivity
 * Calls both health and status endpoints to verify full API functionality
 * @returns {Promise<object>} Combined test results with both responses
 */
export async function testApiConnectivity() {
  try {
    const [healthData, statusData] = await Promise.all([
      healthCheck(),
      getGameStatus()
    ]);
    
    return {
      success: true,
      health: healthData,
      status: statusData,
      timestamp: new Date().toISOString()
    };
    
  } catch (error) {
    return {
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    };
  }
}