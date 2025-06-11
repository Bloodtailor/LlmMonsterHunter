// Home Base Screen Component
// The main hub where players manage monsters, inventory, and start adventures
// Now includes LLM debugging panel for monitoring AI generation

import React, { useState } from 'react';
import { testApiConnectivity } from '../../services/api';
import LLMLogViewer from '../debug/LLMLogViewer';

function HomeBase({ gameData, onRefresh }) {
  const [testing, setTesting] = useState(false);
  const [apiTestResults, setApiTestResults] = useState(null);
  const [queueTesting, setQueueTesting] = useState(false);
  const [queueTestResults, setQueueTestResults] = useState(null);

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

  // Test Queue System
  const handleQueueTest = async () => {
    setQueueTesting(true);
    setQueueTestResults(null);
    
    try {
      // Add a test request to the queue
      const response = await fetch('http://localhost:5000/api/streaming/queue/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: 'Generate a test response about a friendly dragon named Spark.',
          max_tokens: 100,
          temperature: 0.8,
          prompt_type: 'test_generation',
          priority: 2
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setQueueTestResults({
          success: true,
          request_id: data.request_id,
          message: 'Test request added to queue! Watch the streaming display above.',
          timestamp: new Date().toISOString()
        });
      } else {
        setQueueTestResults({
          success: false,
          error: data.error,
          timestamp: new Date().toISOString()
        });
      }
      
    } catch (error) {
      setQueueTestResults({
        success: false,
        error: error.message,
        timestamp: new Date().toISOString()
      });
    }
    
    setQueueTesting(false);
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
            <h4>LLM Queue System Test</h4>
            <p>Test the new prompt queue system with real-time streaming display</p>
            <button 
              onClick={handleQueueTest} 
              disabled={queueTesting}
              className="test-button"
            >
              {queueTesting ? '🔄 Adding to Queue...' : '🎲 Test Queue Generation'}
            </button>
            
            {queueTestResults && (
              <div className={`test-results ${queueTestResults.success ? 'success' : 'error'}`}>
                <h5>{queueTestResults.success ? '✅ Queue Test Started' : '❌ Queue Test Failed'}</h5>
                {queueTestResults.success ? (
                  <div>
                    <p>✅ Request ID: {queueTestResults.request_id}</p>
                    <p>📺 Watch the streaming display in the top-right corner!</p>
                    <p>🔄 The request is now being processed in the queue</p>
                  </div>
                ) : (
                  <p>Error: {queueTestResults.error}</p>
                )}
                <small>Started at: {new Date(queueTestResults.timestamp).toLocaleTimeString()}</small>
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
          <li>✅ <strong>Streaming Display</strong> - Real-time LLM generation progress overlay</li>
          <li>✅ <strong>Queue System</strong> - Proper prompt queuing with priority management</li>
          <li>⏳ <strong>Monster Generation API</strong> - Create endpoints for AI monster creation</li>
          <li>⏳ <strong>Monster Display UI</strong> - Show generated monsters in React</li>
          <li>⏳ <strong>Battle System</strong> - Implement turn-based combat</li>
        </ol>
        <p><strong>🔧 Debug Tools:</strong> Use the "Test Queue Generation" button above to see the streaming system in action. The streaming display in the top-right corner shows all AI activity in real-time!</p>
        <p><strong>📺 Streaming Display:</strong> Watch the top-right corner for live LLM generation progress. It will auto-expand during generation and show queue status, timing, and generated text.</p>
      </section>
    </div>
  );
}

export default HomeBase;