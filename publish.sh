#!/bin/bash

# PyPI Publishing Script for frp-tunnel
set -e

echo "🚀 Publishing frp-tunnel to PyPI..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Run from project root."
    exit 1
fi

# Install build dependencies
echo "📦 Installing build dependencies..."
pip install --upgrade build twine

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

# Build the package
echo "🔨 Building package..."
python -m build

# Check the built package
echo "🔍 Checking package..."
twine check dist/*

# Upload to PyPI
echo "📤 Uploading to PyPI..."
if [ "$1" = "--test" ]; then
    echo "📋 Uploading to TestPyPI..."
    twine upload --repository testpypi dist/*
    echo "✅ Uploaded to TestPyPI: https://test.pypi.org/project/frp-tunnel/"
    echo "🧪 Test install: pip install --index-url https://test.pypi.org/simple/ frp-tunnel"
else
    echo "📋 Uploading to PyPI..."
    twine upload dist/*
    echo "✅ Published to PyPI: https://pypi.org/project/frp-tunnel/"
    echo "📦 Install: pip install frp-tunnel"
fi

echo "🎉 Publishing complete!"
