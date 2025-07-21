// API Interceptors - Request/Response processing and error handling
// Centralizes logging, error normalization, and cross-cutting concerns

import { getApiConfig } from './config.js';

/**
 * Custom API Error class for consistent error handling
 */
export class ApiError extends Error {
  constructor(message, status = null, response = null, endpoint = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.response = response;
    this.endpoint = endpoint;
    this.timestamp = new Date().toISOString();
  }
}

/**
 * Process request before sending - add headers, logging, etc.
 * @param {string} url - Request URL
 * @param {object} options - Fetch options
 * @returns {object} Processed options
 */
export function processRequest(url, options = {}) {
  const config = getApiConfig();
  
  // Add default headers
  const headers = {
    ...config.DEFAULT_HEADERS,
    ...options.headers
  };
  
  // Add timestamp for request tracking
  const processedOptions = {
    ...options,
    headers
  };
  
  // Log request in development
  if (config.LOG_REQUESTS) {
    console.log(`🔗 API Request: ${options.method || 'GET'} ${url}`, {
      options: processedOptions,
      timestamp: new Date().toISOString()
    });
  }
  
  return processedOptions;
}

/**
 * Process response after receiving - parse, log, handle errors
 * @param {Response} response - Fetch response object
 * @param {string} endpoint - Original endpoint for error context
 * @returns {Promise<any>} Parsed response data
 */
export async function processResponse(response, endpoint = 'unknown') {
  const config = getApiConfig();
  
  try {
    // Check if response is ok
    if (!response.ok) {
      throw new ApiError(
        `API request failed: ${response.status} ${response.statusText}`,
        response.status,
        response,
        endpoint
      );
    }
    
    // Parse JSON response
    const data = await response.json();
    
    // Log successful response in development
    if (config.LOG_RESPONSES) {
      console.log(`✅ API Response: ${endpoint}`, {
        status: response.status,
        data,
        timestamp: new Date().toISOString()
      });
    }
    
    return data;
    
  } catch (error) {
    // If it's already an ApiError, just re-throw
    if (error instanceof ApiError) {
      throw error;
    }
    
    // Handle JSON parsing errors
    if (error.name === 'SyntaxError') {
      throw new ApiError(
        `Invalid JSON response from server`,
        response.status,
        response,
        endpoint
      );
    }
    
    // Handle other parsing errors
    throw new ApiError(
      `Response processing error: ${error.message}`,
      response.status,
      response,
      endpoint
    );
  }
}

/**
 * Process and normalize errors for consistent error handling
 * @param {Error} error - Original error
 * @param {string} endpoint - Endpoint where error occurred
 * @returns {ApiError} Normalized API error
 */
export function processError(error, endpoint = 'unknown') {
  // If it's already an ApiError, return as-is
  if (error instanceof ApiError) {
    return error;
  }
  
  // Handle specific error types
  if (error.message === 'Request timeout') {
    return new ApiError(
      'Request timed out - backend server may be slow or unresponsive',
      null,
      null,
      endpoint
    );
  }
  
  if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
    return new ApiError(
      'Cannot connect to backend server - make sure it is running on localhost:5000',
      null,
      null,
      endpoint
    );
  }
  
  if (error.name === 'AbortError') {
    return new ApiError(
      'Request was cancelled',
      null,
      null,
      endpoint
    );
  }
  
  // Generic error fallback
  return new ApiError(
    `Unexpected error: ${error.message}`,
    null,
    null,
    endpoint
  );
}

/**
 * Log API call for debugging (replaces the old logApiCall function)
 * @param {string} endpoint - API endpoint
 * @param {any} data - Response data
 * @param {Error|null} error - Error if call failed
 */
export function logApiCall(endpoint, data = null, error = null) {
  const config = getApiConfig();
  
  if (config.ENABLE_LOGGING) {
    const logData = {
      endpoint,
      timestamp: new Date().toISOString(),
      success: !error
    };
    
    if (data) {
      logData.data = data;
    }
    
    if (error) {
      logData.error = {
        message: error.message,
        status: error.status,
        endpoint: error.endpoint
      };
      console.error(`❌ API Call Failed: ${endpoint}`, logData);
    } else {
      console.log(`✅ API Call Success: ${endpoint}`, logData);
    }
  }
}