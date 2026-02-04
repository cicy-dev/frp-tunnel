# 🚀 FRP Tunnel - SSH Access Made Easy

**[中文文档](README_CN.md) | [English](README.md)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-blue.svg)](https://github.com/cicy-dev/frp-tunnel)

> **Connect to Google Colab or any remote server via SSH in 30 seconds. No complex setup needed!**

## 🎯 What This Does

- **Problem**: Can't SSH into Google Colab or access remote servers behind firewalls
- **Solution**: Creates a secure tunnel so you can SSH from anywhere
- **Result**: Use your favorite tools (VS Code, file transfer, etc.) with remote servers

## 🏗️ How It Works

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

## ⚡ Quick Start (3 Steps)

### Step 1: Install
```bash
pip install frp-tunnel
```

### Step 2: Set Up Server (One-time)
```bash
# On your VPS/cloud server
frp-tunnel setup
```
*Follow the prompts - it takes 30 seconds*

### Step 3: Connect from Anywhere
```bash
# Google Colab (paste in notebook)
!pip install frp-tunnel && frp-tunnel colab --server YOUR_SERVER_IP --token YOUR_TOKEN

# Your computer
frp-tunnel client --server YOUR_SERVER_IP --token YOUR_TOKEN

# Then SSH normally
ssh -p 6001 colab@YOUR_SERVER_IP
```

## 🔧 Real-World Examples

### Example 1: Access Google Colab Files
```python
# In Colab notebook
!pip install frp-tunnel && frp-tunnel colab --server 34.123.45.67 --token abc123
```
```bash
# On your computer
ssh -p 6001 colab@34.123.45.67
# Now you can browse files, upload/download, use git, etc.
```

### Example 2: VS Code Remote Development
1. Set up tunnel (steps above)
2. In VS Code: Install "Remote-SSH" extension
3. Connect to `colab@YOUR_SERVER_IP:6001`
4. Code directly in Colab with full VS Code features!

### Example 3: Multiple Connections
```bash
# Colab 1
frp-tunnel colab --server YOUR_IP --token YOUR_TOKEN --port 6001

# Colab 2  
frp-tunnel colab --server YOUR_IP --token YOUR_TOKEN --port 6002

# Your laptop
frp-tunnel client --server YOUR_IP --token YOUR_TOKEN --port 6003
```

## 🛠️ Troubleshooting (Common Issues)

### "Connection refused"
```bash
# Check if server is running
ssh YOUR_SERVER_IP "ps aux | grep frps"
```

### "Permission denied"
```bash
# Make sure you're using the right port
ssh -p 6001 colab@YOUR_SERVER_IP  # Not port 22!
```

### "Token mismatch"
```bash
# Get the token from your server
ssh YOUR_SERVER_IP "cat ~/data/frp/frps.ini | grep token"
```

## 📋 What You Need

- **Server**: Any Linux VPS (Google Cloud, AWS, DigitalOcean, etc.)
- **Ports**: Open ports 6001-6010 and 7000 on your server
- **Client**: Any computer with SSH (Windows/Mac/Linux)

### Quick Server Setup (GCP/AWS)
```bash
# Open firewall ports
gcloud compute firewall-rules create frp-tunnel --allow tcp:6001-6010,tcp:7000

# Or for AWS
aws ec2 authorize-security-group-ingress --group-id sg-xxxxx --protocol tcp --port 6001-6010 --cidr 0.0.0.0/0
```

## 🎉 That's It!

No complex configuration files, no networking knowledge needed. Just install, run, and connect!

**Need help?** [Open an issue](https://github.com/cicy-dev/frp-tunnel/issues) - we respond quickly!

---

⭐ **Star this repo if it saved you time!**
