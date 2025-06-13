// Developer Screen Component
// Contains all debugging tools, system monitoring, and test runner

import React, { useState } from 'react';
import { testApiConnectivity } from '../../services/api';
import LLMLogViewer from '../debug/LLMLogViewer';
import TestRunner from '../debug/TestRunner';

function DeveloperScreen({ gameData, onRefresh }) {
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

  // Test Complete Flow using proper logging flow
  const handleQueueTest = async () => {
    setQueueTesting(true);
    setQueueTestResults(null);
    
    try {
      // Use the simple test endpoint that ensures proper logging
      const response = await fetch('http://localhost:5000/api/streaming/test/simple', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({})
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
    <div className="developer-screen">
      {/* Developer Header */}
      <section className="developer-header">
        <h1>🔧 Developer & Debug Tools</h1>
        <p>System monitoring, testing, and debugging interface for the Monster Hunter Game backend</p>
      </section>

      {/* System Status Panel */}
      <section className="system-status-panel">
        <h2>🎮 System Status</h2>
        <div className="status-grid">
          <div className="status-card">
            <h4>Game Information</h4>
            <p><strong>Name:</strong> {gameData?.game_name || 'Loading...'}</p>
            <p><strong>Version:</strong> {gameData?.version || 'Unknown'}</p>
            <p><strong>Phase:</strong> {gameData?.status || 'Unknown'}</p>
          </div>
          
          <div className="status-card">
            <h4>Backend Status</h4>
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

      {/* Quick Testing Tools */}
      <section className="quick-testing">
        <h2>🧪 Quick System Tests</h2>
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
            <h4>Complete Flow Test</h4>
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
                  </div>
                ) : (
                  <p>Error: {queueTestResults.error}</p>
                )}
                <small>Started at: {new Date(queueTestResults.timestamp).toLocaleTimeString()}</small>
              </div>
            )}
          </div>
          
          <div className="tool-card">
            <h4>Refresh System Data</h4>
            <p>Reload game status and backend connection information</p>
            <button onClick={onRefresh} className="refresh-button">
              🔄 Refresh Data
            </button>
          </div>
        </div>
      </section>

      {/* Backend Test Runner */}
      <section className="backend-testing">
        <h2>🔬 Backend Test Runner</h2>
        <TestRunner />
      </section>

      {/* LLM System Debug Panel */}
      <section className="llm-debug-panel">
        <h2>🤖 LLM System Monitor</h2>
        <LLMLogViewer />
      </section>

      {/* Development Instructions */}
      <section className="dev-instructions">
        <h2>📋 Development Testing Guide</h2>
        <div className="instructions-grid">
          <div className="instruction-card">
            <h4>🎯 System Testing Flow</h4>
            <ol>
              <li>✅ <strong>API Test</strong> - Verify backend connectivity</li>
              <li>✅ <strong>Complete Flow Test</strong> - Test LLM generation pipeline</li>
              <li>🔍 <strong>Watch Streaming</strong> - Real-time progress in top-right corner</li>
              <li>📋 <strong>Check Logs</strong> - Detailed info in LLM Log Viewer</li>
              <li>🎯 <strong>Verify GPU</strong> - Look for 15+ tokens/second generation speed</li>
            </ol>
          </div>
          
          <div className="instruction-card">
            <h4>🧪 Backend Testing</h4>
            <ol>
              <li>📝 <strong>Create Test Files</strong> - Add .py files to backend/tests/</li>
              <li>🔄 <strong>Refresh Tests</strong> - Click refresh to see new tests</li>
              <li>▶️ <strong>Run Tests</strong> - Click run and see output</li>
              <li>📊 <strong>Check Results</strong> - View success/failure and stack traces</li>
            </ol>
          </div>
          
          <div className="instruction-card">
            <h4>⚡ Performance Indicators</h4>
            <ul>
              <li><strong>GPU Usage:</strong> 15+ tokens/second indicates GPU acceleration</li>
              <li><strong>Queue Health:</strong> Worker should be running</li>
              <li><strong>Database:</strong> All connections should be green</li>
              <li><strong>Streaming:</strong> Real-time updates should appear instantly</li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  );
}

export default DeveloperScreen;