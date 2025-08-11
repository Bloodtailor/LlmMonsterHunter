// Test Runner Component - Developer tool for running backend tests
// UPDATED: Now uses Select component for test selection instead of individual buttons
// Better UX with single dropdown + run button

import React, { useState, useCallback } from 'react';
import { useGameTester } from '../../../app/hooks/useGameTester.js';
import { Button, Card, CardSection, Select, FormField, StatusBadge, Alert, LoadingSpinner } from '../../../shared/ui/index.js';

/**
 * Test Runner Component - Interface for running backend tests
 * @returns {JSX.Element} Test runner interface
 */
export default function TestRunner() {
  // Local state for selected test
  const [selectedTest, setSelectedTest] = useState('');

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

  // Handle test selection change
  const handleTestSelection = useCallback((event) => {
    setSelectedTest(event.target.value);
  }, []);

  // Handle running the selected test
  const handleRunSelectedTest = useCallback(async () => {
    if (!selectedTest) {
      console.warn('No test selected');
      return;
    }

    try {
      await runTest(selectedTest);
      // Keep selection after successful run so user can re-run if needed
    } catch (error) {
      // Error is already handled by the hook
      console.error('Test run failed:', error);
    }
  }, [selectedTest, runTest]);

  // Handle clearing results and selection
  const handleClear = useCallback(() => {
    resetTestRun();
    setSelectedTest('');
  }, [resetTestRun]);

  // Prepare options for Select component
  const testOptions = [
    { value: '', label: 'Choose a test...' },
    ...testFiles.map(testName => ({
      value: testName,
      label: testName
    }))
  ];

  return (
    <Card size="lg" >
      {/* Header */}
      <CardSection title="🧪 Test Runner" type="header"/>

      {/* Test Selection Section */}
      <CardSection type="content" title={`Test Selection (${testFilesCount} available)`}>
        
        {/* Loading State */}
        {isLoadingTestFiles && (
          <div style={{ padding: '1rem', textAlign: 'center', color: 'var(--text-dim)' }}>
            Loading test files...
          </div>
        )}

        {/* Error State */}
        {testFilesError && (
          <Alert type="error" title="Failed to load test files">
            {testFilesError.message}
          </Alert>
        )}

        {/* Test Selection Form */}
        {!isLoadingTestFiles && !testFilesError && testFiles.length > 0 && (
          <div style={{ display: 'flex', gap: '1rem' }}>
            <FormField label="Select Test to Run" >
              <Select
                value={selectedTest}
                onChange={handleTestSelection}
                options={testOptions}
                disabled={isRunningTest}
                style={{width: '200px'}}
              />
            </FormField>
            
            <Button
              variant="primary"
              onClick={handleRunSelectedTest}
              disabled={!selectedTest || isRunningTest}
              loading={isRunningTest}
            >
              {isRunningTest ? 'Running Test...' : 'Run Test'}
            </Button>
          </div>
        )}

        {/* No Tests Available */}
        {!isLoadingTestFiles && !testFilesError && testFiles.length === 0 && (
          <div style={{ padding: '1rem', textAlign: 'center', color: 'var(--text-dim)' }}>
            No test files found in backend
          </div>
        )}
      </CardSection>

      {/* Test Results Section */}
      <CardSection
        title="Test Results"
        type="content"
        action={
          (testResult.testName || testRunError) && (
            <Button size="sm" variant="secondary" onClick={handleClear}>
              Clear Results
            </Button>
          )
        }
      >

        {isRunningTest ? (
          <div >
            <LoadingSpinner size='card'/>
          </div>
        ) : testRunError ? (
          <Alert type="error" title="Test Execution Failed">
            {testRunError.message}
          </Alert>
        ) : testResult.testName ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            
            {/* Test Header */}
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              padding: '0.5rem',
              background: 'var(--background-light)',
              borderRadius: 'var(--radius-sm)'
            }}>
              <div>
                <strong>Test:</strong> {testResult.testName}
              </div>
              <StatusBadge 
                status={testResult.success ? 'success' : 'error'} 
                size="md"
              >
                {testResult.success ? 'PASSED' : 'FAILED'}
              </StatusBadge>
            </div>

            {/* Success Message */}
            {testResult.message && (
              <div style={{ 
                padding: '0.75rem',
                background: 'var(--background-light)',
                borderRadius: 'var(--radius-sm)',
                borderLeft: '4px solid var(--success-color)'
              }}>
                <strong>Message:</strong> {testResult.message}
              </div>
            )}

            {/* Error Details */}
            {testResult.error && (
              <Alert type="error" title="Test Error">
                {testResult.error}
              </Alert>
            )}

            {/* Traceback */}
            {testResult.traceback && (
              <div>
                <h4 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-light)' }}>
                  Traceback:
                </h4>
                <Card size="sm" background="dark">
                  <pre style={{ 
                    margin: 0, 
                    fontSize: 'var(--font-size-sm)',
                    lineHeight: '1.4',
                    overflow: 'auto',
                    maxHeight: '200px'
                  }}>
                    {testResult.traceback}
                  </pre>
                </Card>
              </div>
            )}

            {/* Test Output */}
            {testResult.output && (
              <div>
                <h4 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-light)' }}>
                  Output:
                </h4>
                <Card size="sm" background="dark">
                  <pre style={{ 
                    margin: 0, 
                    fontSize: 'var(--font-size-sm)',
                    lineHeight: '1.4',
                    overflow: 'auto',
                    maxHeight: '300px',
                    whiteSpace: 'pre-wrap'
                  }}>
                    {testResult.output}
                  </pre>
                </Card>
              </div>
            )}
          </div>
        ) : (
          <div style={{ 
            padding: '2rem', 
            textAlign: 'center', 
            color: 'var(--text-dim)',
            fontStyle: 'italic'
          }}>
            Select a test and click "Run Test" to see results here
          </div>
        )}
      </CardSection>
    </Card>
  );
}