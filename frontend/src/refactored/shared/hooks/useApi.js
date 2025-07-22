// useApi Hook - API calls + React lifecycle integration
// Builds on useAsyncState to handle common API calling patterns with lifecycle management

import { useEffect, useCallback, useRef } from 'react';
import { useAsyncState } from './useAsyncState.js';

/**
 * Hook for API calls with automatic lifecycle management
 * @param {Function} apiFunction - Function that returns a Promise (API call)
 * @param {object} options - Configuration options
 * @param {boolean} options.immediate - Call API on mount (default: true)
 * @param {Array} options.deps - Dependencies array to watch for changes
 * @param {Function} options.transform - Optional data transformation function
 * @param {boolean} options.retryOnError - Enable retry functionality (default: false)
 * @returns {object} API state and control functions
 */
export function useApi(apiFunction, options = {}) {
  const {
    immediate = true,
    deps = [],
    transform = null,
    retryOnError = false
  } = options;

  // Use our pure useAsyncState for state management
  const asyncState = useAsyncState();
  
  // Keep track of the current API function to avoid stale closures
  const apiFunctionRef = useRef(apiFunction);
  apiFunctionRef.current = apiFunction;

  /**
   * Execute the API call with automatic state management
   */
  const executeApiCall = useCallback(async (...args) => {
    try {
      const result = await asyncState.execute(apiFunctionRef.current, ...args);
      
      // Apply transformation if provided
      if (transform) {
        const transformedData = transform(result);
        asyncState.setSuccess(transformedData);
        return transformedData;
      }
      
      return result;
    } catch (error) {
      // Error is already set by asyncState.execute
      throw error;
    }
  }, [asyncState, transform]);

  /**
   * Retry the last API call (useful for error recovery)
   */
  const retry = useCallback(() => {
    return executeApiCall();
  }, [executeApiCall]);

  /**
   * Refetch with same parameters (alias for retry, more semantic)
   */
  const refetch = useCallback(() => {
    return executeApiCall();
  }, [executeApiCall]);

  // Auto-execute on mount and when dependencies change
  useEffect(() => {
    if (immediate) {
      executeApiCall();
    }
  }, [immediate, executeApiCall, ...deps]);

  // Return enhanced state with API-specific functions
  return {
    // All useAsyncState values and flags
    ...asyncState,
    
    // API-specific functions
    execute: executeApiCall,
    retry: retryOnError ? retry : undefined,
    refetch,
    
    // Convenience flags
    canRetry: retryOnError && asyncState.isError
  };
}

/**
 * Hook for manual API calls (immediate: false by default)
 * Convenience wrapper for common "button click" scenarios
 * @param {Function} apiFunction - Function that returns a Promise
 * @param {object} options - Configuration options (same as useApi)
 * @returns {object} API state and control functions
 */
export function useApiMutation(apiFunction, options = {}) {
  return useApi(apiFunction, {
    immediate: false,
    ...options
  });
}

/**
 * Hook for API calls with parameters that change over time
 * @param {Function} apiFunction - Function that returns a Promise
 * @param {Array} params - Parameters to pass to the API function
 * @param {object} options - Configuration options
 * @returns {object} API state and control functions
 */
export function useApiWithParams(apiFunction, params = [], options = {}) {
  const { deps = [], ...restOptions } = options;
  
  // Create a wrapper function that applies the parameters
  const wrappedApiFunction = useCallback(() => {
    return apiFunction(...params);
  }, [...params]);
  
  return useApi(wrappedApiFunction, {
    ...restOptions,
    deps: [...params, ...deps]
  });
}