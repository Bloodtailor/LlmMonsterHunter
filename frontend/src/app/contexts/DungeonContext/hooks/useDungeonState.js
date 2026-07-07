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

  // Returning monster - a remembered creature crosses the party's path
  const [reunionText, setReunionText] = useState(''); // streamed recognition scene
  const [isReturningEncounter, setIsReturningEncounter] = useState(false);

  // Growth - reflections from camp spotlights and the exit ceremony
  // [{ monster_id, monster_name, reflection, stat, tier, new_ability, reworded_ability }]
  const [growthResults, setGrowthResults] = useState([]);

  // Party in the dungeon - conditions persist across the run, and any
  // monster can use its abilities on anything (the LLM referees it)
  const [partyConditions, setPartyConditions] = useState({}); // { monsterId: condition }

  // Stamina/mana word ladders - refill only on dungeon entry (and camp rest)
  const [partyResources, setPartyResources] = useState({}); // { monsterId: { stamina, mana } }
  const [isUsingAbility, setIsUsingAbility] = useState(false);
  const [abilityResult, setAbilityResult] = useState(null); // { narration, effect }

  // Inventory items - usable on anything like abilities (LLM referees it)
  const [isUsingItem, setIsUsingItem] = useState(false);
  const [itemResult, setItemResult] = useState(null); // { narration, effect }

  // Treasure path event - the streamed discovery text and the found item
  const [treasureText, setTreasureText] = useState('');
  const [treasureItem, setTreasureItem] = useState(null);

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
    setReunionText('');
    setIsReturningEncounter(false);
    setGrowthResults([]);
    setAbilityResult(null);
    setItemResult(null);
    setTreasureText('');
    setTreasureItem(null);
    // partyResources intentionally survives - reserves belong to the RUN
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
    setReunionText('');
    setIsReturningEncounter(false);
    setGrowthResults([]);
    setPartyConditions({});
    setPartyResources({});
    setIsUsingAbility(false);
    setAbilityResult(null);
    setIsUsingItem(false);
    setItemResult(null);
    setTreasureText('');
    setTreasureItem(null);
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
      reunionText,
      isReturningEncounter,
      growthResults,
      partyConditions,
      partyResources,
      isUsingAbility,
      abilityResult,
      isUsingItem,
      itemResult,
      treasureText,
      treasureItem,
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
      setReunionText,
      setIsReturningEncounter,
      setGrowthResults,
      setPartyConditions,
      setPartyResources,
      setIsUsingAbility,
      setAbilityResult,
      setIsUsingItem,
      setItemResult,
      setTreasureText,
      setTreasureItem,
      setExitText,
      clearEncounter
    },

    // Utilities
    resetState
  };
}
