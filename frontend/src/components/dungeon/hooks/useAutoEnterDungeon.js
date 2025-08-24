// useAutoEnterDungeon.js - Custom hook for auto-entering dungeon on mount
// PERFORMANCE FOCUSED - Isolates the auto-enter logic from the main screen
// Only subscribes to enterDungeon action, doesn't cause screen rerenders

import { useEffect, useRef } from 'react';
import { useDungeon } from '../../../app/contexts/DungeonContext/index.js';

/**
 * Custom hook for auto-entering dungeon when component mounts
 * Handles the ref logic and prevents multiple entries
 * Follows healthy pattern for context consumers
 * 
 * @returns {object} Hook state and utilities
 */
function useAutoEnterDungeon() {
  // Ref to track if we've already called enterDungeon
  const hasEnteredRef = useRef(false);
  
  // Only consume what we need - enterDungeon action and resetDungeon
  const { enterDungeon, resetDungeon } = useDungeon();

  // Auto-enter dungeon when hook is first used (only once)
  useEffect(() => {
    if (!hasEnteredRef.current) {
      console.log('useAutoEnterDungeon: Auto-entering dungeon');
      hasEnteredRef.current = true;
      enterDungeon();
    }
  }, [enterDungeon]);

  // Reset function for when component unmounts/remounts
  const resetAutoEnter = () => {
    hasEnteredRef.current = false;
    resetDungeon(); // Also reset dungeon state
  };

  return {
    hasEntered: hasEnteredRef.current,
    resetAutoEnter
  };
}

export default useAutoEnterDungeon;