// Game Tester API Service - Following established patterns
// Co-located: HTTP calls + defaults in one place  
// 1:1 with backend routes, functions carry their own defaults for perfect pairing with useAsyncState

import { get } from '../core/client.js';

// ===== TEST MANAGEMENT =====

/**
 * Get list of available test files
 * @returns {Promise<object>} Clean transformed response with test file names array
 */
export async function getTestFiles() {
  const response = await get('/api/game_tester/tests');
  
  // Backend returns array directly, so we normalize it to an object
  const testFiles = Array.isArray(response) ? response : getTestFiles.defaults.testFiles;
  
  return {
    testFiles: testFiles ?? getTestFiles.defaults.testFiles,
    _raw: response // Raw response for debugging
  };
}

// Defaults attached to function - perfect pairing with useAsyncState!
getTestFiles.defaults = {
  testFiles: []
};

/**
 * Run a specific test file and capture its output
 * @param {string} testName - Name of the test file to run (without .py extension)
 * @returns {Promise<object>} Clean transformed response with test results and output
 */
export async function runTest(testName) {
  if (!testName || typeof testName !== 'string') {
    throw new Error('Test name is required and must be a string');
  }
  
  const response = await get(`/api/game_tester/run/${testName}`);
  
  return {
    success: response.success ?? runTest.defaults.success,
    testName: response.test_name ?? runTest.defaults.testName,
    output: response.output ?? runTest.defaults.output,
    message: response.message ?? runTest.defaults.message,
    error: response.error ?? runTest.defaults.error,
    traceback: response.traceback ?? runTest.defaults.traceback,
    _raw: response // Raw response for debugging
  };
}

runTest.defaults = {
  success: null,
  testName: '',
  output: '',
  message: '',
  error: null,
  traceback: null
};
