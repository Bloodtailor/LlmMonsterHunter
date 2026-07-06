// useBattleActions.js - Actions for the turn-based battle system
// Turn selection, executing turns, replying to enemy talk, and
// advancing the click-through battle log

import { useCallback, useEffect } from 'react';
import { useTakeTurn, useRespondToTalk } from '../../../hooks/useBattle.js';

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
    setPendingActorId,
    setPendingActorName,
    setPendingTalk,
    setCurrentSelection,
    setIsProcessing,
    setPendingNarrations,
    setCurrentNarration,
    setTurnResult,
    setOutcome,
    setResolution,
    setOutcomeText,
    setJoinedNames,
    setBattleError
  } = setters;

  const turnApi = useTakeTurn();
  const respondApi = useRespondToTalk();

  // Sync API errors into battle state
  useEffect(() => {
    const apiError = (turnApi.isError && turnApi.error) || (respondApi.isError && respondApi.error);
    if (apiError) {
      setBattleError(apiError?.message || 'Battle request failed');
      setIsProcessing(false);
    }
  }, [turnApi.isError, turnApi.error, respondApi.isError, respondApi.error, setBattleError, setIsProcessing]);

  // Apply a completed turn's result: whose turn is next, an enemy's
  // words awaiting reply, or the battle's outcome
  const applyTurnResult = useCallback((result) => {
    if (result.battle_snapshot) {
      setDisplayedBattle(result.battle_snapshot);
    }

    if (result.pending === 'player_turn') {
      setPendingActorId(String(result.pending_actor));
      setPendingActorName(result.pending_actor_name || null);
      setCurrentSelection({});
    } else if (result.pending === 'player_response') {
      setPendingTalk({
        speakerName: result.pending_talk?.speaker_name || 'The enemy',
        dialogue: result.pending_talk?.dialogue || ''
      });
    } else if (result.outcome && result.outcome !== 'unresolved') {
      setOutcome(result.outcome);
      setResolution(result.resolution || 'combat');
      setOutcomeText(result.outcome_text || '');
      setJoinedNames(result.joined_names || []);
    }

    setTurnResult(null);
    setCurrentNarration(null);
    setIsProcessing(false);
  }, [
    setDisplayedBattle, setPendingActorId, setPendingActorName, setPendingTalk,
    setCurrentSelection, setOutcome, setResolution, setOutcomeText, setJoinedNames,
    setTurnResult, setCurrentNarration, setIsProcessing
  ]);

  // Some turns have nothing to click through (e.g. opening initiative
  // landing straight on an ally's turn) - consume the result directly
  useEffect(() => {
    if (state.turnResult && !state.currentNarration && state.pendingNarrations.length === 0) {
      applyTurnResult(state.turnResult);
    }
  }, [state.turnResult, state.currentNarration, state.pendingNarrations, applyTurnResult]);

  // Begin the battle: opening initiative (no player action yet)
  const beginBattle = useCallback(async () => {
    if (turnApi.isLoading || state.isProcessing) return;
    setBattleError(null);
    setIsProcessing(true);
    await turnApi.takeTurn(null);
  }, [turnApi.isLoading, turnApi.takeTurn, state.isProcessing, setBattleError, setIsProcessing]);

  // Update the in-progress selection for the pending monster's turn
  const updateSelection = useCallback((patch) => {
    setCurrentSelection(prev => ({ ...prev, ...patch }));
  }, [setCurrentSelection]);

  // Execute the pending monster's turn
  const executeTurn = useCallback(async () => {
    if (turnApi.isLoading || state.isProcessing) return;

    const selection = state.currentSelection;
    const action = {
      type: selection.type,
      ability_id: selection.abilityId ?? null,
      target_id: selection.targetId ?? null,
      text: selection.text ?? null,
      info: selection.info ?? null
    };

    setBattleError(null);
    setPendingNarrations([]);
    setCurrentNarration(null);
    setTurnResult(null);
    setPendingActorId(null);
    setPendingActorName(null);
    setIsProcessing(true);

    const result = await turnApi.takeTurn(action);
    if (result && result.success === false) {
      setIsProcessing(false);
    }
  }, [
    turnApi.isLoading, turnApi.takeTurn, state.isProcessing, state.currentSelection,
    setBattleError, setPendingNarrations, setCurrentNarration, setTurnResult,
    setPendingActorId, setPendingActorName, setIsProcessing
  ]);

  // Reply to an enemy's battlefield talk
  const respondToTalk = useCallback(async (text) => {
    if (respondApi.isLoading || state.isProcessing) return;

    setBattleError(null);
    setPendingNarrations([]);
    setCurrentNarration(null);
    setTurnResult(null);
    setPendingTalk(null);
    setIsProcessing(true);

    const result = await respondApi.respondToTalk(text);
    if (result && result.success === false) {
      setIsProcessing(false);
    }
  }, [
    respondApi.isLoading, respondApi.respondToTalk, state.isProcessing,
    setBattleError, setPendingNarrations, setCurrentNarration, setTurnResult,
    setPendingTalk, setIsProcessing
  ]);

  // The "Next" button: reveal the next narration, or apply the turn's
  // result when the story has caught up with the backend
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

    if (state.turnResult) {
      applyTurnResult(state.turnResult);
    }
  }, [state.pendingNarrations, state.turnResult, setPendingNarrations, setCurrentNarration, setDisplayedBattle, applyTurnResult]);

  // Leave the battle behind (after victory continue / defeat return home)
  const resetBattle = useCallback(() => {
    resetState();
  }, [resetState]);

  return {
    actions: {
      beginBattle,
      updateSelection,
      executeTurn,
      respondToTalk,
      advanceLog,
      resetBattle
    }
  };
}
