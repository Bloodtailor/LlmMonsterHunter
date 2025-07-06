// Main React application component - UPDATED WITH HOME BASE SCREEN
// Now includes screen switching between Sanctuary, Home Base, Developer, and Dungeon
// Clean navigation with Home Base as the new game preparation hub

import React, { useState, useEffect } from 'react';
import MonsterSanctuary from './components/screens/MonsterSanctuary';
import HomeBaseScreen from './components/screens/HomeBaseScreen';
import DeveloperScreen from './components/screens/DeveloperScreen';
import StreamingDisplay from './components/streaming/StreamingDisplay';
import { healthCheck, getGameStatus } from './services/api';

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
  const [currentScreen, setCurrentScreen] = useState('homebase'); // 'homebase', 'sanctuary', 'developer', 'dungeon'

  // Check backend connection on app startup
  useEffect(() => {
    checkBackendStatus();
  }, []);

  const checkBackendStatus = async () => {
    setAppStatus(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      // Test backend connection
      const healthData = await healthCheck();
      const gameData = await getGameStatus();
      
      setAppStatus({
        backendConnected: true,
        databaseConnected: healthData.database === 'connected',
        gameData: gameData,
        loading: false,
        error: null
      });
      
    } catch (error) {
      console.error('Backend connection failed:', error);
      setAppStatus({
        backendConnected: false,
        databaseConnected: false,
        gameData: null,
        loading: false,
        error: error.message
      });
    }
  };

  // Handle entering dungeon from Home Base
  const handleEnterDungeon = () => {
    console.log('🏰 Entering dungeon...');
    setCurrentScreen('dungeon');
  };

  // Handle returning to home base from dungeon
  const handleReturnToHomeBase = () => {
    console.log('🏠 Returning to home base...');
    setCurrentScreen('homebase');
  };

  // Loading screen
  if (appStatus.loading) {
    return (
      <div className="App">
        <div className="loading-screen">
          <h1>🎮 Monster Hunter Game</h1>
          <div className="loading-spinner"></div>
          <p>Connecting to backend...</p>
        </div>
      </div>
    );
  }

  // Error screen if backend is not accessible
  if (!appStatus.backendConnected) {
    return (
      <div className="App">
        <div className="error-screen">
          <h1>🎮 Monster Hunter Game</h1>
          <div className="error-message">
            <h2>❌ Cannot Connect to Backend</h2>
            <p>{appStatus.error}</p>
            <div className="error-help">
              <h3>💡 To fix this:</h3>
              <ol>
                <li>Make sure the backend server is running</li>
                <li>Run: <code>start_backend.bat</code></li>
                <li>Check that the server shows "✅ Database connection verified"</li>
                <li>Refresh this page</li>
              </ol>
            </div>
            <button onClick={checkBackendStatus} className="retry-button">
              🔄 Retry Connection
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Main application - backend is connected
  return (
    <div className="App">
      {/* Always-visible LLM Streaming Display */}
      <StreamingDisplay />
      
      {/* App Header with Title Left, Navigation Centered */}
      <header className="app-header">
        <h1>🎮 Monster Hunter Game</h1>
        <nav className="screen-navigation">
          <button 
            className={`nav-button ${currentScreen === 'homebase' ? 'active' : ''}`}
            onClick={() => setCurrentScreen('homebase')}
          >
            🏠 Home Base
          </button>
          <button 
            className={`nav-button ${currentScreen === 'sanctuary' ? 'active' : ''}`}
            onClick={() => setCurrentScreen('sanctuary')}
          >
            🏛️ Sanctuary
          </button>
          <button 
            className={`nav-button ${currentScreen === 'developer' ? 'active' : ''}`}
            onClick={() => setCurrentScreen('developer')}
          >
            🔧 Developer
          </button>
          {/* Dungeon button only shows when in dungeon */}
          {currentScreen === 'dungeon' && (
            <button className="nav-button active">
              🏰 In Dungeon
            </button>
          )}
        </nav>
      </header>

      {/* Main Content - Switch between screens */}
      <main className="app-main">
        {currentScreen === 'homebase' && (
          <HomeBaseScreen 
            onEnterDungeon={handleEnterDungeon}
          />
        )}
        
        {currentScreen === 'sanctuary' && (
          <MonsterSanctuary 
            gameData={appStatus.gameData}
            onRefresh={checkBackendStatus}
          />
        )}
        
        {currentScreen === 'developer' && (
          <DeveloperScreen 
            gameData={appStatus.gameData}
            onRefresh={checkBackendStatus}
          />
        )}

        {currentScreen === 'dungeon' && (
          <div className="dungeon-placeholder">
            <h2>🏰 Dungeon Screen</h2>
            <p>Coming in Batch 4!</p>
            <button 
              onClick={handleReturnToHomeBase}
              className="btn btn-primary"
            >
              🏠 Return to Home Base
            </button>
          </div>
        )}
      </main>

      {/* App Footer */}
      <footer className="app-footer">
        <p>Monster Hunter Game - MVP Development Phase</p>
        <div className="footer-info">
          <span>Status: {appStatus.gameData?.status || 'Unknown'}</span>
          <span>•</span>
          <span>Current Screen: {
            currentScreen === 'homebase' ? 'Home Base' :
            currentScreen === 'sanctuary' ? 'Monster Sanctuary' :
            currentScreen === 'developer' ? 'Developer Tools' :
            currentScreen === 'dungeon' ? 'Dungeon Adventure' : 'Unknown'
          }</span>
        </div>
      </footer>
    </div>
  );
}

export default App;