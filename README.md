# NovaSandbox: Ultra-fast microVM system for AI agents

Minimalistic, highly optimized system for creating and managing ultra-fast microVMs for AI agents. Support for Firecracker (Linux) and Apple Virtualization Framework (macOS) with the goal of achieving startup times under 150ms.

## 🚀 Features

- **Ultra-fast startup**: Boot times under 150ms (Firecracker)
- **Multi-platform**: Linux (Firecracker) + macOS (Apple VZ)
- **Minimalistic**: No unnecessary features - focus on performance
- **Asyncio**: Fully asynchronous API for concurrent management of multiple VMs
- **Isolation**: Network namespacing and filesystem isolation
- **Templates**: Pre-configured Docker-like templates
- **Monitoring**: Real-time statistics and metrics

## 📋 Requirements

### Linux (Firecracker)
- Linux kernel 4.14+
- KVM module
- Firecracker binary
- curl (for API communication)
- sudo privileges (for network configuration)

```bash
# Install Firecracker on Linux
curl -s https://raw.githubusercontent.com/firecracker-microvm/firecracker/master/tools/devtool \
  | bash
```

### macOS (Apple VZ)
- macOS 11.0+
- Apple Silicon (M1/M2/M3 or newer)
- Python 3.9+

## 📦 Installation

```bash
# Clone the project
git clone https://github.com/yourusername/novasandbox.git
cd novasandbox

# Install dependencies
pip install -r requirements.txt

# (Optional) Install development dependencies
pip install -e .[dev]
```

## 🎯 Quick Start

### Basic Example

```python
import asyncio
from novasandbox.core import SandboxConfig
from novasandbox.providers import FirecrackerHypervisor

async def main():
    # Initialize hypervisor
    hypervisor = FirecrackerHypervisor()
    
    # Configure sandbox
    config = SandboxConfig(
        template_id="alpine-python",
        memory_mb=512,
        vcpus=2
    )
    
    # Create and start sandbox
    sandbox = await hypervisor.create_sandbox(config)
    print(f"Sandbox {sandbox.sandbox_id} started in {sandbox.metadata['boot_time_ms']:.2f}ms")
    
    # Stop
    await sandbox.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

### Examples

Find more examples in [examples/](examples/):
- [basic_usage.py](examples/basic_usage.py) - Basic operations

## 📚 Project Structure

```
novasandbox/
├── core/                      # Project core
│   ├── __init__.py
│   ├── hypervisor.py         # Abstract hypervisor layer
│   ├── sandbox.py            # Sandbox class
│   └── template_manager.py   # Template management
│
├── providers/                 # Implementations for specific hypervisors
│   ├── __init__.py
│   ├── firecracker.py        # Firecracker (Linux)
│   └── apple_vz.py           # Apple VZ (macOS)
│
├── templates/                 # Pre-configured VM templates
│   └── alpine-python.json
│
├── tests/                      # Test suite
│   ├── test_sandbox.py
│   └── benchmark.py
│
├── examples/                   # Usage examples
│   └── basic_usage.py
│
├── requirements.txt           # Python dependencies
└── README.md                  # This documentation
```

## 🔌 API Reference

### SandboxConfig

Configuration for creating a sandbox:

```python
SandboxConfig(
    template_id: str = "alpine-python",  # Template ID
    memory_mb: int = 512,                # Memory in MB
    vcpus: int = 2,                      # Number of vCPUs
    boot_timeout_ms: int = 5000,         # Boot timeout
    kernel_args: str = "...",            # Kernel arguments
    enable_network: bool = True,         # Network connections
    host_port: int = None,               # Port on host
    guest_port: int = 8080,              # Port in sandbox
    rootfs_path: str = None,             # Path to rootfs
    extra_drives: List[Dict] = None,     # Extra drives
    labels: Dict[str, str] = None        # Metadata labels
)
```

### Sandbox Class

```python
class Sandbox:
    # Attributes
    sandbox_id: str                # Unique identifier
    state: SandboxState           # Current state
    config: SandboxConfig         # Configuration
    
    # Methods
    async execute_command(cmd: str) -> str  # Execute command
    async get_stats() -> Dict                # Statistics
    async stop(force=False) -> bool         # Stop
    async pause() -> bool                   # Pause
    async resume() -> bool                  # Resume
    
    is_running() -> bool                    # Is running?
    get_uptime_ms() -> float               # Uptime in ms
```

### Hypervisor Interface

```python
class BaseHypervisor:
    async create_sandbox(config: SandboxConfig) -> Sandbox
    async start_sandbox(sandbox_id: str) -> bool
    async stop_sandbox(sandbox_id: str, force=False) -> bool
    async pause_sandbox(sandbox_id: str) -> bool
    async resume_sandbox(sandbox_id: str) -> bool
    async get_sandbox_stats(sandbox_id: str) -> Dict
```

## 🔧 Configuration

### Firecracker-Specific Settings

In `core/hypervisor.py`, the default kernel arguments:

```python
kernel_args = (
    "console=ttyS0 reboot=k panic=1 "
    "pci=off nomodules random.trust_cpu=on "
    "init=/sbin/init noapic noacpi"
)
```

Optimizations for fastest startup:
- `pci=off` - Disable PCI discovery
- `nomodules` - No dynamic module loading
- `noapic/noacpi` - Disable APIC/ACPI to reduce boot time

### Template Structure

Templates are located in `templates/`. Each template needs:

```
templates/alpine-python/
├── alpine-python.json  # Metadata
├── vmlinux             # Kernel image
└── rootfs.ext4         # Root filesystem
```

JSON configuration:

```json
{
  "name": "Alpine Linux with Python",
  "template_id": "alpine-python",
  "os_type": "linux",
  "memory_mb": 512,
  "vcpus": 2,
  "boot_time_ms": 150,
  "disk_size_gb": 1.0,
  "kernel_version": "6.1",
  "required_files": ["vmlinux", "rootfs.ext4"],
  "packages": ["python3", "curl", "wget"]
}
```

## 🧪 Testing

```bash
# Run unit tests
pytest tests/test_sandbox.py -v

# Run benchmark tests
pytest tests/benchmark.py -v --benchmark-only

# Code coverage
pytest tests/ --cov=core --cov=providers

# Specific test
pytest tests/test_sandbox.py::TestSandboxConfig::test_default_config -v
```

## 📊 Performance Benchmarks

Expected values on Intel CPU with KVM (Firecracker):

| Operation | Time |
|---------|------|
| Sandbox boot | <150ms |
| Config creation | <1ms |
| Pause/Resume | <100ms |
| Stats retrieval | <50ms |

Expected values on Apple Silicon (VZ):

| Operation | Time |
|---------|------|
| Sandbox boot | <200ms |
| Config creation | <1ms |
| Pause/Resume | <150ms |
| Stats retrieval | <50ms |

## 🛡️ Security

- **Namespace isolation**: Each sandbox is in a separate network namespace
- **Resource limits**: Memory and CPU limits are enforced
- **Read-only rootfs**: Option to run read-only filesystem
- **Network NAT**: All sandboxes behind NAT gateway

⚠️ **Note**: For production we recommend:
- SELinux/AppArmor profiles
- Signed kernel images
- Mutual TLS for API communication

## 🐛 Troubleshooting

### Firecracker: "Permission denied"
```bash
# Solution: Run with sudo or add to kvm group
sudo usermod -a -G kvm $USER
```

### "Template not found"
```bash
# Create templates/ directory with correct files
mkdir -p templates/alpine-python
# Copy vmlinux and rootfs.ext4
```

### macOS: "Virtualization.Framework not available"
```bash
# Requires macOS 11+ with Apple Silicon
system_profiler SPHardwareDataType | grep "Chip"
```

## 📝 Examples

### Concurrent Management of Multiple VMs

```python
import asyncio
from novasandbox.core import SandboxConfig
from novasandbox.providers import FirecrackerHypervisor

async def main():
    hypervisor = FirecrackerHypervisor()
    
    # Create multiple configurations
    configs = [
        SandboxConfig(
            memory_mb=256,
            labels={"worker": f"task-{i}"}
        )
        for i in range(5)
    ]
    
    # Start all concurrently
    sandboxes = await asyncio.gather(
        *[hypervisor.create_sandbox(cfg) for cfg in configs]
    )
    
    print(f"Started {len(sandboxes)} sandboxes")
    
    # Stop all
    await asyncio.gather(
        *[sb.stop() for sb in sandboxes]
    )
```

### Sandbox Monitoring

```python
async def monitor_sandbox(sandbox, interval=1.0):
    while sandbox.is_running():
        stats = await sandbox.get_stats()
        print(f"Memory: {stats.get('memory_usage_mb')}MB")
        print(f"CPU: {stats.get('cpu_usage_us')}μs")
        await asyncio.sleep(interval)
```

## 🤝 Contributing

We welcome pull requests! Please:
1. Fork the project
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 👥 Authors

- Created for AI agents and ultra-fast workloads

## 🔗 Useful Links

- [Firecracker documentation](https://github.com/firecracker-microvm/firecracker)
- [Apple Virtualization.Framework](https://developer.apple.com/documentation/virtualization)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)

---

**Last updated**: January 16, 2026
