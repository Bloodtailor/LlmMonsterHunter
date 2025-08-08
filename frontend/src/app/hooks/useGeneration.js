import { useCallback, useMemo } from 'react';
import { useAsyncState } from '../../shared/hooks/useAsyncState.js';
import * as genApi from './../../api/services/generation.js'
import { transformGenerationLogs } from '../transformers/generation.js';

/**
 * Hook for managing monster collections
 * Provides clean monster data + loading state
 */
export function useGenerationLogs() {
  const asyncState = useAsyncState();

  const loadLogs = useCallback(async (options = {}) => {
    await asyncState.execute(genApi.getGenerationLogs, options);
  }, [asyncState.execute]);

  // Transform raw data when it changes
  const transformedData = useMemo(() => {
    if (!asyncState.data) {
      return { logs: [], count: 0 };
    }
    
    return {
      logs: transformGenerationLogs(asyncState.data.data?.logs || []),
      count: asyncState.data.data?.count || 0
    };
  }, [asyncState.data]);

  return {
    // Clean transformed data
    ...transformedData,

    // Raw data (for debugging)
    rawResponse: asyncState.data,

    // State flags
    isLoading: asyncState.isLoading,
    isError: asyncState.isError,
    error: asyncState.error,

    // Actions
    loadLogs
  };
}

