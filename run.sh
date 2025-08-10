#!/bin/bash

# Simple RAG System Startup Script

echo "🚀 Starting Simple RAG System..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment and run chat
source .venv/bin/activate
python chat.py "$@"
