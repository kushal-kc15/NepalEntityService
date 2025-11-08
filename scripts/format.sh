#!/bin/bash
# Format script for developers
# Run this before committing to ensure code passes CI checks

set -e

echo "🔧 Installing/updating formatting tools..."
poetry install --no-interaction

echo ""
echo "🎨 Running black formatter..."
poetry run black .

echo ""
echo "📦 Running isort to sort imports..."
poetry run isort .

echo ""
echo "✅ Running flake8 to check for issues..."
poetry run flake8 .

echo ""
echo "✨ Formatting complete! Your code is ready to commit."
