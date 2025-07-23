// useMonsters Hook - Complete monster management with clean game objects
// Handles monster collections, individual monsters, generation, and abilities
// Uses API services + transformers to provide clean data to components

import { useState, useCallback } from 'react';
import { useApi, useApiMutation, useApiWithParams } from '../../shared/hooks/useApi.js';
import * as monstersApi from '../../api/services/monsters.js';
import {
  transformMonsterCollection,
  transformMonsterResponse,
  transformMonsterStats,
  transformAbilitiesCollection,
  transformCardArt,
  transformMonsterTemplates,
  transformMonsterGeneration,
  transformAbilityGeneration
} from '../transformers/monsters.js';

/**
 * Hook for managing monster collections with pagination and filtering
 * @param {object} options - Collection options
 * @param {number} options.limit - Number of monsters per page (default: 12)
 * @param {string} options.filter - Filter type ('all', 'with_art', 'without_art')
 * @param {string} options.sort - Sort order ('newest', 'oldest', 'name', 'species')
 * @param {boolean} options.immediate - Load on mount (default: true)
 * @returns {object} Collection state and actions
 */
export function useMonsterCollection(options = {}) {
  const {
    limit = 12,
    filter = 'all',
    sort = 'newest',
    immediate = true
  } = options;

  // Track pagination state
  const [currentOffset, setCurrentOffset] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);

  // Use API hook with direct function call
  const {
    data: rawData,
    isLoading,
    isError,
    error,
    refetch,
    execute
  } = useApi(
    () => monstersApi.loadMonsters({
      limit,
      offset: currentOffset,
      filter: filter !== 'all' ? filter : undefined,
      sort
    }),
    {
      immediate,
      transform: transformMonsterCollection,
      deps: [limit, currentOffset, filter, sort]
    }
  );

  // Pagination helpers
  const goToPage = useCallback((page) => {
    const newOffset = (page - 1) * limit;
    setCurrentOffset(newOffset);
    setCurrentPage(page);
  }, [limit]);

  const nextPage = useCallback(() => {
    if (rawData?.pagination?.hasMore) {
      const newPage = currentPage + 1;
      goToPage(newPage);
    }
  }, [rawData?.pagination?.hasMore, currentPage, goToPage]);

  const prevPage = useCallback(() => {
    if (currentPage > 1) {
      const newPage = currentPage - 1;
      goToPage(newPage);
    }
  }, [currentPage, goToPage]);

  const resetPagination = useCallback(() => {
    setCurrentOffset(0);
    setCurrentPage(1);
  }, []);

  // Calculate pagination info
  const pagination = rawData?.pagination ? {
    ...rawData.pagination,
    currentPage,
    totalPages: Math.ceil(rawData.pagination.total / limit),
    hasNextPage: rawData.pagination.hasMore,
    hasPrevPage: currentPage > 1
  } : null;

  return {
    // Data
    monsters: rawData?.monsters || [],
    filters: rawData?.filters || { type: filter, sortBy: sort },
    pagination,

    // States
    isLoading,
    isError,
    error,

    // Actions
    refetch,
    reload: execute,
    goToPage,
    nextPage,
    prevPage,
    resetPagination
  };
}

/**
 * Hook for managing individual monster data
 * @param {number|null} monsterId - Monster ID to load
 * @param {boolean} immediate - Load on mount (default: true)
 * @returns {object} Monster state and actions
 */
export function useMonster(monsterId, immediate = true) {
  const {
    data: monster,
    isLoading,
    isError,
    error,
    refetch,
    execute
  } = useApiWithParams(
    monstersApi.getMonster,
    [monsterId],
    {
      immediate: immediate && monsterId != null,
      transform: transformMonsterResponse,
      deps: [monsterId]
    }
  );

  return {
    monster,
    isLoading,
    isError,
    error,
    refetch,
    reload: execute
  };
}

/**
 * Hook for monster statistics
 * @param {string} filter - Filter type ('all', 'with_art', 'without_art')
 * @param {boolean} immediate - Load on mount (default: true)
 * @returns {object} Stats state and actions
 */
export function useMonsterStats(filter = 'all', immediate = true) {
  const {
    data: stats,
    isLoading,
    isError,
    error,
    refetch
  } = useApi(
    () => monstersApi.loadMonsterStats(filter),
    {
      immediate,
      transform: transformMonsterStats,
      deps: [filter]
    }
  );

  return {
    stats,
    isLoading,
    isError,
    error,
    refetch
  };
}

/**
 * Hook for monster abilities
 * @param {number|null} monsterId - Monster ID to load abilities for
 * @param {boolean} immediate - Load on mount (default: true)
 * @returns {object} Abilities state and actions
 */
export function useMonsterAbilities(monsterId, immediate = true) {
  const {
    data: abilitiesData,
    isLoading,
    isError,
    error,
    refetch
  } = useApiWithParams(
    monstersApi.getMonsterAbilities,
    [monsterId],
    {
      immediate: immediate && monsterId != null,
      transform: transformAbilitiesCollection,
      deps: [monsterId]
    }
  );

  return {
    abilities: abilitiesData?.abilities || [],
    count: abilitiesData?.count || 0,
    monsterId: abilitiesData?.monsterId || null,
    isLoading,
    isError,
    error,
    refetch
  };
}

/**
 * Hook for monster card art
 * @param {number|null} monsterId - Monster ID to load card art for
 * @param {boolean} immediate - Load on mount (default: true)
 * @returns {object} Card art state and actions
 */
export function useMonsterCardArt(monsterId, immediate = true) {
  const {
    data: cardArt,
    isLoading,
    isError,
    error,
    refetch
  } = useApiWithParams(
    monstersApi.getMonsterCardArt,
    [monsterId],
    {
      immediate: immediate && monsterId != null,
      transform: transformCardArt,
      deps: [monsterId]
    }
  );

  return {
    cardArt,
    isLoading,
    isError,
    error,
    refetch
  };
}

/**
 * Hook for monster templates (generation options)
 * @param {boolean} immediate - Load on mount (default: true)
 * @returns {object} Templates state and actions
 */
export function useMonsterTemplates(immediate = true) {
  const {
    data: templates,
    isLoading,
    isError,
    error,
    refetch
  } = useApi(monstersApi.getMonsterTemplates, {
    immediate,
    transform: transformMonsterTemplates
  });

  return {
    templates: templates || {},
    isLoading,
    isError,
    error,
    refetch
  };
}

/**
 * Hook for monster generation (mutation)
 * @returns {object} Generation state and actions
 */
export function useMonsterGeneration() {
  const {
    data: generationResult,
    isLoading: isGenerating,
    isError,
    error,
    execute: generateMonster
  } = useApiMutation(
    (options) => monstersApi.generateMonster(options),
    {
      transform: transformMonsterGeneration
    }
  );

  // Helper function with default options
  const generate = useCallback((options = {}) => {
    return generateMonster({
      prompt_name: 'detailed_monster',
      generate_card_art: true,
      ...options
    });
  }, [generateMonster]);

  return {
    generationResult,
    monster: generationResult?.monster || null,
    isGenerating,
    isError,
    error,
    generate,
    generateMonster
  };
}

/**
 * Hook for ability generation (mutation)
 * @returns {object} Ability generation state and actions
 */
export function useAbilityGeneration() {
  const {
    data: generationResult,
    isLoading: isGenerating,
    isError,
    error,
    execute: generateAbility
  } = useApiMutation(
    (monsterId, options) => monstersApi.generateAbility(monsterId, options),
    {
      transform: transformAbilityGeneration
    }
  );

  // Helper function with default options
  const generate = useCallback((monsterId, options = {}) => {
    return generateAbility(monsterId, {
      wait_for_completion: true,
      ...options
    });
  }, [generateAbility]);

  return {
    generationResult,
    ability: generationResult?.ability || null,
    isGenerating,
    isError,
    error,
    generate,
    generateAbility
  };
}

/**
 * Hook for card art generation (mutation)
 * @returns {object} Card art generation state and actions
 */
export function useCardArtGeneration() {
  const {
    data: generationResult,
    isLoading: isGenerating,
    isError,
    error,
    execute: generateCardArt
  } = useApiMutation(
    (monsterId, options) => monstersApi.generateCardArt(monsterId, options)
  );

  return {
    generationResult,
    isGenerating,
    isError,
    error,
    generateCardArt
  };
}

/**
 * Comprehensive hook that combines multiple monster operations
 * Perfect for complex components that need multiple monster operations
 * @param {object} options - Configuration options
 * @returns {object} All monster operations
 */
export function useMonsters(options = {}) {
  const collection = useMonsterCollection(options.collection);
  const stats = useMonsterStats(options.statsFilter, options.loadStats);
  const generation = useMonsterGeneration();
  const abilityGeneration = useAbilityGeneration();
  const cardArtGeneration = useCardArtGeneration();
  const templates = useMonsterTemplates(options.loadTemplates);

  return {
    // Collection operations
    collection,
    
    // Statistics
    stats,
    
    // Generation operations
    generation,
    abilityGeneration,
    cardArtGeneration,
    
    // Templates
    templates,
    
    // Helper function to reload everything
    refreshAll: useCallback(() => {
      collection.refetch();
      stats.refetch();
      templates.refetch();
    }, [collection, stats, templates])
  };
}