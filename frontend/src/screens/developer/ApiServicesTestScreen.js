// API Services Test Screen - Comprehensive testing of all refactored API services
// Tests every service function to verify the API layer works correctly
// Displays raw responses and handles errors gracefully

import React, { useState } from 'react';

// Import all API services from refactored directory
import * as monstersApi from '../../api/services/monsters.js';
import * as gameStateApi from '../../api/services/gameState.js';
import * as dungeonApi from '../../api/services/dungeon.js';
import * as systemApi from '../../api/services/system.js';
import * as generationApi from '../../api/services/generation.js';
import * as testingApi from '../../api/services/testing.js';

function ApiServicesTestScreen() {
  const [testResults, setTestResults] = useState({});
  const [runningTests, setRunningTests] = useState(new Set());
  const [testMonsters, setTestMonsters] = useState([]); // Store monsters for testing

  // Helper to run a test and store results
  const runTest = async (testName, testFunction, ...args) => {
    setRunningTests(prev => new Set([...prev, testName]));
    
    try {
      const startTime = Date.now();
      const result = await testFunction(...args);
      const duration = Date.now() - startTime;
      
      setTestResults(prev => ({
        ...prev,
        [testName]: {
          success: true,
          result,
          duration,
          timestamp: new Date().toISOString()
        }
      }));
      
      // Store monsters for other tests
      if (testName === 'loadMonsters' && result.success && result.monsters) {
        setTestMonsters(result.monsters.slice(0, 3)); // Store first 3 for testing
      }
      
    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        [testName]: {
          success: false,
          error: error.message,
          timestamp: new Date().toISOString()
        }
      }));
    } finally {
      setRunningTests(prev => {
        const newSet = new Set(prev);
        newSet.delete(testName);
        return newSet;
      });
    }
  };

  // Clear all test results
  const clearResults = () => {
    setTestResults({});
    setTestMonsters([]);
  };

  // Run all tests in sequence
  const runAllTests = async () => {
    const tests = [
      // System tests first
      ['healthCheck', systemApi.healthCheck],
      ['getGameStatus', systemApi.getGameStatus],
      ['testApiConnectivity', systemApi.testApiConnectivity],
      
      // Monsters tests
      ['loadMonsters', monstersApi.loadMonsters, { limit: 5 }],
      ['loadMonsterStats', monstersApi.loadMonsterStats],
      ['getMonsterTemplates', monstersApi.getMonsterTemplates],
      ['testMonstersApi', monstersApi.testMonstersApi],
      
      // Game state tests
      ['getGameState', gameStateApi.getGameState],
      ['getFollowingMonsters', gameStateApi.getFollowingMonsters],
      ['getActiveParty', gameStateApi.getActiveParty],
      ['isPartyReady', gameStateApi.isPartyReady],
      
      // Dungeon tests
      ['getDungeonStatus', dungeonApi.getDungeonStatus],
      ['getDungeonState', dungeonApi.getDungeonState],
      
      // Generation tests
      ['getGenerationStatus', generationApi.getGenerationStatus],
      ['getGenerationStats', generationApi.getGenerationStats],
      ['getGenerationLogs', generationApi.getGenerationLogs, { limit: 5 }],
      ['getStreamingConnections', generationApi.getStreamingConnections],
      
      // Testing tests
      ['getAvailableTests', testingApi.getAvailableTests],
    ];
    
    for (const [testName, testFn, ...args] of tests) {
      await runTest(testName, testFn, ...args);
      // Small delay between tests
      await new Promise(resolve => setTimeout(resolve, 200));
    }
  };

  // Test individual monster operations (needs monster ID)
  const testIndividualMonster = async () => {
    if (testMonsters.length === 0) {
      alert('Run "Load Monsters" test first to get monster IDs');
      return;
    }
    
    const monsterId = testMonsters[0].id;
    await runTest('getMonster', monstersApi.getMonster, monsterId);
    await runTest('getMonsterAbilities', monstersApi.getMonsterAbilities, monsterId);
    await runTest('getMonsterCardArt', monstersApi.getMonsterCardArt, monsterId);
  };

  // Test party operations (needs monster IDs)
  const testPartyOperations = async () => {
    if (testMonsters.length === 0) {
      alert('Run "Load Monsters" test first to get monster IDs');
      return;
    }
    
    const monsterId = testMonsters[0].id;
    await runTest('addMonsterToFollowing', gameStateApi.addMonsterToFollowing, monsterId);
    await runTest('setActiveParty', gameStateApi.setActiveParty, [monsterId]);
    await runTest('removeMonsterFromFollowing', gameStateApi.removeMonsterFromFollowing, monsterId);
  };

  // Format test result for display
  const formatResult = (result) => {
    if (typeof result === 'string') return result;
    return JSON.stringify(result, null, 2);
  };

  // Get test status styling
  const getTestStatus = (testName) => {
    const result = testResults[testName];
    const isRunning = runningTests.has(testName);
    
    if (isRunning) return 'running';
    if (!result) return 'not-run';
    return result.success ? 'success' : 'error';
  };

  return (
    <div className="api-services-test-screen">
      <div className="test-header">
        <h1>🔧 API Services Test Suite</h1>
        <p>Comprehensive testing of all refactored API services</p>
        
        <div className="test-controls">
          <button onClick={runAllTests} className="btn btn-primary btn-lg">
            🚀 Run All Tests
          </button>
          <button onClick={clearResults} className="btn btn-secondary">
            🗑️ Clear Results
          </button>
          <div className="test-summary">
            <span>Tests Run: {Object.keys(testResults).length}</span>
            <span>Running: {runningTests.size}</span>
            <span>Success: {Object.values(testResults).filter(r => r.success).length}</span>
            <span>Failed: {Object.values(testResults).filter(r => !r.success).length}</span>
          </div>
        </div>
      </div>

      {/* System API Tests */}
      <div className="test-section">
        <h2>🏥 System API Tests</h2>
        <div className="test-grid">
          <TestButton
            testName="healthCheck"
            label="Health Check"
            onClick={() => runTest('healthCheck', systemApi.healthCheck)}
            status={getTestStatus('healthCheck')}
          />
          <TestButton
            testName="getGameStatus"
            label="Game Status"
            onClick={() => runTest('getGameStatus', systemApi.getGameStatus)}
            status={getTestStatus('getGameStatus')}
          />
          <TestButton
            testName="testApiConnectivity"
            label="API Connectivity"
            onClick={() => runTest('testApiConnectivity', systemApi.testApiConnectivity)}
            status={getTestStatus('testApiConnectivity')}
          />
        </div>
      </div>

      {/* Monster API Tests */}
      <div className="test-section">
        <h2>🐲 Monster API Tests</h2>
        <div className="test-grid">
          <TestButton
            testName="loadMonsters"
            label="Load Monsters"
            onClick={() => runTest('loadMonsters', monstersApi.loadMonsters, { limit: 5 })}
            status={getTestStatus('loadMonsters')}
          />
          <TestButton
            testName="loadMonsterStats"
            label="Monster Stats"
            onClick={() => runTest('loadMonsterStats', monstersApi.loadMonsterStats)}
            status={getTestStatus('loadMonsterStats')}
          />
          <TestButton
            testName="getMonsterTemplates"
            label="Monster Templates"
            onClick={() => runTest('getMonsterTemplates', monstersApi.getMonsterTemplates)}
            status={getTestStatus('getMonsterTemplates')}
          />
          <TestButton
            testName="individualMonster"
            label="Test Individual Monster"
            onClick={testIndividualMonster}
            status={getTestStatus('getMonster')}
            disabled={testMonsters.length === 0}
          />
        </div>
      </div>

      {/* Game State API Tests */}
      <div className="test-section">
        <h2>🎮 Game State API Tests</h2>
        <div className="test-grid">
          <TestButton
            testName="getGameState"
            label="Game State"
            onClick={() => runTest('getGameState', gameStateApi.getGameState)}
            status={getTestStatus('getGameState')}
          />
          <TestButton
            testName="getFollowingMonsters"
            label="Following Monsters"
            onClick={() => runTest('getFollowingMonsters', gameStateApi.getFollowingMonsters)}
            status={getTestStatus('getFollowingMonsters')}
          />
          <TestButton
            testName="getActiveParty"
            label="Active Party"
            onClick={() => runTest('getActiveParty', gameStateApi.getActiveParty)}
            status={getTestStatus('getActiveParty')}
          />
          <TestButton
            testName="isPartyReady"
            label="Party Ready"
            onClick={() => runTest('isPartyReady', gameStateApi.isPartyReady)}
            status={getTestStatus('isPartyReady')}
          />
          <TestButton
            testName="partyOperations"
            label="Test Party Operations"
            onClick={testPartyOperations}
            status={getTestStatus('addMonsterToFollowing')}
            disabled={testMonsters.length === 0}
          />
        </div>
      </div>

      {/* Dungeon API Tests */}
      <div className="test-section">
        <h2>🏰 Dungeon API Tests</h2>
        <div className="test-grid">
          <TestButton
            testName="getDungeonStatus"
            label="Dungeon Status"
            onClick={() => runTest('getDungeonStatus', dungeonApi.getDungeonStatus)}
            status={getTestStatus('getDungeonStatus')}
          />
          <TestButton
            testName="getDungeonState"
            label="Dungeon State"
            onClick={() => runTest('getDungeonState', dungeonApi.getDungeonState)}
            status={getTestStatus('getDungeonState')}
          />
        </div>
      </div>

      {/* Generation API Tests */}
      <div className="test-section">
        <h2>⚡ Generation API Tests</h2>
        <div className="test-grid">
          <TestButton
            testName="getGenerationStatus"
            label="Generation Status"
            onClick={() => runTest('getGenerationStatus', generationApi.getGenerationStatus)}
            status={getTestStatus('getGenerationStatus')}
          />
          <TestButton
            testName="getGenerationStats"
            label="Generation Stats"
            onClick={() => runTest('getGenerationStats', generationApi.getGenerationStats)}
            status={getTestStatus('getGenerationStats')}
          />
          <TestButton
            testName="getGenerationLogs"
            label="Generation Logs"
            onClick={() => runTest('getGenerationLogs', generationApi.getGenerationLogs, { limit: 5 })}
            status={getTestStatus('getGenerationLogs')}
          />
          <TestButton
            testName="getStreamingConnections"
            label="Streaming Connections"
            onClick={() => runTest('getStreamingConnections', generationApi.getStreamingConnections)}
            status={getTestStatus('getStreamingConnections')}
          />
        </div>
      </div>

      {/* Testing API Tests */}
      <div className="test-section">
        <h2>🧪 Testing API Tests</h2>
        <div className="test-grid">
          <TestButton
            testName="getAvailableTests"
            label="Available Tests"
            onClick={() => runTest('getAvailableTests', testingApi.getAvailableTests)}
            status={getTestStatus('getAvailableTests')}
          />
        </div>
      </div>

      {/* Test Results Display */}
      <div className="test-results-section">
        <h2>📋 Test Results</h2>
        {Object.keys(testResults).length === 0 ? (
          <div className="no-results">
            <p>No tests run yet. Click "Run All Tests" or individual test buttons above.</p>
          </div>
        ) : (
          <div className="results-list">
            {Object.entries(testResults).map(([testName, result]) => (
              <div key={testName} className={`result-item ${result.success ? 'success' : 'error'}`}>
                <div className="result-header">
                  <h4>{result.success ? '✅' : '❌'} {testName}</h4>
                  <span className="result-time">
                    {result.duration ? `${result.duration}ms` : ''} 
                    {new Date(result.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <div className="result-content">
                  <pre>{result.success ? formatResult(result.result) : result.error}</pre>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// Reusable test button component
function TestButton({ testName, label, onClick, status, disabled = false }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled || status === 'running'}
      className={`test-button test-${status}`}
    >
      <span className="test-icon">
        {status === 'running' ? '🔄' : 
         status === 'success' ? '✅' : 
         status === 'error' ? '❌' : '⚪'}
      </span>
      <span className="test-label">{label}</span>
      {status === 'running' && <span className="test-status">Running...</span>}
    </button>
  );
}

export default ApiServicesTestScreen;