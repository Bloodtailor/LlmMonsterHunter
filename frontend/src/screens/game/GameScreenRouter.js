// GameScreenRouter.js - Routes between different game screens
// Uses NavigationContext to determine which game screen to show
// Handles all game-specific navigation (homebase, dungeon screens, etc.)

import React from 'react';
import { useNavigation } from '../../app/contexts/NavigationContext/index.js';

// Import game screens
import TitleScreen from './TitleScreen.js';
import CharacterCreationScreen from './CharacterCreationScreen.js';
import FirstRunOpeningScreen from './FirstRunOpeningScreen.js';
import HomeBaseScreen from './HomeBaseScreen.js';
import MonsterSanctuaryScreen from './MonsterSanctuaryScreen.js';
import MonsterChatScreen from './MonsterChatScreen.js';
import MonsterEvolutionScreen from './MonsterEvolutionScreen.js';

// Import dungeon screens
import { DungeonEntranceScreen } from '../../components/dungeon/index.js';
import DungeonDoorsScreen from '../../components/dungeon/screens/DungeonDoorsScreen.js';
import DungeonLocationScreen from '../../components/dungeon/screens/DungeonLocationScreen.js';
import DungeonBattleScreen from '../../components/battle/screens/DungeonBattleScreen.js';

/**
 * GameScreenRouter component
 * Routes between different game screens based on NavigationContext state
 * Only handles game screens - App.js handles top-level navigation
 */
function GameScreenRouter() {
  const { currentGameScreen } = useNavigation();

  // Render the appropriate game screen
  switch (currentGameScreen) {
    case 'title':
      return <TitleScreen />;

    case 'character-creation':
      return <CharacterCreationScreen />;

    case 'first-run-opening':
      return <FirstRunOpeningScreen />;

    case 'homebase':
      return <HomeBaseScreen />;

    case 'sanctuary':
      return <MonsterSanctuaryScreen />;

    case 'monster-chat':
      return <MonsterChatScreen />;

    case 'monster-evolution':
      return <MonsterEvolutionScreen />;

    case 'dungeon-entrance':
      return <DungeonEntranceScreen />;

    case 'dungeon-doors':
      return <DungeonDoorsScreen />;

    case 'dungeon-location':
      return <DungeonLocationScreen />;

    case 'dungeon-battle':
      return <DungeonBattleScreen />;

    default:
      // Fallback to homebase if unknown screen
      console.warn(`Unknown game screen: ${currentGameScreen}`);
      return <HomeBaseScreen />;
  }
}

export default GameScreenRouter;
