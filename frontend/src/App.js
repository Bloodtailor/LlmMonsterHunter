// Main React application component - UPDATED WITH HOME BASE SCREEN
// Now includes screen switching between Sanctuary, Home Base, Developer, and Dungeon
// Clean navigation with Home Base as the new game preparation hub

import React, { useState, useEffect } from 'react';
import ApiServicesTestScreen from './screens/ApiServicesTestScreen';
import StyleTestScreen from './screens/StyleTestScreen';
import MyCurrentTestScreen from './screens/MyCurrentTestScreen';
import { PartyProvider } from './app/contexts/PartyContext';
import BYOComponentTestScreen from './screens/BYOComponentTestScreen';
import CoCaTokDemo from './screens/CoCaTokDemo';
import ExplosionDemo from './screens/ExplosionDemo';

function App() {
  // Application state
  const [appStatus, setAppStatus] = useState({
    backendConnected: false,
    databaseConnected: false,
    gameData: null,
    loading: true,
    error: null
  });

  // Navigation state - Home Base is the main game screen
  const [currentScreen, setCurrentScreen] = useState('homebase'); 
  

  // Main application - backend is connected
  return (
    <PartyProvider>
      <div className="App">
        
        {/* App Header with Title Left, Navigation Centered */}
        <header className="app-header">
          <h1>🎮 Monster Hunter Game</h1>
          <nav className="screen-navigation">
            
            <button 
              className={`nav-button ${currentScreen === 'api-services' ? 'active' : ''}`}
              onClick={() => setCurrentScreen('api-services')}
            >
              🧪 API Tests
            </button>

            <button 
              className={`nav-button ${currentScreen === 'cocatok-demo' ? 'active' : ''}`}
              onClick={() => setCurrentScreen('cocatok-demo')}
            >
              ❄️ CoCaTok Demo
            </button>

            <button 
              className={`nav-button ${currentScreen === 'explosion-demo' ? 'active' : ''}`}
              onClick={() => setCurrentScreen('explosion-demo')}
            >
              ❄️ Explosion Demo
            </button>

            <button 
              className={`nav-button ${currentScreen === 'style-test' ? 'active' : ''}`}
              onClick={() => setCurrentScreen('style-test')}
            >
              🧪 Style Test
            </button>

            <button 
              className={`nav-button ${currentScreen === 'current-test' ? 'active' : ''}`}
              onClick={() => setCurrentScreen('current-test')}
            >
              🧪 Current Test
            </button>

            <button 
              className={`nav-button ${currentScreen === 'byoc-test' ? 'active' : ''}`}
              onClick={() => setCurrentScreen('byoc-test')}
            >
              🧪 BYOC Test
            </button>

          </nav>
        </header>

        {/* Main Content - Switch between screens */}
        <main className="app-main">
          

          {currentScreen === 'api-services' && (
            <ApiServicesTestScreen />
          )}

          
          {currentScreen === 'cocatok-demo' && (
            <CoCaTokDemo />
          )}

          {currentScreen === 'explosion-demo' && (
            <ExplosionDemo />
          )}

          {currentScreen === 'style-test' && (
            <StyleTestScreen />
          )}

          {currentScreen === 'current-test' && (
            <MyCurrentTestScreen />
          )}

          {currentScreen === 'byoc-test' && (
            <BYOComponentTestScreen />
          )}

        </main>

        {/* App Footer */}
        <footer className="app-footer">
          <p>Monster Hunter Game - MVP Development Phase</p>
        </footer>
      </div>
    </PartyProvider>
  );
}

export default App;