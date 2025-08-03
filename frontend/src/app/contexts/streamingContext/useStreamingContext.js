// useStreaming.js - Hook to access streaming data from anywhere in the app
// This is the consumer hook that components use to get streaming state
// Different from app/hooks/useStreaming.js which is the domain hook

import { useContext } from 'react';
import { StreamingContext } from './StreamingContext.js';

/**
 * Hook to access global streaming state from any component
 * Must be used within a StreamingProvider
 * 
 * @returns {object} Streaming state and controls
 */
export function useStreaming() {
  const context = useContext(StreamingContext);
  
  if (context === null) {
    throw new Error(
      'useStreaming must be used within a StreamingProvider. ' +
      'Make sure your component is wrapped with <StreamingProvider>.'
    );
  }
  
  return context;
}