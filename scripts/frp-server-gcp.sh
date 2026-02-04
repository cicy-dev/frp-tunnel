#!/bin/bash

# FRP服务器一键启动脚本 - GCP服务器端
# 使用方法:
#   ./frp-server-gcp.sh          # 使用默认配置
#   ./frp-server-gcp.sh -r       # 强制重写配置

set -e

# 参数处理
OVERWRITE_CONFIG=${1}                     # -r 参数强制重写配置

# 获取服务器地址用于SSH配置显示
SERVER_ADDR="35.220.164.135"

echo "🚀 启动FRP服务器..."
echo "=========================="
if [ "$OVERWRITE_CONFIG" = "-r" ]; then
    echo "📋 配置模式: 强制重写"
else
    echo "📋 配置模式: 保留现有"
fi
echo "=========================="
echo "=========================="

# 创建数据目录
mkdir -p ~/data/frp
cd ~/data/frp

# 复制或创建配置文件
if [ ! -f "frps.ini" ] || [ "$OVERWRITE_CONFIG" = "-r" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    if [ "$OVERWRITE_CONFIG" = "-r" ]; then
        echo "📝 强制重写FRP服务器配置..."
        # 生成新token
        TOKEN="frp_$(openssl rand -hex 16)"
    else
        echo "📝 创建FRP服务器配置..."
        # 生成新token
        TOKEN="frp_$(openssl rand -hex 16)"
    fi
    
    cat > frps.ini << EOF
[common]
bind_port = 7000
token = $TOKEN

# 默认端口配置 (自动生成)
[ssh_demo_6001]
type = tcp
bind_port = 6001

[ssh_demo_6002]
type = tcp
bind_port = 6002

[ssh_demo_6003]
type = tcp
bind_port = 6003
EOF
    echo "✅ 已创建配置，token: $TOKEN"
    echo "✅ 已添加默认端口配置: 6001, 6002, 6003"
else
    echo "✅ FRP配置文件已存在，保留现有配置"
    echo "💡 使用 -r 参数可强制重写配置"
    # 读取现有token
    TOKEN=$(grep "token = " frps.ini | cut -d'=' -f2 | tr -d ' ')
    echo "✅ 使用现有token: [已设置]"
fi

# 检查并下载FRP
if [ ! -d "frp_0.52.3_linux_amd64" ]; then
    echo "📥 下载FRP服务器..."
    wget -q https://github.com/fatedier/frp/releases/download/v0.52.3/frp_0.52.3_linux_amd64.tar.gz
    tar -xzf frp_0.52.3_linux_amd64.tar.gz
else
    echo "✅ FRP服务器已下载"
fi

# 停止现有frps进程
if pgrep -f "frps" > /dev/null; then
    echo "🔄 停止现有FRP服务器..."
    pkill -f "frps"
    sleep 2
fi

echo "🔗 启动FRP服务器..."
mkdir -p ~/logs
cd frp_0.52.3_linux_amd64
./frps -c ../frps.ini > ~/logs/frps.log 2>&1 &

sleep 3

echo ""
echo "🔍 服务器状态检查..."
echo "=========================="

# 检查进程
if pgrep -f "frps" > /dev/null; then
    FRP_PID=$(pgrep -f "frps")
    echo "✅ FRP服务器: 运行中 (PID: $FRP_PID)"
else
    echo "❌ FRP服务器: 启动失败"
    echo "日志:"
    cat ~/logs/frps.log
    exit 1
fi

# 检查端口监听
if netstat -tlnp 2>/dev/null | grep -q ":7000"; then
    echo "✅ 端口7000: 监听中"
else
    echo "❌ 端口7000: 未监听"
fi

# 检查配置
echo "✅ 配置文件: ~/data/frp/frps.ini"
echo "✅ 工作目录: ~/data/frp"

echo ""
echo "🎉 FRP服务器启动完成!"
echo "=========================="
echo "📋 服务信息:"
echo "   监听端口: 7000"
echo "   客户端端口: 6001, 6002, 6003 (默认)"
echo "   认证令牌: $TOKEN"
echo "   工作目录: ~/data/frp"
echo "   日志文件: ~/logs/frps.log"
echo "=========================="
echo "📝 SSH配置模板:"
echo "   复制以下内容到 ~/.ssh/config:"
echo ""
echo "Host colab-6001"
echo "    HostName $SERVER_ADDR"
echo "    User colab"
echo "    Port 6001"
echo "    IdentityFile ~/.ssh/id_rsa"
echo ""
echo "Host colab-6002"
echo "    HostName $SERVER_ADDR"
echo "    User colab"
echo "    Port 6002"
echo "    IdentityFile ~/.ssh/id_rsa"
echo ""
echo "Host colab-6003"
echo "    HostName $SERVER_ADDR"
echo "    User colab"
echo "    Port 6003"
echo "    IdentityFile ~/.ssh/id_rsa"
echo "=========================="
echo "📝 测试命令:"
echo "   ssh colab-6001"
echo "   ssh colab-6002"
echo "   ssh colab-6003"
echo "=========================="
