# 🚀 FRP Tunnel

**[中文文档](README_CN.md) | [English](README.md)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-blue.svg)](https://github.com/cicy-dev/frp-tunnel)

> 基于 [FRP](https://github.com/fatedier/frp) 的简单 CLI 封装 — 轻松管理 SSH 隧道。

## 安装

```bash
pip install frp-tunnel
```

## 快速开始

### 服务端

```bash
ft server init          # 生成配置 + 自动下载二进制
ft server start         # 启动服务端
ft server status        # 查看状态
```

### 客户端

```bash
ft client init --server 1.2.3.4 --token YOUR_TOKEN --port 6022
ft client start         # 启动客户端
ssh -p 6022 user@1.2.3.4
```

## 命令

```
ft server init          生成 ~/data/frp/frps.yaml（自动下载二进制）
ft server start         启动 frps
ft server stop          停止 frps
ft server reload        重启 frps（应用配置变更）
ft server status        查看服务端状态 + 活跃客户端
ft server install       安装为系统服务（systemd/launchd/startup）

ft client init          生成 ~/data/frp/frpc.yaml（自动下载二进制）
ft client start         启动 frpc
ft client stop          停止 frpc
ft client reload        热重载 frpc 配置（不断开连接）
ft client status        查看客户端状态

ft frps <args>          直接运行 frps（透传参数）
ft frpc <args>          直接运行 frpc（透传参数）
ft token                生成认证 token
ft stop                 停止所有 FRP 进程
ft --version            查看版本
ft -h                   帮助
```

## 配置

### 服务端 (`~/data/frp/frps.yaml`)

```yaml
bindPort: 7000
auth:
  token: frp_your_token_here
webServer:
  addr: 0.0.0.0
  port: 7500
  user: admin
  password: admin
log:
  to: ~/data/frp/frps.log
  level: info
```

### 客户端 (`~/data/frp/frpc.yaml`)

```yaml
serverAddr: YOUR_SERVER_IP
serverPort: 7000
auth:
  token: frp_your_token_here
log:
  to: ~/data/frp/frpc.log
  level: info
webServer:
  addr: 127.0.0.1
  port: 7400
proxies:
  - name: ssh_6022
    type: tcp
    localIP: 127.0.0.1
    localPort: 22
    remotePort: 6022
```

直接编辑配置文件增删代理，然后 `ft client reload`。

## 二进制文件

FRP 二进制文件打包在 `bin/` 目录：

| 目录 | 平台 |
|------|------|
| `bin/linux_arm64/` | Linux ARM64 |
| `bin/darwin_amd64/` | macOS x86_64 |
| `bin/windows_amd64/` | Windows x86_64 |

如果当前平台没有对应二进制，`ft server init` / `ft client init` 会自动从 [FRP releases](https://github.com/fatedier/frp/releases) 下载。

## 控制面板

访问 `http://服务器IP:7500`（admin/admin）查看已连接客户端。

API: `curl -u admin:admin http://localhost:7500/api/proxy/tcp`

## 要求

- Python >= 3.7
- 服务端：任意 VPS，开放 7000、7500 及隧道端口

## 致谢

基于 fatedier 的 [FRP](https://github.com/fatedier/frp) 构建。
