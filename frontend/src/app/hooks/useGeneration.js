import { useEffect } from 'react';
import { useAsyncState } from '../../shared/hooks/useAsyncState.js';
import * as generationApi  from './../../api/services/generation.js'

/**
 * Hook for managing monster collections
 * Provides clean monster data + loading state
 */
/**
 * Hook for managing generation logs
 * Provides clean generation logs data + loading state with business logic
 */
export function useGenerationLogs() {
  // ✨ SUPER CLEAN - automatically uses getGenerationLogs.defaults
  const api = useAsyncState(generationApi.getGenerationLogs);

  return {
    // Clean transformed data (guaranteed shapes from function.defaults!)
    logs: api.data.logs,         // Always an array
    count: api.data.count,       // Always a number

    // Raw data (for debugging)
    rawResponse: api.data._raw,

    // State flags
    isLoading: api.isLoading,
    isError: api.isError,
    error: api.error,

    // Actions
    loadLogs: api.execute,
    reset: api.reset
  };
}

/**
 * Hook for generation log filter and sort options
 * Auto-loads options on mount for immediate use
 */
export function useGenerationLogOptions() {
  // ✨ Automatically uses getGenerationLogOptions.defaults
  const api = useAsyncState(generationApi.getGenerationLogOptions);

  // Auto-load options on mount
  useEffect(() => {
    api.execute();
  }, [api.execute]);

  return {
    // Clean transformed data (guaranteed shapes!)
    filterOptions: api.data.filterOptions,           // Always an object with arrays
    sortOptions: api.data.sortOptions,   // Always an object

    // Raw data (for debugging)
    rawResponse: api.data._raw,

    // State flags
    isLoading: api.isLoading,
    isError: api.isError,
    error: api.error,

    // Actions
    loadLogOptions: api.execute,
    reset: api.reset
  };
}
