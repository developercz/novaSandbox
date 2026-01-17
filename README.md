# NovaSandbox: Ultra-rychlý microVM systém pro AI agenty

Minimalistický, vysoce optimalizovaný systém pro vytváření a správu ultra-rychlých microVM pro AI agenty. Podpora Firecracker (Linux) a Apple Virtualization Framework (macOS) s cílem dosáhnout startu pod 150ms.

## 🚀 Vlastnosti

- **Ultra-rychlý start**: Boot časy pod 150ms (Firecracker)
- **Multi-platform**: Linux (Firecracker) + macOS (Apple VZ)
- **Minimalistický**: Zbytnečné feature nejsou - zaměření na výkon
- **Asyncio**: Plně asynchronní API pro souběžné správy více VM
- **Izolace**: Network namespacing a filesystem isolation
- **Šablony**: Předpřipravené Docker-like šablony
- **Monitoring**: Real-time statistiky a metriky

## 📋 Požadavky

### Linux (Firecracker)
- Linux kernel 4.14+
- KVM modul
- Firecracker binary
- curl (pro API komunikaci)
- sudo práva (pro síťovou konfiguraci)

```bash
# Instalace Firecracker na Linux
curl -s https://raw.githubusercontent.com/firecracker-microvm/firecracker/master/tools/devtool \
  | bash
```

### macOS (Apple VZ)
- macOS 11.0+
- Apple Silicon (M1/M2/M3 nebo novější)
- Python 3.9+

## 📦 Instalace

```bash
# Klonování projektu
git clone https://github.com/yourusername/novasandbox.git
cd novasandbox

# Instalace závislostí
pip install -r requirements.txt

# (Volitelně) Instalace development závislostí
pip install -e .[dev]
```

## 🎯 Rychlý start

### Základní příklad

```python
import asyncio
from novasandbox.core import SandboxConfig
from novasandbox.providers import FirecrackerHypervisor

async def main():
    # Inicialisace hypervisoru
    hypervisor = FirecrackerHypervisor()
    
    # Konfigurace sandboxu
    config = SandboxConfig(
        template_id="alpine-python",
        memory_mb=512,
        vcpus=2
    )
    
    # Vytvoření a spuštění sandboxu
    sandbox = await hypervisor.create_sandbox(config)
    print(f"Sandbox {sandbox.sandbox_id} spuštěn za {sandbox.metadata['boot_time_ms']:.2f}ms")
    
    # Zastavení
    await sandbox.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

### Příklady

Více příkladů najdete v [examples/](examples/):
- [basic_usage.py](examples/basic_usage.py) - Základní operace

## 📚 Struktura projektu

```
novasandbox/
├── core/                      # Jádro projektu
│   ├── __init__.py
│   ├── hypervisor.py         # Abstraktní vrstva hypervisoru
│   ├── sandbox.py            # Třída Sandbox
│   └── template_manager.py   # Správa šablon
│
├── providers/                 # Implementace pro konkrétní hypervisory
│   ├── __init__.py
│   ├── firecracker.py        # Firecracker (Linux)
│   └── apple_vz.py           # Apple VZ (macOS)
│
├── templates/                 # Předpřipravené šablony VM
│   └── alpine-python.json
│
├── tests/                      # Testovací sada
│   ├── test_sandbox.py
│   └── benchmark.py
│
├── examples/                   # Příklady použití
│   └── basic_usage.py
│
├── requirements.txt           # Python závislosti
└── README.md                  # Tato dokumentace
```

## 🔌 API Reference

### SandboxConfig

Konfigurace pro vytvoření sandboxu:

```python
SandboxConfig(
    template_id: str = "alpine-python",  # ID šablony
    memory_mb: int = 512,                # Paměť v MB
    vcpus: int = 2,                      # Počet vCPU
    boot_timeout_ms: int = 5000,         # Timeout bootování
    kernel_args: str = "...",            # Argumenty kernelu
    enable_network: bool = True,         # Síťová připojení
    host_port: int = None,               # Port na hostiteli
    guest_port: int = 8080,              # Port v sandboxu
    rootfs_path: str = None,             # Cesta k rootfs
    extra_drives: List[Dict] = None,     # Extra disky
    labels: Dict[str, str] = None        # Metadata labels
)
```

### Sandbox třída

```python
class Sandbox:
    # Atributy
    sandbox_id: str                # Jedinečný identifikátor
    state: SandboxState           # Aktuální stav
    config: SandboxConfig         # Konfigurace
    
    # Metody
    async execute_command(cmd: str) -> str  # Vykoná příkaz
    async get_stats() -> Dict                # Statistiky
    async stop(force=False) -> bool         # Zastavení
    async pause() -> bool                   # Pozastavení
    async resume() -> bool                  # Obnovení
    
    is_running() -> bool                    # Je spuštěn?
    get_uptime_ms() -> float               # Uptime v ms
```

### Hypervisor rozhraní

```python
class BaseHypervisor:
    async create_sandbox(config: SandboxConfig) -> Sandbox
    async start_sandbox(sandbox_id: str) -> bool
    async stop_sandbox(sandbox_id: str, force=False) -> bool
    async pause_sandbox(sandbox_id: str) -> bool
    async resume_sandbox(sandbox_id: str) -> bool
    async get_sandbox_stats(sandbox_id: str) -> Dict
```

## 🔧 Konfigurace

### Firecracker specifické nastavení

V `core/hypervisor.py` se výchozí kernel argumenty:

```python
kernel_args = (
    "console=ttyS0 reboot=k panic=1 "
    "pci=off nomodules random.trust_cpu=on "
    "init=/sbin/init noapic noacpi"
)
```

Optimalizace pro co nejrychlejší start:
- `pci=off` - Vypnutí PCI discovery
- `nomodules` - Bez dynamického loadingu modulů
- `noapic/noacpi` - Vypnutí APIC/ACPI pro snížení bootování

### Template struktura

Šablony se nacházejí v `templates/`. Každá šablona potřebuje:

```
templates/alpine-python/
├── alpine-python.json  # Metadata
├── vmlinux             # Kernel image
└── rootfs.ext4         # Root filesystem
```

JSON konfigurace:

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

## 🧪 Testování

```bash
# Spuštění unit testů
pytest tests/test_sandbox.py -v

# Spuštění benchmark testů
pytest tests/benchmark.py -v --benchmark-only

# Pokrytí kódu
pytest tests/ --cov=core --cov=providers

# Specifický test
pytest tests/test_sandbox.py::TestSandboxConfig::test_default_config -v
```

## 📊 Výkonnostní benchmarky

Očekávané hodnoty na Intel CPU s KVM (Firecracker):

| Operace | Čas |
|---------|------|
| Sandbox boot | <150ms |
| Config vytvoření | <1ms |
| Pause/Resume | <100ms |
| Stats retrieval | <50ms |

Očekávané hodnoty na Apple Silicon (VZ):

| Operace | Čas |
|---------|------|
| Sandbox boot | <200ms |
| Config vytvoření | <1ms |
| Pause/Resume | <150ms |
| Stats retrieval | <50ms |

## 🛡️ Bezpečnost

- **Namespace isolation**: Každý sandbox je v separátním network namespacu
- **Resource limits**: Memory a CPU limity jsou vynucovány
- **Read-only rootfs**: Možnost spouštění read-only filesystému
- **Network NAT**: Všechny sandboxes za NAT gateway

⚠️ **Poznámka**: Pro produkci doporučujeme:
- SELinux/AppArmor profily
- Signed kernel images
- Mutual TLS pro API komunikaci

## 🐛 Troubleshooting

### Firecracker: "Permission denied"
```bash
# Řešení: Spusťte s sudo nebo přidejte do kvm group
sudo usermod -a -G kvm $USER
```

### "Template not found"
```bash
# Vytvořte templates/ adresář se správnými soubory
mkdir -p templates/alpine-python
# Zkopírujte vmlinux a rootfs.ext4
```

### macOS: "Virtualization.Framework not available"
```bash
# Vyžaduje macOS 11+ s Apple Silicon
system_profiler SPHardwareDataType | grep "Chip"
```

## 📝 Příklady

### Souběžná správa více VM

```python
import asyncio
from novasandbox.core import SandboxConfig
from novasandbox.providers import FirecrackerHypervisor

async def main():
    hypervisor = FirecrackerHypervisor()
    
    # Vytvoření více konfigurací
    configs = [
        SandboxConfig(
            memory_mb=256,
            labels={"worker": f"task-{i}"}
        )
        for i in range(5)
    ]
    
    # Spuštění všech souběžně
    sandboxes = await asyncio.gather(
        *[hypervisor.create_sandbox(cfg) for cfg in configs]
    )
    
    print(f"Spuštěno {len(sandboxes)} sandboxů")
    
    # Zastavení všech
    await asyncio.gather(
        *[sb.stop() for sb in sandboxes]
    )
```

### Monitoring sandboxu

```python
async def monitor_sandbox(sandbox, interval=1.0):
    while sandbox.is_running():
        stats = await sandbox.get_stats()
        print(f"Memory: {stats.get('memory_usage_mb')}MB")
        print(f"CPU: {stats.get('cpu_usage_us')}μs")
        await asyncio.sleep(interval)
```

## 🤝 Přispívání

Vítáme pull requests! Prosím:
1. Forknout projekt
2. Vytvořit feature branch (`git checkout -b feature/amazing-feature`)
3. Commitnout změny (`git commit -m 'Add amazing feature'`)
4. Pushnout do branch (`git push origin feature/amazing-feature`)
5. Otevřít Pull Request

## 📄 Licence

MIT License - viz [LICENSE](LICENSE) soubor

## 👥 Autoři

- Vytvořeno pro AI agenty a ultra-rychlé workloady

## 🔗 Užitečné odkazy

- [Firecracker dokumentace](https://github.com/firecracker-microvm/firecracker)
- [Apple Virtualization.Framework](https://developer.apple.com/documentation/virtualization)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)

---

**Poslední aktualizace**: 16. ledna 2026
