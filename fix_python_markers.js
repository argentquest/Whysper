const fs = require('fs');
const path = require('path');

function findPythonFiles(dir) {
  let files = [];
  const items = fs.readdirSync(dir, { withFileTypes: true });
  
  for (const item of items) {
    const fullPath = path.join(dir, item.name);
    if (item.isDirectory()) {
      if (!item.name.startsWith('.') && item.name !== 'node_modules' && item.name !== '__pycache__') {
        files = files.concat(findPythonFiles(fullPath));
      }
    } else if (item.isFile() && item.name.endsWith('.py')) {
      files.push(fullPath);
    }
  }
  return files;
}

function fixPythonFile(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    const originalContent = content;
    
    // Remove ```python from start if present
    if (content.startsWith('```python\n')) {
      content = content.substring('```python\n'.length);
    } else if (content.startsWith('```python')) {
      content = content.substring('```python'.length);
      if (content.startsWith('\n')) {
        content = content.substring(1);
      }
    }
    
    // Remove trailing ``` if present
    if (content.endsWith('\n```')) {
      content = content.substring(0, content.length - 4);
    } else if (content.endsWith('```')) {
      content = content.substring(0, content.length - 3);
    }
    
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

const backendPath = './backend';
const pythonFiles = findPythonFiles(backendPath);

console.log(`Found ${pythonFiles.length} Python files`);

let fixed = 0;
for (const file of pythonFiles) {
  if (fixPythonFile(file)) {
    fixed++;
    const relativePath = file.replace(/^\.\//, '');
    console.log(`✅ Fixed: ${relativePath}`);
  }
}

console.log(`\n✅ Fixed ${fixed} files with markdown markers`);
