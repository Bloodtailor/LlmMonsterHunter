// useDungeonActions.js - Actions for the dungeon exploration loop
// Uses existing app hooks for API calls to maintain consistency
// Actions prepare local state (clearing stale data), queue the workflow,
// and let useDungeonEvents pick up the results via SSE

import { useCallback, useEffect } from 'react';
import {
  useEnterDungeon,
  useChoosePath,
  useAnswerRiddle,
  useContinueExploring
} from '../../../hooks/useDungeon.js';

/**
 * Hook for managing dungeon actions
 * @param {object} stateHook - State hook from useDungeonState
 * @returns {object} Action functions
 */
export function useDungeonActions(stateHook) {
  const {
    setters,
    resetState
  } = stateHook;

  const {
    setErrorState,
    setCurrentLocation,
    setPaths,
    setArePathsReady,
    setIsJudgingAnswer,
    setExitText,
    clearEncounter
  } = setters;

  // App hooks for the API calls
  const enterApi = useEnterDungeon();
  const choosePathApi = useChoosePath();
  const answerRiddleApi = useAnswerRiddle();
  const continueApi = useContinueExploring();

  // Sync API hook errors with context state
  useEffect(() => {
    const apiError =
      (enterApi.isError && enterApi.error) ||
      (choosePathApi.isError && choosePathApi.error) ||
      (answerRiddleApi.isError && answerRiddleApi.error) ||
      (continueApi.isError && continueApi.error);

    if (apiError) {
      setErrorState(apiError?.message || 'Dungeon request failed');
      setIsJudgingAnswer(false); // don't leave the riddle stuck on "judging"
    }
  }, [
    enterApi.isError, enterApi.error,
    choosePathApi.isError, choosePathApi.error,
    answerRiddleApi.isError, answerRiddleApi.error,
    continueApi.isError, continueApi.error,
    setErrorState, setIsJudgingAnswer
  ]);

  // Enter dungeon action
  const enterDungeon = useCallback(async () => {
    if (enterApi.isLoading) {
      return;
    }

    setErrorState(null);
    await enterApi.enterDungeon();
  }, [enterApi.isLoading, enterApi.enterDungeon, setErrorState]);

  // Take a path - clear everything from the previous junction first
  const choosePath = useCallback(async (pathId) => {
    if (choosePathApi.isLoading) {
      return;
    }

    setErrorState(null);
    clearEncounter();
    setExitText(null);
    setCurrentLocation(null);   // traveling... until location_generated arrives
    setPaths(null);
    setArePathsReady(false);
    await choosePathApi.choosePath(pathId);
  }, [choosePathApi.isLoading, choosePathApi.choosePath, setErrorState, clearEncounter, setExitText, setCurrentLocation, setPaths, setArePathsReady]);

  // Answer the active riddle
  const answerRiddle = useCallback(async (answer) => {
    if (answerRiddleApi.isLoading) {
      return;
    }

    setErrorState(null);
    setIsJudgingAnswer(true);
    await answerRiddleApi.answerRiddle(answer);
  }, [answerRiddleApi.isLoading, answerRiddleApi.answerRiddle, setErrorState, setIsJudgingAnswer]);

  // Continue exploring - fresh paths from the current location
  const continueExploring = useCallback(async () => {
    if (continueApi.isLoading) {
      return;
    }

    setErrorState(null);
    clearEncounter();
    setExitText(null);
    setPaths(null);
    setArePathsReady(false);
    await continueApi.continueExploring();
  }, [continueApi.isLoading, continueApi.continueExploring, setErrorState, clearEncounter, setExitText, setPaths, setArePathsReady]);

  // Reset dungeon state
  const resetDungeon = useCallback(() => {
    resetState();
  }, [resetState]);

  return {
    actions: {
      enterDungeon,
      choosePath,
      answerRiddle,
      continueExploring,
      resetDungeon
    }
  };
}
