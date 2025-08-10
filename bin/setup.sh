#!/bin/bash

# Simple RAG - Production Setup Script

set -e

echo "🚀 Setting up Simple RAG for production..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8+"
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $required_version or higher is required. Found: $python_version"
    exit 1
fi

echo "✅ Python $python_version found"
echo "📦 Installing dependencies..."

# Upgrade pip and install requirements
python3 -m pip install --upgrade pip
pip install -r requirements.txt

echo "🎉 Production setup complete!"
echo "📋 Run 'make run' or 'python chat.py' to start the application"
