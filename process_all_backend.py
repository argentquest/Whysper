#!/usr/bin/env python3
"""
Master automation script to process ALL backend Python files with inline comments.
Handles batch processing, progress tracking, error recovery, and reporting.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Configuration
ROOT_DIR = Path(__file__).parent
BACKEND_DIR = ROOT_DIR / "backend"
SCRIPT_PATH = ROOT_DIR / "add_inline_comments.py"
MANIFEST_FILE = ROOT_DIR / "backend_comments_manifest.json"
LOG_FILE = ROOT_DIR / "backend_comments_processing.log"

# Batch size for processing
BATCH_SIZE = 5  # Process 5 files at a time to manage API rate limits


class BackendProcessor:
    def __init__(self):
        self.manifest = self.load_manifest()
        self.start_time = datetime.now()
        self.stats = {
            'total_files': 0,
            'processed': 0,
            'failed': 0,
            'skipped': 0,
            'total_comments_added': 0
        }

    def load_manifest(self) -> Dict:
        """Load existing manifest if available"""
        if MANIFEST_FILE.exists():
            try:
                with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            'processed_files': [],
            'failed_files': [],
            'skipped_files': [],
            'files_stats': {}
        }

    def save_manifest(self):
        """Save progress to manifest"""
        self.manifest['last_updated'] = datetime.now().isoformat()
        self.manifest['stats'] = self.stats
        try:
            with open(MANIFEST_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.manifest, f, indent=2)
        except Exception as e:
            self.log(f"Error saving manifest: {e}")

    def log(self, message: str):
        """Log to both console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        try:
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(log_msg + "\n")
        except:
            pass

    def get_all_python_files(self) -> List[Path]:
        """Get all Python files recursively"""
        python_files = []
        exclude_dirs = {'.venv', 'venv', '__pycache__', '.pytest_cache', '.mypy_cache', 'node_modules'}

        for root, dirs, files in os.walk(BACKEND_DIR):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                if file.endswith('.py') and not file.startswith('test_'):
                    file_path = Path(root) / file
                    python_files.append(file_path)

        return sorted(python_files)

    def get_pending_files(self, all_files: List[Path]) -> List[Path]:
        """Get files that haven't been processed yet"""
        processed = set(self.manifest.get('processed_files', []))
        pending = []

        for file_path in all_files:
            relative_path = str(file_path.relative_to(ROOT_DIR))
            if relative_path not in processed:
                pending.append(file_path)

        return pending

    def process_batch(self, files: List[Path]) -> Dict:
        """Process a batch of files"""
        file_paths = [str(f) for f in files]

        self.log(f"\nProcessing batch of {len(files)} files...")

        try:
            # Call the add_inline_comments.py script
            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH)] + file_paths,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per batch
            )

            # Parse output to get statistics
            output = result.stdout
            self.log(output)

            # Update manifest with processed files
            for file_path in files:
                relative_path = str(file_path.relative_to(ROOT_DIR))
                if result.returncode == 0:
                    if relative_path not in self.manifest['processed_files']:
                        self.manifest['processed_files'].append(relative_path)
                    self.stats['processed'] += 1
                else:
                    if relative_path not in self.manifest['failed_files']:
                        self.manifest['failed_files'].append(relative_path)
                    self.stats['failed'] += 1

            return {
                'success': result.returncode == 0,
                'output': output
            }

        except subprocess.TimeoutExpired:
            self.log(f"Batch processing timed out!")
            for file_path in files:
                relative_path = str(file_path.relative_to(ROOT_DIR))
                if relative_path not in self.manifest['failed_files']:
                    self.manifest['failed_files'].append(relative_path)
            self.stats['failed'] += len(files)
            return {'success': False, 'output': 'Timeout'}

        except Exception as e:
            self.log(f"Error processing batch: {e}")
            for file_path in files:
                relative_path = str(file_path.relative_to(ROOT_DIR))
                if relative_path not in self.manifest['failed_files']:
                    self.manifest['failed_files'].append(relative_path)
            self.stats['failed'] += len(files)
            return {'success': False, 'output': str(e)}

    def run(self):
        """Main execution"""
        self.log("=" * 80)
        self.log("BACKEND INLINE COMMENTS - MASTER AUTOMATION")
        self.log("=" * 80)

        # Get all Python files
        all_files = self.get_all_python_files()
        self.stats['total_files'] = len(all_files)

        self.log(f"\nFound {len(all_files)} Python files in backend/")

        # Get pending files
        pending_files = self.get_pending_files(all_files)
        already_processed = len(all_files) - len(pending_files)

        self.log(f"Already processed: {already_processed}")
        self.log(f"Remaining to process: {len(pending_files)}")

        if not pending_files:
            self.log("\nAll files already processed!")
            return

        # Process in batches
        total_batches = (len(pending_files) + BATCH_SIZE - 1) // BATCH_SIZE

        for i in range(0, len(pending_files), BATCH_SIZE):
            batch = pending_files[i:i + BATCH_SIZE]
            batch_num = (i // BATCH_SIZE) + 1

            self.log(f"\n{'=' * 80}")
            self.log(f"BATCH {batch_num}/{total_batches}")
            self.log(f"{'=' * 80}")

            # Process batch
            result = self.process_batch(batch)

            # Save progress after each batch
            self.save_manifest()

            # Small delay between batches to respect API rate limits
            if i + BATCH_SIZE < len(pending_files):
                import time
                self.log("Waiting 2 seconds before next batch...")
                time.sleep(2)

        # Final summary
        self.log("\n" + "=" * 80)
        self.log("FINAL SUMMARY")
        self.log("=" * 80)
        self.log(f"Total Python files: {self.stats['total_files']}")
        self.log(f"Successfully processed: {self.stats['processed']}")
        self.log(f"Failed: {self.stats['failed']}")
        self.log(f"Skipped: {self.stats['skipped']}")

        elapsed = datetime.now() - self.start_time
        self.log(f"\nTime elapsed: {elapsed}")
        self.log(f"Manifest: {MANIFEST_FILE}")
        self.log(f"Log file: {LOG_FILE}")

        # List failed files if any
        if self.manifest.get('failed_files'):
            self.log("\nFailed files:")
            for f in self.manifest['failed_files']:
                self.log(f"  - {f}")


if __name__ == "__main__":
    processor = BackendProcessor()
    processor.run()
