#!/usr/bin/env python3
"""
FRP Tunnel CLI - Easy SSH tunneling with FRP
"""

import sys
import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from .core.installer import install_binaries
from .core.tunnel import TunnelManager
from .core.platform import detect_platform, is_colab
from .core.config import ConfigManager

# Force UTF-8 encoding on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

console = Console()
tunnel_manager = TunnelManager()
config_manager = ConfigManager()

@click.group()
@click.version_option()
def cli():
    """🚀 FRP Tunnel - Easy SSH tunneling with FRP"""
    pass

@cli.command()
@click.option('--mode', type=click.Choice(['server', 'client', 'colab', 'auto']), default='auto', help='Setup mode')
@click.option('--server', help='Server address (for client mode)')
@click.option('--token', help='Authentication token')
@click.option('--port', default=6001, help='Remote port')
@click.option('--user', default='colab', help='SSH username')
def setup(mode, server, token, port, user):
    """Interactive setup wizard"""
    console.print(Panel.fit("🚀 FRP Tunnel Setup", style="bold blue"))
    
    # Auto-detect mode if not specified
    if mode == 'auto':
        if is_colab():
            mode = 'colab'
            console.print("🔬 Detected Google Colab environment")
        else:
            mode = click.prompt('Setup mode', type=click.Choice(['server', 'client']))
    
    if mode == 'server':
        setup_server()
    elif mode in ['client', 'colab']:
        setup_client(mode, server, token, port, user)

def setup_server():
    """Setup FRP server"""
    console.print("🖥️  Setting up FRP server...")
    
    port = click.prompt('Server port', default=7000, type=int)
    
    # Check if config exists and get existing token
    existing_config = config_manager.get_server_config()
    existing_token = existing_config.get('token', '')
    
    if existing_token:
        console.print(f"🔑 Found existing token: [bold yellow]{existing_token}[/bold yellow]")
        use_existing = click.confirm('Use existing token?', default=True)
        if use_existing:
            token = existing_token
        else:
            token = click.prompt('Authentication token (empty to generate)', default='', show_default=False)
            if not token:
                import secrets
                token = f"frp_{secrets.token_hex(16)}"
                console.print(f"🔑 Generated token: [bold yellow]{token}[/bold yellow]")
    else:
        token = click.prompt('Authentication token (empty to generate)', default='', show_default=False)
        if not token:
            import secrets
            token = f"frp_{secrets.token_hex(16)}"
            console.print(f"🔑 Generated token: [bold yellow]{token}[/bold yellow]")
    
    # Install server binary
    with console.status("📦 Installing FRP server..."):
        install_binaries('server')
    
    # Create configuration
    config = {
        'bind_port': port,
        'token': token
    }
    config_manager.create_server_config(config)
    
    # Start server
    if click.confirm('Start server now?', default=True):
        tunnel_manager.start_server(config)
        console.print("✅ Server started successfully!")
        console.print(f"🔑 Share this token with clients: [bold]{token}[/bold]")

def setup_client(mode, server, token, port, user):
    """Setup FRP client"""
    console.print(f"📱 Setting up FRP client ({mode})...")
    
    # Get configuration
    if not server:
        server = click.prompt('Server address')
    if not token:
        token = click.prompt('Authentication token')
    
    # Install client binary
    with console.status("📦 Installing FRP client..."):
        install_binaries('client')
    
    # Create configuration
    config = {
        'server_addr': server,
        'server_port': 7000,
        'token': token,
        'remote_port': port,
        'username': user
    }
    config_manager.create_client_config(config)
    
    # Setup SSH for Colab
    if mode == 'colab':
        with console.status("🔧 Setting up SSH..."):
            tunnel_manager.setup_colab_ssh(user)
    
    # Start client
    tunnel_manager.start_client(config)
    console.print("✅ Client connected successfully!")
    console.print(f"🔗 SSH command: [bold]ssh -p {port} {user}@{server}[/bold]")

@cli.command()
@click.option('--server', required=True, help='Server address')
@click.option('--token', required=True, help='Authentication token')
@click.option('--port', default=6001, help='Remote port')
@click.option('--user', default='colab', help='SSH username')
def colab(server, token, port, user):
    """Quick setup for Google Colab"""
    console.print("🔬 Setting up Google Colab tunnel...")
    setup_client('colab', server, token, port, user)

@cli.command()
def status():
    """Show tunnel status"""
    console.print("📊 Tunnel Status")
    status_info = tunnel_manager.get_status()
    
    if status_info['server_running']:
        console.print("🖥️  Server: [green]Running[/green]")
    else:
        console.print("🖥️  Server: [red]Stopped[/red]")
    
    if status_info['client_running']:
        console.print("📱 Client: [green]Connected[/green]")
    else:
        console.print("📱 Client: [red]Disconnected[/red]")

@cli.command()
def stop():
    """Stop all tunnels"""
    console.print("🛑 Stopping tunnels...")
    tunnel_manager.stop_all()
    console.print("✅ All tunnels stopped")

@cli.command()
def logs():
    """View tunnel logs"""
    console.print("📝 Recent logs:")
    logs = tunnel_manager.get_logs()
    for log_line in logs:
        console.print(log_line)

@cli.command()
def install():
    """Install/update FRP binaries"""
    console.print("📦 Installing FRP binaries...")
    with console.status("Downloading..."):
        install_binaries()
    console.print("✅ Installation complete")

@cli.command()
@click.option('--component', type=click.Choice(['server', 'client', 'both']), required=True, help='Component to start')
@click.option('--server', help='Server address (for client mode)')
@click.option('--token', help='Authentication token')
@click.option('--port', type=int, default=6001, help='Remote port for SSH')
@click.option('--local-port', type=int, default=22, help='Local SSH port')
def start(component, server, token, port, local_port):
    """Start FRP server or client"""
    if component in ['server', 'both']:
        config = config_manager.get_server_config()
        
        # Override with command line args if provided
        if token and config:
            if 'common' not in config:
                config['common'] = {}
            config['common']['token'] = token
        
        if not config:
            console.print("❌ No server configuration found. Run 'frp-tunnel setup server' first.")
            return
        
        if tunnel_manager.start_server(config):
            console.print("✅ Server started successfully!")
        else:
            console.print("❌ Failed to start server")
    
    if component in ['client', 'both']:
        config = config_manager.get_client_config()
        
        # Override with command line args if provided
        if server or token or port != 6001 or local_port != 22:
            if not config:
                config = {
                    'common': {
                        'server_port': 7000
                    },
                    'ssh': {
                        'type': 'tcp',
                        'local_ip': '127.0.0.1',
                        'local_port': local_port,
                        'remote_port': port
                    }
                }
            else:
                if 'common' not in config:
                    config['common'] = {}
                if 'ssh' not in config:
                    config['ssh'] = {'type': 'tcp', 'local_ip': '127.0.0.1'}
            
            if server:
                config['common']['server_addr'] = server
            if token:
                config['common']['token'] = token
            if port != 6001:
                config['ssh']['remote_port'] = port
            if local_port != 22:
                config['ssh']['local_port'] = local_port
        
        if not config:
            console.print("❌ No client configuration found. Run 'frp-tunnel setup client' first.")
            return
        
        if tunnel_manager.start_client(config):
            console.print("✅ Client connected successfully!")
        else:
            console.print("❌ Failed to start client")


@cli.command()
def update():
    """Update frp-tunnel to latest version"""
    import subprocess
    import sys
    
    console.print("🔄 Updating frp-tunnel...")
    
    try:
        # Update using pip
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '--upgrade', 'frp-tunnel'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print("✅ frp-tunnel updated successfully!")
            console.print("🔧 Run 'frp-tunnel --version' to see the new version")
        else:
            console.print(f"❌ Update failed: {result.stderr}")
            
    except Exception as e:
        console.print(f"❌ Update error: {e}")


@cli.command()
def clean():
    """Clean cache and temporary files"""
    console.print("🧹 Cleaning cache...")
    tunnel_manager.clean_cache()
    console.print("✅ Cache cleaned")

def main():
    """Entry point for the CLI"""
    cli()

if __name__ == '__main__':
    main()
