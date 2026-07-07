// BattleProvider.js - Orchestration for battle state management
// Same structure as DungeonProvider: state + actions + SSE events

import React from 'react';
import { BattleContext } from './BattleContext.js';
import { useBattleState } from './hooks/useBattleState.js';
import { useBattleActions } from './hooks/useBattleActions.js';
import { useBattleEvents } from './hooks/useBattleEvents.js';

/**
 * BattleProvider component
 * @param {object} props - Provider props
 * @param {React.ReactNode} props.children - Child components
 */
function BattleProvider({ children }) {
  // State management
  const stateHook = useBattleState();

  // Actions (select, execute, advance log, reset)
  const actionsHook = useBattleActions(stateHook);

  // SSE event processing (battle start, narrations, round completion)
  useBattleEvents(stateHook);

  // Clean context value using spread syntax
  const contextValue = {
    ...stateHook.state,
    ...actionsHook.actions,
  };

  return <BattleContext.Provider value={contextValue}>{children}</BattleContext.Provider>;
}

export default BattleProvider;
