@echo off
REM PyPI Publishing Script for Windows
echo 🚀 Publishing frp-tunnel to PyPI...

REM Check if we're in the right directory
if not exist "pyproject.toml" (
    echo ❌ Error: pyproject.toml not found. Run from project root.
    exit /b 1
)

REM Install build dependencies
echo 📦 Installing build dependencies...
pip install --upgrade build twine

REM Clean previous builds
echo 🧹 Cleaning previous builds...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
for /d %%i in (*.egg-info) do rmdir /s /q "%%i"

REM Build the package
echo 🔨 Building package...
python -m build

REM Check the built package
echo 🔍 Checking package...
twine check dist/*

REM Upload to PyPI
echo 📤 Uploading to PyPI...
if "%1"=="--test" (
    echo 📋 Uploading to TestPyPI...
    twine upload --repository testpypi dist/*
    echo ✅ Uploaded to TestPyPI: https://test.pypi.org/project/frp-tunnel/
    echo 🧪 Test install: pip install --index-url https://test.pypi.org/simple/ frp-tunnel
) else (
    echo 📋 Uploading to PyPI...
    twine upload dist/*
    echo ✅ Published to PyPI: https://pypi.org/project/frp-tunnel/
    echo 📦 Install: pip install frp-tunnel
)

echo 🎉 Publishing complete!
