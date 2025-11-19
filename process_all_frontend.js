#!/usr/bin/env node
/**
 * Master automation script to process ALL frontend TypeScript/TSX files with inline comments.
 * Handles batch processing, progress tracking, error recovery, and reporting.
 */

const fs = require('fs').promises;
const path = require('path');
const { spawn } = require('child_process');

// Configuration
const ROOT_DIR = __dirname;
const FRONTEND_DIR = path.join(ROOT_DIR, 'frontend', 'src');
const SCRIPT_PATH = path.join(ROOT_DIR, 'add-inline-comments.js');
const MANIFEST_FILE = path.join(ROOT_DIR, 'frontend_comments_manifest.json');
const LOG_FILE = path.join(ROOT_DIR, 'frontend_comments_processing.log');

// Batch size for processing
const BATCH_SIZE = 5; // Process 5 files at a time to manage API rate limits

class FrontendProcessor {
  constructor() {
    this.manifest = null;
    this.startTime = new Date();
    this.stats = {
      total_files: 0,
      processed: 0,
      failed: 0,
      skipped: 0,
      total_comments_added: 0
    };
  }

  async loadManifest() {
    try {
      const content = await fs.readFile(MANIFEST_FILE, 'utf8');
      this.manifest = JSON.parse(content);
    } catch {
      this.manifest = {
        processed_files: [],
        failed_files: [],
        skipped_files: [],
        files_stats: {}
      };
    }
  }

  async saveManifest() {
    this.manifest.last_updated = new Date().toISOString();
    this.manifest.stats = this.stats;
    try {
      await fs.writeFile(MANIFEST_FILE, JSON.stringify(this.manifest, null, 2));
    } catch (error) {
      this.log(`Error saving manifest: ${error.message}`);
    }
  }

  log(message) {
    const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
    const logMsg = `[${timestamp}] ${message}`;
    console.log(logMsg);
    fs.appendFile(LOG_FILE, logMsg + '\n').catch(() => {});
  }

  async getAllTsFiles() {
    const files = [];
    const excludeDirs = new Set(['node_modules', '.git', 'dist', 'build', 'coverage']);

    async function walk(dir) {
      const entries = await fs.readdir(dir, { withFileTypes: true });

      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);

        if (entry.isDirectory()) {
          if (!excludeDirs.has(entry.name)) {
            await walk(fullPath);
          }
        } else if (entry.isFile()) {
          const ext = path.extname(entry.name);
          if (['.ts', '.tsx'].includes(ext) && !entry.name.endsWith('.test.ts') && !entry.name.endsWith('.test.tsx')) {
            files.push(fullPath);
          }
        }
      }
    }

    await walk(FRONTEND_DIR);
    return files.sort();
  }

  getPendingFiles(allFiles) {
    const processed = new Set(this.manifest.processed_files || []);
    return allFiles.filter(file => {
      const relativePath = path.relative(ROOT_DIR, file);
      return !processed.has(relativePath);
    });
  }

  async processBatch(files) {
    this.log(`\nProcessing batch of ${files.length} files...`);

    return new Promise((resolve) => {
      const child = spawn('node', [SCRIPT_PATH, ...files], {
        stdio: ['inherit', 'pipe', 'pipe'],
        timeout: 300000 // 5 minute timeout
      });

      let output = '';
      let errorOutput = '';

      child.stdout.on('data', (data) => {
        const text = data.toString();
        output += text;
        process.stdout.write(text);
      });

      child.stderr.on('data', (data) => {
        const text = data.toString();
        errorOutput += text;
        process.stderr.write(text);
      });

      child.on('close', (code) => {
        // Update manifest
        for (const file of files) {
          const relativePath = path.relative(ROOT_DIR, file);
          if (code === 0) {
            if (!this.manifest.processed_files.includes(relativePath)) {
              this.manifest.processed_files.push(relativePath);
            }
            this.stats.processed++;
          } else {
            if (!this.manifest.failed_files.includes(relativePath)) {
              this.manifest.failed_files.push(relativePath);
            }
            this.stats.failed++;
          }
        }

        resolve({
          success: code === 0,
          output: output
        });
      });

      child.on('error', (error) => {
        this.log(`Error spawning process: ${error.message}`);
        for (const file of files) {
          const relativePath = path.relative(ROOT_DIR, file);
          if (!this.manifest.failed_files.includes(relativePath)) {
            this.manifest.failed_files.push(relativePath);
          }
        }
        this.stats.failed += files.length;

        resolve({
          success: false,
          output: error.message
        });
      });
    });
  }

  async run() {
    this.log('='.repeat(80));
    this.log('FRONTEND INLINE COMMENTS - MASTER AUTOMATION');
    this.log('='.repeat(80));

    // Load manifest
    await this.loadManifest();

    // Get all TypeScript files
    const allFiles = await this.getAllTsFiles();
    this.stats.total_files = allFiles.length;

    this.log(`\nFound ${allFiles.length} TypeScript/TSX files in frontend/src/`);

    // Get pending files
    const pendingFiles = this.getPendingFiles(allFiles);
    const alreadyProcessed = allFiles.length - pendingFiles.length;

    this.log(`Already processed: ${alreadyProcessed}`);
    this.log(`Remaining to process: ${pendingFiles.length}`);

    if (pendingFiles.length === 0) {
      this.log('\nAll files already processed!');
      return;
    }

    // Process in batches
    const totalBatches = Math.ceil(pendingFiles.length / BATCH_SIZE);

    for (let i = 0; i < pendingFiles.length; i += BATCH_SIZE) {
      const batch = pendingFiles.slice(i, i + BATCH_SIZE);
      const batchNum = Math.floor(i / BATCH_SIZE) + 1;

      this.log('\n' + '='.repeat(80));
      this.log(`BATCH ${batchNum}/${totalBatches}`);
      this.log('='.repeat(80));

      // Process batch
      await this.processBatch(batch);

      // Save progress after each batch
      await this.saveManifest();

      // Small delay between batches
      if (i + BATCH_SIZE < pendingFiles.length) {
        this.log('Waiting 2 seconds before next batch...');
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }

    // Final summary
    this.log('\n' + '='.repeat(80));
    this.log('FINAL SUMMARY');
    this.log('='.repeat(80));
    this.log(`Total TypeScript/TSX files: ${this.stats.total_files}`);
    this.log(`Successfully processed: ${this.stats.processed}`);
    this.log(`Failed: ${this.stats.failed}`);
    this.log(`Skipped: ${this.stats.skipped}`);

    const elapsed = new Date() - this.startTime;
    const minutes = Math.floor(elapsed / 60000);
    const seconds = Math.floor((elapsed % 60000) / 1000);
    this.log(`\nTime elapsed: ${minutes}m ${seconds}s`);
    this.log(`Manifest: ${MANIFEST_FILE}`);
    this.log(`Log file: ${LOG_FILE}`);

    // List failed files if any
    if (this.manifest.failed_files && this.manifest.failed_files.length > 0) {
      this.log('\nFailed files:');
      for (const f of this.manifest.failed_files) {
        this.log(`  - ${f}`);
      }
    }
  }
}

// Main execution
async function main() {
  const processor = new FrontendProcessor();
  await processor.run();
}

main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
