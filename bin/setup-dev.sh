#!/bin/bash

# Simple RAG - Development Setup Script

set -e

echo "🚀 Setting up Simple RAG development environment..."

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

# Create and setup virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "🔌 Activating virtual environment..."
    source venv/bin/activate

    echo "⬆️  Upgrading pip..."
    pip install --upgrade pip

    echo "📚 Installing production dependencies..."
    pip install -r requirements.txt

    echo "🛠️  Installing development dependencies..."
    pip install -r requirements-dev.txt

    echo "🪝 Setting up pre-commit hooks..."
    pre-commit install

    echo "🎨 Running initial code formatting..."
    if [ -f "chat.py" ]; then
        black chat.py 2>/dev/null || echo "  ⚠️  Black formatting issues found in chat.py"
        isort chat.py 2>/dev/null || echo "  ⚠️  Import sorting issues found in chat.py"
    fi

    if [ -d "src" ]; then
        black src/ 2>/dev/null || echo "  ⚠️  Black formatting issues found in src/"
        isort src/ 2>/dev/null || echo "  ⚠️  Import sorting issues found in src/"
    fi
else
    echo "📦 Virtual environment already exists"
    source venv/bin/activate

    echo "⬆️  Upgrading pip..."
    pip install --upgrade pip

    echo "📚 Installing/updating dependencies..."
    pip install -r requirements.txt
    pip install -r requirements-dev.txt

    echo "🪝 Setting up pre-commit hooks..."
    pre-commit install
fi

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "📋 Available commands:"
echo "  make help          - Show all available commands"
echo "  make format        - Format code with black and isort"
echo "  make lint          - Run flake8 linter"
echo "  make type-check    - Run mypy type checker"
echo "  make all-checks    - Run all quality checks"
echo "  make pre-commit    - Run pre-commit hooks on all files"
echo "  make run           - Start the chat application"
echo ""
echo "🔧 To activate the virtual environment manually:"
echo "  source venv/bin/activate"
