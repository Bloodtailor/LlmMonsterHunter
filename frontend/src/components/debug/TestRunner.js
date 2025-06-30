// Test Runner Component - CLEANED UP
// Displays available tests and runs them with output display

import React, { useState, useEffect } from 'react';

// Helper function for API calls
async function apiRequest(url, options = {}) {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options
  });
  return await response.json();
}

// Helper function to get test status
function getTestStatus(testResults, testName) {
  const result = testResults[testName];
  if (!result) return 'not-run';
  return result.success ? 'success' : 'error';
}

// Helper function to format output
const formatOutput = (output) => output ? output.trim() : 'No output';

// Test Output Section Component
function TestOutputSection({ result }) {
  if (!result) return null;
  
  return (
    <div className="test-output-section">
      <details>
        <summary>
          📋 Output ({result.output?.length || 0} chars)
        </summary>
        
        <div className="test-output">
          <pre>{formatOutput(result.output)}</pre>
        </div>
        
        {result.error && (
          <div className="test-error">
            <h6>❌ Error Details:</h6>
            <pre>{result.error}</pre>
          </div>
        )}
        
        {result.traceback && (
          <div className="test-traceback">
            <h6>🔍 Stack Trace:</h6>
            <pre>{result.traceback}</pre>
          </div>
        )}
      </details>
    </div>
  );
}

// Individual Test Item Component
function TestItem({ testName, testResults, onRunTest, runningTest }) {
  const result = testResults[testName];
  const status = getTestStatus(testResults, testName);
  const isRunning = runningTest === testName;
  
  return (
    <div className={`test-item ${status}`}>
      <div className="test-info">
        <h5>{testName}</h5>
        <p className="test-file">backend/tests/{testName}.py</p>
        
        {result && (
          <div className="test-status">
            <span className={`status-badge ${status === 'success' ? 'status-completed' : 'status-failed'}`}>
              {result.success ? '✅ Passed' : '❌ Failed'}
            </span>
            <span className="test-time">
              {result.timestamp}
            </span>
          </div>
        )}
      </div>
      
      <div className="test-actions">
        <button 
          onClick={() => onRunTest(testName)}
          disabled={isRunning}
          className="btn btn-primary"
        >
          {isRunning ? '🔄 Running...' : '▶️ Run Test'}
        </button>
      </div>
      
      <TestOutputSection result={result} />
    </div>
  );
}

function TestRunner() {
  const [availableTests, setAvailableTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [runningTest, setRunningTest] = useState(null);
  const [testResults, setTestResults] = useState({});
  const [error, setError] = useState(null);

  // Load available tests on component mount
  useEffect(() => {
    loadAvailableTests();
  }, []);

  const loadAvailableTests = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const tests = await apiRequest('http://localhost:5000/api/game_tester/tests');
      
      if (Array.isArray(tests)) {
        setAvailableTests(tests);
      } else {
        setError('Invalid response format from tests endpoint');
      }
    } catch (err) {
      setError(`Failed to load tests: ${err.message}`);
    }
    
    setLoading(false);
  };

  const runTest = async (testName) => {
    setRunningTest(testName);
    setError(null);
    
    try {
      const result = await apiRequest(`http://localhost:5000/api/game_tester/run/${testName}`);
      
      setTestResults(prev => ({
        ...prev,
        [testName]: {
          ...result,
          timestamp: new Date().toLocaleTimeString()
        }
      }));
      
    } catch (err) {
      setTestResults(prev => ({
        ...prev,
        [testName]: {
          success: false,
          error: err.message,
          timestamp: new Date().toLocaleTimeString()
        }
      }));
    }
    
    setRunningTest(null);
  };

  const clearResults = () => setTestResults({});

  if (loading) {
    return (
      <div className="test-runner">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p className="loading-text">Loading available tests...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="test-runner">
      <div className="test-runner-header">
        <h3>🧪 Backend Test Runner</h3>
        <p>Run backend tests in the Flask environment and see their output</p>
        
        <div className="test-runner-controls">
          <button onClick={loadAvailableTests} className="btn btn-secondary">
            🔄 Refresh Tests
          </button>
          <button onClick={clearResults} className="btn btn-danger btn-sm">
            🗑️ Clear Results
          </button>
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          <h4>❌ Error</h4>
          <p>{error}</p>
        </div>
      )}

      {availableTests.length === 0 ? (
        <div className="no-tests">
          <p>No test files found in backend/tests/</p>
          <p>Create some .py files in the tests directory to see them here!</p>
        </div>
      ) : (
        <div className="test-list">
          <h4>📋 Available Tests ({availableTests.length})</h4>
          
          <div className="flex flex-col gap-md">
            {availableTests.map(testName => (
              <TestItem
                key={testName}
                testName={testName}
                testResults={testResults}
                onRunTest={runTest}
                runningTest={runningTest}
              />
            ))}
          </div>
        </div>
      )}
      
      <div className="test-runner-footer">
        <p><strong>💡 How to add tests:</strong></p>
        <ol>
          <li>Create a .py file in <code>backend/tests/</code></li>
          <li>Write your test code (it will run in Flask context)</li>
          <li>Click "Refresh Tests" to see it appear here</li>
          <li>Run and see the output in real-time!</li>
        </ol>
      </div>
    </div>
  );
}

export default TestRunner;