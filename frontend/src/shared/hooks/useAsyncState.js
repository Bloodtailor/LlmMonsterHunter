// useAsyncState Hook - Manages loading, error, and data state for async operations
// Eliminates the scattered loading/error/data patterns throughout the codebase

import { useState, useCallback } from 'react';
import { APP_STATES} from '../constants/constants';

/**
 * Hook for managing async operation state consistently
 * @param {any} initialData - Initial data value
 * @returns {object} Async state and control functions
 */
export function useAsyncState(initialData = null) {
  const [state, setState] = useState(APP_STATES.IDLE);
  const [data, setData] = useState(initialData);
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
   * Reset to idle state
   */
  const reset = useCallback(() => {
    setState(APP_STATES.IDLE);
    setData(initialData);
    setError(null);
  }, [initialData]);

  /**
   * Execute an async function with automatic state management
   * @param {Function} asyncFn - Async function to execute
   * @param {...any} args - Arguments to pass to the async function
   * @returns {Promise<any>} Result of the async function
   */
  const execute = useCallback(async (asyncFn, ...args) => {
    try {
      setLoading();
      const result = await asyncFn(...args);
      setSuccess(result);
      return result;
    } catch (err) {
      setErrorState(err);
      throw err; // Re-throw so caller can handle if needed
    }
  }, [setLoading, setSuccess, setErrorState]);

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
    
    // Main execution function
    execute
  };
}