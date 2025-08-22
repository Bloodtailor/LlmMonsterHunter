// DungeonContext.js - Context for dungeon state management
// Manages dungeon workflow state, entry text streaming, and door generation
// Follows established context pattern from NavigationContext and EventContext

import { createContext } from 'react';

/**
 * Dungeon context for dungeon workflow and state management
 * Provides dungeon workflow state, entry text, doors, and navigation functions
 * Handles all dungeon-related SSE event processing and state persistence
 */
export const DungeonContext = createContext(null);