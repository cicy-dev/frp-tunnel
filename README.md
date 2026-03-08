# 🚀 FRP Tunnel

**[中文文档](README_CN.md) | [English](README.md)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-blue.svg)](https://github.com/cicy-dev/frp-tunnel)

> Simple CLI wrapper for [FRP](https://github.com/fatedier/frp) — manage SSH tunnels with ease.

## Install

```bash
pip install frp-tunnel
```

## Quick Start

### Server

```bash
ft server init          # Generate config + auto-download binary
ft server start         # Start server
ft server status        # Check status
```

### Client

```bash
ft client init --server 1.2.3.4 --token YOUR_TOKEN --port 6022
ft client start         # Start client
ssh -p 6022 user@1.2.3.4
```

## Commands

```
ft server init          Generate ~/data/frp/frps.yaml (auto-download binary)
ft server start         Start frps
ft server stop          Stop frps
ft server reload        Restart frps (apply config changes)
ft server status        Show server status + active clients
ft server install       Install as system service (systemd/launchd/startup)

ft client init          Generate ~/data/frp/frpc.yaml (auto-download binary)
ft client start         Start frpc
ft client stop          Stop frpc
ft client reload        Hot-reload frpc config (no disconnect)
ft client status        Show client status

ft frps <args>          Run frps directly (passthrough)
ft frpc <args>          Run frpc directly (passthrough)
ft token                Generate auth token
ft stop                 Stop all FRP processes
ft --version            Show version
ft -h                   Help
```

## Configuration

### Server (`~/data/frp/frps.yaml`)

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

### Client (`~/data/frp/frpc.yaml`)

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
  - name: ssh_6022
    type: tcp
    localIP: 127.0.0.1
    localPort: 22
    remotePort: 6022
```

Edit the config file directly to add/remove proxies, then `ft client reload`.

## Binaries

FRP binaries are bundled in `bin/` for default platforms:

| Directory | Platform |
|-----------|----------|
| `bin/linux_arm64/` | Linux ARM64 |
| `bin/darwin_amd64/` | macOS x86_64 |
| `bin/windows_amd64/` | Windows x86_64 |

If binaries are not found for your platform, `ft server init` / `ft client init` will auto-download from [FRP releases](https://github.com/fatedier/frp/releases).

## Dashboard

Visit `http://YOUR_SERVER_IP:7500` (admin/admin) to see connected clients.

API: `curl -u admin:admin http://localhost:7500/api/proxy/tcp`

## Requirements

- Python >= 3.7
- Server: Any VPS with ports 7000, 7500, and your tunnel ports open

## Acknowledgments

Built on [FRP](https://github.com/fatedier/frp) by fatedier.
