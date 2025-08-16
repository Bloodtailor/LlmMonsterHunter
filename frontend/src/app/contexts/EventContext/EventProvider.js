// eventProvider.js - Provides streaming data to the entire app
// SIMPLE CLEAN VERSION: Just useState + useEffect, no complex logic
// All computation logic moved to dedicated hooks

import { EventContext } from './EventContext.js';
import { useSSE } from '../../../api/core/useSSE.js';
import { useAiEvents } from '../../../api/events/useAiEvents.js';

function EventProvider({ children }) {
  
const aiEvents = useAiEvents();

  // Use AI event handlers
  const combinedHandlers = aiEvents.eventHandlers;

  // Call useSSE once with combined handlers
  const { isConnected, connectionError, connect, disconnect } = useSSE(combinedHandlers);

  // Create context value using spread syntax
  const contextValue = {
    isConnected,
    connectionError,
    connect,
    disconnect,
    ...aiEvents.state
  };

  return (
    <EventContext.Provider value={contextValue}>
      {children}
    </EventContext.Provider>
  );
}

export default EventProvider;