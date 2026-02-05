#!/bin/bash

# Budget Transparency App - Start Backend Script
# This script starts the Python FastAPI backend

echo "=========================================="
echo "Starting Backend (FastAPI)"
echo "=========================================="

cd app/python_service

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Activate venv
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "❌ Dependencies not installed!"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Start server
echo "✅ Starting FastAPI server on http://127.0.0.1:8000"
echo "📚 API Documentation: http://127.0.0.1:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo "=========================================="

uvicorn main:app --reload --host 127.0.0.1 --port 8000
