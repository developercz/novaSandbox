#!/usr/bin/env python3
"""
NovaSandbox Quick Reference Guide
Run: python QUICK_START.py
"""

QUICK_START = """
╔════════════════════════════════════════════════════════════════╗
║           NovaSandbox - Ultra-fast microVM System              ║
║                      Quick Start Guide                          ║
╚════════════════════════════════════════════════════════════════╝

## 🚀 Installation

1. Clone repository:
   $ git clone https://github.com/yourusername/novasandbox.git
   $ cd novasandbox

2. Install dependencies:
   $ pip install -r requirements.txt
   
3. (Optional) Install dev tools:
   $ make install-dev

## 📦 Project Structure

novasandbox/
├── core/                 # Core abstractions
│   ├── hypervisor.py    # BaseHypervisor, SandboxConfig
│   ├── sandbox.py       # Sandbox class
│   └── template_manager.py
├── providers/           # Platform implementations
│   ├── firecracker.py   # Linux - Firecracker
│   └── apple_vz.py      # macOS - Apple VZ
├── templates/           # VM templates
│   └── alpine-python.json
├── tests/               # Unit & benchmark tests
├── examples/            # Usage examples
└── README.md            # Full documentation

## 🎯 Basic Usage

```python
import asyncio
from novasandbox.core import SandboxConfig
from novasandbox.providers import FirecrackerHypervisor

async def main():
    # Initialize hypervisor
    hypervisor = FirecrackerHypervisor()
    
    # Create sandbox
    config = SandboxConfig(memory_mb=512, vcpus=2)
    sandbox = await hypervisor.create_sandbox(config)
    
    # Use sandbox
    stats = await sandbox.get_stats()
    print(f"Boot time: {sandbox.metadata['boot_time_ms']:.2f}ms")
    
    # Stop sandbox
    await sandbox.stop()

asyncio.run(main())
```

## 📚 Common Commands

# Run example
$ python examples/basic_usage.py

# Run REST API server
$ python examples/api_server.py

# Run tests
$ make test

# Run benchmarks
$ make test-bench

# Format code
$ make format

# Run linter
$ make lint

# Clean cache
$ make clean

## 🔌 API Reference

### SandboxConfig
config = SandboxConfig(
    template_id="alpine-python",  # Template to use
    memory_mb=512,                # RAM in MB
    vcpus=2,                      # CPU count
    boot_timeout_ms=5000,         # Boot timeout
    enable_network=True,          # Enable networking
    labels={"app": "myapp"}       # Metadata
)

### Sandbox Methods
await sandbox.execute_command("ls -la")   # Run command
await sandbox.get_stats()                 # Get stats
await sandbox.pause()                     # Pause VM
await sandbox.resume()                    # Resume VM
await sandbox.stop()                      # Stop VM
sandbox.is_running()                      # Check status
sandbox.get_uptime_ms()                   # Get uptime

## 🐛 Troubleshooting

### "Template not found"
→ Create templates/ directory with vmlinux and rootfs.ext4
→ Run: python examples/firecracker_setup.py

### Firecracker "Permission denied"
→ Install: sudo apt install firecracker
→ Or add user to kvm group: sudo usermod -a -G kvm $USER

### macOS "Virtualization not available"
→ Requires macOS 11+ with Apple Silicon (M1/M2/M3)

## 📖 More Resources

- Full documentation: README.md
- API details: core/hypervisor.py (docstrings)
- Examples: examples/ directory
- Tests: tests/ directory
- Setup guide: examples/firecracker_setup.py

## 🔑 Key Features

✓ Ultra-fast boot (<150ms on Firecracker)
✓ Cross-platform (Linux/macOS)
✓ Async API (asyncio)
✓ Resource limits (memory, CPU)
✓ Network isolation
✓ Template support
✓ REST API ready

## 📊 Performance Targets

Linux (Firecracker):
- Boot time: <150ms
- Config creation: <1ms
- Memory overhead: <50MB

macOS (Apple VZ):
- Boot time: <200ms
- Config creation: <1ms
- Memory overhead: <100MB

## 🤝 Contributing

1. Read CONTRIBUTING.md
2. Fork the repository
3. Create feature branch: git checkout -b feature/foo
4. Make changes and test: make test lint
5. Push and create Pull Request

## 📄 License

MIT License - See LICENSE file

═══════════════════════════════════════════════════════════════
Last Updated: 16. ledna 2026
For latest: https://github.com/yourusername/novasandbox
═══════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(QUICK_START)
    
    # Try to import and show version
    try:
        import novasandbox
        print(f"\n✓ NovaSandbox version: {novasandbox.__version__}")
        print("✓ Installation successful!")
    except ImportError:
        print("\n⚠ NovaSandbox not installed in current environment")
        print("Run: pip install -e .")
