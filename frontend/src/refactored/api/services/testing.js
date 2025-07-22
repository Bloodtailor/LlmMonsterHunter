// Testing API Service - Pure API communication for development and debugging
// Handles backend test runner and debug utilities
// Returns raw API responses - no business logic or data transformation

import { get, post } from '../core/client.js';
import { API_ENDPOINTS } from '../core/config.js';

// ===== BACKEND TEST RUNNER =====

/**
 * Get list of available test files
 * @returns {Promise<object>} Raw API response with array of available test names
 */
export async function getAvailableTests() {
  return await get(API_ENDPOINTS.GAME_TESTER_TESTS);
}

/**
 * Run a specific test file
 * @param {string} testName - Name of the test file to run (without .py extension)
 * @returns {Promise<object>} Raw API response with test execution results
 */
export async function runTest(testName) {
  return await get(API_ENDPOINTS.GAME_TESTER_RUN(testName));
}

// ===== DEBUG UTILITIES =====

/**
 * Test complete flow (queue → LLM generation → logging → streaming)
 * @param {object} options - Test options
 * @returns {Promise<object>} Raw API response with test initiation results
 */
export async function testCompleteFlow(options = {}) {
  return await post(API_ENDPOINTS.STREAMING_TEST, options);
}

/**
 * Test testing API connectivity
 * Useful for verifying debug endpoints work
 * @returns {Promise<object>} Raw API response
 */
export async function testTestingApi() {
  return await get(API_ENDPOINTS.GAME_TESTER_TESTS);
}