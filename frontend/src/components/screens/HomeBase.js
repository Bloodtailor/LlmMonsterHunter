// Home Base Screen Component

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

  // 🔧 FIXED: Test Queue System using proper logging flow
  const handleQueueTest = async () => {
    setQueueTesting(true);
    setQueueTestResults(null);
    
    try {
      // Use the NEW simple test endpoint that ensures proper logging
      const response = await fetch('http://localhost:5000/api/streaming/test/simple', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({})  // Simple test, no parameters needed
      });
      
      const data = await response.json();
      
      if (data.success) {
        setQueueTestResults({
          success: true,
          request_id: data.request_id,
          log_id: data.log_id,
          message: 'Test started! Watch the streaming display and LLM log viewer.',
          instructions: data.instructions,
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
            <h4>System Status</h4>
            {gameData?.system_status ? (
              <div>
                <p><strong>Model Loaded:</strong> {gameData.system_status.llm?.model_loaded ? '✅ Yes' : '❌ No'}</p>
                <p><strong>GPU Layers:</strong> {gameData.system_status.llm?.gpu_layers || 'Unknown'}</p>
                <p><strong>Queue Worker:</strong> {gameData.system_status.queue?.worker_running ? '✅ Running' : '❌ Stopped'}</p>
                <p><strong>Database:</strong> {gameData.system_status.database?.connected ? '✅ Connected' : '❌ Disconnected'}</p>
              </div>
            ) : (
              <p>Loading system status...</p>
            )}
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
            <h4>🔧 FIXED: Queue + Logging + Streaming Test</h4>
            <p>Test the complete flow: queue → LLM generation → logging → streaming display</p>
            <button 
              onClick={handleQueueTest} 
              disabled={queueTesting}
              className="test-button"
            >
              {queueTesting ? '🔄 Starting Test...' : '🎲 Test Complete Flow'}
            </button>
            
            {queueTestResults && (
              <div className={`test-results ${queueTestResults.success ? 'success' : 'error'}`}>
                <h5>{queueTestResults.success ? '✅ Complete Flow Test Started' : '❌ Test Failed'}</h5>
                {queueTestResults.success ? (
                  <div>
                    <p>✅ Request ID: {queueTestResults.request_id}</p>
                    <p>✅ Log ID: {queueTestResults.log_id}</p>
                    <p>📺 Watch the streaming display (top-right corner)!</p>
                    <p>📋 Check the LLM Log Viewer below for detailed progress</p>
                    <p>🔄 The request is now being processed through the complete flow</p>
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

      {/* LLM System Debug Panel */}
      <section className="llm-debug-panel">
        <LLMLogViewer />
      </section>

      {/* Instructions Section */}
      <section className="instructions">
        <h3>📋 System Testing Instructions</h3>
        <ol>
          <li>✅ <strong>Backend API</strong> - Test with "Test API" button</li>
          <li>✅ <strong>Complete Flow</strong> - Test with "Test Complete Flow" button</li>
          <li>🔍 <strong>Watch Streaming</strong> - Real-time progress in top-right corner</li>
          <li>📋 <strong>Check Logs</strong> - Detailed info in LLM Log Viewer below</li>
          <li>🎯 <strong>Verify GPU</strong> - Look for 30+ tokens/second generation speed</li>
        </ol>
        <p><strong>🔧 Testing Flow:</strong> The "Test Complete Flow" button now properly creates log entries, queues requests, processes through the LLM, and streams results in real-time.</p>
        <p><strong>📺 Streaming Display:</strong> Watch for live generation progress, token counts, and completion status.</p>
        <p><strong>⚡ GPU Check:</strong> Generation speed over 15 tok/s indicates GPU usage.</p>
      </section>
    </div>
  );
}

export default HomeBase;