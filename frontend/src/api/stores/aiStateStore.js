// AI State Store - External state management for AI status
// Manages computed states outside React with useSyncExternalStore infrastructure
// Each computed state can be subscribed to independently to prevent unnecessary re-renders

// ===== EXTERNAL STATE STORAGE =====
let aiState = {
  // Active generation tracking
  activeGeneration: {
    state: null,
    queueItem: null,
    type: null,
  },

  // Current activity (computed from activeGeneration + streaming states)
  currentActivity: {
    type: null,
    label: 'Idle',
    progress: '',
    queueItem: null,
  },

  // Queue status
  queueStatus: {
    total: 0,
    pending: 0,
    processing: 0,
    completed: 0,
    failed: 0,
    items: [],
    trigger: null,
  },

  // LLM status with streaming data
  llmStatus: {
    generationId: null,
    promptType: null,
    promptName: null,
    modelName: null,
    status: 'idle',
    partialText: null,
    tokensSoFar: null,
    result: null,
    error: null,
    startedAt: null,
  },

  // Image status with streaming data
  imageStatus: {
    generationId: null,
    promptName: null,
    status: 'idle',
    elapsedSeconds: null,
    result: null,
    error: null,
    startedAt: null,
    imageUrl: null,
  },
};

// ===== SUBSCRIPTION MANAGEMENT =====
const listeners = {
  activeGeneration: new Set(),
  currentActivity: new Set(),
  queueStatus: new Set(),
  llmStatus: new Set(),
  imageStatus: new Set(),
};

// Notify all subscribers of a specific state slice
const notifyListeners = (stateKey) => {
  listeners[stateKey].forEach((listener) => listener());
};

// ===== PUBLIC SUBSCRIPTION INTERFACE =====
export const aiStateStore = {
  // Getters for current state snapshots
  getActiveGeneration: () => aiState.activeGeneration,
  getCurrentActivity: () => aiState.currentActivity,
  getQueueStatus: () => aiState.queueStatus,
  getLlmStatus: () => aiState.llmStatus,
  getImageStatus: () => aiState.imageStatus,

  // Subscribe functions for useSyncExternalStore
  subscribeToActiveGeneration: (listener) => {
    listeners.activeGeneration.add(listener);
    return () => listeners.activeGeneration.delete(listener);
  },
  subscribeToCurrentActivity: (listener) => {
    listeners.currentActivity.add(listener);
    return () => listeners.currentActivity.delete(listener);
  },
  subscribeToQueueStatus: (listener) => {
    listeners.queueStatus.add(listener);
    return () => listeners.queueStatus.delete(listener);
  },
  subscribeToLlmStatus: (listener) => {
    listeners.llmStatus.add(listener);
    return () => listeners.llmStatus.delete(listener);
  },
  subscribeToImageStatus: (listener) => {
    listeners.imageStatus.add(listener);
    return () => listeners.imageStatus.delete(listener);
  },
};

// ===== INTERNAL STATE UPDATE FUNCTIONS =====
const updateActiveGeneration = (newState) => {
  const oldState = aiState.activeGeneration;
  aiState.activeGeneration = { ...oldState, ...newState };
  notifyListeners('activeGeneration');

  // Active generation changes trigger current activity recalculation
  recalculateCurrentActivity();
};

const updateLlmStatus = (updates) => {
  const oldState = aiState.llmStatus;
  aiState.llmStatus = { ...oldState, ...updates };
  notifyListeners('llmStatus');

  // LLM status changes might trigger current activity recalculation
  recalculateCurrentActivity();
};

const updateImageStatus = (updates) => {
  const oldState = aiState.imageStatus;
  aiState.imageStatus = { ...oldState, ...updates };
  notifyListeners('imageStatus');

  // Image status changes might trigger current activity recalculation
  recalculateCurrentActivity();
};

const updateQueueStatus = (newQueueData) => {
  if (!newQueueData || !newQueueData.allAiQueueItems) {
    return;
  }

  const items = newQueueData.allAiQueueItems;
  const statusCounts = items.reduce((acc, item) => {
    const status = item.status || 'pending';
    acc[status] = (acc[status] || 0) + 1;
    return acc;
  }, {});

  aiState.queueStatus = {
    total: items.length,
    pending: statusCounts.pending || 0,
    processing: statusCounts.processing || 0,
    completed: statusCounts.completed || 0,
    failed: statusCounts.failed || 0,
    items,
    trigger: newQueueData.trigger,
  };

  notifyListeners('queueStatus');
};

const recalculateCurrentActivity = () => {
  const { activeGeneration, llmStatus, imageStatus } = aiState;
  let newActivity;

  if (activeGeneration.state && activeGeneration.queueItem) {
    const { state, type, queueItem } = activeGeneration;

    if (state === 'generating') {
      let progress = 'initializing...';

      if (type === 'llm' && llmStatus.tokensSoFar !== null) {
        progress = `${llmStatus.tokensSoFar} tokens`;
      } else if (type === 'image' && imageStatus.elapsedSeconds !== null) {
        progress = `${Math.floor(imageStatus.elapsedSeconds)}s elapsed`;
      }

      newActivity = {
        type,
        label: type === 'llm' ? 'Generating text' : 'Generating image',
        progress,
        queueItem,
      };
    } else {
      newActivity = {
        type: null,
        label: 'Idle',
        progress: '',
        queueItem: null,
      };
    }
  } else {
    newActivity = {
      type: null,
      label: 'Idle',
      progress: '',
      queueItem: null,
    };
  }

  // Only update if actually changed
  const currentActivity = aiState.currentActivity;
  if (JSON.stringify(currentActivity) !== JSON.stringify(newActivity)) {
    aiState.currentActivity = newActivity;
    notifyListeners('currentActivity');
  }
};

// ===== EVENT ROUTER =====
export const aiStatusRouter = (eventName, eventData) => {
  switch (eventName) {
    case 'llmGenerationStarted':
      updateActiveGeneration({
        state: 'generating',
        queueItem: eventData.aiQueueItem,
        type: 'llm',
      });
      updateLlmStatus({
        generationId: eventData.generationId,
        promptType: eventData.aiQueueItem?.promptType || null,
        promptName: eventData.aiQueueItem?.promptName || null,
        modelName: eventData.aiQueueItem?.modelName || null,
        status: 'initializing...',
        partialText: null,
        tokensSoFar: null,
        result: null,
        error: null,
        startedAt: eventData.aiQueueItem?.startedAt || null,
      });
      break;

    case 'llmGenerationUpdate':
      updateLlmStatus({
        status: 'generating',
        partialText: eventData.partialText,
        tokensSoFar: eventData.tokensSoFar,
      });
      break;

    case 'llmGenerationCompleted':
      updateActiveGeneration({
        state: 'completed',
        queueItem: eventData.aiQueueItem,
        type: 'llm',
      });
      updateLlmStatus({
        status: 'completed',
        result: eventData.result,
      });
      break;

    case 'llmGenerationFailed':
      updateActiveGeneration({
        state: 'failed',
        queueItem: eventData.aiQueueItem,
        type: 'llm',
      });
      updateLlmStatus({
        status: 'failed',
        error: eventData.error,
      });
      break;

    case 'imageGenerationStarted':
      updateActiveGeneration({
        state: 'generating',
        queueItem: eventData.aiQueueItem,
        type: 'image',
      });
      updateImageStatus({
        generationId: eventData.generationId,
        promptName: eventData.aiQueueItem?.promptName || null,
        status: 'initializing...',
        elapsedSeconds: null,
        result: null,
        error: null,
        startedAt: eventData.aiQueueItem?.startedAt || null,
        imageUrl: null,
      });
      break;

    case 'imageGenerationUpdate':
      updateImageStatus({
        status: 'generating',
        elapsedSeconds: eventData.elapsedSeconds,
      });
      break;

    case 'imageGenerationCompleted':
      updateActiveGeneration({
        state: 'completed',
        queueItem: eventData.aiQueueItem,
        type: 'image',
      });

      // Create image URL if we have an image path
      const imageUrl = eventData.result?.imagePath
        ? `http://localhost:5000/api/monsters/card-art/${eventData.result.imagePath}`
        : null;

      updateImageStatus({
        status: 'completed',
        result: eventData.result,
        imageUrl,
      });
      break;

    case 'imageGenerationFailed':
      updateActiveGeneration({
        state: 'failed',
        queueItem: eventData.aiQueueItem,
        type: 'image',
      });
      updateImageStatus({
        status: 'failed',
        error: eventData.error,
      });
      break;

    case 'aiQueueUpdate':
      updateQueueStatus(eventData);
      break;

    // If event name not recognized, ignore silently
    default:
      break;
  }
};
