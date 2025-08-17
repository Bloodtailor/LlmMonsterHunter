// Monster App Hooks - PERFECT ARCHITECTURE VERSION
// Uses enhanced useAsyncState with automatic function.defaults detection
// Super clean usage - just pass the function, defaults are automatic!
// App hooks focus purely on business logic, services handle everything else

import { useCallback } from 'react';
import { useAsyncState } from '../../shared/hooks/useAsyncState.js';
import * as monstersApi from '../../api/services/monster.js'

// ===== MONSTER COLLECTION HOOKS =====

/**
 * Hook for managing monster collections
 * Provides clean monster data + loading state with business logic
 */
export function useMonsterCollection() {
  // ✨ SUPER CLEAN - automatically uses loadMonsters.defaults
  const api = useAsyncState(monstersApi.loadMonsters);

  return {
    // Clean transformed data (guaranteed shapes from function.defaults!)
    monsters: api.data.monsters,     // Always an array
    total: api.data.total,           // Always a number
    count: api.data.count,           // Always a number
    limit: api.data.limit,           // Always a number
    offset: api.data.offset,         // Always a number

    // Raw data (for debugging)
    rawResponse: api.data._raw,

    // State flags
    isLoading: api.isLoading,
    isError: api.isError,
    error: api.error,

    // Actions
    loadMonsters: api.execute,
    reset: api.reset
  };
}

/**
 * Hook for monster generation (mutation)
 */
export function useMonsterGeneration() {
  // ✨ Automatically uses generateMonster.defaults
  const api = useAsyncState(monstersApi.generateMonster);

  const generate = useCallback(async () => {
    
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
    generate,
  };
}

/**
 * Hook for ability generation (mutation)
 */
export function useAbilityGeneration() {
  // ✨ Automatically uses generateAbility.defaults
  const api = useAsyncState(monstersApi.generateAbility);

  return {
    // Clean generation result
    success: api.data.success,           // false initially
    ability: api.data.ability,           // null initially, then ability object
    requestId: api.data.requestId,       // null initially, then string
    logId: api.data.logId,               // null initially, then string
    generationError: api.data.error,     // null initially, then string

    // Raw data (for debugging)
    rawResponse: api.data._raw,

    // State flags
    isGenerating: api.isLoading,
    isError: api.isError,
    error: api.error,

    // Actions
    generate: api.execute,
    reset: api.reset
  };
}