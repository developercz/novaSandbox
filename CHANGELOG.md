# Changelog

Všechny zásadní změny v tomto projektu jsou dokumentovány v tomto souboru.

Formát je založen na [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
a projekt dodržuje [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-16

### Added
- Inicializace projektu NovaSandbox
- Abstraktní vrstva `BaseHypervisor` pro jednotné API
- Implementace Firecracker hypervisoru pro Linux
  - Ultra-rychlé boot časy (<150ms)
  - TAP interface management
  - API socket komunikace
  - Resource monitoring
- Implementace Apple VZ hypervisoru pro macOS
  - Nativní Virtualization.Framework integrace
  - Pause/Resume podpora
  - Network NAT konfiguraci
- `Sandbox` třída pro reprezentaci VM instancí
  - Lifecycle management (start, pause, resume, stop)
  - Statistiky a monitoring
  - Metadata storage
- `TemplateManager` pro správu šablon
  - JSON-based konfigurace
  - Validace šablon
  - Dynamické loadování
- `SandboxConfig` dataclass pro konfiguraci
  - Paměť, CPU, síť
  - Extra disky
  - Metadata labels
- Příklady:
  - `basic_usage.py` - základní operace
  - `api_server.py` - REST API server s FastAPI
  - `firecracker_setup.py` - instrukce pro setup
- Testy:
  - Unit testy v `test_sandbox.py`
  - Benchmark testy v `benchmark.py`
  - Coverage repor generování
- Dokumentace:
  - Komplexní README.md
  - API reference
  - Troubleshooting guide
  - Contributing guidelines
- Development tools:
  - Makefile pro common tasks
  - pyproject.toml s black/isort konfigurací
  - pytest konfigurace s async support
  - .gitignore pro Python projekty

### Technical Details
- Asynchronní API s asyncio
- Type hints všech public API
- Logging s Python logging module
- Cross-platform support (Linux/macOS)

## Plánované features

### [0.2.0]
- [ ] REST API server (alpha)
- [ ] Persistent storage management
- [ ] Custom kernel support
- [ ] Hook systém (pre/post lifecycle events)
- [ ] Metrics export (Prometheus)

### [0.3.0]
- [ ] Windows Hyper-V support
- [ ] gVisor implementace
- [ ] Docker image import
- [ ] Volume management
- [ ] Multi-VM orchestration

### [1.0.0]
- [ ] Production-ready stability
- [ ] Full test coverage
- [ ] Performance optimization
- [ ] Extended documentation
- [ ] CLI tool

## Známé problémy

- Apple VZ implementace vyžaduje macOS 11+ s Apple Silicon
- Firecracker vyžaduje KVM a sudo oprávnění
- Network isolation vyžaduje Linux network namespace support

## Bezpečnost

Pro informace o bezpečnostních zranitelnostech prosím kontaktujte maintainers
přímo místo veřejného reportu.

---

Změny jsou organizovány pod verzemi se standardními sekce:
- **Added** - nové funkcionality
- **Changed** - změny v existující funkcionalitě
- **Deprecated** - budoucí odebrání
- **Removed** - odebrané funkcionality
- **Fixed** - opravy bugů
- **Security** - bezpečnostní aktualizace
