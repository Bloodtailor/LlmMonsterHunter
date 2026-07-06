// useBattleState.js - State for the battle system
// The battle snapshot shown to the player deliberately lags the backend:
// narrations are queued and revealed one at a time via "Next", and the
// displayed conditions update with each revealed story beat

import { useState, useCallback } from 'react';

/**
 * Hook for managing battle state
 * @returns {object} State values, setters, and reset function
 */
export function useBattleState() {

  // The battle as the PLAYER currently sees it (lags backend on purpose)
  const [displayedBattle, setDisplayedBattle] = useState(null); // {allies, enemies, round, phase}

  // The enemies' opening challenge
  const [battleIntro, setBattleIntro] = useState(null);

  // Player action selection: { [monsterId]: {action, abilityId?, targetId?} }
  const [selectedActions, setSelectedActions] = useState({});

  // Round processing + the click-through narration queue
  const [isProcessing, setIsProcessing] = useState(false);
  const [pendingNarrations, setPendingNarrations] = useState([]); // queued action_results
  const [currentNarration, setCurrentNarration] = useState(null); // the one on screen

  // Battle end
  const [outcome, setOutcome] = useState(null);       // 'victory' | 'defeat'
  const [outcomeText, setOutcomeText] = useState(null);
  const [roundComplete, setRoundComplete] = useState(false); // backend finished the round

  // Errors
  const [battleError, setBattleError] = useState(null);

  // Reset all state to initial values
  const resetState = useCallback(() => {
    setDisplayedBattle(null);
    setBattleIntro(null);
    setSelectedActions({});
    setIsProcessing(false);
    setPendingNarrations([]);
    setCurrentNarration(null);
    setOutcome(null);
    setOutcomeText(null);
    setRoundComplete(false);
    setBattleError(null);
  }, []);

  return {
    // Public state (for spreading in provider)
    state: {
      displayedBattle,
      battleIntro,
      selectedActions,
      isProcessing,
      pendingNarrations,
      currentNarration,
      outcome,
      outcomeText,
      roundComplete,
      battleError
    },

    // Internal setters (for other hooks)
    setters: {
      setDisplayedBattle,
      setBattleIntro,
      setSelectedActions,
      setIsProcessing,
      setPendingNarrations,
      setCurrentNarration,
      setOutcome,
      setOutcomeText,
      setRoundComplete,
      setBattleError
    },

    // Utilities
    resetState
  };
}
