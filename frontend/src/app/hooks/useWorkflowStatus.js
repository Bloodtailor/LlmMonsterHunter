// useWorkflowStatus Hook - Workflow status from the external workflow state store
// Thin aggregator over useWorkflowStore slice hooks - all event processing happens
// outside React (workflowEventHandlers -> broadcastEvent -> workflowStateStore)
// Return shape unchanged so existing consumers (StreamingDisplay) keep working

import {
  useWorkflowStatusSlice,
  useWorkflowQueueStatus
} from '../../api/stores/useWorkflowStore.js';

export function useWorkflowStatus() {

  const {
    activeWorkflow,
    status,
    currentStep,
    currentData,
    isWorkflowActive
  } = useWorkflowStatusSlice();

  const workflowQueueStatus = useWorkflowQueueStatus();

  return {
    // Core state
    activeWorkflow,
    workflowStatus: status,
    currentStep,
    currentData,
    isWorkflowActive,
    workflowQueueStatus
  };
}
