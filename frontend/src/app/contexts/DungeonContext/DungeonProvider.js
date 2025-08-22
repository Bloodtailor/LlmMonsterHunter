// DungeonProvider.js - Minimal orchestration for dungeon state management
// Starting simple: just entry workflow and text streaming

import React from 'react';
import { DungeonContext } from './DungeonContext.js';
import { useDungeonState } from './hooks/useDungeonState.js';
import { useDungeonActions } from './hooks/useDungeonActions.js';
import { useDungeonEvents } from './hooks/useDungeonEvents.js';

/**
 * DungeonProvider component
 * Minimal version: just workflow entry and text streaming
 * @param {object} props - Provider props
 * @param {React.ReactNode} props.children - Child components
 */
function DungeonProvider({ children }) {
  
  // State management (minimal: workflow + text)
  const stateHook = useDungeonState();
  
  // Actions (minimal: just enter dungeon)
  const actionsHook = useDungeonActions(stateHook);
  
  // SSE event processing (minimal: generation ID + text streaming)
  useDungeonEvents(stateHook);

  // Clean context value using spread syntax
  const contextValue = {
    ...stateHook.state,      // currentWorkflowId, isLoading, error, entryText, etc.
    ...actionsHook.actions   // enterDungeon, resetDungeon
  };

  return (
    <DungeonContext.Provider value={contextValue}>
      {children}
    </DungeonContext.Provider>
  );
}

export default DungeonProvider;