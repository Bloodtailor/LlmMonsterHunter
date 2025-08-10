// useAsyncState Hook - ENHANCED VERSION with function.defaults support
// Automatically uses function.defaults if available, falls back to explicit initialData
// Manages loading, error, and data state for async operations with perfect pairing

import { useState, useCallback } from 'react';
import { APP_STATES } from '../constants/constants';

/**
 * Enhanced useAsyncState - automatically uses function.defaults if available
 * @param {Function} asyncFunction - The async function to bind to this state
 * @param {any} initialData - Explicit initial data (optional if function has defaults)
 * @returns {object} Async state and control functions
 */
export function useAsyncState(asyncFunction, initialData = null) {
  // Use function.defaults if available, otherwise use explicit initialData
  const resolvedInitialData = asyncFunction.defaults ?? initialData;
  
  const [state, setState] = useState(APP_STATES.IDLE);
  const [data, setData] = useState(resolvedInitialData);
  const [error, setError] = useState(null);

  /**
   * Set loading state and clear previous error
   */
  const setLoading = useCallback(() => {
    setState(APP_STATES.LOADING);
    setError(null);
  }, []);

  /**
   * Set success state with data
   * @param {any} newData - Success data
   */
  const setSuccess = useCallback((newData) => {
    setState(APP_STATES.SUCCESS);
    setData(newData);
    setError(null);
  }, []);

  /**
   * Set error state with error info
   * @param {Error|string} newError - Error object or message
   */
  const setErrorState = useCallback((newError) => {
    setState(APP_STATES.ERROR);
    setError(newError);
  }, []);

  /**
   * Reset to idle state with initial data
   */
  const reset = useCallback(() => {
    setState(APP_STATES.IDLE);
    setData(resolvedInitialData);
    setError(null);
  }, [resolvedInitialData]);

  /**
   * Execute the bound async function with automatic state management
   * @param {...any} args - Arguments to pass to the bound async function
   * @returns {Promise<any>} Result of the async function
   */
  const execute = useCallback(async (...args) => {
    try {
      setLoading();
      const result = await asyncFunction(...args);
      setSuccess(result);
      return result;
    } catch (err) {
      setErrorState(err);
      throw err; // Re-throw so caller can handle if needed
    }
  }, [asyncFunction, setLoading, setSuccess, setErrorState]);

  // Computed state flags for convenience
  const isLoading = state === APP_STATES.LOADING;
  const isError = state === APP_STATES.ERROR;
  const isSuccess = state === APP_STATES.SUCCESS;
  const isIdle = state === APP_STATES.IDLE;

  return {
    // State values
    state,
    data,
    error,
    
    // Computed flags
    isLoading,
    isError,
    isSuccess,
    isIdle,
    
    // State setters
    setLoading,
    setSuccess,
    setError: setErrorState,
    reset,
    
    // Main execution function - bound to the asyncFunction
    execute
  };
}