// useDungeonActions.js - Minimal actions for dungeon workflow
// Uses existing app hooks for API calls to maintain consistency

import { useCallback, useEffect } from 'react';
import { useEnterDungeon } from '../../../hooks/useDungeon.js';

/**
 * Hook for managing minimal dungeon actions
 * Uses existing useEnterDungeon hook for consistency with other API patterns
 * @param {object} stateHook - State hook from useDungeonState
 * @returns {object} Action functions
 */
export function useDungeonActions(stateHook) {
  const {
    setters,
    resetState
  } = stateHook;

  const {
    setErrorState
  } = setters;

  // Use existing app hook for API call
  const {
    enterDungeon: enterDungeonApi,
    isLoading: isEnteringDungeon,
    isError: hasEnterError,
    error: enterError
  } = useEnterDungeon();

  // Sync API hook errors with context state
  useEffect(() => {
    if (hasEnterError) {
      setErrorState(enterError?.message || 'Failed to enter dungeon');
    }
  }, [hasEnterError, enterError, setErrorState]);

  // Enter dungeon action - uses app hook
  const enterDungeon = useCallback(async () => {
    if (isEnteringDungeon) {
      console.log('DungeonActions: Already entering dungeon, skipping');
      return;
    }

    console.log('DungeonActions: Starting dungeon entry workflow');
    setErrorState(null); // Clear any previous errors
    await enterDungeonApi();
  }, [isEnteringDungeon, enterDungeonApi, setErrorState]);

  // Reset dungeon state
  const resetDungeon = useCallback(() => {
    console.log('DungeonActions: Resetting dungeon state');
    resetState();
  }, [resetState]);

  return {
    actions: {
      enterDungeon,
      resetDungeon
    }
  };
}