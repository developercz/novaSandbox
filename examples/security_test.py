#!/usr/bin/env python3
"""
Bezpečnostní testy NovaSandbox
Testuje různé útočné vektory a ověřuje ochranu
"""
import asyncio
import sys
from dataclasses import dataclass
from novasandbox.core import SandboxConfig, SecurityLevel, Sandbox
from novasandbox.core.security import SecurityPolicy, SandboxSecurityManager

@dataclass
class SecurityTest:
    name: str
    attack_type: str
    command: str
    expected_blocked: bool
    security_level: SecurityLevel

# Sada bezpečnostních testů
SECURITY_TESTS = [
    # Host breakout pokusy
    SecurityTest(
        name="Breakout: Přístup k /host",
        attack_type="host_breakout",
        command="ls -la /host",
        expected_blocked=True,
        security_level=SecurityLevel.STANDARD
    ),
    SecurityTest(
        name="Breakout: Directory traversal",
        attack_type="host_breakout",
        command="cat /../../../etc/passwd",
        expected_blocked=True,
        security_level=SecurityLevel.STANDARD
    ),
    SecurityTest(
        name="Breakout: ptrace syscall",
        attack_type="privilege_escalation",
        command="strace -p 1",
        expected_blocked=True,
        security_level=SecurityLevel.STRICT
    ),
    
    # Privilege escalation
    SecurityTest(
        name="Privilege: setuid binary",
        attack_type="privilege_escalation",
        command="sudo -i",
        expected_blocked=True,
        security_level=SecurityLevel.STRICT
    ),
    SecurityTest(
        name="Privilege: Access to /proc/sys",
        attack_type="privilege_escalation",
        command="cat /proc/sys/kernel/sysrq",
        expected_blocked=True,
        security_level=SecurityLevel.PARANOID
    ),
    
    # DOS prevence
    SecurityTest(
        name="DOS: Fork bomb fork()",
        attack_type="dos",
        command=":() { : | : & }; :",
        expected_blocked=True,
        security_level=SecurityLevel.STRICT
    ),
    SecurityTest(
        name="DOS: Memory exhaustion",
        attack_type="dos",
        command="python -c 'import os; os.urandom(2**30)'",
        expected_blocked=True,
        security_level=SecurityLevel.STANDARD
    ),
    
    # Network exploitation
    SecurityTest(
        name="Network: Connect to blocked IP",
        attack_type="network_exploit",
        command="nc -zv 192.168.1.1 22",
        expected_blocked=True,
        security_level=SecurityLevel.STANDARD
    ),
    SecurityTest(
        name="Network: Raw socket",
        attack_type="network_exploit",
        command="python -c 'import socket; socket.socket(socket.AF_INET, socket.SOCK_RAW)'",
        expected_blocked=True,
        security_level=SecurityLevel.STRICT
    ),
    
    # Kernel module injection
    SecurityTest(
        name="Code injection: insmod",
        attack_type="code_injection",
        command="insmod malicious.ko",
        expected_blocked=True,
        security_level=SecurityLevel.STRICT
    ),
    SecurityTest(
        name="Code injection: module_load",
        attack_type="code_injection",
        command="modprobe evil_module",
        expected_blocked=True,
        security_level=SecurityLevel.STRICT
    ),
]

class SecurityTestRunner:
    """Nástroj pro běh bezpečnostních testů"""
    
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
    
    async def run_test(self, test: SecurityTest):
        """Spustí jeden bezpečnostní test"""
        print(f"\n🔒 Test: {test.name}")
        print(f"   Attack type: {test.attack_type}")
        print(f"   Command: {test.command}")
        print(f"   Expected blocked: {test.expected_blocked}")
        print(f"   Security level: {test.security_level.value}")
        
        # Simulace testu (v produkci by se spustilo v reálném sandboxu)
        try:
            # Vytvořit security manager
            policy = self._get_policy_for_level(test.security_level)
            manager = SandboxSecurityManager("test_sandbox", policy)
            
            # Ověřit podle typu útoku
            allowed = self._simulate_attack(test, manager)
            
            # Porovnat výsledek s očekáváním
            success = allowed != test.expected_blocked
            
            if success:
                self.passed += 1
                status = "✅ PASS"
            else:
                self.failed += 1
                status = "❌ FAIL"
            
            violations = manager.get_violations_summary()
            
            result = {
                'test': test.name,
                'status': status,
                'success': success,
                'violations': violations['total_violations'],
                'blocked': not allowed
            }
            
            self.results.append(result)
            print(f"   {status} (Violations: {violations['total_violations']})")
            
        except Exception as e:
            self.failed += 1
            print(f"   ❌ FAIL (Exception: {str(e)})")
            self.results.append({
                'test': test.name,
                'status': '❌ FAIL',
                'success': False,
                'error': str(e)
            })
    
    def _get_policy_for_level(self, level: SecurityLevel) -> SecurityPolicy:
        """Vrátí politiku pro danou úroveň"""
        from novasandbox.core.security import DEFAULT_POLICIES
        return DEFAULT_POLICIES[level]
    
    def _simulate_attack(self, test: SecurityTest, manager: SandboxSecurityManager) -> bool:
        """Simuluje útok a vrátí, zda je povolen"""
        
        if test.attack_type == "host_breakout":
            # Pokus přistupovat k /host nebo ../
            if "/host" in test.command or "/../" in test.command:
                return manager.check_file_access("/host/etc/passwd", "read")
        
        elif test.attack_type == "privilege_escalation":
            # Kontrola přístupu k ptrace
            if "strace" in test.command or "ptrace" in test.command:
                return manager.check_syscall("ptrace")
            # Kontrola setuid
            elif "sudo" in test.command:
                return manager.policy.allow_setuid
            # Kontrola /proc/sys
            elif "/proc/sys" in test.command:
                return manager.check_file_access("/proc/sys/kernel/sysrq", "read")
        
        elif test.attack_type == "dos":
            # Fork bomb
            if "fork" in test.command or ":" in test.command:
                return manager.check_syscall("fork") or manager.check_syscall("clone")
            # Memory exhaustion
            elif "urandom" in test.command or "memory" in test.command:
                return manager.policy.max_memory_mb > 512  # Teoreticky
        
        elif test.attack_type == "network_exploit":
            # Pokus na blokovanou IP
            if "192.168.1.1" in test.command:
                return manager.check_network_access("192.168.1.1", 22)
            # Raw socket
            elif "raw" in test.command or "SOCK_RAW" in test.command:
                return manager.policy.allow_raw_sockets
        
        elif test.attack_type == "code_injection":
            # Kernel module loading
            if "insmod" in test.command or "modprobe" in test.command or "module_load" in test.command:
                return manager.policy.allow_kernel_modules and manager.check_syscall("module_load")
        
        return True  # Default: povoleno
    
    def print_summary(self):
        """Vytiskne souhrn testů"""
        print("\n" + "=" * 70)
        print("📊 SHRNUTÍ BEZPEČNOSTNÍCH TESTŮ")
        print("=" * 70)
        print(f"\nCelkem testů: {len(self.results)}")
        print(f"✅ Prošly: {self.passed}")
        print(f"❌ Selhaly: {self.failed}")
        print(f"Success rate: {self.passed / len(self.results) * 100:.1f}%")
        
        # Detailní seznam
        print("\n📋 Detailní výsledky:")
        print("-" * 70)
        
        for result in self.results:
            status = result['status']
            test_name = result['test']
            violations = result.get('violations', 'N/A')
            print(f"{status} {test_name}")
            if violations and violations != 'N/A':
                print(f"    └─ Violations: {violations}")
        
        print("\n" + "=" * 70)
        
        if self.failed == 0:
            print("✅ VŠECHNY BEZPEČNOSTNÍ TESTY PROŠLY!")
            print("🔒 Systém je správně zabezpečen")
        else:
            print(f"⚠️  {self.failed} testů selhalo")
            print("🔴 Je třeba zlepšit bezpečnost")
        
        print("=" * 70)
    
    async def run_all_tests(self):
        """Spustí všechny testy"""
        print("\n" + "=" * 70)
        print("🔐 NOVASANDBOX SECURITY TEST SUITE")
        print("=" * 70)
        print(f"Testů k běhu: {len(SECURITY_TESTS)}")
        
        for test in SECURITY_TESTS:
            await self.run_test(test)
        
        self.print_summary()

async def main():
    """Hlavní funkce"""
    runner = SecurityTestRunner()
    await runner.run_all_tests()
    
    # Vrátit exit code podle výsledků
    return 0 if runner.failed == 0 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
