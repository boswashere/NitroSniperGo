#!/bin/bash
# Quick start script for NitroSniper

set -e

echo "=========================================="
echo "NitroSniper 2026 - Quick Start"
echo "=========================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment if needed
if [ ! -d "venv" ]; then
    echo "▶ Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "▶ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "▶ Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Check settings.json
if [ ! -f "settings.json" ]; then
    echo "⚠ settings.json not found. Creating..."
    # Copy from template if exists
    if [ -f "settings.json.template" ]; then
        cp settings.json.template settings.json
    fi
    echo "⚠ Please edit settings.json with your tokens!"
fi

echo ""
echo "=========================================="
echo "✓ Setup complete! Ready to run."
echo "=========================================="
echo ""
echo "To start the bot:"
echo "  python main.py"
echo ""
