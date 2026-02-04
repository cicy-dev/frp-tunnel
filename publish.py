#!/usr/bin/env python3
"""
PyPI Publishing Script
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Run command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        sys.exit(1)

def main():
    """Main publishing function"""
    print("🚀 Publishing frp-tunnel to PyPI...")
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found. Run from project root.")
        sys.exit(1)
    
    # Check for test flag
    test_mode = "--test" in sys.argv
    
    # Install build dependencies
    run_command("pip install --upgrade build twine", "Installing build dependencies")
    
    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    for path in ["dist", "build"]:
        if Path(path).exists():
            shutil.rmtree(path)
    
    for egg_info in Path(".").glob("*.egg-info"):
        shutil.rmtree(egg_info)
    
    # Build the package
    run_command("python -m build", "Building package")
    
    # Check the built package
    run_command("twine check dist/*", "Checking package")
    
    # Upload to PyPI
    if test_mode:
        print("📋 Uploading to TestPyPI...")
        run_command("twine upload --repository testpypi dist/*", "Uploading to TestPyPI")
        print("✅ Uploaded to TestPyPI: https://test.pypi.org/project/frp-tunnel/")
        print("🧪 Test install: pip install --index-url https://test.pypi.org/simple/ frp-tunnel")
    else:
        print("📋 Uploading to PyPI...")
        run_command("twine upload dist/*", "Uploading to PyPI")
        print("✅ Published to PyPI: https://pypi.org/project/frp-tunnel/")
        print("📦 Install: pip install frp-tunnel")
    
    print("🎉 Publishing complete!")

if __name__ == "__main__":
    main()
