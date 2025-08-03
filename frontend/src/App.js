// Main React application component - UPDATED WITH BUTTON GROUP UI COMPONENT
// Now uses ButtonGroup and Button components from shared UI library
// Clean navigation with Home Base as the new game preparation hub

import React, { useState, useEffect } from 'react';
import ApiServicesTestScreen from './screens/ApiServicesTestScreen';
import StyleTestScreen from './screens/StyleTestScreen';
import MyCurrentTestScreen from './screens/MyCurrentTestScreen';
import { PartyProvider } from './app/contexts/PartyContext';
import { StreamingProvider } from './app/contexts/streamingContext';
import BYOComponentTestScreen from './screens/BYOComponentTestScreen';
import CoCaTokDemo from './screens/CoCaTokDemo';
import ExplosionDemo from './screens/ExplosionDemo';
import StreamingDisplay from './components/streaming/StreamingDisplay.js';
import StreamingTestScreen from './screens/StreamingTextScreen.js';

// Import NavButtons component from shared UI library
import NavButtons from './shared/ui/Button/NavButtons.js';

function App() {

  // Navigation state - Home Base is the main game screen
  const [currentScreen, setCurrentScreen] = useState('current-test'); 
  
  // Navigation button configurations
  const navigationButtons = [
    {
      screen: 'api-services',
      label: '🧪 API Tests'
    },
    {
      screen: 'streaming',
      label: '🧪 Streaming Context Test'
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
      screen: 'current-test',
      label: '🔬 Current Test'
    },
    {
      screen: 'byo-component',
      label: '🧱 BYO Component'
    }
  ];

  // Main application
  return (
    <StreamingProvider>
      <PartyProvider>
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
            {currentScreen === 'streaming' && <StreamingTestScreen />}
            {currentScreen === 'cocatok-demo' && <CoCaTokDemo />}
            {currentScreen === 'explosion-demo' && <ExplosionDemo />}
            {currentScreen === 'style-test' && <StyleTestScreen />}
            {currentScreen === 'current-test' && <MyCurrentTestScreen />}
            {currentScreen === 'byo-component' && <BYOComponentTestScreen />}
          </main>

          
        </div>
      </PartyProvider>
    </StreamingProvider>
  );
}

export default App;