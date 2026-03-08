# Publishing

## PyPI

```bash
pip install build twine
python -m build
twine upload dist/*
```

## Version Bump

Update version in:
- `pyproject.toml` → `version`
- `setup.cfg` → `version`
- `frp_tunnel/__init__.py` → `__version__`
- `frp_tunnel/_version.py` → `version`

Then update `CHANGELOG.md`.
