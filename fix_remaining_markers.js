const fs = require('fs');
const path = require('path');

function removeMarkers(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    const originalContent = content;

    // Remove markdown code block markers and preamble patterns
    // Pattern 1: Remove opening and closing code block markers with language
    content = content.replace(/^```\w+\n?/gm, '');
    content = content.replace(/\n?^```\n?/gm, '');

    // Pattern 2: Remove AI explanation preamble patterns
    const explanationPatterns = [
      /\n+I've added inline comments[\s\S]*$/,
      /\n+The comments explain[\s\S]*$/,
      /\n+This code[\s\S]*$/,
      /\n+Here's what[\s\S]*$/,
      /\n+These comments[\s\S]*$/,
      /\n+The inline comments[\s\S]*$/,
      /\n+You can[\s\S]*$/,
      /\n+Would you like[\s\S]*$/,
      /\n+This pattern[\s\S]*$/,
      /\n+The key[\s\S]*$/,
      /\n+Each section[\s\S]*$/,
    ];

    for (const pattern of explanationPatterns) {
      content = content.replace(pattern, '');
    }

    // Pattern 3: Clean trailing whitespace and empty lines at end
    content = content.trimRight() + '\n';

    if (content !== originalContent) {
      fs.writeFileSync(filePath, content, 'utf8');
      return true;
    }
    return false;
  } catch (error) {
    console.error('Error processing ' + filePath + ':', error.message);
    return false;
  }
}

// List of files with markers
const filesToFix = [
  'backend/validate_history_d2.py',
  'backend/tests/conftest.py',
  'backend/tests/2-INTEGRATION/provider_core/test_provider_integration.py',
  'backend/tests/2-INTEGRATION/provider_core/conftest.py',
  'backend/tests/2-INTEGRATION/llm_testing/kroki_structurizr/__init__.py',
  'backend/tests/2-INTEGRATION/llm_testing/kroki_d2/__init__.py',
  'backend/mvp_diagram_generator/renderer_v3_mermaid_cli_only.py',
  'backend/mvp_diagram_generator/diagram_validators.py',
  'backend/diagrams/__init__.py',
  'backend/diagrams/tests/test_config.py',
  'backend/diagrams/tests/d2v1/test_d2_config.py',
  'backend/diagrams/mermaidv1/__init__.py',
  'backend/diagrams/kroki_base.py',
  'backend/diagrams/krokistructurizr/__init__.py',
  'backend/diagrams/krokistructurizr/kroki_renderer.py',
  'backend/diagrams/krokimermaid/__init__.py',
  'backend/diagrams/krokid2/__init__.py',
  'backend/diagrams/krokic4/__init__.py',
  'backend/diagrams/d2v1/__init__.py',
  'backend/app/utils/diagram_wizard/tool_config.py',
  'backend/app/utils/diagram_wizard/session_store.py',
  'backend/app/utils/diagram_wizard/prompt_loader.py',
  'backend/app/utils/diagram_wizard/keyword_scorer.py',
  'backend/app/api/v1/endpoints/code.py',
  'backend/app/api/v1/endpoints/auth.py',
  'backend/tests/2-INTEGRATION/provider_core/__init__.py',
  'backend/tests/2-INTEGRATION/llm_testing/mermaid/__init__.py',
  'backend/tests/2-INTEGRATION/llm_testing/d2/__init__.py',
  'backend/tests/1-UNIT/utils/test_code_extraction.py',
  'backend/tests/1-UNIT/utils/conftest.py',
  'backend/tests/1-UNIT/providers/test_llm_correction_service.py',
  'backend/diagrams/tests/test_llm_correction_service.py',
  'backend/diagrams/llm_correction_service.py',
];

let fixedCount = 0;
console.log('Cleaning ' + filesToFix.length + ' Python files with markers...\n');

for (const file of filesToFix) {
  const fullPath = path.join('.', file);
  if (removeMarkers(fullPath)) {
    fixedCount++;
    console.log('✅ Fixed: ' + file);
  }
}

console.log('\n✅ Fixed ' + fixedCount + ' files');
