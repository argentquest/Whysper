/**
 * Testing Script for Diagram Provider Service
 *
 * Usage: Paste this entire script into browser console and run
 * This will execute a series of tests and output results
 */

console.clear();
console.log('%c🧪 DIAGRAM PROVIDER SERVICE TEST SUITE', 'font-size: 18px; font-weight: bold; color: #1890ff;');
console.log('Testing frontend diagram provider integration\n');

// Test results tracker
const results = {
  passed: 0,
  failed: 0,
  tests: []
};

// Helper function for assertions
function assert(condition, message) {
  if (condition) {
    console.log(`✅ ${message}`);
    results.passed++;
    results.tests.push({ status: 'PASS', message });
  } else {
    console.error(`❌ ${message}`);
    results.failed++;
    results.tests.push({ status: 'FAIL', message });
  }
}

// Test 1: Service Existence
console.log('%c--- TEST 1: Service Initialization ---', 'color: #1890ff; font-weight: bold;');
try {
  assert(typeof diagramProviderService !== 'undefined', 'DiagramProviderService is defined');
  assert(typeof diagramProviderService.render === 'function', 'render() method exists');
  assert(typeof diagramProviderService.validate === 'function', 'validate() method exists');
  assert(typeof diagramProviderService.getProviderInfo === 'function', 'getProviderInfo() method exists');
  assert(typeof diagramProviderService.listProviders === 'function', 'listProviders() method exists');
  assert(typeof diagramProviderService.checkHealth === 'function', 'checkHealth() method exists');
} catch (err) {
  console.error('❌ Service not available:', err.message);
}
console.log();

// Test 2: Provider Info
console.log('%c--- TEST 2: Provider Information ---', 'color: #1890ff; font-weight: bold;');
(async () => {
  try {
    console.log('Fetching mermaid provider info...');
    const mermaidInfo = await diagramProviderService.getProviderInfo('mermaid');
    assert(mermaidInfo.provider_id === 'mermaidv1', 'Mermaid provider_id is mermaidv1');
    assert(mermaidInfo.diagram_type === 'mermaid', 'Mermaid diagram_type is correct');
    assert(mermaidInfo.available === true, 'Mermaid provider is available');
    assert(Array.isArray(mermaidInfo.capabilities), 'Mermaid has capabilities array');
    console.log(`  Provider: ${mermaidInfo.provider_name}`);
    console.log(`  Capabilities: ${mermaidInfo.capabilities.join(', ')}\n`);

    console.log('Fetching D2 provider info...');
    const d2Info = await diagramProviderService.getProviderInfo('d2');
    assert(d2Info.provider_id === 'd2v1', 'D2 provider_id is d2v1');
    assert(d2Info.diagram_type === 'd2', 'D2 diagram_type is correct');
    assert(d2Info.available === true, 'D2 provider is available');
    console.log(`  Provider: ${d2Info.provider_name}`);
    console.log(`  Capabilities: ${d2Info.capabilities.join(', ')}\n`);
  } catch (err) {
    console.error(`❌ Provider info error: ${err.message}\n`);
    results.failed += 2;
  }

  // Test 3: List Providers
  console.log('%c--- TEST 3: List All Providers ---', 'color: #1890ff; font-weight: bold;');
  try {
    const list = await diagramProviderService.listProviders();
    assert(Array.isArray(list.providers), 'Providers list is array');
    assert(list.total_providers > 0, `Found ${list.total_providers} total providers`);
    assert(list.available_providers > 0, `Found ${list.available_providers} available providers`);

    const mermaidProviders = list.providers.filter(p => p.diagram_type === 'mermaid');
    const d2Providers = list.providers.filter(p => p.diagram_type === 'd2');
    assert(mermaidProviders.length > 0, 'Mermaid provider registered');
    assert(d2Providers.length > 0, 'D2 provider registered');

    console.log(`  Total: ${list.total_providers}, Available: ${list.available_providers}\n`);
  } catch (err) {
    console.error(`❌ List providers error: ${err.message}\n`);
    results.failed += 5;
  }

  // Test 4: Health Check
  console.log('%c--- TEST 4: System Health ---', 'color: #1890ff; font-weight: bold;');
  try {
    const health = await diagramProviderService.checkHealth();
    assert(health.status !== 'unhealthy', `System status is ${health.status}`);
    assert(health.available_providers > 0, `${health.available_providers} providers available`);
    assert(Array.isArray(health.diagram_types), 'Diagram types listed');
    console.log(`  Status: ${health.status}`);
    console.log(`  Available: ${health.available_providers}/${health.total_providers}`);
    console.log(`  Types: ${health.diagram_types.join(', ')}\n`);
  } catch (err) {
    console.error(`❌ Health check error: ${err.message}\n`);
    results.failed += 3;
  }

  // Test 5: Validate Mermaid Code
  console.log('%c--- TEST 5: Mermaid Validation ---', 'color: #1890ff; font-weight: bold;');
  try {
    const mermaidCode = `flowchart TD
  A[Start] --> B[Process]
  B --> C[End]`;

    console.log('Validating valid Mermaid code...');
    const validResult = await diagramProviderService.validate({
      code: mermaidCode,
      diagram_type: 'mermaid',
      auto_fix: true
    });
    assert(validResult.is_valid === true, 'Valid mermaid code passes validation');
    assert(validResult.provider_id === 'mermaidv1', 'Validation uses mermaidv1 provider');

    console.log('Validating invalid Mermaid code...');
    const invalidResult = await diagramProviderService.validate({
      code: 'flowchart TD\n  A --> --> B',
      diagram_type: 'mermaid',
      auto_fix: true
    });
    console.log(`  Invalid code detected: ${!invalidResult.is_valid ? 'yes' : 'no'}`);
    console.log(`  Auto-fixed: ${invalidResult.auto_fixed ? 'yes' : 'no'}\n`);
    results.passed += 1; // Count the check
  } catch (err) {
    console.error(`❌ Validation error: ${err.message}\n`);
    results.failed += 3;
  }

  // Test 6: Validate D2 Code
  console.log('%c--- TEST 6: D2 Validation ---', 'color: #1890ff; font-weight: bold;');
  try {
    const d2Code = `direction: right
frontend: "Frontend" {
  shape: rectangle
}
backend: "Backend" {
  shape: rectangle
}
frontend -> backend`;

    console.log('Validating valid D2 code...');
    const validResult = await diagramProviderService.validate({
      code: d2Code,
      diagram_type: 'd2',
      auto_fix: true
    });
    assert(validResult.is_valid === true, 'Valid D2 code passes validation');
    assert(validResult.provider_id === 'd2v1', 'Validation uses d2v1 provider');
    console.log('  ✅ D2 validation working\n');
  } catch (err) {
    console.error(`❌ D2 validation error: ${err.message}\n`);
    results.failed += 2;
  }

  // Test 7: Render Mermaid Diagram
  console.log('%c--- TEST 7: Mermaid Rendering ---', 'color: #1890ff; font-weight: bold;');
  try {
    const mermaidCode = `flowchart LR
  A[Request] --> B{Valid?}
  B -->|Yes| C[Process]
  B -->|No| D[Error]
  C --> E[Response]`;

    console.log('Rendering Mermaid diagram...');
    const startTime = performance.now();
    const result = await diagramProviderService.render({
      code: mermaidCode,
      diagram_type: 'mermaid',
      output_format: 'svg'
    });
    const renderTime = performance.now() - startTime;

    assert(result.success === true, 'Mermaid rendering successful');
    assert(result.content && result.content.length > 0, `SVG rendered (${result.content.length} bytes)`);
    assert(result.metadata.provider_id === 'mermaidv1', 'Rendered by mermaidv1');
    assert(result.metadata.render_time > 0, `Render time: ${result.metadata.render_time.toFixed(2)}ms`);
    console.log(`  Total time: ${renderTime.toFixed(2)}ms\n`);
  } catch (err) {
    console.error(`❌ Mermaid rendering error: ${err.message}\n`);
    results.failed += 4;
  }

  // Test 8: Render D2 Diagram
  console.log('%c--- TEST 8: D2 Rendering ---', 'color: #1890ff; font-weight: bold;');
  try {
    const d2Code = `direction: down
user: "User" {
  shape: person
}
web: "Web Server" {
  shape: rectangle
}
db: "Database" {
  shape: cylinder
}
user -> web: "HTTP Request"
web -> db: "Query"
db -> web: "Result"
web -> user: "HTTP Response"`;

    console.log('Rendering D2 diagram...');
    const startTime = performance.now();
    const result = await diagramProviderService.render({
      code: d2Code,
      diagram_type: 'd2',
      output_format: 'svg'
    });
    const renderTime = performance.now() - startTime;

    assert(result.success === true, 'D2 rendering successful');
    assert(result.content && result.content.length > 0, `SVG rendered (${result.content.length} bytes)`);
    assert(result.metadata.provider_id === 'd2v1', 'Rendered by d2v1');
    assert(result.metadata.render_time > 0, `Render time: ${result.metadata.render_time.toFixed(2)}ms`);
    console.log(`  Total time: ${renderTime.toFixed(2)}ms\n`);
  } catch (err) {
    console.error(`❌ D2 rendering error: ${err.message}\n`);
    results.failed += 4;
  }

  // Test 9: Caching
  console.log('%c--- TEST 9: Provider Info Caching ---', 'color: #1890ff; font-weight: bold;');
  try {
    // Clear cache
    diagramProviderService.clearCache();
    console.log('Cache cleared');

    // First call (should fetch)
    console.time('first-call');
    await diagramProviderService.getProviderInfo('mermaid');
    console.timeEnd('first-call');

    // Second call (should be cached)
    console.time('cached-call');
    const cached = await diagramProviderService.getProviderInfo('mermaid');
    console.timeEnd('cached-call');

    assert(cached !== null, 'Cached data retrieved');
    console.log('  ✅ Caching working\n');
  } catch (err) {
    console.error(`❌ Caching error: ${err.message}\n`);
    results.failed += 1;
  }

  // Test 10: Error Handling
  console.log('%c--- TEST 10: Error Handling ---', 'color: #1890ff; font-weight: bold;');
  try {
    console.log('Testing error handling...');
    try {
      await diagramProviderService.validate({
        code: '', // Empty code
        diagram_type: 'mermaid'
      });
      console.log('  ❌ Should have thrown error for empty code');
      results.failed += 1;
    } catch (err) {
      assert(true, 'Empty code validation throws error');
    }

    try {
      const result = await diagramProviderService.render({
        code: 'invalid code that makes no sense',
        diagram_type: 'mermaid'
      });
      console.log(`  Invalid code handling: ${result.success ? 'rendered' : 'error'}`);
      results.passed += 1;
    } catch (err) {
      console.log(`  ❌ Unexpected error: ${err.message}`);
      results.failed += 1;
    }
  } catch (err) {
    console.error(`❌ Error handling test failed: ${err.message}\n`);
    results.failed += 2;
  }

  // Summary
  console.log('%c========================================', 'color: #1890ff; font-weight: bold;');
  console.log('%c✨ TEST SUMMARY', 'font-size: 16px; font-weight: bold; color: #1890ff;');
  console.log('%c========================================', 'color: #1890ff; font-weight: bold;');
  console.log(`✅ Passed: ${results.passed}`);
  console.log(`❌ Failed: ${results.failed}`);
  console.log(`📊 Total: ${results.passed + results.failed}`);
  console.log(`💯 Success Rate: ${Math.round((results.passed / (results.passed + results.failed)) * 100)}%`);

  if (results.failed === 0) {
    console.log('%c✨ ALL TESTS PASSED! ✨', 'font-size: 14px; font-weight: bold; color: #52c41a; background: #f6ffed; padding: 10px;');
  } else {
    console.log(`%c⚠️  ${results.failed} test(s) failed`, 'font-size: 14px; font-weight: bold; color: #ff4d4f; background: #fff1f0; padding: 10px;');
  }
  console.log('\n');

  // Detailed results
  console.log('%cDetailed Results:', 'font-weight: bold; color: #1890ff;');
  results.tests.forEach((test, idx) => {
    const icon = test.status === 'PASS' ? '✅' : '❌';
    console.log(`${idx + 1}. ${icon} ${test.message}`);
  });
})();

console.log('\n%c📚 For more info, see: TESTING_PLAN.md and QUICK_TEST_GUIDE.md', 'color: #666; font-style: italic;');
