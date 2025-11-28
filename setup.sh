#!/bin/bash
# Quick setup script for LLM Quiz Solver (macOS compatible)

echo "🚀 Setting up LLM Quiz Solver..."

# Check Python version (use python3 on macOS)
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

python_version=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version detected"

# Create virtual environment
echo "Creating virtual environment..."
$PYTHON_CMD -m venv .venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

echo "✓ Virtual environment activated"

# Upgrade pip first
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "Installing dependencies..."
pip install -e . --quiet

echo "✓ Dependencies installed"

# Install Playwright
echo "Installing Playwright browsers..."
playwright install chromium

echo "✓ Playwright installed"

# Setup .env file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Please edit .env file with your credentials"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your EMAIL, SECRET, and GOOGLE_API_KEY"
echo "2. Activate venv: source .venv/bin/activate"
echo "3. Run: python main.py"
echo "4. Test with demo URL (see QUICKSTART.md)"
