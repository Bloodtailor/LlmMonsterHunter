// Main React application component - UPDATED WITH MONSTER SANCTUARY
// Separates game interface from developer tools
// Now uses the new MonsterSanctuary screen with flippable cards

import React, { useState, useEffect } from 'react';
import MonsterSanctuary from './components/screens/MonsterSanctuary';
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

  // Navigation state
  const [currentScreen, setCurrentScreen] = useState('game'); // 'game' or 'developer'

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
      
      {/* App Header with Navigation */}
      <header className="app-header">
        <div className="header-left">
          <h1>🎮 Monster Hunter Game</h1>
          <div className="status-indicators">
            <div className={`status-indicator ${appStatus.backendConnected ? 'connected' : 'disconnected'}`}>
              Backend: {appStatus.backendConnected ? '✅ Connected' : '❌ Disconnected'}
            </div>
            <div className={`status-indicator ${appStatus.databaseConnected ? 'connected' : 'disconnected'}`}>
              Database: {appStatus.databaseConnected ? '✅ Connected' : '❌ Disconnected'}
            </div>
            <div className="game-version">
              v{appStatus.gameData?.version || '0.1.0'}
            </div>
          </div>
        </div>
        
        <div className="header-right">
          <nav className="screen-navigation">
            <button 
              className={`nav-button ${currentScreen === 'game' ? 'active' : ''}`}
              onClick={() => setCurrentScreen('game')}
            >
              🏛️ Sanctuary
            </button>
            <button 
              className={`nav-button ${currentScreen === 'developer' ? 'active' : ''}`}
              onClick={() => setCurrentScreen('developer')}
            >
              🔧 Developer
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content - Switch between screens */}
      <main className="app-main">
        {currentScreen === 'game' ? (
          <MonsterSanctuary 
            gameData={appStatus.gameData}
            onRefresh={checkBackendStatus}
          />
        ) : (
          <DeveloperScreen 
            gameData={appStatus.gameData}
            onRefresh={checkBackendStatus}
          />
        )}
      </main>

      {/* App Footer */}
      <footer className="app-footer">
        <p>Monster Hunter Game - MVP Development Phase</p>
        <div className="footer-info">
          <span>Status: {appStatus.gameData?.status || 'Unknown'}</span>
          <span>•</span>
          <span>Current Screen: {currentScreen === 'game' ? 'Monster Sanctuary' : 'Developer Tools'}</span>
        </div>
      </footer>
    </div>
  );
}

export default App;