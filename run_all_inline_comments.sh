#!/bin/bash
# Master script to add inline comments to ALL 321 files in the codebase
# Processes 249 Python files + 72 TypeScript/TSX files

echo "================================================================================"
echo "COMPREHENSIVE INLINE COMMENTS AUTOMATION"
echo "================================================================================"
echo ""
echo "This script will process:"
echo "  - 249 Python files in backend/"
echo "  - 72 TypeScript/TSX files in frontend/src/"
echo ""
echo "Total: 321 files"
echo ""
echo "================================================================================"
echo ""

# Check for ANTHROPIC_API_KEY
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: ANTHROPIC_API_KEY environment variable is not set"
    echo "Please set it using: export ANTHROPIC_API_KEY=your-api-key-here"
    exit 1
fi

echo "[1/2] Processing Backend Python Files..."
echo "================================================================================"
.venv/bin/python process_all_backend.py
if [ $? -ne 0 ]; then
    echo ""
    echo "WARNING: Backend processing had some errors. Check backend_comments_processing.log"
    echo "Continuing with frontend processing..."
    echo ""
else
    echo ""
    echo "Backend processing completed successfully!"
    echo ""
fi

echo ""
echo "[2/2] Processing Frontend TypeScript/TSX Files..."
echo "================================================================================"
node process_all_frontend.js
if [ $? -ne 0 ]; then
    echo ""
    echo "WARNING: Frontend processing had some errors. Check frontend_comments_processing.log"
    echo ""
else
    echo ""
    echo "Frontend processing completed successfully!"
    echo ""
fi

echo ""
echo "================================================================================"
echo "ALL PROCESSING COMPLETE"
echo "================================================================================"
echo ""
echo "Check the following files for details:"
echo "  - backend_comments_manifest.json (Backend progress)"
echo "  - frontend_comments_manifest.json (Frontend progress)"
echo "  - backend_comments_processing.log (Backend log)"
echo "  - frontend_comments_processing.log (Frontend log)"
echo ""
echo "================================================================================"
