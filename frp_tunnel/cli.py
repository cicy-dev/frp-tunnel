#!/usr/bin/env python3
"""FRP Tunnel CLI - Simple SSH tunneling"""

import sys
import os
import subprocess
import secrets
import configparser
from pathlib import Path
import click
from rich.console import Console

console = Console()

# Force UTF-8 on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Paths
HOME = Path.home()
DATA_DIR = HOME / 'data' / 'frp'
BIN_DIR = HOME / '.frp-tunnel' / 'bin'
SERVER_INI = DATA_DIR / 'frps.ini'
CLIENT_INI = DATA_DIR / 'frpc.ini'

DATA_DIR.mkdir(parents=True, exist_ok=True)
BIN_DIR.mkdir(parents=True, exist_ok=True)

def download_frp():
    """Download FRP binaries if not exists"""
    frps = BIN_DIR / ('frps.exe' if sys.platform == 'win32' else 'frps')
    frpc = BIN_DIR / ('frpc.exe' if sys.platform == 'win32' else 'frpc')
    
    if frps.exists() and frpc.exists():
        return
    
    console.print("📦 Downloading FRP binaries...")
    from .core.installer import install_binaries
    install_binaries()
    console.print("✅ Download complete")

def gen_token():
    """Generate a new token"""
    return f"frp_{secrets.token_hex(16)}"

def get_public_ip():
    """Get public IP"""
    try:
        import requests
        return requests.get('https://api.myip.com', timeout=3).json().get('ip', 'unknown')
    except:
        return 'unknown'

def is_running(name):
    """Check if process is running"""
    try:
        if sys.platform == 'win32':
            result = subprocess.run(['tasklist'], capture_output=True, text=True)
            return name in result.stdout
        else:
            result = subprocess.run(['pgrep', '-f', name], capture_output=True)
            return result.returncode == 0
    except:
        return False

@click.group()
@click.version_option()
def cli():
    """🚀 FRP Tunnel - Easy SSH tunneling"""
    pass

@cli.command()
def token():
    """Generate a new token"""
    new_token = gen_token()
    console.print(f"🔑 Generated token: [bold yellow]{new_token}[/bold yellow]")
    console.print("💡 Configure manually in server.ini")

@cli.command()
def version():
    """Show version information"""
    console.print("🚀 FRP Tunnel v1.0.9")
    console.print("📦 Simple SSH tunneling with FRP")
    
    # Check FRP binary version
    frps = BIN_DIR / ('frps.exe' if sys.platform == 'win32' else 'frps')
    if frps.exists():
        try:
            result = subprocess.run([str(frps), '--version'], 
                                  capture_output=True, text=True, timeout=2)
            if result.stdout:
                console.print(f"🔧 FRP: {result.stdout.strip()}")
        except:
            pass

@cli.command()
@click.option('-f', '--force', is_flag=True, help='Force restart if running')
@click.option('-r', '--restart', is_flag=True, help='Restart server')
def server(force, restart):
    """Start FRP server
    
    Examples:
      frp-tunnel server           # Start server (auto-gen token)
      frp-tunnel server -f        # Force restart
      frp-tunnel server -r        # Restart and show status
    """
    download_frp()
    
    # Check if running
    if is_running('frps'):
        if not force and not restart:
            console.print("⚠️  Server already running")
            show_status()
            return
        console.print("🔄 Stopping server...")
        stop_server()
    
    # Generate config if not exists
    if not SERVER_INI.exists():
        console.print("📝 Generating server config...")
        token = gen_token()
        config = f"""[common]
bind_port = 7000
token = {token}
dashboard_port = 7500
dashboard_user = admin
dashboard_pwd = admin
log_file = {DATA_DIR}/frps.log
log_level = info
authentication_method = token
"""
        SERVER_INI.write_text(config)
        console.print(f"🔑 Token: [bold yellow]{token}[/bold yellow]")
    
    # Start server
    console.print("🚀 Starting server...")
    frps = BIN_DIR / ('frps.exe' if sys.platform == 'win32' else 'frps')
    
    if sys.platform == 'win32':
        subprocess.Popen([str(frps), '-c', str(SERVER_INI)], 
                        creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        subprocess.Popen([str(frps), '-c', str(SERVER_INI)],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    import time
    time.sleep(2)
    console.print("✅ Server started")
    show_status()

@cli.command()
@click.option('--server', required=True, help='Server address')
@click.option('--token', required=True, help='Authentication token')
@click.option('--port', required=True, type=int, help='Remote port to forward')
def client(server, token, port):
    """Start FRP client
    
    Examples:
      frp-tunnel client --server 1.2.3.4 --token xxx --port 6000
      
    Note: Configure additional ports in frpc.ini manually
    """
    download_frp()
    
    # Generate client config with single port
    config = f"""[common]
server_addr = {server}
server_port = 7000
token = {token}
log_file = {DATA_DIR}/frpc.log
log_level = info

[ssh_{port}]
type = tcp
local_ip = 127.0.0.1
local_port = 22
remote_port = {port}
"""
    
    CLIENT_INI.write_text(config)
    
    # Start client
    console.print(f"🚀 Starting client (port: {port})...")
    console.print(f"💡 Add more ports in: {CLIENT_INI}")
    frpc = BIN_DIR / ('frpc.exe' if sys.platform == 'win32' else 'frpc')
    
    if sys.platform == 'win32':
        subprocess.Popen([str(frpc), '-c', str(CLIENT_INI)],
                        creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        subprocess.Popen([str(frpc), '-c', str(CLIENT_INI)],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    import time
    time.sleep(2)
    console.print("✅ Client started")

@cli.command()
def stop():
    """Stop all FRP processes"""
    console.print("🛑 Stopping...")
    stop_server()
    stop_client()
    console.print("✅ Stopped")

def stop_server():
    """Stop server process"""
    if sys.platform == 'win32':
        subprocess.run(['taskkill', '/F', '/IM', 'frps.exe'], 
                      capture_output=True)
    else:
        subprocess.run(['pkill', '-9', 'frps'], capture_output=True)

def stop_client():
    """Stop client process"""
    if sys.platform == 'win32':
        subprocess.run(['taskkill', '/F', '/IM', 'frpc.exe'],
                      capture_output=True)
    else:
        subprocess.run(['pkill', '-9', 'frpc'], capture_output=True)

@cli.command()
def status():
    """Show tunnel status"""
    show_status()

def show_status():
    """Display status"""
    console.print("\n📊 Tunnel Status")
    
    # Server status
    if is_running('frps'):
        console.print("🖥️  Server: [green]Running[/green]")
        ip = get_public_ip()
        if ip != 'unknown':
            console.print(f"   🌐 Public IP: [cyan]{ip}[/cyan]")
        console.print(f"   📄 Config: [cyan]{SERVER_INI}[/cyan]")
        
        # Read token from config
        if SERVER_INI.exists():
            config = configparser.ConfigParser()
            config.read(SERVER_INI)
            if 'common' in config and 'token' in config['common']:
                token = config['common']['token']
                console.print(f"   🔑 Token: [yellow]{token}[/yellow]")
    else:
        console.print("🖥️  Server: [red]Stopped[/red]")
    
    # Client status
    if is_running('frpc'):
        console.print("📱 Client: [green]Connected[/green]")
        console.print(f"   📄 Config: [cyan]{CLIENT_INI}[/cyan]")
    else:
        console.print("📱 Client: [red]Disconnected[/red]")
    
    console.print()

def main():
    cli()

if __name__ == '__main__':
    main()
