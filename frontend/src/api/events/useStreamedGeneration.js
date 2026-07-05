// useStreamedGeneration - Reusable hook for streaming workflow-owned LLM text
// The recurring pattern for vanity text throughout the game:
//   1. A workflow emits step 'emit_generation_id' with the generation ID in its data
//   2. We capture that ID and stream only the matching llmGenerationUpdate events
// First used for dungeon entry text; encounter vanity text and riddles come next

import { useRef } from 'react';
import { useEventSubscription } from './useEventSubscription.js';

/**
 * Stream LLM text for a generation announced by a workflow
 * @param {string} generationIdKey - Key inside the workflow step data that holds
 *   the generation ID (e.g., 'entry_text_generation_id')
 * @param {object} callbacks
 * @param {function} callbacks.onText - Called with (partialText) on each streamed update
 * @param {function} [callbacks.onComplete] - Called with (result) when the generation completes
 */
export const useStreamedGeneration = (generationIdKey, { onText, onComplete }) => {
  // Ref (not state) - capturing the ID shouldn't cause a re-render
  const generationIdRef = useRef(null);

  // Capture the generation ID when the workflow announces it
  useEventSubscription('workflowUpdate', (eventData) => {
    if (eventData?.step === 'emit_generation_id') {
      const generationId = eventData.data?.[generationIdKey];
      if (generationId) {
        generationIdRef.current = generationId;
      }
    }
  });

  // Stream text - only for our captured generation ID
  useEventSubscription('llmGenerationUpdate', (eventData) => {
    const generationId = generationIdRef.current;
    if (generationId && eventData?.generationId === generationId) {
      onText(eventData.partialText || '');
    }
  });

  // Notify when our generation completes
  useEventSubscription('llmGenerationCompleted', (eventData) => {
    const generationId = generationIdRef.current;
    if (onComplete && generationId && eventData?.generationId === generationId) {
      onComplete(eventData.result);
    }
  });
};
