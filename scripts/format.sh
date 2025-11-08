#!/bin/bash
# Format and check script
# Usage:
#   ./scripts/format.sh          - Format code (default)
#   ./scripts/format.sh --check  - Check formatting without modifying files (CI mode)

set -e

# Parse arguments
CHECK_ONLY=false
if [[ "$1" == "--check" ]]; then
    CHECK_ONLY=true
fi

if [[ "$CHECK_ONLY" == true ]]; then
    echo "🔍 Checking code formatting..."
else
    echo "🔧 Installing/updating formatting tools..."
    poetry install --no-interaction
fi

echo ""
if [[ "$CHECK_ONLY" == true ]]; then
    echo "🎨 Checking black formatting..."
    poetry run black --check .
else
    echo "🎨 Running black formatter..."
    poetry run black .
fi

echo ""
if [[ "$CHECK_ONLY" == true ]]; then
    echo "📦 Checking import sorting with isort..."
    poetry run isort --check-only .
else
    echo "📦 Running isort to sort imports..."
    poetry run isort .
fi

echo ""
echo "✅ Running flake8 to check for issues..."
poetry run flake8 .

echo ""
if [[ "$CHECK_ONLY" == true ]]; then
    echo "✨ All formatting checks passed!"
else
    echo "✨ Formatting complete! Your code is ready to commit."
fi
