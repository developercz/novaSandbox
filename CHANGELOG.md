# Changelog

All significant changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and the project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-16

### Added
- NovaSandbox project initialization
- Abstract `BaseHypervisor` layer for unified API
- Firecracker hypervisor implementation for Linux
  - Ultra-fast boot times (<150ms)
  - TAP interface management
  - API socket communication
  - Resource monitoring
- Apple VZ hypervisor implementation for macOS
  - Native Virtualization.Framework integration
  - Pause/Resume support
  - Network NAT configuration
- `Sandbox` class for VM instance representation
  - Lifecycle management (start, pause, resume, stop)
  - Statistics and monitoring
  - Metadata storage
- `TemplateManager` for template management
  - JSON-based configuration
  - Template validation
  - Dynamic loading
- `SandboxConfig` dataclass for configuration
  - Memory, CPU, network
  - Extra disks
  - Metadata labels
- Examples:
  - `basic_usage.py` - basic operations
  - `api_server.py` - REST API server with FastAPI
  - `firecracker_setup.py` - setup instructions
- Tests:
  - Unit tests in `test_sandbox.py`
  - Benchmark tests in `benchmark.py`
  - Coverage report generation
- Documentation:
  - Comprehensive README.md
  - API reference
  - Troubleshooting guide
  - Contributing guidelines
- Development tools:
  - Makefile for common tasks
  - pyproject.toml with black/isort configuration
  - pytest configuration with async support
  - .gitignore for Python projects

### Technical Details
- Asynchronous API with asyncio
- Type hints for all public APIs
- Logging with Python logging module
- Cross-platform support (Linux/macOS)

## Planned Features

### [0.2.0]
- [ ] REST API server (alpha)
- [ ] Persistent storage management
- [ ] Custom kernel support
- [ ] Hook system (pre/post lifecycle events)
- [ ] Metrics export (Prometheus)

### [0.3.0]
- [ ] Windows Hyper-V support
- [ ] gVisor implementation
- [ ] Docker image import
- [ ] Volume management
- [ ] Multi-VM orchestration

### [1.0.0]
- [ ] Production-ready stability
- [ ] Full test coverage
- [ ] Performance optimization
- [ ] Extended documentation
- [ ] CLI tool

## Known Issues

- Apple VZ implementation requires macOS 11+ with Apple Silicon
- Firecracker requires KVM and sudo privileges
- Network isolation requires Linux network namespace support

## Security

For information about security vulnerabilities, please contact maintainers
directly instead of public reporting.

---

Changes are organized under versions with standard sections:
- **Added** - new features
- **Changed** - changes in existing functionality
- **Deprecated** - future removal
- **Removed** - removed features
- **Fixed** - bug fixes
- **Security** - security updates
