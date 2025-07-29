// API Client - Core HTTP client that replaces all scattered apiRequest functions
// Provides consistent, robust API communication with centralized error handling

import { API_CONFIG, getApiConfig } from './config.js';
import { 
  processRequest, 
  processResponse, 
  processError, 
  logApiCall,
  ApiError 
} from './interceptors.js';

/**
 * Core API client - handles all HTTP requests with consistent error handling
 * @param {string} endpoint - API endpoint (e.g., '/api/monsters')
 * @param {object} options - Request options (method, body, headers, etc.)
 * @returns {Promise<any>} - Promise that resolves to response data
 */
export async function apiClient(endpoint, options = {}) {
  const config = getApiConfig();
  
  // Build full URL
  const url = `${config.BASE_URL}${endpoint}`;
  
  // Process request (add headers, logging, etc.)
  const processedOptions = processRequest(url, {
    method: 'GET',
    timeout: config.DEFAULT_TIMEOUT,
    ...options
  });

  try {
    // Create timeout promise
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(
        () => reject(new Error('Request timeout')), 
        processedOptions.timeout
      );
    });

    // Make the fetch request
    const fetchPromise = fetch(url, processedOptions);
    
    // Race between fetch and timeout
    const response = await Promise.race([fetchPromise, timeoutPromise]);
    
    // Process response (parse JSON, handle errors, log)
    const data = await processResponse(response, endpoint);
    
    // Log successful API call
    logApiCall(endpoint, data);
    
    return data;
    
  } catch (error) {
    // Process and normalize the error
    const processedError = processError(error, endpoint);
    
    // Log failed API call
    logApiCall(endpoint, null, processedError);
    
    // Re-throw the processed error
    throw processedError;
  }
}

/**
 * HTTP Method Helpers - Convenience functions for common HTTP methods
 */

/**
 * GET request helper
 * @param {string} endpoint - API endpoint
 * @param {object} options - Additional options
 * @returns {Promise<any>} Response data
 */
export function get(endpoint, options = {}) {
  return apiClient(endpoint, {
    method: 'GET',
    ...options
  });
}

/**
 * POST request helper
 * @param {string} endpoint - API endpoint
 * @param {any} data - Request body data
 * @param {object} options - Additional options
 * @returns {Promise<any>} Response data
 */
export function post(endpoint, data = null, options = {}) {
  const requestOptions = {
    method: 'POST',
    ...options
  };
  
  // Add body if data provided
  if (data !== null) {
    requestOptions.body = JSON.stringify(data);
  }
  
  return apiClient(endpoint, requestOptions);
}

/**
 * PUT request helper
 * @param {string} endpoint - API endpoint
 * @param {any} data - Request body data
 * @param {object} options - Additional options
 * @returns {Promise<any>} Response data
 */
export function put(endpoint, data = null, options = {}) {
  const requestOptions = {
    method: 'PUT',
    ...options
  };
  
  // Add body if data provided
  if (data !== null) {
    requestOptions.body = JSON.stringify(data);
  }
  
  return apiClient(endpoint, requestOptions);
}

/**
 * DELETE request helper
 * @param {string} endpoint - API endpoint
 * @param {object} options - Additional options
 * @returns {Promise<any>} Response data
 */
export function deleteRequest(endpoint, options = {}) {
  return apiClient(endpoint, {
    method: 'DELETE',
    ...options
  });
}

/**
 * Utility function to build query parameters for GET requests
 * @param {object} params - Query parameters object
 * @returns {string} Query string
 */
export function buildQueryString(params = {}) {
  const searchParams = new URLSearchParams();
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      searchParams.append(key, value.toString());
    }
  });
  
  const queryString = searchParams.toString();
  return queryString ? `?${queryString}` : '';
}

/**
 * GET request with query parameters helper
 * @param {string} endpoint - API endpoint
 * @param {object} params - Query parameters
 * @param {object} options - Additional options
 * @returns {Promise<any>} Response data
 */
export function getWithParams(endpoint, params = {}, options = {}) {
  const queryString = buildQueryString(params);
  return get(`${endpoint}${queryString}`, options);
}

// Export the ApiError class for use in components
export { ApiError };