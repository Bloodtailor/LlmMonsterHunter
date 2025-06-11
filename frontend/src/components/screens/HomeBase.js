// Home Base Screen Component
// The main hub where players manage monsters, inventory, and start adventures
// Now includes LLM debugging panel for monitoring AI generation

import React, { useState } from 'react';
import { testApiConnectivity } from '../../services/api';
import LLMLogViewer from '../debug/LLMLogViewer';

function HomeBase({ gameData, onRefresh }) {
  const [testing, setTesting] = useState(false);
  const [apiTestResults, setApiTestResults] = useState(null);

  // Test API connectivity
  const handleApiTest = async () => {
    setTesting(true);
    try {
      const results = await testApiConnectivity();
      setApiTestResults(results);
    } catch (error) {
      setApiTestResults({
        success: false,
        error: error.message,
        timestamp: new Date().toISOString()
      });
    }
    setTesting(false);
  };

  return (
    <div className="home-base">
      {/* Welcome Section */}
      <section className="welcome-section">
        <h2>🏠 Welcome to Your Home Base</h2>
        <p>This is where you'll manage your monsters, prepare for adventures, and plan your strategies.</p>
      </section>

      {/* Game Status Panel */}
      <section className="game-status-panel">
        <h3>🎮 Game Status</h3>
        <div className="status-grid">
          <div className="status-card">
            <h4>Game Information</h4>
            <p><strong>Name:</strong> {gameData?.game_name || 'Loading...'}</p>
            <p><strong>Version:</strong> {gameData?.version || 'Unknown'}</p>
            <p><strong>Phase:</strong> {gameData?.status || 'Unknown'}</p>
          </div>
          
          <div className="status-card">
            <h4>Feature Development Status</h4>
            {gameData?.features ? (
              <div className="features-list">
                {Object.entries(gameData.features).map(([feature, enabled]) => (
                  <div key={feature} className="feature-item">
                    <span className={`feature-status ${enabled ? 'enabled' : 'disabled'}`}>
                      {enabled ? '✅' : '⏳'}
                    </span>
                    <span className="feature-name">
                      {feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p>Loading features...</p>
            )}
          </div>
        </div>
      </section>

      {/* Future Features Preview */}
      <section className="features-preview">
        <h3>🚀 Coming Soon</h3>
        <div className="preview-grid">
          <div className="preview-card disabled">
            <h4>🐉 Monster Roster</h4>
            <p>View and manage your captured monsters</p>
            <div className="placeholder-roster">
              <div className="placeholder-monster">?</div>
              <div className="placeholder-monster">?</div>
              <div className="placeholder-monster">?</div>
              <div className="placeholder-monster">?</div>
            </div>
          </div>
          
          <div className="preview-card disabled">
            <h4>🎒 Inventory</h4>
            <p>Manage items and equipment</p>
            <div className="placeholder-inventory">
              <div className="placeholder-item">📦</div>
              <div className="placeholder-item">⚔️</div>
              <div className="placeholder-item">🛡️</div>
              <div className="placeholder-item">💊</div>
            </div>
          </div>
          
          <div className="preview-card disabled">
            <h4>🗺️ Dungeon Explorer</h4>
            <p>Enter dungeons to find new monsters</p>
            <button className="preview-button" disabled>
              Enter Dungeon
            </button>
          </div>
          
          <div className="preview-card disabled">
            <h4>💬 Monster Chat</h4>
            <p>Talk with your captured monsters</p>
            <div className="placeholder-chat">
              <div className="chat-bubble">Hello trainer!</div>
            </div>
          </div>
        </div>
      </section>

      {/* Developer Tools Section */}
      <section className="developer-tools">
        <h3>🔧 Developer Tools</h3>
        <div className="tools-grid">
          <div className="tool-card">
            <h4>API Connectivity Test</h4>
            <p>Test connection to Flask backend and verify all endpoints are working</p>
            <button 
              onClick={handleApiTest} 
              disabled={testing}
              className="test-button"
            >
              {testing ? '🔄 Testing...' : '🧪 Test API'}
            </button>
            
            {apiTestResults && (
              <div className={`test-results ${apiTestResults.success ? 'success' : 'error'}`}>
                <h5>{apiTestResults.success ? '✅ API Test Passed' : '❌ API Test Failed'}</h5>
                {apiTestResults.success ? (
                  <div>
                    <p>✅ Health check: {apiTestResults.health?.status}</p>
                    <p>✅ Database: {apiTestResults.health?.database}</p>
                    <p>✅ Game status: {apiTestResults.status?.status}</p>
                  </div>
                ) : (
                  <p>Error: {apiTestResults.error}</p>
                )}
                <small>Tested at: {new Date(apiTestResults.timestamp).toLocaleTimeString()}</small>
              </div>
            )}
          </div>
          
          <div className="tool-card">
            <h4>Refresh Game Data</h4>
            <p>Reload game status and backend connection information</p>
            <button onClick={onRefresh} className="refresh-button">
              🔄 Refresh Data
            </button>
          </div>
        </div>
      </section>

      {/* LLM System Debug Panel */}
      <section className="llm-debug-panel">
        <LLMLogViewer />
      </section>

      {/* Instructions Section */}
      <section className="instructions">
        <h3>📋 Next Development Steps</h3>
        <ol>
          <li>✅ <strong>Backend API</strong> - Working with health and status endpoints</li>
          <li>✅ <strong>React Frontend</strong> - Connecting to backend successfully</li>
          <li>✅ <strong>LLM Infrastructure</strong> - Complete AI system with logging and monitoring</li>
          <li>⏳ <strong>Monster Generation Debug</strong> - Use LLM panel above to see why generation failed</li>
          <li>⏳ <strong>Monster Generation API</strong> - Create endpoints for AI monster creation</li>
          <li>⏳ <strong>Monster Display UI</strong> - Show generated monsters in React</li>
          <li>⏳ <strong>Battle System</strong> - Implement turn-based combat</li>
        </ol>
        <p><strong>🔧 Debug Tool:</strong> The "LLM System Status" panel above shows all AI generation attempts. If monster generation failed, check the logs to see the exact error and LLM response.</p>
      </section>
    </div>
  );
}

export default HomeBase;