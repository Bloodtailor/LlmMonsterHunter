// useMonsters Hook - FINAL CLEAN VERSION
// Domain hooks that manage state + provide both raw and clean data
// Components get clean data effortlessly, raw data available for debugging

import { useCallback, useMemo } from 'react';
import { useAsyncState } from '../../shared/hooks/useAsyncState.js';
import * as monstersApi from '../../api/services/monsters.js';
import {
  transformMonster,
  transformMonsters,
  transformAbility,
  transformAbilities,
  transformMonsterStats
} from '../transformers/monsters.js';

/**
 * Hook for managing monster collections
 * Provides clean monster data + loading state
 */
export function useMonsterCollection() {
  const asyncState = useAsyncState();

  const loadMonsters = useCallback(async (options = {}) => {
    await asyncState.execute(monstersApi.loadMonsters, options);
  }, [asyncState.execute]);

  // Transform raw data when it changes
  const transformedData = useMemo(() => {
    if (!asyncState.data) {
      return { monsters: [], total: 0 };
    }
    
    return {
      monsters: transformMonsters(asyncState.data.monsters || []),
      total: asyncState.data.total || 0
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
    loadMonsters
  };
}

/**
 * Hook for managing individual monster data
 */
export function useMonster() {
  const asyncState = useAsyncState();

  const loadMonster = useCallback(async (monsterId) => {
    try {
      await asyncState.exectue(monstersApi.getMonster(monsterId));
      const rawResponse = asyncState.data
      const monster = transformMonster(rawResponse.monster);
      return {monster, rawResponse};
    } catch (error) {
      console.error(`Failed to load monster ${monsterId}:`, error);
      return null;
    }
  }, []);

  return {
    isLoading: asyncState.isLoading,
    isError: asyncState.isError,
    error: asyncState.error,
    loadMonster
  };
}

/**
 * Hook for monster statistics
 */
export function useMonsterStats() {
  const asyncState = useAsyncState();

  const loadStats = useCallback(async (filter = 'all') => {
    await asyncState.execute(monstersApi.loadMonsterStats, filter);
  }, [asyncState.execute]);

  // Transform raw stats when data changes
  const stats = useMemo(() => {
    if (!asyncState.data?.stats) return null;
    return transformMonsterStats(asyncState.data.stats);
  }, [asyncState.data]);

  return {
    stats,
    rawResponse: asyncState.data,
    isLoading: asyncState.isLoading,
    isError: asyncState.isError,
    error: asyncState.error,
    loadStats
  };
}

/**
 * Hook for monster abilities
 */
export function useMonsterAbilities() {
  const asyncState = useAsyncState();

  const loadAbilities = useCallback(async (monsterId) => {
    await asyncState.execute(monstersApi.getMonsterAbilities, monsterId);
  }, [asyncState.execute]);

  // Transform raw abilities when data changes
  const transformedData = useMemo(() => {
    if (!asyncState.data) {
      return { abilities: [], count: 0, monsterId: null };
    }
    
    return {
      abilities: transformAbilities(asyncState.data.abilities || []),
      count: asyncState.data.count || 0,
      monsterId: asyncState.data.monster_id || null
    };
  }, [asyncState.data]);

  return {
    ...transformedData,
    rawResponse: asyncState.data,
    isLoading: asyncState.isLoading,
    isError: asyncState.isError,
    error: asyncState.error,
    loadAbilities
  };
}

/**
 * Hook for monster card art
 */
export function useMonsterCardArt() {
  const asyncState = useAsyncState();

  const loadCardArt = useCallback(async (monsterId) => {
    await asyncState.execute(monstersApi.getMonsterCardArt, monsterId);
  }, [asyncState.execute]);

  // Transform raw card art when data changes
  const cardArt = useMemo(() => {
    if (!asyncState.data) return null;
    
    return {
      exists: asyncState.data.card_art?.exists || false,
      relativePath: asyncState.data.card_art?.relative_path || null,
      monsterId: asyncState.data.monster_id || null
    };
  }, [asyncState.data]);

  return {
    cardArt,
    rawResponse: asyncState.data,
    isLoading: asyncState.isLoading,
    isError: asyncState.isError,
    error: asyncState.error,
    loadCardArt
  };
}

/**
 * Hook for monster templates
 */
export function useMonsterTemplates() {
  const asyncState = useAsyncState();

  const loadTemplates = useCallback(async () => {
    await asyncState.execute(monstersApi.getMonsterTemplates);
  }, [asyncState.execute]);

  // Templates are already clean, just extract them
  const templates = useMemo(() => {
    return asyncState.data?.templates || {};
  }, [asyncState.data]);

  return {
    templates,
    rawResponse: asyncState.data,
    isLoading: asyncState.isLoading,
    isError: asyncState.isError,
    error: asyncState.error,
    loadTemplates
  };
}

/**
 * Hook for monster generation (mutation)
 */
export function useMonsterGeneration() {
  const asyncState = useAsyncState();

  const generate = useCallback(async (options = {}) => {
    const generationOptions = {
      prompt_name: 'detailed_monster',
      generate_card_art: true,
      ...options
    };
    
    await asyncState.execute(monstersApi.generateMonster, generationOptions);
  }, [asyncState.execute]);

  // Transform generation result when data changes
  const generationResult = useMemo(() => {
    if (!asyncState.data) return null;
    
    return {
      success: asyncState.data.success || false,
      monster: asyncState.data.monster ? transformMonster(asyncState.data.monster) : null,
      requestId: asyncState.data.request_id || null,
      logId: asyncState.data.log_id || null,
      error: asyncState.data.error || null
    };
  }, [asyncState.data]);

  return {
    generationResult,
    monster: generationResult?.monster || null,
    rawResponse: asyncState.data,
    isGenerating: asyncState.isLoading,
    isError: asyncState.isError,
    error: asyncState.error,
    generate
  };
}

/**
 * Hook for ability generation (mutation)
 */
export function useAbilityGeneration() {
  const asyncState = useAsyncState();

  const generate = useCallback(async (monsterId, options = {}) => {
    const generationOptions = {
      wait_for_completion: true,
      ...options
    };
    
    await asyncState.execute(monstersApi.generateAbility, monsterId, generationOptions);
  }, [asyncState.execute]);

  // Transform ability generation result when data changes
  const generationResult = useMemo(() => {
    if (!asyncState.data) return null;
    
    return {
      success: asyncState.data.success || false,
      ability: asyncState.data.ability ? transformAbility(asyncState.data.ability) : null,
      requestId: asyncState.data.request_id || null,
      logId: asyncState.data.log_id || null,
      error: asyncState.data.error || null
    };
  }, [asyncState.data]);

  return {
    generationResult,
    ability: generationResult?.ability || null,
    rawResponse: asyncState.data,
    isGenerating: asyncState.isLoading,
    isError: asyncState.isError,
    error: asyncState.error,
    generate
  };
}

/**
 * Hook for card art generation (mutation)
 */
export function useCardArtGeneration() {
  const asyncState = useAsyncState();

  const generate = useCallback(async (monsterId, options = {}) => {
    await asyncState.execute(monstersApi.generateCardArt, monsterId, options);
  }, [asyncState.execute]);

  return {
    generationResult: asyncState.data,
    rawResponse: asyncState.data,
    isGenerating: asyncState.isLoading,
    isError: asyncState.isError,
    error: asyncState.error,
    generate
  };
}

// ===== CLEAN COMPONENT USAGE EXAMPLE =====
/*

function MonsterListScreen() {
  // UI state
  const [filter, setFilter] = useState('all');
  const [sort, setSort] = useState('newest');

  // Domain hook - provides clean data + state management
  const { 
    monsters,         // ← Clean transformed monsters
    total,           // ← Clean total number
    isLoading,       // ← Managed by useAsyncState
    loadMonsters     // ← Just call it, no await needed!
  } = useMonsterCollection();

  // UI pagination hook
  const pagination = usePagination({ limit: 12, total });

  // Component coordinates when to load
  useEffect(() => {
    loadMonsters({
      limit: pagination.limit,
      offset: pagination.currentOffset,
      filter: filter !== 'all' ? filter : undefined,
      sort
    });
  }, [filter, sort, pagination.currentOffset]);

  const handlePageChange = (page) => {
    pagination.goToPage(page);
    // loadMonsters will be called by useEffect when pagination.currentOffset changes
  };

  return (
    <div>
      <select value={filter} onChange={(e) => setFilter(e.target.value)}>
        <option value="all">All</option>
        <option value="with_art">With Art</option>
        <option value="without_art">Without Art</option>
      </select>

      {isLoading ? (
        <LoadingContainer message="Loading monsters..." />
      ) : (
        <MonsterGrid monsters={monsters} />  // ← Clean data, no transformation needed
      )}

      <Pagination pagination={pagination} onPageChange={handlePageChange} />
    </div>
  );
}

*/