// eventProvider.js - Provides streaming data to the entire app
// SIMPLE CLEAN VERSION: Just useState + useEffect, no complex logic
// All computation logic moved to dedicated hooks

import { EventContext } from './EventContext.js';
import { useEventSource } from './useEventsource.js';
import { EventRegistry, initialEventState } from './EventRegistry.js';

function EventProvider({ children, autoConnect = true }) {

  const EVENTS_URL = 'http://localhost:5000/api/sse/events';
  
  // Use generic EventSource hook with streaming-specific registry
  const eventState = useEventSource(
    EVENTS_URL, 
    EventRegistry, 
    { 
      autoConnect,
      initialState: initialEventState 
    }
  );

  // Simple pass-through - no computation logic here
  const contextValue = {
    ...eventState
  };

  return (
    <EventContext.Provider value={contextValue}>
      {children}
    </EventContext.Provider>
  );
}

export default EventProvider;