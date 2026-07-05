// eventProvider.js - Owns the SSE connection, provides connection state only
// SSE events are handled OUTSIDE React by pure handler modules:
//   useSSE -> aiEventHandlers / workflowEventHandlers -> broadcastEvent
//     -> state stores (aiStateStore, workflowStateStore) + event subscribers
// This provider never re-renders on SSE events - only on connect/disconnect

import { EventContext } from './EventContext.js';
import { useSSE } from '../../../api/core/useSSE.js';
import { aiEventHandlers } from '../../../api/events/aiEventHandlers.js';
import { workflowEventHandlers } from '../../../api/events/workflowEventHandlers.js';

// Module-level constant - stable reference, combined once
const sseEventHandlers = {
  ...aiEventHandlers,
  ...workflowEventHandlers
};

function EventProvider({ children }) {

  // Call useSSE once with the pure (non-React) handlers
  const { isConnected, connectionError, connect, disconnect } = useSSE(sseEventHandlers);

  // Context value is connection state only
  const contextValue = {
    isConnected,
    connectionError,
    connect,
    disconnect
  };

  return (
    <EventContext.Provider value={contextValue}>
      {children}
    </EventContext.Provider>
  );
}

export default EventProvider;
