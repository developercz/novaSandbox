"""
Implementace pro Apple Virtualization.Framework na macOS.
Používá nativní Apple API pro maximální výkon.
"""
import asyncio
import time
import uuid
from typing import Dict, Any, Optional
from pathlib import Path

try:
    from Virtualization import (
        VZVirtualMachine, VZVirtualMachineConfiguration,
        VZGenericPlatformConfiguration,
        VZStorageDeviceConfiguration, VZVirtioBlockDeviceConfiguration,
        VZNetworkDeviceConfiguration, VZNATNetworkDeviceAttachment,
        VZVirtioNetworkDeviceConfiguration, VZLinuxBootLoader,
        VZDiskImageStorageDeviceAttachment
    )
    from Foundation import NSURL, NSData
    HAS_VIRTUALIZATION = True
except ImportError:
    HAS_VIRTUALIZATION = False
    # Fallback pro ne-macOS systémy nebo starší verze

from ..core.hypervisor import BaseHypervisor, SandboxConfig, SandboxState
import logging

logger = logging.getLogger(__name__)

class AppleVZHypervisor(BaseHypervisor):
    """Implementace pomocí Apple Virtualization.Framework"""
    
    def __init__(self):
        super().__init__(None)
        if not HAS_VIRTUALIZATION:
            logger.warning(
                "Apple Virtualization.Framework not available. "
                "Requires macOS 11+ with Apple Silicon."
            )
    
    @property
    def supported_platform(self) -> str:
        return "macos"
    
    async def create_sandbox(self, config: SandboxConfig) -> 'Sandbox':
        """Vytvoří sandbox pomocí Virtualization.Framework"""
        from ..core.sandbox import Sandbox
        
        if not HAS_VIRTUALIZATION:
            raise RuntimeError(
                "Apple Virtualization.Framework not available. "
                "Requires macOS 11+ with Apple Silicon."
            )
        
        sandbox_id = f"vz_{uuid.uuid4().hex[:12]}"
        start_time = time.time()
        
        # Načtení předpřipraveného image
        template_dir = Path("templates") / config.template_id
        disk_path = template_dir / "disk.img"
        kernel_path = template_dir / "vmlinux"
        
        if not disk_path.exists():
            raise FileNotFoundError(f"Disk image not found: {disk_path}")
        
        if not kernel_path.exists():
            raise FileNotFoundError(f"Kernel not found: {kernel_path}")
        
        try:
            # Vytvoření konfigurace VM
            vm_config = VZVirtualMachineConfiguration()
            
            # Boot loader pro Linux
            boot_loader = VZLinuxBootLoader(
                kernelURL_=NSURL.fileURLWithPath_(str(kernel_path))
            )
            boot_loader.setCommandLineArguments_(["console=hvc0"])
            vm_config.setBootLoader_(boot_loader)
            
            # CPU a paměť
            vm_config.setCPUCount_(config.vcpus)
            vm_config.setMemorySize_(config.memory_mb * 1024 * 1024)  # MB to bytes
            
            # Úložiště
            disk_attachment = VZDiskImageStorageDeviceAttachment(
                url=NSURL.fileURLWithPath_(str(disk_path)),
                readOnly=False
            )
            disk_config = VZVirtioBlockDeviceConfiguration()
            disk_config.setAttachment_(disk_attachment)
            vm_config.setStorageDevices_([disk_config])
            
            # Síť (NAT)
            if config.enable_network:
                network_attachment = VZNATNetworkDeviceAttachment()
                network_config = VZVirtioNetworkDeviceConfiguration()
                network_config.setAttachment_(network_attachment)
                vm_config.setNetworkDevices_([network_config])
            
            # Platforma (Generic)
            platform_config = VZGenericPlatformConfiguration()
            vm_config.setPlatformConfiguration_(platform_config)
            
            # Validace konfigurace
            error = None
            vm_config_valid = vm_config.validateWithError_(error)
            
            if not vm_config_valid:
                raise ValueError(f"Invalid VM configuration: {error}")
            
            # Vytvoření a spuštění VM
            vm = VZVirtualMachine(configuration_=vm_config)
            
            # Asynchronní spuštění
            boot_completed = asyncio.Event()
            boot_error = None
            
            def start_completion_handler(error):
                nonlocal boot_error
                boot_error = error
                boot_completed.set()
            
            # Spuštění VM v background
            vm.startWithCompletionHandler_(start_completion_handler)
            
            # Čekání na spuštění s timeout
            try:
                await asyncio.wait_for(boot_completed.wait(), timeout=config.boot_timeout_ms / 1000)
            except asyncio.TimeoutError:
                raise RuntimeError("VM boot timeout")
            
            if boot_error:
                raise RuntimeError(f"VM boot failed: {boot_error}")
            
            boot_time = (time.time() - start_time) * 1000
            
            logger.info(f"Apple VZ sandbox {sandbox_id} started in {boot_time:.2f}ms")
            
            # Vytvoření Sandbox objektu
            sandbox = Sandbox(
                sandbox_id=sandbox_id,
                config=config,
                hypervisor=self,
                state=SandboxState.RUNNING,
                process=None,  # VM je spravováno frameworkem
                metadata={
                    "boot_time_ms": boot_time,
                    "vm": vm,
                    "disk_path": str(disk_path),
                    "kernel_path": str(kernel_path)
                }
            )
            
            self._sandboxes[sandbox_id] = sandbox
            return sandbox
            
        except Exception as e:
            logger.error(f"Failed to create sandbox: {e}")
            raise
    
    async def start_sandbox(self, sandbox_id: str) -> bool:
        """Spustí existující sandbox - u Apple VZ je již spuštěno"""
        if sandbox_id not in self._sandboxes:
            return False
        return self._sandboxes[sandbox_id].is_running()
    
    async def stop_sandbox(self, sandbox_id: str, force: bool = False) -> bool:
        """Zastaví sandbox"""
        if sandbox_id not in self._sandboxes:
            return False
        
        sandbox = self._sandboxes[sandbox_id]
        vm = sandbox.metadata.get("vm")
        
        if vm:
            stop_completed = asyncio.Event()
            stop_error = None
            
            def stop_completion_handler(error):
                nonlocal stop_error
                stop_error = error
                stop_completed.set()
            
            # Zastavení VM
            if force:
                vm.stop(None)  # Força stop
            else:
                vm.stopWithCompletionHandler_(stop_completion_handler)
                try:
                    await asyncio.wait_for(stop_completed.wait(), timeout=30)
                except asyncio.TimeoutError:
                    vm.stop(None)
        
        del self._sandboxes[sandbox_id]
        return True
    
    async def pause_sandbox(self, sandbox_id: str) -> bool:
        """Pozastaví sandbox"""
        if sandbox_id not in self._sandboxes:
            return False
        
        sandbox = self._sandboxes[sandbox_id]
        vm = sandbox.metadata.get("vm")
        
        if vm and hasattr(vm, 'pause'):
            # Apple VZ podporuje pause pouze na novějších verzích
            pause_completed = asyncio.Event()
            
            def pause_completion_handler(error):
                pause_completed.set()
            
            vm.pauseWithCompletionHandler_(pause_completion_handler)
            await pause_completed.wait()
            return True
        
        return False
    
    async def resume_sandbox(self, sandbox_id: str) -> bool:
        """Obnoví sandbox"""
        if sandbox_id not in self._sandboxes:
            return False
        
        sandbox = self._sandboxes[sandbox_id]
        vm = sandbox.metadata.get("vm")
        
        if vm and hasattr(vm, 'resume'):
            resume_completed = asyncio.Event()
            
            def resume_completion_handler(error):
                resume_completed.set()
            
            vm.resumeWithCompletionHandler_(resume_completion_handler)
            await resume_completed.wait()
            return True
        
        return False
    
    async def get_sandbox_stats(self, sandbox_id: str) -> Dict[str, Any]:
        """Získá základní statistiky sandboxu"""
        if sandbox_id not in self._sandboxes:
            return {}
        
        sandbox = self._sandboxes[sandbox_id]
        vm = sandbox.metadata.get("vm")
        
        stats = {
            "platform": "apple_vz",
            "status": "running" if sandbox.is_running() else "stopped",
            "memory_mb": sandbox.config.memory_mb,
            "vcpus": sandbox.config.vcpus,
        }
        
        if vm:
            # Pokud VM má dostupné další statistiky
            if hasattr(vm, 'isRunning'):
                stats["is_running"] = vm.isRunning()
        
        return stats
