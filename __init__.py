"""
NovaSandbox - Ultra-fast microVM system for AI agents

A minimalist, highly optimized system for creating and managing ultra-fast
microVMs for AI agents. Supports Firecracker (Linux) and Apple Virtualization
Framework (macOS) with boot times under 150ms.
"""

__version__ = "0.1.0"
__author__ = "NovaSandbox Team"
__license__ = "MIT"

from .core import (
    BaseHypervisor,
    SandboxConfig,
    SandboxState,
    Sandbox,
    TemplateManager,
    TemplateInfo,
)
from .providers import (
    FirecrackerHypervisor,
    AppleVZHypervisor,
)

__all__ = [
    "BaseHypervisor",
    "SandboxConfig",
    "SandboxState",
    "Sandbox",
    "TemplateManager",
    "TemplateInfo",
    "FirecrackerHypervisor",
    "AppleVZHypervisor",
]
