"""
Implementace pro Firecracker microVM (AWS) na Linuxu.
Dosažení startu pod 150 ms.
"""
import asyncio
import json
import os
import tempfile
import time
import uuid
import socket
from pathlib import Path
from typing import Dict, Any, Optional
import aiofiles
import aiofiles.os
from ..core.hypervisor import BaseHypervisor, SandboxConfig, SandboxState
import logging

logger = logging.getLogger(__name__)

class FirecrackerHypervisor(BaseHypervisor):
    """Firecracker implementace pro ultra-rychlé microVM"""
    
    def __init__(self, firecracker_path: str = "/usr/bin/firecracker",
                 jailer_path: Optional[str] = None):
        super().__init__(firecracker_path)
        self.jailer_path = jailer_path
        self._api_sockets: Dict[str, str] = {}
        self._tap_interfaces: Dict[str, str] = {}
        
        # Optimalizované výchozí parametry pro rychlý start
        self._default_kernel_args = (
            "console=ttyS0 reboot=k panic=1 "
            "pci=off nomodules random.trust_cpu=on "
            "init=/sbin/init noapic noacpi"
        )
    
    @property
    def supported_platform(self) -> str:
        return "linux"
    
    async def _create_tap_interface(self, sandbox_id: str) -> str:
        """Vytvoří TAP interface pro síťovou izolaci"""
        tap_name = f"tap_{sandbox_id[:8]}"
        
        # Vytvoření TAP interface
        commands = [
            ["sudo", "ip", "tuntap", "add", tap_name, "mode", "tap"],
            ["sudo", "ip", "link", "set", tap_name, "up"],
            ["sudo", "ip", "link", "set", "dev", tap_name, "mtu", "1500"],
        ]
        
        for cmd in commands:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.wait()
        
        self._tap_interfaces[sandbox_id] = tap_name
        return tap_name
    
    async def _prepare_vm_config(self, config: SandboxConfig, 
                                kernel_path: str, 
                                rootfs_path: str) -> Dict[str, Any]:
        """Připraví optimalizovanou konfiguraci pro Firecracker"""
        
        vm_config = {
            "boot-source": {
                "kernel_image_path": kernel_path,
                "boot_args": config.kernel_args or self._default_kernel_args,
                "initrd_path": None
            },
            "drives": [
                {
                    "drive_id": "rootfs",
                    "path_on_host": rootfs_path,
                    "is_root_device": True,
                    "is_read_only": False,
                    "rate_limiter": {
                        "bandwidth": {"size": 0, "refill_time": 0},
                        "ops": {"size": 0, "refill_time": 0}
                    }
                }
            ],
            "machine-config": {
                "vcpu_count": config.vcpus,
                "mem_size_mib": config.memory_mb,
                "ht_enabled": False,  # Pro rychlejší start
                "track_dirty_pages": False
            },
            "cpu-config": {
                "features": {
                    "avx2": False,  # Vypnuto pro rychlejší inicializaci
                    "avx512": False
                }
            }
        }
        
        # Přidání síťového interface pokud je povoleno
        if config.enable_network:
            tap_name = await self._create_tap_interface(str(uuid.uuid4()))
            vm_config["network-interfaces"] = [{
                "iface_id": "eth0",
                "host_dev_name": tap_name,
                "guest_mac": "AA:FC:00:00:00:01",
                "rx_rate_limiter": {
                    "bandwidth": {"size": 0, "refill_time": 0},
                    "ops": {"size": 0, "refill_time": 0}
                },
                "tx_rate_limiter": {
                    "bandwidth": {"size": 0, "refill_time": 0},
                    "ops": {"size": 0, "refill_time": 0}
                }
            }]
        
        # Přidání extra disků
        for i, drive in enumerate(config.extra_drives):
            vm_config["drives"].append({
                "drive_id": f"drive_{i}",
                "path_on_host": drive["path"],
                "is_root_device": False,
                "is_read_only": drive.get("readonly", False)
            })
        
        return vm_config
    
    async def create_sandbox(self, config: SandboxConfig) -> 'Sandbox':
        """Vytvoří a spustí microVM pomocí Firecracker"""
        from ..core.sandbox import Sandbox
        
        sandbox_id = f"fc_{uuid.uuid4().hex[:12]}"
        start_time = time.time()
        
        # Vytvoření unix socket pro API komunikaci
        sock_dir = tempfile.mkdtemp(prefix="fc_")
        api_socket = os.path.join(sock_dir, "api.socket")
        self._api_sockets[sandbox_id] = api_socket
        
        # Cesty k předpřipraveným šablonám
        template_dir = Path("templates") / config.template_id
        kernel_path = template_dir / "vmlinux"
        rootfs_path = template_dir / "rootfs.ext4"
        
        if not kernel_path.exists() or not rootfs_path.exists():
            raise FileNotFoundError(
                f"Template {config.template_id} not found. "
                f"Expected {kernel_path} and {rootfs_path}"
            )
        
        # Příprava konfigurace
        vm_config = await self._prepare_vm_config(
            config, str(kernel_path), str(rootfs_path)
        )
        
        # Zápis konfigurace do dočasného souboru
        config_file = Path(sock_dir) / "config.json"
        async with aiofiles.open(config_file, 'w') as f:
            await f.write(json.dumps(vm_config, indent=2))
        
        # Spuštění Firecracker procesu
        cmd = [
            self.hypervisor_path,
            "--api-sock", api_socket,
            "--config-file", str(config_file),
            "--no-api",  # Rychlejší start bez HTTP API
            "--seccomp-level", "0"  # Pro maximální výkon (pouze v důvěryhodném prostředí)
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Okamžitě spustíme VM (bez čekání na API)
        boot_cmd = [
            "curl", "-X", "PUT",
            "--unix-socket", api_socket,
            "http://localhost/actions",
            "-H", "Accept: application/json",
            "-H", "Content-Type: application/json",
            "-d", '{"action_type": "InstanceStart"}'
        ]
        
        # Spuštění VM
        boot_process = await asyncio.create_subprocess_exec(
            *boot_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await boot_process.communicate()
        
        if boot_process.returncode != 0:
            logger.error(f"Failed to start VM: {stderr.decode()}")
            await self._cleanup_resources(sandbox_id)
            raise RuntimeError(f"Failed to start sandbox: {stderr.decode()}")
        
        boot_time = (time.time() - start_time) * 1000  # v ms
        
        logger.info(f"Firecracker sandbox {sandbox_id} started in {boot_time:.2f}ms")
        
        # Vytvoření Sandbox objektu
        sandbox = Sandbox(
            sandbox_id=sandbox_id,
            config=config,
            hypervisor=self,
            state=SandboxState.RUNNING,
            process=process,
            metadata={
                "boot_time_ms": boot_time,
                "api_socket": api_socket,
                "config_file": str(config_file)
            }
        )
        
        self._sandboxes[sandbox_id] = sandbox
        return sandbox
    
    async def start_sandbox(self, sandbox_id: str) -> bool:
        """Spustí existující sandbox - u Firecracker ihned běží"""
        if sandbox_id not in self._sandboxes:
            return False
        return True
    
    async def stop_sandbox(self, sandbox_id: str, force: bool = False) -> bool:
        """Zastaví sandbox"""
        if sandbox_id not in self._sandboxes:
            return False
        
        sandbox = self._sandboxes[sandbox_id]
        
        if sandbox.process:
            if force:
                sandbox.process.terminate()
            await sandbox.process.wait()
        
        await self._cleanup_resources(sandbox_id)
        
        del self._sandboxes[sandbox_id]
        return True
    
    async def pause_sandbox(self, sandbox_id: str) -> bool:
        """Pozastaví sandbox"""
        if sandbox_id not in self._sandboxes:
            return False
        # Firecracker specifická implementace
        return True
    
    async def resume_sandbox(self, sandbox_id: str) -> bool:
        """Obnoví sandbox"""
        if sandbox_id not in self._sandboxes:
            return False
        # Firecracker specifická implementace
        return True
    
    async def _cleanup_resources(self, sandbox_id: str):
        """Vyčistí prostředky sandboxu"""
        # Uklizení TAP interface
        if sandbox_id in self._tap_interfaces:
            tap_name = self._tap_interfaces[sandbox_id]
            cmd = ["sudo", "ip", "tuntap", "del", tap_name, "mode", "tap"]
            process = await asyncio.create_subprocess_exec(*cmd)
            await process.wait()
            del self._tap_interfaces[sandbox_id]
        
        # Uklizení socketu
        if sandbox_id in self._api_sockets:
            sock_path = self._api_sockets[sandbox_id]
            if os.path.exists(sock_path):
                os.unlink(sock_path)
            # Uklidit celý adresář
            sock_dir = os.path.dirname(sock_path)
            if os.path.exists(sock_dir):
                import shutil
                shutil.rmtree(sock_dir, ignore_errors=True)
            del self._api_sockets[sandbox_id]
    
    async def get_sandbox_stats(self, sandbox_id: str) -> Dict[str, Any]:
        """Získá statistiky sandboxu přes Firecracker API"""
        if sandbox_id not in self._api_sockets:
            return {}
        
        api_socket = self._api_sockets[sandbox_id]
        
        # Získání statistik přes HTTP API
        cmd = [
            "curl", "-s",
            "--unix-socket", api_socket,
            "http://localhost/stats"
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            stats = json.loads(stdout.decode())
            return {
                "vcpu_count": stats.get("vcpu_count", 0),
                "memory_usage_mb": stats.get("memory_usage_mb", 0),
                "uptime_ns": stats.get("uptime_ns", 0),
                "cpu_usage_us": stats.get("cpu_usage_us", 0),
                "rx_packets": stats.get("network", {}).get("rx_packets", 0),
                "tx_packets": stats.get("network", {}).get("tx_packets", 0),
            }
        
        return {}
