// DungeonResetButton.js - Isolated reset button with context subscription
// PERFORMANCE FOCUSED - Only this small component rerenders on context changes
// Handles dungeon reset without affecting parent screen

import React from 'react';
import { Button } from '../../../shared/ui/index.js';
import { useNavigation } from '../../../app/contexts/NavigationContext/index.js';
import { useDungeon } from '../../../app/contexts/DungeonContext/index.js';

/**
 * DungeonResetButton component
 * Isolated button that handles dungeon reset and navigation
 * Only this component subscribes to context, not the parent screen
 */
function DungeonResetButton() {
  const { navigateToGameScreen } = useNavigation();
  
  // Only consume what we need - just the reset action
  const { resetDungeon } = useDungeon();

  // Handle back to home base with reset
  const handleBackToHome = () => {
    resetDungeon(); // Clear dungeon state
    navigateToGameScreen('homebase');
  };

  return (
    <Button 
      size="md" 
      variant="tertiary"
      onClick={handleBackToHome}
    >
      ← Back to Home Base
    </Button>
  );
}

export default DungeonResetButton;