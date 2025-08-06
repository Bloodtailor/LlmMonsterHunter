// useStreaming.js - Hook to access streaming data from anywhere in the app
// This is the consumer hook that components use to get streaming state
// Different from app/hooks/useStreaming.js which is the domain hook

import { useContext } from 'react';
import { EventContext } from './EventContext.js';

/**
 * Hook to access global streaming state from any component
 * Must be used within a StreamingProvider
 * 
 * @returns {object} Streaming state and controls
 */
export function useEventContext() {
  const context = useContext(EventContext);
  
  if (context === null) {
    throw new Error(
      'useEventContext must be used within a EventProvider. ' +
      'Make sure your component is wrapped with <EventProvider>.'
    );
  }
  
  return context;
}