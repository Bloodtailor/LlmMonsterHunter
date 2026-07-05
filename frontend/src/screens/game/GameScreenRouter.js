// GameScreenRouter.js - Routes between different game screens
// Uses NavigationContext to determine which game screen to show
// Handles all game-specific navigation (homebase, dungeon screens, etc.)

import React from 'react';
import { useNavigation } from '../../app/contexts/NavigationContext/index.js';

// Import game screens
import HomeBaseScreen from './HomeBaseScreen.js';
import MonsterSanctuaryScreen from './MonsterSanctuaryScreen.js';

// Import dungeon screens
import { DungeonEntranceScreen } from '../../components/dungeon/index.js';
import DungeonDoorsScreen from '../../components/dungeon/screens/DungeonDoorsScreen.js';
import DungeonLocationScreen from '../../components/dungeon/screens/DungeonLocationScreen.js';

/**
 * GameScreenRouter component
 * Routes between different game screens based on NavigationContext state
 * Only handles game screens - App.js handles top-level navigation
 */
function GameScreenRouter() {
  const { currentGameScreen } = useNavigation();

  // Render the appropriate game screen
  switch (currentGameScreen) {
    case 'homebase':
      return <HomeBaseScreen />;
      
    case 'sanctuary':
      return <MonsterSanctuaryScreen />;
      
    case 'dungeon-entrance':
      return <DungeonEntranceScreen />;
      
    case 'dungeon-doors':
      return <DungeonDoorsScreen />;

    case 'dungeon-location':
      return <DungeonLocationScreen />;

    default:
      // Fallback to homebase if unknown screen
      console.warn(`Unknown game screen: ${currentGameScreen}`);
      return <HomeBaseScreen />;
  }
}

export default GameScreenRouter;