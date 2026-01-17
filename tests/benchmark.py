"""
Benchmark testy pro výkon NovaSandbox
"""
import pytest
import asyncio
import time
from pathlib import Path
import sys

# Přidání root adresáře do path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import SandboxConfig, SandboxState
from unittest.mock import AsyncMock, MagicMock, patch
import logging

logger = logging.getLogger(__name__)


class TestBootPerformance:
    """Testy výkonu bootování"""
    
    def test_config_creation_performance(self, benchmark):
        """Benchmark vytváření konfigurace"""
        def create_config():
            return SandboxConfig(
                template_id="alpine-python",
                memory_mb=512,
                vcpus=2,
                enable_network=True
            )
        
        result = benchmark(create_config)
        assert result.memory_mb == 512
    
    def test_multiple_configs_creation(self, benchmark):
        """Benchmark vytváření více konfigurací"""
        def create_multiple():
            configs = []
            for i in range(100):
                configs.append(SandboxConfig(
                    template_id=f"template-{i}",
                    memory_mb=256 + i,
                    vcpus=1 + (i % 4)
                ))
            return configs
        
        result = benchmark(create_multiple)
        assert len(result) == 100


class TestMemoryUsage:
    """Testy paměťové spotřeby"""
    
    def test_sandbox_config_memory(self):
        """Test velikosti objektu konfigurace"""
        import sys
        config = SandboxConfig()
        size = sys.getsizeof(config)
        
        # Config by měl být relativně malý
        assert size < 1000  # méně než 1KB
        logger.info(f"SandboxConfig size: {size} bytes")
    
    def test_large_metadata_memory(self):
        """Test paměti s velkými metadaty"""
        import sys
        from core import Sandbox
        
        config = SandboxConfig()
        mock_hypervisor = MagicMock()
        
        # Vytvoření sandboxu s velkými metadaty
        large_metadata = {
            f"key_{i}": f"value_{i}" * 100
            for i in range(1000)
        }
        
        sandbox = Sandbox(
            sandbox_id="test_123",
            config=config,
            hypervisor=mock_hypervisor,
            metadata=large_metadata
        )
        
        size = sys.getsizeof(sandbox.metadata)
        logger.info(f"Large metadata size: {size} bytes")


class TestConcurrency:
    """Testy souběžnosti"""
    
    @pytest.mark.asyncio
    async def test_concurrent_config_creation(self):
        """Test souběžného vytváření konfigurací"""
        async def create_config(i):
            await asyncio.sleep(0.01)  # Simulace práce
            return SandboxConfig(
                template_id=f"template-{i}",
                memory_mb=256 + i
            )
        
        start = time.time()
        
        # Vytvoření 10 konfigurací souběžně
        tasks = [create_config(i) for i in range(10)]
        configs = await asyncio.gather(*tasks)
        
        elapsed = time.time() - start
        
        assert len(configs) == 10
        logger.info(f"Created 10 configs concurrently in {elapsed:.3f}s")
        
        # Souběžné by mělo být rychlejší než sekvenční
        # (přibližně 10x méně času než 10 * 0.01s)
        assert elapsed < 0.2  # mělo by být kolem 0.11s
    
    @pytest.mark.asyncio
    async def test_concurrent_sandbox_operations(self):
        """Test souběžných operací na sandboxech"""
        from core import Sandbox
        
        async def get_uptime(sandbox):
            await asyncio.sleep(0.01)
            return sandbox.get_uptime_ms()
        
        # Vytvoření mehrere sandboxů
        sandboxes = []
        mock_hypervisor = MagicMock()
        
        for i in range(5):
            sandbox = Sandbox(
                sandbox_id=f"sandbox_{i}",
                config=SandboxConfig(),
                hypervisor=mock_hypervisor,
                state=SandboxState.RUNNING
            )
            sandboxes.append(sandbox)
        
        # Souběžné získávání uptime
        tasks = [get_uptime(sb) for sb in sandboxes]
        uptimes = await asyncio.gather(*tasks)
        
        assert len(uptimes) == 5
        assert all(ut > 0 for ut in uptimes)


class TestScalability:
    """Testy škálovatelnosti"""
    
    def test_many_sandboxes_config(self, benchmark):
        """Test vytváření konfigurací pro více sandboxů"""
        def create_many_configs():
            configs = {}
            for i in range(1000):
                configs[f"sandbox_{i}"] = SandboxConfig(
                    memory_mb=256 + (i % 256),
                    vcpus=1 + (i % 8)
                )
            return configs
        
        result = benchmark(create_many_configs)
        assert len(result) == 1000
    
    def test_large_extra_drives_config(self):
        """Test konfigurace s mnoha extra disky"""
        config = SandboxConfig()
        
        # Přidání 100 extra disků
        config.extra_drives = [
            {
                "path": f"/dev/sda{i}",
                "readonly": i % 2 == 0
            }
            for i in range(100)
        ]
        
        assert len(config.extra_drives) == 100
        
        # Zkontrolovat všechny disky
        for i, drive in enumerate(config.extra_drives):
            assert drive["path"] == f"/dev/sda{i}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--benchmark-only"])
