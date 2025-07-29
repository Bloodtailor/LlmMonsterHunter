// API Service Layer
// Handles all communication with the Flask backend
// Provides consistent error handling and response processing

// Configuration
const API_BASE_URL = 'http://localhost:5000';
const API_TIMEOUT = 5000; // 5 seconds

/**
 * Custom error class for API-related errors
 */
class ApiError extends Error {
  constructor(message, status = null, response = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.response = response;
  }
}

/**
 * Generic API request function with error handling
 * @param {string} endpoint - API endpoint (e.g., '/api/health')
 * @param {object} options - Fetch options (method, headers, body, etc.)
 * @returns {Promise} - Promise that resolves to response data
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // Default options
  const defaultOptions = {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: API_TIMEOUT,
    ...options
  };

  try {
    // Create timeout promise
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Request timeout')), API_TIMEOUT);
    });

    // Make the fetch request
    const fetchPromise = fetch(url, defaultOptions);
    
    // Race between fetch and timeout
    const response = await Promise.race([fetchPromise, timeoutPromise]);
    
    // Check if response is ok
    if (!response.ok) {
      throw new ApiError(
        `API request failed: ${response.status} ${response.statusText}`,
        response.status,
        response
      );
    }
    
    // Parse JSON response
    const data = await response.json();
    return data;
    
  } catch (error) {
    // Handle different types of errors
    if (error instanceof ApiError) {
      throw error;
    } else if (error.message === 'Request timeout') {
      throw new ApiError('Request timed out - backend server may be slow or unresponsive');
    } else if (error.message.includes('Failed to fetch')) {
      throw new ApiError('Cannot connect to backend server - make sure it is running on localhost:5000');
    } else {
      throw new ApiError(`Unexpected error: ${error.message}`);
    }
  }
}

/**
 * Health check endpoint
 * Tests backend connectivity and database status
 * @returns {Promise<object>} Health check data
 */
export async function healthCheck() {
  return await apiRequest('/api/health');
}

/**
 * Get game status information
 * Returns current game state and feature flags
 * @returns {Promise<object>} Game status data
 */
export async function getGameStatus() {
  return await apiRequest('/api/game/status');
}


/**
 * Utility function to log API calls for debugging
 */
export function logApiCall(endpoint, data, error = null) {
  if (process.env.NODE_ENV === 'development') {
    console.log(`🔗 API Call: ${endpoint}`, {
      data,
      error,
      timestamp: new Date().toISOString()
    });
  }
}

/**
 * Test API connectivity
 * Calls both health and status endpoints to verify full API functionality
 * @returns {Promise<object>} Combined test results
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

/**
 * LLM monitoring and debugging endpoints
 */

/**
 * Get LLM status information
 * @returns {Promise<object>} LLM status data
 */
export async function getLLMStatus() {
  return await apiRequest('/api/llm/status');
}

/**
 * Get recent LLM logs for debugging
 * @param {object} options - Query options (limit, status, prompt_type)
 * @returns {Promise<object>} LLM logs data
 */
export async function getLLMLogs(options = {}) {
  const params = new URLSearchParams(options).toString();
  const endpoint = params ? `/api/llm/logs?${params}` : '/api/llm/logs';
  return await apiRequest(endpoint);
}

/**
 * Get detailed information about a specific LLM log
 * @param {number} logId - ID of the log to retrieve
 * @returns {Promise<object>} Detailed log data
 */
export async function getLLMLogDetail(logId) {
  return await apiRequest(`/api/llm/logs/${logId}`);
}

/**
 * Get LLM generation statistics
 * @returns {Promise<object>} Statistics data
 */
export async function getLLMStats() {
  return await apiRequest('/api/llm/stats');
}

/**
 * Get available LLM prompts
 * @returns {Promise<object>} Available prompts
 */
export async function getLLMPrompts() {
  return await apiRequest('/api/llm/prompts');
}

/**
 * Get current generation status
 * @returns {Promise<object>} Current generation info
 */
export async function getCurrentGeneration() {
  return await apiRequest('/api/llm/current-generation');
}