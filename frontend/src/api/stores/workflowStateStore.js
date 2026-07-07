// Workflow State Store - External state management for workflow status
// Manages computed states outside React with useSyncExternalStore infrastructure
// Mirror of aiStateStore.js for the workflow domain

// ===== EXTERNAL STATE STORAGE =====
let workflowState = {
  // Current workflow tracking (computed from lifecycle events)
  workflowStatus: {
    activeWorkflow: null,
    status: 'idle',
    currentStep: null,
    currentData: null,
    isWorkflowActive: false,
  },

  // Workflow queue status
  workflowQueueStatus: {
    total: 0,
    pending: 0,
    processing: 0,
    completed: 0,
    failed: 0,
    items: [],
    trigger: null,
  },
};

// ===== SUBSCRIPTION MANAGEMENT =====
const listeners = {
  workflowStatus: new Set(),
  workflowQueueStatus: new Set(),
};

// Notify all subscribers of a specific state slice
const notifyListeners = (stateKey) => {
  listeners[stateKey].forEach((listener) => listener());
};

// ===== PUBLIC SUBSCRIPTION INTERFACE =====
export const workflowStateStore = {
  // Getters for current state snapshots
  getWorkflowStatus: () => workflowState.workflowStatus,
  getWorkflowQueueStatus: () => workflowState.workflowQueueStatus,

  // Subscribe functions for useSyncExternalStore
  subscribeToWorkflowStatus: (listener) => {
    listeners.workflowStatus.add(listener);
    return () => listeners.workflowStatus.delete(listener);
  },
  subscribeToWorkflowQueueStatus: (listener) => {
    listeners.workflowQueueStatus.add(listener);
    return () => listeners.workflowQueueStatus.delete(listener);
  },
};

// ===== INTERNAL STATE UPDATE FUNCTIONS =====
const updateWorkflowStatus = (updates) => {
  workflowState.workflowStatus = { ...workflowState.workflowStatus, ...updates };
  notifyListeners('workflowStatus');
};

const updateWorkflowQueueStatus = (newQueueData) => {
  if (!newQueueData || !newQueueData.allWorkflowItems) {
    return;
  }

  const items = newQueueData.allWorkflowItems;
  const statusCounts = items.reduce((acc, item) => {
    const status = item.status || 'pending';
    acc[status] = (acc[status] || 0) + 1;
    return acc;
  }, {});

  workflowState.workflowQueueStatus = {
    total: items.length,
    pending: statusCounts.pending || 0,
    processing: statusCounts.processing || 0,
    completed: statusCounts.completed || 0,
    failed: statusCounts.failed || 0,
    items,
    trigger: newQueueData.trigger,
  };

  notifyListeners('workflowQueueStatus');
};

// ===== EVENT ROUTER =====
export const workflowStatusRouter = (eventName, eventData) => {
  switch (eventName) {
    case 'workflowStarted':
      updateWorkflowStatus({
        activeWorkflow: eventData.workflowItem,
        status: 'running',
        currentStep: null,
        currentData: null,
        isWorkflowActive: true,
      });
      break;

    case 'workflowUpdate':
      updateWorkflowStatus({
        currentStep: eventData.step,
        currentData: eventData.data,
        status: 'processing...',
      });
      break;

    case 'workflowCompleted':
      updateWorkflowStatus({
        status: 'completed',
        isWorkflowActive: false,
      });
      break;

    case 'workflowFailed':
      updateWorkflowStatus({
        status: 'failed',
        isWorkflowActive: false,
      });
      break;

    case 'workflowQueueUpdate':
      updateWorkflowQueueStatus(eventData);
      break;

    // If event name not recognized, ignore silently
    default:
      break;
  }
};
