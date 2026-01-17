"""
Základní příklad použití NovaSandbox
"""
import asyncio
import sys
from pathlib import Path

# Přidání root adresáře do path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import Sandbox, SandboxConfig, SandboxState
from providers import FirecrackerHypervisor, AppleVZHypervisor
import platform
import logging

# Nastavení loggingu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Základní příklad vytvoření a spuštění sandboxu"""
    
    # Výběr správného hypervisoru podle platformy
    system = platform.system()
    
    if system == "Linux":
        logger.info("Inicialisace Firecracker hypervisoru (Linux)")
        try:
            hypervisor = FirecrackerHypervisor()
        except FileNotFoundError:
            logger.error("Firecracker není nainstalován. Instalace: https://github.com/firecracker-microvm/firecracker")
            return
    elif system == "Darwin":
        logger.info("Inicialisace Apple VZ hypervisoru (macOS)")
        hypervisor = AppleVZHypervisor()
    else:
        logger.error(f"Nepodporovaná platforma: {system}")
        return
    
    # Vytvoření konfigurace sandboxu
    config = SandboxConfig(
        template_id="alpine-python",
        memory_mb=512,
        vcpus=2,
        enable_network=True,
    )
    
    try:
        # Vytvoření a spuštění sandboxu
        logger.info("Vytváření sandboxu...")
        sandbox = await hypervisor.create_sandbox(config)
        
        logger.info(f"Sandbox vytvořen: {sandbox.sandbox_id}")
        logger.info(f"Stav: {sandbox.state.value}")
        logger.info(f"Boot čas: {sandbox.metadata.get('boot_time_ms', 'N/A'):.2f}ms")
        
        # Ověření, že sandbox běží
        assert sandbox.is_running(), "Sandbox by měl běžet"
        logger.info("✓ Sandbox je spuštěn")
        
        # Získání statistik
        stats = await sandbox.get_stats()
        logger.info(f"Statistiky: {stats}")
        
        # Pozastavení (pokud je podporováno)
        logger.info("Pozastavování sandboxu...")
        paused = await sandbox.pause()
        if paused:
            logger.info("✓ Sandbox je pozastaven")
            
            # Obnovení
            logger.info("Obnovování sandboxu...")
            resumed = await sandbox.resume()
            if resumed:
                logger.info("✓ Sandbox je obnoven")
        
        # Zastavení sandboxu
        logger.info("Zastavování sandboxu...")
        stopped = await sandbox.stop()
        if stopped:
            logger.info("✓ Sandbox je zastaven")
        
    except FileNotFoundError as e:
        logger.error(f"Chyba při hledání šablony: {e}")
        logger.info("Vytvořte adresář templates/ se šablonami vmlinux a rootfs.ext4")
    except Exception as e:
        logger.error(f"Chyba při práci se sandboxem: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
