// AutoEnterDungeonEffect.js - Side effect component for auto-entering dungeon
// PERFORMANCE FOCUSED - Renders nothing, only handles side effects
// Isolated context subscription that doesn't affect parent components

import { useEffect, useRef } from 'react';
import { useDungeon } from '../../../app/contexts/DungeonContext/index.js';

/**
 * AutoEnterDungeonEffect component
 * Invisible component that only handles the auto-enter dungeon side effect
 * Doesn't render anything - pure side effect component
 */
function AutoEnterDungeonEffect() {
  // Ref to track if we've already called enterDungeon
  const hasEnteredRef = useRef(false);
  
  // Subscribe to context for auto-enter (isolated from parent)
  const { enterDungeon } = useDungeon();

  // Auto-enter dungeon when component mounts (only once)
  useEffect(() => {
    if (!hasEnteredRef.current) {
      console.log('AutoEnterDungeonEffect: Auto-entering dungeon');
      hasEnteredRef.current = true;
      enterDungeon();
    }
  }, [enterDungeon]);

  // This component renders nothing - pure side effect
  return null;
}

export default AutoEnterDungeonEffect;