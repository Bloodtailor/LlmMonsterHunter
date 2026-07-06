// useBattleActions.js - Actions for the battle system
// Action selection, executing the round, and advancing the battle log

import { useCallback, useEffect } from 'react';
import { useSubmitRound } from '../../../hooks/useBattle.js';

/**
 * Hook for managing battle actions
 * @param {object} stateHook - State hook from useBattleState
 * @returns {object} Action functions
 */
export function useBattleActions(stateHook) {
  const {
    state,
    setters,
    resetState
  } = stateHook;

  const {
    setDisplayedBattle,
    setSelectedActions,
    setIsProcessing,
    setPendingNarrations,
    setCurrentNarration,
    setRoundComplete,
    setBattleError
  } = setters;

  const submitApi = useSubmitRound();

  // Sync API errors into battle state
  useEffect(() => {
    if (submitApi.isError) {
      setBattleError(submitApi.error?.message || 'Failed to submit the round');
      setIsProcessing(false);
    }
  }, [submitApi.isError, submitApi.error, setBattleError, setIsProcessing]);

  // Select one monster's action for this round
  const setMonsterAction = useCallback((monsterId, action) => {
    setSelectedActions(prev => ({ ...prev, [monsterId]: action }));
  }, [setSelectedActions]);

  // Execute the round - after this the player can't change anything
  const executeRound = useCallback(async () => {
    if (submitApi.isLoading || state.isProcessing) return;

    const actions = Object.entries(state.selectedActions).map(([monsterId, selection]) => ({
      monster_id: monsterId,
      action: selection.action,
      ability_id: selection.abilityId ?? null,
      target_id: selection.targetId ?? null
    }));

    setBattleError(null);
    setPendingNarrations([]);
    setCurrentNarration(null);
    setRoundComplete(false);
    setIsProcessing(true);

    const result = await submitApi.submitRound(actions);
    if (result && result.success === false) {
      setIsProcessing(false);
    }
  }, [
    submitApi.isLoading, submitApi.submitRound, state.isProcessing, state.selectedActions,
    setBattleError, setPendingNarrations, setCurrentNarration, setRoundComplete, setIsProcessing
  ]);

  // The "Next" button: reveal the next narration, or finish the round
  // when the story has caught up with the backend
  const advanceLog = useCallback(() => {
    if (state.pendingNarrations.length > 0) {
      const [next, ...rest] = state.pendingNarrations;
      setPendingNarrations(rest);
      setCurrentNarration(next);
      if (next.battle_snapshot) {
        setDisplayedBattle(prev => ({ ...prev, ...next.battle_snapshot }));
      }
      return;
    }

    // Nothing queued - if the backend finished, close out the round
    if (state.roundComplete) {
      setIsProcessing(false);
      setCurrentNarration(null);
      setRoundComplete(false);
      setSelectedActions({});
      // Outcome (if any) is already in state - the outcome view takes over.
      // Otherwise the displayed battle moves to the new selection round.
      setDisplayedBattle(prev => prev ? { ...prev, phase: state.outcome ? state.outcome : 'selecting', round: (prev.round || 1) + (state.outcome ? 0 : 1) } : prev);
    }
  }, [
    state.pendingNarrations, state.roundComplete, state.outcome,
    setPendingNarrations, setCurrentNarration, setDisplayedBattle,
    setIsProcessing, setRoundComplete, setSelectedActions
  ]);

  // Leave the battle behind (after victory continue / defeat return home)
  const resetBattle = useCallback(() => {
    resetState();
  }, [resetState]);

  return {
    actions: {
      setMonsterAction,
      executeRound,
      advanceLog,
      resetBattle
    }
  };
}
