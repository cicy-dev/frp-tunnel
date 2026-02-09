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

@cli.command()
@click.option('--server', help='Server address (required for first time)')
@click.option('--token', help='Authentication token (required for first time)')
@click.option('--port', multiple=True, type=int, help='Remote port(s) to add')
@click.option('--remove', multiple=True, type=int, help='Remote port(s) to remove')
def client(server, token, port, remove):
    """Start FRP client
    
    Examples:
      # First time - specify server and token
      frp-tunnel client --server 1.2.3.4 --token xxx --port 6003 --port 6004
      
      # Add more ports
      frp-tunnel client --port 6005
      
      # Remove ports
      frp-tunnel client --remove 6005
      
    Note: Configure additional ports in frpc.ini manually
    """
    download_frp()
    
    # Check if config exists
    existing_config = {}
    if CLIENT_INI.exists():
        import configparser
        parser = configparser.ConfigParser()
        parser.read(CLIENT_INI)
        if 'common' in parser:
            existing_config = {
                'server': parser['common'].get('server_addr'),
                'token': parser['common'].get('token'),
                'ports': [int(s.split('_')[1]) for s in parser.sections() if s != 'common']
            }
    
    # Use existing config if not provided
    if not server and existing_config.get('server'):
        server = existing_config['server']
    if not token and existing_config.get('token'):
        token = existing_config['token']
    
    # Validate required params
    if not server or not token:
        console.print("❌ Error: --server and --token required for first time setup", style="red")
        return
    
    if not port and not remove:
        console.print("❌ Error: Specify --port to add or --remove to remove", style="red")
        return
    
    # Merge with existing ports
    all_ports = set(existing_config.get('ports', []))
    all_ports.update(port)
    all_ports -= set(remove)
    
    if not all_ports:
        console.print("❌ Error: At least one port must remain", style="red")
        return
    
    all_ports = sorted(list(all_ports))
    
    # Generate client config with multiple ports
    config_lines = [
        "[common]",
        f"server_addr = {server}",
        "server_port = 7000",
        f"token = {token}",
        f"log_file = {DATA_DIR}/frpc.log",
        "log_level = info",
        "login_fail_exit = false",
        ""
    ]
    
    # Add SSH port (first port)
    config_lines.extend([
        f"[ssh_{all_ports[0]}]",
        "type = tcp",
        "local_ip = 127.0.0.1",
        "local_port = 22",
        f"remote_port = {all_ports[0]}",
        ""
    ])
    
    # Add additional ports (RDP, etc.)
    for p in all_ports[1:]:
        service_name = "rdp" if "04" in str(p) or p == 3389 else "service"
        local_port = 3389 if service_name == "rdp" else p
        config_lines.extend([
            f"[{service_name}_{p}]",
            "type = tcp",
            "local_ip = 127.0.0.1",
            f"local_port = {local_port}",
            f"remote_port = {p}",
            ""
        ])
    
    config = "\n".join(config_lines)
    CLIENT_INI.write_text(config)
    
    # Start client
    ports_str = ", ".join(str(p) for p in all_ports)
    if remove:
        console.print(f"🗑️  Removed ports: {', '.join(str(p) for p in remove)}")
    console.print(f"🚀 Starting client (ports: {ports_str})...")
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

@cli.command('client-add-port')
@click.argument('ports', nargs=-1, type=int, required=True)
def client_add_port(ports):
    """Add port(s) to existing client config
    
    Examples:
      frp-tunnel client-add-port 6005
      frp-tunnel client-add-port 6005 6006 6007
    """
    if not CLIENT_INI.exists():
        console.print("❌ Error: No existing config. Run 'frp-tunnel client' first", style="red")
        return
    
    # Read existing config
    import configparser
    parser = configparser.ConfigParser()
    parser.read(CLIENT_INI)
    
    server = parser['common']['server_addr']
    token = parser['common']['token']
    existing_ports = [int(s.split('_')[1]) for s in parser.sections() if s != 'common']
    
    # Add new ports
    all_ports = sorted(list(set(existing_ports + list(ports))))
    
    # Stop existing client
    stop_client()
    import time
    time.sleep(1)
    
    # Generate new config
    _generate_client_config(server, token, all_ports)
    _start_frpc()
    
    ports_str = ", ".join(str(p) for p in all_ports)
    console.print(f"✅ Added ports. Active: {ports_str}")

@cli.command('client-remove-port')
@click.argument('ports', nargs=-1, type=int, required=True)
def client_remove_port(ports):
    """Remove port(s) from existing client config
    
    Examples:
      frp-tunnel client-remove-port 6005
      frp-tunnel client-remove-port 6005 6006
    """
    if not CLIENT_INI.exists():
        console.print("❌ Error: No existing config", style="red")
        return
    
    # Read existing config
    import configparser
    parser = configparser.ConfigParser()
    parser.read(CLIENT_INI)
    
    server = parser['common']['server_addr']
    token = parser['common']['token']
    existing_ports = [int(s.split('_')[1]) for s in parser.sections() if s != 'common']
    
    # Remove ports
    all_ports = sorted(list(set(existing_ports) - set(ports)))
    
    if not all_ports:
        console.print("❌ Error: Cannot remove all ports", style="red")
        return
    
    # Stop existing client
    stop_client()
    import time
    time.sleep(1)
    
    # Generate new config
    _generate_client_config(server, token, all_ports)
    _start_frpc()
    
    ports_str = ", ".join(str(p) for p in all_ports)
    console.print(f"✅ Removed ports. Active: {ports_str}")

def _generate_client_config(server, token, ports):
    """Generate client config file"""
    config_lines = [
        "[common]",
        f"server_addr = {server}",
        "server_port = 7000",
        f"token = {token}",
        f"log_file = {DATA_DIR}/frpc.log",
        "log_level = info",
        "login_fail_exit = false",
        ""
    ]
    
    # Add SSH port (first port)
    config_lines.extend([
        f"[ssh_{ports[0]}]",
        "type = tcp",
        "local_ip = 127.0.0.1",
        "local_port = 22",
        f"remote_port = {ports[0]}",
        ""
    ])
    
    # Add additional ports
    for p in ports[1:]:
        service_name = "rdp" if "04" in str(p) or p == 3389 else "service"
        local_port = 3389 if service_name == "rdp" else p
        config_lines.extend([
            f"[{service_name}_{p}]",
            "type = tcp",
            "local_ip = 127.0.0.1",
            f"local_port = {local_port}",
            f"remote_port = {p}",
            ""
        ])
    
    CLIENT_INI.write_text("\n".join(config_lines))

def _start_frpc():
    """Start frpc process"""
    frpc = BIN_DIR / ('frpc.exe' if sys.platform == 'win32' else 'frpc')
    
    if sys.platform == 'win32':
        subprocess.Popen([str(frpc), '-c', str(CLIENT_INI)],
                        creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        subprocess.Popen([str(frpc), '-c', str(CLIENT_INI)],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    import time
    time.sleep(2)

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

@cli.command('server-status')
def server_status():
    """Show server status"""
    console.print("\n📊 Server Status")
    if is_running('frps'):
        console.print("🖥️  Server: [green]Running[/green]")
        ip = get_public_ip()
        if ip != 'unknown':
            console.print(f"   🌐 Public IP: [cyan]{ip}[/cyan]")
        console.print(f"   📄 Config: [cyan]{SERVER_INI}[/cyan]")
        log_file = DATA_DIR / 'frps.log'
        if log_file.exists():
            console.print(f"   📋 Log: [cyan]{log_file}[/cyan]")
        frps_bin = BIN_DIR / ('frps.exe' if sys.platform == 'win32' else 'frps')
        if frps_bin.exists():
            console.print(f"   🔧 Binary: [cyan]{frps_bin}[/cyan]")
        
        # Show active clients via API
        try:
            import requests
            response = requests.get('http://localhost:7500/api/proxy/tcp', 
                                  auth=('admin', 'admin'), timeout=2)
            if response.status_code == 200:
                data = response.json()
                proxies = data.get('proxies', [])
                
                # Filter online proxies only
                online_proxies = [p for p in proxies if p.get('status') != 'offline']
                
                if online_proxies:
                    console.print(f"   👥 Active clients: [green]{len(online_proxies)}[/green]")
                    for proxy in online_proxies:
                        name = proxy.get('name', 'unknown')
                        conf = proxy.get('conf', {}) or {}
                        port = conf.get('remotePort', 'unknown')
                        version = proxy.get('clientVersion', 'unknown')
                        conns = proxy.get('curConns', 0)
                        console.print(f"      • {name}: port {port} (v{version}, {conns} conns)")
                else:
                    console.print(f"   👥 Active clients: [yellow]0[/yellow]")
            else:
                console.print(f"   👥 Active clients: [yellow]API unavailable[/yellow]")
        except Exception as e:
            console.print(f"   👥 Active clients: [yellow]Unknown[/yellow]")
    else:
        console.print("🖥️  Server: [red]Stopped[/red]")
    console.print()

@cli.command('client-status')
def client_status():
    """Show client status"""
    console.print("\n📊 Client Status")
    if is_running('frpc'):
        try:
            if sys.platform == 'win32':
                result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq frpc.exe'], 
                                      capture_output=True, text=True)
                count = result.stdout.count('frpc.exe')
            else:
                result = subprocess.run(['pgrep', '-c', 'frpc'], capture_output=True, text=True)
                count = int(result.stdout.strip()) if result.returncode == 0 else 1
        except:
            count = 1
        
        if count > 1:
            console.print(f"📱 Clients: [green]{count} Connected[/green]")
        else:
            console.print("📱 Client: [green]Connected[/green]")
        
        console.print(f"   📄 Config: [cyan]{CLIENT_INI}[/cyan]")
        log_file = DATA_DIR / 'frpc.log'
        if log_file.exists():
            console.print(f"   📋 Log: [cyan]{log_file}[/cyan]")
        frpc_bin = BIN_DIR / ('frpc.exe' if sys.platform == 'win32' else 'frpc')
        if frpc_bin.exists():
            console.print(f"   🔧 Binary: [cyan]{frpc_bin}[/cyan]")
    else:
        console.print("📱 Client: [red]Disconnected[/red]")
    console.print()

def main():
    cli()

if __name__ == '__main__':
    main()
