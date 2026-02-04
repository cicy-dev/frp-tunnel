#!/bin/bash

# FRP Tunnel 安装脚本
# 标准 pip 安装

set -e

echo "🚀 Installing FRP Tunnel..."

pip install -e .

echo "✅ FRP Tunnel installed successfully!"
echo "🔧 Run 'frp-tunnel setup' to get started"
