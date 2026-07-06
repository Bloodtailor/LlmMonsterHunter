// useDungeonState.js - State for the dungeon exploration loop
// Business-focused state: what do components actually need to know?
// Screens render by data presence (location set? dialogue started? exit
// text set?) rather than a separate phase machine - less state to get
// out of sync

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

  // Encounter state - streamed vanity text and the revealed monsters
  const [encounterText, setEncounterText] = useState('');
  const [encounterMonsters, setEncounterMonsters] = useState([]); // battles can reveal several

  // Dialogue encounter - the conversation with the monster(s).
  // The LLM decides the outcome of every exchange:
  // null while talking; then 'begin_battle' | 'allow_passage' |
  // 'reward' | 'punish' | 'join_party' resolves the encounter
  const [dialogue, setDialogue] = useState([]); // [{ speaker, text }]
  const [isMonsterResponding, setIsMonsterResponding] = useState(false);
  const [dialogueOutcome, setDialogueOutcome] = useState(null); // { outcome, joinedNames }

  // Explore event - the party looks around and decides what to do
  const [monstersPresent, setMonstersPresent] = useState(null); // null until an explore event resolves it
  const [lookText, setLookText] = useState(''); // streamed look-around text
  const [sneakResult, setSneakResult] = useState(null); // { success, narration }
  const [isSneaking, setIsSneaking] = useState(false);
  const [isAmbushing, setIsAmbushing] = useState(false);

  // Camp - vanity dialogue between the party's monsters
  const [campText, setCampText] = useState(''); // streamed camp scene
  const [isCamping, setIsCamping] = useState(false);
  const [hasCamped, setHasCamped] = useState(false);

  // Party in the dungeon - conditions persist across the run, and any
  // monster can use its abilities on anything (the LLM referees it)
  const [partyConditions, setPartyConditions] = useState({}); // { monsterId: condition }
  const [isUsingAbility, setIsUsingAbility] = useState(false);
  const [abilityResult, setAbilityResult] = useState(null); // { narration, effect }

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
    setDialogue([]);
    setIsMonsterResponding(false);
    setDialogueOutcome(null);
    setMonstersPresent(null);
    setLookText('');
    setSneakResult(null);
    setIsSneaking(false);
    setIsAmbushing(false);
    setCampText('');
    setIsCamping(false);
    setHasCamped(false);
    setAbilityResult(null);
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
    setDialogue([]);
    setIsMonsterResponding(false);
    setDialogueOutcome(null);
    setMonstersPresent(null);
    setLookText('');
    setSneakResult(null);
    setIsSneaking(false);
    setIsAmbushing(false);
    setCampText('');
    setIsCamping(false);
    setHasCamped(false);
    setPartyConditions({});
    setIsUsingAbility(false);
    setAbilityResult(null);
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
      dialogue,
      isMonsterResponding,
      dialogueOutcome,
      monstersPresent,
      lookText,
      sneakResult,
      isSneaking,
      isAmbushing,
      campText,
      isCamping,
      hasCamped,
      partyConditions,
      isUsingAbility,
      abilityResult,
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
      setDialogue,
      setIsMonsterResponding,
      setDialogueOutcome,
      setMonstersPresent,
      setLookText,
      setSneakResult,
      setIsSneaking,
      setIsAmbushing,
      setCampText,
      setIsCamping,
      setHasCamped,
      setPartyConditions,
      setIsUsingAbility,
      setAbilityResult,
      setExitText,
      clearEncounter
    },

    // Utilities
    resetState
  };
}
