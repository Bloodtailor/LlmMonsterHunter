// useApi Hook - SIMPLIFIED VERSION
// Just combines useAsyncState with API function execution
// No automatic behavior, no dependencies, no transforms - just state + execute

import { useCallback } from 'react';
import { useAsyncState } from './useAsyncState.js';

/**
 * Simple hook for API calls with state management
 * Component controls WHEN to make API calls via execute function
 * 
 * @param {Function} apiFunction - Function that returns a Promise (API call)
 * @returns {object} API state and execute function
 */
export function useApi(apiFunction) {
  const asyncState = useAsyncState();
  
  /**
   * Execute the API call with provided arguments
   * Automatically manages loading/error/success state
   */
  const execute = useCallback(async (...args) => {
    return await asyncState.execute(apiFunction, ...args);
  }, [apiFunction, asyncState.execute]);

  return {
    // All useAsyncState values and flags
    ...asyncState,
    
    // Main execution function - component controls when this is called
    execute
  };
}