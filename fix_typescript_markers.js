const fs = require('fs');
const path = require('path');

function findTypeScriptFiles(dir) {
  let files = [];
  const items = fs.readdirSync(dir, { withFileTypes: true });
  
  for (const item of items) {
    const fullPath = path.join(dir, item.name);
    if (item.isDirectory()) {
      if (!item.name.startsWith('.') && item.name !== 'node_modules' && item.name !== '__pycache__') {
        files = files.concat(findTypeScriptFiles(fullPath));
      }
    } else if (item.isFile() && (item.name.endsWith('.ts') || item.name.endsWith('.tsx'))) {
      files.push(fullPath);
    }
  }
  return files;
}

function fixTypeScriptFile(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    const originalContent = content;
    
    // Remove ```typescript or ```tsx from start if present
    if (content.startsWith('```typescript\n')) {
      content = content.substring('```typescript\n'.length);
    } else if (content.startsWith('```typescript')) {
      content = content.substring('```typescript'.length);
      if (content.startsWith('\n')) {
        content = content.substring(1);
      }
    } else if (content.startsWith('```tsx\n')) {
      content = content.substring('```tsx\n'.length);
    } else if (content.startsWith('```tsx')) {
      content = content.substring('```tsx'.length);
      if (content.startsWith('\n')) {
        content = content.substring(1);
      }
    } else if (content.startsWith('```javascript\n')) {
      content = content.substring('```javascript\n'.length);
    } else if (content.startsWith('```javascript')) {
      content = content.substring('```javascript'.length);
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

const frontendPath = './frontend/src';
const typeScriptFiles = findTypeScriptFiles(frontendPath);

console.log(`Found ${typeScriptFiles.length} TypeScript/TSX files`);

let fixed = 0;
for (const file of typeScriptFiles) {
  if (fixTypeScriptFile(file)) {
    fixed++;
    const relativePath = file.replace(/^\.\//, '');
    console.log(`✅ Fixed: ${relativePath}`);
  }
}

console.log(`\n✅ Fixed ${fixed} TypeScript/TSX files with markdown markers`);
