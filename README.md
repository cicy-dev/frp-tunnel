# 🚀 FRP SSH Tunnel - Easy Remote Access Solution

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-blue.svg)](https://github.com/your-username/frp-ssh-tunnel)
[![Shell Script](https://img.shields.io/badge/Shell-Bash%20%7C%20PowerShell-green.svg)](https://github.com/your-username/frp-ssh-tunnel)

> **One-click SSH tunnel setup for Google Colab, remote servers, and local development environments using FRP (Fast Reverse Proxy).**

## ✨ Features

- 🔐 **Secure SSH tunneling** with RSA key authentication
- 🌐 **Multi-platform support** (Linux, Windows, macOS, Google Colab)
- 🚀 **One-click deployment** with automated scripts
- 🔄 **Multi-client support** (up to 10 concurrent connections)
- 🛡️ **Token-based authentication** for enhanced security
- 📱 **Smart configuration management** with overwrite protection
- 🔧 **Auto-detection** of existing installations
- 📊 **Real-time status monitoring** and diagnostics

## 🎯 Use Cases

- **Machine Learning**: Access Google Colab via SSH for file transfers and remote debugging
- **Remote Development**: Connect local IDEs to cloud environments
- **Data Processing**: Secure transfer of large datasets
- **DevOps**: Remote server management and automation

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Local Client  │    │   GCP Server    │    │  Google Colab   │
│  (Any Platform) │    │   (frps:7000)   │    │  (frpc+SSH)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │ SSH -p 6001-6010     │                       │
         └──────────────────────┼───────────────────────┘
                                │
                         FRP Tunnel Forwarding
                      6001-6010 → Target:22
```

## 🚀 Quick Start

### Installation
```bash
pip install frp-tunnel
```

### Server Setup (GCP/VPS)
```bash
frp-tunnel setup
# Follow interactive wizard
```

### Google Colab (One-liner)
```python
# In Colab notebook cell
!pip install frp-tunnel && frp-tunnel colab --server YOUR_IP --token YOUR_TOKEN
```

### Local Client
```bash
frp-tunnel client --server YOUR_IP --token YOUR_TOKEN
```

### Connect via SSH
```bash
ssh -p 6001 colab@YOUR_SERVER_IP
```

## 📖 Detailed Documentation

### Prerequisites

- **Server**: Linux VPS/GCP instance with root access
- **Client**: Any system with SSH client
- **Network**: Open ports 6001-6010 and 7000 on server

### Port Configuration

| Port Range | Purpose | Description |
|------------|---------|-------------|
| 7000 | FRP Server | Main FRP service port |
| 6001-6010 | SSH Tunnels | Client SSH connections |

### Token Management

- Tokens are automatically generated and stored in `~/data/frp/frps.ini`
- Use `-r` flag to regenerate tokens
- Clients must use the same token as the server

## ⚙️ Configuration

### SSH Config Template

Add to `~/.ssh/config` for simplified connections:

```ssh-config
Host colab-6001
    HostName YOUR_SERVER_IP
    User colab
    Port 6001
    IdentityFile ~/.ssh/id_rsa

Host colab-6002
    HostName YOUR_SERVER_IP
    User colab
    Port 6002
    IdentityFile ~/.ssh/id_rsa
```

Then connect with: `ssh colab-6001`

### Firewall Setup (GCP)

```bash
# Create firewall rule
gcloud compute firewall-rules create frp-tunnel --allow tcp:6001-6010,tcp:7000
```

## 🔧 Advanced Usage

### Multiple Clients

```bash
# Client 1 (Colab)
bash frp-client-colab.sh colab 6001 SERVER_IP TOKEN

# Client 2 (Another Colab)
bash frp-client-colab.sh colab 6002 SERVER_IP TOKEN

# Client 3 (Custom user)
bash frp-client-colab.sh myuser 6003 SERVER_IP TOKEN
```

### Configuration Management

```bash
# Preserve existing config (default)
./frp-server-gcp.sh

# Force overwrite config
./frp-server-gcp.sh -r

# Check current configuration
cat ~/data/frp/frps.ini
```

## 🛠️ Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Connection refused | Check if FRP server is running: `ps aux \| grep frps` |
| Authentication failed | Verify token matches between server and client |
| Port already in use | Use different port or check existing connections |
| SSH key rejected | Ensure RSA key is properly configured |

### Diagnostic Commands

```bash
# Check FRP server status
ps aux | grep frps

# View server logs
cat ~/logs/frps.log

# View client logs  
cat ~/logs/frpc.log

# Test FRP server connectivity
telnet YOUR_SERVER_IP 7000

# Check SSH service
service ssh status

# Verify token
grep token ~/data/frp/frps.ini
```

### Log Locations

- Server logs: `~/logs/frps.log`
- Client logs: `~/logs/frpc.log`
- SSH logs: `/var/log/auth.log`

## 📁 Project Structure

```
frp-ssh-tunnel/
├── 📄 README.md                 # This file
├── 📄 LICENSE                   # MIT License
├── 📁 scripts/
│   ├── 🔧 frp-server-gcp.sh     # Server setup script
│   ├── 🔧 frp-client-colab.sh   # Colab client script
│   ├── 🔧 frp-client-windows.ps1 # Windows client script
│   └── 🔧 frp-client-linux.sh   # Linux/macOS client script
├── 📁 config/
│   ├── ⚙️ frps.ini              # Server config template
│   ├── ⚙️ frpc.ini              # Client config template
│   └── ⚙️ ssh-config-template   # SSH config template
├── 📁 docs/
│   ├── 📖 INSTALLATION.md       # Detailed installation guide
│   ├── 📖 CONFIGURATION.md      # Configuration reference
│   └── 📖 TROUBLESHOOTING.md    # Troubleshooting guide
└── 📁 examples/
    ├── 💡 colab-example.ipynb   # Jupyter notebook example
    └── 💡 automation-example.sh # Automation script example
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FRP Project](https://github.com/fatedier/frp) - The underlying reverse proxy tool
- Google Colab team for providing the cloud environment
- Community contributors and testers

## 📊 Stats

![GitHub stars](https://img.shields.io/github/stars/your-username/frp-ssh-tunnel?style=social)
![GitHub forks](https://img.shields.io/github/forks/your-username/frp-ssh-tunnel?style=social)
![GitHub issues](https://img.shields.io/github/issues/your-username/frp-ssh-tunnel)
![GitHub pull requests](https://img.shields.io/github/issues-pr/your-username/frp-ssh-tunnel)

---

⭐ **Star this repository if it helped you!**

📧 **Questions?** Open an [issue](https://github.com/your-username/frp-ssh-tunnel/issues) or start a [discussion](https://github.com/your-username/frp-ssh-tunnel/discussions)
