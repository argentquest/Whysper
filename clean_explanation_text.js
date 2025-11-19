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

function removeExplanationText(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    const originalContent = content;

    // Remove leftover explanation text patterns
    // These are common patterns AI leaves after code
    const patterns = [
      /^\n+The comments explain:[\s\S]*$/m,
      /^\n+This code[\s\S]*$/m,
      /^\n+Here's what[\s\S]*$/m,
      /^\n+These comments[\s\S]*$/m,
      /^\n+The inline comments[\s\S]*$/m,
      /^\n+You can[\s\S]*$/m,
      /^\n+Would you like[\s\S]*$/m,
      /^\n+This pattern[\s\S]*$/m,
      /^\n+The key[\s\S]*$/m,
      /^\n+Each section[\s\S]*$/m,
      /^\n+\d+\. [\s\S]*$/m,
    ];

    for (const pattern of patterns) {
      content = content.replace(pattern, '');
    }

    // Also clean up any remaining text after the last meaningful code line
    // Look for lines that start with capital letters followed by explanatory text
    const lines = content.split('\n');
    let lastCodeLineIndex = -1;

    // Find the last line that looks like actual code
    for (let i = lines.length - 1; i >= 0; i--) {
      const line = lines[i].trim();
      // Skip empty lines
      if (!line) continue;
      // Check if line looks like it's part of explanation (starts with capital letter, no code chars)
      if (/^[A-Z]/.test(line) && !line.includes('(') && !line.includes('{') && !line.includes('[')) {
        continue;
      }
      // This looks like code
      lastCodeLineIndex = i;
      break;
    }

    if (lastCodeLineIndex >= 0 && lastCodeLineIndex < lines.length - 1) {
      content = lines.slice(0, lastCodeLineIndex + 1).join('\n').trim() + '\n';
    }

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

// Fix both TypeScript and Python files
const frontendPath = './frontend/src';
const backendPath = './backend';

const typeScriptFiles = findCodeFiles(frontendPath, ['.ts', '.tsx']);
const pythonFiles = findCodeFiles(backendPath, ['.py']);

console.log('Scanning ' + typeScriptFiles.length + ' TypeScript/TSX files');
console.log('Scanning ' + pythonFiles.length + ' Python files');

let fixedTS = 0;
let fixedPy = 0;

console.log('\n=== Cleaning TypeScript/TSX Files ===');
for (const file of typeScriptFiles) {
  if (removeExplanationText(file)) {
    fixedTS++;
    const relativePath = file.replace(/^\.\//, '');
    console.log('✅ Cleaned: ' + relativePath);
  }
}

console.log('\n=== Cleaning Python Files ===');
for (const file of pythonFiles) {
  if (removeExplanationText(file)) {
    fixedPy++;
    const relativePath = file.replace(/^\.\//, '');
    console.log('✅ Cleaned: ' + relativePath);
  }
}

console.log('\n✅ Cleaned ' + fixedTS + ' TypeScript/TSX files');
console.log('✅ Cleaned ' + fixedPy + ' Python files');
console.log('✅ Total: ' + (fixedTS + fixedPy) + ' files cleaned');
