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
frp-tunnel server

# Output:
# 🚀 Starting server...
# 🔑 Generated token: frp_abc123...
# ✅ Server started
```

### Connect Client
```bash
# Connect to server
frp-tunnel client --server YOUR_SERVER_IP --token YOUR_TOKEN --port 6000

# Then SSH normally
ssh -p 6000 user@YOUR_SERVER_IP
```

## 🎮 Commands

```bash
# Server
frp-tunnel server              # Start server (auto-gen token)
frp-tunnel server -f           # Force restart
frp-tunnel server -r           # Restart
frp-tunnel server-status       # Show server status

# Client
frp-tunnel client --server IP --token TOKEN --port 6000
frp-tunnel client-status       # Show client status

# Utilities
frp-tunnel token               # Generate new token
frp-tunnel version             # Show version
frp-tunnel stop                # Stop all
```

## 📊 Status Display

```bash
$ frp-tunnel server-status

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

### Server Config (`~/data/frp/frps.ini`)
```ini
[common]
bind_port = 7000
token = frp_your_token_here
dashboard_port = 7500
dashboard_user = admin
dashboard_pwd = admin
```

### Client Config (`~/data/frp/frpc.ini`)
```ini
[common]
server_addr = YOUR_SERVER_IP
server_port = 7000
token = frp_your_token_here

[ssh_6000]
type = tcp
local_ip = 127.0.0.1
local_port = 22
remote_port = 6000
```

Add more ports by editing the config file manually.

## 🌟 Features

- ✅ **Auto-download** FRP binaries (no manual installation)
- ✅ **Auto-generate** token and config
- ✅ **Background mode** - runs as daemon
- ✅ **Multi-platform** - Windows, Linux, macOS
- ✅ **Dashboard** - Web UI at port 7500
- ✅ **API support** - Query client status via REST API

## 🛠️ Advanced Usage

### Multiple Ports
Edit `~/data/frp/frpc.ini` to add more ports:
```ini
[ssh_6001]
type = tcp
local_ip = 127.0.0.1
local_port = 22
remote_port = 6001
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

Special thanks to the [FRP project](https://github.com/fatedier/frp) for creating the excellent reverse proxy tool.

---

⭐ **Star this repo if it saved you time!**
