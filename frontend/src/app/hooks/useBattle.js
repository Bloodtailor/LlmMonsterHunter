// Battle App Hooks - PERFECT ARCHITECTURE VERSION
// Uses enhanced useAsyncState with automatic function.defaults detection
// App hooks focus purely on business logic, services handle everything else

import { useCallback } from 'react';
import { useAsyncState } from '../../shared/hooks/useAsyncState.js';
import * as battleApi from '../../api/services/battle.js';

/**
 * Hook for submitting a battle round (queues battle_round workflow)
 */
export function useSubmitRound() {
  // ✨ Automatically uses submitRound.defaults
  const api = useAsyncState(battleApi.submitRound);

  const submitRound = useCallback(async (actions) => {

    return await api.execute(actions);
  }, [api.execute]);

  return {
    success: api.data.success,
    workflowId: api.data.workflowId,
    rawResponse: api.data._raw,

    isLoading: api.isLoading,
    isError: api.isError,
    error: api.error,

    submitRound,
  };
}
