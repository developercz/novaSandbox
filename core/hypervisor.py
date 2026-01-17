"""
Univerzální abstrakce pro různé hypervisory.
Zajišťuje jednotné API pro Firecracker, Apple VZ a další.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional, Dict, Any, List
import asyncio
import json
import time
import logging
from .security import SecurityPolicy, SecurityLevel, DEFAULT_POLICIES

logger = logging.getLogger(__name__)

class SandboxState(Enum):
    """Stavy sandboxu pro sledování životního cyklu"""
    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

@dataclass
class SandboxConfig:
    """Konfigurace pro vytvoření sandboxu"""
    template_id: str = "alpine-python"
    memory_mb: int = 512
    vcpus: int = 2
    boot_timeout_ms: int = 5000
    kernel_args: str = "console=ttyS0 reboot=k panic=1"
    
    # Síťová konfigurace
    enable_network: bool = True
    host_port: Optional[int] = None
    guest_port: Optional[int] = 8080
    
    # Úložiště
    rootfs_path: Optional[str] = None
    extra_drives: List[Dict[str, str]] = None
    
    # Metadata
    labels: Dict[str, str] = None
    
    # Bezpečnost
    security_level: SecurityLevel = SecurityLevel.STANDARD
    custom_security_policy: Optional[SecurityPolicy] = None
    
    def __post_init__(self):
        if self.extra_drives is None:
            self.extra_drives = []
        if self.labels is None:
            self.labels = {}
    
    def get_security_policy(self) -> SecurityPolicy:
        """Vrátí efektivní bezpečnostní politiku"""
        if self.custom_security_policy:
            return self.custom_security_policy
        return DEFAULT_POLICIES.get(self.security_level, DEFAULT_POLICIES[SecurityLevel.STANDARD])

class BaseHypervisor(ABC):
    """Abstraktní základ pro všechny hypervisorové implementace"""
    
    def __init__(self, hypervisor_path: Optional[str] = None):
        self.hypervisor_path = hypervisor_path
        self._sandboxes: Dict[str, 'Sandbox'] = {}
        
    @abstractmethod
    async def create_sandbox(self, config: SandboxConfig) -> 'Sandbox':
        """Vytvoří nový sandbox"""
        pass
    
    @abstractmethod
    async def start_sandbox(self, sandbox_id: str) -> bool:
        """Spustí sandbox"""
        pass
    
    @abstractmethod
    async def stop_sandbox(self, sandbox_id: str, force: bool = False) -> bool:
        """Zastaví sandbox"""
        pass
    
    @abstractmethod
    async def pause_sandbox(self, sandbox_id: str) -> bool:
        """Pozastaví sandbox"""
        pass
    
    @abstractmethod
    async def resume_sandbox(self, sandbox_id: str) -> bool:
        """Obnoví pozastavený sandbox"""
        pass
    
    @abstractmethod
    async def get_sandbox_stats(self, sandbox_id: str) -> Dict[str, Any]:
        """Získá statistiky sandboxu"""
        pass
    
    @property
    @abstractmethod
    def supported_platform(self) -> str:
        """Vrátí podporovanou platformu (linux, macos, windows)"""
        pass
