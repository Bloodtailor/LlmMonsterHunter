// useBattleEvents.js - SSE event processing for turn-based battles
// Queues turn narrations for click-through as the backend resolves them
// (the backend runs ahead; the player reads at their own pace)

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
    setPendingActorId,
    setPendingActorName,
    setPendingTalk,
    setPendingNarrations,
    setCurrentNarration,
    setTurnResult,
    setIsProcessing,
    setBattleError
  } = setters;

  // A battle begins. Several dungeon moments can start one:
  //   choose_path        - hostile monsters attack on arrival
  //   respond_to_monster - a conversation turned hostile (begin_battle)
  //   sneak_past         - the party was noticed
  //   surprise_attack    - the party struck first
  // They all return a battle_snapshot + battle_intro on completion.
  const BATTLE_STARTING_WORKFLOWS = ['choose_path', 'respond_to_monster', 'sneak_past', 'surprise_attack'];

  useEventSubscription('workflowCompleted', (eventData) => {
    const workflowType = eventData?.workflowItem?.workflowType;
    const result = eventData?.result;
    if (!result?.success) return;

    if (BATTLE_STARTING_WORKFLOWS.includes(workflowType) && result.battle_snapshot?.in_battle) {
      setBattleIntro(result.battle_intro || null);
      setDisplayedBattle(result.battle_snapshot || null);
      return;
    }

    // A battle_turn call finished backend-side. The player may still be
    // clicking through narrations - hold the result; advanceLog applies
    // it when the story catches up
    if (workflowType === 'battle_turn') {
      setTurnResult(result);
      // Nothing to click through (e.g. instant hand-off to an ally turn)?
      // The actions hook's advanceLog effect will consume it.
    }
  });

  // Each resolved turn arrives as a workflow update
  useEventSubscription('workflowUpdate', (eventData) => {
    if (eventData?.step !== 'action_resolved') return;
    const actionResult = eventData.data?.action_result;
    if (!actionResult) return;

    // First narration shows immediately; the rest queue up
    if (!state.currentNarration) {
      setCurrentNarration(actionResult);
      if (actionResult.battle_snapshot) {
        setDisplayedBattle(prev => ({ ...prev, ...actionResult.battle_snapshot }));
      }
    } else {
      setPendingNarrations(prev => [...prev, actionResult]);
    }
  });

  // A failed battle turn should not strand the player mid-processing
  // (the backend restores the awaiting phase for retry)
  useEventSubscription('workflowFailed', (eventData) => {
    if (eventData?.workflowItem?.workflowType !== 'battle_turn') return;
    // Keep pendingActor/pendingTalk so the player can retry their input
    setIsProcessing(false);
    setCurrentNarration(null);
    setPendingNarrations([]);
    setTurnResult(null);
    const error = typeof eventData?.error === 'string' ? eventData.error : 'The battle turn failed - try again';
    setBattleError(error);
  });

  // This hook only provides side effects, no return value
}
