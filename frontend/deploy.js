/**
 * Frontend Deployment Script
 * 
 * This script automatically copies the built frontend files to the backend
 * static directory for integrated serving. It handles cross-platform file
 * operations and provides clear feedback on the deployment process.
 * 
 * Usage:
 *   npm run deploy       - Deploy built files to backend
 *   npm run build:deploy - Build and deploy in one command
 */

import { copyFile, mkdir, readdir, stat } from 'fs/promises';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

// Get current directory (ES module equivalent of __dirname)
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Define source and destination paths
const DIST_DIR = join(__dirname, 'dist');
const BACKEND_STATIC_DIR = join(__dirname, '..', 'backend', 'static');

/**
 * Recursively copy directory contents
 */
async function copyDirectory(src, dest) {
  try {
    // Create destination directory if it doesn't exist
    await mkdir(dest, { recursive: true });
    
    // Read source directory contents
    const entries = await readdir(src);
    
    for (const entry of entries) {
      const srcPath = join(src, entry);
      const destPath = join(dest, entry);
      
      // Check if entry is a directory or file
      const stats = await stat(srcPath);
      
      if (stats.isDirectory()) {
        // Recursively copy subdirectory
        await copyDirectory(srcPath, destPath);
      } else {
        // Copy file
        await copyFile(srcPath, destPath);
        console.log(`✓ Copied: ${entry}`);
      }
    }
  } catch (error) {
    console.error(`❌ Error copying from ${src} to ${dest}:`, error.message);
    throw error;
  }
}

/**
 * Main deployment function
 */
async function deploy() {
  console.log('🚀 Starting frontend deployment...');
  console.log(`📁 Source: ${DIST_DIR}`);
  console.log(`📁 Destination: ${BACKEND_STATIC_DIR}`);
  console.log('');
  
  try {
    // Check if dist directory exists
    await stat(DIST_DIR);
    
    // Copy all files from dist to backend/static
    await copyDirectory(DIST_DIR, BACKEND_STATIC_DIR);
    
    console.log('');
    console.log('✅ Frontend deployment completed successfully!');
    console.log('🎯 The frontend is now available at the backend server URL');
    console.log('💡 Start the backend server with: cd ../backend && python main.py');
    
  } catch (error) {
    if (error.code === 'ENOENT' && error.path === DIST_DIR) {
      console.error('❌ Dist directory not found. Please run "npm run build" first.');
      console.error('💡 Or use "npm run build:deploy" to build and deploy in one step.');
    } else {
      console.error('❌ Deployment failed:', error.message);
    }
    process.exit(1);
  }
}

// Run deployment if this script is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  deploy();
}

export default deploy;