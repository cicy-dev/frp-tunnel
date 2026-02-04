"""Configuration management"""

import os
import secrets
from pathlib import Path
from typing import Dict, Any
import configparser

class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / '.frp-tunnel'
        self.config_dir.mkdir(exist_ok=True)
        
        self.server_config_path = self.config_dir / 'frps.ini'
        self.client_config_path = self.config_dir / 'frpc.ini'
    
    def create_server_config(self, config: Dict[str, Any]) -> Path:
        """Create server configuration file"""
        config_content = f"""[common]
bind_port = {config.get('bind_port', 7000)}
token = {config.get('token', self._generate_token())}

# Dashboard (optional)
dashboard_port = 7500
dashboard_user = admin
dashboard_pwd = admin

# Logging
log_file = {self.config_dir}/frps.log
log_level = info
log_max_days = 3

# Security
authentication_method = token
heartbeat_timeout = 90
"""
        
        with open(self.server_config_path, 'w') as f:
            f.write(config_content)
        
        return self.server_config_path
    
    def create_client_config(self, config: Dict[str, Any]) -> Path:
        """Create client configuration file"""
        config_content = f"""[common]
server_addr = {config['server_addr']}
server_port = {config.get('server_port', 7000)}
token = {config['token']}

# Logging
log_file = {self.config_dir}/frpc.log
log_level = info

[ssh_{config.get('username', 'colab')}]
type = tcp
local_ip = 127.0.0.1
local_port = 22
remote_port = {config.get('remote_port', 6001)}
"""
        
        with open(self.client_config_path, 'w') as f:
            f.write(config_content)
        
        return self.client_config_path
    
    def get_server_config(self) -> Dict[str, Any]:
        """Read server configuration"""
        if not self.server_config_path.exists():
            return {}
        
        config = configparser.ConfigParser()
        config.read(self.server_config_path)
        
        if 'common' not in config:
            return {}
        
        return dict(config['common'])
    
    def get_client_config(self) -> Dict[str, Any]:
        """Read client configuration"""
        if not self.client_config_path.exists():
            return {}
        
        config = configparser.ConfigParser()
        config.read(self.client_config_path)
        
        if 'common' not in config:
            return {}
        
        return dict(config['common'])
    
    def _generate_token(self) -> str:
        """Generate a secure token"""
        return f"frp_{secrets.token_hex(16)}"
    
    def get_log_path(self, component: str) -> Path:
        """Get log file path"""
        return self.config_dir / f"frp{component[0]}.log"
