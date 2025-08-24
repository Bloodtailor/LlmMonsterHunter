// ContinueToDoorsButton.js - Minimal component for dungeon continue button
// PERFORMANCE FOCUSED - Only subscribes to isDoorsReady, doesn't rerender on text updates
// Handles navigation internally to keep parent screen clean

import React from 'react';
import { Button } from '../../../shared/ui/index.js';
import { useNavigation } from '../../../app/contexts/NavigationContext/index.js';
import { useDungeon } from '../../../app/contexts/DungeonContext/index.js';

/**
 * ContinueToDoorsButton component
 * Only handles continue button state and navigation - minimal rerenders
 * Follows healthy pattern for context consumers
 */
function ContinueToDoorsButton() {
  // Only consume what we need - just isDoorsReady
  const { isDoorsReady } = useDungeon();
  const { navigateToGameScreen } = useNavigation();

  // Handle continue to doors
  const handleContinue = () => {
    navigateToGameScreen('dungeon-doors');
  };

  // Button styling for consistent appearance
  const buttonContainerStyles = {
    display: 'flex',
    justifyContent: 'center',
    padding: '24px'
  };

  return (
    <div style={buttonContainerStyles}>
      <Button 
        size="xl" 
        icon="🚪"
        onClick={handleContinue}
        disabled={!isDoorsReady}
        variant={isDoorsReady ? 'primary' : 'secondary'}
      >
        {isDoorsReady ? 'Continue to Doors' : 'Generating Doors...'}
      </Button>
    </div>
  );
}

export default ContinueToDoorsButton;