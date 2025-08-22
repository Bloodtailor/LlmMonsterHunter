// useDungeonEvents.js - Minimal SSE event processing for dungeon workflow
// Starting simple: just generation ID capture and text streaming

import { useEffect, useState } from 'react';
import { useEventContext } from '../../EventContext/index.js';

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
    setIsDoorsReady
  } = setters;

  // Subscribe to SSE events
  const {
    workflowUpdateEvent,
    workflowCompletedEvent,
    llmGenerationUpdateEvent
  } = useEventContext();

  const [entryTextGenerationId, setEntryTextGenerationId] = useState(null);

  // Process workflow update events - capture generation ID
  useEffect(() => {
    if (workflowUpdateEvent?.step === 'emit_generation_id') {
      // Extract entry text generation ID
      const generationId = workflowUpdateEvent.data?.entry_text_generation_id;
      if (generationId) {
        setEntryTextGenerationId(generationId);
      }
    }
  }, [workflowUpdateEvent]);

  // Process LLM generation updates - streaming entry text
  useEffect(() => {
    // Only process LLM updates for our entry text generation
    if (llmGenerationUpdateEvent?.generationId === entryTextGenerationId) {
      setEntryText(llmGenerationUpdateEvent.partialText || '');
    }
  }, [llmGenerationUpdateEvent, entryTextGenerationId, setEntryText]);

  // Process workflow completion - enable doors when ready
  useEffect(() => {
    if (workflowCompletedEvent?.result?.success) {
      setIsDoorsReady(true);
    }
  }, [workflowCompletedEvent, setIsDoorsReady]);

  // This hook only provides side effects, no return value
}