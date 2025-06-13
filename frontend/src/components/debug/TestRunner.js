// Test Runner Component
// Displays available tests and runs them with output display

import React, { useState, useEffect } from 'react';

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
      const response = await fetch('http://localhost:5000/api/game_tester/tests');
      const tests = await response.json();
      
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
      const response = await fetch(`http://localhost:5000/api/game_tester/run/${testName}`);
      const result = await response.json();
      
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

  const clearResults = () => {
    setTestResults({});
  };

  const getTestStatus = (testName) => {
    const result = testResults[testName];
    if (!result) return 'not-run';
    return result.success ? 'success' : 'error';
  };

  const formatOutput = (output) => {
    if (!output) return 'No output';
    return output.trim();
  };

  if (loading) {
    return (
      <div className="test-runner">
        <div className="loading">
          <div className="loading-spinner"></div>
          <p>Loading available tests...</p>
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
          <button onClick={loadAvailableTests} className="refresh-button">
            🔄 Refresh Tests
          </button>
          <button onClick={clearResults} className="clear-button">
            🗑️ Clear Results
          </button>
        </div>
      </div>

      {error && (
        <div className="test-runner-error">
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
          
          <div className="test-grid">
            {availableTests.map(testName => (
              <div 
                key={testName} 
                className={`test-item ${getTestStatus(testName)}`}
              >
                <div className="test-info">
                  <h5>{testName}</h5>
                  <p className="test-file">backend/tests/{testName}.py</p>
                  
                  {testResults[testName] && (
                    <div className="test-status">
                      <span className={`status-badge ${getTestStatus(testName)}`}>
                        {testResults[testName].success ? '✅ Passed' : '❌ Failed'}
                      </span>
                      <span className="test-time">
                        {testResults[testName].timestamp}
                      </span>
                    </div>
                  )}
                </div>
                
                <div className="test-actions">
                  <button 
                    onClick={() => runTest(testName)}
                    disabled={runningTest === testName}
                    className="run-test-button"
                  >
                    {runningTest === testName ? '🔄 Running...' : '▶️ Run Test'}
                  </button>
                </div>
                
                {testResults[testName] && (
                  <div className="test-output-section">
                    <details>
                      <summary>
                        📋 Output ({testResults[testName].output?.length || 0} chars)
                      </summary>
                      
                      <div className="test-output">
                        <pre>{formatOutput(testResults[testName].output)}</pre>
                      </div>
                      
                      {testResults[testName].error && (
                        <div className="test-error">
                          <h6>❌ Error Details:</h6>
                          <pre>{testResults[testName].error}</pre>
                        </div>
                      )}
                      
                      {testResults[testName].traceback && (
                        <div className="test-traceback">
                          <h6>🔍 Stack Trace:</h6>
                          <pre>{testResults[testName].traceback}</pre>
                        </div>
                      )}
                    </details>
                  </div>
                )}
              </div>
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