#!/bin/bash

# Simple RAG - Application Runner

set -e

echo "🚀 Starting Simple RAG chat application..."

# Check if virtual environment exists and use it
if [ -f "venv/bin/activate" ]; then
    echo "🔌 Using virtual environment..."
    source venv/bin/activate
    python chat.py
else
    echo "⚠️  No virtual environment found, using system Python"
    python3 chat.py
fi
