# 🚀 FRP 隧道 - 30秒搞定SSH连接

**[中文文档](README_CN.md) | [English](README.md)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-blue.svg)](https://github.com/cicy-dev/frp-tunnel)

> **30秒内通过SSH连接Google Colab或任何远程服务器，无需复杂配置！**

## 🎯 这个工具解决什么问题

- **问题**: 无法SSH连接Google Colab，或者访问防火墙后面的远程服务器
- **解决**: 创建安全隧道，让你从任何地方都能SSH连接
- **结果**: 用你喜欢的工具（VS Code、文件传输等）操作远程服务器

## ⚡ 快速开始（3步搞定）

### 第1步：安装
```bash
pip install frp-tunnel
```

### 第2步：服务器设置（一次性）
```bash
# 在你的VPS/云服务器上运行
frp-tunnel setup
```
*按提示操作，30秒搞定*

### 第3步：随时随地连接
```bash
# Google Colab（粘贴到笔记本）
!pip install frp-tunnel && frp-tunnel colab --server 你的服务器IP --token 你的令牌

# 你的电脑
frp-tunnel client --server 你的服务器IP --token 你的令牌

# 然后正常SSH连接
ssh -p 6001 colab@你的服务器IP
```

## 🔧 实际使用例子

### 例子1：访问Google Colab文件
```python
# 在Colab笔记本中
!pip install frp-tunnel && frp-tunnel colab --server 34.123.45.67 --token abc123
```
```bash
# 在你的电脑上
ssh -p 6001 colab@34.123.45.67
# 现在你可以浏览文件、上传下载、使用git等等
```

### 例子2：VS Code远程开发
1. 设置隧道（上面的步骤）
2. VS Code安装"Remote-SSH"扩展
3. 连接到 `colab@你的服务器IP:6001`
4. 直接在Colab里用完整的VS Code功能写代码！

### 例子3：多个连接
```bash
# Colab 1
frp-tunnel colab --server 你的IP --token 你的令牌 --port 6001

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
