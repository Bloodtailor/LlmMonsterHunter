// Main React application component - UPDATED WITH NAVIGATION CONTEXT
// Now uses NavigationContext for game screen management
// Clean separation between top-level navigation and game navigation

import React, { useState } from 'react';

// Import NavButtons component from shared UI library
import NavButtons from './shared/ui/Button/NavButtons.js';

// Providers
import AppProvider from './app/AppProvider.js';

// Game Screen Router
import GameScreenRouter from './screens/game/GameScreenRouter.js';

// Developer Screens
import ApiServicesTestScreen from './screens/developer/ApiServicesTestScreen';
import StyleTestScreen from './screens/developer/StyleTestScreen';
import BYOComponentTestScreen from './screens/developer/BYOComponentTestScreen';
import CoCaTokDemo from './screens/developer/CoCaTokDemo';
import ExplosionDemo from './screens/developer/ExplosionDemo';
import StreamingDisplay from './components/streaming/StreamingDisplay.js';
import DungeonContextPanel from './components/debug/DungeonContextPanel.js';
import EventTestScreen from './screens/developer/EventTestScreen.js';
import DeveloperScreen from './screens/developer/DeveloperScreen.js';
import UiExamplesScreen from './screens/developer/UiExamplesScreen.js';

function App() {

  // Top-level navigation state - separates game from developer screens
  const [currentScreen, setCurrentScreen] = useState('game'); 

  
  // Navigation button configurations - single Game entry point
  const navigationButtons = [
    {
      screen: 'game',
      label: '🎮 Game'
    },
    {
      screen: 'api-services',
      label: '🧪 API Tests'
    },
    {
      screen: 'dev',
      label: '🧪 Developer'
    },
    {
      screen: 'event-test',
      label: '🧪 Event Context Test'
    },
    {
      screen: 'cocatok-demo',
      label: '❄️ CoCaTok Demo'
    },
    {
      screen: 'explosion-demo', 
      label: '💥 Explosion Demo'
    },
    {
      screen: 'style-test',
      label: '🧪 Style Test'
    },
    {
      screen: 'ui-examples',
      label: '🧪 UI Examples'
    },
    {
      screen: 'byo-component',
      label: '🧱 BYO Component'
    }
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

          {/* Global Streaming Display (right side) */}
          <StreamingDisplay />

          {/* Global LLM-context debug panel (left side) */}
          <DungeonContextPanel />
        </header>

        {/* Main Content Area */}
        <main className="app-main">
          {currentScreen === 'game' && <GameScreenRouter />}
          {currentScreen === 'api-services' && <ApiServicesTestScreen />}
          {currentScreen === 'dev' && <DeveloperScreen />}
          {currentScreen === 'event-test' && <EventTestScreen />}
          {currentScreen === 'cocatok-demo' && <CoCaTokDemo />}
          {currentScreen === 'explosion-demo' && <ExplosionDemo />}
          {currentScreen === 'style-test' && <StyleTestScreen />}
          {currentScreen === 'ui-examples' && <UiExamplesScreen />}
          {currentScreen === 'byo-component' && <BYOComponentTestScreen />}
        </main>

        <footer className='app-footer'>LLM Monster Hunter</footer>

      </div>
    </AppProvider>
  );
}

export default App;