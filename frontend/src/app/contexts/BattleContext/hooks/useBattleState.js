// useBattleState.js - State for the turn-based battle system
// The battle snapshot shown to the player deliberately lags the backend:
// narrations are queued and revealed one at a time via "Next", and the
// turn's result (whose turn is next / enemy talk / the outcome) is
// applied only after the player has read everything

import { useState, useCallback } from 'react';

/**
 * Hook for managing battle state
 * @returns {object} State values, setters, and reset function
 */
export function useBattleState() {

  // The battle as the PLAYER currently sees it (lags backend on purpose)
  const [displayedBattle, setDisplayedBattle] = useState(null);

  // The enemies' opening challenge
  const [battleIntro, setBattleIntro] = useState(null);

  // Whose turn is it? (an ally awaiting the player's orders)
  const [pendingActorId, setPendingActorId] = useState(null);
  const [pendingActorName, setPendingActorName] = useState(null);

  // Streamed inner monologue for the acting monster - what it feels,
  // thinks, and wants (the player still decides the action)
  const [turnVanityText, setTurnVanityText] = useState('');

  // An enemy spoke - the player must respond
  const [pendingTalk, setPendingTalk] = useState(null); // { speakerName, dialogue }

  // The player's in-progress selection for the pending turn
  const [currentSelection, setCurrentSelection] = useState({}); // {type, abilityId, targetId, text, info}

  // Turn processing + the click-through narration queue
  const [isProcessing, setIsProcessing] = useState(false);
  const [pendingNarrations, setPendingNarrations] = useState([]);
  const [currentNarration, setCurrentNarration] = useState(null);

  // The completed turn's result, held until the story catches up
  const [turnResult, setTurnResult] = useState(null);

  // Battle end
  const [outcome, setOutcome] = useState(null);        // 'victory' | 'defeat'
  const [resolution, setResolution] = useState(null);  // 'combat'|'joined'|'yielded'|'fled'|'spared'
  const [outcomeText, setOutcomeText] = useState(null);
  const [joinedNames, setJoinedNames] = useState([]);  // monsters who joined the party
  const [victoryCocatok, setVictoryCocatok] = useState(null); // the minted keepsake (pickup ceremony)
  const [defeatReflection, setDefeatReflection] = useState(null); // the lesson the party carries out

  // Errors
  const [battleError, setBattleError] = useState(null);

  // Reset all state to initial values
  const resetState = useCallback(() => {
    setDisplayedBattle(null);
    setBattleIntro(null);
    setPendingActorId(null);
    setPendingActorName(null);
    setTurnVanityText('');
    setPendingTalk(null);
    setCurrentSelection({});
    setIsProcessing(false);
    setPendingNarrations([]);
    setCurrentNarration(null);
    setTurnResult(null);
    setOutcome(null);
    setResolution(null);
    setOutcomeText(null);
    setJoinedNames([]);
    setVictoryCocatok(null);
    setDefeatReflection(null);
    setBattleError(null);
  }, []);

  return {
    // Public state (for spreading in provider)
    state: {
      displayedBattle,
      battleIntro,
      pendingActorId,
      pendingActorName,
      turnVanityText,
      pendingTalk,
      currentSelection,
      isProcessing,
      pendingNarrations,
      currentNarration,
      turnResult,
      outcome,
      resolution,
      outcomeText,
      joinedNames,
      victoryCocatok,
      defeatReflection,
      battleError
    },

    // Internal setters (for other hooks)
    setters: {
      setDisplayedBattle,
      setBattleIntro,
      setPendingActorId,
      setPendingActorName,
      setTurnVanityText,
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
      setVictoryCocatok,
      setDefeatReflection,
      setBattleError
    },

    // Utilities
    resetState
  };
}
