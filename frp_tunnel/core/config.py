"""Configuration management"""

import secrets
from pathlib import Path
from typing import Dict, Any
import yaml

class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / 'data' / 'frp'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.server_config_path = self.config_dir / 'frps.yaml'
    
    def create_server_config(self, config: Dict[str, Any]) -> Path:
        """Create server configuration file in YAML format"""
        # Preserve existing config if it exists
        existing_config = {}
        if self.server_config_path.exists():
            with open(self.server_config_path) as f:
                existing_config = yaml.safe_load(f) or {}
        
        # Use provided token or existing token or generate new one
        token = config.get('token') or existing_config.get('auth', {}).get('token') or self._generate_token()
        bind_port = config.get('bind_port', existing_config.get('bindPort', 7000))
        dashboard_port = existing_config.get('webServer', {}).get('port', 7500)
        
        yaml_config = {
            'bindPort': bind_port,
            'auth': {'token': token},
            'webServer': {
                'addr': '0.0.0.0',
                'port': dashboard_port,
                'user': 'admin',
                'password': 'admin'
            },
            'log': {
                'to': str(self.config_dir / 'frps.log'),
                'level': 'info',
                'maxDays': 3
            }
        }
        
        with open(self.server_config_path, 'w') as f:
            yaml.dump(yaml_config, f, default_flow_style=False)
        
        return self.server_config_path
    
    def get_server_config(self) -> Dict[str, Any]:
        """Read server configuration"""
        if not self.server_config_path.exists():
            return {}
        
        with open(self.server_config_path) as f:
            return yaml.safe_load(f) or {}
    
    def _generate_token(self) -> str:
        """Generate a secure token"""
        return f"frp_{secrets.token_hex(16)}"
    
    def get_log_path(self, component: str) -> Path:
        """Get log file path"""
        return self.config_dir / f"frp{component[0]}.log"
