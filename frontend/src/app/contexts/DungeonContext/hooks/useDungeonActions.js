// useDungeonActions.js - Actions for the dungeon exploration loop
// Uses existing app hooks for API calls to maintain consistency
// Actions prepare local state (clearing stale data), queue the workflow,
// and let useDungeonEvents pick up the results via SSE

import { useCallback, useEffect } from 'react';
import {
  useExpeditionNotices,
  useEnterDungeon,
  useChoosePath,
  useRespondToMonster,
  useSneakPast,
  useSurpriseAttack,
  useSetupCamp,
  useDungeonAbility,
  useDungeonItem,
  useContinueExploring,
} from '../../../hooks/useDungeon.js';

/**
 * Hook for managing dungeon actions
 * @param {object} stateHook - State hook from useDungeonState
 * @returns {object} Action functions
 */
export function useDungeonActions(stateHook) {
  const { setters, resetState } = stateHook;

  const {
    setErrorState,
    setNotices,
    setIsGeneratingNotices,
    setExpedition,
    setGoal,
    setGoalReward,
    setCurrentLocation,
    setPaths,
    setArePathsReady,
    setDialogue,
    setIsMonsterResponding,
    setIsSneaking,
    setIsAmbushing,
    setIsCamping,
    setIsUsingAbility,
    setAbilityResult,
    setIsUsingItem,
    setItemResult,
    setExitText,
    clearEncounter,
  } = setters;

  // App hooks for the API calls
  const noticesApi = useExpeditionNotices();
  const enterApi = useEnterDungeon();
  const choosePathApi = useChoosePath();
  const respondApi = useRespondToMonster();
  const sneakApi = useSneakPast();
  const surpriseApi = useSurpriseAttack();
  const campApi = useSetupCamp();
  const abilityApi = useDungeonAbility();
  const itemApi = useDungeonItem();
  const continueApi = useContinueExploring();

  // Sync API hook errors with context state
  useEffect(() => {
    const apiError =
      (noticesApi.isError && noticesApi.error) ||
      (enterApi.isError && enterApi.error) ||
      (choosePathApi.isError && choosePathApi.error) ||
      (respondApi.isError && respondApi.error) ||
      (sneakApi.isError && sneakApi.error) ||
      (surpriseApi.isError && surpriseApi.error) ||
      (campApi.isError && campApi.error) ||
      (abilityApi.isError && abilityApi.error) ||
      (continueApi.isError && continueApi.error);

    if (apiError) {
      setErrorState(apiError?.message || 'Dungeon request failed');
      // Don't leave any action stuck on "waiting"
      setIsGeneratingNotices(false);
      setIsMonsterResponding(false);
      setIsSneaking(false);
      setIsAmbushing(false);
      setIsCamping(false);
      setIsUsingAbility(false);
    }
  }, [
    noticesApi.isError,
    noticesApi.error,
    enterApi.isError,
    enterApi.error,
    choosePathApi.isError,
    choosePathApi.error,
    respondApi.isError,
    respondApi.error,
    sneakApi.isError,
    sneakApi.error,
    surpriseApi.isError,
    surpriseApi.error,
    campApi.isError,
    campApi.error,
    abilityApi.isError,
    abilityApi.error,
    continueApi.isError,
    continueApi.error,
    setErrorState,
    setIsGeneratingNotices,
    setIsMonsterResponding,
    setIsSneaking,
    setIsAmbushing,
    setIsCamping,
    setIsUsingAbility,
  ]);

  // Ask the entrance board for fresh expedition notices to pick from
  const requestNotices = useCallback(async () => {
    if (noticesApi.isLoading) {
      return;
    }

    setErrorState(null);
    setNotices(null);
    setIsGeneratingNotices(true);
    await noticesApi.generateNotices();
  }, [
    noticesApi.isLoading,
    noticesApi.generateNotices,
    setErrorState,
    setNotices,
    setIsGeneratingNotices,
  ]);

  // Enter dungeon action - a fresh run starts clean, so any leftover
  // state from a previous run is dropped before the workflow queues.
  // Answering a notice (noticeId) makes it a themed expedition.
  const enterDungeon = useCallback(
    async (noticeId) => {
      if (enterApi.isLoading) {
        return;
      }

      setErrorState(null);
      clearEncounter();
      setExpedition(null);
      setGoal(null);
      setGoalReward(null);
      setExitText(null);
      setCurrentLocation(null);
      setPaths(null);
      setArePathsReady(false);
      await enterApi.enterDungeon(noticeId);
    },
    [
      enterApi.isLoading,
      enterApi.enterDungeon,
      setErrorState,
      clearEncounter,
      setExpedition,
      setGoal,
      setGoalReward,
      setExitText,
      setCurrentLocation,
      setPaths,
      setArePathsReady,
    ],
  );

  // Take a path - clear everything from the previous junction first
  const choosePath = useCallback(
    async (pathId) => {
      if (choosePathApi.isLoading) {
        return;
      }

      setErrorState(null);
      clearEncounter();
      setExitText(null);
      setCurrentLocation(null); // traveling... until location_generated arrives
      setPaths(null);
      setArePathsReady(false);
      await choosePathApi.choosePath(pathId);
    },
    [
      choosePathApi.isLoading,
      choosePathApi.choosePath,
      setErrorState,
      clearEncounter,
      setExitText,
      setCurrentLocation,
      setPaths,
      setArePathsReady,
    ],
  );

  // Speak to the encounter monsters - the party's words appear
  // immediately; the monster's response (and its decision) arrive via SSE
  const respondToMonster = useCallback(
    async (message) => {
      if (respondApi.isLoading) {
        return;
      }

      setErrorState(null);
      setIsMonsterResponding(true);
      setDialogue((prev) => [...prev, { speaker: 'The party', text: message }]);
      await respondApi.respondToMonster(message);
    },
    [
      respondApi.isLoading,
      respondApi.respondToMonster,
      setErrorState,
      setIsMonsterResponding,
      setDialogue,
    ],
  );

  // Try to slip past the monsters spotted while exploring
  const sneakPast = useCallback(async () => {
    if (sneakApi.isLoading) {
      return;
    }

    setErrorState(null);
    setIsSneaking(true);
    await sneakApi.sneakPast();
  }, [sneakApi.isLoading, sneakApi.sneakPast, setErrorState, setIsSneaking]);

  // Strike first at the monsters spotted while exploring
  const surpriseAttack = useCallback(async () => {
    if (surpriseApi.isLoading) {
      return;
    }

    setErrorState(null);
    setIsAmbushing(true);
    await surpriseApi.surpriseAttack();
  }, [surpriseApi.isLoading, surpriseApi.surpriseAttack, setErrorState, setIsAmbushing]);

  // Set up camp in a monster-free location
  const setupCamp = useCallback(async () => {
    if (campApi.isLoading) {
      return;
    }

    setErrorState(null);
    setIsCamping(true);
    await campApi.setupCamp();
  }, [campApi.isLoading, campApi.setupCamp, setErrorState, setIsCamping]);

  // A party monster uses an ability on anything - the LLM decides
  // whether it does anything at all
  const activateAbility = useCallback(
    async ({ monsterId, abilityId, targetType, targetId, targetText }) => {
      if (abilityApi.isLoading) {
        return;
      }

      setErrorState(null);
      setIsUsingAbility(true);
      setAbilityResult(null);
      await abilityApi.activateAbility({ monsterId, abilityId, targetType, targetId, targetText });
    },
    [
      abilityApi.isLoading,
      abilityApi.activateAbility,
      setErrorState,
      setIsUsingAbility,
      setAbilityResult,
    ],
  );

  // The party uses an inventory item on anything - the LLM reads the
  // item's description and decides what actually happens
  const activateItem = useCallback(
    async ({ itemId, targetType, targetId, targetText }) => {
      if (itemApi.isLoading) {
        return;
      }

      setErrorState(null);
      setIsUsingItem(true);
      setItemResult(null);
      await itemApi.activateItem({ itemId, targetType, targetId, targetText });
    },
    [itemApi.isLoading, itemApi.activateItem, setErrorState, setIsUsingItem, setItemResult],
  );

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
  }, [
    continueApi.isLoading,
    continueApi.continueExploring,
    setErrorState,
    clearEncounter,
    setExitText,
    setPaths,
    setArePathsReady,
  ]);

  // Reset dungeon state
  const resetDungeon = useCallback(() => {
    resetState();
  }, [resetState]);

  return {
    actions: {
      requestNotices,
      enterDungeon,
      choosePath,
      respondToMonster,
      sneakPast,
      surpriseAttack,
      setupCamp,
      activateAbility,
      activateItem,
      continueExploring,
      resetDungeon,
    },
  };
}
