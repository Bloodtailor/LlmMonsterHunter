import { useCallback, useMemo, useEffect } from 'react';
import { useAsyncState } from '../../shared/hooks/useAsyncState.js';
import * as genApi from './../../api/services/generation.js'
import { transformGenerationLogs } from '../transformers/generation.js';

/**
 * Hook for managing monster collections
 * Provides clean monster data + loading state
 */
export function useGenerationLogs() {
  const asyncState = useAsyncState();
  const rawResponse = asyncState.data;

  const loadLogs = useCallback(async (options = {}) => {
    await asyncState.execute(genApi.getGenerationLogs, options);
  }, [asyncState.execute]);

  // Transform raw data when it changes
  const transformedData = useMemo(() => {
    if (!rawResponse) {
      return { logs: [], count: 0 };
    }
    
    return {
      logs: transformGenerationLogs(rawResponse.data?.logs || []),
      count: rawResponse.data?.count || 0
    };
  }, [rawResponse]);

  return {
    // Clean transformed data
    ...transformedData,

    // Raw data (for debugging)
    rawResponse,

    // State flags
    isLoading: asyncState.isLoading,
    isError: asyncState.isError,
    error: asyncState.error,

    // Actions
    loadLogs
  };
}

export function useGenerationLogOptions(){
  const asyncState = useAsyncState();
  const rawResponse = asyncState.data;

  const loadLogOptions = useCallback(async() => {
    await asyncState.execute(genApi.getGenerationLogOptions);
  }, [asyncState.execute])

  // Run the loadLogOptions function on mount
  useEffect(() => {
    loadLogOptions();
  }, [loadLogOptions]);  // Only runs when loadLogOptions changes (i.e., on mount)

  return {
    filterOptions: rawResponse?.data?.filters,
    sortOptions: rawResponse?.data?.sort,
    rawResponse,
    isLoading: asyncState.isLoading,
    isError: asyncState.isError,
    error: asyncState.error
  };
}
