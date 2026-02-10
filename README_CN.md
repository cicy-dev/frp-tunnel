# 🚀 FRP Tunnel - SSH 访问变简单

**[中文文档](README_CN.md) | [English](README.md)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-blue.svg)](https://github.com/cicy-dev/frp-tunnel)

> **30 秒内通过 SSH 连接到 Google Colab 或任何远程服务器，无需复杂配置！**

## 🎯 这是什么

- **问题**：无法 SSH 到 Google Colab 或访问防火墙后的远程服务器
- **解决方案**：创建安全隧道，让你可以从任何地方 SSH 连接
- **结果**：使用你喜欢的工具（VS Code、文件传输等）访问远程服务器

## ⚡ 快速开始

### 安装
```bash
pip install frp-tunnel
```

### 启动服务器（一次性设置）
```bash
# 自动生成 token 和配置
frp-tunnel server

# 输出：
# 🚀 Starting server...
# 🔑 Generated token: frp_abc123...
# ✅ Server started
```

### 连接客户端
```bash
# 连接到服务器
frp-tunnel client --server 你的服务器IP --token 你的TOKEN --port 6000

# 然后正常 SSH 连接
ssh -p 6000 user@你的服务器IP
```

## 🎮 命令

```bash
# 服务器
frp-tunnel server              # 启动服务器（自动生成 token）
frp-tunnel server -f           # 强制重启
frp-tunnel server -r           # 重启
frp-tunnel server-status       # 显示服务器状态

# 客户端
frp-tunnel client --server IP --token TOKEN --port 6000
frp-tunnel client-status       # 显示客户端状态

# 工具
frp-tunnel token               # 生成新 token
frp-tunnel version             # 显示版本
frp-tunnel stop                # 停止所有
```

## 📊 状态显示

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

## 🔧 配置

### 服务器配置 (`~/data/frp/frps.ini`)
```ini
[common]
bind_port = 7000
token = frp_your_token_here
dashboard_port = 7500
dashboard_user = admin
dashboard_pwd = admin
```

### 客户端配置 (`~/data/frp/frpc.ini`)
```ini
[common]
server_addr = 你的服务器IP
server_port = 7000
token = frp_your_token_here
login_fail_exit = false

[ssh_6000]
type = tcp
local_ip = 127.0.0.1
local_port = 22
remote_port = 6000
```

手动编辑配置文件可添加更多端口。

## 🌟 特性

- ✅ **自动下载** FRP 二进制文件（无需手动安装）
- ✅ **自动生成** token 和配置
- ✅ **YAML 配置** - 现代格式，支持热重载
- ✅ **多端口支持** - SSH、RDP 或任何服务
- ✅ **简易端口管理** - 无需编辑配置文件即可添加/删除端口
- ✅ **热重载** - 更新配置不断开 SSH 连接
- ✅ **后台模式** - 作为守护进程运行
- ✅ **多平台** - Windows、Linux、macOS
- ✅ **控制面板** - Web UI 在 7500 端口
- ✅ **API 支持** - 通过 REST API 查询客户端状态
- ✅ **Systemd 集成** - Linux 服务器开机自启
- ✅ **健康监控** - Windows 客户端自动监控（5.5小时运行限制）

## 🛠️ 高级用法

### Systemd 服务（Linux 服务器）
```bash
# 启用开机自启
sudo systemctl enable frps.service
sudo systemctl start frps.service
sudo systemctl status frps.service
```

服务文件会自动创建在 `/etc/systemd/system/frps.service`，如果崩溃会自动重启服务器。

### Windows 客户端监控
Windows 启动脚本包含自动监控功能：
- 创建 `C:\running.txt` 作为健康检查文件
- 每 50 秒监控 FRP 客户端状态
- 运行 5.5 小时后自动停止
- 删除 `C:\running.txt` 将停止监控循环

### 多端口
编辑 `~/data/frp/frpc.ini` 添加更多端口：
```ini
[ssh_6001]
type = tcp
local_ip = 127.0.0.1
local_port = 22
remote_port = 6001
```

### 控制面板访问
访问 `http://你的服务器IP:7500`（admin/admin）

### API 访问
```bash
curl -u admin:admin http://localhost:7500/api/proxy/tcp
```

## 📋 要求

- **服务器**：任何 Linux VPS（Google Cloud、AWS、DigitalOcean 等）
- **端口**：在服务器上开放 6000-6010、7000、7500 端口
- **客户端**：任何有 SSH 的计算机

## 🙏 致谢

特别感谢 [FRP 项目](https://github.com/fatedier/frp) 的作者创建了这个优秀的反向代理工具，使本项目成为可能。

---

⭐ **如果这个项目帮你节省了时间，请给个 Star！**

# Colab 2  
frp-tunnel colab --server 你的IP --token 你的令牌 --port 6002

# 你的笔记本
frp-tunnel client --server 你的IP --token 你的令牌 --port 6003
```

## 🛠️ 常见问题解决

### "连接被拒绝"
```bash
# 检查服务器是否在运行
ssh 你的服务器IP "ps aux | grep frps"
```

### "权限被拒绝"
```bash
# 确保使用正确的端口
ssh -p 6001 colab@你的服务器IP  # 不是22端口！
```

### "令牌不匹配"
```bash
# 从服务器获取令牌
ssh 你的服务器IP "cat ~/data/frp/frps.ini | grep token"
```

## 📋 你需要什么

- **服务器**: 任何Linux VPS（Google Cloud、AWS、DigitalOcean等）
- **端口**: 在服务器上开放6001-6010和7000端口
- **客户端**: 任何有SSH的电脑（Windows/Mac/Linux）

### 快速服务器设置（GCP/AWS）
```bash
# 开放防火墙端口
gcloud compute firewall-rules create frp-tunnel --allow tcp:6001-6010,tcp:7000

# 或者AWS
aws ec2 authorize-security-group-ingress --group-id sg-xxxxx --protocol tcp --port 6001-6010 --cidr 0.0.0.0/0
```

## 🎉 就这么简单！

不需要复杂的配置文件，不需要网络知识。只需安装、运行、连接！

**需要帮助？** [提交问题](https://github.com/cicy-dev/frp-tunnel/issues) - 我们回复很快！

---

⭐ **如果这个工具帮到你了，请给个星标！**
