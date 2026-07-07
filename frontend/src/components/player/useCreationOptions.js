// useCreationOptions.js - options for ONE creation field, over SSE
// Queues a generate_player_options workflow and resolves its result
// from the workflowCompleted broadcast (matching on workflowId). The
// player can always ask for fresh ideas - each request replaces the
// last set.

import { useCallback, useRef, useState } from 'react';
import { useEventSubscription } from '../../api/events/useEventSubscription.js';
import * as playerApi from '../../api/services/player.js';

export function useCreationOptions(field) {
  const [options, setOptions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // The workflow we are currently waiting on (ref: event handlers must
  // see the latest id without re-subscribing)
  const pendingWorkflowIdRef = useRef(null);

  const request = useCallback(
    async (choices) => {
      setIsLoading(true);
      setError(null);
      try {
        const result = await playerApi.generateOptions(field, choices);
        if (!result.success || !result.workflowId) {
          setError(result.error || 'The muse is quiet - try again.');
          setIsLoading(false);
          return;
        }
        pendingWorkflowIdRef.current = result.workflowId;
      } catch (requestError) {
        setError(requestError.message || 'The muse is quiet - try again.');
        setIsLoading(false);
      }
    },
    [field],
  );

  useEventSubscription('workflowCompleted', ({ workflowId, result }) => {
    if (!workflowId || workflowId !== pendingWorkflowIdRef.current) return;
    pendingWorkflowIdRef.current = null;
    setOptions(Array.isArray(result?.options) ? result.options : []);
    setIsLoading(false);
  });

  useEventSubscription('workflowFailed', ({ workflowId, error: failure }) => {
    if (!workflowId || workflowId !== pendingWorkflowIdRef.current) return;
    pendingWorkflowIdRef.current = null;
    setError(
      (typeof failure === 'object' ? failure?.error : failure) || 'The muse is quiet - try again.',
    );
    setIsLoading(false);
  });

  return { options, isLoading, error, request };
}
