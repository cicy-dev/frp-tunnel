"""Configuration management"""

import os
import secrets
from pathlib import Path
from typing import Dict, Any
import configparser

class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / 'data' / 'frp'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.server_config_path = self.config_dir / 'frps.ini'
    
    def create_server_config(self, config: Dict[str, Any]) -> Path:
        """Create server configuration file"""
        # Preserve existing config if it exists
        existing_config = {}
        if self.server_config_path.exists():
            parser = configparser.ConfigParser()
            parser.read(self.server_config_path)
            if 'common' in parser:
                existing_config = dict(parser['common'])
        
        # Use provided token or existing token or generate new one
        token = config.get('token') or existing_config.get('token') or self._generate_token()
        bind_port = config.get('bind_port', existing_config.get('bind_port', 7000))
        dashboard_port = existing_config.get('dashboard_port', 7500)
        
        config_content = f"""[common]
bind_port = {bind_port}
token = {token}

# Dashboard (optional)
dashboard_port = {dashboard_port}
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
    
    def get_server_config(self) -> Dict[str, Any]:
        """Read server configuration"""
        if not self.server_config_path.exists():
            return {}
        
        config = configparser.ConfigParser()
        config.read(self.server_config_path)
        
        if 'common' not in config:
            return {}
        
        return dict(config['common'])
    
    def _generate_token(self) -> str:
        """Generate a secure token"""
        return f"frp_{secrets.token_hex(16)}"
    
    def get_log_path(self, component: str) -> Path:
        """Get log file path"""
        return self.config_dir / f"frp{component[0]}.log"
