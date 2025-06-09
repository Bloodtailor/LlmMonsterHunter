// Main React application component
// Sets up routing and global state management
// Provides app-level error handling and API integration

import React, { useState, useEffect } from 'react';
import HomeBase from './components/screens/HomeBase';
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
      {/* App Header */}
      <header className="app-header">
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
      </header>

      {/* Main Content */}
      <main className="app-main">
        <HomeBase 
          gameData={appStatus.gameData}
          onRefresh={checkBackendStatus}
        />
      </main>

      {/* App Footer */}
      <footer className="app-footer">
        <p>Monster Hunter Game - MVP Development Phase</p>
        <p>Status: {appStatus.gameData?.status || 'Unknown'}</p>
      </footer>
    </div>
  );
}

export default App;