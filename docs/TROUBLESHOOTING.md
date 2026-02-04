# Troubleshooting Guide

## Common Issues and Solutions

### Connection Issues

#### "Connection refused" Error

**Symptoms:**
```bash
ssh: connect to host YOUR_SERVER_IP port 6001: Connection refused
```

**Solutions:**

1. **Check FRP server status:**
```bash
ps aux | grep frps
sudo systemctl status frps
```

2. **Restart FRP server:**
```bash
cd ~/data/frp
./frps -c frps.ini &
```

3. **Check firewall:**
```bash
# GCP
gcloud compute firewall-rules list | grep frp

# Ubuntu UFW
sudo ufw status
```

#### "Authentication failed" Error

**Symptoms:**
```bash
Permission denied (publickey)
```

**Solutions:**

1. **Verify SSH key:**
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa
ssh-copy-id -p 6001 colab@YOUR_SERVER_IP
```

2. **Check SSH service:**
```bash
sudo systemctl status ssh
sudo systemctl restart ssh
```

3. **Verify user exists:**
```bash
id colab
sudo useradd -m colab
```

#### "Port already in use" Error

**Symptoms:**
```bash
bind: address already in use
```

**Solutions:**

1. **Find process using port:**
```bash
sudo lsof -i :6001
sudo netstat -tulpn | grep 6001
```

2. **Kill conflicting process:**
```bash
sudo kill -9 PID_NUMBER
```

3. **Use different port:**
```bash
bash frp-client-colab.sh colab 6002 SERVER_IP TOKEN
```

### Token Issues

#### "Token mismatch" Error

**Solutions:**

1. **Check server token:**
```bash
grep token ~/data/frp/frps.ini
```

2. **Regenerate token:**
```bash
./frp-server-gcp.sh -r
```

3. **Update client with new token:**
```bash
bash frp-client-colab.sh colab 6001 SERVER_IP NEW_TOKEN
```

### Performance Issues

#### Slow Connection

**Diagnosis:**
```bash
# Test network latency
ping YOUR_SERVER_IP

# Test bandwidth
iperf3 -c YOUR_SERVER_IP -p 5201
```

**Solutions:**

1. **Optimize FRP config:**
```ini
# frps.ini
[common]
tcp_mux = true
heartbeat_timeout = 30
```

2. **Use compression:**
```ini
# frpc.ini
[ssh]
use_compression = true
```

#### High CPU Usage

**Solutions:**

1. **Limit connections:**
```ini
# frps.ini
[common]
max_clients = 5
```

2. **Adjust log level:**
```ini
log_level = warn
```

### Platform-Specific Issues

#### Google Colab Issues

**Colab disconnects frequently:**

```python
# Keep Colab alive
import time
import threading

def keep_alive():
    while True:
        time.sleep(300)  # 5 minutes
        print("Keeping Colab alive...")

thread = threading.Thread(target=keep_alive)
thread.daemon = True
thread.start()
```

**Runtime reset:**

```python
# Auto-reconnect after reset
!bash frp-client-colab.sh colab 6001 YOUR_SERVER_IP YOUR_TOKEN
```

#### Windows PowerShell Issues

**Execution policy error:**

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Path issues:**

```powershell
$env:PATH += ";C:\Program Files\OpenSSH"
```

#### Linux/macOS Issues

**Permission denied:**

```bash
chmod +x frp-client-linux.sh
sudo chown $USER:$USER frp-client-linux.sh
```

**Missing dependencies:**

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y openssh-client wget curl

# CentOS/RHEL
sudo yum install -y openssh-clients wget curl

# macOS
brew install openssh
```

## Diagnostic Commands

### Server Diagnostics

```bash
# Check all FRP processes
ps aux | grep frp

# Check listening ports
sudo netstat -tulpn | grep -E "(7000|600[0-9])"

# Check logs
tail -f ~/logs/frps.log

# Test FRP server
telnet localhost 7000

# Check system resources
top -p $(pgrep frps)
```

### Client Diagnostics

```bash
# Check FRP client
ps aux | grep frpc

# Check client logs
tail -f ~/logs/frpc.log

# Test SSH locally
ssh -p 22 localhost

# Check SSH config
ssh -F ~/.ssh/config -T colab-6001
```

### Network Diagnostics

```bash
# Test connectivity
nc -zv YOUR_SERVER_IP 7000
nc -zv YOUR_SERVER_IP 6001

# Trace route
traceroute YOUR_SERVER_IP

# Check DNS
nslookup YOUR_SERVER_IP
```

## Log Analysis

### Server Logs

```bash
# Error patterns
grep -i error ~/logs/frps.log
grep -i "connection refused" ~/logs/frps.log
grep -i "authentication failed" ~/logs/frps.log

# Connection patterns
grep "new connection" ~/logs/frps.log
grep "client login" ~/logs/frps.log
```

### Client Logs

```bash
# Connection status
grep -i "connect to server" ~/logs/frpc.log
grep -i "start proxy" ~/logs/frpc.log
grep -i "proxy stopped" ~/logs/frpc.log
```

### SSH Logs

```bash
# Authentication logs
sudo grep "sshd" /var/log/auth.log | tail -20
sudo grep "Failed password" /var/log/auth.log
sudo grep "Accepted publickey" /var/log/auth.log
```

## Recovery Procedures

### Complete Reset

```bash
# Stop all services
sudo pkill frps
sudo pkill frpc

# Remove configurations
rm -rf ~/data/frp
rm -rf ~/logs

# Reinstall
./frp-server-gcp.sh -r
```

### Backup and Restore

```bash
# Create backup
tar -czf frp-backup-$(date +%Y%m%d).tar.gz \
    ~/data/frp \
    ~/logs \
    ~/.ssh/config

# Restore backup
tar -xzf frp-backup-YYYYMMDD.tar.gz -C /
```

## Getting Help

### Debug Mode

```bash
# Run server in debug mode
cd ~/data/frp
./frps -c frps.ini -L debug

# Run client in debug mode
./frpc -c frpc.ini -L debug
```

### Collect System Information

```bash
# System info script
cat > debug-info.sh << 'EOF'
#!/bin/bash
echo "=== System Information ==="
uname -a
cat /etc/os-release

echo "=== Network Configuration ==="
ip addr show
ss -tulpn | grep -E "(7000|600[0-9])"

echo "=== FRP Processes ==="
ps aux | grep frp

echo "=== FRP Configuration ==="
cat ~/data/frp/frps.ini 2>/dev/null || echo "No server config"
cat ~/data/frp/frpc.ini 2>/dev/null || echo "No client config"

echo "=== Recent Logs ==="
tail -20 ~/logs/frps.log 2>/dev/null || echo "No server logs"
tail -20 ~/logs/frpc.log 2>/dev/null || echo "No client logs"
EOF

chmod +x debug-info.sh
./debug-info.sh > debug-report.txt
```

### Contact Support

When reporting issues, please include:

1. Operating system and version
2. FRP version
3. Complete error messages
4. Output from `debug-info.sh`
5. Steps to reproduce the issue

Create an issue at: https://github.com/your-username/frp-ssh-tunnel/issues
