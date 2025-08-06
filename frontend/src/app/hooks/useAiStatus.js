// useAiStatus Hook - Comprehensive AI status with clean helper functions
// All AI status state in one hook: activeGeneration, currentActivity, queueStatus, llmStatus, imageStatus
// Uses explicit status tracking and clean event destructuring

import { useState, useEffect, useMemo } from 'react';
import { useStreaming } from '../contexts/streamingContext/useStreamingContext';

/**
 * Comprehensive hook for all AI status information
 * Returns everything a component needs for AI generation UI
 */
export function useAiStatus() {
  
  // Destructure all streaming events at the beginning
  const {
    isConnected,
    connectionError,
    eventLlmGenerationStarted,
    eventLlmGenerationUpdate,
    eventLlmGenerationCompleted,
    eventLlmGenerationFailed,
    eventImageGenerationStarted,
    eventImageGenerationUpdate,
    eventImageGenerationCompleted,
    eventImageGenerationFailed,
    eventAiQueueUpdate,
    lastActivity
  } = useStreaming();
  
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
          queueItem: eventLlmGenerationStarted.aiQueueItem,
          type: 'llm'
        });
        break;
      case 'imageStarted':
        setActiveGeneration({
          state: 'generating',
          queueItem: eventImageGenerationStarted.aiQueueItem,
          type: 'image'
        });
        break;
      case 'llmCompleted':
        setActiveGeneration({
          state: 'completed',
          queueItem: eventLlmGenerationCompleted.aiQueueItem,
          type: 'llm'
        });
        break;
      case 'llmFailed':
        setActiveGeneration({
          state: 'failed',
          queueItem: eventLlmGenerationFailed.aiQueueItem,
          type: 'llm'
        });
        break;
      case 'imageCompleted':
        setActiveGeneration({
          state: 'completed',
          queueItem: eventImageGenerationCompleted.aiQueueItem,
          type: 'image'
        });
        break;
      case 'imageFailed':
        setActiveGeneration({
          state: 'failed',
          queueItem: eventImageGenerationFailed.aiQueueItem,
          type: 'image'
        });
        break;
    }
  };

  const handleResetStreamingText = () => {
    setStreamingText({
      generationId: eventLlmGenerationStarted.generationId,
      partialText: null,
      tokensSoFar: null
    });
  };

  const handleResetStreamingImage = () => {
    setStreamingImage({
      generationId: eventImageGenerationStarted.generationId,
      elapsedSeconds: null
    });
  };

  const handleUpdateStreamingText = () => {
    setStreamingText({
      partialText: eventLlmGenerationUpdate.partialText,
      tokensSoFar: eventLlmGenerationUpdate.tokensSoFar
    });
  };

  const handleUpdateStreamingImage = () => {
    setStreamingImage({
      elapsedSeconds: eventImageGenerationUpdate.elapsedSeconds
    });
  };

  // Event handlers using clean useEffect pattern
  useEffect(() => {
    if (eventLlmGenerationStarted) {
      handleActiveGeneration('llmStarted');
      handleResetStreamingText();
      setLlmStatus('initializing...');
    }
  }, [eventLlmGenerationStarted]);

  useEffect(() => {
    if (eventImageGenerationStarted) {
      handleActiveGeneration('imageStarted');
      handleResetStreamingImage();
      setImageStatus('initializing...');
    }
  }, [eventImageGenerationStarted]);

  useEffect(() => {
    if (eventLlmGenerationUpdate) {
      handleUpdateStreamingText();
      setLlmStatus('generating');
    }
  }, [eventLlmGenerationUpdate]);

  useEffect(() => {
    if (eventImageGenerationUpdate) {
      handleUpdateStreamingImage();
      setImageStatus('generating');
    }
  }, [eventImageGenerationUpdate]);

  useEffect(() => {
    if (eventLlmGenerationCompleted) {
      handleActiveGeneration('llmCompleted');
      setLlmStatus('completed');
    }
  }, [eventLlmGenerationCompleted]);

  useEffect(() => {
    if (eventLlmGenerationFailed) {
      handleActiveGeneration('llmFailed');
      setLlmStatus('failed');
    }
  }, [eventLlmGenerationFailed]);

  useEffect(() => {
    if (eventImageGenerationCompleted) {
      handleActiveGeneration('imageCompleted');
      setImageStatus('completed');
    }
  }, [eventImageGenerationCompleted]);

  useEffect(() => {
    if (eventImageGenerationFailed) {
      handleActiveGeneration('imageFailed');
      setImageStatus('failed');
    }
  }, [eventImageGenerationFailed]);

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
    if (!eventAiQueueUpdate || !eventAiQueueUpdate.allAiQueueItems) {
      return {
        total: 0,
        pending: 0,
        processing: 0,
        completed: 0,
        failed: 0,
        items: []
      };
    }

    const items = eventAiQueueUpdate.allAiQueueItems;
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
      trigger: eventAiQueueUpdate.trigger
    };
  }, [eventAiQueueUpdate]);

  const computedLlmStatus = useMemo(() => {
    return {
      generationId: streamingText.generationId,
      promptType: eventLlmGenerationStarted?.aiQueueItem?.promptType || null,
      promptName: eventLlmGenerationStarted?.aiQueueItem?.promptName || null,
      status: llmStatus,
      partialText: streamingText.partialText,
      tokensSoFar: streamingText.tokensSoFar,
      result: eventLlmGenerationCompleted?.result || null,
      error: eventLlmGenerationFailed?.error || null,
      startedAt: eventLlmGenerationStarted?.aiQueueItem?.startedAt || null
    };
  }, [
    eventLlmGenerationStarted,
    eventLlmGenerationCompleted,
    eventLlmGenerationFailed,
    streamingText,
    llmStatus
  ]);

  const computedImageStatus = useMemo(() => {

    // Only create imageUrl if we have an imagePath
    const imageUrl = eventImageGenerationCompleted?.result?.imagePath 
      ? `http://localhost:5000/api/monsters/card-art/${eventImageGenerationCompleted.result.imagePath}`
      : null;

    return {
      generationId: streamingImage.generationId,
      promptName: eventImageGenerationStarted?.aiQueueItem?.promptName || null,
      status: imageStatus,
      elapsedSeconds: streamingImage.elapsedSeconds || null,
      result: eventImageGenerationCompleted?.result || null,
      error: eventImageGenerationFailed?.error || null,
      startedAt: eventImageGenerationStarted?.aiQueueItem?.startedAt || null,
      imageUrl
    };
  }, [
    eventImageGenerationStarted,
    eventImageGenerationCompleted,
    eventImageGenerationFailed,
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