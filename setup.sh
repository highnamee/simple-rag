#!/bin/bash

# Setup script for Simple RAG System

echo "🔧 Setting up Simple RAG System..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Install requirements
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Start LMStudio and load a model"
echo "2. Add your documents to the 'data' folder"
echo "3. Run: ./run.sh"
echo "   or: python chat.py"
