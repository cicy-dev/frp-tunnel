# GitHub Secrets Configuration

## Trusted Publishing Setup (Recommended)

**No secrets needed!** Use PyPI's Trusted Publishing for secure, token-free publishing.

### Setup Steps:
1. **First, create the package on PyPI manually:**
   ```bash
   pip install build twine
   python -m build
   twine upload dist/*
   ```

2. **Then configure Trusted Publisher:**
   - Go to: https://pypi.org/manage/project/frp-tunnel/settings/publishing/
   - Click "Add a new pending publisher"
   - Fill in:
     - **PyPI Project Name**: `frp-tunnel`
     - **Owner**: `cicy-dev`
     - **Repository name**: `frp-tunnel`
     - **Workflow filename**: `publish.yml`
     - **Environment name**: (leave empty)

3. **Future releases will publish automatically** when you push tags!

---

## Alternative: API Token Method (Legacy)

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

### Automatic Publishing (on Tag Push)
1. Push a version tag: `git tag v1.0.2 && git push --tags`
2. Action will automatically publish to PyPI

### Manual Publishing
1. Go to **Actions** tab in your repo
2. Click **Publish to PyPI** workflow
3. Click **Run workflow**
4. Choose:
   - ✅ **TestPyPI**: Check the box (recommended for testing)
   - ✅ **PyPI**: Leave unchecked (production)

## Security Notes

- ✅ **Trusted Publishing** is more secure than API tokens
- ✅ No secrets needed in repository
- ✅ Direct GitHub → PyPI authentication
- ✅ Automatic token rotation

## Verification

After setup, test with:
1. Push a new tag to trigger automatic publishing
2. Check package appears at: https://pypi.org/project/frp-tunnel/
3. Test install: `pip install frp-tunnel`
