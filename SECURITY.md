# Security

## Authentication

FRP Tunnel uses token-based authentication. Tokens are generated with `ft token` using `secrets.token_hex(16)`.

## Best Practices

- Change the default dashboard password (`admin/admin`) in `frps.yaml`
- Restrict firewall rules to specific IP ranges when possible
- Use SSH key authentication instead of passwords
- Keep FRP binaries updated

## Reporting Vulnerabilities

Please report security issues via [GitHub Issues](https://github.com/cicy-dev/frp-tunnel/issues) with the "security" label.
