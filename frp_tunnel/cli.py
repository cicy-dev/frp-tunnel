#!/usr/bin/env python3
"""FRP Tunnel CLI - Simple SSH tunneling"""

import sys
import os
import subprocess
import secrets
import platform
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
SERVER_YAML = DATA_DIR / 'frps.yaml'
CLIENT_YAML = DATA_DIR / 'frpc.yaml'
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Binary paths - bundled in project, auto-download if missing
FRP_VERSION = "0.52.3"

def _platform_info():
    """Returns (os_name, arch) for current platform"""
    machine = platform.machine().lower()
    arch = {'x86_64': 'amd64', 'amd64': 'amd64', 'aarch64': 'arm64', 'arm64': 'arm64'}.get(machine, machine)
    os_name = {'linux': 'linux', 'darwin': 'darwin', 'win32': 'windows'}.get(sys.platform, sys.platform)
    return os_name, arch

def _get_bin_dir():
    """Get binary directory for current platform"""
    os_name, arch = _platform_info()
    # Try project bundled dir first
    pkg_dir = Path(__file__).parent.parent / 'bin' / f'{os_name}_{arch}'
    if pkg_dir.exists():
        return pkg_dir
    # Fallback: ~/.frp-tunnel/bin
    fallback = HOME / '.frp-tunnel' / 'bin'
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback

BIN_DIR = _get_bin_dir()

def _frps_bin():
    return BIN_DIR / ('frps.exe' if sys.platform == 'win32' else 'frps')

def _frpc_bin():
    return BIN_DIR / ('frpc.exe' if sys.platform == 'win32' else 'frpc')

def _check_bin(binary):
    if not binary.exists():
        console.print(f"❌ Binary not found: {binary}", style="red")
        console.print("💡 Run 'ft server init' or 'ft client init' to auto-download")
        sys.exit(1)

def _ensure_binaries():
    """Download FRP binaries if not present in bin dir"""
    frps, frpc = _frps_bin(), _frpc_bin()
    if frps.exists() and frpc.exists():
        return
    os_name, arch = _platform_info()
    ext = 'zip' if os_name == 'windows' else 'tar.gz'
    filename = f"frp_{FRP_VERSION}_{os_name}_{arch}.{ext}"
    url = f"https://github.com/fatedier/frp/releases/download/v{FRP_VERSION}/{filename}"
    console.print(f"📦 Downloading FRP {FRP_VERSION} ({os_name}/{arch})...")
    import tempfile, urllib.request
    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / filename
        urllib.request.urlretrieve(url, archive)
        if ext == 'zip':
            import zipfile
            with zipfile.ZipFile(archive) as z:
                z.extractall(tmp)
        else:
            import tarfile
            with tarfile.open(archive, 'r:gz') as t:
                t.extractall(tmp)
        # Find extracted dir
        extracted = [d for d in Path(tmp).iterdir() if d.is_dir()][0]
        import shutil
        for name in ('frps', 'frpc', 'frps.exe', 'frpc.exe'):
            src = extracted / name
            if src.exists():
                shutil.copy2(src, BIN_DIR / name)
    # Make executable on unix
    if os_name != 'windows':
        frps.chmod(0o755)
        frpc.chmod(0o755)
    console.print("✅ Download complete")

def gen_token():
    return f"frp_{secrets.token_hex(16)}"

def get_public_ip():
    try:
        import requests
        return requests.get('https://api.myip.com', timeout=3).json().get('ip', 'unknown')
    except:
        return 'unknown'

def is_running(name):
    try:
        if sys.platform == 'win32':
            result = subprocess.run(['tasklist'], capture_output=True, text=True)
            return name in result.stdout
        else:
            result = subprocess.run(['pgrep', '-f', name], capture_output=True)
            return result.returncode == 0
    except:
        return False

def _stop(name):
    if sys.platform == 'win32':
        subprocess.run(['taskkill', '/F', '/IM', f'{name}.exe'], capture_output=True)
    else:
        subprocess.run(['pkill', '-9', name], capture_output=True)

def _start_bg(binary, config):
    _check_bin(binary)
    if sys.platform == 'win32':
        subprocess.Popen([str(binary), '-c', str(config)], creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        subprocess.Popen([str(binary), '-c', str(config)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ─── CLI ───

CTX = {'help_option_names': ['-h', '--help']}

@click.group(context_settings=CTX)
@click.version_option(__version__)
def cli():
    """🚀 FRP Tunnel - Easy SSH tunneling with FRP

    \b
    ft server init          Generate server config
    ft server start/stop    Control server
    ft server status        Show server status
    ft server install       Install as system service
    ft server reload        Restart server (apply config)
    \b
    ft client init          Generate client config
    ft client start/stop    Control client
    ft client status        Show client status
    ft client reload        Hot-reload client config
    \b
    ft frps <args>          Run frps directly
    ft frpc <args>          Run frpc directly
    ft token                Generate auth token
    """
    pass

# ─── SERVER ───

@cli.group(context_settings=CTX)
def server():
    """Manage FRP server"""
    pass

@server.command('init')
@click.option('--force', '-f', is_flag=True, help='Overwrite existing config')
def server_init(force):
    """Generate server config (frps.yaml)"""
    _ensure_binaries()
    if SERVER_YAML.exists() and not force:
        console.print(f"⚠️  Config exists: {SERVER_YAML} (use -f to overwrite)")
        return
    import yaml
    token = gen_token()
    config = {
        'bindPort': 7000,
        'auth': {'token': token},
        'webServer': {'addr': '0.0.0.0', 'port': 7500, 'user': 'admin', 'password': 'admin'},
        'log': {'to': str(DATA_DIR / 'frps.log'), 'level': 'info'}
    }
    with open(SERVER_YAML, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    console.print(f"✅ Config created: {SERVER_YAML}")
    console.print(f"🔑 Token: [bold yellow]{token}[/bold yellow]")

@server.command('start')
def server_start():
    """Start FRP server"""
    if is_running('frps'):
        console.print("⚠️  Server already running")
        return
    if not SERVER_YAML.exists():
        console.print("❌ No config. Run 'ft server init' first", style="red")
        return
    _start_bg(_frps_bin(), SERVER_YAML)
    import time; time.sleep(1)
    if is_running('frps'):
        console.print("✅ Server started")
    else:
        console.print("❌ Server failed to start, check log: " + str(DATA_DIR / 'frps.log'), style="red")

@server.command('stop')
def server_stop():
    """Stop FRP server"""
    _stop('frps')
    console.print("✅ Server stopped")

@server.command('reload')
def server_reload():
    """Restart server to apply config changes"""
    if not SERVER_YAML.exists():
        console.print("❌ No config. Run 'ft server init' first", style="red")
        return
    _stop('frps')
    import time; time.sleep(1)
    _start_bg(_frps_bin(), SERVER_YAML)
    time.sleep(1)
    if is_running('frps'):
        console.print("✅ Server restarted")
    else:
        console.print("❌ Server failed to start, check log: " + str(DATA_DIR / 'frps.log'), style="red")

@server.command('status')
def server_status():
    """Show server status"""
    console.print("\n📊 Server Status")
    if not is_running('frps'):
        console.print("🖥️  Server: [red]Stopped[/red]\n")
        return
    console.print("🖥️  Server: [green]Running[/green]")
    ip = get_public_ip()
    if ip != 'unknown':
        console.print(f"   🌐 Public IP: [cyan]{ip}[/cyan]")
    console.print(f"   📄 Config: [cyan]{SERVER_YAML}[/cyan]")
    log_file = DATA_DIR / 'frps.log'
    if log_file.exists():
        console.print(f"   📋 Log: [cyan]{log_file}[/cyan]")
    console.print(f"   🔧 Binary: [cyan]{_frps_bin()}[/cyan]")
    # Active clients via API
    try:
        import requests
        resp = requests.get('http://localhost:7500/api/proxy/tcp', timeout=2)
        if resp.status_code == 200:
            proxies = [p for p in resp.json().get('proxies', []) if p.get('status') != 'offline']
            console.print(f"   👥 Active clients: [green]{len(proxies)}[/green]")
            for p in proxies:
                name = p.get('name', '?')
                port = (p.get('conf') or {}).get('remotePort', '?')
                ver = p.get('clientVersion', '?')
                conns = p.get('curConns', 0)
                console.print(f"      • {name}: :{port} (v{ver}, {conns} conns)")
    except:
        pass
    # Show token (masked)
    if SERVER_YAML.exists():
        import yaml
        with open(SERVER_YAML) as f:
            cfg = yaml.safe_load(f)
        token = cfg.get('auth', {}).get('token', '')
        if len(token) > 16:
            masked = token[:8] + '*' * (len(token) - 16) + token[-8:]
        else:
            masked = '***'
        console.print(f"\n💡 Client command:")
        console.print(f"   [yellow]ft client init --server {ip} --token {masked} --port <PORT>[/yellow]")
        console.print(f"\n📦 Install client:")
        console.print(f"   [yellow]pip install frp-tunnel[/yellow]")
        console.print(f"   [yellow]pip install frp-tunnel -i https://pypi.tuna.tsinghua.edu.cn/simple[/yellow]  # 国内镜像")
        console.print(f"   [yellow]pip install git+https://github.com/cicy-dev/frp-tunnel.git[/yellow]  # GitHub 最新版")
        console.print(f"   [yellow]pip install https://gh-proxy.com/https://github.com/cicy-dev/frp-tunnel/archive/refs/heads/main.zip[/yellow]  # 国内加速")
    console.print()

@server.command('install')
def server_install():
    """Install as system service (systemd/launchd)"""
    if not SERVER_YAML.exists():
        console.print("❌ No config. Run 'ft server init' first", style="red")
        return
    frps = _frps_bin()
    _check_bin(frps)

    if sys.platform == 'darwin':
        # macOS launchd
        plist_name = 'com.frp-tunnel.server'
        plist_path = HOME / 'Library' / 'LaunchAgents' / f'{plist_name}.plist'
        plist_path.parent.mkdir(parents=True, exist_ok=True)
        plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>{plist_name}</string>
  <key>ProgramArguments</key><array><string>{frps}</string><string>-c</string><string>{SERVER_YAML}</string></array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>{DATA_DIR / 'frps-stdout.log'}</string>
  <key>StandardErrorPath</key><string>{DATA_DIR / 'frps-stderr.log'}</string>
</dict></plist>"""
        plist_path.write_text(plist)
        subprocess.run(['launchctl', 'load', str(plist_path)])
        console.print(f"✅ Installed: {plist_path}")
    elif sys.platform == 'win32':
        # Windows: create startup bat
        bat = HOME / 'AppData' / 'Roaming' / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup' / 'frp-server.bat'
        bat.write_text(f'@echo off\nstart "" "{frps}" -c "{SERVER_YAML}"\n')
        console.print(f"✅ Installed startup: {bat}")
    else:
        # Linux systemd
        service = f"""[Unit]
Description=FRP Tunnel Server
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'root')}
ExecStart={frps} -c {SERVER_YAML}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        try:
            subprocess.run(['sudo', 'tee', '/etc/systemd/system/frp-server.service'], input=service, text=True, capture_output=True, check=True)
            subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
            subprocess.run(['sudo', 'systemctl', 'enable', 'frp-server'], check=True)
            subprocess.run(['sudo', 'systemctl', 'start', 'frp-server'], check=True)
            console.print("✅ Installed systemd service: frp-server")
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Failed: {e}", style="red")

# ─── CLIENT ───

@cli.group(context_settings=CTX)
def client():
    """Manage FRP client"""
    pass

@client.command('init')
@click.option('--server', default='YOUR_SERVER_IP', help='Server address')
@click.option('--token', default='YOUR_TOKEN', help='Auth token')
@click.option('--port', default=6022, type=int, help='Remote SSH port')
@click.option('--force', '-f', is_flag=True, help='Overwrite existing config')
def client_init(server, token, port, force):
    """Generate client config (frpc.yaml)"""
    _ensure_binaries()
    if CLIENT_YAML.exists() and not force:
        console.print(f"⚠️  Config exists: {CLIENT_YAML} (use -f to overwrite)")
        return
    import yaml
    config = {
        'serverAddr': server,
        'serverPort': 7000,
        'auth': {'token': token},
        'log': {'to': str(DATA_DIR / 'frpc.log'), 'level': 'info'},
        'webServer': {'addr': '127.0.0.1', 'port': 7400},
        'proxies': [
            {'name': f'ssh_{port}', 'type': 'tcp', 'localIP': '127.0.0.1', 'localPort': 22, 'remotePort': port}
        ]
    }
    with open(CLIENT_YAML, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    console.print(f"✅ Config created: {CLIENT_YAML}")
    console.print(f"📝 Edit config to add more proxies, then: ft client start")

@client.command('start')
def client_start():
    """Start FRP client"""
    if is_running('frpc'):
        console.print("⚠️  Client already running")
        return
    if not CLIENT_YAML.exists():
        console.print("❌ No config. Run 'ft client init' first", style="red")
        return
    _start_bg(_frpc_bin(), CLIENT_YAML)
    import time; time.sleep(1)
    if is_running('frpc'):
        console.print("✅ Client started")
    else:
        console.print("❌ Client failed to start, check log: " + str(DATA_DIR / 'frpc.log'), style="red")

@client.command('stop')
def client_stop():
    """Stop FRP client"""
    _stop('frpc')
    console.print("✅ Client stopped")

@client.command('reload')
def client_reload():
    """Hot-reload client config"""
    frpc = _frpc_bin()
    _check_bin(frpc)
    result = subprocess.run([str(frpc), 'reload', '-c', str(CLIENT_YAML)], capture_output=True, text=True)
    if result.returncode == 0:
        console.print("✅ Client config reloaded")
    else:
        console.print(f"❌ Reload failed: {result.stderr.strip()}", style="red")

@client.command('status')
def client_status():
    """Show client status"""
    console.print("\n📊 Client Status")
    if not is_running('frpc'):
        console.print("📱 Client: [red]Disconnected[/red]")
        if CLIENT_YAML.exists():
            import yaml
            with open(CLIENT_YAML) as f:
                cfg = yaml.safe_load(f)
            console.print(f"   📄 Config: [cyan]{CLIENT_YAML}[/cyan]")
            console.print(f"   🌐 Server: [cyan]{cfg.get('serverAddr', '?')}:{cfg.get('serverPort', 7000)}[/cyan]")
            ports = [p.get('remotePort', '?') for p in cfg.get('proxies', [])]
            if ports:
                console.print(f"   🔌 Ports: [cyan]{', '.join(map(str, ports))}[/cyan]")
        console.print()
        return
    console.print("📱 Client: [green]Connected[/green]")
    if CLIENT_YAML.exists():
        import yaml
        with open(CLIENT_YAML) as f:
            cfg = yaml.safe_load(f)
        console.print(f"   🌐 Server: [cyan]{cfg.get('serverAddr', '?')}:{cfg.get('serverPort', 7000)}[/cyan]")
        ports = [p.get('remotePort', '?') for p in cfg.get('proxies', [])]
        if ports:
            console.print(f"   🔌 Ports: [cyan]{', '.join(map(str, ports))}[/cyan]")
    console.print(f"   📄 Config: [cyan]{CLIENT_YAML}[/cyan]")
    log_file = DATA_DIR / 'frpc.log'
    if log_file.exists():
        console.print(f"   📋 Log: [cyan]{log_file}[/cyan]")
    console.print(f"   🔧 Binary: [cyan]{_frpc_bin()}[/cyan]")
    console.print()

# ─── PASSTHROUGH ───

@cli.command('frps', context_settings={'ignore_unknown_options': True, 'allow_interspersed_args': False})
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def passthrough_frps(args):
    """Run frps directly (passthrough all args)"""
    frps = _frps_bin()
    _check_bin(frps)
    os.execvp(str(frps), [str(frps)] + list(args))

@cli.command('frpc', context_settings={'ignore_unknown_options': True, 'allow_interspersed_args': False})
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def passthrough_frpc(args):
    """Run frpc directly (passthrough all args)"""
    frpc = _frpc_bin()
    _check_bin(frpc)
    os.execvp(str(frpc), [str(frpc)] + list(args))

# ─── UTILS ───

@cli.command()
def token():
    """Generate authentication token"""
    t = gen_token()
    console.print(f"🔑 {t}")

@cli.command()
def stop():
    """Stop all FRP processes"""
    _stop('frps')
    _stop('frpc')
    console.print("✅ All FRP processes stopped")

def main():
    cli()

if __name__ == '__main__':
    main()
