// Dungeon App Hooks - PERFECT ARCHITECTURE VERSION
// Uses enhanced useAsyncState with automatic function.defaults detection
// Super clean usage - just pass the function, defaults are automatic!
// App hooks focus purely on business logic, services handle everything else

import { useCallback } from 'react';
import { useAsyncState } from '../../shared/hooks/useAsyncState.js';
import * as dungeonApi from '../../api/services/dungeon.js';

/**
 * Hook for entering the dungeon (queues enter_dungeon workflow)
 */
export function useEnterDungeon() {
  // ✨ Automatically uses enterDungeon.defaults
  const api = useAsyncState(dungeonApi.enterDungeon);

  const enterDungeon = useCallback(async () => {

    return await api.execute();
  }, [api.execute]);

  return {
    // Clean result (guaranteed shapes!)
    success: api.data.success,           // null initially, then boolean
    workflowId: api.data.workflowId,     // null initially, then number

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

/**
 * Hook for taking a path (queues choose_path workflow)
 */
export function useChoosePath() {
  // ✨ Automatically uses choosePath.defaults
  const api = useAsyncState(dungeonApi.choosePath);

  const choosePath = useCallback(async (pathId) => {

    return await api.execute(pathId);
  }, [api.execute]);

  return {
    success: api.data.success,
    workflowId: api.data.workflowId,
    rawResponse: api.data._raw,

    isLoading: api.isLoading,
    isError: api.isError,
    error: api.error,

    choosePath,
  };
}

/**
 * Hook for answering the active riddle (queues answer_riddle workflow)
 */
export function useAnswerRiddle() {
  // ✨ Automatically uses answerRiddle.defaults
  const api = useAsyncState(dungeonApi.answerRiddle);

  const answerRiddle = useCallback(async (answer) => {

    return await api.execute(answer);
  }, [api.execute]);

  return {
    success: api.data.success,
    workflowId: api.data.workflowId,
    rawResponse: api.data._raw,

    isLoading: api.isLoading,
    isError: api.isError,
    error: api.error,

    answerRiddle,
  };
}

/**
 * Hook for continuing exploration (queues continue_exploring workflow)
 */
export function useContinueExploring() {
  // ✨ Automatically uses continueExploring.defaults
  const api = useAsyncState(dungeonApi.continueExploring);

  const continueExploring = useCallback(async () => {

    return await api.execute();
  }, [api.execute]);

  return {
    success: api.data.success,
    workflowId: api.data.workflowId,
    rawResponse: api.data._raw,

    isLoading: api.isLoading,
    isError: api.isError,
    error: api.error,

    continueExploring,
  };
}
