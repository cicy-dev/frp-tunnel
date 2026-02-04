#!/bin/bash

# Project Structure Generator
# Creates a clean, GitHub-ready project structure

echo "🚀 Generating GitHub-ready project structure..."

# Remove checkpoint files
find . -name "*checkpoint*" -type f -delete
find . -name ".ipynb_checkpoints" -type d -exec rm -rf {} + 2>/dev/null || true

echo "✅ Cleaned up checkpoint files"

# Create final project tree
echo "📁 Final Project Structure:"
echo "=========================="

tree -a -I '.git' . || find . -type f -name ".*" -prune -o -type f -print | sort

echo "=========================="
echo "📊 Project Statistics:"
echo "=========================="

# Count files by type
echo "📄 Documentation files: $(find . -name "*.md" | wc -l)"
echo "🔧 Shell scripts: $(find . -name "*.sh" | wc -l)"
echo "💻 PowerShell scripts: $(find . -name "*.ps1" | wc -l)"
echo "⚙️ Configuration files: $(find . -name "*.ini" | wc -l)"
echo "📓 Jupyter notebooks: $(find . -name "*.ipynb" | wc -l)"
echo "🏗️ GitHub templates: $(find .github -name "*.yml" | wc -l)"

echo "=========================="
echo "✅ Project is ready for GitHub!"
echo "=========================="

echo "📋 Next steps:"
echo "1. Initialize git repository: git init"
echo "2. Add files: git add ."
echo "3. Commit: git commit -m 'Initial commit: Complete FRP SSH tunnel solution'"
echo "4. Create GitHub repository"
echo "5. Push to GitHub: git remote add origin <url> && git push -u origin main"
echo "6. Add topics/tags: frp, ssh, tunnel, colab, automation, devops"
echo "7. Enable GitHub Pages for documentation"
echo "8. Set up branch protection rules"
