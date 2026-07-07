// useAiStore - React hooks for subscribing to AI state store slices
// Each hook subscribes to exactly one slice, so components only re-render
// when the slice they display actually changes

import { useSyncExternalStore } from 'react';
import { aiStateStore } from './aiStateStore.js';

export const useActiveGeneration = () =>
  useSyncExternalStore(aiStateStore.subscribeToActiveGeneration, aiStateStore.getActiveGeneration);

export const useCurrentActivity = () =>
  useSyncExternalStore(aiStateStore.subscribeToCurrentActivity, aiStateStore.getCurrentActivity);

export const useQueueStatus = () =>
  useSyncExternalStore(aiStateStore.subscribeToQueueStatus, aiStateStore.getQueueStatus);

export const useLlmStatus = () =>
  useSyncExternalStore(aiStateStore.subscribeToLlmStatus, aiStateStore.getLlmStatus);

export const useImageStatus = () =>
  useSyncExternalStore(aiStateStore.subscribeToImageStatus, aiStateStore.getImageStatus);
