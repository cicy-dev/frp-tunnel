# Changelog

## [1.2.0] - 2026-03-08

### Changed
- **CLI restructured**: `ft server <cmd>` / `ft client <cmd>` subcommand groups
- **Binaries bundled** in `bin/` directory (linux_arm64, darwin_amd64, windows_amd64)
- Auto-download from GitHub releases if binary not found for current platform
- `ft server reload` now restarts server (frps has no hot-reload)
- `ft client reload` uses frpc native hot-reload
- `ft frps` / `ft frpc` passthrough to native binary via `execvp`
- Removed `client-add-port` / `client-remove-port` (edit config directly)
- Removed `service` command (merged into `ft server install`)
- Removed `version` subcommand (use `ft --version`)
- Added `-h` short help flag
- Version now read from `__version__` instead of hardcoded

### Fixed
- RDP port detection bug (`"04" in str(p)` false positives)
- Version inconsistency across files (unified to single source)
- pip install compatibility with old pip/setuptools (added setup.cfg)

## [1.1.6] - 2026-02-24

### Changed
- YAML config format (INI deprecated in FRP 0.52+)
- Multi-port support via CLI
- Hot reload support with webServer config
- Dashboard API integration for status display

## [1.0.0] - 2026-02-04

### Added
- Initial release
- FRP server/client setup scripts
- Token-based authentication
- Multi-platform support (Linux, Windows, macOS, Google Colab)
- Systemd service integration
- GitHub Actions CI/CD

[1.2.0]: https://github.com/cicy-dev/frp-tunnel/compare/v1.1.6...v1.2.0
[1.1.6]: https://github.com/cicy-dev/frp-tunnel/compare/v1.0.0...v1.1.6
[1.0.0]: https://github.com/cicy-dev/frp-tunnel/releases/tag/v1.0.0
