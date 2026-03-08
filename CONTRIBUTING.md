# Contributing

## Setup

```bash
git clone https://github.com/cicy-dev/frp-tunnel.git
cd frp-tunnel
pip install -e .
```

## Project Structure

```
frp_tunnel/
├── cli.py              # All CLI commands
├── __init__.py         # Package version
├── _version.py         # Version file
└── core/               # Core modules (installer, config, platform, tunnel)

bin/                    # Bundled FRP binaries per platform
config/                 # Config templates
scripts/                # Deployment scripts
docs/                   # Documentation
```

## Development

```bash
# Run locally
ft -h
ft server status

# Test syntax
python -c "import ast; ast.parse(open('frp_tunnel/cli.py').read())"

# Install in dev mode
pip install -e .
```

## Adding a New Platform Binary

1. Download from https://github.com/fatedier/frp/releases
2. Place `frps` and `frpc` in `bin/{os}_{arch}/`
3. Directory naming: `linux_arm64`, `darwin_amd64`, `windows_amd64`, etc.

## Pull Requests

- Keep changes minimal
- Test on your platform before submitting
- Update CHANGELOG.md
