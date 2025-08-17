// eventProvider.js - Provides streaming data to the entire app
// SIMPLE CLEAN VERSION: Just useState + useEffect, no complex logic
// All computation logic moved to dedicated hooks
// Now supports both AI and Workflow events

import { EventContext } from './EventContext.js';
import { useSSE } from '../../../api/core/useSSE.js';
import { useAiEvents } from '../../../api/events/useAiEvents.js';
import { useWorkflowEvents } from '../../../api/events/useWorkflowEvents.js';

function EventProvider({ children }) {
  
  // Get both AI and workflow events
  const aiEvents = useAiEvents();
  const workflowEvents = useWorkflowEvents();

  // Combine event handlers from both systems
  const combinedHandlers = {
    ...aiEvents.eventHandlers,
    ...workflowEvents.eventHandlers
  };

  // Call useSSE once with combined handlers
  const { isConnected, connectionError, connect, disconnect } = useSSE(combinedHandlers);

  // Create context value using spread syntax for both event systems
  const contextValue = {
    isConnected,
    connectionError,
    connect,
    disconnect,
    ...aiEvents.state,
    ...workflowEvents.state
  };

  return (
    <EventContext.Provider value={contextValue}>
      {children}
    </EventContext.Provider>
  );
}

export default EventProvider;