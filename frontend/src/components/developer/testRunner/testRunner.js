// Test Runner Component - Developer tool for running backend tests
// Simple interface to view available tests and execute them with results display

import React from 'react';
import { useGameTester } from '../../../app/hooks/useGameTester.js';
import { Button, Card, CardSection } from '../../../shared/ui/index.js';

/**
 * Test Runner Component - Interface for running backend tests
 * @returns {JSX.Element} Test runner interface
 */
export default function TestRunner() {
  const {
    testFiles,
    testFilesCount,
    isLoadingTestFiles,
    testFilesError,
    runTest,
    testResult,
    isRunningTest,
    testRunError,
    resetTestRun
  } = useGameTester();

  // Handle running a specific test
  const handleRunTest = async (testName) => {
    try {
      await runTest(testName);
    } catch (error) {
      // Error is already handled by the hook
      console.error('Test run failed:', error);
    }
  };

  return (
    <Card size="lg">
      {/* Header */}
      <CardSection title="🧪 Test Runner" type="header">
        <p>Developer tool for running backend tests</p>
      </CardSection>

      {/* Test Files Section */}
      <CardSection type="content" title={`Available Tests (${testFilesCount})`}>
        {isLoadingTestFiles && <div>Loading test files...</div>}

        {testFilesError && (
          <div>Error loading test files: {testFilesError.message}</div>
        )}

        {!isLoadingTestFiles && !testFilesError && (
          <ul>
            {testFiles.map((testName) => (
              <li key={testName}>
                <span>{testName}</span>
                <button
                  onClick={() => handleRunTest(testName)}
                  disabled={isRunningTest}
                >
                  {isRunningTest ? 'Running...' : 'Run Test'}
                </button>
              </li>
            ))}
          </ul>
        )}

        {!isLoadingTestFiles &&
          !testFilesError &&
          testFiles.length === 0 && <div>No test files found</div>}
      </CardSection>

      <CardSection
        title="Test Results"
        type="content"
        action={
          <Button size="sm" onClick={resetTestRun}>
            Clear Results
          </Button>
        }
      >
        {testRunError && (
          <div>Error running test: {testRunError.message}</div>
        )}

        {testResult.testName && (
          <CardSection type="content">
            <div>
              <span>Test: </span>
              {testResult.testName}
            </div>

            {testResult.success && (
              <div>
                <span>Result: </span>
                {testResult.message ? 'SUCCESS' : 'FAILED'}
              </div>
            )}

            {testResult.message && (
              <div>
                <span>Message: </span>
                {testResult.message}
              </div>
            )}

            {testResult.error && (
              <div>
                <span>Error: </span>
                <div>{testResult.error}</div>
              </div>
            )}

            {testResult.traceback && (
              <div>
                <span>Traceback: </span>
                <div>{testResult.traceback}</div>
              </div>
            )}

            {testResult.output && (
              <div>
                <span>Output: </span>
                <Card size="sm" background="dark">
                  <pre>{testResult.output}</pre>
                </Card>
              </div>
            )}
          </CardSection>
        )}
      </CardSection>
    </Card>
  );
}
