// useWorkflowStore - React hooks for subscribing to workflow state store slices
// Each hook subscribes to exactly one slice, so components only re-render
// when the slice they display actually changes

import { useSyncExternalStore } from 'react';
import { workflowStateStore } from './workflowStateStore.js';

export const useWorkflowStatusSlice = () =>
  useSyncExternalStore(
    workflowStateStore.subscribeToWorkflowStatus,
    workflowStateStore.getWorkflowStatus,
  );

export const useWorkflowQueueStatus = () =>
  useSyncExternalStore(
    workflowStateStore.subscribeToWorkflowQueueStatus,
    workflowStateStore.getWorkflowQueueStatus,
  );
