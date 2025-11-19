const fs = require('fs');
const path = require('path');

function findCodeFiles(dir, extensions) {
  let files = [];
  const items = fs.readdirSync(dir, { withFileTypes: true });

  for (const item of items) {
    const fullPath = path.join(dir, item.name);
    if (item.isDirectory()) {
      if (!item.name.startsWith('.') && item.name !== 'node_modules' && item.name !== '__pycache__') {
        files = files.concat(findCodeFiles(fullPath, extensions));
      }
    } else if (item.isFile()) {
      const ext = path.extname(item.name);
      if (extensions.includes(ext)) {
        files.push(fullPath);
      }
    }
  }
  return files;
}

function fixFile(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    const originalContent = content;

    // Strip preambles like "Here's the TypeScript code..." or similar
    content = content.replace(/^Here's the .*?:\n\n/i, '');

    // Remove markdown code block markers (```language ... ```)
    // Remove opening markers
    content = content.replace(/^```(?:typescript|tsx|javascript|python|java|go|rust|cpp|c)\n/i, '');
    content = content.replace(/^```(?:typescript|tsx|javascript|python|java|go|rust|cpp|c)$/m, '');

    // Remove closing markers
    if (content.endsWith('\n```')) {
      content = content.substring(0, content.length - 4);
    } else if (content.endsWith('```')) {
      content = content.substring(0, content.length - 3);
    }

    // Clean up any extra whitespace at start/end
    content = content.trim() + '\n';

    if (content !== originalContent) {
      fs.writeFileSync(filePath, content, 'utf8');
      return true;
    }
    return false;
  } catch (error) {
    console.error(`Error processing ${filePath}:`, error.message);
    return false;
  }
}

// Fix both TypeScript and Python files
const frontendPath = './frontend/src';
const backendPath = './backend';

const typeScriptFiles = findCodeFiles(frontendPath, ['.ts', '.tsx']);
const pythonFiles = findCodeFiles(backendPath, ['.py']);

console.log('Found ' + typeScriptFiles.length + ' TypeScript/TSX files');
console.log('Found ' + pythonFiles.length + ' Python files');

let fixedTS = 0;
let fixedPy = 0;

console.log('\n=== Fixing TypeScript/TSX Files ===');
for (const file of typeScriptFiles) {
  if (fixFile(file)) {
    fixedTS++;
    const relativePath = file.replace(/^\.\//, '');
    console.log('✅ Fixed: ' + relativePath);
  }
}

console.log('\n=== Fixing Python Files ===');
for (const file of pythonFiles) {
  if (fixFile(file)) {
    fixedPy++;
    const relativePath = file.replace(/^\.\//, '');
    console.log('✅ Fixed: ' + relativePath);
  }
}

console.log('\n✅ Fixed ' + fixedTS + ' TypeScript/TSX files');
console.log('✅ Fixed ' + fixedPy + ' Python files');
console.log('✅ Total: ' + (fixedTS + fixedPy) + ' files fixed');
