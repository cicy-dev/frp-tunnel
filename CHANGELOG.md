# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure
- Comprehensive documentation
- Multi-platform support
- GitHub Actions CI/CD pipeline

## [1.0.0] - 2026-02-04

### Added
- FRP server setup script for GCP/VPS
- FRP client scripts for multiple platforms:
  - Google Colab
  - Linux/macOS
  - Windows PowerShell
- Automated SSH tunnel configuration
- Token-based authentication system
- Multi-client support (ports 6001-6010)
- Smart configuration management
- Real-time monitoring and diagnostics
- Comprehensive documentation:
  - Installation guide
  - Configuration reference
  - Troubleshooting guide
- Example implementations:
  - Jupyter notebook for Colab
  - Automation script for batch operations
- Security features:
  - RSA key authentication
  - Token validation
  - Firewall configuration
- Project templates:
  - GitHub issue templates
  - Pull request template
  - Contributing guidelines
  - Security policy

### Features
- **One-click deployment**: Single command setup for all platforms
- **Cross-platform compatibility**: Works on Linux, Windows, macOS, and Google Colab
- **Secure by default**: Implements RSA key authentication and token validation
- **Scalable architecture**: Supports up to 10 concurrent client connections
- **Smart configuration**: Preserves existing configs, optional force overwrite
- **Comprehensive logging**: Detailed logs for debugging and monitoring
- **Auto-recovery**: Built-in health checks and restart mechanisms

### Documentation
- Complete README with quick start guide
- Detailed installation instructions
- Configuration reference with examples
- Troubleshooting guide with common solutions
- Contributing guidelines for developers
- Security policy and best practices
- Example implementations and automation scripts

### Infrastructure
- GitHub Actions CI/CD pipeline
- Automated testing for shell scripts and PowerShell
- Security scanning for hardcoded secrets
- Documentation linting and link checking
- Issue and PR templates for better collaboration

[Unreleased]: https://github.com/your-username/frp-ssh-tunnel/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/your-username/frp-ssh-tunnel/releases/tag/v1.0.0
