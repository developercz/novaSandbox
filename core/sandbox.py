"""
Hlavní třída Sandbox reprezentující microVM instanci.
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import asyncio
from .hypervisor import SandboxState, SandboxConfig, BaseHypervisor
import logging

logger = logging.getLogger(__name__)

@dataclass
class Sandbox:
    """Reprezentace běžící microVM instance"""
    sandbox_id: str
    config: SandboxConfig
    hypervisor: BaseHypervisor
    state: SandboxState = SandboxState.CREATED
    process: Optional[asyncio.subprocess.Process] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=__import__('time').time)
    
    async def execute_command(self, command: str, timeout: float = 30.0) -> str:
        """Vykoná příkaz v sandboxu a vrátí výstup"""
        # Implementace bude záviset na komunikačním kanálu
        # V budoucnosti: SSH, API, serial port, atd.
        raise NotImplementedError("Execute command implementation depends on hypervisor")
    
    async def get_logs(self) -> str:
        """Vrátí logy z sandboxu"""
        if self.process and self.process.stderr:
            return "stderr stream available"
        return ""
    
    async def get_stats(self) -> Dict[str, Any]:
        """Vrátí statistiky sandboxu"""
        return await self.hypervisor.get_sandbox_stats(self.sandbox_id)
    
    async def stop(self, force: bool = False) -> bool:
        """Zastaví sandbox"""
        success = await self.hypervisor.stop_sandbox(self.sandbox_id, force=force)
        if success:
            self.state = SandboxState.STOPPED
        return success
    
    async def pause(self) -> bool:
        """Pozastaví sandbox"""
        success = await self.hypervisor.pause_sandbox(self.sandbox_id)
        if success:
            self.state = SandboxState.PAUSED
        return success
    
    async def resume(self) -> bool:
        """Obnoví sandbox"""
        success = await self.hypervisor.resume_sandbox(self.sandbox_id)
        if success:
            self.state = SandboxState.RUNNING
        return success
    
    def is_running(self) -> bool:
        """Zkontroluje, zda je sandbox spuštěn"""
        return self.state == SandboxState.RUNNING
    
    def get_uptime_ms(self) -> float:
        """Vrátí dobu běhu sandboxu v ms"""
        import time
        return (time.time() - self.created_at) * 1000
