# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability, please follow these steps:

### 1. Do Not Create Public Issues

Please **do not** create GitHub issues for security vulnerabilities. This could put users at risk.

### 2. Report Privately

Send an email to: **security@your-domain.com** (replace with actual email)

Include the following information:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### 3. Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Varies based on severity

### 4. Disclosure Policy

- We will acknowledge receipt of your report
- We will investigate and validate the vulnerability
- We will develop and test a fix
- We will release the fix and publicly disclose the vulnerability

## Security Best Practices

### For Users

1. **Keep tokens secure**: Never share your FRP tokens publicly
2. **Use strong SSH keys**: Generate RSA keys with at least 2048 bits
3. **Limit access**: Only open necessary ports in your firewall
4. **Monitor logs**: Regularly check FRP and SSH logs for suspicious activity
5. **Update regularly**: Keep FRP and system packages updated

### For Developers

1. **Input validation**: Always validate user inputs
2. **Secure defaults**: Use secure configuration defaults
3. **Least privilege**: Run services with minimal required permissions
4. **Audit dependencies**: Regularly check for vulnerable dependencies

## Known Security Considerations

### FRP Token Security

- Tokens are transmitted in plaintext over the initial connection
- Use HTTPS/TLS when possible for token transmission
- Rotate tokens regularly

### SSH Key Management

- Private keys should never be shared
- Use strong passphrases for SSH keys
- Consider using SSH certificates for large deployments

### Network Security

- FRP traffic is not encrypted by default
- Consider using VPN or additional encryption layers
- Implement proper firewall rules

## Vulnerability Disclosure History

No vulnerabilities have been reported yet.

## Contact

For security-related questions or concerns:
- Email: security@your-domain.com
- PGP Key: [Link to PGP key if available]

---

**Note**: This security policy is subject to change. Please check back regularly for updates.
