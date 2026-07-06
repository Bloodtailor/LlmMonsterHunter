// Battle App Hooks - PERFECT ARCHITECTURE VERSION
// Uses enhanced useAsyncState with automatic function.defaults detection
// App hooks focus purely on business logic, services handle everything else

import { useCallback } from 'react';
import { useAsyncState } from '../../shared/hooks/useAsyncState.js';
import * as battleApi from '../../api/services/battle.js';

/**
 * Hook for taking a battle turn (queues battle_turn workflow)
 */
export function useTakeTurn() {
  // ✨ Automatically uses takeTurn.defaults
  const api = useAsyncState(battleApi.takeTurn);

  const takeTurn = useCallback(async (action) => {

    return await api.execute(action);
  }, [api.execute]);

  return {
    success: api.data.success,
    workflowId: api.data.workflowId,
    rawResponse: api.data._raw,

    isLoading: api.isLoading,
    isError: api.isError,
    error: api.error,

    takeTurn,
  };
}

/**
 * Hook for replying to enemy battlefield talk (queues battle_turn workflow)
 */
export function useRespondToTalk() {
  // ✨ Automatically uses respondToTalk.defaults
  const api = useAsyncState(battleApi.respondToTalk);

  const respondToTalk = useCallback(async (responseText) => {

    return await api.execute(responseText);
  }, [api.execute]);

  return {
    success: api.data.success,
    workflowId: api.data.workflowId,
    rawResponse: api.data._raw,

    isLoading: api.isLoading,
    isError: api.isError,
    error: api.error,

    respondToTalk,
  };
}
