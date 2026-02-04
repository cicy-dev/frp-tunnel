# Configuration Reference

## Server Configuration

### FRP Server Config (`frps.ini`)

```ini
[common]
bind_port = 7000
token = your_secure_token_here

# Dashboard (optional)
dashboard_port = 7500
dashboard_user = admin
dashboard_pwd = admin

# Logging
log_file = ./frps.log
log_level = info
log_max_days = 3

# Security
authentication_method = token
heartbeat_timeout = 90
```

### Environment Variables

```bash
# Server configuration
export FRP_SERVER_PORT=7000
export FRP_TOKEN="your_token_here"
export FRP_LOG_LEVEL="info"
```

## Client Configuration

### FRP Client Config (`frpc.ini`)

```ini
[common]
server_addr = YOUR_SERVER_IP
server_port = 7000
token = your_secure_token_here

[ssh]
type = tcp
local_ip = 127.0.0.1
local_port = 22
remote_port = 6001
```

### SSH Client Config

Add to `~/.ssh/config`:

```ssh-config
# Colab connections
Host colab-1
    HostName YOUR_SERVER_IP
    User colab
    Port 6001
    IdentityFile ~/.ssh/id_rsa
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

Host colab-2
    HostName YOUR_SERVER_IP
    User colab
    Port 6002
    IdentityFile ~/.ssh/id_rsa
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

# Template for additional connections
Host colab-*
    HostName YOUR_SERVER_IP
    User colab
    IdentityFile ~/.ssh/id_rsa
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
```

## Port Management

### Default Port Allocation

| Port | Purpose | Client Type |
|------|---------|-------------|
| 7000 | FRP Server | Control |
| 6001 | SSH Tunnel | Primary Colab |
| 6002 | SSH Tunnel | Secondary Colab |
| 6003-6010 | SSH Tunnel | Additional clients |

### Custom Port Configuration

```bash
# Use custom port range
./frp-server-gcp.sh -p 8001-8010

# Single custom port
bash frp-client-colab.sh colab 8001 SERVER_IP TOKEN
```

## Security Configuration

### Token Management

```bash
# Generate secure token
TOKEN=$(openssl rand -hex 32)

# Update server config
sed -i "s/token = .*/token = $TOKEN/" ~/data/frp/frps.ini

# Restart server
sudo systemctl restart frps
```

### SSH Key Management

```bash
# Generate new SSH key pair
ssh-keygen -t rsa -b 4096 -f ~/.ssh/frp_tunnel

# Add to SSH config
Host colab-secure
    HostName YOUR_SERVER_IP
    User colab
    Port 6001
    IdentityFile ~/.ssh/frp_tunnel
```

### Firewall Configuration

#### GCP Firewall

```bash
# Create specific rule
gcloud compute firewall-rules create frp-ssh-tunnel \
    --allow tcp:6001-6010,tcp:7000 \
    --source-ranges YOUR_IP_RANGE \
    --target-tags frp-server

# Apply to instance
gcloud compute instances add-tags frp-server \
    --tags frp-server \
    --zone us-central1-a
```

#### UFW (Ubuntu)

```bash
# Allow FRP ports
sudo ufw allow 7000/tcp
sudo ufw allow 6001:6010/tcp

# Restrict to specific IPs
sudo ufw allow from YOUR_IP to any port 7000
```

## Advanced Configuration

### Load Balancing

```ini
# frps.ini - Multiple servers
[common]
bind_port = 7000
token = shared_token

# Health check
heartbeat_timeout = 30
```

### Monitoring

```ini
# frps.ini - Enable metrics
[common]
enable_prometheus = true
```

### Custom Domains

```ini
# frpc.ini - Custom domain
[ssh-custom]
type = tcp
local_ip = 127.0.0.1
local_port = 22
remote_port = 6001
custom_domains = ssh.yourdomain.com
```

## Environment-Specific Settings

### Google Colab

```python
# Colab-specific environment variables
import os
os.environ['FRP_SERVER'] = 'YOUR_SERVER_IP'
os.environ['FRP_TOKEN'] = 'YOUR_TOKEN'
os.environ['SSH_PORT'] = '6001'
```

### Windows PowerShell

```powershell
# PowerShell profile configuration
$env:FRP_SERVER = "YOUR_SERVER_IP"
$env:FRP_TOKEN = "YOUR_TOKEN"
$env:SSH_PORT = "6001"
```

### Linux/macOS

```bash
# Add to ~/.bashrc or ~/.zshrc
export FRP_SERVER="YOUR_SERVER_IP"
export FRP_TOKEN="YOUR_TOKEN"
export SSH_PORT="6001"
```

## Configuration Validation

### Test Configuration

```bash
# Validate server config
frps -c frps.ini -t

# Validate client config
frpc -c frpc.ini -t

# Test connectivity
telnet YOUR_SERVER_IP 7000
```

### Configuration Backup

```bash
# Backup configurations
tar -czf frp-config-backup.tar.gz ~/data/frp/ ~/.ssh/config

# Restore from backup
tar -xzf frp-config-backup.tar.gz -C /
```
