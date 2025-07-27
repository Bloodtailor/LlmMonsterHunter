// useMonsters Hook - Updated to use simplified useApi pattern
// Components control WHEN to make API calls via execute functions
// Hooks provide data access + business logic, transformers applied explicitly

import { useState, useCallback } from 'react';
import { useApi } from '../../shared/hooks/useApi.js';
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
 * Hook for managing monster collections with pagination
 * Component controls when to load via loadMonsters function
 */
export function useMonsterCollection() {
  const { data, isLoading, isError, error, execute } = useApi(monstersApi.loadMonsters);
  
  // Pagination state managed by this hook
  const [currentOffset, setCurrentOffset] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);

  /**
   * Load monsters with specified options
   * Component calls this when it wants to load data
   * @param {object} options - Query options (limit, filter, sort, etc.)
   * @returns {Promise<object>} Transformed monster collection
   */
  const loadMonsters = useCallback(async (options = {}) => {
    const params = {
      offset: currentOffset,
      ...options  // Component provides limit, filter, sort, etc.
    };
    
    console.log('🔄 Loading monsters with params:', params);
    const rawData = await execute(params);
    
    // Apply transformation explicitly
    const transformedData = transformMonsterCollection(rawData);
    return transformedData;
  }, [currentOffset, execute]);

  /**
   * Navigate to specific page
   * Updates pagination state - component should call loadMonsters after
   */
  const goToPage = useCallback((page, limit = 12) => {
    const newOffset = (page - 1) * limit;
    setCurrentOffset(newOffset);
    setCurrentPage(page);
  }, []);

  /**
   * Reset pagination to first page  
   */
  const resetPagination = useCallback(() => {
    setCurrentOffset(0);
    setCurrentPage(1);
  }, []);

  // Calculate pagination info from current data
  const pagination = data?.pagination ? {
    ...data.pagination,
    currentPage,
    totalPages: Math.ceil(data.pagination.total / (data.pagination.limit || 12)),
    hasNextPage: data.pagination.hasMore,
    hasPrevPage: currentPage > 1
  } : null;

  return {
    // Transformed data
    monsters: data?.monsters || [],
    filters: data?.filters || { type: 'all', sortBy: 'newest' },
    pagination,

    // State flags
    isLoading,
    isError,
    error,

    // Pagination state
    currentPage,
    currentOffset,

    // Actions (component controls when these are called)
    loadMonsters,
    goToPage,
    resetPagination
  };
}

/**
 * Hook for managing individual monster data
 * Component controls when to load via loadMonster function
 */
export function useMonster() {
  const { data, isLoading, isError, error, execute } = useApi(monstersApi.getMonster);

  /**
   * Load specific monster by ID
   * @param {number} monsterId - Monster ID to load
   * @returns {Promise<object>} Transformed monster object
   */
  const loadMonster = useCallback(async (monsterId) => {
    console.log('🐲 Loading monster:', monsterId);
    const rawData = await execute(monsterId);
    
    // Apply transformation explicitly
    const transformedData = transformMonsterResponse(rawData);
    return transformedData;
  }, [execute]);

  return {
    monster: data,
    isLoading,
    isError,
    error,
    loadMonster
  };
}

/**
 * Hook for monster statistics
 * Component controls when to load via loadStats function
 */
export function useMonsterStats() {
  const { data, isLoading, isError, error, execute } = useApi(monstersApi.loadMonsterStats);

  /**
   * Load monster statistics with filter
   * @param {string} filter - Filter type ('all', 'with_art', 'without_art')
   * @returns {Promise<object>} Transformed stats object
   */
  const loadStats = useCallback(async (filter = 'all') => {
    console.log('📈 Loading monster stats with filter:', filter);
    const rawData = await execute(filter);
    
    // Apply transformation explicitly
    const transformedData = transformMonsterStats(rawData);
    return transformedData;
  }, [execute]);

  return {
    stats: data,
    isLoading,
    isError,
    error,
    loadStats
  };
}

/**
 * Hook for monster abilities
 * Component controls when to load via loadAbilities function
 */
export function useMonsterAbilities() {
  const { data, isLoading, isError, error, execute } = useApi(monstersApi.getMonsterAbilities);

  /**
   * Load abilities for specific monster
   * @param {number} monsterId - Monster ID to load abilities for
   * @returns {Promise<object>} Transformed abilities collection
   */
  const loadAbilities = useCallback(async (monsterId) => {
    console.log('⚡ Loading abilities for monster:', monsterId);
    const rawData = await execute(monsterId);
    
    // Apply transformation explicitly
    const transformedData = transformAbilitiesCollection(rawData);
    return transformedData;
  }, [execute]);

  return {
    abilities: data?.abilities || [],
    count: data?.count || 0,
    monsterId: data?.monsterId || null,
    isLoading,
    isError,
    error,
    loadAbilities
  };
}

/**
 * Hook for monster card art
 * Component controls when to load via loadCardArt function
 */
export function useMonsterCardArt() {
  const { data, isLoading, isError, error, execute } = useApi(monstersApi.getMonsterCardArt);

  /**
   * Load card art for specific monster
   * @param {number} monsterId - Monster ID to load card art for
   * @returns {Promise<object>} Transformed card art object
   */
  const loadCardArt = useCallback(async (monsterId) => {
    console.log('🎨 Loading card art for monster:', monsterId);
    const rawData = await execute(monsterId);
    
    // Apply transformation explicitly
    const transformedData = transformCardArt(rawData);
    return transformedData;
  }, [execute]);

  return {
    cardArt: data,
    isLoading,
    isError,
    error,
    loadCardArt
  };
}

/**
 * Hook for monster templates
 * Component controls when to load via loadTemplates function
 */
export function useMonsterTemplates() {
  const { data, isLoading, isError, error, execute } = useApi(monstersApi.getMonsterTemplates);

  /**
   * Load available monster templates
   * @returns {Promise<object>} Transformed templates object
   */
  const loadTemplates = useCallback(async () => {
    console.log('📝 Loading monster templates');
    const rawData = await execute();
    
    // Apply transformation explicitly
    const transformedData = transformMonsterTemplates(rawData);
    return transformedData;
  }, [execute]);

  return {
    templates: data || {},
    isLoading,
    isError,
    error,
    loadTemplates
  };
}

/**
 * Hook for monster generation (mutation)
 * Component controls when to generate via generate function
 */
export function useMonsterGeneration() {
  const { data, isLoading, isError, error, execute } = useApi(monstersApi.generateMonster);

  /**
   * Generate a new monster
   * @param {object} options - Generation options
   * @returns {Promise<object>} Transformed generation result
   */
  const generate = useCallback(async (options = {}) => {
    const generationOptions = {
      prompt_name: 'detailed_monster',
      generate_card_art: true,
      ...options
    };
    
    console.log('✨ Generating monster with options:', generationOptions);
    const rawData = await execute(generationOptions);
    
    // Apply transformation explicitly
    const transformedData = transformMonsterGeneration(rawData);
    return transformedData;
  }, [execute]);

  return {
    generationResult: data,
    monster: data?.monster || null,
    isGenerating: isLoading,
    isError,
    error,
    generate
  };
}

/**
 * Hook for ability generation (mutation)
 * Component controls when to generate via generate function
 */
export function useAbilityGeneration() {
  const { data, isLoading, isError, error, execute } = useApi(monstersApi.generateAbility);

  /**
   * Generate an ability for specific monster
   * @param {number} monsterId - Monster ID to generate ability for
   * @param {object} options - Generation options
   * @returns {Promise<object>} Transformed ability generation result
   */
  const generate = useCallback(async (monsterId, options = {}) => {
    const generationOptions = {
      wait_for_completion: true,
      ...options
    };
    
    console.log('⚡ Generating ability for monster:', monsterId, 'with options:', generationOptions);
    const rawData = await execute(monsterId, generationOptions);
    
    // Apply transformation explicitly
    const transformedData = transformAbilityGeneration(rawData);
    return transformedData;
  }, [execute]);

  return {
    generationResult: data,
    ability: data?.ability || null,
    isGenerating: isLoading,
    isError,
    error,
    generate
  };
}

/**
 * Hook for card art generation (mutation)
 * Component controls when to generate via generate function
 */
export function useCardArtGeneration() {
  const { data, isLoading, isError, error, execute } = useApi(monstersApi.generateCardArt);

  /**
   * Generate card art for specific monster
   * @param {number} monsterId - Monster ID to generate card art for
   * @param {object} options - Generation options
   * @returns {Promise<object>} Raw generation result
   */
  const generate = useCallback(async (monsterId, options = {}) => {
    console.log('🎨 Generating card art for monster:', monsterId);
    const rawData = await execute(monsterId, options);
    return rawData;
  }, [execute]);

  return {
    generationResult: data,
    isGenerating: isLoading,
    isError,
    error,
    generate
  };
}

/**
 * Comprehensive hook that provides multiple monster operations
 * Components can use individual hooks or this combined one based on needs
 */
export function useMonsters() {
  const collection = useMonsterCollection();
  const individual = useMonster();
  const stats = useMonsterStats();
  const abilities = useMonsterAbilities();
  const cardArt = useMonsterCardArt();
  const templates = useMonsterTemplates();
  const generation = useMonsterGeneration();
  const abilityGeneration = useAbilityGeneration();
  const cardArtGeneration = useCardArtGeneration();

  return {
    // Individual hook instances
    collection,
    individual,
    stats,
    abilities,
    cardArt,
    templates,
    generation,
    abilityGeneration,
    cardArtGeneration,
    
    // Helper function to load initial data
    loadInitialData: useCallback(async () => {
      await Promise.all([
        collection.loadMonsters({ limit: 12 }),
        stats.loadStats('all'),
        templates.loadTemplates()
      ]);
    }, [collection, stats, templates])
  };
}