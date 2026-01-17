#!/usr/bin/env python3
"""
Performance test suite pro NovaSandbox
Měří časy lokálních operací bez závislosti na hypervisorech
"""
import asyncio
import time
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import statistics

# Přidání root adresáře do path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import SandboxConfig, SandboxState, TemplateManager, Sandbox
from unittest.mock import MagicMock

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceTester:
    """Test nástroj pro měření výkonu NovaSandbox"""
    
    def __init__(self):
        self.results: Dict[str, List[float]] = {}
    
    def measure(self, operation_name: str, func, iterations: int = 100):
        """Měří čas operace a zaznamenává výsledky"""
        times = []
        
        print(f"\n⏱️  Měření: {operation_name}")
        print(f"   Iterací: {iterations}")
        
        for i in range(iterations):
            start = time.perf_counter()
            func()
            end = time.perf_counter()
            elapsed = (end - start) * 1000  # v ms
            times.append(elapsed)
            
            if (i + 1) % max(1, iterations // 10) == 0:
                print(f"   Progress: {i + 1}/{iterations}")
        
        self.results[operation_name] = times
        self._print_stats(operation_name, times)
    
    async def measure_async(self, operation_name: str, func, iterations: int = 100):
        """Měří čas asynchronní operace"""
        times = []
        
        print(f"\n⏱️  Měření: {operation_name} (async)")
        print(f"   Iterací: {iterations}")
        
        for i in range(iterations):
            start = time.perf_counter()
            await func()
            end = time.perf_counter()
            elapsed = (end - start) * 1000  # v ms
            times.append(elapsed)
            
            if (i + 1) % max(1, iterations // 10) == 0:
                print(f"   Progress: {i + 1}/{iterations}")
        
        self.results[operation_name] = times
        self._print_stats(operation_name, times)
    
    def _print_stats(self, name: str, times: List[float]):
        """Tiskne statistiky pro operaci"""
        if not times:
            return
        
        min_time = min(times)
        max_time = max(times)
        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        stdev = statistics.stdev(times) if len(times) > 1 else 0
        
        print(f"\n   📊 Statistiky pro: {name}")
        print(f"      Min:    {min_time:.3f}ms")
        print(f"      Max:    {max_time:.3f}ms")
        print(f"      Avg:    {avg_time:.3f}ms")
        print(f"      Median: {median_time:.3f}ms")
        print(f"      StDev:  {stdev:.3f}ms")
    
    def print_summary(self):
        """Tiskne souhrn všech výsledků"""
        print("\n" + "="*60)
        print("📈 SHRNUTÍ VÝKONU")
        print("="*60)
        
        for operation, times in self.results.items():
            avg = statistics.mean(times)
            median = statistics.median(times)
            print(f"\n{operation:40} | Avg: {avg:7.3f}ms | Median: {median:7.3f}ms")
    
    def compare_to_target(self):
        """Porovnává výsledky s cílovými hodnotami"""
        print("\n" + "="*60)
        print("🎯 POROVNÁNÍ S CÍLOVÝMI HODNOTAMI")
        print("="*60)
        
        targets = {
            "Config creation": 1.0,      # < 1ms
            "Sandbox creation": 5.0,     # < 5ms (bez hypervisoru)
            "State change": 0.5,         # < 0.5ms
        }
        
        for operation, times in self.results.items():
            avg = statistics.mean(times)
            
            for target_name, target_time in targets.items():
                if target_name.lower() in operation.lower():
                    status = "✅ PASS" if avg < target_time else "❌ FAIL"
                    print(f"\n{operation:40}")
                    print(f"  Cíl:       {target_time:.3f}ms")
                    print(f"  Dosaženo:  {avg:.3f}ms")
                    print(f"  Status:    {status}")


async def run_tests():
    """Spuštění všech testů"""
    tester = PerformanceTester()
    
    print("\n" + "="*60)
    print("🚀 NOVASANDBOX PERFORMANCE TEST")
    print("="*60)
    print(f"Platforma: {sys.platform}")
    print(f"Python: {sys.version.split()[0]}")
    
    # ========== TEST 1: Config creation ==========
    def create_config():
        return SandboxConfig(
            template_id="alpine-python",
            memory_mb=512,
            vcpus=2,
            enable_network=True,
            labels={"test": "value"}
        )
    
    tester.measure("Config creation", create_config, iterations=1000)
    
    # ========== TEST 2: Config with extra drives ==========
    def create_config_with_drives():
        config = SandboxConfig(memory_mb=512)
        config.extra_drives = [
            {"path": f"/dev/sda{i}", "readonly": i % 2 == 0}
            for i in range(10)
        ]
        return config
    
    tester.measure("Config creation (with drives)", create_config_with_drives, iterations=500)
    
    # ========== TEST 3: Sandbox object creation ==========
    def create_sandbox():
        config = SandboxConfig()
        mock_hypervisor = MagicMock()
        return Sandbox(
            sandbox_id="test_123",
            config=config,
            hypervisor=mock_hypervisor,
            state=SandboxState.RUNNING
        )
    
    tester.measure("Sandbox creation", create_sandbox, iterations=500)
    
    # ========== TEST 4: Sandbox state checks ==========
    def check_sandbox_state():
        config = SandboxConfig()
        mock_hypervisor = MagicMock()
        sandbox = Sandbox(
            sandbox_id="test_123",
            config=config,
            hypervisor=mock_hypervisor,
            state=SandboxState.RUNNING
        )
        return sandbox.is_running()
    
    tester.measure("State check (is_running)", check_sandbox_state, iterations=1000)
    
    # ========== TEST 5: Uptime calculation ==========
    def get_uptime():
        config = SandboxConfig()
        mock_hypervisor = MagicMock()
        sandbox = Sandbox(
            sandbox_id="test_123",
            config=config,
            hypervisor=mock_hypervisor,
            state=SandboxState.RUNNING
        )
        return sandbox.get_uptime_ms()
    
    tester.measure("Uptime calculation", get_uptime, iterations=1000)
    
    # ========== TEST 6: Template manager ==========
    def create_template_manager():
        return TemplateManager("templates")
    
    tester.measure("TemplateManager creation", create_template_manager, iterations=100)
    
    # ========== TEST 7: List templates ==========
    tm = TemplateManager("templates")
    def list_templates():
        return tm.list_templates()
    
    tester.measure("List templates", list_templates, iterations=100)
    
    # ========== TEST 8: Async sandbox operations ==========
    async def async_stub():
        await asyncio.sleep(0.0001)  # Minimální delay
    
    await tester.measure_async("Async operation (stub)", async_stub, iterations=200)
    
    # ========== TEST 9: Multiple sandbox creation ==========
    def create_multiple_sandboxes():
        mock_hypervisor = MagicMock()
        sandboxes = []
        for i in range(10):
            config = SandboxConfig()
            sandbox = Sandbox(
                sandbox_id=f"sandbox_{i}",
                config=config,
                hypervisor=mock_hypervisor,
                state=SandboxState.RUNNING
            )
            sandboxes.append(sandbox)
        return sandboxes
    
    tester.measure("Create 10 sandboxes", create_multiple_sandboxes, iterations=100)
    
    # ========== TEST 10: Concurrent sandbox operations ==========
    async def create_sandboxes_concurrent():
        mock_hypervisor = MagicMock()
        
        async def create_one():
            config = SandboxConfig()
            return Sandbox(
                sandbox_id=f"sandbox_{time.time()}",
                config=config,
                hypervisor=mock_hypervisor,
                state=SandboxState.RUNNING
            )
        
        tasks = [create_one() for _ in range(10)]
        return await asyncio.gather(*tasks)
    
    await tester.measure_async("Concurrent sandbox creation (10x)", 
                               create_sandboxes_concurrent, iterations=100)
    
    # ========== RESULTS ==========
    tester.print_summary()
    tester.compare_to_target()
    
    # ========== DETAILED REPORT ==========
    print("\n" + "="*60)
    print("📋 DETAILNÍ ZPRÁVA")
    print("="*60)
    
    total_tests = sum(len(times) for times in tester.results.values())
    total_time = sum(sum(times) for times in tester.results.values())
    
    print(f"\nCelkový počet operací: {total_tests}")
    print(f"Celkový čas všech testů: {total_time:.2f}ms")
    print(f"Průměrný čas na operaci: {total_time/total_tests:.4f}ms")
    
    # Slowest operations
    slowest = sorted(
        [(name, statistics.mean(times)) for name, times in tester.results.items()],
        key=lambda x: x[1],
        reverse=True
    )[:3]
    
    print("\n🐢 Nejpomalejší operace:")
    for i, (name, avg_time) in enumerate(slowest, 1):
        print(f"  {i}. {name:40} {avg_time:.3f}ms")
    
    # Fastest operations
    fastest = sorted(
        [(name, statistics.mean(times)) for name, times in tester.results.items()],
        key=lambda x: x[1]
    )[:3]
    
    print("\n🚀 Nejrychlejší operace:")
    for i, (name, avg_time) in enumerate(fastest, 1):
        print(f"  {i}. {name:40} {avg_time:.3f}ms")
    
    print("\n✅ Testy dokončeny!\n")


def main():
    """Main entry point"""
    try:
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        print("\n\n❌ Testy přerušeny uživatelem")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Chyba během testů: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
