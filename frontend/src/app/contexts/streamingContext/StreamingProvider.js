// StreamingProvider.js - Provides streaming data to the entire app
// SIMPLE CLEAN VERSION: Just useState + useEffect, no complex logic
// All computation logic moved to dedicated hooks

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

  // Simple pass-through - no computation logic here
  const contextValue = {
    ...streamingState
  };

  return (
    <StreamingContext.Provider value={contextValue}>
      {children}
    </StreamingContext.Provider>
  );
}

export default StreamingProvider;