// useDungeonEvents.js - Minimal SSE event processing for dungeon workflow
// Subscribes to specific broadcast events instead of context state,
// so dungeon state only updates for events it actually cares about
// Handles: generation ID capture, entry text streaming, door readiness

import { useRef } from 'react';
import { useEventSubscription } from '../../../../api/events/useEventSubscription.js';

/**
 * Hook for processing minimal dungeon-related SSE events
 * Just handles generation ID and text streaming for now
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

  // Ref (not state) - capturing the ID shouldn't cause a re-render
  const entryTextGenerationIdRef = useRef(null);

  // Capture the entry text generation ID from workflow updates
  useEventSubscription('workflowUpdate', (eventData) => {
    if (eventData?.step === 'emit_generation_id') {
      const generationId = eventData.data?.entry_text_generation_id;
      if (generationId) {
        entryTextGenerationIdRef.current = generationId;
      }
    }
  });

  // Stream entry text - only for our captured generation ID
  useEventSubscription('llmGenerationUpdate', (eventData) => {
    const entryTextGenerationId = entryTextGenerationIdRef.current;
    if (entryTextGenerationId && eventData?.generationId === entryTextGenerationId) {
      setEntryText(eventData.partialText || '');
    }
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
