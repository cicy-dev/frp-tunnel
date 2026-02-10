# 🚀 FRP Tunnel - SSH Access Made Easy

**[中文文档](README_CN.md) | [English](README.md)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-blue.svg)](https://github.com/cicy-dev/frp-tunnel)

> **Connect to Google Colab or any remote server via SSH in 30 seconds. No complex setup needed!**

## 🎯 What This Does

- **Problem**: Can't SSH into Google Colab or access remote servers behind firewalls
- **Solution**: Creates a secure tunnel so you can SSH from anywhere
- **Result**: Use your favorite tools (VS Code, file transfer, etc.) with remote servers

## ⚡ Quick Start

### Install
```bash
pip install frp-tunnel
```

### Start Server (One-time setup)
```bash
# Auto-generates token and config
ft server

# Output:
# 🚀 Starting server...
# 🔑 Generated token: frp_abc123...
# ✅ Server started
```

### Connect Client
```bash
# First time - specify server and token
ft client --server YOUR_SERVER_IP --token YOUR_TOKEN --port 6003

# Multiple ports (SSH + RDP)
ft client --server YOUR_SERVER_IP --token YOUR_TOKEN --port 6003 --port 6004

# Add more ports later (reuses existing config)
ft client-add-port 6005 6006

# Remove ports
ft client-remove-port 6005

# Then SSH normally
ssh -p 6003 user@YOUR_SERVER_IP
```

## 🎮 Commands

```bash
# Server
ft server              # Start server (auto-gen token)
ft server -f           # Force restart
ft server -r           # Restart
ft server-status       # Show server status

# Client
ft client --server IP --token TOKEN --port 6003 --port 6004
ft client-add-port 6005 6006    # Add ports to existing config
ft client-remove-port 6005      # Remove ports
ft client-status                # Show client status

# Forward to frpc/frps
ft frpc -c ~/data/frp/frpc.yaml           # Start client
ft frpc reload -c ~/data/frp/frpc.yaml    # Hot reload
ft frps -c ~/data/frp/frps.yaml           # Start server

# Utilities
ft token               # Generate new token
ft version             # Show version
ft stop                # Stop all
```

## 📊 Status Display

```bash
$ ft server-status

📊 Server Status
🖥️  Server: Running
   🌐 Public IP: 34.102.78.219
   📄 Config: ~/data/frp/frps.ini
   📋 Log: ~/data/frp/frps.log
   🔧 Binary: ~/.frp-tunnel/bin/frps
   👥 Active clients: 1
      • ssh_6000: port 6000 (v0.52.3, 0 conns)
```

## 🔧 Configuration

### Server Config (`~/data/frp/frps.yaml`)
```yaml
bindPort: 7000
auth:
  token: frp_your_token_here
webServer:
  addr: 0.0.0.0
  port: 7500
  user: admin
  password: admin
log:
  to: ~/data/frp/frps.log
  level: info
```

### Client Config (`~/data/frp/frpc.yaml`)
```yaml
serverAddr: YOUR_SERVER_IP
serverPort: 7000
auth:
  token: frp_your_token_here
log:
  to: ~/data/frp/frpc.log
  level: info
webServer:
  addr: 127.0.0.1
  port: 7400
proxies:
  - name: ssh_6003
    type: tcp
    localIP: 127.0.0.1
    localPort: 22
    remotePort: 6003
  - name: rdp_6004
    type: tcp
    localIP: 127.0.0.1
    localPort: 3389
    remotePort: 6004
```

**Note**: Both server and client use YAML format (INI is deprecated in FRP 0.52+). The `webServer` section enables hot reload and dashboard access.

Use `ft client-add-port` and `ft client-remove-port` commands to manage ports easily.

## 🌟 Features

- ✅ **Auto-download** FRP binaries (no manual installation)
- ✅ **Auto-generate** token and config
- ✅ **YAML config** - Modern format with hot reload support
- ✅ **Multiple ports** - SSH, RDP, or any service
- ✅ **Easy port management** - add/remove ports without editing config
- ✅ **Hot reload** - Update config without disconnecting SSH
- ✅ **Background mode** - runs as daemon
- ✅ **Multi-platform** - Windows, Linux, macOS
- ✅ **Dashboard** - Web UI at port 7500
- ✅ **API support** - Query client status via REST API
- ✅ **Systemd integration** - Auto-start on Linux boot
- ✅ **Health monitoring** - Windows client with auto-monitoring (5.5h runtime limit)

## 🛠️ Advanced Usage

### Systemd Service (Linux Server)
```bash
# Enable auto-start on boot
sudo systemctl enable frps.service
sudo systemctl start frps.service
sudo systemctl status frps.service
```

The service file is automatically created at `/etc/systemd/system/frps.service` and will restart the server automatically if it crashes.

### Windows Client Monitoring
The Windows boot script includes automatic monitoring:
- Creates `C:\running.txt` as a health check file
- Monitors FRP client status every 50 seconds
- Auto-stops after 5.5 hours runtime
- Deleting `C:\running.txt` will stop the monitoring loop

### Hot Reload (No SSH Disconnection)
```bash
# Start client with webServer enabled (auto-configured)
ft frpc -c ~/data/frp/frpc.yaml &

# Add/remove ports
ft client-add-port 6005 6006
ft client-remove-port 6004

# Hot reload - no SSH disconnection!
ft frpc reload -c ~/data/frp/frpc.yaml
```

### Multiple Ports
Use commands to manage ports easily:
```bash
# Add multiple ports at once
ft client-add-port 6005 6006 6007

# Remove specific ports
ft client-remove-port 6005

# Or edit config manually: ~/data/frp/frpc.yaml
```

### Dashboard Access
Visit `http://YOUR_SERVER_IP:7500` (admin/admin)

### API Access
```bash
curl -u admin:admin http://localhost:7500/api/proxy/tcp
```

## 📋 Requirements

- **Server**: Any Linux VPS (Google Cloud, AWS, DigitalOcean, etc.)
- **Ports**: Open ports 6000-6010 and 7000, 7500 on your server
- **Client**: Any computer with SSH

## 🙏 Acknowledgments

Special thanks to the [FRP project](https://github.com/fatedier/frp) authors for creating the excellent reverse proxy tool that makes this package possible.

---

⭐ **Star this repo if it saved you time!**
