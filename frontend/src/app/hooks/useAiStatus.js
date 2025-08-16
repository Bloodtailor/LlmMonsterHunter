// useAiStatus Hook - Comprehensive AI status with clean helper functions
// All AI status state in one hook: activeGeneration, currentActivity, queueStatus, llmStatus, imageStatus
// Uses explicit status tracking and clean event destructuring
// UPDATED: Now uses new naming scheme (llmGenerationStartedEvent instead of eventLlmGenerationStarted)

import { useState, useEffect, useMemo } from 'react';
import { useEventContext } from '../contexts/EventContext';

/**
 * Comprehensive hook for all AI status information
 * Returns everything a component needs for AI generation UI
 */
export function useAiStatus() {
  
  // Destructure all streaming events using new naming scheme
  const {
    isConnected,
    connectionError,
    llmGenerationStartedEvent,
    llmGenerationUpdateEvent,
    llmGenerationCompletedEvent,
    llmGenerationFailedEvent,
    imageGenerationStartedEvent,
    imageGenerationUpdateEvent,
    imageGenerationCompletedEvent,
    imageGenerationFailedEvent,
    aiQueueUpdateEvent,
    lastActivity
  } = useEventContext();
  
  // Helper state for tracking current streaming (resets on new generation)
  const [streamingText, setStreamingText] = useState({
    generationId: null,
    partialText: null,
    tokensSoFar: null
  });
  
  const [streamingImage, setStreamingImage] = useState({
    generationId: null,
    elapsedSeconds: null
  });
  
  // Explicit status tracking
  const [llmStatus, setLlmStatus] = useState('idle');
  const [imageStatus, setImageStatus] = useState('idle');
  
  // Active generation tracking
  const [activeGeneration, setActiveGeneration] = useState({ 
    state: null, 
    queueItem: null, 
    type: null 
  });

  // Helper functions for clean event handling
  const handleActiveGeneration = (eventType) => {
    switch (eventType) {
      case 'llmStarted':
        setActiveGeneration({
          state: 'generating',
          queueItem: llmGenerationStartedEvent.aiQueueItem,
          type: 'llm'
        });
        break;
      case 'imageStarted':
        setActiveGeneration({
          state: 'generating',
          queueItem: imageGenerationStartedEvent.aiQueueItem,
          type: 'image'
        });
        break;
      case 'llmCompleted':
        setActiveGeneration({
          state: 'completed',
          queueItem: llmGenerationCompletedEvent.aiQueueItem,
          type: 'llm'
        });
        break;
      case 'llmFailed':
        setActiveGeneration({
          state: 'failed',
          queueItem: llmGenerationFailedEvent.aiQueueItem,
          type: 'llm'
        });
        break;
      case 'imageCompleted':
        setActiveGeneration({
          state: 'completed',
          queueItem: imageGenerationCompletedEvent.aiQueueItem,
          type: 'image'
        });
        break;
      case 'imageFailed':
        setActiveGeneration({
          state: 'failed',
          queueItem: imageGenerationFailedEvent.aiQueueItem,
          type: 'image'
        });
        break;
    }
  };

  const handleResetStreamingText = () => {
    setStreamingText({
      generationId: llmGenerationStartedEvent.generationId,
      partialText: null,
      tokensSoFar: null
    });
  };

  const handleResetStreamingImage = () => {
    setStreamingImage({
      generationId: imageGenerationStartedEvent.generationId,
      elapsedSeconds: null
    });
  };

  const handleUpdateStreamingText = () => {
    setStreamingText({
      partialText: llmGenerationUpdateEvent.partialText,
      tokensSoFar: llmGenerationUpdateEvent.tokensSoFar
    });
  };

  const handleUpdateStreamingImage = () => {
    setStreamingImage({
      elapsedSeconds: imageGenerationUpdateEvent.elapsedSeconds
    });
  };

  // Event handlers using clean useEffect pattern
  useEffect(() => {
    if (llmGenerationStartedEvent) {
      handleActiveGeneration('llmStarted');
      handleResetStreamingText();
      setLlmStatus('initializing...');
    }
  }, [llmGenerationStartedEvent]);

  useEffect(() => {
    if (imageGenerationStartedEvent) {
      handleActiveGeneration('imageStarted');
      handleResetStreamingImage();
      setImageStatus('initializing...');
    }
  }, [imageGenerationStartedEvent]);

  useEffect(() => {
    if (llmGenerationUpdateEvent) {
      handleUpdateStreamingText();
      setLlmStatus('generating');
    }
  }, [llmGenerationUpdateEvent]);

  useEffect(() => {
    if (imageGenerationUpdateEvent) {
      handleUpdateStreamingImage();
      setImageStatus('generating');
    }
  }, [imageGenerationUpdateEvent]);

  useEffect(() => {
    if (llmGenerationCompletedEvent) {
      handleActiveGeneration('llmCompleted');
      setLlmStatus('completed');
    }
  }, [llmGenerationCompletedEvent]);

  useEffect(() => {
    if (llmGenerationFailedEvent) {
      handleActiveGeneration('llmFailed');
      setLlmStatus('failed');
    }
  }, [llmGenerationFailedEvent]);

  useEffect(() => {
    if (imageGenerationCompletedEvent) {
      handleActiveGeneration('imageCompleted');
      setImageStatus('completed');
    }
  }, [imageGenerationCompletedEvent]);

  useEffect(() => {
    if (imageGenerationFailedEvent) {
      handleActiveGeneration('imageFailed');
      setImageStatus('failed');
    }
  }, [imageGenerationFailedEvent]);

  // Computed status objects
  const currentActivity = useMemo(() => {
    if (activeGeneration.state && activeGeneration.queueItem) {
      const { state, type, queueItem } = activeGeneration;
      
      if (state === 'generating') {
        let progress = 'initializing...';
        
        if (type === 'llm' && streamingText.tokensSoFar !== null) {
          progress = `${streamingText.tokensSoFar} tokens`;
        } else if (type === 'image' && streamingImage.elapsedSeconds !== null) {
          progress = `${Math.floor(streamingImage.elapsedSeconds)}s elapsed`;
        }

        return {
          type,
          label: type === 'llm' ? 'Generating text' : 'Generating image',
          progress,
          queueItem
        };
      } 
    }

    if (isConnected) {
      return {
        type: null,
        label: 'Idle',
        progress: '',
        queueItem: null
      };
    } else {
      return {
        type: null,
        label: 'Disconnected',
        progress: '',
        queueItem: null
      };
    }
  }, [activeGeneration, streamingText.tokensSoFar, streamingImage.elapsedSeconds, isConnected]);

  const queueStatus = useMemo(() => {
    if (!aiQueueUpdateEvent || !aiQueueUpdateEvent.allAiQueueItems) {
      return {
        total: 0,
        pending: 0,
        processing: 0,
        completed: 0,
        failed: 0,
        items: []
      };
    }

    const items = aiQueueUpdateEvent.allAiQueueItems;
    const statusCounts = items.reduce((acc, item) => {
      const status = item.status || 'pending';
      acc[status] = (acc[status] || 0) + 1;
      return acc;
    }, {});

    return {
      total: items.length,
      pending: statusCounts.pending || 0,
      processing: statusCounts.processing || 0,
      completed: statusCounts.completed || 0,
      failed: statusCounts.failed || 0,
      items,
      trigger: aiQueueUpdateEvent.trigger
    };
  }, [aiQueueUpdateEvent]);

  const computedLlmStatus = useMemo(() => {
    return {
      generationId: streamingText.generationId,
      promptType: llmGenerationStartedEvent?.aiQueueItem?.promptType || null,
      promptName: llmGenerationStartedEvent?.aiQueueItem?.promptName || null,
      status: llmStatus,
      partialText: streamingText.partialText,
      tokensSoFar: streamingText.tokensSoFar,
      result: llmGenerationCompletedEvent?.result || null,
      error: llmGenerationFailedEvent?.error || null,
      startedAt: llmGenerationStartedEvent?.aiQueueItem?.startedAt || null
    };
  }, [
    llmGenerationStartedEvent,
    llmGenerationCompletedEvent,
    llmGenerationFailedEvent,
    streamingText,
    llmStatus
  ]);

  const computedImageStatus = useMemo(() => {

    // Only create imageUrl if we have an imagePath
    const imageUrl = imageGenerationCompletedEvent?.result?.imagePath 
      ? `http://localhost:5000/api/monsters/card-art/${imageGenerationCompletedEvent.result.imagePath}`
      : null;

    return {
      generationId: streamingImage.generationId,
      promptName: imageGenerationStartedEvent?.aiQueueItem?.promptName || null,
      status: imageStatus,
      elapsedSeconds: streamingImage.elapsedSeconds || null,
      result: imageGenerationCompletedEvent?.result || null,
      error: imageGenerationFailedEvent?.error || null,
      startedAt: imageGenerationStartedEvent?.aiQueueItem?.startedAt || null,
      imageUrl
    };
  }, [
    imageGenerationStartedEvent,
    imageGenerationCompletedEvent,
    imageGenerationFailedEvent,
    streamingImage,
    imageStatus
  ]);

  return {
    activeGeneration,
    currentActivity,
    queueStatus,
    llmStatus: computedLlmStatus,
    imageStatus: computedImageStatus
    
  };
}