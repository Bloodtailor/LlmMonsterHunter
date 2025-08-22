// GameScreenRouter.js - Routes between different game screens
// Uses NavigationContext to determine which game screen to show
// Handles all game-specific navigation (homebase, dungeon screens, etc.)

import React from 'react';
import { useNavigation } from '../../app/contexts/NavigationContext/index.js';

// Import game screens
import HomeBaseScreen from './HomeBaseScreen.js';
import MonsterSanctuaryScreen from './MonsterSanctuaryScreen.js';
// TODO: Import dungeon screens when they're created
// import DungeonEntranceScreen from '../../components/dungeon/screens/DungeonEntranceScreen.js';
// import DungeonDoorsScreen from '../../components/dungeon/screens/DungeonDoorsScreen.js';

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
      // TODO: Uncomment when DungeonEntranceScreen is created
      // return <DungeonEntranceScreen />;
      return <div>Dungeon Entrance Screen - Coming Soon</div>;
      
    case 'dungeon-doors':
      // TODO: Uncomment when DungeonDoorsScreen is created  
      // return <DungeonDoorsScreen />;
      return <div>Dungeon Doors Screen - Coming Soon</div>;
      
    default:
      // Fallback to homebase if unknown screen
      console.warn(`Unknown game screen: ${currentGameScreen}`);
      return <HomeBaseScreen />;
  }
}

export default GameScreenRouter;