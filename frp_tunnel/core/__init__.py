"""Core module initialization"""

from .platform import detect_platform, is_colab
from .installer import install_binaries, get_binary_path, is_installed
from .config import ConfigManager
from .tunnel import TunnelManager

__all__ = [
    'detect_platform',
    'is_colab', 
    'install_binaries',
    'get_binary_path',
    'is_installed',
    'ConfigManager',
    'TunnelManager'
]
