// useDungeonState.js - State for the dungeon exploration loop
// Business-focused state: what do components actually need to know?
// Screens render by data presence (location set? riddle set? exit text set?)
// rather than a separate phase machine - less state to get out of sync

import { useState, useCallback } from 'react';

/**
 * Hook for managing dungeon state
 * Focused on business logic rather than technical loading states
 * @returns {object} State values, setters, and reset function
 */
export function useDungeonState() {

  // Error state - for critical errors that "crash" the game
  const [isError, setIsError] = useState(false);
  const [error, setError] = useState(null);

  // Entry text streaming (dungeon entrance)
  const [entryText, setEntryText] = useState('');

  // Where the party currently is
  const [currentLocation, setCurrentLocation] = useState(null);

  // Paths onward - for the paths screen (events are hidden backend-side)
  const [paths, setPaths] = useState(null);
  const [arePathsReady, setArePathsReady] = useState(false);

  // Encounter state - streamed vanity text, the monsters, and the riddle
  const [encounterText, setEncounterText] = useState('');
  const [encounterMonsters, setEncounterMonsters] = useState([]); // battles can reveal several
  const [riddleGreeting, setRiddleGreeting] = useState(null); // the monster's in-character justification
  const [riddle, setRiddle] = useState(null);
  const [isJudgingAnswer, setIsJudgingAnswer] = useState(false);
  const [riddleResult, setRiddleResult] = useState(null); // { correct, response } - the monster's spoken reaction

  // Exit state - set when the party takes an exit path
  const [exitText, setExitText] = useState(null);

  // Helper to set error state
  const setErrorState = useCallback((errorMessage) => {
    setIsError(!!errorMessage);
    setError(errorMessage);
  }, []);

  // Clear everything tied to a single junction/encounter
  // (used when taking a new path or continuing exploration)
  const clearEncounter = useCallback(() => {
    setEncounterText('');
    setEncounterMonsters([]);
    setRiddleGreeting(null);
    setRiddle(null);
    setIsJudgingAnswer(false);
    setRiddleResult(null);
  }, []);

  // Reset all state to initial values
  const resetState = useCallback(() => {
    setIsError(false);
    setError(null);
    setEntryText('');
    setCurrentLocation(null);
    setPaths(null);
    setArePathsReady(false);
    setEncounterText('');
    setEncounterMonsters([]);
    setRiddleGreeting(null);
    setRiddle(null);
    setIsJudgingAnswer(false);
    setRiddleResult(null);
    setExitText(null);
  }, []);

  return {
    // Public state (for spreading in provider)
    state: {
      isError,
      error,
      entryText,
      currentLocation,
      paths,
      arePathsReady,
      encounterText,
      encounterMonsters,
      riddleGreeting,
      riddle,
      isJudgingAnswer,
      riddleResult,
      exitText
    },

    // Internal setters (for other hooks)
    setters: {
      setErrorState,
      setEntryText,
      setCurrentLocation,
      setPaths,
      setArePathsReady,
      setEncounterText,
      setEncounterMonsters,
      setRiddleGreeting,
      setRiddle,
      setIsJudgingAnswer,
      setRiddleResult,
      setExitText,
      clearEncounter
    },

    // Utilities
    resetState
  };
}
