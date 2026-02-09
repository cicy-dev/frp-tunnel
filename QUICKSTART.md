# Quick Start Examples

## Installation
```bash
pip install frp-tunnel
```

## Server Setup (One-time)
```bash
# Auto-generates token and config
frp-tunnel server

# Output shows your token - save it!
```

## Client Connection
```bash
# Connect to server
frp-tunnel client --server YOUR_SERVER_IP --token YOUR_TOKEN --port 6000

# Then SSH normally
ssh -p 6000 user@YOUR_SERVER_IP
```

## Status and Management
```bash
# Check server status
frp-tunnel server-status

# Check client status
frp-tunnel client-status

# Stop all
frp-tunnel stop

# Restart server
frp-tunnel server -r
```

## Advanced
```bash
# Generate new token
frp-tunnel token

# Show version
frp-tunnel version

# Force restart server
frp-tunnel server -f
```
