# GitHub Secrets Configuration

## Required Secrets for PyPI Publishing

Add these secrets in your GitHub repository settings:
**Settings → Secrets and variables → Actions → New repository secret**

### 1. PYPI_API_TOKEN
- **Name**: `PYPI_API_TOKEN`
- **Value**: Your PyPI API token
- **How to get**:
  1. Go to https://pypi.org/manage/account/
  2. Click "Add API token"
  3. Name: `frp-tunnel-github-action`
  4. Scope: `Entire account` or `Project: frp-tunnel`
  5. Copy the token (starts with `pypi-`)

### 2. TEST_PYPI_API_TOKEN
- **Name**: `TEST_PYPI_API_TOKEN`
- **Value**: Your TestPyPI API token
- **How to get**:
  1. Go to https://test.pypi.org/manage/account/
  2. Click "Add API token"
  3. Name: `frp-tunnel-test`
  4. Scope: `Entire account`
  5. Copy the token (starts with `pypi-`)

## How to Use the Action

### Automatic Publishing (on Release)
1. Create a new release on GitHub
2. Action will automatically publish to PyPI

### Manual Publishing
1. Go to **Actions** tab in your repo
2. Click **Publish to PyPI** workflow
3. Click **Run workflow**
4. Choose:
   - ✅ **TestPyPI**: Check the box (recommended for testing)
   - ✅ **PyPI**: Leave unchecked (production)

## Security Notes

- ✅ Tokens are encrypted and only accessible to workflows
- ✅ Use project-scoped tokens when possible
- ✅ Rotate tokens periodically
- ✅ Never commit tokens to code

## Token Format Examples

```
# PyPI Token (production)
pypi-AgEIcHlwaS5vcmcCJGE4ZjY3YjE4LWE5...

# TestPyPI Token (testing)  
pypi-AgEIcHlwaS5vcmcCJGE4ZjY3YjE4LWE5...
```

## Verification

After setup, test with:
1. Manual workflow run to TestPyPI
2. Check package appears at: https://test.pypi.org/project/frp-tunnel/
3. Test install: `pip install --index-url https://test.pypi.org/simple/ frp-tunnel`
