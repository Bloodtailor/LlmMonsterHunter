// Game State Hooks - Individual hooks matching the useMonsters.js pattern
// 1-to-1 with backend routes, using useAsyncState + useMemo transformations

import { useAsyncState } from '../../shared/hooks/useAsyncState.js';
import * as gameStateApi from '../../api/services/gameState.js';

/**
 * Hook for following monsters (player collection)
 */
export function useFollowingMonsters() {
  // ✨ Automatically uses getFollowingMonsters.defaults
  const api = useAsyncState(gameStateApi.getFollowingMonsters);

  return {
    // Clean transformed data
    ids: api.data.ids,                           // Always an array
    count: api.data.count,                       // Always a number
    followingMonsters: api.data.followingMonsters, // Always an array

    // Raw data (for debugging)
    rawResponse: api.data._raw,

    // State flags
    isLoading: api.isLoading,
    isError: api.isError,
    error: api.error,

    // Actions
    getFollowingMonsters: api.execute,
    reset: api.reset,

    // Computed helpers
    hasFollowing: api.data.count > 0,
    isEmpty: api.data.count === 0
  };
}

/**
 * Hook for active party management
 */
export function useActiveParty() {
  // ✨ Automatically uses getActiveParty.defaults
  const api = useAsyncState(gameStateApi.getActiveParty);

  return {
    // Clean transformed data
    ids: api.data.ids,                     // Always an array
    count: api.data.count,                 // Always a number
    partyMonsters: api.data.partyMonsters, // Always an array

    // Raw data (for debugging)
    rawResponse: api.data._raw,

    // State flags
    isLoading: api.isLoading,
    isError: api.isError,
    error: api.error,

    // Actions
    getActiveParty: api.execute,
    reset: api.reset,

    // Computed helpers
    hasParty: api.data.count > 0,
    isEmpty: api.data.count === 0,
    isFull: api.data.count >= 4
  };
}

/**
 * Hook for setting active party
 */
export function useSetActiveParty() {
  // ✨ Automatically uses setActiveParty.defaults
  const api = useAsyncState(gameStateApi.setActiveParty);

  return {
    // Clean set result
    success: api.data.success,           // false initially, then boolean
    message: api.data.message,           // null initially, then string
    partyCount: api.data.partyCount,     // 0 initially, then number
    partyIds: api.data.partyIds,         // [] initially, then array

    // Raw data (for debugging)
    rawResponse: api.data._raw,

    // State flags
    isSetting: api.isLoading,
    isError: api.isError,
    error: api.error,

    // Actions
    setActiveParty: api.execute,
    reset: api.reset
  };
}