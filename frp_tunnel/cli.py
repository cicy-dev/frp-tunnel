#!/usr/bin/env python3
"""FRP Tunnel CLI - Simple SSH tunneling"""

import sys
import os
import subprocess
import secrets
from pathlib import Path
import click
from rich.console import Console
from . import __version__

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

@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option()
def cli():
    """🚀 FRP Tunnel - Easy SSH tunneling with FRP
    
    Quick Start:
      1. Server: ft server
      2. Client: ft client --server <IP> --token <TOKEN> --port 6022
      3. Start:  ft frpc -c ~/data/frp/frpc.yaml
      4. Status: ft server-status / ft client-status
    """
    pass

@cli.command()
def token():
    """Generate authentication token for server"""
    new_token = gen_token()
    console.print(f"🔑 Generated token: [bold yellow]{new_token}[/bold yellow]")
    console.print("💡 Use this token when configuring clients")

@cli.command('frpc', context_settings={'ignore_unknown_options': True, 'allow_interspersed_args': False})
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def forward_frpc(args):
    """Start/control FRP client (runs in background)
    
    Examples:
      ft frpc -c ~/data/frp/frpc.yaml          # Start client
      ft frpc reload -c ~/data/frp/frpc.yaml   # Hot reload config
      ft frpc stop -c ~/data/frp/frpc.yaml     # Stop client
    """
    download_frp()
    frpc_bin = BIN_DIR / ('frpc.exe' if sys.platform == 'win32' else 'frpc')
    
    # Run frpc in background
    if sys.platform == 'win32':
        subprocess.Popen([str(frpc_bin)] + list(args),
                         creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        subprocess.Popen([str(frpc_bin)] + list(args),
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

@cli.command('frps', context_settings={'ignore_unknown_options': True, 'allow_interspersed_args': False})
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def forward_frps(args):
    """Start/control FRP server (runs in background)
    
    Examples:
      ft frps -c ~/data/frp/frps.yaml          # Start server
      ft frps reload -c ~/data/frp/frps.yaml   # Hot reload config
      ft frps stop -c ~/data/frp/frps.yaml     # Stop server
    """
    download_frp()
    frps_bin = BIN_DIR / ('frps.exe' if sys.platform == 'win32' else 'frps')
    
    # Run frps in background
    if sys.platform == 'win32':
        subprocess.Popen([str(frps_bin)] + list(args),
                         creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        subprocess.Popen([str(frps_bin)] + list(args),
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

@cli.command()
def version():
    """Show version information"""
    console.print(f"🚀 FRP Tunnel v{__version__}")
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
@click.option('-f', '--force', is_flag=True, help='Force restart if already running')
def server(force):
    """Start FRP server with auto-generated config
    
    The server will:
      - Auto-generate authentication token
      - Listen on port 7000 for clients
      - Enable web dashboard on port 7500
      - Create config at ~/data/frp/frps.yaml
    
    Examples:
      ft server           # Start server
      ft server -f        # Force restart if running
      ft server-status    # Check server status
    """
    download_frp()
    
    # Check if running
    if is_running('frps'):
        if not force:
            console.print("⚠️  Server already running. Use -f to force restart")
            return
        console.print("🔄 Stopping server...")
        stop_server()
    
    # Generate config if not exists
    import yaml
    if not SERVER_YAML.exists():
        console.print("📝 Generating server config...")
        token = gen_token()
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
    
    # Read token from config
    with open(SERVER_YAML) as f:
        config = yaml.safe_load(f)
        token = config['auth']['token']
    
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
@click.option('--server', required=True, help='Server IP address')
@click.option('--token', required=True, help='Authentication token from server')
@click.option('--port', multiple=True, type=int, required=True, help='Remote port(s) to expose')
def client(server, token, port):
    """Generate client config to connect to FRP server
    
    This creates a config file at ~/data/frp/frpc.yaml that:
      - Connects to the specified server
      - Exposes local SSH (port 22) to remote port(s)
      - Supports multiple ports for additional services
    
    Examples:
      # Single port (SSH only)
      ft client --server 1.2.3.4 --token xxx --port 6022
      
      # Multiple ports (SSH + RDP)
      ft client --server 1.2.3.4 --token xxx --port 6022 --port 3389
      
      # After config generation, start client:
      ft frpc -c ~/data/frp/frpc.yaml
      
      # Hot reload after config changes:
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

@cli.command('service')
@click.argument('action', type=click.Choice(['install', 'uninstall', 'status']))
def service_cmd(action):
    """Manage FRP server as systemd service (Linux/Ubuntu/Debian only)
    
    Examples:
      ft service install    # Install frps as systemd service
      ft service uninstall  # Remove systemd service
      ft service status     # Check service status
    """
    if sys.platform == 'win32':
        console.print("❌ Service management only supported on Linux/macOS")
        return
    
    if action == 'install':
        frps_bin = BIN_DIR / 'frps'
        if not frps_bin.exists():
            console.print("❌ FRP binary not found. Run 'ft server' first.")
            return
        
        service_content = f"""[Unit]
Description=FRP Tunnel Server
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'root')}
WorkingDirectory={HOME}
ExecStart={frps_bin} -c {SERVER_YAML}
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
        service_file = Path('/etc/systemd/system/frp-server.service')
        try:
            subprocess.run(['sudo', 'tee', str(service_file)], input=service_content, text=True, check=True)
            subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
            subprocess.run(['sudo', 'systemctl', 'enable', 'frp-server'], check=True)
            subprocess.run(['sudo', 'systemctl', 'start', 'frp-server'], check=True)
            console.print("✅ FRP server installed as systemd service")
            console.print(f"   Binary: {frps_bin}")
            console.print(f"   Config: {SERVER_YAML}")
            console.print("   Start: sudo systemctl start frp-server")
            console.print("   Stop: sudo systemctl stop frp-server")
            console.print("   Status: sudo systemctl status frp-server")
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Failed to install service: {e}")
    
    elif action == 'uninstall':
        try:
            subprocess.run(['sudo', 'systemctl', 'stop', 'frp-server'], check=False)
            subprocess.run(['sudo', 'systemctl', 'disable', 'frp-server'], check=False)
            subprocess.run(['sudo', 'rm', '/etc/systemd/system/frp-server.service'], check=True)
            subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
            console.print("✅ FRP server service removed")
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Failed to uninstall service: {e}")
    
    elif action == 'status':
        try:
            result = subprocess.run(['sudo', 'systemctl', 'status', 'frp-server'], 
                                  capture_output=True, text=True)
            console.print(result.stdout)
        except subprocess.CalledProcessError:
            console.print("❌ Service not installed or not running")

@cli.command('client-add-port')
@click.argument('ports', nargs=-1, type=int, required=True)
def client_add_port(ports):
    """Add port(s) to existing client config
    
    Examples:
      ft client-add-port 8080              # Add single port
      ft client-add-port 8080 9000 9001    # Add multiple ports
      
      # Then hot reload to apply changes:
      ft frpc reload -c ~/data/frp/frpc.yaml
    """
    if not CLIENT_YAML.exists():
        console.print("❌ Error: No existing config. Run 'ft client' first", style="red")
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
      ft client-remove-port 8080           # Remove single port
      ft client-remove-port 8080 9000      # Remove multiple ports
      
      # Then hot reload to apply changes:
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
        is_rdp = (p == 3389)
        service_name = "rdp" if is_rdp else "service"
        local_port = 3389 if is_rdp else p
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
    """Stop all FRP processes (server and client)
    
    Examples:
      ft stop              # Stop all FRP processes
      ft server-status     # Verify server stopped
      ft client-status     # Verify client stopped
    """
    console.print("🛑 Stopping all FRP processes...")
    stop_server()
    stop_client()
    console.print("✅ All FRP processes stopped")

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
    """Show detailed server status and connected clients
    
    Displays:
      - Server running status
      - Public IP address
      - Configuration file location
      - Active client connections
      - SSH key paths
      - Example client connection command
    
    Examples:
      ft server-status     # Check server status
    """
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
        
        # Show SSH authorized_keys path
        import os
        ssh_pub_key = os.path.expanduser('~/.ssh/id_rsa.pub')
        if os.path.exists(ssh_pub_key):
            console.print(f"   🔑 SSH Keys: [cyan]{ssh_pub_key}[/cyan]")
        
        # Show active clients via API
        try:
            import requests
            response = requests.get('http://localhost:7500/api/proxy/tcp', timeout=2)
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
                        client_ip = proxy.get('addr', 'unknown')
                        console.print(f"      • {name}: {ip}:{port} ← {client_ip} (v{version}, {conns} conns)")
                else:
                    console.print(f"   👥 Active clients: [yellow]0[/yellow]")
            else:
                console.print(f"   👥 Active clients: [yellow]API unavailable[/yellow]")
        except Exception as e:
            console.print(f"   👥 Active clients: [yellow]Unknown[/yellow]")
        
        # Show example command to start client
        import yaml
        if SERVER_YAML.exists():
            with open(SERVER_YAML) as f:
                config = yaml.safe_load(f)
            token = config.get('auth', {}).get('token', 'N/A')
            masked_token = token[:8] + '*' * (len(token) - 16) + token[-8:] if len(token) > 16 else '***'
            console.print(f"\n💡 Start client (IP):")
            console.print(f"   [yellow]ft client --server {ip} --token {masked_token} --port <PORT>[/yellow]")
            console.print(f"\n💡 Start client (Domain):")
            console.print(f"   [yellow]ft client --server gcp-hk-1001.cicy.de5.net --token {masked_token} --port <PORT>[/yellow]")
    else:
        console.print("🖥️  Server: [red]Stopped[/red]")
    console.print()

@cli.command('client-status')
def client_status():
    """Show detailed client status and configuration
    
    Displays:
      - Client connection status
      - Server address and port
      - Exposed ports
      - Configuration file location
      - SSH authorized_keys path (platform-specific)
    
    Examples:
      ft client-status     # Check client status
    """
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
        
        # Show server public IP
        if CLIENT_YAML.exists():
            import yaml
            with open(CLIENT_YAML) as f:
                config = yaml.safe_load(f)
            server_addr = config.get('serverAddr', 'N/A')
            server_port = config.get('serverPort', 7000)
            console.print(f"   🌐 Server: [cyan]{server_addr}:{server_port}[/cyan]")
            
            # Show configured ports
            proxies = config.get('proxies', [])
            if proxies:
                ports = [p.get('remotePort', 'N/A') for p in proxies]
                console.print(f"   🔌 Ports: [cyan]{', '.join(map(str, ports))}[/cyan]")
        
        console.print(f"   📄 Config: [cyan]{CLIENT_YAML}[/cyan]")
        log_file = DATA_DIR / 'frpc.log'
        if log_file.exists():
            console.print(f"   📋 Log: [cyan]{log_file}[/cyan]")
        frpc_bin = BIN_DIR / ('frpc.exe' if sys.platform == 'win32' else 'frpc')
        if frpc_bin.exists():
            console.print(f"   🔧 Binary: [cyan]{frpc_bin}[/cyan]")
        
        # Show SSH key path (Windows Administrator vs regular users)
        if sys.platform == 'win32':
            import getpass
            username = getpass.getuser()
            # Check if user is Administrator
            try:
                result = subprocess.run(['net', 'localgroup', 'Administrators'], 
                                      capture_output=True, text=True)
                is_admin = username.lower() in result.stdout.lower()
            except:
                is_admin = False
            
            if is_admin:
                key_path = r'C:\ProgramData\ssh\administrators_authorized_keys'
            else:
                key_path = f'C:\\Users\\{username}\\.ssh\\authorized_keys'
        else:
            from pathlib import Path
            key_path = str(Path.home() / '.ssh' / 'authorized_keys')
        
        console.print(f"   🔑 SSH Keys: [cyan]{key_path}[/cyan]")
    else:
        console.print("📱 Client: [red]Disconnected[/red]")
        
        # Show config if exists
        if CLIENT_YAML.exists():
            import yaml
            with open(CLIENT_YAML) as f:
                config = yaml.safe_load(f)
            server_addr = config.get('serverAddr', 'N/A')
            server_port = config.get('serverPort', 7000)
            console.print(f"   📄 Config: [cyan]{CLIENT_YAML}[/cyan]")
            console.print(f"   🌐 Server: [cyan]{server_addr}:{server_port}[/cyan]")
            ports = [p.get('remotePort', 'N/A') for p in config.get('proxies', [])]
            if ports:
                console.print(f"   🔌 Ports: [cyan]{', '.join(map(str, ports))}[/cyan]")
    console.print()

def main():
    cli()

if __name__ == '__main__':
    main()
