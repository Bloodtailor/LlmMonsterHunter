// Game State Hooks - Individual hooks matching the useMonsters.js pattern
// 1-to-1 with backend routes, using useAsyncState + useMemo transformations

import { useCallback, useMemo } from 'react';
import { useAsyncState } from '../../shared/hooks/useAsyncState.js';
import * as gameStateApi from '../../api/services/gameState.js';

/**
 * Hook for /api/game-state/following
 */
export function useFollowingMonsters() {
  const asyncState = useAsyncState();

  const getFollowingMonsters = useCallback(async () => {
    await asyncState.execute(gameStateApi.getFollowingMonsters);
  }, [asyncState.execute]);

  // Transform raw data when it changes
  const followingData = useMemo(() => {
    if (!asyncState.data) {
      return { ids: [], count: 0 };
    }
    
    return {
      ids: asyncState.data.following_monsters?.ids || [],
      count: asyncState.data.following_monsters?.count || 0
    };
  }, [asyncState.data]);

  return {
    ...followingData,
    rawResponse: asyncState.data,
    isLoading: asyncState.isLoading,
    isError: asyncState.isError,
    error: asyncState.error,
    getFollowingMonsters
  };
}

/**
 * Hook for /api/game-state/party
 */
export function useActiveParty() {
  const asyncState = useAsyncState();

  const getActiveParty = useCallback(async () => {
    await asyncState.execute(gameStateApi.getActiveParty);
  }, [asyncState.execute]);

  // Transform raw data when it changes
  const partyData = useMemo(() => {
    if (!asyncState.data) {
      return { ids: [], count: 0 };
    }
    
    return {
      ids: asyncState.data.active_party?.ids || [],
      count: asyncState.data.active_party?.count || 0
    };
  }, [asyncState.data]);

  return {
    ...partyData,
    rawResponse: asyncState.data,
    isLoading: asyncState.isLoading,
    isError: asyncState.isError,
    error: asyncState.error,
    getActiveParty
  };
}

/**
 * Hook for /api/game-state/party/ready
 */
export function usePartyReady() {
  const asyncState = useAsyncState();

  const checkPartyReady = useCallback(async () => {
    await asyncState.execute(gameStateApi.isPartyReady);
  }, [asyncState.execute]);

  // Transform raw data when it changes
  const partyReadyData = useMemo(() => {
    if (!asyncState.data) {
      return { ready: false, message: '' };
    }
    
    return {
      ready: asyncState.data.ready_for_dungeon || false,
      message: asyncState.data.message || ''
    };
  }, [asyncState.data]);

  return {
    ...partyReadyData,
    rawResponse: asyncState.data,
    isLoading: asyncState.isLoading,
    isError: asyncState.isError,
    error: asyncState.error,
    checkPartyReady
  };
}

/**
 * Hook for /api/game-state/following/add
 */
export function useAddMonsterToFollowing() {
  const asyncState = useAsyncState();

  const addMonsterToFollowing = useCallback(async (monsterId) => {
    await asyncState.execute(gameStateApi.addMonsterToFollowing, monsterId);
  }, [asyncState.execute]);

  // Transform raw data when it changes
  const addResult = useMemo(() => {
    if (!asyncState.data) {
      return { success: false, message: '', followingCount: 0 };
    }
    
    return {
      success: asyncState.data.success || false,
      message: asyncState.data.message || '',
      followingCount: asyncState.data.following_count || 0
    };
  }, [asyncState.data]);

  return {
    ...addResult,
    rawResponse: asyncState.data,
    isLoading: asyncState.isLoading,
    isError: asyncState.isError,
    error: asyncState.error,
    addMonsterToFollowing
  };
}

/**
 * Hook for /api/game-state/following/remove
 */
export function useRemoveMonsterFromFollowing() {
  const asyncState = useAsyncState();

  const removeMonsterFromFollowing = useCallback(async (monsterId) => {
    await asyncState.execute(gameStateApi.removeMonsterFromFollowing, monsterId);
  }, [asyncState.execute]);

  // Transform raw data when it changes
  const removeResult = useMemo(() => {
    if (!asyncState.data) {
      return { success: false, message: '', followingCount: 0, partyCount: 0 };
    }
    
    return {
      success: asyncState.data.success || false,
      message: asyncState.data.message || '',
      followingCount: asyncState.data.following_count || 0,
      partyCount: asyncState.data.party_count || 0
    };
  }, [asyncState.data]);

  return {
    ...removeResult,
    rawResponse: asyncState.data,
    isLoading: asyncState.isLoading,
    isError: asyncState.isError,
    error: asyncState.error,
    removeMonsterFromFollowing
  };
}

/**
 * Hook for /api/game-state/party/set
 */
export function useSetActiveParty() {
  const asyncState = useAsyncState();

  const setActiveParty = useCallback(async (monsterIds) => {
    await asyncState.execute(gameStateApi.setActiveParty, monsterIds);
  }, [asyncState.execute]);

  // Transform raw data when it changes
  const setPartyResult = useMemo(() => {
    if (!asyncState.data) {
      return { success: false, message: '', partyCount: 0, partyIds: [] };
    }
    
    return {
      success: asyncState.data.success || false,
      message: asyncState.data.message || '',
      partyCount: asyncState.data.active_party?.count || 0,
      partyIds: asyncState.data.active_party?.ids || []
    };
  }, [asyncState.data]);

  return {
    ...setPartyResult,
    rawResponse: asyncState.data,
    isLoading: asyncState.isLoading,
    isError: asyncState.isError,
    error: asyncState.error,
    setActiveParty
  };
}