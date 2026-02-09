"""Binary installer for FRP"""

import os
import tarfile
import tempfile
import urllib.request
from pathlib import Path
from typing import Optional

from .platform import get_frp_binary_url, get_binary_names, detect_platform

class BinaryInstaller:
    def __init__(self):
        self.platform_info = detect_platform()
        self.binary_names = get_binary_names()
        self.install_dir = Path.home() / '.frp-tunnel' / 'bin'
        self.install_dir.mkdir(parents=True, exist_ok=True)
    
    def install_binaries(self, component: Optional[str] = None) -> bool:
        """Install FRP binaries
        
        Args:
            component: 'server', 'client', or None for both
        """
        try:
            # Download and extract
            binary_path = self._download_and_extract()
            
            # Copy required binaries
            if component == 'server' or component is None:
                self._copy_binary(binary_path, 'server')
            
            if component == 'client' or component is None:
                self._copy_binary(binary_path, 'client')
            
            # Make binaries executable
            self._make_executable()
            
            return True
            
        except Exception as e:
            print(f"Error installing binaries: {e}")
            return False
    
    def _download_and_extract(self) -> Path:
        """Download and extract FRP archive"""
        url = get_frp_binary_url()
        is_zip = url.endswith('.zip')
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            archive_path = temp_path / ('frp.zip' if is_zip else 'frp.tar.gz')
            
            # Download
            urllib.request.urlretrieve(url, archive_path)
            
            # Extract
            if is_zip:
                import zipfile
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_path)
            else:
                with tarfile.open(archive_path, 'r:gz') as tar:
                    tar.extractall(temp_path)
            
            # Find extracted directory
            extracted_dirs = [d for d in temp_path.iterdir() if d.is_dir()]
            if not extracted_dirs:
                raise Exception("No directory found in archive")
            
            binary_path = extracted_dirs[0]
            
            # Copy to permanent location
            import shutil
            permanent_path = self.install_dir / 'extracted'
            if permanent_path.exists():
                shutil.rmtree(permanent_path)
            shutil.copytree(binary_path, permanent_path)
            
            return permanent_path
    
    def _copy_binary(self, source_dir: Path, component: str):
        """Copy binary to install directory"""
        binary_name = self.binary_names[component]
        source_file = source_dir / binary_name
        dest_file = self.install_dir / binary_name
        
        if not source_file.exists():
            raise Exception(f"Binary {binary_name} not found in archive")
        
        import shutil
        shutil.copy2(source_file, dest_file)
    
    def _make_executable(self):
        """Make binaries executable on Unix systems"""
        if self.platform_info['os'] != 'windows':
            for binary_name in self.binary_names.values():
                binary_path = self.install_dir / binary_name
                if binary_path.exists():
                    os.chmod(binary_path, 0o755)
    
    def get_binary_path(self, component: str) -> Path:
        """Get path to installed binary"""
        binary_name = self.binary_names[component]
        return self.install_dir / binary_name
    
    def is_installed(self, component: str) -> bool:
        """Check if binary is installed"""
        return self.get_binary_path(component).exists()

# Global installer instance
_installer = BinaryInstaller()

def install_binaries(component: Optional[str] = None) -> bool:
    """Install FRP binaries"""
    return _installer.install_binaries(component)

def get_binary_path(component: str) -> Path:
    """Get path to binary"""
    return _installer.get_binary_path(component)

def is_installed(component: str) -> bool:
    """Check if binary is installed"""
    return _installer.is_installed(component)
