/**
 * Test Runner for Architecture Gen Studio
 * Executes all integration and workflow tests
 */

import {
  runIntegrationTests,
  IntegrationTestSuite,
  SCENARIO_AGENT_SELECTION,
  SCENARIO_DIAGRAM_GENERATION,
  SCENARIO_CODE_VALIDATION,
  SCENARIO_VALIDATION_ERROR,
  SCENARIO_REQUEST_CANCELLATION,
  SCENARIO_MULTIPLE_DIAGRAMS,
} from './frontend/src/components/architectureGenStudio/__tests__/integration.test';

import {
  runStateSynchronizationTests,
  StateSynchronizationTestRunner,
} from './frontend/src/components/architectureGenStudio/__tests__/stateSynchronization.test';

import {
  runErrorHandlingTests,
  ErrorHandlingTestRunner,
} from './frontend/src/components/architectureGenStudio/__tests__/errorHandling.test';

/**
 * Main test execution
 */
async function main() {
  console.log('='.repeat(80));
  console.log('Architecture Gen Studio - Integration Test Suite');
  console.log('='.repeat(80));
  console.log('');

  const startTime = Date.now();

  // Test 1: Integration Tests
  console.log('Running Integration Tests...');
  console.log('-'.repeat(80));
  try {
    await runIntegrationTests();
  } catch (error) {
    console.error('Integration tests failed:', error);
  }
  console.log('');

  // Test 2: State Synchronization Tests
  console.log('Running State Synchronization Tests...');
  console.log('-'.repeat(80));
  try {
    await runStateSynchronizationTests();
  } catch (error) {
    console.error('State synchronization tests failed:', error);
  }
  console.log('');

  // Test 3: Error Handling Tests
  console.log('Running Error Handling Tests...');
  console.log('-'.repeat(80));
  try {
    await runErrorHandlingTests();
  } catch (error) {
    console.error('Error handling tests failed:', error);
  }
  console.log('');

  // Summary
  const duration = Date.now() - startTime;
  console.log('='.repeat(80));
  console.log(`Test Suite Completed in ${(duration / 1000).toFixed(2)}s`);
  console.log('='.repeat(80));
  console.log('');
  console.log('Next Steps:');
  console.log('1. ✅ Review the test results above');
  console.log('2. ✅ Deploy backend API if not already running');
  console.log('3. ✅ Configure .env with REACT_APP_API_URL');
  console.log('4. ✅ Run npm start to start the frontend');
  console.log('5. ✅ Navigate to http://localhost:3000/studio');
  console.log('6. ✅ Execute manual workflow tests from workflowTesting.guide.md');
  console.log('');
}

// Run the test suite
main().catch(console.error);
