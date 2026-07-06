// Monster App Hooks - PERFECT ARCHITECTURE VERSION
// Uses enhanced useAsyncState with automatic function.defaults detection
// Super clean usage - just pass the function, defaults are automatic!
// App hooks focus purely on business logic, services handle everything else

import { useCallback, useState, useEffect } from 'react';
import { useAsyncState } from '../../shared/hooks/useAsyncState.js';
import { useEventSubscription } from '../../api/events/useEventSubscription.js';
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
 * Hook for a monster collection that stays live via monster domain events
 * Patches single monsters in place from event payloads (no refetch),
 * so cards update without unmounting or losing their flip state
 */
export function useLiveMonsterCollection() {
  const collection = useMonsterCollection();

  // Local copy of the collection that we can patch per-monster
  const [monsters, setMonsters] = useState(collection.monsters);

  // Sync from API whenever a real load completes (initial load, pagination, filters)
  useEffect(() => {
    setMonsters(collection.monsters);
  }, [collection.monsters]);

  // Helper - update one monster in place, leave the rest untouched
  const patchMonster = (monsterId, patch) => {
    setMonsters(prev => prev.map(monster =>
      monster.id === monsterId ? { ...monster, ...patch(monster) } : monster
    ));
  };

  // Staged generation filled in more of the monster (persona, story) -
  // replace it wholesale; the event payload is the complete monster
  useEventSubscription('monsterUpdated', ({ monster }) => {
    if (!monster?.id) return;
    setMonsters(prev => prev.map(existing =>
      existing.id === monster.id ? monster : existing
    ));
  });

  // Card art finished - attach it to just that monster's card
  useEventSubscription('monsterArtReady', ({ monsterId, imagePath }) => {
    if (!monsterId || !imagePath) return;
    patchMonster(monsterId, () => ({
      cardArt: { exists: true, relativePath: imagePath }
    }));
  });

  // New ability landed - append it to just that monster's card
  useEventSubscription('monsterAbilityAdded', ({ monsterId, ability }) => {
    if (!monsterId || !ability) return;
    patchMonster(monsterId, (monster) => ({
      abilities: [...(monster.abilities || []), ability],
      abilityCount: (monster.abilityCount || 0) + 1
    }));
  });

  return {
    ...collection,
    monsters
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