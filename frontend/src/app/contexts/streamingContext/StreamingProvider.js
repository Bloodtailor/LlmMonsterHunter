// StreamingProvider.js - Provides streaming data to the entire app
// SIMPLE CLEAN VERSION: Just useState + useEffect, no complex logic

import React, { useState, useEffect } from 'react';
import { StreamingContext } from './StreamingContext.js';
import { useEventSource } from '../../hooks/useEventsource.js';
import { streamingEventRegistry, initialStreamingState } from '../../streaming/index.js';
import { STREAMING_EVENTS_URL } from '../../../api/services/streaming.js';

function StreamingProvider({ children, autoConnect = true }) {
  
  // Use generic EventSource hook with streaming-specific registry
  const streamingState = useEventSource(
    STREAMING_EVENTS_URL, 
    streamingEventRegistry, 
    { 
      autoConnect,
      initialState: initialStreamingState 
    }
  );

  // Simple state tracking for active generation
  const [activeGeneration, setActiveGeneration] = useState({ 
    state: null, 
    queueItem: null, 
    type: null 
  });

  // Update activeGeneration when LLM events change
  useEffect(() => {
    if (streamingState.llmGenerationStarted) {
      setActiveGeneration({
        state: 'generating',
        queueItem: streamingState.llmGenerationStarted.aiQueueItem,
        type: 'llm'
      });
    }
  }, [streamingState.llmGenerationStarted]);

  useEffect(() => {
    if (streamingState.llmGenerationCompleted) {
      setActiveGeneration({
        state: 'completed',
        queueItem: streamingState.llmGenerationCompleted.aiQueueItem,
        type: 'llm'
      });
    }
  }, [streamingState.llmGenerationCompleted]);

  useEffect(() => {
    if (streamingState.llmGenerationFailed) {
      setActiveGeneration({
        state: 'failed',
        queueItem: streamingState.llmGenerationFailed.aiQueueItem,
        type: 'llm'
      });
    }
  }, [streamingState.llmGenerationFailed]);

  // Update activeGeneration when Image events change
  useEffect(() => {
    if (streamingState.imageGenerationStarted) {
      setActiveGeneration({
        state: 'generating',
        queueItem: streamingState.imageGenerationStarted.aiQueueItem,
        type: 'image'
      });
    }
  }, [streamingState.imageGenerationStarted]);

  useEffect(() => {
    if (streamingState.imageGenerationCompleted) {
      setActiveGeneration({
        state: 'completed',
        queueItem: streamingState.imageGenerationCompleted.aiQueueItem,
        type: 'image'
      });
    }
  }, [streamingState.imageGenerationCompleted]);

  useEffect(() => {
    if (streamingState.imageGenerationFailed) {
      setActiveGeneration({
        state: 'failed',
        queueItem: streamingState.imageGenerationFailed.aiQueueItem,
        type: 'image'
      });
    }
  }, [streamingState.imageGenerationFailed]);

  // Simple currentActivity based on activeGeneration state
  const getCurrentActivity = () => {
    // No active generation = idle
    if (!activeGeneration.state) {
      return { type: null, label: 'Idle', progress: null };
    }
    
    // Failed or completed = idle
    if (activeGeneration.state === 'failed' || activeGeneration.state === 'completed') {
      return { type: null, label: 'Idle', progress: null };
    }
    
    // Currently generating
    if (activeGeneration.state === 'generating') {
      if (activeGeneration.type === 'llm') {
        // Check for token progress
        if (streamingState.llmGenerationUpdate?.tokensSoFar) {
          return {
            type: 'llm',
            label: '🤖 Generating Text',
            progress: `${streamingState.llmGenerationUpdate.tokensSoFar} tokens`
          };
        }
        // No progress yet
        return {
          type: 'llm',
          label: '🤖 Starting LLM',
          progress: 'Initializing...'
        };
      }
      
      if (activeGeneration.type === 'image') {
        // Check for elapsed time
        if (streamingState.imageGenerationUpdate?.elapsedSeconds) {
          return {
            type: 'image',
            label: '🎨 Generating Image',
            progress: `${streamingState.imageGenerationUpdate.elapsedSeconds}s`
          };
        }
        // No progress yet
        return {
          type: 'image',
          label: '🎨 Starting Image',
          progress: 'Initializing...'
        };
      }
    }
    
    return { type: null, label: 'Idle', progress: null };
  };

  // Context value with simple computed values
  const contextValue = {
    ...streamingState,
    activeGeneration,
    currentActivity: getCurrentActivity()
  };

  return (
    <StreamingContext.Provider value={contextValue}>
      {children}
    </StreamingContext.Provider>
  );
}

export default StreamingProvider;