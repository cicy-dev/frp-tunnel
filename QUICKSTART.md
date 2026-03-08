# Quick Start

## Install

```bash
pip install frp-tunnel
```

## Server

```bash
ft server init          # Generate config + download binary
ft server start         # Start
ft server status        # Check
```

## Client

```bash
ft client init --server YOUR_IP --token YOUR_TOKEN --port 6022
ft client start
ssh -p 6022 user@YOUR_IP
```

## Manage

```bash
# Edit config directly
vim ~/data/frp/frpc.yaml

# Hot-reload (no disconnect)
ft client reload

# Restart server (apply changes)
ft server reload

# Stop all
ft stop
```
