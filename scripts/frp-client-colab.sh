#!/bin/bash

# FRP SSH隧道一键设置脚本 - Colab客户端
# 
# 快速开始:
# 1. 先在GCP服务器运行: ./frp-server-gcp.sh
# 2. 复制显示的token
# 3. 在Colab中运行: !bash frp-client-colab.sh colab 6001 35.220.164.135 your_token_here
# 4. 连接: ssh -p 6001 colab@35.220.164.135
#
# 使用方法: 
#   !bash frp-client-colab.sh                                    # 错误：需要token
#   !bash frp-client-colab.sh colab 6001 35.220.164.135 my_token # 指定所有参数
#   !bash frp-client-colab.sh myuser 6005 35.220.164.135 my_token -r # 强制重写配置
#
# 参数说明:
#   $1 - 用户名 (默认: colab)
#   $2 - 端口 (默认: 6001)  
#   $3 - 服务器地址 (默认: 35.220.164.135)
#   $4 - Token (必须提供)
#   $5 - -r 强制重写配置 (可选)

set -e

# 参数处理
USERNAME=${1:-"colab"}                     # 默认用户名colab
REMOTE_PORT=${2:-6001}                     # 默认端口6001
SERVER_ADDR=${3:-"35.220.164.135"}        # 默认服务器地址
TOKEN=${4:-""}                             # token参数
OVERWRITE_CONFIG=${5}                      # -r 参数强制重写配置

# 检查token不能为空
if [ -z "$TOKEN" ]; then
    echo "❌ 错误: Token不能为空"
    echo "使用方法: bash frp-client-colab.sh [username] [port] [server_addr] [token] [-r]"
    exit 1
fi

echo "🚀 FRP SSH隧道一键设置..."
echo "=================================="
echo "📋 配置参数:"
echo "   用户名: $USERNAME"
echo "   远程端口: $REMOTE_PORT"
echo "   服务器地址: $SERVER_ADDR"
echo "   认证令牌: [已设置]"
if [ "$OVERWRITE_CONFIG" = "-r" ]; then
    echo "   配置模式: 强制重写"
else
    echo "   配置模式: 保留现有"
fi
echo "=================================="

# 检查并安装SSH服务器
if ! dpkg -l | grep -q openssh-server; then
    echo "📦 安装SSH服务器..."
    apt update -qq
    apt install -y openssh-server
else
    echo "✅ SSH服务器已安装"
fi

# 创建用户(如果不存在)
if ! id $USERNAME &>/dev/null; then
    echo "👤 创建用户$USERNAME..."
    useradd -m -s /bin/bash $USERNAME
    usermod -aG sudo $USERNAME
    
    # 添加到sudoers，允许无密码sudo
    echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/$USERNAME
    chmod 440 /etc/sudoers.d/$USERNAME
else
    echo "✅ 用户$USERNAME已存在"
fi

# 设置SSH密钥认证 (无论用户是否存在都检查)
echo "🔑 配置SSH密钥认证..."
mkdir -p /home/$USERNAME/.ssh
chmod 700 /home/$USERNAME/.ssh

if [ ! -f "/home/$USERNAME/.ssh/authorized_keys" ]; then
    echo "📝 创建authorized_keys文件..."
    # 创建空的authorized_keys文件
    touch /home/$USERNAME/.ssh/authorized_keys
    chmod 600 /home/$USERNAME/.ssh/authorized_keys
    chown -R $USERNAME:$USERNAME /home/$USERNAME/.ssh
    echo "✅ SSH密钥文件已创建 (需要手动添加公钥)"
else
    echo "✅ authorized_keys文件已存在"
    # 确保权限正确
    chmod 600 /home/$USERNAME/.ssh/authorized_keys
    chown -R $USERNAME:$USERNAME /home/$USERNAME/.ssh
    echo "✅ SSH密钥权限已更新"
fi

# 配置SSH端口2022
echo "🔧 配置SSH服务..."
mkdir -p /etc/ssh/sshd_config.d
cat > /etc/ssh/sshd_config.d/frp.conf << EOF
Port 2022
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
EOF

# 重启SSH服务
echo "🔄 重启SSH服务..."
if pgrep sshd > /dev/null; then
    pkill sshd
fi
service ssh start

# 创建frpc配置文件
if [ ! -f "/content/frpc.ini" ] || [ "$OVERWRITE_CONFIG" = "-r" ]; then
    if [ "$OVERWRITE_CONFIG" = "-r" ]; then
        echo "📝 强制重写FRP客户端配置..."
    else
        echo "📝 创建FRP客户端配置..."
    fi
    
    cat > /content/frpc.ini << EOF
[common]
server_addr = $SERVER_ADDR
server_port = 7000
token = $TOKEN

[ssh]
type = tcp
local_ip = 127.0.0.1
local_port = 2022
remote_port = $REMOTE_PORT
EOF
    echo "✅ 配置端口: $REMOTE_PORT"
else
    echo "✅ FRP配置文件已存在，保留现有配置"
    echo "💡 使用 -r 参数可强制重写配置"
    # 读取现有配置显示信息
    EXISTING_PORT=$(grep "remote_port" /content/frpc.ini | cut -d'=' -f2 | tr -d ' ')
    EXISTING_SERVER=$(grep "server_addr" /content/frpc.ini | cut -d'=' -f2 | tr -d ' ')
    echo "✅ 现有端口: $EXISTING_PORT"
    echo "✅ 现有服务器: $EXISTING_SERVER"
fi

# 检查并下载FRP
if [ ! -d "/content/frp_0.52.3_linux_amd64" ]; then
    echo "📥 下载FRP客户端..."
    cd /content
    wget -q https://github.com/fatedier/frp/releases/download/v0.52.3/frp_0.52.3_linux_amd64.tar.gz
    tar -xzf frp_0.52.3_linux_amd64.tar.gz
else
    echo "✅ FRP客户端已下载"
fi

# 停止现有FRP进程并重启
echo "🔄 重启FRP客户端..."
if pgrep -f "frpc" > /dev/null; then
    pkill -f "frpc"
    sleep 2
fi

mkdir -p ~/logs
cd /content/frp_0.52.3_linux_amd64
./frpc -c /content/frpc.ini > ~/logs/frpc.log 2>&1 &
sleep 3

echo ""
echo "🔍 系统状态检查..."
echo "=================================="

# 检查用户
if id $USERNAME &>/dev/null; then
    echo "✅ 用户: $USERNAME ($(id $USERNAME | cut -d' ' -f1-3))"
    if [ -f "/home/$USERNAME/.ssh/authorized_keys" ]; then
        echo "✅ SSH密钥: 已配置"
    else
        echo "❌ SSH密钥: 未配置"
    fi
    if [ -f "/etc/sudoers.d/$USERNAME" ]; then
        echo "✅ Sudo权限: 无密码sudo已配置"
    else
        echo "⚠️  Sudo权限: 需要密码"
    fi
else
    echo "❌ 用户: $USERNAME 不存在"
fi

# 检查SSH服务
if pgrep sshd > /dev/null; then
    echo "✅ SSH服务: 运行中 (端口2022)"
    if netstat -tlnp 2>/dev/null | grep -q ":2022"; then
        echo "✅ SSH端口: 2022 监听中"
    else
        echo "⚠️  SSH端口: 2022 未监听"
    fi
else
    echo "❌ SSH服务: 未运行"
fi

# 检查FRP客户端
if pgrep -f "frpc" > /dev/null; then
    FRP_PID=$(pgrep -f "frpc")
    echo "✅ FRP客户端: 运行中 (PID: $FRP_PID)"
    
    # 检查连接状态
    sleep 2
    if grep -q "login to server success" ~/logs/frpc.log 2>/dev/null; then
        echo "✅ FRP连接: 已连接到服务器"
    elif grep -q "connect to server" ~/logs/frpc.log 2>/dev/null; then
        echo "🔄 FRP连接: 正在连接..."
    else
        echo "⚠️  FRP连接: 状态未知"
    fi
else
    echo "❌ FRP客户端: 未运行"
fi

# 检查配置文件
if [ -f "/content/frpc.ini" ]; then
    echo "✅ 配置文件: frpc.ini 存在"
else
    echo "❌ 配置文件: frpc.ini 不存在"
fi

echo ""
echo "🎉 设置完成!"
echo "=================================="
echo "📋 连接信息:"
echo "   SSH命令: ssh -p $REMOTE_PORT $USERNAME@$SERVER_ADDR"
echo "   SSH配置: ssh $USERNAME-$REMOTE_PORT (需配置 ~/.ssh/config)"
echo "   认证方式: RSA密钥"
echo "   密钥文件: ~/.ssh/id_rsa (本地)"
echo "=================================="
echo "📝 注意事项:"
echo "   • 确保GCP服务器frps正在运行"
echo "   • 确保防火墙开放端口6001-6010,7000"
echo "   • 使用RSA密钥认证，无需密码"
echo "   • $USERNAME用户可无密码使用sudo命令"
echo "   • 如有问题查看日志: cat ~/logs/frpc.log"
echo "=================================="
