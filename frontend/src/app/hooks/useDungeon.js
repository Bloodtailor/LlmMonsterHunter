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
    success: api.data.success, // null initially, then boolean
    workflowId: api.data.workflowId, // null initially, then number

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

  const choosePath = useCallback(
    async (pathId) => {
      return await api.execute(pathId);
    },
    [api.execute],
  );

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
 * Hook for speaking to the encounter monsters (queues respond_to_monster workflow)
 */
export function useRespondToMonster() {
  // ✨ Automatically uses respondToMonster.defaults
  const api = useAsyncState(dungeonApi.respondToMonster);

  const respondToMonster = useCallback(
    async (message) => {
      return await api.execute(message);
    },
    [api.execute],
  );

  return {
    success: api.data.success,
    workflowId: api.data.workflowId,
    rawResponse: api.data._raw,

    isLoading: api.isLoading,
    isError: api.isError,
    error: api.error,

    respondToMonster,
  };
}

/**
 * Hook for sneaking past the area's monsters (queues sneak_past workflow)
 */
export function useSneakPast() {
  // ✨ Automatically uses sneakPast.defaults
  const api = useAsyncState(dungeonApi.sneakPast);

  const sneakPast = useCallback(async () => {
    return await api.execute();
  }, [api.execute]);

  return {
    success: api.data.success,
    workflowId: api.data.workflowId,
    rawResponse: api.data._raw,

    isLoading: api.isLoading,
    isError: api.isError,
    error: api.error,

    sneakPast,
  };
}

/**
 * Hook for springing a surprise attack (queues surprise_attack workflow)
 */
export function useSurpriseAttack() {
  // ✨ Automatically uses surpriseAttack.defaults
  const api = useAsyncState(dungeonApi.surpriseAttack);

  const surpriseAttack = useCallback(async () => {
    return await api.execute();
  }, [api.execute]);

  return {
    success: api.data.success,
    workflowId: api.data.workflowId,
    rawResponse: api.data._raw,

    isLoading: api.isLoading,
    isError: api.isError,
    error: api.error,

    surpriseAttack,
  };
}

/**
 * Hook for setting up camp (queues setup_camp workflow)
 */
export function useSetupCamp() {
  // ✨ Automatically uses setupCamp.defaults
  const api = useAsyncState(dungeonApi.setupCamp);

  const setupCamp = useCallback(async () => {
    return await api.execute();
  }, [api.execute]);

  return {
    success: api.data.success,
    workflowId: api.data.workflowId,
    rawResponse: api.data._raw,

    isLoading: api.isLoading,
    isError: api.isError,
    error: api.error,

    setupCamp,
  };
}

/**
 * Hook for using a party monster's ability on anything outside battle
 * (queues use_dungeon_ability workflow)
 * Note: the action is named activateAbility (not useAbility) so lint
 * doesn't mistake it for a React hook
 */
export function useDungeonAbility() {
  // ✨ Automatically uses useDungeonAbility.defaults
  const api = useAsyncState(dungeonApi.useDungeonAbility);

  const activateAbility = useCallback(
    async ({ monsterId, abilityId, targetType, targetId, targetText }) => {
      return await api.execute({ monsterId, abilityId, targetType, targetId, targetText });
    },
    [api.execute],
  );

  return {
    success: api.data.success,
    workflowId: api.data.workflowId,
    rawResponse: api.data._raw,

    isLoading: api.isLoading,
    isError: api.isError,
    error: api.error,

    activateAbility,
  };
}

/**
 * Hook for using an inventory item on anything outside battle
 * (queues use_dungeon_item workflow)
 * Note: the action is named activateItem (not useItem) so lint
 * doesn't mistake it for a React hook
 */
export function useDungeonItem() {
  // ✨ Automatically uses useDungeonItem.defaults
  const api = useAsyncState(dungeonApi.useDungeonItem);

  const activateItem = useCallback(
    async ({ itemId, targetType, targetId, targetText }) => {
      return await api.execute({ itemId, targetType, targetId, targetText });
    },
    [api.execute],
  );

  return {
    success: api.data.success,
    workflowId: api.data.workflowId,
    rawResponse: api.data._raw,

    isLoading: api.isLoading,
    isError: api.isError,
    error: api.error,

    activateItem,
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
