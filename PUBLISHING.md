# PyPI Publishing Guide

## Prerequisites

1. **PyPI Account**: Create accounts on [PyPI](https://pypi.org) and [TestPyPI](https://test.pypi.org)
2. **API Tokens**: Generate API tokens for authentication
3. **Configure credentials**:

```bash
# Create ~/.pypirc file
cat > ~/.pypirc << EOF
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
EOF
```

## Publishing Commands

### Test Publishing (Recommended First)
```bash
# Using bash script
./publish.sh --test

# Using Python script
python publish.py --test

# Using Windows batch
publish.bat --test
```

### Production Publishing
```bash
# Using bash script
./publish.sh

# Using Python script
python publish.py

# Using Windows batch
publish.bat
```

## Manual Steps

```bash
# 1. Install dependencies
pip install --upgrade build twine

# 2. Clean previous builds
rm -rf dist/ build/ *.egg-info/

# 3. Build package
python -m build

# 4. Check package
twine check dist/*

# 5. Upload to TestPyPI (test first)
twine upload --repository testpypi dist/*

# 6. Test installation
pip install --index-url https://test.pypi.org/simple/ frp-tunnel

# 7. Upload to PyPI (production)
twine upload dist/*
```

## Version Management

Update version in `pyproject.toml`:
```toml
[project]
name = "frp-tunnel"
version = "1.0.1"  # Increment this
```

## Verification

After publishing, verify:
- Package appears on PyPI: https://pypi.org/project/frp-tunnel/
- Installation works: `pip install frp-tunnel`
- CLI works: `frp-tunnel --help`
