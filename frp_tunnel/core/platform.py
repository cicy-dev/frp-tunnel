"""Platform detection and utilities"""

import os
import platform
import subprocess
from typing import Dict, List

def detect_platform() -> Dict[str, str]:
    """Detect current platform and architecture"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # Normalize architecture names
    arch_map = {
        'x86_64': 'amd64',
        'amd64': 'amd64',
        'aarch64': 'arm64',
        'arm64': 'arm64',
        'armv7l': 'arm',
    }
    
    arch = arch_map.get(machine, machine)
    
    return {
        'os': system,
        'arch': arch,
        'platform': f"{system}-{arch}"
    }

def is_colab() -> bool:
    """Check if running in Google Colab"""
    return 'COLAB_GPU' in os.environ or os.path.exists('/content')

def is_docker() -> bool:
    """Check if running in Docker"""
    return os.path.exists('/.dockerenv')

def check_requirements() -> Dict[str, bool]:
    """Check if required tools are available"""
    requirements = {
        'ssh': _command_exists('ssh'),
        'wget': _command_exists('wget') or _command_exists('curl'),
        'tar': _command_exists('tar'),
    }
    
    # Additional checks for different platforms
    if platform.system().lower() == 'linux':
        requirements['systemctl'] = _command_exists('systemctl')
    
    return requirements

def _command_exists(command: str) -> bool:
    """Check if a command exists in PATH"""
    try:
        subprocess.run(['which', command], 
                      capture_output=True, 
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_frp_binary_url(version: str = "0.52.3") -> str:
    """Get FRP binary download URL for current platform"""
    platform_info = detect_platform()
    
    # Map platform names to FRP naming convention
    os_map = {
        'linux': 'linux',
        'darwin': 'darwin',
        'windows': 'windows'
    }
    
    os_name = os_map.get(platform_info['os'], platform_info['os'])
    arch = platform_info['arch']
    
    filename = f"frp_{version}_{os_name}_{arch}.tar.gz"
    url = f"https://github.com/fatedier/frp/releases/download/v{version}/{filename}"
    
    return url

def get_binary_names() -> Dict[str, str]:
    """Get binary names for current platform"""
    if platform.system().lower() == 'windows':
        return {
            'server': 'frps.exe',
            'client': 'frpc.exe'
        }
    else:
        return {
            'server': 'frps',
            'client': 'frpc'
        }
