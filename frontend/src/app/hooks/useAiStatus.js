// useAiStatus Hook - Comprehensive AI status from the external AI state store
// Thin aggregator over useAiStore slice hooks - all event processing happens
// outside React (aiEventHandlers -> broadcastEvent -> aiStateStore)
// Return shape unchanged so existing consumers (StreamingDisplay) keep working

import { useEventContext } from '../contexts/EventContext';
import {
  useActiveGeneration,
  useCurrentActivity,
  useQueueStatus,
  useLlmStatus,
  useImageStatus,
} from '../../api/stores/useAiStore.js';

/**
 * Comprehensive hook for all AI status information
 * Returns everything a component needs for AI generation UI
 */
export function useAiStatus() {
  // Connection state still comes from context (it's connection-only now)
  const { isConnected } = useEventContext();

  // Each slice subscription only re-renders this hook when that slice changes
  const activeGeneration = useActiveGeneration();
  const storeActivity = useCurrentActivity();
  const queueStatus = useQueueStatus();
  const llmStatus = useLlmStatus();
  const imageStatus = useImageStatus();

  // Show "Disconnected" instead of "Idle" when the SSE connection is down
  const currentActivity =
    !isConnected && !storeActivity.type
      ? { ...storeActivity, label: 'Disconnected' }
      : storeActivity;

  return {
    activeGeneration,
    currentActivity,
    queueStatus,
    llmStatus,
    imageStatus,
  };
}
