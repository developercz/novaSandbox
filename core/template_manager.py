"""
Správa předpřipravených šablon microVM.
"""
import json
import os
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class TemplateInfo:
    """Informace o šabloně"""
    template_id: str
    name: str
    description: str
    os_type: str
    memory_mb: int
    vcpus: int
    boot_time_ms: float
    disk_size_gb: float
    kernel_version: str
    files: Dict[str, str]  # path -> sha256

class TemplateManager:
    """Správce šablon microVM"""
    
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self._templates: Dict[str, TemplateInfo] = {}
        self._load_templates()
    
    def _load_templates(self):
        """Načte všechny dostupné šablony"""
        if not self.templates_dir.exists():
            logger.warning(f"Templates directory not found: {self.templates_dir}")
            return
        
        for template_dir in self.templates_dir.iterdir():
            if not template_dir.is_dir():
                continue
            
            config_file = template_dir / f"{template_dir.name}.json"
            if not config_file.exists():
                config_file = template_dir / "config.json"
            
            if config_file.exists():
                try:
                    self._load_template(template_dir.name, config_file)
                except Exception as e:
                    logger.error(f"Failed to load template {template_dir.name}: {e}")
    
    def _load_template(self, template_id: str, config_file: Path):
        """Načte jednu šablonu z JSON souboru"""
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        template_dir = config_file.parent
        
        # Validace potřebných souborů
        required_files = {}
        for fname in config.get("required_files", []):
            file_path = template_dir / fname
            if not file_path.exists():
                raise FileNotFoundError(f"Required file not found: {fname}")
            required_files[fname] = file_path.resolve().as_posix()
        
        template_info = TemplateInfo(
            template_id=template_id,
            name=config.get("name", template_id),
            description=config.get("description", ""),
            os_type=config.get("os_type", "linux"),
            memory_mb=config.get("memory_mb", 512),
            vcpus=config.get("vcpus", 2),
            boot_time_ms=config.get("boot_time_ms", 150.0),
            disk_size_gb=config.get("disk_size_gb", 1.0),
            kernel_version=config.get("kernel_version", "unknown"),
            files=required_files
        )
        
        self._templates[template_id] = template_info
        logger.info(f"Loaded template: {template_id}")
    
    def get_template(self, template_id: str) -> Optional[TemplateInfo]:
        """Vrátí informace o šabloně"""
        return self._templates.get(template_id)
    
    def list_templates(self) -> List[str]:
        """Vrátí seznam všech dostupných šablon"""
        return list(self._templates.keys())
    
    def validate_template(self, template_id: str) -> bool:
        """Ověří, zda je šablona platná a všechny soubory existují"""
        template = self.get_template(template_id)
        if not template:
            return False
        
        for fname, fpath in template.files.items():
            if not os.path.exists(fpath):
                return False
        
        return True
