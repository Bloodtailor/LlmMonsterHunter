// Main React application component - UPDATED WITH BUTTON GROUP UI COMPONENT
// Now uses ButtonGroup and Button components from shared UI library
// Clean navigation with Home Base as the new game preparation hub

import React, { useState, useEffect } from 'react';

// Import NavButtons component from shared UI library
import NavButtons from './shared/ui/Button/NavButtons.js';
import { Button } from './shared/ui';

// Providers
import AppProvider from './app/AppProvider.js';

// Game Screen
import MonsterSanctuaryScreen from './screens/game/MonsterSanctuaryScreen.js';
import HomeBaseScreen from './screens/game/HomeBaseScreen.js';
import AppLoadingScreen from './screens/game/AppLoadingScreen.js';

// Developer Screens
import ApiServicesTestScreen from './screens/developer/ApiServicesTestScreen';
import StyleTestScreen from './screens/developer/StyleTestScreen';
import BYOComponentTestScreen from './screens/developer/BYOComponentTestScreen';
import CoCaTokDemo from './screens/developer/CoCaTokDemo';
import ExplosionDemo from './screens/developer/ExplosionDemo';
import StreamingDisplay from './components/streaming/StreamingDisplay.js';
import EventTestScreen from './screens/developer/EventTestScreen.js';

function App() {

  // Navigation state - Home Base is the main game screen
  const [currentScreen, setCurrentScreen] = useState('homebase'); 

  
  // Navigation button configurations
  const navigationButtons = [
    {
      screen: 'api-services',
      label: '🧪 API Tests'
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
      screen: 'sanctuary',
      label: '🏛️ Monster Sanctuary'
    },
    {
      screen: 'homebase',
      label: '🏠 Home Base'
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

            {/* Global Streaming Display */}
            <StreamingDisplay />
          </header>

          {/* Main Content Area */}
          <main className="app-main">
            {currentScreen === 'api-services' && <ApiServicesTestScreen />}
            {currentScreen === 'event-test' && <EventTestScreen />}
            {currentScreen === 'cocatok-demo' && <CoCaTokDemo />}
            {currentScreen === 'explosion-demo' && <ExplosionDemo />}
            {currentScreen === 'style-test' && <StyleTestScreen />}
            {currentScreen === 'sanctuary' && <MonsterSanctuaryScreen />}
            {currentScreen === 'homebase' && <HomeBaseScreen />}
            {currentScreen === 'byo-component' && <BYOComponentTestScreen />}
          </main>

          <footer className='app-footer'>LLM Monster Hunter</footer>

          
        </div>
    </AppProvider>
  );
}

export default App;