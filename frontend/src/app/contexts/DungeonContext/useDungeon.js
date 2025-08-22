// useDungeon.js - Hook to access dungeon state from any component
// Consumer hook for DungeonContext following the useParty/useEventContext pattern
// Provides clean API for dungeon workflow state and actions

import { useContext } from 'react';
import { DungeonContext } from './DungeonContext.js';

/**
 * Hook to access dungeon state and actions
 * Must be used within a DungeonProvider (typically within game screens)
 * 
 * @returns {object} Dungeon state and functions
 */
export function useDungeon() {
  const context = useContext(DungeonContext);
  
  if (context === null) {
    throw new Error(
      'useDungeon must be used within a DungeonProvider. ' +
      'Make sure your component is wrapped with <DungeonProvider>.'
    );
  }
  
  return context;
}