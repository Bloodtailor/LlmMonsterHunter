// Main React application component
// Two top-level destinations: the game itself, and the developer hub
// (all test/demo/tooling screens live inside DeveloperScreen's sub-nav)

import React, { useState } from 'react';

// Import NavButtons component from shared UI library
import NavButtons from './shared/ui/Button/NavButtons.js';
import Button from './shared/ui/Button/Button.js';

// Providers
import AppProvider from './app/AppProvider.js';

// Game Screen Router
import GameScreenRouter from './screens/game/GameScreenRouter.js';

// Developer hub (hosts every dev screen behind its own sub-navigation)
import DeveloperScreen from './screens/developer/DeveloperScreen.js';

// Global overlays
import StreamingDisplay from './components/streaming/StreamingDisplay.js';
import DungeonContextPanel from './components/debug/DungeonContextPanel.js';
import SettingsOverlay from './components/settings/SettingsOverlay.js';

function App() {
  // Top-level navigation state - separates game from developer screens
  const [currentScreen, setCurrentScreen] = useState('game');

  // Settings live in a header overlay, never a screen: opening them must
  // not unmount a live dungeon/battle, and the gear works on the title
  // screen and Developer view alike
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  const navigationButtons = [
    {
      screen: 'game',
      label: '🎮 Game',
    },
    {
      screen: 'dev',
      label: '🧪 Developer',
    },
  ];

  // Main application
  return (
    <AppProvider>
      <div className="App">
        {/* App Header with Title Left, Navigation Centered */}
        <header className="app-header">
          <h1>🎮 Monster Hunter Game</h1>

          {/* Navigation using NavButtons component */}
          <NavButtons
            buttons={navigationButtons}
            activeScreen={currentScreen}
            onScreenChange={setCurrentScreen}
            spacing="tight"
            alignment="left"
          />

          {/* Settings gear - available everywhere */}
          <Button size="sm" variant="ghost" onClick={() => setIsSettingsOpen(true)}>
            ⚙️ Settings
          </Button>

          {/* Global Streaming Display (right side) */}
          <StreamingDisplay />

          {/* Global LLM-context debug panel (left side) */}
          <DungeonContextPanel />

          {/* Settings overlay (opened by the gear) */}
          <SettingsOverlay isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
        </header>

        {/* Main Content Area */}
        <main className="app-main">
          {currentScreen === 'game' && <GameScreenRouter />}
          {currentScreen === 'dev' && <DeveloperScreen />}
        </main>

        <footer className="app-footer">LLM Monster Hunter</footer>
      </div>
    </AppProvider>
  );
}

export default App;
