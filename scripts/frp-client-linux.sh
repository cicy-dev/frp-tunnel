#!/bin/bash

# FRP Client for Linux/macOS
# Usage: bash frp-client-linux.sh [username] [port] [server_addr] [token] [-r]

set -e

# Default parameters
USERNAME=${1:-"colab"}
REMOTE_PORT=${2:-6001}
SERVER_ADDR=${3:-""}
TOKEN=${4:-""}
OVERWRITE_CONFIG=${5}

# Validate required parameters
if [ -z "$SERVER_ADDR" ] || [ -z "$TOKEN" ]; then
    echo "❌ Error: Server address and token are required"
    echo "Usage: bash frp-client-linux.sh [username] [port] [server_addr] [token] [-r]"
    exit 1
fi

echo "🚀 FRP SSH Tunnel Setup - Linux/macOS"
echo "======================================"
echo "📋 Configuration:"
echo "   Username: $USERNAME"
echo "   Remote Port: $REMOTE_PORT"
echo "   Server Address: $SERVER_ADDR"
echo "   Token: [configured]"
if [ "$OVERWRITE_CONFIG" = "-r" ]; then
    echo "   Config Mode: Force overwrite"
else
    echo "   Config Mode: Preserve existing"
fi
echo "======================================"

# Create directories
mkdir -p ~/data/frp ~/logs

# Download FRP if not exists
if [ ! -f ~/data/frp/frpc ]; then
    echo "📥 Downloading FRP client..."
    cd ~/data/frp
    
    # Detect architecture
    ARCH=$(uname -m)
    case $ARCH in
        x86_64) FRP_ARCH="amd64" ;;
        aarch64|arm64) FRP_ARCH="arm64" ;;
        armv7l) FRP_ARCH="arm" ;;
        *) echo "❌ Unsupported architecture: $ARCH"; exit 1 ;;
    esac
    
    # Detect OS
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    
    FRP_VERSION="0.52.3"
    FRP_FILE="frp_${FRP_VERSION}_${OS}_${FRP_ARCH}.tar.gz"
    FRP_URL="https://github.com/fatedier/frp/releases/download/v${FRP_VERSION}/${FRP_FILE}"
    
    wget -q "$FRP_URL"
    tar -xzf "$FRP_FILE" --strip-components=1
    rm "$FRP_FILE"
    
    echo "✅ FRP client downloaded"
fi

# Create or update FRP client configuration
if [ ! -f ~/data/frp/frpc.ini ] || [ "$OVERWRITE_CONFIG" = "-r" ]; then
    echo "📝 Creating FRP client configuration..."
    
    cat > ~/data/frp/frpc.ini << EOF
[common]
server_addr = $SERVER_ADDR
server_port = 7000
token = $TOKEN
log_file = $HOME/logs/frpc.log
log_level = info

[ssh_$USERNAME]
type = tcp
local_ip = 127.0.0.1
local_port = 22
remote_port = $REMOTE_PORT
EOF
    
    echo "✅ FRP client configuration created"
else
    echo "ℹ️  Using existing FRP configuration"
fi

# Setup SSH if needed
if [ ! -f ~/.ssh/id_rsa ]; then
    echo "🔑 Generating SSH key pair..."
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
    echo "✅ SSH key pair generated"
fi

# Create user if not exists (requires sudo)
if ! id "$USERNAME" &>/dev/null; then
    echo "👤 Creating user: $USERNAME"
    if command -v sudo &>/dev/null; then
        sudo useradd -m -s /bin/bash "$USERNAME" || true
        sudo mkdir -p "/home/$USERNAME/.ssh"
        sudo cp ~/.ssh/id_rsa.pub "/home/$USERNAME/.ssh/authorized_keys"
        sudo chown -R "$USERNAME:$USERNAME" "/home/$USERNAME/.ssh"
        sudo chmod 700 "/home/$USERNAME/.ssh"
        sudo chmod 600 "/home/$USERNAME/.ssh/authorized_keys"
        echo "✅ User $USERNAME created and configured"
    else
        echo "⚠️  Warning: sudo not available, user creation skipped"
    fi
fi

# Start SSH service if not running
if command -v systemctl &>/dev/null; then
    if ! systemctl is-active --quiet ssh; then
        echo "🔧 Starting SSH service..."
        sudo systemctl start ssh
        sudo systemctl enable ssh
        echo "✅ SSH service started"
    fi
elif command -v service &>/dev/null; then
    if ! service ssh status &>/dev/null; then
        echo "🔧 Starting SSH service..."
        sudo service ssh start
        echo "✅ SSH service started"
    fi
fi

# Stop existing FRP client
pkill frpc || true
sleep 2

# Start FRP client
echo "🚀 Starting FRP client..."
cd ~/data/frp
nohup ./frpc -c frpc.ini > ~/logs/frpc.log 2>&1 &

# Wait and verify
sleep 3
if pgrep frpc > /dev/null; then
    echo "✅ FRP client started successfully"
else
    echo "❌ Failed to start FRP client"
    echo "📋 Log output:"
    tail -10 ~/logs/frpc.log
    exit 1
fi

# Display connection information
echo
echo "🎉 Setup Complete!"
echo "=================="
echo "SSH Command: ssh -p $REMOTE_PORT $USERNAME@$SERVER_ADDR"
echo "SCP Upload: scp -P $REMOTE_PORT file.txt $USERNAME@$SERVER_ADDR:~/"
echo "SCP Download: scp -P $REMOTE_PORT $USERNAME@$SERVER_ADDR:~/file.txt ./"
echo
echo "💡 Add to ~/.ssh/config:"
echo "Host $USERNAME-$REMOTE_PORT"
echo "    HostName $SERVER_ADDR"
echo "    User $USERNAME"
echo "    Port $REMOTE_PORT"
echo "    IdentityFile ~/.ssh/id_rsa"
echo "=================="
