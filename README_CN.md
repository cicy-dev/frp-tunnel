# 🚀 FRP SSH 隧道 - 简易远程访问解决方案

**[中文文档](README_CN.md) | [English](README.md)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-blue.svg)](https://github.com/cicy-dev/frp-tunnel)
[![Shell Script](https://img.shields.io/badge/Shell-Bash%20%7C%20PowerShell-green.svg)](https://github.com/cicy-dev/frp-tunnel)

> **使用 FRP（快速反向代理）为 Google Colab、远程服务器和本地开发环境提供一键式 SSH 隧道设置。**

## ✨ 特性

- 🔐 **安全的 SSH 隧道** 支持 RSA 密钥认证
- 🌐 **多平台支持** (Linux, Windows, macOS, Google Colab)
- 🚀 **一键部署** 自动化脚本
- 🔄 **多客户端支持** (最多 10 个并发连接)
- 🛡️ **基于令牌的认证** 增强安全性
- 📱 **智能配置管理** 防止覆盖保护
- 🔧 **自动检测** 现有安装
- 📊 **实时状态监控** 和诊断

## 🎯 使用场景

- **机器学习**: 通过 SSH 访问 Google Colab 进行文件传输和远程调试
- **远程开发**: 将本地 IDE 连接到云环境
- **数据处理**: 大型数据集的安全传输
- **DevOps**: 远程服务器管理和自动化

## 🚀 快速开始

### 安装
```bash
pip install frp-tunnel
```

### 服务器设置 (GCP/VPS)
```bash
frp-tunnel setup
# 按照交互式向导操作
```

### Google Colab (一行命令)
```python
# 在 Colab 笔记本单元格中
!pip install frp-tunnel && frp-tunnel colab --server YOUR_IP --token YOUR_TOKEN
```

### 本地客户端
```bash
frp-tunnel client --server YOUR_IP --token YOUR_TOKEN
```

### 通过 SSH 连接
```bash
ssh -p 6001 colab@YOUR_SERVER_IP
```

## 📖 详细文档

### 前置要求

- **服务器**: 具有 root 访问权限的 Linux VPS/GCP 实例
- **客户端**: 任何带有 SSH 客户端的系统
- **网络**: 在服务器上开放端口 6001-6010 和 7000

### 端口配置

| 端口范围 | 用途 | 描述 |
|----------|------|------|
| 7000 | FRP 服务器 | 主要 FRP 服务端口 |
| 6001-6010 | SSH 隧道 | 客户端 SSH 连接 |

### 令牌管理

- 令牌自动生成并存储在 `~/data/frp/frps.ini`
- 使用 `-r` 标志重新生成令牌
- 客户端必须使用与服务器相同的令牌

## ⚙️ 配置

### SSH 配置模板

添加到 `~/.ssh/config` 以简化连接：

```ssh-config
Host colab-6001
    HostName YOUR_SERVER_IP
    User colab
    Port 6001
    IdentityFile ~/.ssh/id_rsa

Host colab-6002
    HostName YOUR_SERVER_IP
    User colab
    Port 6002
    IdentityFile ~/.ssh/id_rsa
```

然后使用: `ssh colab-6001` 连接

### 防火墙设置 (GCP)

```bash
# 创建防火墙规则
gcloud compute firewall-rules create frp-tunnel --allow tcp:6001-6010,tcp:7000
```

## 🔧 高级用法

### 多客户端

```bash
# 客户端 1 (Colab)
bash frp-client-colab.sh colab 6001 SERVER_IP TOKEN

# 客户端 2 (另一个 Colab)
bash frp-client-colab.sh colab 6002 SERVER_IP TOKEN

# 客户端 3 (自定义用户)
bash frp-client-colab.sh myuser 6003 SERVER_IP TOKEN
```

## 🛠️ 故障排除

### 常见问题

| 问题 | 解决方案 |
|------|----------|
| 连接被拒绝 | 检查 FRP 服务器是否运行: `ps aux \| grep frps` |
| 认证失败 | 验证服务器和客户端令牌是否匹配 |
| 端口已被使用 | 使用不同端口或检查现有连接 |
| SSH 密钥被拒绝 | 确保 RSA 密钥配置正确 |

### 诊断命令

```bash
# 检查 FRP 服务器状态
ps aux | grep frps

# 查看服务器日志
cat ~/logs/frps.log

# 查看客户端日志
cat ~/logs/frpc.log

# 测试 FRP 服务器连接
telnet YOUR_SERVER_IP 7000

# 检查 SSH 服务
service ssh status

# 验证令牌
grep token ~/data/frp/frps.ini
```

## 🤝 贡献

欢迎贡献！请查看我们的 [贡献指南](CONTRIBUTING.md) 了解详情。

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开 Pull Request

## 📝 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [FRP 项目](https://github.com/fatedier/frp) - 底层反向代理工具
- Google Colab 团队提供云环境
- 社区贡献者和测试人员

---

⭐ **如果这个项目对您有帮助，请给个星标！**

📧 **有问题？** 提交 [issue](https://github.com/cicy-dev/frp-tunnel/issues) 或开始 [讨论](https://github.com/cicy-dev/frp-tunnel/discussions)
