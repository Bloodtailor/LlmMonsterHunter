// useDungeonState.js - Minimal state for dungeon workflow
// Business-focused state: what do components actually need to know?

import { useState, useCallback } from 'react';

/**
 * Hook for managing minimal dungeon state
 * Focused on business logic rather than technical loading states
 * @returns {object} State values, setters, and reset function
 */
export function useDungeonState() {
  
  // Error state - for critical errors that "crash" the game
  const [isError, setIsError] = useState(false);
  const [error, setError] = useState(null);

  // Entry text streaming
  const [entryText, setEntryText] = useState('');

  // Doors state - for continue button and future door choices
  const [isDoorsReady, setIsDoorsReady] = useState(false);
  const [doors, setDoors] = useState([]); // To be implemented

  // Helper to set error state
  const setErrorState = useCallback((errorMessage) => {
    setIsError(!!errorMessage);
    setError(errorMessage);
  }, []);

  // Reset all state to initial values
  const resetState = useCallback(() => {
    setIsError(false);
    setError(null);
    setEntryText('');
    setIsDoorsReady(false);
    setDoors([]);
  }, []);

  return {
    // Public state (for spreading in provider)
    state: {
      isError,
      error,
      entryText,
      isDoorsReady,
      doors
    },

    // Internal setters (for other hooks)
    setters: {
      setErrorState,
      setEntryText,
      setIsDoorsReady,
      setDoors
    },

    // Utilities
    resetState
  };
}