// useDungeonEvents.js - Minimal SSE event processing for dungeon workflow
// Subscribes to specific broadcast events instead of context state,
// so dungeon state only updates for events it actually cares about
// Handles: entry text streaming (via useStreamedGeneration) and door readiness

import { useEventSubscription } from '../../../../api/events/useEventSubscription.js';
import { useStreamedGeneration } from '../../../../api/events/useStreamedGeneration.js';

/**
 * Hook for processing minimal dungeon-related SSE events
 * Just handles entry text streaming and doors for now
 * @param {object} stateHook - State hook from useDungeonState
 */
export function useDungeonEvents(stateHook) {
  const {
    setters
  } = stateHook;

  const {
    setEntryText,
    setIsDoorsReady,
    setDoors
  } = setters;

  // Stream the entry text announced by the enter_dungeon workflow
  useStreamedGeneration('entry_text_generation_id', {
    onText: (partialText) => setEntryText(partialText)
  });

  // Enable doors when the enter_dungeon workflow completes
  useEventSubscription('workflowCompleted', (eventData) => {
    const isDungeonWorkflow = eventData?.workflowItem?.workflowType === 'enter_dungeon';
    if (isDungeonWorkflow && eventData?.result?.success) {
      setIsDoorsReady(true);
      setDoors(eventData.result);
    }
  });

  // This hook only provides side effects, no return value
}
