"""
Advanced example: REST API server pro NovaSandbox
Umožňuje správu sandboxů přes HTTP API
"""
import asyncio
import logging
from typing import Dict, List, Optional
import sys
from pathlib import Path

# Přidání root adresáře do path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks
    from fastapi.responses import JSONResponse
    import uvicorn
except ImportError:
    print("FastAPI je vyžadován pro tento příklad.")
    print("Instalace: pip install fastapi uvicorn")
    sys.exit(1)

from core import SandboxConfig, SandboxState, TemplateManager
from providers import FirecrackerHypervisor, AppleVZHypervisor
import platform

# Nastavení loggingu
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializace FastAPI app
app = FastAPI(
    title="NovaSandbox API",
    description="REST API pro správu microVM",
    version="0.1.0"
)

# Globální stav
hypervisor = None
sandboxes_registry: Dict[str, dict] = {}
template_manager = TemplateManager("templates")


@app.on_event("startup")
async def startup_event():
    """Inicializace hypervisoru při startu"""
    global hypervisor
    
    system = platform.system()
    logger.info(f"Inicializace na platformě: {system}")
    
    try:
        if system == "Linux":
            hypervisor = FirecrackerHypervisor()
        elif system == "Darwin":
            hypervisor = AppleVZHypervisor()
        else:
            raise RuntimeError(f"Nepodporovaná platforma: {system}")
        
        logger.info("Hypervisor inicializován úspěšně")
    except Exception as e:
        logger.error(f"Chyba při inicializaci: {e}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "NovaSandbox API",
        "version": "0.1.0",
        "platform": platform.system(),
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "sandboxes_count": len(sandboxes_registry)
    }


# ============= Templates endpoints =============

@app.get("/templates")
async def list_templates():
    """Výpis dostupných šablon"""
    templates = template_manager.list_templates()
    return {
        "templates": templates,
        "count": len(templates)
    }


@app.get("/templates/{template_id}")
async def get_template(template_id: str):
    """Podrobnosti o konkrétní šabloně"""
    template = template_manager.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {
        "id": template.template_id,
        "name": template.name,
        "description": template.description,
        "os_type": template.os_type,
        "memory_mb": template.memory_mb,
        "vcpus": template.vcpus,
        "boot_time_ms": template.boot_time_ms,
        "disk_size_gb": template.disk_size_gb,
        "kernel_version": template.kernel_version,
        "files": template.files
    }


# ============= Sandboxes endpoints =============

@app.post("/sandboxes")
async def create_sandbox(config_data: dict):
    """Vytvoření nového sandboxu"""
    if not hypervisor:
        raise HTTPException(status_code=500, detail="Hypervisor not initialized")
    
    try:
        # Validace template
        template_id = config_data.get("template_id", "alpine-python")
        if not template_manager.validate_template(template_id):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid or missing template: {template_id}"
            )
        
        # Vytvoření konfigurace
        config = SandboxConfig(
            template_id=template_id,
            memory_mb=config_data.get("memory_mb", 512),
            vcpus=config_data.get("vcpus", 2),
            enable_network=config_data.get("enable_network", True),
            labels=config_data.get("labels", {})
        )
        
        # Vytvoření sandboxu
        sandbox = await hypervisor.create_sandbox(config)
        
        # Uložení do registru
        sandboxes_registry[sandbox.sandbox_id] = {
            "sandbox": sandbox,
            "created_at": sandbox.created_at
        }
        
        logger.info(f"Sandbox vytvořen: {sandbox.sandbox_id}")
        
        return {
            "sandbox_id": sandbox.sandbox_id,
            "state": sandbox.state.value,
            "boot_time_ms": sandbox.metadata.get("boot_time_ms"),
            "config": {
                "memory_mb": sandbox.config.memory_mb,
                "vcpus": sandbox.config.vcpus,
                "template_id": sandbox.config.template_id
            }
        }
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=f"Template error: {str(e)}")
    except Exception as e:
        logger.error(f"Chyba při vytváření sandboxu: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sandboxes")
async def list_sandboxes():
    """Výpis všech sandboxů"""
    return {
        "sandboxes": [
            {
                "sandbox_id": sid,
                "state": data["sandbox"].state.value,
                "created_at": data["created_at"],
                "config": {
                    "memory_mb": data["sandbox"].config.memory_mb,
                    "vcpus": data["sandbox"].config.vcpus
                }
            }
            for sid, data in sandboxes_registry.items()
        ],
        "count": len(sandboxes_registry)
    }


@app.get("/sandboxes/{sandbox_id}")
async def get_sandbox(sandbox_id: str):
    """Podrobnosti o sandboxu"""
    if sandbox_id not in sandboxes_registry:
        raise HTTPException(status_code=404, detail="Sandbox not found")
    
    data = sandboxes_registry[sandbox_id]
    sandbox = data["sandbox"]
    
    return {
        "sandbox_id": sandbox.sandbox_id,
        "state": sandbox.state.value,
        "uptime_ms": sandbox.get_uptime_ms(),
        "config": {
            "memory_mb": sandbox.config.memory_mb,
            "vcpus": sandbox.config.vcpus,
            "template_id": sandbox.config.template_id,
            "labels": sandbox.config.labels
        },
        "created_at": sandbox.created_at
    }


@app.get("/sandboxes/{sandbox_id}/stats")
async def get_sandbox_stats(sandbox_id: str):
    """Statistiky sandboxu"""
    if sandbox_id not in sandboxes_registry:
        raise HTTPException(status_code=404, detail="Sandbox not found")
    
    sandbox = sandboxes_registry[sandbox_id]["sandbox"]
    stats = await sandbox.get_stats()
    
    return {
        "sandbox_id": sandbox_id,
        "stats": stats,
        "uptime_ms": sandbox.get_uptime_ms()
    }


@app.post("/sandboxes/{sandbox_id}/pause")
async def pause_sandbox(sandbox_id: str):
    """Pozastavení sandboxu"""
    if sandbox_id not in sandboxes_registry:
        raise HTTPException(status_code=404, detail="Sandbox not found")
    
    sandbox = sandboxes_registry[sandbox_id]["sandbox"]
    success = await sandbox.pause()
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to pause sandbox")
    
    return {"sandbox_id": sandbox_id, "state": "paused"}


@app.post("/sandboxes/{sandbox_id}/resume")
async def resume_sandbox(sandbox_id: str):
    """Obnovení sandboxu"""
    if sandbox_id not in sandboxes_registry:
        raise HTTPException(status_code=404, detail="Sandbox not found")
    
    sandbox = sandboxes_registry[sandbox_id]["sandbox"]
    success = await sandbox.resume()
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to resume sandbox")
    
    return {"sandbox_id": sandbox_id, "state": "running"}


@app.post("/sandboxes/{sandbox_id}/stop")
async def stop_sandbox(sandbox_id: str, force: bool = False):
    """Zastavení sandboxu"""
    if sandbox_id not in sandboxes_registry:
        raise HTTPException(status_code=404, detail="Sandbox not found")
    
    sandbox = sandboxes_registry[sandbox_id]["sandbox"]
    success = await sandbox.stop(force=force)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to stop sandbox")
    
    # Odebrání z registru
    del sandboxes_registry[sandbox_id]
    
    logger.info(f"Sandbox zastaven: {sandbox_id}")
    
    return {"sandbox_id": sandbox_id, "state": "stopped"}


@app.delete("/sandboxes/{sandbox_id}")
async def delete_sandbox(sandbox_id: str):
    """Smazání sandboxu"""
    if sandbox_id not in sandboxes_registry:
        raise HTTPException(status_code=404, detail="Sandbox not found")
    
    sandbox = sandboxes_registry[sandbox_id]["sandbox"]
    
    if sandbox.is_running():
        await sandbox.stop(force=True)
    
    del sandboxes_registry[sandbox_id]
    
    logger.info(f"Sandbox smazán: {sandbox_id}")
    
    return {"sandbox_id": sandbox_id, "message": "Deleted successfully"}


# ============= Error handlers =============

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Globální handler pro neočekávané výjimky"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


def main():
    """Spuštění API serveru"""
    logger.info("Spuštění NovaSandbox API server")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()
