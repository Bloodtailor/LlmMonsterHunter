// StreamingProvider.js - Provides streaming data to the entire app
// Uses generic useEventSource hook + streaming event registry  
// One EventSource connection for the whole app!

import React, { useState, useEffect } from 'react';
import { StreamingContext } from './StreamingContext.js';
import { useEventSource } from '../../hooks/useEventsource.js';
import { streamingEventRegistry, initialStreamingState } from '../../streaming/index.js';
import { STREAMING_EVENTS_URL } from '../../../api/services/streaming.js';

/**
 * StreamingProvider - Wraps your app to provide global streaming state
 * Creates ONE EventSource connection that all components can subscribe to
 * 
 * @param {object} props - StreamingProvider props
 * @param {React.ReactNode} props.children - Child components
 * @param {boolean} props.autoConnect - Auto-connect on mount (default: true)
 */
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
  
  // UI-specific state that components might need
  const [isMinimized, setIsMinimized] = useState(false);
  
  // Auto-expand when generation starts
  useEffect(() => {
    if (streamingState.currentGeneration?.status === 'generating') {
      setIsMinimized(false);
    }
  }, [streamingState.currentGeneration?.status]);

  // Combined context value that any component can access
  const contextValue = {
    // From useEventSource (connection state + event data)
    isConnected: streamingState.isConnected,
    connectionError: streamingState.connectionError,
    currentGeneration: streamingState.currentGeneration,
    streamingText: streamingState.streamingText,
    queueStatus: streamingState.queueStatus,
    lastActivity: streamingState.lastActivity,
    
    // UI state
    isMinimized,
    setIsMinimized,
    
    // Derived state
    isGenerating: streamingState.currentGeneration?.status === 'generating',
    hasActiveGeneration: !!streamingState.currentGeneration,
    
    // Connection controls (passed through from useEventSource)
    connect: streamingState.connect,
    disconnect: streamingState.disconnect
  };

  return (
    <StreamingContext.Provider value={contextValue}>
      {children}
    </StreamingContext.Provider>
  );
}

export default StreamingProvider;