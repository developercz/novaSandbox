# NovaSandbox - Project File Index

## Core Components

| File | Purpose |
|------|---------|
| `core/__init__.py` | Core module exports |
| `core/hypervisor.py` | Abstract hypervisor interface, SandboxState, SandboxConfig |
| `core/sandbox.py` | Sandbox class for VM instance representation |
| `core/template_manager.py` | Template management and validation |

## Provider Implementations

| File | Purpose |
|------|---------|
| `providers/__init__.py` | Provider module exports |
| `providers/firecracker.py` | Firecracker (Linux) implementation |
| `providers/apple_vz.py` | Apple Virtualization.Framework (macOS) implementation |

## Templates

| File | Purpose |
|------|---------|
| `templates/__init__.py` | Templates module |
| `templates/alpine-python.json` | Alpine Linux with Python template metadata |

## Tests

| File | Purpose |
|------|---------|
| `tests/__init__.py` | Tests module |
| `tests/test_sandbox.py` | Unit tests for core components |
| `tests/benchmark.py` | Performance benchmarks |

## Examples & Documentation

| File | Purpose |
|------|---------|
| `examples/__init__.py` | Examples module |
| `examples/basic_usage.py` | Basic sandbox creation and management |
| `examples/api_server.py` | REST API server using FastAPI |
| `examples/firecracker_setup.py` | Instructions for setting up Firecracker templates |

## Configuration & Build

| File | Purpose |
|------|---------|
| `__init__.py` | Main package initialization |
| `pyproject.toml` | Python project metadata and tool configuration |
| `requirements.txt` | Python package dependencies |
| `Makefile` | Development commands and tasks |
| `.gitignore` | Git ignore rules |

## Documentation

| File | Purpose |
|------|---------|
| `README.md` | Comprehensive project documentation |
| `CONTRIBUTING.md` | Contribution guidelines |
| `CHANGELOG.md` | Version history and planned features |
| `LICENSE` | MIT License |

## CI/CD

| File | Purpose |
|------|---------|
| `.github/workflows/tests.yml` | GitHub Actions test pipeline |

---

## Project Statistics

- **Python Files**: 15
- **Test Files**: 2
- **Configuration Files**: 4
- **Documentation Files**: 5
- **Total Lines of Code**: ~3500+

## Key Classes

### Core API
- `SandboxState` - Enum for VM states
- `SandboxConfig` - Configuration dataclass
- `BaseHypervisor` - Abstract base for implementations
- `Sandbox` - VM instance representation
- `TemplateManager` - Template management

### Implementations
- `FirecrackerHypervisor` - Linux/Firecracker
- `AppleVZHypervisor` - macOS/Apple VZ

## Main Dependencies

- **asyncio** - Async runtime (stdlib)
- **pathlib** - Path handling (stdlib)
- **logging** - Logging (stdlib)
- **psutil** - System metrics
- **aiofiles** - Async file operations
- **httpx** - HTTP client (optional)
- **fastapi** - REST API framework (optional)
- **pytest** - Testing framework (dev)

## Quick Start Commands

```bash
# Install
pip install -r requirements.txt

# Run example
python examples/basic_usage.py

# Run tests
pytest tests/test_sandbox.py -v

# Format code
make format

# Run API server
python examples/api_server.py
```

## Project Structure Map

```
novaSandbox/
├── Core Logic
│   ├── core/hypervisor.py         ← Abstract interfaces
│   ├── core/sandbox.py            ← VM representation
│   └── core/template_manager.py   ← Template handling
│
├── Platform Implementations
│   ├── providers/firecracker.py   ← Linux (Firecracker)
│   └── providers/apple_vz.py      ← macOS (Apple VZ)
│
├── User Code
│   ├── examples/basic_usage.py    ← Getting started
│   ├── examples/api_server.py     ← REST API
│   └── examples/firecracker_setup.py ← Setup guide
│
├── Testing
│   ├── tests/test_sandbox.py      ← Unit tests
│   └── tests/benchmark.py         ← Performance tests
│
└── Support Files
    ├── README.md                  ← Documentation
    ├── requirements.txt           ← Dependencies
    ├── pyproject.toml            ← Build config
    └── Makefile                  ← Development commands
```

---

Generated: 16. ledna 2026
