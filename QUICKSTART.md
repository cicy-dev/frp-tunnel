# Quick Start Examples

## Installation
```bash
pip install frp-tunnel
```

## Server Setup (GCP/VPS)
```bash
# Interactive setup
frp-tunnel setup

# Or direct command
frp-tunnel setup --mode server
```

## Google Colab (One-liner)
```python
# In Colab notebook cell
!pip install frp-tunnel && frp-tunnel colab --server YOUR_IP --token YOUR_TOKEN
```

## Local Client
```bash
# Interactive setup
frp-tunnel setup --mode client

# Or direct command
frp-tunnel client --server YOUR_IP --token YOUR_TOKEN --port 6001
```

## Status and Management
```bash
# Check status
frp-tunnel status

# View logs
frp-tunnel logs

# Stop all tunnels
frp-tunnel stop

# Clean cache
frp-tunnel clean
```

## SSH Connection
```bash
# After setup, connect via SSH
ssh -p 6001 colab@YOUR_SERVER_IP
```
