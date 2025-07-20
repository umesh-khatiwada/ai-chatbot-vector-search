#!/bin/bash

# AI Chatbot Vector Search - Setup Script
# This script sets up the complete development environment

set -e  # Exit on any error

echo "🚀 AI Chatbot Vector Search - Setup Script"
echo "=============================================="

# Check if Python 3.8+ is available
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "🐍 Python version: $python_version"

# Check minimum version
if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
    echo "✅ Python version is compatible"
else
    echo "❌ Python 3.8+ required. Please upgrade Python."
    exit 1
fi

# Setup training environment
echo ""
echo "📦 Setting up training environment..."
cd training

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Setup environment file
if [ ! -f ".env" ]; then
    echo "Creating environment configuration..."
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo "⚠️  Please edit .env with your API keys and configuration"
else
    echo "✅ Environment file already exists"
fi

# Return to root directory
cd ..

# Setup chatbot environment
echo ""
echo "🤖 Setting up chatbot environment..."
cd chatbot

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Return to root directory
cd ..

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Edit training/.env with your API keys:"
echo "   - GEMINI_API_KEY (required)"
echo "   - QDRANT_URL (default: http://localhost:6333)"
echo "   - RABBITMQ_URL (optional, for queue-based training)"
echo ""
echo "2. Start Qdrant database:"
echo "   docker run -p 6333:6333 qdrant/qdrant"
echo ""
echo "3. Validate your setup:"
echo "   cd training && source venv/bin/activate"
echo "   python3 validate_system.py"
echo ""
echo "4. Start training:"
echo "   python3 training-job-gemini.py"
echo ""
echo "5. Start chatbot:"
echo "   cd ../chatbot && source venv/bin/activate"
echo "   python3 chat.py"
echo ""
echo "📚 Documentation:"
echo "   - Main README: ./README.md"
echo "   - Training docs: ./training/README.md"
echo "   - API reference: ./docs/API.md"
echo "   - Contributing: ./CONTRIBUTING.md"
echo ""
echo "🆘 Need help? Check the documentation or open an issue on GitHub"
