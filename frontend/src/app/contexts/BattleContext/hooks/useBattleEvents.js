// useBattleEvents.js - SSE event processing for battles
// Queues action narrations for click-through as the backend's referee
// resolves them (the backend runs ahead; the player reads at their pace)

import { useEventSubscription } from '../../../../api/events/useEventSubscription.js';

/**
 * Hook for processing battle-related SSE events
 * @param {object} stateHook - State hook from useBattleState
 */
export function useBattleEvents(stateHook) {
  const {
    state,
    setters
  } = stateHook;

  const {
    setDisplayedBattle,
    setBattleIntro,
    setSelectedActions,
    setPendingNarrations,
    setCurrentNarration,
    setRoundComplete,
    setOutcome,
    setOutcomeText,
    setIsProcessing,
    setBattleError
  } = setters;

  // A battle begins: choose_path completed with a monster_battle event
  useEventSubscription('workflowCompleted', (eventData) => {
    const workflowType = eventData?.workflowItem?.workflowType;
    const result = eventData?.result;
    if (!result?.success) return;

    if (workflowType === 'choose_path' && result.event === 'monster_battle') {
      setBattleIntro(result.battle_intro || null);
      setDisplayedBattle(result.battle_snapshot || null);
      setSelectedActions({});
      setOutcome(null);
      setOutcomeText(null);
      return;
    }

    // A round finished processing backend-side. The player may still be
    // clicking through narrations - store the result; advanceLog applies
    // it when the story catches up
    if (workflowType === 'battle_round') {
      setRoundComplete(true);
      if (result.outcome && result.outcome !== 'unresolved') {
        setOutcome(result.outcome);
        setOutcomeText(result.outcome_text || '');
      }
    }
  });

  // Each referee resolution arrives as a workflow update
  useEventSubscription('workflowUpdate', (eventData) => {
    if (eventData?.step !== 'action_resolved') return;
    const actionResult = eventData.data?.action_result;
    if (!actionResult) return;

    // First narration of the round shows immediately; the rest queue up
    if (!state.currentNarration) {
      setCurrentNarration(actionResult);
      if (actionResult.battle_snapshot) {
        setDisplayedBattle(prev => ({ ...prev, ...actionResult.battle_snapshot }));
      }
    } else {
      setPendingNarrations(prev => [...prev, actionResult]);
    }
  });

  // A failed battle round should not strand the player mid-processing
  // (the backend already resets the battle phase to selecting)
  useEventSubscription('workflowFailed', (eventData) => {
    if (eventData?.workflowItem?.workflowType !== 'battle_round') return;
    setIsProcessing(false);
    setCurrentNarration(null);
    setPendingNarrations([]);
    setRoundComplete(false);
    const error = typeof eventData?.error === 'string' ? eventData.error : 'The battle round failed - try again';
    setBattleError(error);
  });

  // This hook only provides side effects, no return value
}
