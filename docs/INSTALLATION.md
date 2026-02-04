# Installation Guide

## Prerequisites

### Server Requirements
- Linux VPS or GCP instance
- Root or sudo access
- Open ports: 7000, 6001-6010
- Minimum 1GB RAM, 1 CPU core

### Client Requirements
- SSH client installed
- Internet connection
- For Windows: PowerShell 5.0+

## Server Installation

### 1. GCP Instance Setup

```bash
# Create GCP instance
gcloud compute instances create frp-server \
    --zone=us-central1-a \
    --machine-type=e2-micro \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=10GB

# Configure firewall
gcloud compute firewall-rules create frp-tunnel \
    --allow tcp:6001-6010,tcp:7000 \
    --source-ranges 0.0.0.0/0
```

### 2. Server Script Installation

```bash
# SSH to your server
gcloud compute ssh frp-server --zone=us-central1-a

# Download and run setup
wget https://raw.githubusercontent.com/your-username/frp-ssh-tunnel/main/scripts/frp-server-gcp.sh
chmod +x frp-server-gcp.sh
./frp-server-gcp.sh
```

### 3. Save Your Token

The script will display a token like:
```
🔑 Your connection token: frp_a1b2c3d4e5f6...
```

**Important**: Save this token - you'll need it for all client connections.

## Client Installation

### Google Colab

```python
# In a Colab cell
!wget -q https://raw.githubusercontent.com/your-username/frp-ssh-tunnel/main/scripts/frp-client-colab.sh
!bash frp-client-colab.sh colab 6001 YOUR_SERVER_IP YOUR_TOKEN
```

### Windows

```powershell
# Download script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/your-username/frp-ssh-tunnel/main/scripts/frp-client-windows.ps1" -OutFile "frp-client-windows.ps1"

# Run setup
.\frp-client-windows.ps1 -Username "colab" -RemotePort 6001 -ServerAddr "YOUR_SERVER_IP" -Token "YOUR_TOKEN"
```

### Linux/macOS

```bash
wget https://raw.githubusercontent.com/your-username/frp-ssh-tunnel/main/scripts/frp-client-linux.sh
bash frp-client-linux.sh colab 6001 YOUR_SERVER_IP YOUR_TOKEN
```

## Verification

### Test Connection

```bash
# Test SSH connection
ssh -p 6001 colab@YOUR_SERVER_IP

# Should see Colab environment prompt
```

### Check Services

```bash
# On server - check FRP server
ps aux | grep frps

# On client - check FRP client  
ps aux | grep frpc

# Check SSH service
sudo systemctl status ssh
```

## Next Steps

1. Set up SSH config for easy connections (see [Configuration Guide](CONFIGURATION.md))
2. Configure multiple clients if needed
3. Set up monitoring and logging
4. Review security settings

## Troubleshooting

If installation fails, see [Troubleshooting Guide](TROUBLESHOOTING.md) for common solutions.
