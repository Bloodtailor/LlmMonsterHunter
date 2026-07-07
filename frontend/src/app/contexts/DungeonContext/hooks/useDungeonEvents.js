// useDungeonEvents.js - SSE event processing for the dungeon exploration loop
// Subscribes to specific broadcast events instead of context state,
// so dungeon state only updates for events it actually cares about
// Handles: entry/encounter/look/camp text streaming, arrival locations,
// the encounter monsters' live reveal, and all dungeon workflow completions

import { useEventSubscription } from '../../../../api/events/useEventSubscription.js';
import { useStreamedGeneration } from '../../../../api/events/useStreamedGeneration.js';

// Every workflow this context owns - used for error surfacing
const DUNGEON_WORKFLOWS = [
  'generate_expedition_notices',
  'enter_dungeon',
  'choose_path',
  'respond_to_monster',
  'sneak_past',
  'surprise_attack',
  'setup_camp',
  'use_dungeon_ability',
  'use_dungeon_item',
  'continue_exploring',
];

/**
 * Hook for processing dungeon-related SSE events
 * @param {object} stateHook - State hook from useDungeonState
 */
export function useDungeonEvents(stateHook) {
  const { state, setters } = stateHook;

  const {
    setNotices,
    setIsGeneratingNotices,
    setExpedition,
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
    setErrorState,
  } = setters;

  // Stream the entry text announced by the enter_dungeon workflow
  useStreamedGeneration('entry_text_generation_id', {
    onText: (partialText) => setEntryText(partialText),
  });

  // Stream the encounter vanity text announced by the choose_path workflow
  useStreamedGeneration('encounter_text_generation_id', {
    onText: (partialText) => setEncounterText(partialText),
  });

  // Stream the look-around text for explore arrivals
  useStreamedGeneration('look_text_generation_id', {
    onText: (partialText) => setLookText(partialText),
  });

  // Stream the camp scene - the party's monsters talking around the fire
  useStreamedGeneration('camp_text_generation_id', {
    onText: (partialText) => setCampText(partialText),
  });

  // Stream the treasure discovery narration for treasure arrivals
  useStreamedGeneration('treasure_text_generation_id', {
    onText: (partialText) => setTreasureText(partialText),
  });

  // Stream the reunion scene - the party recognizes a returning monster
  useStreamedGeneration('reunion_text_generation_id', {
    onText: (partialText) => setReunionText(partialText),
  });

  // The choose_path workflow announces the arrival location mid-flight
  useEventSubscription('workflowUpdate', (eventData) => {
    if (eventData?.step === 'location_generated' && eventData.data?.current_location) {
      setCurrentLocation(eventData.data.current_location);
    }
  });

  // The encounter monsters reveal themselves as they are generated:
  // cards appear on creation, abilities and art pop in live.
  // Battles and explore areas can spawn several - they accumulate.
  // Only capture monsters while the party is at a location mid-run
  // so Sanctuary summons don't leak in
  const isEncounterUnfolding = () => state.currentLocation && !state.exitText;

  useEventSubscription('monsterCreated', ({ monster }) => {
    if (isEncounterUnfolding() && monster) {
      setEncounterMonsters((prev) => [...prev, monster]);
    }
  });

  // A PRE-EXISTING monster staged into the encounter (returning monsters
  // and blend-ins arrive complete - no monster.created fires for them)
  useEventSubscription('dungeonMonsterRevealed', ({ monster }) => {
    if (isEncounterUnfolding() && monster) {
      setEncounterMonsters((prev) =>
        prev.some((existing) => existing.id === monster.id)
          ? prev.map((existing) => (existing.id === monster.id ? monster : existing))
          : [...prev, monster],
      );
    }
  });

  useEventSubscription('monsterAbilityAdded', ({ monsterId, ability }) => {
    if (!monsterId || !ability) return;
    setEncounterMonsters((prev) =>
      prev.map((monster) =>
        monster.id === monsterId
          ? {
              ...monster,
              abilities: [...(monster.abilities || []), ability],
              abilityCount: (monster.abilityCount || 0) + 1,
            }
          : monster,
      ),
    );
  });

  useEventSubscription('monsterArtReady', ({ monsterId, imagePath }) => {
    if (!monsterId || !imagePath) return;
    setEncounterMonsters((prev) =>
      prev.map((monster) =>
        monster.id === monsterId
          ? { ...monster, cardArt: { exists: true, relativePath: imagePath } }
          : monster,
      ),
    );
  });

  // A dungeon workflow failed - surface the error instead of hanging the UI
  const handleWorkflowFailure = (workflowType, error) => {
    if (!DUNGEON_WORKFLOWS.includes(workflowType)) return;

    setIsGeneratingNotices(false);
    setIsMonsterResponding(false);
    setIsSneaking(false);
    setIsAmbushing(false);
    setIsCamping(false);
    setIsUsingAbility(false);
    setIsUsingItem(false);

    // The party's optimistic dialogue line never reached the monster
    if (workflowType === 'respond_to_monster') {
      setDialogue((prev) =>
        prev.length && prev[prev.length - 1].speaker === 'The party' ? prev.slice(0, -1) : prev,
      );
    }

    setErrorState(typeof error === 'string' ? error : `${workflowType} failed`);
  };

  useEventSubscription('workflowFailed', (eventData) => {
    handleWorkflowFailure(eventData?.workflowItem?.workflowType, eventData?.error);
  });

  // Dungeon workflow completions - branch by workflow type
  useEventSubscription('workflowCompleted', (eventData) => {
    const workflowType = eventData?.workflowItem?.workflowType;
    const result = eventData?.result;
    if (!result) return;

    if (!result.success) {
      handleWorkflowFailure(workflowType, result.error);
      return;
    }

    // Most workflows report the party's current conditions and reserves
    if (DUNGEON_WORKFLOWS.includes(workflowType) && result.party_conditions) {
      setPartyConditions(result.party_conditions);
    }
    if (DUNGEON_WORKFLOWS.includes(workflowType) && result.party_resources) {
      setPartyResources(result.party_resources);
    }

    switch (workflowType) {
      case 'generate_expedition_notices':
        setIsGeneratingNotices(false);
        setNotices(result.notices || []);
        break;

      case 'enter_dungeon':
        setExpedition(result.expedition || null);
        setCurrentLocation(result.current_location || null);
        setPaths(result.paths || null);
        setArePathsReady(true);
        break;

      case 'choose_path':
        if (result.returning) {
          setIsReturningEncounter(true);
        }
        if (result.exited) {
          setExitText(result.exit_text || 'You emerge back into the daylight.');
          setGrowthResults(result.growth || []);
        } else if (result.event === 'monster_dialogue') {
          // The monster opens the conversation: greeting, then its question
          setDialogue((prev) => {
            const speaker = state.encounterMonsters?.[0]?.name || 'The monster';
            const opening = [];
            if (result.greeting) opening.push({ speaker, text: result.greeting });
            if (result.question) opening.push({ speaker, text: result.question });
            return [...prev, ...opening];
          });
        } else if (result.event === 'location_explore') {
          setMonstersPresent(!!result.monsters_present);
        } else if (result.event === 'treasure') {
          // The found item was already announced via inventory.item_added;
          // hold it here for the discovery display, then the moment plays
          // like a creature-free explore (continue / camp)
          setTreasureItem(result.item || null);
          setMonstersPresent(false);
        }
        // monster_battle is handled by the BattleContext
        break;

      case 'respond_to_monster': {
        setIsMonsterResponding(false);
        const speaker = state.encounterMonsters?.[0]?.name || 'The monster';
        if (result.response) {
          setDialogue((prev) => [...prev, { speaker, text: result.response }]);
        }
        // continue_dialogue keeps the conversation open; every other
        // outcome resolves the encounter (battle start is handled by
        // the BattleContext via the battle_snapshot in this result)
        if (result.outcome && result.outcome !== 'continue_dialogue') {
          setDialogueOutcome({
            outcome: result.outcome,
            joinedNames: result.joined_names || [],
          });
        }
        break;
      }

      case 'sneak_past':
        setIsSneaking(false);
        setSneakResult({
          success: !!result.success,
          narration: result.narration || '',
        });
        // On failure the battle starts - the BattleContext picks up the snapshot
        break;

      case 'surprise_attack':
        setIsAmbushing(false);
        // The battle itself is handled by the BattleContext
        break;

      case 'setup_camp':
        setIsCamping(false);
        setHasCamped(true);
        setGrowthResults(result.growth || []);
        break;

      case 'use_dungeon_ability':
        setIsUsingAbility(false);
        setAbilityResult({
          narration: result.narration || '',
          effect: result.effect || 'none',
        });
        break;

      case 'use_dungeon_item':
        setIsUsingItem(false);
        setItemResult({
          narration: result.narration || '',
          effect: result.effect || 'none',
        });
        break;

      case 'continue_exploring':
        setCurrentLocation(result.current_location || null);
        setPaths(result.paths || null);
        setArePathsReady(true);
        break;

      default:
        break;
    }
  });

  // This hook only provides side effects, no return value
}
