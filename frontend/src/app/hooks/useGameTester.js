// useGameTester Hook - Game testing functionality
// Manages test files and test execution using useAsyncState pattern
// Simple, focused hook for viewing available tests and running them

import { useEffect } from 'react';
import { useAsyncState } from '../../shared/hooks/useAsyncState.js';
import { getTestFiles, runTest } from '../../api/services/gameTester.js';

export function useGameTester() {
  // State for loading and managing test files list
  const testFilesState = useAsyncState(getTestFiles);
  
  // State for running individual tests
  const runTestState = useAsyncState(runTest);
  
  // Load test files on mount
  useEffect(() => {
    testFilesState.execute();
  }, [testFilesState.execute]);
  
  // Computed values
  const testFilesCount = testFilesState.data?.testFiles?.length ?? 0;
  
  return {
    // ==== TEST FILES MANAGEMENT ====
    
    /** @type {string[]} Array of available test file names */
    testFiles: testFilesState.data?.testFiles ?? [],
    
    testFilesCount,
    isLoadingTestFiles: testFilesState.isLoading,
    testFilesError: testFilesState.error,
    
    isRunningTest: runTestState.isLoading,
    testRunError: runTestState.error,
    
    testResult: runTestState.data,

    /**
     * Run a specific test file
     * @param {string} testName - Name of test file to run (without .py extension)
     * @returns {Promise<object>} Test execution results
     */
    runTest: runTestState.execute,
    
    // ==== RESET FUNCTIONS ====
    
    resetTestRun: runTestState.reset
  };
}