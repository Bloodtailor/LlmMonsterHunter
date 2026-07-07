// useBattleContext.js - Hook to access battle state from any component
// Consumer hook for BattleContext following the useDungeon pattern

import { useContext } from 'react';
import { BattleContext } from './BattleContext.js';

/**
 * Hook to access battle state and actions
 * Must be used within a BattleProvider
 *
 * @returns {object} Battle state and functions
 */
export function useBattleContext() {
  const context = useContext(BattleContext);

  if (context === null) {
    throw new Error(
      'useBattleContext must be used within a BattleProvider. ' +
        'Make sure your component is wrapped with <BattleProvider>.',
    );
  }

  return context;
}
