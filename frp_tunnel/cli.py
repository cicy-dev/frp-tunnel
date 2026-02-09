#!/usr/bin/env python3
"""FRP Tunnel CLI - Simple SSH tunneling"""

import sys
import os
import subprocess
import secrets
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
SERVER_YAML = DATA_DIR / 'frps.yaml'
CLIENT_YAML = DATA_DIR / 'frpc.yaml'

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
    console.print("💡 Configure manually in frps.yaml")

@cli.command('frpc', context_settings={'ignore_unknown_options': True, 'allow_interspersed_args': False})
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def forward_frpc(args):
    """Forward command to frpc binary
    
    Examples:
      ft frpc -c ~/data/frp/frpc.yaml
      ft frpc reload -c ~/data/frp/frpc.yaml
      ft frpc status -c ~/data/frp/frpc.yaml
    """
    download_frp()
    frpc_bin = BIN_DIR / ('frpc.exe' if sys.platform == 'win32' else 'frpc')
    
    # Forward to frpc with all args
    result = subprocess.run([str(frpc_bin)] + list(args))
    sys.exit(result.returncode)

@cli.command('frps', context_settings={'ignore_unknown_options': True, 'allow_interspersed_args': False})
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def forward_frps(args):
    """Forward command to frps binary
    
    Examples:
      ft frps -c ~/data/frp/frps.yaml
    """
    download_frp()
    frps_bin = BIN_DIR / ('frps.exe' if sys.platform == 'win32' else 'frps')
    
    # Forward to frps with all args
    result = subprocess.run([str(frps_bin)] + list(args))
    sys.exit(result.returncode)

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
      ft server           # Start server (auto-gen token)
      ft server -f        # Force restart
      ft server -r        # Restart and show status
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
    if not SERVER_YAML.exists():
        console.print("📝 Generating server config...")
        token = gen_token()
        import yaml
        config = {
            'bindPort': 7000,
            'auth': {'token': token},
            'webServer': {
                'addr': '0.0.0.0',
                'port': 7500,
                'user': 'admin',
                'password': 'admin'
            },
            'log': {
                'to': str(DATA_DIR / 'frps.log'),
                'level': 'info'
            }
        }
        with open(SERVER_YAML, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        console.print(f"🔑 Token: [bold yellow]{token}[/bold yellow]")
    
    # Start server
    console.print("🚀 Starting server...")
    frps = BIN_DIR / ('frps.exe' if sys.platform == 'win32' else 'frps')
    
    if sys.platform == 'win32':
        subprocess.Popen([str(frps), '-c', str(SERVER_YAML)], 
                        creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        subprocess.Popen([str(frps), '-c', str(SERVER_YAML)],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    import time
    time.sleep(2)
    console.print("✅ Server started")

@cli.command()
@click.option('--server', required=True, help='Server address')
@click.option('--token', required=True, help='Authentication token')
@click.option('--port', multiple=True, type=int, required=True, help='Remote port(s)')
def client(server, token, port):
    """Generate client config (YAML format)
    
    Examples:
      # Generate config
      ft client --server 1.2.3.4 --token xxx --port 6003 --port 6004
      
      # Start client
      ft frpc -c ~/data/frp/frpc.yaml
      
      # Hot reload after config change
      ft frpc reload -c ~/data/frp/frpc.yaml
    """
    download_frp()
    
    config_file = _generate_client_config(server, token, list(port))
    
    ports_str = ", ".join(str(p) for p in port)
    console.print(f"✅ Config generated: {config_file}")
    console.print(f"📝 Ports: {ports_str}")
    console.print(f"\n🚀 Start client:")
    console.print(f"   ft frpc -c {config_file}")
    console.print(f"\n🔄 Hot reload:")
    console.print(f"   ft frpc reload -c {config_file}")

@cli.command('client-add-port')
@click.argument('ports', nargs=-1, type=int, required=True)
def client_add_port(ports):
    """Add port(s) to existing client config
    
    Examples:
      ft client-add-port 6005
      ft client-add-port 6005 6006 6007
      
      # Then hot reload
      ft frpc reload -c ~/data/frp/frpc.yaml
    """
    if not CLIENT_YAML.exists():
        console.print("❌ Error: No existing config. Run 'frp-tunnel client' first", style="red")
        return
    
    # Read existing config
    import yaml
    with open(CLIENT_YAML) as f:
        config = yaml.safe_load(f)
    
    server = config['serverAddr']
    token = config['auth']['token']
    existing_ports = [p['remotePort'] for p in config['proxies']]
    
    # Add new ports
    all_ports = sorted(list(set(existing_ports + list(ports))))
    
    # Regenerate config
    config_file = _generate_client_config(server, token, all_ports)
    
    ports_str = ", ".join(str(p) for p in all_ports)
    console.print(f"✅ Added ports. Config updated: {config_file}")
    console.print(f"📝 Active ports: {ports_str}")
    console.print(f"\n🔄 Hot reload:")
    console.print(f"   ft frpc reload -c {config_file}")

@cli.command('client-remove-port')
@click.argument('ports', nargs=-1, type=int, required=True)
def client_remove_port(ports):
    """Remove port(s) from existing client config
    
    Examples:
      ft client-remove-port 6005
      ft client-remove-port 6005 6006
      
      # Then hot reload
      ft frpc reload -c ~/data/frp/frpc.yaml
    """
    if not CLIENT_YAML.exists():
        console.print("❌ Error: No existing config", style="red")
        return
    
    # Read existing config
    import yaml
    with open(CLIENT_YAML) as f:
        config = yaml.safe_load(f)
    
    server = config['serverAddr']
    token = config['auth']['token']
    existing_ports = [p['remotePort'] for p in config['proxies']]
    
    # Remove ports
    all_ports = sorted(list(set(existing_ports) - set(ports)))
    
    if not all_ports:
        console.print("❌ Error: Cannot remove all ports", style="red")
        return
    
    # Regenerate config
    config_file = _generate_client_config(server, token, all_ports)
    
    ports_str = ", ".join(str(p) for p in all_ports)
    console.print(f"✅ Removed ports. Config updated: {config_file}")
    console.print(f"📝 Active ports: {ports_str}")
    console.print(f"\n🔄 Hot reload:")
    console.print(f"   ft frpc reload -c {config_file}")

def _generate_client_config(server, token, ports):
    """Generate client config file in YAML format"""
    import yaml
    
    config = {
        'serverAddr': server,
        'serverPort': 7000,
        'auth': {'token': token},
        'log': {
            'to': str(DATA_DIR / 'frpc.log'),
            'level': 'info'
        },
        'webServer': {
            'addr': '127.0.0.1',
            'port': 7400
        },
        'proxies': []
    }
    
    # Add SSH proxy (first port)
    config['proxies'].append({
        'name': f'ssh_{ports[0]}',
        'type': 'tcp',
        'localIP': '127.0.0.1',
        'localPort': 22,
        'remotePort': ports[0]
    })
    
    # Add additional proxies
    for p in ports[1:]:
        service_name = "rdp" if "04" in str(p) or p == 3389 else "service"
        local_port = 3389 if service_name == "rdp" else p
        config['proxies'].append({
            'name': f'{service_name}_{p}',
            'type': 'tcp',
            'localIP': '127.0.0.1',
            'localPort': local_port,
            'remotePort': p
        })
    
    # Write YAML config
    with open(CLIENT_YAML, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    return CLIENT_YAML

def _start_frpc(config_file):
    """Start frpc process"""
    frpc = BIN_DIR / ('frpc.exe' if sys.platform == 'win32' else 'frpc')
    
    if sys.platform == 'win32':
        subprocess.Popen([str(frpc), '-c', str(config_file)],
                        creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        subprocess.Popen([str(frpc), '-c', str(config_file)],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    import time
    time.sleep(2)

def _reload_frpc(config_file):
    """Reload frpc configuration without restart"""
    frpc = BIN_DIR / ('frpc.exe' if sys.platform == 'win32' else 'frpc')
    
    try:
        result = subprocess.run([str(frpc), 'reload', '-c', str(config_file)],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return True
        else:
            # Reload failed, fallback to restart
            return False
    except:
        return False

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
        console.print(f"   📄 Config: [cyan]{SERVER_YAML}[/cyan]")
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
        
        console.print(f"   📄 Config: [cyan]{CLIENT_YAML}[/cyan]")
        log_file = DATA_DIR / 'frpc.log'
        if log_file.exists():
            console.print(f"   📋 Log: [cyan]{log_file}[/cyan]")
        frpc_bin = BIN_DIR / ('frpc.exe' if sys.platform == 'win32' else 'frpc')
        if frpc_bin.exists():
            console.print(f"   🔧 Binary: [cyan]{frpc_bin}[/cyan]")
    else:
        console.print("📱 Client: [red]Disconnected[/red]")
        
        # Show config if exists
        if CLIENT_YAML.exists():
            import yaml
            with open(CLIENT_YAML) as f:
                config = yaml.safe_load(f)
            console.print(f"   📄 Config: [cyan]{CLIENT_YAML}[/cyan]")
            console.print(f"   🌐 Server: [cyan]{config.get('serverAddr', 'N/A')}:{config.get('serverPort', 7000)}[/cyan]")
            ports = [p['remotePort'] for p in config.get('proxies', [])]
            if ports:
                console.print(f"   🔌 Ports: [cyan]{', '.join(map(str, ports))}[/cyan]")
    console.print()

def main():
    cli()

if __name__ == '__main__':
    main()
