// StreamingProvider.js - Provides streaming data to the entire app
// UPDATED: Now just returns streamingState directly (cleaner separation of concerns)
// UI state management moved to components that need it

import React from 'react';
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

  // Return streamingState directly - no more UI state management here!
  // This follows better separation of concerns: provider = data, components = UI
  const contextValue = streamingState;

  return (
    <StreamingContext.Provider value={contextValue}>
      {children}
    </StreamingContext.Provider>
  );
}

export default StreamingProvider;