#!/bin/bash

# FRP SSH Tunnel Automation Example
# This script demonstrates automated deployment and management

set -e

# Configuration
SERVER_IP="YOUR_SERVER_IP"
TOKEN="YOUR_TOKEN"
BASE_PORT=6001
MAX_CLIENTS=5

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if running in Colab
    if [ -d "/content" ]; then
        info "Running in Google Colab environment"
        ENVIRONMENT="colab"
    else
        info "Running in standard Linux environment"
        ENVIRONMENT="linux"
    fi
    
    # Check required commands
    for cmd in wget curl ssh; do
        if ! command -v $cmd &> /dev/null; then
            error "$cmd is not installed"
            exit 1
        fi
    done
    
    log "Prerequisites check passed"
}

# Download FRP client script
download_client_script() {
    log "Downloading FRP client script..."
    
    local script_url="https://raw.githubusercontent.com/cicy-dev/frp-tunnel/main/scripts/frp-client-colab.sh"
    
    if wget -q "$script_url" -O frp-client-colab.sh; then
        chmod +x frp-client-colab.sh
        log "Client script downloaded successfully"
    else
        error "Failed to download client script"
        exit 1
    fi
}

# Setup single client
setup_client() {
    local username=$1
    local port=$2
    
    log "Setting up client: $username on port $port"
    
    if ./frp-client-colab.sh "$username" "$port" "$SERVER_IP" "$TOKEN"; then
        log "Client $username setup completed on port $port"
        return 0
    else
        error "Failed to setup client $username on port $port"
        return 1
    fi
}

# Setup multiple clients
setup_multiple_clients() {
    log "Setting up multiple clients..."
    
    local success_count=0
    local failed_count=0
    
    for i in $(seq 1 $MAX_CLIENTS); do
        local username="colab$i"
        local port=$((BASE_PORT + i - 1))
        
        if setup_client "$username" "$port"; then
            ((success_count++))
        else
            ((failed_count++))
        fi
        
        # Small delay between setups
        sleep 2
    done
    
    log "Setup complete: $success_count successful, $failed_count failed"
}

# Monitor connections
monitor_connections() {
    log "Monitoring FRP connections..."
    
    while true; do
        local active_clients=$(ps aux | grep frpc | grep -v grep | wc -l)
        local ssh_status=$(systemctl is-active ssh 2>/dev/null || echo "unknown")
        
        info "Active FRP clients: $active_clients"
        info "SSH service status: $ssh_status"
        
        # Check each client
        for i in $(seq 1 $MAX_CLIENTS); do
            local port=$((BASE_PORT + i - 1))
            if nc -z localhost 22 2>/dev/null; then
                echo "✅ Port $port: SSH service accessible"
            else
                echo "❌ Port $port: SSH service not accessible"
            fi
        done
        
        echo "---"
        sleep 30
    done
}

# Health check
health_check() {
    log "Performing health check..."
    
    local issues=0
    
    # Check FRP client processes
    local frpc_count=$(ps aux | grep frpc | grep -v grep | wc -l)
    if [ $frpc_count -eq 0 ]; then
        error "No FRP client processes running"
        ((issues++))
    else
        info "FRP client processes: $frpc_count"
    fi
    
    # Check SSH service
    if systemctl is-active --quiet ssh 2>/dev/null; then
        info "SSH service is active"
    else
        error "SSH service is not active"
        ((issues++))
    fi
    
    # Check network connectivity
    if ping -c 1 "$SERVER_IP" &>/dev/null; then
        info "Server connectivity: OK"
    else
        error "Cannot reach server: $SERVER_IP"
        ((issues++))
    fi
    
    # Check logs for errors
    if [ -f ~/logs/frpc.log ]; then
        local error_count=$(grep -i error ~/logs/frpc.log | wc -l)
        if [ $error_count -gt 0 ]; then
            warn "Found $error_count errors in logs"
            ((issues++))
        fi
    fi
    
    if [ $issues -eq 0 ]; then
        log "Health check passed"
        return 0
    else
        error "Health check failed with $issues issues"
        return 1
    fi
}

# Restart all clients
restart_clients() {
    log "Restarting all FRP clients..."
    
    # Stop all existing clients
    pkill frpc || true
    sleep 3
    
    # Restart clients
    setup_multiple_clients
}

# Cleanup function
cleanup() {
    log "Cleaning up..."
    pkill frpc || true
    rm -f frp-client-colab.sh
}

# Main menu
show_menu() {
    echo
    echo "=== FRP SSH Tunnel Automation ==="
    echo "1. Setup single client"
    echo "2. Setup multiple clients"
    echo "3. Monitor connections"
    echo "4. Health check"
    echo "5. Restart all clients"
    echo "6. Cleanup and exit"
    echo "================================="
    echo -n "Choose an option [1-6]: "
}

# Main function
main() {
    log "Starting FRP SSH Tunnel automation"
    
    # Validate configuration
    if [ "$SERVER_IP" = "YOUR_SERVER_IP" ] || [ "$TOKEN" = "YOUR_TOKEN" ]; then
        error "Please update SERVER_IP and TOKEN in the script"
        exit 1
    fi
    
    check_prerequisites
    download_client_script
    
    # Interactive mode if no arguments
    if [ $# -eq 0 ]; then
        while true; do
            show_menu
            read -r choice
            
            case $choice in
                1)
                    echo -n "Enter username: "
                    read -r username
                    echo -n "Enter port: "
                    read -r port
                    setup_client "$username" "$port"
                    ;;
                2)
                    setup_multiple_clients
                    ;;
                3)
                    monitor_connections
                    ;;
                4)
                    health_check
                    ;;
                5)
                    restart_clients
                    ;;
                6)
                    cleanup
                    exit 0
                    ;;
                *)
                    error "Invalid option"
                    ;;
            esac
        done
    fi
    
    # Command line mode
    case $1 in
        "setup")
            setup_multiple_clients
            ;;
        "monitor")
            monitor_connections
            ;;
        "health")
            health_check
            ;;
        "restart")
            restart_clients
            ;;
        "cleanup")
            cleanup
            ;;
        *)
            echo "Usage: $0 [setup|monitor|health|restart|cleanup]"
            exit 1
            ;;
    esac
}

# Trap cleanup on exit
trap cleanup EXIT

# Run main function
main "$@"
