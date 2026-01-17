"""
Jednotkové testy pro NovaSandbox
"""
import pytest
import asyncio
from pathlib import Path
import sys

# Přidání root adresáře do path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import SandboxConfig, SandboxState, Sandbox
from core.template_manager import TemplateManager
import logging

logger = logging.getLogger(__name__)


class TestSandboxConfig:
    """Testy konfigurace sandboxu"""
    
    def test_default_config(self):
        """Test výchozích hodnot konfigurace"""
        config = SandboxConfig()
        
        assert config.template_id == "alpine-python"
        assert config.memory_mb == 512
        assert config.vcpus == 2
        assert config.boot_timeout_ms == 5000
        assert config.enable_network is True
        assert config.guest_port == 8080
    
    def test_custom_config(self):
        """Test vlastní konfigurace"""
        config = SandboxConfig(
            template_id="custom",
            memory_mb=1024,
            vcpus=4,
            enable_network=False
        )
        
        assert config.template_id == "custom"
        assert config.memory_mb == 1024
        assert config.vcpus == 4
        assert config.enable_network is False
    
    def test_extra_drives(self):
        """Test přidávání extra disků"""
        config = SandboxConfig()
        config.extra_drives = [
            {"path": "/dev/sda", "readonly": False},
            {"path": "/dev/sdb", "readonly": True}
        ]
        
        assert len(config.extra_drives) == 2
        assert config.extra_drives[0]["readonly"] is False
        assert config.extra_drives[1]["readonly"] is True
    
    def test_labels(self):
        """Test přidávání labelů"""
        config = SandboxConfig()
        config.labels = {
            "app": "test",
            "version": "1.0"
        }
        
        assert config.labels["app"] == "test"
        assert config.labels["version"] == "1.0"


class TestTemplateManager:
    """Testy správce šablon"""
    
    def test_template_manager_init(self):
        """Test inicializace Template Manageru"""
        manager = TemplateManager("templates")
        assert manager.templates_dir == Path("templates")
    
    def test_list_templates(self):
        """Test výpisu dostupných šablon"""
        manager = TemplateManager("templates")
        templates = manager.list_templates()
        
        assert isinstance(templates, list)
        # Pokud templates/ existuje a obsahuje alpine-python
        if manager.templates_dir.exists():
            # Test bude záviset na obsahu
            logger.info(f"Found templates: {templates}")


class TestSandboxState:
    """Testy stavů sandboxu"""
    
    def test_sandbox_states(self):
        """Test všech stavů sandboxu"""
        states = [
            SandboxState.CREATED,
            SandboxState.STARTING,
            SandboxState.RUNNING,
            SandboxState.PAUSED,
            SandboxState.STOPPED,
            SandboxState.ERROR
        ]
        
        assert len(states) == 6
        assert SandboxState.RUNNING.value == "running"


class TestSandboxObject:
    """Testy Sandbox objektu"""
    
    def test_sandbox_creation(self):
        """Test vytvoření Sandbox objektu"""
        config = SandboxConfig()
        
        # Vytvoření mock hypervisoru
        from unittest.mock import AsyncMock, MagicMock
        mock_hypervisor = MagicMock()
        
        sandbox = Sandbox(
            sandbox_id="test_123",
            config=config,
            hypervisor=mock_hypervisor,
            state=SandboxState.CREATED
        )
        
        assert sandbox.sandbox_id == "test_123"
        assert sandbox.config == config
        assert sandbox.state == SandboxState.CREATED
        assert sandbox.created_at > 0
    
    def test_sandbox_is_running(self):
        """Test kontroly běhu sandboxu"""
        config = SandboxConfig()
        from unittest.mock import MagicMock
        mock_hypervisor = MagicMock()
        
        sandbox = Sandbox(
            sandbox_id="test_123",
            config=config,
            hypervisor=mock_hypervisor,
            state=SandboxState.RUNNING
        )
        
        assert sandbox.is_running() is True
        
        sandbox.state = SandboxState.STOPPED
        assert sandbox.is_running() is False


@pytest.mark.asyncio
async def test_sandbox_uptime():
    """Test výpočtu doby běhu"""
    import time
    config = SandboxConfig()
    from unittest.mock import MagicMock
    mock_hypervisor = MagicMock()
    
    sandbox = Sandbox(
        sandbox_id="test_123",
        config=config,
        hypervisor=mock_hypervisor,
        state=SandboxState.RUNNING
    )
    
    # Čekání na chvíli
    await asyncio.sleep(0.1)
    
    uptime = sandbox.get_uptime_ms()
    assert uptime > 100  # Minimálně 100ms


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
