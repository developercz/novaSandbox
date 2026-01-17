"""
Bezpečnostní modul pro NovaSandbox.
Prevence breakoutu, DOS útoků a neautorizovaného přístupu.
"""
import logging
import time
from dataclasses import dataclass
from typing import Dict, Optional, Set
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Úrovně bezpečnosti"""
    BASIC = "basic"              # Minimální - jen izolace
    STANDARD = "standard"        # Doporučené - s limity
    STRICT = "strict"            # Přísné - SELinux-like pravidla
    PARANOID = "paranoid"        # Maximum - všechny kontroly


@dataclass
class SecurityPolicy:
    """Bezpečnostní politika pro sandbox"""
    
    # Úroveň bezpečnosti
    level: SecurityLevel = SecurityLevel.STANDARD
    
    # Resource limity (DOS prevence)
    max_memory_mb: int = 2048
    max_vcpus: int = 8
    max_processes: int = 1000
    max_open_files: int = 1024
    max_network_connections: int = 500
    
    # Filesystem omezení
    allow_host_mount: bool = False  # Přístup k hostiteli FS
    readonly_rootfs: bool = False
    allowed_devices: Set[str] = None  # /dev/null, /dev/zero, ...
    
    # Network omezení
    allow_raw_sockets: bool = False
    allowed_ports: Set[int] = None     # None = jakýkoliv port
    blocked_ips: Set[str] = None
    rate_limit_mbps: int = 1000
    
    # Execution omezení
    allowed_syscalls: Set[str] = None  # None = všechny
    allow_ptrace: bool = False         # Debug/escape prevence
    allow_setuid: bool = False         # Privilege escalation
    allow_kernel_modules: bool = False
    
    # Kontrola obsahu
    enable_seccomp: bool = True        # Syscall filtering
    enable_apparmor: bool = True       # Mandatory access control
    enable_cgroups: bool = True        # Resource accounting
    
    # Audit & monitoring
    log_syscalls: bool = False
    log_network: bool = False
    kill_on_violation: bool = True
    
    def __post_init__(self):
        if self.allowed_devices is None:
            self.allowed_devices = {"/dev/null", "/dev/zero", "/dev/urandom"}
        if self.blocked_ips is None:
            self.blocked_ips = set()


class RateLimiter:
    """Rate limiter pro DOS ochranu"""
    
    def __init__(self, limit_per_second: int = 1000):
        self.limit = limit_per_second
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, sandbox_id: str, resource_id: str = "default") -> bool:
        """Ověří, zda je request povolen"""
        key = f"{sandbox_id}:{resource_id}"
        now = time.time()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Vyčistí staré requesty (starší než 1 sekunda)
        self.requests[key] = [
            req_time for req_time in self.requests[key] 
            if now - req_time < 1.0
        ]
        
        if len(self.requests[key]) >= self.limit:
            logger.warning(f"Rate limit exceeded for {key}")
            return False
        
        self.requests[key].append(now)
        return True


class SandboxSecurityManager:
    """Správce bezpečnosti pro jednotlivé sandoxy"""
    
    def __init__(self, sandbox_id: str, policy: SecurityPolicy):
        self.sandbox_id = sandbox_id
        self.policy = policy
        self.created_at = time.time()
        self.violations: list = []
        self.rate_limiter = RateLimiter(limit_per_second=10000)
        self._syscall_log = []
    
    def validate_config(self, config_dict: dict) -> bool:
        """Ověří konfiguraci proti politice"""
        errors = []
        
        # Ověření resource limitů
        if config_dict.get('memory_mb', 0) > self.policy.max_memory_mb:
            errors.append(f"Memory {config_dict['memory_mb']}MB exceeds max {self.policy.max_memory_mb}MB")
        
        if config_dict.get('vcpus', 0) > self.policy.max_vcpus:
            errors.append(f"vCPU {config_dict['vcpus']} exceeds max {self.policy.max_vcpus}")
        
        if errors:
            for error in errors:
                logger.warning(f"[{self.sandbox_id}] Config violation: {error}")
                self.violations.append({
                    'type': 'config_violation',
                    'message': error,
                    'timestamp': time.time()
                })
            
            if self.policy.level == SecurityLevel.PARANOID:
                return False
        
        return True
    
    def check_syscall(self, syscall_name: str) -> bool:
        """Ověří, zda je syscall povolen"""
        if self.policy.allowed_syscalls is None:
            # Všechny syscalls povoleny
            if self.policy.log_syscalls:
                self._syscall_log.append({
                    'syscall': syscall_name,
                    'timestamp': time.time(),
                    'allowed': True
                })
            return True
        
        allowed = syscall_name in self.policy.allowed_syscalls
        
        if self.policy.log_syscalls:
            self._syscall_log.append({
                'syscall': syscall_name,
                'timestamp': time.time(),
                'allowed': allowed
            })
        
        if not allowed:
            violation = {
                'type': 'syscall_violation',
                'syscall': syscall_name,
                'timestamp': time.time()
            }
            self.violations.append(violation)
            logger.warning(f"[{self.sandbox_id}] Blocked syscall: {syscall_name}")
            
            if self.policy.kill_on_violation:
                logger.error(f"[{self.sandbox_id}] Killing sandbox due to syscall violation")
                return False
        
        return True
    
    def check_network_access(self, dest_ip: str, dest_port: int) -> bool:
        """Ověří povolení síťového přístupu"""
        # Kontrola IP blacklistu
        if dest_ip in self.policy.blocked_ips:
            violation = {
                'type': 'network_violation',
                'reason': 'blocked_ip',
                'ip': dest_ip,
                'timestamp': time.time()
            }
            self.violations.append(violation)
            logger.warning(f"[{self.sandbox_id}] Blocked IP: {dest_ip}")
            return False
        
        # Kontrola povolených portů
        if self.policy.allowed_ports is not None:
            if dest_port not in self.policy.allowed_ports:
                violation = {
                    'type': 'network_violation',
                    'reason': 'port_not_allowed',
                    'port': dest_port,
                    'timestamp': time.time()
                }
                self.violations.append(violation)
                logger.warning(f"[{self.sandbox_id}] Blocked port: {dest_port}")
                return False
        
        # Rate limiting
        if not self.rate_limiter.is_allowed(self.sandbox_id, f"net:{dest_ip}:{dest_port}"):
            violation = {
                'type': 'rate_limit_violation',
                'ip': dest_ip,
                'port': dest_port,
                'timestamp': time.time()
            }
            self.violations.append(violation)
            logger.warning(f"[{self.sandbox_id}] Rate limit exceeded for {dest_ip}:{dest_port}")
            return False
        
        return True
    
    def check_file_access(self, file_path: str, mode: str = 'read') -> bool:
        """Ověří povolení přístupu k souboru"""
        if self.policy.allow_host_mount:
            return True
        
        # Zákaz přístupu k hostiteli mimo sandbox
        if file_path.startswith('/host') or file_path.startswith('/../'):
            violation = {
                'type': 'file_access_violation',
                'path': file_path,
                'mode': mode,
                'reason': 'host_breakout_attempt',
                'timestamp': time.time()
            }
            self.violations.append(violation)
            logger.error(f"[{self.sandbox_id}] Breakout attempt blocked: {file_path}")
            
            if self.policy.kill_on_violation:
                return False
        
        return True
    
    def get_violations_summary(self) -> dict:
        """Vrátí souhrn porušení"""
        return {
            'sandbox_id': self.sandbox_id,
            'total_violations': len(self.violations),
            'created_at': self.created_at,
            'lifetime_seconds': time.time() - self.created_at,
            'violations': self.violations[-100:],  # Posledních 100
            'syscall_log_size': len(self._syscall_log)
        }


class HostSecurityHardening:
    """Hardening bezpečnosti hostitele"""
    
    @staticmethod
    def get_firecracker_seccomp_rules() -> Dict[str, list]:
        """Pravidla pro Firecracker seccomp"""
        return {
            "defaultAction": "SCMP_ACT_ALLOW",
            "defaultErrnoRet": 1,
            "archMap": [
                {
                    "architecture": "SCMP_ARCH_X86_64",
                    "subArchitectures": [
                        "SCMP_ARCH_X86",
                        "SCMP_ARCH_X32"
                    ]
                }
            ],
            "syscalls": [
                # Zákaz nebezpečných syscalls
                {
                    "names": ["ptrace", "clone", "fork", "vfork"],
                    "action": "SCMP_ACT_ERRNO",
                    "errnoRet": 1,
                    "comment": "Disable process spawning and debugging"
                },
                {
                    "names": ["mount", "umount2"],
                    "action": "SCMP_ACT_ERRNO",
                    "errnoRet": 1,
                    "comment": "Disable mount operations"
                },
                {
                    "names": ["module_load"],
                    "action": "SCMP_ACT_ERRNO",
                    "errnoRet": 1,
                    "comment": "Disable kernel module loading"
                }
            ]
        }
    
    @staticmethod
    def get_cgroup_limits(config) -> Dict[str, str]:
        """Cgroup limity pro resource control"""
        return {
            "memory.limit_in_bytes": str(config.memory_mb * 1024 * 1024),
            "cpuset.cpus": f"0-{config.vcpus - 1}",
            "pids.max": str(config.max_processes),
            "net.ipv4.tcp_max_syn_backlog": "100",
        }


# Výchozí politiky pro různé use-case
DEFAULT_POLICIES = {
    SecurityLevel.BASIC: SecurityPolicy(
        level=SecurityLevel.BASIC,
        enable_seccomp=False,
        enable_apparmor=False,
        kill_on_violation=False
    ),
    SecurityLevel.STANDARD: SecurityPolicy(
        level=SecurityLevel.STANDARD,
        max_memory_mb=2048,
        max_vcpus=4,
        max_network_connections=100,
        enable_seccomp=True,
        enable_apparmor=True,
        kill_on_violation=False
    ),
    SecurityLevel.STRICT: SecurityPolicy(
        level=SecurityLevel.STRICT,
        max_memory_mb=1024,
        max_vcpus=2,
        max_network_connections=10,
        allow_raw_sockets=False,
        allow_ptrace=False,
        allow_setuid=False,
        enable_seccomp=True,
        enable_apparmor=True,
        kill_on_violation=True,
        log_syscalls=True
    ),
    SecurityLevel.PARANOID: SecurityPolicy(
        level=SecurityLevel.PARANOID,
        max_memory_mb=512,
        max_vcpus=1,
        max_network_connections=5,
        readonly_rootfs=True,
        allow_host_mount=False,
        allow_raw_sockets=False,
        allow_ptrace=False,
        allow_setuid=False,
        allow_kernel_modules=False,
        enable_seccomp=True,
        enable_apparmor=True,
        kill_on_violation=True,
        log_syscalls=True,
        log_network=True
    )
}
