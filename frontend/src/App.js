// Main React application component - UPDATED WITH HOME BASE SCREEN
// Now includes screen switching between Sanctuary, Home Base, Developer, and Dungeon
// Clean navigation with Home Base as the new game preparation hub

import React, { useState, useEffect } from 'react';
import ApiServicesTestScreen from './screens/ApiServicesTestScreen';
import HooksTestScreen from './screens/HooksTestScreen';
import MyCurrentTestScreen from './screens/MyCurrentTestScreen';
import { PartyProvider } from './app/contexts/PartyContext';

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
              className={`nav-button ${currentScreen === 'hook-tests' ? 'active' : ''}`}
              onClick={() => setCurrentScreen('hook-tests')}
            >
              🧪 Hook Tests
            </button>

            <button 
              className={`nav-button ${currentScreen === 'current-test' ? 'active' : ''}`}
              onClick={() => setCurrentScreen('current-test')}
            >
              🧪 Current Test
            </button>

          </nav>
        </header>

        {/* Main Content - Switch between screens */}
        <main className="app-main">
          

          {currentScreen === 'api-services' && (
            <ApiServicesTestScreen />
          )}

          {currentScreen === 'hook-tests' && (
            <HooksTestScreen />
          )}

          {currentScreen === 'current-test' && (
            <MyCurrentTestScreen />
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