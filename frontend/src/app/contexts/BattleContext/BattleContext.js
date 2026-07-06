// BattleContext.js - Context for battle state management
// Manages battle rounds, action selection, the click-through battle log,
// and outcomes. Follows the established DungeonContext pattern.

import { createContext } from 'react';

/**
 * Battle context for LLM-refereed combat
 * Provides battle state (conditions, phases), action selection,
 * narration queue, and round actions
 */
export const BattleContext = createContext(null);
