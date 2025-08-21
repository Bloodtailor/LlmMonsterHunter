// Monster App Hooks - PERFECT ARCHITECTURE VERSION
// Uses enhanced useAsyncState with automatic function.defaults detection
// Super clean usage - just pass the function, defaults are automatic!
// App hooks focus purely on business logic, services handle everything else

import { useCallback } from 'react';
import { useAsyncState } from '../../shared/hooks/useAsyncState.js';
import * as dungeonApi from '../../api/services/dungeon.js';

/**
 * Hook for monster generation (mutation)
 */
export function useEnterDungeon() {
  // ✨ Automatically uses generateMonster.defaults
  const api = useAsyncState(dungeonApi.enterDungeon);

  const enterDungeon = useCallback(async () => {
    
    return await api.execute();
  }, [api.execute]);

  return {
    // Clean generation result (guaranteed shapes!)
    success: api.data.success,           // false initially, then boolean
    workflowId: api.data.workflowId,           // null initially, then monster object

    // Raw data (for debugging)
    rawResponse: api.data._raw,

    // State flags
    isLoading: api.isLoading,
    isError: api.isError,
    error: api.error,

    // Actions
    enterDungeon,
  };
}