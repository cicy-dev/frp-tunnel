"""Tunnel management"""

import os
import subprocess
import signal
import time
from pathlib import Path
from typing import Dict, List, Optional

from .installer import get_binary_path, is_installed, install_binaries
from .config import ConfigManager
from .platform import is_colab

class TunnelManager:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.pid_dir = Path.home() / '.frp-tunnel' / 'pids'
        self.pid_dir.mkdir(parents=True, exist_ok=True)
    
    def start_server(self, config: Dict) -> bool:
        """Start FRP server"""
        if not is_installed('server'):
            install_binaries('server')
        
        binary_path = get_binary_path('server')
        config_path = self.config_manager.create_server_config(config)
        
        try:
            # Start server process
            process = subprocess.Popen([
                str(binary_path),
                '-c', str(config_path)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Save PID
            pid_file = self.pid_dir / 'frps.pid'
            with open(pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # Wait a moment to check if it started successfully
            time.sleep(2)
            if process.poll() is None:
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error starting server: {e}")
            return False
    
    def start_client(self, config: Dict) -> bool:
        """Start FRP client"""
        if not is_installed('client'):
            install_binaries('client')
        
        binary_path = get_binary_path('client')
        config_path = self.config_manager.create_client_config(config)
        
        try:
            # Start client process
            process = subprocess.Popen([
                str(binary_path),
                '-c', str(config_path)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Save PID
            pid_file = self.pid_dir / 'frpc.pid'
            with open(pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # Wait a moment to check if it started successfully
            time.sleep(2)
            if process.poll() is None:
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error starting client: {e}")
            return False
    
    def setup_colab_ssh(self, username: str = 'colab'):
        """Setup SSH for Google Colab environment"""
        try:
            # Generate SSH key if not exists
            subprocess.run([
                'bash', '-c',
                'test -f ~/.ssh/id_rsa || ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""'
            ], check=True)
            
            # Create user if not exists
            subprocess.run([
                'bash', '-c',
                f'id {username} || sudo useradd -m -s /bin/bash {username}'
            ], check=False)  # Don't fail if user exists
            
            # Setup SSH key
            subprocess.run([
                'bash', '-c',
                f'''
                sudo mkdir -p /home/{username}/.ssh
                sudo cp ~/.ssh/id_rsa.pub /home/{username}/.ssh/authorized_keys
                sudo chown -R {username}:{username} /home/{username}/.ssh
                sudo chmod 700 /home/{username}/.ssh
                sudo chmod 600 /home/{username}/.ssh/authorized_keys
                '''
            ], check=False)
            
            # Start SSH service
            subprocess.run([
                'bash', '-c',
                'sudo systemctl start ssh || sudo service ssh start'
            ], check=False)
            
        except Exception as e:
            print(f"Warning: Some SSH setup steps failed: {e}")
    
    def stop_process(self, component: str) -> bool:
        """Stop FRP process"""
        pid_file = self.pid_dir / f'frp{component[0]}.pid'
        
        if not pid_file.exists():
            return True
        
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Try to terminate gracefully
            os.kill(pid, signal.SIGTERM)
            time.sleep(2)
            
            # Force kill if still running
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass  # Process already dead
            
            # Remove PID file
            pid_file.unlink()
            return True
            
        except Exception as e:
            print(f"Error stopping {component}: {e}")
            return False
    
    def stop_all(self):
        """Stop all FRP processes"""
        self.stop_process('server')
        self.stop_process('client')
    
    def get_status(self) -> Dict[str, bool]:
        """Get status of FRP processes"""
        return {
            'server_running': self._is_process_running('server'),
            'client_running': self._is_process_running('client')
        }
    
    def _is_process_running(self, component: str) -> bool:
        """Check if process is running"""
        pid_file = self.pid_dir / f'frp{component[0]}.pid'
        
        if not pid_file.exists():
            return False
        
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process exists
            os.kill(pid, 0)
            return True
            
        except (ProcessLookupError, ValueError, OSError):
            # Remove stale PID file
            if pid_file.exists():
                pid_file.unlink()
            return False
    
    def get_logs(self, lines: int = 20) -> List[str]:
        """Get recent log lines"""
        logs = []
        
        for component in ['server', 'client']:
            log_path = self.config_manager.get_log_path(component)
            if log_path.exists():
                try:
                    with open(log_path, 'r') as f:
                        log_lines = f.readlines()
                        recent_lines = log_lines[-lines:]
                        logs.extend([f"[{component}] {line.strip()}" for line in recent_lines])
                except Exception:
                    pass
        
        return logs
    
    def clean_cache(self):
        """Clean cache and temporary files"""
        import shutil
        
        # Clean extracted binaries
        extracted_path = Path.home() / '.frp-tunnel' / 'bin' / 'extracted'
        if extracted_path.exists():
            shutil.rmtree(extracted_path)
        
        # Clean old log files
        for log_file in self.config_manager.config_dir.glob('*.log.*'):
            log_file.unlink()
