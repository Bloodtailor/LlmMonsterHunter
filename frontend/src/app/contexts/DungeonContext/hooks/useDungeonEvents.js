// useDungeonEvents.js - SSE event processing for the dungeon exploration loop
// Subscribes to specific broadcast events instead of context state,
// so dungeon state only updates for events it actually cares about
// Handles: entry/encounter text streaming, arrival locations, the
// encounter monster's live reveal, and all dungeon workflow completions

import { useEventSubscription } from '../../../../api/events/useEventSubscription.js';
import { useStreamedGeneration } from '../../../../api/events/useStreamedGeneration.js';

/**
 * Hook for processing dungeon-related SSE events
 * @param {object} stateHook - State hook from useDungeonState
 */
export function useDungeonEvents(stateHook) {
  const {
    state,
    setters
  } = stateHook;

  const {
    setEntryText,
    setCurrentLocation,
    setPaths,
    setArePathsReady,
    setEncounterText,
    setEncounterMonster,
    setRiddleGreeting,
    setRiddle,
    setIsJudgingAnswer,
    setRiddleResult,
    setExitText,
    setErrorState
  } = setters;

  // Stream the entry text announced by the enter_dungeon workflow
  useStreamedGeneration('entry_text_generation_id', {
    onText: (partialText) => setEntryText(partialText)
  });

  // Stream the encounter vanity text announced by the choose_path workflow
  useStreamedGeneration('encounter_text_generation_id', {
    onText: (partialText) => setEncounterText(partialText)
  });

  // The choose_path workflow announces the arrival location mid-flight
  useEventSubscription('workflowUpdate', (eventData) => {
    if (eventData?.step === 'location_generated' && eventData.data?.current_location) {
      setCurrentLocation(eventData.data.current_location);
    }
  });

  // The encounter monster reveals itself as it is generated:
  // card appears on creation, abilities and art pop in live.
  // Only capture monsters while an encounter is unfolding (encounter
  // text present but no riddle yet) so Sanctuary summons don't leak in
  const isEncounterUnfolding = () => state.currentLocation && !state.riddleResult;

  useEventSubscription('monsterCreated', ({ monster }) => {
    if (isEncounterUnfolding() && monster) {
      setEncounterMonster(monster);
    }
  });

  useEventSubscription('monsterAbilityAdded', ({ monsterId, ability }) => {
    if (!monsterId || !ability) return;
    setEncounterMonster(prev =>
      prev && prev.id === monsterId
        ? { ...prev, abilities: [...(prev.abilities || []), ability], abilityCount: (prev.abilityCount || 0) + 1 }
        : prev
    );
  });

  useEventSubscription('monsterArtReady', ({ monsterId, imagePath }) => {
    if (!monsterId || !imagePath) return;
    setEncounterMonster(prev =>
      prev && prev.id === monsterId
        ? { ...prev, cardArt: { exists: true, relativePath: imagePath } }
        : prev
    );
  });

  // Dungeon workflow failures - surface the error instead of hanging the UI
  useEventSubscription('workflowFailed', (eventData) => {
    const workflowType = eventData?.workflowItem?.workflowType;
    const dungeonWorkflows = ['enter_dungeon', 'choose_path', 'answer_riddle', 'continue_exploring'];
    if (dungeonWorkflows.includes(workflowType)) {
      setIsJudgingAnswer(false);
      const error = typeof eventData?.error === 'string' ? eventData.error : `${workflowType} failed`;
      setErrorState(error);
    }
  });

  // Dungeon workflow completions - branch by workflow type
  useEventSubscription('workflowCompleted', (eventData) => {
    const workflowType = eventData?.workflowItem?.workflowType;
    const result = eventData?.result;
    if (!result) return;

    if (!result.success) {
      // A dungeon workflow failed - surface the error
      const dungeonWorkflows = ['enter_dungeon', 'choose_path', 'answer_riddle', 'continue_exploring'];
      if (dungeonWorkflows.includes(workflowType)) {
        setErrorState(result.error || `${workflowType} failed`);
      }
      return;
    }

    switch (workflowType) {
      case 'enter_dungeon':
        setCurrentLocation(result.current_location || null);
        setPaths(result.paths || null);
        setArePathsReady(true);
        break;

      case 'choose_path':
        if (result.exited) {
          setExitText(result.exit_text || 'You emerge back into the daylight.');
        } else if (result.event === 'monster_riddle') {
          setRiddleGreeting(result.greeting || null);
          setRiddle(result.riddle || null);
        }
        break;

      case 'answer_riddle':
        setIsJudgingAnswer(false);
        setRiddleResult({
          correct: !!result.correct,
          response: result.response || ''
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
